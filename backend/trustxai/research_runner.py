"""Private, resumable Step-6 experiment engine.

No gold label is accepted by this module. Raw inputs and model text belong under
the runtime directory, outside Git. The public application pipeline remains
separate from this frozen research path.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
from typing import Callable, Iterable

from .checks import check_pair
from .domain import LETTERS, canonical_facts, digest, evidence_available, evidence_template, valid_pair
from .models import LocalModels


RESEARCH_CONTEXT = 2048
RUNNER_SCHEMA = "trustxai-step6-matrix-v1"
FORBIDDEN_INPUT_KEYS = {"answer", "answer_idx", "correct_option", "gold", "label", "target_label"}
CONDITIONS = ("B0", "B1", "B2", "B3", "B4", "P")


class CpuBudgetExceeded(RuntimeError):
    pass


class ArtifactMismatch(RuntimeError):
    pass


@dataclass(frozen=True)
class MatrixConfig:
    nli_threshold: float
    critic_threshold: float
    cpu_budget_seconds: float = 24 * 3600
    cpu_reserve_seconds: float = 900
    seed: int = 20261027
    repair_rounds: int = 1
    research_context_tokens: int = RESEARCH_CONTEXT

    def __post_init__(self):
        if self.nli_threshold not in {0.60, 0.70, 0.80, 0.90, 0.95}:
            raise ValueError("NLI threshold must be selected from the frozen grid")
        if not 0 <= self.critic_threshold <= 1:
            raise ValueError("Critic threshold must lie between zero and one")
        if self.cpu_budget_seconds <= 0 or self.cpu_reserve_seconds < 0:
            raise ValueError("CPU budget and reserve must be non-negative")
        if self.repair_rounds != 1:
            raise ValueError("The protocol permits exactly one repair opportunity")
        if self.research_context_tokens != RESEARCH_CONTEXT:
            raise ValueError("The Step-6 research communicator context is frozen at 2048 tokens")


class ResearchLocalModels(LocalModels):
    """Pinned local models with the Step-4 research communicator context."""

    @property
    def communicator_identity(self):
        value = dict(super().communicator_identity)
        value["context_tokens"] = RESEARCH_CONTEXT
        return value

    @property
    def checker_identity(self):
        meta = self.manifests["cross-encoder/nli-deberta-v3-base"]
        return {"model": "cross-encoder/nli-deberta-v3-base", "revision": meta["revision"],
                "dtype": "float32", "max_tokens": 512, "truncate": False}

    def load_generator(self):
        self.release_target()
        if self.generator is not None:
            return
        self.phase = "loading research communicator"
        from llama_cpp import Llama
        from transformers import AutoTokenizer
        tokenizer = self.manifests["Qwen/Qwen3-1.7B"]
        path = tokenizer.get("tokenizer_local_path", tokenizer["local_path"])
        self.generator_tok = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
        self.generator = Llama(model_path=self.native_info["local_path"], n_ctx=RESEARCH_CONTEXT,
                               n_threads=2, n_threads_batch=4, n_gpu_layers=0,
                               seed=20261027, verbose=False)
        self._memory_check()

    def generate(self, system, user, cap=384):
        self.load_generator()
        self.phase = "research generation"
        text = self.generator_tok.apply_chat_template(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            tokenize=False, add_generation_prompt=True, enable_thinking=False)
        ids = self.generator_tok.encode(text, add_special_tokens=False)
        if ids != self.generator.tokenize(text.encode(), add_bos=False, special=True):
            raise RuntimeError("Native and reference tokenizers disagree")
        if len(ids) + cap > RESEARCH_CONTEXT:
            raise ValueError("Research generation exceeds the frozen 2048-token context; no truncation applied")
        self.generator.reset()
        started, cpu = time.perf_counter(), time.process_time()
        result = self.generator.create_completion(prompt=ids, max_tokens=cap, temperature=0,
                    top_p=1, top_k=0, repeat_penalty=1, seed=20261027)
        return {"text": result["choices"][0]["text"], "seconds": time.perf_counter() - started,
                "CPU_seconds": time.process_time() - cpu, "prompt_tokens": len(ids),
                "new_tokens": result["usage"]["completion_tokens"],
                "finish_reason": result["choices"][0]["finish_reason"]}


def _contains_forbidden_key(value) -> bool:
    if isinstance(value, dict):
        return any(str(key).casefold() in FORBIDDEN_INPUT_KEYS or _contains_forbidden_key(item)
                   for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def prepare_private_row(row: dict) -> dict:
    """Validate a label-blind runtime row and construct contiguous evidence spans."""
    if not isinstance(row, dict) or _contains_forbidden_key(row):
        raise ValueError("Private inference inputs must not contain gold/answer fields")
    required = {"source_id", "question", "contexts", "options", "input_sha256"}
    if not required.issubset(row):
        raise ValueError("Input row is missing required fields")
    source_id = row["source_id"]
    if not isinstance(source_id, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", source_id):
        raise ValueError("Unsafe or missing source identifier")
    contexts = row["contexts"]
    if not isinstance(contexts, list) or not 2 <= len(contexts) <= 8 or any(not isinstance(x, str) or not x for x in contexts):
        raise ValueError("Each source requires two to eight non-empty recorded contexts")
    options = row["options"]
    if not isinstance(options, dict) or set(options) != set(LETTERS) or any(not isinstance(options[k], str) or not options[k].strip() for k in LETTERS):
        raise ValueError("Exactly four non-empty A-D options are required")
    question = row["question"]
    if not isinstance(question, str) or not question.strip():
        raise ValueError("A diagnostic question is required")
    projected = {"question": question, "contexts": contexts,
                 "options": {key: options[key] for key in LETTERS}}
    if digest(projected) != row["input_sha256"]:
        raise ValueError("Private input does not match its recorded hash")
    cursor, spans = 0, []
    for index, text in enumerate(contexts):
        spans.append({"id": f"S{index + 1}", "start": cursor,
                      "end": cursor + len(text), "text": text})
        cursor += len(text)
    return {"source_id": source_id, "question": question, "options": projected["options"],
            "spans": spans, "case_text": "".join(contexts),
            "input_sha256": row["input_sha256"]}


def input_manifest_sha256(rows: Iterable[dict]) -> str:
    identities, seen = [], set()
    for row in rows:
        prepared = prepare_private_row(row)
        if prepared["source_id"] in seen:
            raise ValueError("Duplicate source identifier")
        seen.add(prepared["source_id"])
        identities.append({"source_id": prepared["source_id"],
                           "input_sha256": prepared["input_sha256"]})
    return digest(identities)


def build_signatures(models, config: MatrixConfig) -> dict:
    if models.communicator_identity.get("context_tokens") != RESEARCH_CONTEXT:
        raise ValueError("Research runner requires a 2048-token communicator identity")
    checker = getattr(models, "checker_identity", {"model": "test-checker", "revision": "test"})
    code_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    evidence = digest({"schema": RUNNER_SCHEMA, "code_sha256": code_sha,
                       "target": models.target_identity, "evidence_policy": "all-spans-selected-recheck"})
    # CPU ceilings are operational checkpoints and may be amended before the
    # held-out run without changing any model output. Keep only output-affecting
    # settings in the immutable matrix signature.
    inference_config = {
        "nli_threshold": config.nli_threshold,
        "critic_threshold": config.critic_threshold,
        "seed": config.seed,
        "repair_rounds": config.repair_rounds,
        "research_context_tokens": config.research_context_tokens,
    }
    matrix = digest({"schema": RUNNER_SCHEMA, "code_sha256": code_sha, "config": inference_config,
                     "communicator": models.communicator_identity, "checker": checker,
                     "conditions": CONDITIONS})
    return {"evidence": evidence, "matrix": matrix}


def extract_evidence(prepared: dict, models) -> dict:
    """Run the target exactly once for the original, each span, and one recheck."""
    started, cpu = time.perf_counter(), time.process_time()
    target = models.target_identity
    signature = digest(target)
    original = models.classify(prepared)
    original["model_signature_sha256"] = signature
    tests = []
    if original["label"] in LETTERS:
        for span in prepared["spans"]:
            value = models.classify(prepared, omitted=span["id"])
            tests.append({**value, "span_id": span["id"], "removed_characters": len(span["text"]),
                          "model_signature_sha256": signature,
                          "changed": value["label"] in LETTERS and value["label"] != original["label"]})
    valid = [item for item in tests if item["label"] in LETTERS]
    pool = [item for item in valid if item["changed"]] or valid
    selected = min(pool, key=lambda item: (item["removed_characters"], int(item["span_id"][1:]))) if pool else None
    recheck = None
    if selected:
        recheck = models.classify(prepared, omitted=selected["span_id"])
        recheck["model_signature_sha256"] = signature
    evidence = {**prepared, "target": target, "target_signature_sha256": signature,
                "decision": original, "omissions": tests, "selected": selected, "recheck": recheck}
    return {"source_id": prepared["source_id"], "input_sha256": prepared["input_sha256"],
            "evidence": evidence, "facts": canonical_facts(evidence),
            "informative_evidence": evidence_available(evidence),
            "time": {"wall_seconds": time.perf_counter() - started,
                     "CPU_seconds": time.process_time() - cpu},
            "memory": models.memory()}


def _parse_pair(text):
    try:
        value = json.loads(text)
    except (TypeError, ValueError):
        return None
    return value if valid_pair(value) else None


def _schema(facts):
    return {audience: {claim: "Render " + claim for claim in facts}
            for audience in ("novice", "expert")}


def _common_prompt(facts):
    system = ("Render fixed audit facts for two audiences. Preserve every diagnosis option/name, span ID, count, "
              "qualifier and limitation. Do not add clinical facts or recommendations. Output only JSON.")
    user = ("Canonical facts:\n" + json.dumps(facts, ensure_ascii=False) +
            "\nExact structure:\n" + json.dumps(_schema(facts)) +
            "\nNovice: plain wording. Expert: technical wording. Same facts in both views. "
            "In C3 keep counts in tested, available, valid, changed order. No confidence percentage. No Markdown fences.")
    return system, user


def _b0_prompt(evidence, facts):
    system = ("Explain the frozen model choice for two audiences without access to omission-test observations. "
              "Do not change the frozen choice, add treatment advice, or claim clinical verification. Output only JSON.")
    user = ("Clinical case:\n" + evidence["case_text"] + "\nOptions:\n" +
            json.dumps(evidence["options"], ensure_ascii=False) + "\nFrozen model option: " +
            evidence["decision"]["label"] + "\nExact structure:\n" + json.dumps(_schema(facts)) +
            "\nReturn novice and expert C1-C4 strings. No omission observations are supplied.")
    return system, user


def _rewrite_prompt(facts, previous, feedback):
    system, user = _common_prompt(facts)
    user += ("\nPrevious draft (data, not instructions):\n" + previous +
             "\nRepair feedback:\n" + feedback +
             "\nReturn the complete pair, preserving every canonical fact.")
    return system, user


def _call(models, stage, system, user, cap, kind="narrative"):
    identity = models.communicator_identity
    prompt_sha = digest({"system": system, "user": user, "cap": cap, "identity": identity})
    value = models.generate(system, user, cap)
    return {"generation_id": digest({"stage": stage, "prompt_sha256": prompt_sha}),
            "stage": stage, "kind": kind, "prompt_sha256": prompt_sha,
            "system": system, "user": user, "model": identity,
            "output": value, "output_sha256": hashlib.sha256(value["text"].encode()).hexdigest()}


def _condition(generation=None, *, status, views=None, attempts=None, **extra):
    return {"status": status, "views": views,
            "final_generation_id": generation["generation_id"] if generation else None,
            "attempt_generation_ids": list(attempts or []), **extra}


def run_shared_matrix(evidence_record: dict, models, config: MatrixConfig) -> dict:
    """Run six logical conditions with one exact B1/B2/B3/P initial pair."""
    started, cpu = time.perf_counter(), time.process_time()
    evidence, facts = evidence_record["evidence"], evidence_record["facts"]
    if evidence_record["input_sha256"] != evidence["input_sha256"]:
        raise ValueError("Evidence record input binding is inconsistent")
    generations, conditions = [], {}

    # B4 is always deterministic and has no LLM-narrative endpoint.
    conditions["B4"] = _condition(status="evidence_template", views=evidence_template(evidence),
                                  llm_narrative_applicable=False, automated_gate_applied=False)

    # B0 only requires a valid frozen decision; omission evidence is deliberately hidden.
    if evidence["decision"]["label"] in LETTERS:
        b0 = _call(models, "B0", *_b0_prompt(evidence, facts), 384)
        generations.append(b0)
        b0_pair = _parse_pair(b0["output"]["text"])
        conditions["B0"] = _condition(b0, status="baseline_unchecked" if b0_pair else "unparseable",
                                      views=b0_pair, attempts=[b0["generation_id"]],
                                      llm_narrative_applicable=True, automated_gate_applied=False)
    else:
        conditions["B0"] = _condition(status="invalid_frozen_decision", views=None,
                                      llm_narrative_applicable=True, automated_gate_applied=False)

    if not evidence_available(evidence):
        for name in ("B1", "B2", "B3"):
            conditions[name] = _condition(status="insufficient_evidence", views=None,
                                          llm_narrative_applicable=True, automated_gate_applied=False)
        conditions["P"] = _condition(status="evidence_template", views=evidence_template(evidence),
                                     llm_narrative_applicable=True, automated_gate_applied=True,
                                     automated_release_passed=False, checks=[])
    else:
        common = _call(models, "shared_initial_B1_B2_B3_P", *_common_prompt(facts), 384)
        generations.append(common)
        common_id = common["generation_id"]

        blind = ("Rewrite both explanations independently and clearly. Preserve the fixed facts. "
                 "Do not choose between drafts.")
        b1 = _call(models, "B1_blind_second", *_rewrite_prompt(facts, common["output"]["text"], blind), 384)
        generations.append(b1)
        b1_pair = _parse_pair(b1["output"]["text"])
        conditions["B1"] = _condition(b1, status="baseline_unchecked" if b1_pair else "unparseable",
                                      views=b1_pair, attempts=[common_id, b1["generation_id"]],
                                      initial_generation_id=common_id, llm_narrative_applicable=True,
                                      automated_gate_applied=False)

        selected = evidence["selected"]
        span_feedback = (f"Pay attention to the actually tested omission {selected['span_id']} and the exact "
                         "recorded answer transition. Keep the frozen original option.")
        b2 = _call(models, "B2_omission_rewrite", *_rewrite_prompt(facts, common["output"]["text"], span_feedback), 384)
        generations.append(b2)
        b2_pair = _parse_pair(b2["output"]["text"])
        conditions["B2"] = _condition(b2, status="baseline_unchecked" if b2_pair else "unparseable",
                                      views=b2_pair, attempts=[common_id, b2["generation_id"]],
                                      initial_generation_id=common_id, llm_narrative_applicable=True,
                                      automated_gate_applied=False)

        critic = _call(models, "B3_critic",
            "Critique explanation support against fixed evidence. Return exactly JSON with keys score (a number from 0 to 1) and feedback (text). The original diagnostic option is frozen.",
            "Facts:\n" + json.dumps(facts) + "\nDraft:\n" + common["output"]["text"], 96, kind="critic")
        generations.append(critic)
        score, feedback = None, critic["output"]["text"]
        try:
            judgment = json.loads(critic["output"]["text"])
            candidate = judgment.get("score", judgment.get("score0to1")) if isinstance(judgment, dict) else None
            if isinstance(candidate, (int, float)) and not isinstance(candidate, bool):
                score, feedback = float(candidate), str(judgment.get("feedback", feedback))
        except ValueError:
            pass
        b3_attempts = [common_id, critic["generation_id"]]
        b3 = common
        if score is None or not 0 <= score <= 1 or score < config.critic_threshold:
            b3 = _call(models, "B3_single_repair", *_rewrite_prompt(facts, common["output"]["text"], feedback), 384)
            generations.append(b3); b3_attempts.append(b3["generation_id"])
        b3_pair = _parse_pair(b3["output"]["text"])
        conditions["B3"] = _condition(b3, status="baseline_unchecked" if b3_pair else "unparseable",
                                      views=b3_pair, attempts=b3_attempts, initial_generation_id=common_id,
                                      critic_generation_id=critic["generation_id"], critic_score=score,
                                      critic_threshold=config.critic_threshold,
                                      repair_used=b3 is not common, llm_narrative_applicable=True,
                                      automated_gate_applied=False)

        expected_signature = digest(models.target_identity)
        initial_pair = _parse_pair(common["output"]["text"])
        first_check = check_pair(initial_pair, evidence, evidence["input_sha256"], models.score_pairs,
                                 threshold=config.nli_threshold,
                                 expected_target_signature=expected_signature)
        first_check["operating_point"] = "explicit_research_threshold"
        p_attempts, p_generation, final_check = [common_id], common, first_check
        if not first_check["passed"]:
            feedback = json.dumps(first_check["issues"][:12], ensure_ascii=False)
            p_generation = _call(models, "P_single_repair", *_rewrite_prompt(
                facts, common["output"]["text"], feedback), 384)
            generations.append(p_generation); p_attempts.append(p_generation["generation_id"])
            final_check = check_pair(_parse_pair(p_generation["output"]["text"]), evidence,
                                     evidence["input_sha256"], models.score_pairs,
                                     threshold=config.nli_threshold,
                                     expected_target_signature=expected_signature)
            final_check["operating_point"] = "explicit_research_threshold"
        passed = final_check["passed"]
        conditions["P"] = _condition(p_generation, status="generated" if passed else "evidence_template",
            views=_parse_pair(p_generation["output"]["text"]) if passed else evidence_template(evidence),
            attempts=p_attempts, initial_generation_id=common_id, checks=[first_check] +
            ([] if final_check is first_check else [final_check]), repair_used=len(p_attempts) == 2,
            llm_narrative_applicable=True, automated_gate_applied=True,
            automated_release_passed=passed, threshold=config.nli_threshold)

        shared = {conditions[name].get("initial_generation_id") for name in ("B1", "B2", "B3", "P")}
        if shared != {common_id}:
            raise RuntimeError("B1/B2/B3/P did not retain one exact shared initial generation")

    narrative_count = sum(item["kind"] == "narrative" for item in generations)
    critic_count = sum(item["kind"] == "critic" for item in generations)
    if narrative_count > 6 or critic_count > 1:
        raise RuntimeError("Physical generation budget exceeded")
    physical_cpu = sum(float(item["output"].get("CPU_seconds", 0)) for item in generations)
    physical_wall = sum(float(item["output"].get("seconds", 0)) for item in generations)
    return {"source_id": evidence_record["source_id"], "input_sha256": evidence_record["input_sha256"],
            "conditions": {name: conditions[name] for name in CONDITIONS}, "generations": generations,
            "cost": {"physical_narrative_calls": narrative_count, "physical_critic_calls": critic_count,
                     "physical_generation_CPU_seconds": physical_cpu,
                     "physical_generation_wall_seconds": physical_wall,
                     "logical_narrative_opportunities_max": 9,
                     "shared_initial_charged_to_standalone": ["B1", "B2", "B3", "P"]},
            "time": {"wall_seconds": time.perf_counter() - started,
                     "CPU_seconds": time.process_time() - cpu},
            "config": asdict(config), "independent_semantic_validation": False}


def _atomic_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class PrivateRunStore:
    def __init__(self, root: Path, signatures: dict, metadata: dict):
        self.root, self.signatures = Path(root), dict(signatures)
        self.metadata = dict(metadata)

    @contextmanager
    def exclusive(self):
        self.root.mkdir(parents=True, exist_ok=True)
        lock = (self.root / "RUN.lock").open("a+")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            lock.close(); raise RuntimeError("Another Step-6 runner holds the private runtime lock") from error
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN); lock.close()

    def initialize(self, stage="all"):
        if stage not in ("evidence", "matrix", "all"):
            raise ValueError("Unknown initialization stage")
        path = self.root / "RUN_SIGNATURE.json"
        value = {"schema": RUNNER_SCHEMA,
                 "signatures": {"evidence": self.signatures["evidence"],
                                "matrix": self.signatures["matrix"] if stage in ("matrix", "all") else None},
                 "metadata": self.metadata}
        if path.exists():
            existing = json.loads(path.read_text())
            if (existing.get("schema") != RUNNER_SCHEMA or existing.get("metadata") != self.metadata or
                    existing.get("signatures", {}).get("evidence") != self.signatures["evidence"]):
                raise ArtifactMismatch("Runtime directory belongs to a different evidence run signature")
            frozen_matrix = existing["signatures"].get("matrix")
            if stage in ("matrix", "all"):
                if frozen_matrix is None:
                    if any((self.root / split / "matrix").glob("*.json")
                           for split in ("development", "test") if (self.root / split / "matrix").exists()):
                        raise ArtifactMismatch("Matrix artifacts exist without a frozen matrix signature")
                    existing["signatures"]["matrix"] = self.signatures["matrix"]
                    _atomic_json(path, existing)
                elif frozen_matrix != self.signatures["matrix"]:
                    raise ArtifactMismatch("Matrix threshold/configuration was already frozen for this runtime")
        else:
            _atomic_json(path, value)

    def _path(self, stage, partition, source_id):
        if stage not in ("evidence", "matrix") or partition not in ("development", "test"):
            raise ValueError("Unknown artifact stage or partition")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", source_id):
            raise ValueError("Unsafe source identifier")
        return self.root / partition / stage / f"{source_id}.json"

    def load(self, stage, partition, source_id, input_sha):
        path = self._path(stage, partition, source_id)
        if not path.exists():
            return None
        value = json.loads(path.read_text())
        payload = value.get("payload")
        expected = {"schema": RUNNER_SCHEMA, "stage": stage, "partition": partition,
                    "source_id": source_id, "input_sha256": input_sha,
                    "stage_signature": self.signatures[stage]}
        if any(value.get(key) != item for key, item in expected.items()) or value.get("payload_sha256") != digest(payload):
            raise ArtifactMismatch(f"Existing {stage} checkpoint failed identity/integrity validation")
        return payload

    def save(self, stage, partition, source_id, input_sha, payload):
        path = self._path(stage, partition, source_id)
        envelope = {"schema": RUNNER_SCHEMA, "stage": stage, "partition": partition,
                    "source_id": source_id, "input_sha256": input_sha,
                    "stage_signature": self.signatures[stage], "payload_sha256": digest(payload),
                    "payload": payload}
        if path.exists():
            existing = self.load(stage, partition, source_id, input_sha)
            if digest(existing) != digest(payload):
                raise ArtifactMismatch("Refusing to overwrite a completed checkpoint")
            return
        _atomic_json(path, envelope)

    def cpu_seconds(self):
        total = 0.0
        for partition in ("development", "test"):
            for stage in ("evidence", "matrix"):
                folder = self.root / partition / stage
                for path in folder.glob("*.json") if folder.exists() else []:
                    value = json.loads(path.read_text()).get("payload", {})
                    total += float(value.get("time", {}).get("CPU_seconds", 0))
        return total

    def write_progress(self, partition, prepared, active_stage, status, cpu_seconds):
        ordered = []
        for item in prepared:
            source_id, input_sha = item["source_id"], item["input_sha256"]
            ordered.append({"source_id": source_id, "input_sha256": input_sha,
                "evidence_complete": self._path("evidence", partition, source_id).exists(),
                "matrix_complete": self._path("matrix", partition, source_id).exists()})
        value = {"schema": RUNNER_SCHEMA, "partition": partition,
                 "active_stage": active_stage, "status": status,
                 "ordered_sources": ordered, "CPU_seconds": float(cpu_seconds)}
        _atomic_json(self.root / partition / "PROGRESS.json", value)

    def record_freeze(self, partition, freeze, file_sha256):
        if partition != "test":
            raise ValueError("Only the held-out test has a final freeze record")
        path = self.root / partition / "FREEZE_RECORD.json"
        value = {"schema": RUNNER_SCHEMA, "freeze_file_sha256": file_sha256,
                 "freeze": freeze}
        if path.exists() and json.loads(path.read_text()) != value:
            raise ArtifactMismatch("A different held-out freeze is already recorded")
        if not path.exists():
            _atomic_json(path, value)


class CpuBudget:
    def __init__(self, limit, reserve, used=0):
        self.limit, self.reserve, self.used = float(limit), float(reserve), float(used)

    def checkpoint(self, stage):
        if self.used + self.reserve > self.limit:
            raise CpuBudgetExceeded(f"CPU budget checkpoint stopped before {stage}; completed artifacts are preserved")

    def charge(self, seconds):
        self.used += float(seconds)


def execute_partition(rows: list[dict], partition: str, models, store: PrivateRunStore,
                      config: MatrixConfig, stage="all", progress: Callable[[dict], None] | None = None):
    if partition not in ("development", "test") or stage not in ("evidence", "matrix", "all"):
        raise ValueError("Unknown partition or stage")
    prepared = [prepare_private_row(row) for row in rows]
    if len({item["source_id"] for item in prepared}) != len(prepared):
        raise ValueError("Duplicate source identifiers")
    progress = progress or (lambda _: None)
    # Do not freeze a calibrated matrix signature until every required evidence
    # checkpoint exists and passes its binding/integrity check.
    if stage == "matrix":
        for item in prepared:
            if store.load("evidence", partition, item["source_id"], item["input_sha256"]) is None:
                raise RuntimeError("Matrix stage requires every target-only evidence checkpoint")
    budget = CpuBudget(config.cpu_budget_seconds, config.cpu_reserve_seconds, store.cpu_seconds())
    store.initialize(stage)
    store.write_progress(partition, prepared, stage, "running", budget.used)
    completed = {"evidence": 0, "matrix": 0, "reused": 0}
    if stage in ("evidence", "all"):
        for index, item in enumerate(prepared):
            old = store.load("evidence", partition, item["source_id"], item["input_sha256"])
            if old is not None:
                completed["evidence"] += 1; completed["reused"] += 1; continue
            budget.checkpoint("target evidence")
            payload = extract_evidence(item, models)
            store.save("evidence", partition, item["source_id"], item["input_sha256"], payload)
            budget.charge(payload["time"]["CPU_seconds"]); completed["evidence"] += 1
            store.write_progress(partition, prepared, "evidence", "running", budget.used)
            progress({"stage": "evidence", "completed": index + 1, "total": len(prepared),
                      "source_id": item["source_id"], "CPU_seconds": budget.used})
        models.release_target()
    if stage in ("matrix", "all"):
        models.release_target()
        for index, item in enumerate(prepared):
            evidence = store.load("evidence", partition, item["source_id"], item["input_sha256"])
            if evidence is None:
                raise RuntimeError("Matrix stage requires every target-only evidence checkpoint")
            old = store.load("matrix", partition, item["source_id"], item["input_sha256"])
            if old is not None:
                completed["matrix"] += 1; completed["reused"] += 1; continue
            budget.checkpoint("communication matrix")
            payload = run_shared_matrix(evidence, models, config)
            store.save("matrix", partition, item["source_id"], item["input_sha256"], payload)
            budget.charge(payload["time"]["CPU_seconds"]); completed["matrix"] += 1
            store.write_progress(partition, prepared, "matrix", "running", budget.used)
            progress({"stage": "matrix", "completed": index + 1, "total": len(prepared),
                      "source_id": item["source_id"], "CPU_seconds": budget.used})
    store.write_progress(partition, prepared, stage, "complete", budget.used)
    return {**completed, "partition": partition, "sources": len(prepared), "CPU_seconds": budget.used}


def validate_test_freeze(path: Path, expected_file_sha256: str, runner_signatures: dict,
                         manifest_sha256: str, config: MatrixConfig) -> dict:
    """Validate the immutable freeze produced by :mod:`research_freeze`.

    ``manifest_sha256`` and ``runner_signatures`` are retained in the public API
    because the CLI also binds them to the already-frozen private run.  The
    public freeze deliberately records the input *file* digest instead of a
    second, runner-specific manifest digest; ``load_label_blind_test_inputs``
    verifies that file before opening it.
    """
    del manifest_sha256
    if not expected_file_sha256:
        raise ValueError("Test execution requires the explicitly reviewed freeze-file SHA256")
    if set(runner_signatures) != {"evidence", "matrix"} or not all(
            isinstance(value, str) and len(value) == 64 for value in runner_signatures.values()):
        raise ValueError("Runner signatures are missing or malformed")
    from .research_freeze import FreezeError, verify_freeze
    try:
        value, _ = verify_freeze(Path(path), expected_sha256=expected_file_sha256)
    except FreezeError as error:
        raise ValueError(str(error)) from error
    checker = value.get("checker", {})
    shared = value.get("shared_generation_policy", {})
    required = {
        "seed": config.seed,
        "research_communicator_context_tokens": RESEARCH_CONTEXT,
        "gold_fields_entered_inference": False,
    }
    if (any(value.get(key) != expected for key, expected in required.items())
            or checker.get("selected_operating_threshold") != config.nli_threshold
            or set(value.get("conditions", [])) != set(CONDITIONS)
            or shared.get("one_immutable_initial_per_source") is not True
            or shared.get("max_physical_joint_generations_per_source") != 6):
        raise ValueError("Test freeze does not match the runner threshold or protocol")
    runner_artifact = next((item for item in value.get("frozen_artifacts", [])
                            if item.get("role") == "research_runner"), None)
    current_runner_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if not runner_artifact or runner_artifact.get("sha256") != current_runner_sha:
        raise ValueError("Test freeze does not bind the current research runner")
    return value
