import hashlib
import json
from pathlib import Path

import pytest

from trustxai.domain import canonical_facts, digest
from trustxai.research_runner import (
    ArtifactMismatch, CpuBudgetExceeded, MatrixConfig, PrivateRunStore,
    build_signatures, execute_partition, extract_evidence, input_manifest_sha256,
    prepare_private_row, run_shared_matrix, validate_test_freeze,
)


class MatrixFake:
    target_identity = {"model": "target", "revision": "frozen", "decoding": "greedy"}
    communicator_identity = {"model": "communicator", "revision": "frozen",
                             "context_tokens": 2048, "temperature": 0}
    checker_identity = {"model": "checker", "revision": "frozen", "max_tokens": 512}

    def __init__(self, *, entailment=.99, critic_score=.99, labels=None):
        self.entailment, self.critic_score = entailment, critic_score
        self.labels = labels or {None: "A", "S1": "B", "S2": "A", "S3": "A"}
        self.classifications, self.generations, self.scored = [], [], []
        self.released = 0

    def classify(self, prepared, omitted=None):
        self.classifications.append(omitted)
        value = self.labels[omitted]
        if isinstance(value, list):
            value = value.pop(0)
        return {"label": value, "name": prepared["options"].get(value), "raw": value,
                "seconds": .01, "CPU_seconds": .02,
                "modified_input_sha256": digest({"question": prepared["question"],
                    "contexts": [span["text"] for span in prepared["spans"] if span["id"] != omitted],
                    "options": prepared["options"]})}

    def generate(self, system, user, cap=384):
        self.generations.append({"system": system, "user": user, "cap": cap})
        if "Critique explanation" in system:
            text = json.dumps({"score": self.critic_score, "feedback": "Preserve the fixed facts."})
        elif "Canonical facts:\n" in user:
            start = user.index("Canonical facts:\n") + len("Canonical facts:\n")
            facts = json.JSONDecoder().raw_decode(user[start:])[0]
            text = json.dumps({audience: dict(facts) for audience in ("novice", "expert")})
        else:
            text = json.dumps({audience: {f"C{i}": f"Ungated B0 statement {i}." for i in range(1, 5)}
                               for audience in ("novice", "expert")})
        return {"text": text, "seconds": .01, "CPU_seconds": .02,
                "prompt_tokens": 10, "new_tokens": 10, "finish_reason": "stop"}

    def score_pairs(self, pairs):
        self.scored.extend(pairs)
        return [{"status": "scored", "entailment": self.entailment,
                 "neutral": 1-self.entailment, "contradiction": 0} for _ in pairs]

    def memory(self):
        return {"peak_process_RSS_GiB": .01, "residency": "test fake"}

    def release_target(self):
        self.released += 1


def with_source(prepared, source_id="medqa-train-00001"):
    return {**prepared, "source_id": source_id}


def private_row(prepared, source_id="medqa-train-00001"):
    return {"source_id": source_id, "question": prepared["question"],
            "contexts": [span["text"] for span in prepared["spans"]],
            "options": prepared["options"], "input_sha256": prepared["input_sha256"],
            "original_question_sha256": "recorded-but-not-gold"}


def config(**changes):
    return MatrixConfig(**{"nli_threshold": .9, "critic_threshold": .9, **changes})


def test_target_evidence_is_extracted_once_with_all_spans_and_one_recheck(prepared):
    models = MatrixFake()
    record = extract_evidence(with_source(prepared), models)
    assert models.classifications == [None, "S1", "S2", "S3", "S1"]
    assert len(record["evidence"]["omissions"]) == len(prepared["spans"])
    assert record["evidence"]["selected"]["span_id"] == "S1"
    assert record["evidence"]["recheck"]["label"] == "B"
    assert record["facts"] == canonical_facts(record["evidence"])


def test_matrix_uses_one_exact_initial_for_b1_b2_b3_and_p(prepared):
    models = MatrixFake()
    evidence = extract_evidence(with_source(prepared), models)
    before = list(models.classifications)
    result = run_shared_matrix(evidence, models, config())
    assert models.classifications == before  # matrix never reruns target evidence
    shared = {result["conditions"][name]["initial_generation_id"]
              for name in ("B1", "B2", "B3", "P")}
    assert len(shared) == 1
    assert result["conditions"]["B1"]["attempt_generation_ids"][0] in shared
    assert len(result["conditions"]["B1"]["attempt_generation_ids"]) == 2
    assert len(result["conditions"]["B2"]["attempt_generation_ids"]) == 2
    assert result["conditions"]["B3"]["repair_used"] is False
    assert result["conditions"]["P"]["repair_used"] is False
    assert result["conditions"]["P"]["automated_release_passed"] is True
    assert result["conditions"]["B4"]["llm_narrative_applicable"] is False
    assert result["cost"]["physical_narrative_calls"] == 4
    assert result["cost"]["physical_critic_calls"] == 1
    assert result["cost"]["logical_narrative_opportunities_max"] == 9


def test_b3_and_p_each_use_at_most_one_repair_then_p_falls_back(prepared):
    models = MatrixFake(entailment=.01, critic_score=.1)
    evidence = extract_evidence(with_source(prepared), models)
    result = run_shared_matrix(evidence, models, config())
    assert result["conditions"]["B3"]["repair_used"] is True
    assert len(result["conditions"]["B3"]["attempt_generation_ids"]) == 3  # initial, critic, repair
    assert result["conditions"]["P"]["repair_used"] is True
    assert len(result["conditions"]["P"]["attempt_generation_ids"]) == 2
    assert len(result["conditions"]["P"]["checks"]) == 2
    assert result["conditions"]["P"]["status"] == "evidence_template"
    assert result["conditions"]["P"]["automated_release_passed"] is False
    assert result["cost"]["physical_narrative_calls"] == 6
    assert result["cost"]["physical_critic_calls"] == 1


def test_b0_remains_available_when_recheck_makes_audit_uninformative(prepared):
    models = MatrixFake(labels={None: "A", "S1": ["B", "C"], "S2": "A", "S3": "A"})
    evidence = extract_evidence(with_source(prepared), models)
    assert not evidence["informative_evidence"]
    result = run_shared_matrix(evidence, models, config())
    assert result["conditions"]["B0"]["status"] == "baseline_unchecked"
    assert result["conditions"]["B4"]["status"] == "evidence_template"
    assert all(result["conditions"][name]["status"] == "insufficient_evidence"
               for name in ("B1", "B2", "B3"))
    assert result["conditions"]["P"]["status"] == "evidence_template"
    assert result["cost"]["physical_narrative_calls"] == 1


def test_private_input_contract_rejects_gold_and_preserves_manifest_order(prepared):
    first = private_row(prepared, "medqa-train-00001")
    second = private_row(prepared, "medqa-train-00002")
    assert prepare_private_row(first)["source_id"] == first["source_id"]
    assert input_manifest_sha256([first, second]) != input_manifest_sha256([second, first])
    leaked = {**first, "answer_idx": "A"}
    with pytest.raises(ValueError, match="gold/answer"):
        prepare_private_row(leaked)


def test_atomic_checkpoints_resume_without_repeating_models(prepared, tmp_path):
    row = private_row(prepared)
    models = MatrixFake()
    cfg = config()
    signatures = build_signatures(models, cfg)
    store = PrivateRunStore(tmp_path, signatures, {"purpose": "unit test"})
    with store.exclusive():
        first = execute_partition([row], "development", models, store, cfg)
    assert first["evidence"] == 1 and first["matrix"] == 1
    assert (tmp_path / "development/evidence/medqa-train-00001.json").exists()
    assert (tmp_path / "development/matrix/medqa-train-00001.json").exists()
    progress = json.loads((tmp_path / "development/PROGRESS.json").read_text())
    assert progress["ordered_sources"][0]["matrix_complete"] is True

    resumed = MatrixFake()
    resumed_store = PrivateRunStore(tmp_path, build_signatures(resumed, cfg), {"purpose": "unit test"})
    with resumed_store.exclusive():
        second = execute_partition([row], "development", resumed, resumed_store, cfg)
    assert second["reused"] == 2
    assert resumed.classifications == [] and resumed.generations == []


def test_evidence_signature_survives_threshold_selection_and_matrix_freezes_once(prepared, tmp_path):
    row = private_row(prepared)
    provisional = config(nli_threshold=.9)
    evidence_models = MatrixFake()
    evidence_store = PrivateRunStore(tmp_path, build_signatures(evidence_models, provisional),
                                     {"purpose": "threshold transition"})
    with evidence_store.exclusive():
        execute_partition([row], "development", evidence_models, evidence_store,
                          provisional, stage="evidence")
    assert evidence_models.classifications
    signature_before = json.loads((tmp_path / "RUN_SIGNATURE.json").read_text())
    assert signature_before["signatures"]["matrix"] is None

    selected = config(nli_threshold=.6)
    matrix_models = MatrixFake()
    matrix_store = PrivateRunStore(tmp_path, build_signatures(matrix_models, selected),
                                   {"purpose": "threshold transition"})
    with matrix_store.exclusive():
        execute_partition([row], "development", matrix_models, matrix_store,
                          selected, stage="matrix")
    assert matrix_models.classifications == []
    signature_after = json.loads((tmp_path / "RUN_SIGNATURE.json").read_text())
    assert signature_after["signatures"]["matrix"] == build_signatures(matrix_models, selected)["matrix"]

    changed = config(nli_threshold=.9)
    changed_store = PrivateRunStore(tmp_path, build_signatures(MatrixFake(), changed),
                                    {"purpose": "threshold transition"})
    with changed_store.exclusive(), pytest.raises(ArtifactMismatch, match="already frozen"):
        execute_partition([row], "development", MatrixFake(), changed_store,
                          changed, stage="matrix")


def test_operational_budget_amendment_does_not_change_inference_signatures():
    models = MatrixFake()
    initial = config(cpu_budget_seconds=24 * 3600, cpu_reserve_seconds=900)
    amended = config(cpu_budget_seconds=36 * 3600, cpu_reserve_seconds=1800)
    assert build_signatures(models, initial) == build_signatures(models, amended)


def test_matrix_does_not_freeze_signature_before_evidence_exists(prepared, tmp_path):
    row = private_row(prepared)
    models = MatrixFake(); cfg = config()
    store = PrivateRunStore(tmp_path, build_signatures(models, cfg), {"purpose": "preflight"})
    with store.exclusive(), pytest.raises(RuntimeError, match="requires every"):
        execute_partition([row], "development", models, store, cfg, stage="matrix")
    assert not (tmp_path / "RUN_SIGNATURE.json").exists()


def test_checkpoint_integrity_and_cpu_budget_fail_closed(prepared, tmp_path):
    row = private_row(prepared)
    models = MatrixFake(); cfg = config()
    store = PrivateRunStore(tmp_path, build_signatures(models, cfg), {"purpose": "unit test"})
    with store.exclusive():
        store.initialize()
        store.save("evidence", "development", row["source_id"], row["input_sha256"], {"time": {"CPU_seconds": 2}})
    path = tmp_path / "development/evidence/medqa-train-00001.json"
    value = json.loads(path.read_text()); value["payload"]["time"]["CPU_seconds"] = 3
    path.write_text(json.dumps(value))
    with pytest.raises(ArtifactMismatch):
        store.load("evidence", "development", row["source_id"], row["input_sha256"])

    other = tmp_path / "budget"
    tight = config(cpu_budget_seconds=1, cpu_reserve_seconds=2)
    tight_store = PrivateRunStore(other, build_signatures(models, tight), {"purpose": "unit test"})
    with tight_store.exclusive(), pytest.raises(CpuBudgetExceeded):
        execute_partition([row], "development", models, tight_store, tight, stage="evidence")
    assert models.classifications == []


def test_held_out_test_requires_exact_reviewed_freeze(prepared, tmp_path):
    rows = [private_row(prepared, "medqa-test-00001")]
    models = MatrixFake(); cfg = config(); signatures = build_signatures(models, cfg)
    manifest = input_manifest_sha256(rows)
    runner_sha = hashlib.sha256(
        Path(__import__("trustxai.research_runner", fromlist=["x"]).__file__).read_bytes()
    ).hexdigest()
    freeze = {"schema": "trustxai.step6.freeze.v1", "status": "locked_before_test_access",
              "test_outcomes_seen_at_freeze": False, "seed": cfg.seed,
              "research_communicator_context_tokens": 2048,
              "gold_fields_entered_inference": False,
              "conditions": ["B0", "B1", "B2", "B3", "B4", "P"],
              "checker": {"selected_operating_threshold": cfg.nli_threshold},
              "shared_generation_policy": {"one_immutable_initial_per_source": True,
                  "max_physical_joint_generations_per_source": 6},
              "frozen_artifacts": [{"role": "research_runner", "sha256": runner_sha}]}
    path = tmp_path / "freeze.json"
    path.write_text(json.dumps(freeze, sort_keys=True, separators=(",", ":")) + "\n")
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    checksum = path.with_suffix(path.suffix + ".sha256")
    checksum.write_text(f"{sha}  {path.name}\n")
    path.chmod(0o444); checksum.chmod(0o444)
    assert validate_test_freeze(path, sha, signatures, manifest, cfg)["status"] == "locked_before_test_access"
    with pytest.raises(ValueError, match="hash"):
        validate_test_freeze(path, "0" * 64, signatures, manifest, cfg)
    changed = config(nli_threshold=.6)
    with pytest.raises(ValueError, match="threshold"):
        validate_test_freeze(path, sha, signatures, manifest, changed)


def test_research_context_and_threshold_grid_are_enforced():
    with pytest.raises(ValueError, match="frozen grid"):
        MatrixConfig(nli_threshold=.85, critic_threshold=.9)
    bad = MatrixFake(); bad.communicator_identity = {**bad.communicator_identity, "context_tokens": 4096}
    with pytest.raises(ValueError, match="2048"):
        build_signatures(bad, config())
