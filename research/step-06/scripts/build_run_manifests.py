#!/usr/bin/env python3
"""Build label-safe Step-6 completion manifests and the post-development projection.

The private runner checkpoints contain case text, prompts, and model output.  This
script verifies those checkpoints in place and publishes only identifiers,
digests, aggregate counts, and resource measurements.  It never copies a
checkpoint payload into the Git checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Iterable, Mapping


REPO = Path(__file__).resolve().parents[3]
DEFAULT_RUNTIME = Path(os.environ.get(
    "TRUSTXAI_STEP6_PRIVATE",
    "/workspace/thesis-runtime/clinical-cdss/step-06/private",
))
EXPECTED_SOURCES = {"development": 40, "test": 60}
CONDITIONS = ("B0", "B1", "B2", "B3", "B4", "P")
RUNNER_SCHEMA = "trustxai-step6-matrix-v1"
PUBLIC_SCHEMA = "trustxai.step6.public-run-manifest.v1"
PROJECTION_SCHEMA = "trustxai.step6.compute-projection.v1"
RAW_TEXT_KEYS = {
    "question", "case_text", "contexts", "options", "prompt", "prompt_text",
    "text", "raw", "generated_text", "output_text", "views", "generations",
    "facts", "novice", "expert", "evidence",
}


class ManifestError(RuntimeError):
    """A private checkpoint set cannot support a public completion claim."""


def canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=path.name + ".", delete=False) as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    os.replace(temporary, path)


def _read_object(path: Path, role: str) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise ManifestError(f"Cannot read valid {role} JSON: {path}") from error
    if not isinstance(value, dict):
        raise ManifestError(f"{role} must be a JSON object: {path}")
    return value


def _numeric(value: object, location: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        raise ManifestError(f"Missing or invalid non-negative measurement: {location}")
    return float(value)


def _checkpoint_rows(private_root: Path, split: str, stage: str) -> list[dict]:
    signature_path = private_root / "RUN_SIGNATURE.json"
    signature = _read_object(signature_path, "run signature")
    if signature.get("schema") != RUNNER_SCHEMA:
        raise ManifestError("Private runtime has an unrecognized runner schema")
    stage_signature = signature.get("signatures", {}).get(stage)
    if not isinstance(stage_signature, str) or len(stage_signature) != 64:
        raise ManifestError(f"The {stage} signature has not been frozen")

    directory = private_root / split / stage
    rows = []
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        envelope = _read_object(path, f"{stage} checkpoint")
        payload = envelope.get("payload")
        expected = {
            "schema": RUNNER_SCHEMA,
            "stage": stage,
            "partition": split,
            "stage_signature": stage_signature,
        }
        if any(envelope.get(key) != value for key, value in expected.items()):
            raise ManifestError(f"Checkpoint identity mismatch: {path}")
        source_id = envelope.get("source_id")
        input_sha = envelope.get("input_sha256")
        if not isinstance(source_id, str) or not source_id or path.name != f"{source_id}.json":
            raise ManifestError(f"Checkpoint source/file mismatch: {path}")
        if not isinstance(input_sha, str) or len(input_sha) != 64:
            raise ManifestError(f"Checkpoint has no valid input digest: {path}")
        if not isinstance(payload, dict) or payload.get("source_id") != source_id \
                or payload.get("input_sha256") != input_sha:
            raise ManifestError(f"Checkpoint payload binding mismatch: {path}")
        payload_sha = canonical_digest(payload)
        if envelope.get("payload_sha256") != payload_sha:
            raise ManifestError(f"Checkpoint payload digest mismatch: {path}")
        cpu = _numeric(payload.get("time", {}).get("CPU_seconds"),
                       f"{path}: payload.time.CPU_seconds")
        wall = _numeric(payload.get("time", {}).get("wall_seconds"),
                        f"{path}: payload.time.wall_seconds")
        rows.append({
            "source_id": source_id,
            "input_sha256": input_sha,
            "checkpoint_file_sha256": file_sha256(path),
            "payload_sha256": payload_sha,
            "CPU_seconds": cpu,
            "wall_seconds": wall,
            "payload": payload,
        })
    if len({row["source_id"] for row in rows}) != len(rows):
        raise ManifestError(f"Duplicate source identity in {split}/{stage}")
    return rows


def _public_members(rows: Iterable[Mapping[str, object]]) -> list[dict]:
    return [{key: row[key] for key in (
        "source_id", "input_sha256", "checkpoint_file_sha256", "payload_sha256")}
            for row in rows]


def _common_manifest(split: str, stage: str, rows: list[dict]) -> dict:
    expected = EXPECTED_SOURCES[split]
    members = _public_members(rows)
    completed = len(rows)
    return {
        "schema": PUBLIC_SCHEMA,
        "split": split,
        "stage": stage,
        "status": "complete" if completed == expected else "incomplete",
        "sources_expected": expected,
        "sources_completed": completed,
        "source_ids_sha256": canonical_digest(sorted(row["source_id"] for row in rows)),
        "checkpoint_set_sha256": canonical_digest(members),
        "members": members,
        "resource_totals": {
            "CPU_seconds": sum(row["CPU_seconds"] for row in rows),
            "wall_seconds": sum(row["wall_seconds"] for row in rows),
        },
        "test_sources_accessed": completed if split == "test" else 0,
        "raw_text_published": False,
        "gold_fields_entered_inference": False,
    }


def build_evidence_manifest(private_root: Path, split: str) -> tuple[dict, list[dict]]:
    rows = _checkpoint_rows(private_root, split, "evidence")
    manifest = _common_manifest(split, "evidence", rows)
    availability = 0
    valid_decisions = 0
    omission_tests = 0
    selected_rechecks = 0
    for row in rows:
        payload = row["payload"]
        evidence = payload.get("evidence", payload)
        if not isinstance(evidence, dict):
            raise ManifestError("Evidence checkpoint has no evidence object")
        decision = evidence.get("decision", {})
        omissions = evidence.get("omissions", [])
        selected = evidence.get("selected")
        recheck = evidence.get("recheck")
        valid = decision.get("label") in {"A", "B", "C", "D"}
        agreement = bool(selected and recheck and selected.get("label") in {"A", "B", "C", "D"}
                         and selected.get("label") == recheck.get("label"))
        valid_decisions += valid
        omission_tests += len(omissions) if isinstance(omissions, list) else 0
        selected_rechecks += bool(recheck)
        availability += bool(valid and omissions and agreement)
    manifest["aggregate"] = {
        "valid_frozen_decisions": valid_decisions,
        "omission_tests": omission_tests,
        "selected_result_rechecks": selected_rechecks,
        "informative_evidence_available": availability,
    }
    return manifest, rows


def build_prediction_freeze(split: str, inputs_path: Path,
                            evidence_rows: list[dict], matrix_rows: list[dict],
                            controlled_diagnostics_dir: Path,
                            natural_diagnostics_dir: Path) -> dict:
    """Bind every ordered input to all completed prediction/checker artifacts.

    The resulting digest freezes predictions before the separate gold-release
    command is allowed to inspect answer labels.  Evidence, matrix, controlled
    diagnostics and natural-output diagnostics must all be complete.  Payload
    text remains private; only verified checkpoint digests enter this record.
    """
    if split not in EXPECTED_SOURCES:
        raise ManifestError("Prediction freeze supports only development or test")
    try:
        inputs = json.loads(inputs_path.read_text())
    except (OSError, ValueError) as error:
        raise ManifestError(f"Cannot read ordered label-blind inputs: {inputs_path}") from error
    if not isinstance(inputs, list) or len(inputs) != EXPECTED_SOURCES[split]:
        raise ManifestError(
            f"Prediction freeze requires exactly {EXPECTED_SOURCES[split]} ordered {split} inputs")
    ordered = []
    seen = set()
    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            raise ManifestError(f"Input row {index} is not an object")
        source_id, input_sha = item.get("source_id"), item.get("input_sha256")
        if not isinstance(source_id, str) or source_id in seen:
            raise ManifestError("Ordered inputs have a missing or duplicate source identity")
        if not isinstance(input_sha, str) or len(input_sha) != 64:
            raise ManifestError(f"Ordered input {source_id} has no valid input digest")
        seen.add(source_id)
        ordered.append((source_id, input_sha))

    evidence = {row["source_id"]: row for row in evidence_rows}
    matrix = {row["source_id"]: row for row in matrix_rows}
    if set(evidence) != seen or set(matrix) != seen:
        raise ManifestError("All and only ordered inputs need completed evidence and matrix checkpoints")
    controlled = _diagnostic_checkpoint_rows(
        controlled_diagnostics_dir, split, "controlled", evidence, matrix)
    natural = _diagnostic_checkpoint_rows(
        natural_diagnostics_dir, split, "natural", evidence, matrix)
    if set(controlled) != seen or set(natural) != seen:
        raise ManifestError(
            "All and only ordered inputs need completed controlled and natural diagnostics")
    bindings = []
    for source_id, input_sha in ordered:
        evidence_row, matrix_row = evidence[source_id], matrix[source_id]
        if evidence_row["input_sha256"] != input_sha or matrix_row["input_sha256"] != input_sha:
            raise ManifestError(f"Prediction/input digest mismatch for {source_id}")
        bindings.append({
            "source_id": source_id,
            "input_sha256": input_sha,
            "evidence_payload_sha256": evidence_row["payload_sha256"],
            "matrix_payload_sha256": matrix_row["payload_sha256"],
            "controlled_diagnostics_file_sha256": controlled[source_id]["file_sha256"],
            "controlled_diagnostics_config_sha256": controlled[source_id]["config_signature"],
            "controlled_slots": controlled[source_id]["controlled_slots"],
            "natural_diagnostics_file_sha256": natural[source_id]["file_sha256"],
            "natural_diagnostics_config_sha256": natural[source_id]["config_signature"],
            "natural_final_rows": natural[source_id]["natural_final_rows"],
            "natural_P_initial_rows": natural[source_id]["natural_P_initial_rows"],
        })
    return {
        "schema": "trustxai.step6.prediction-freeze.v1",
        "split": split,
        "status": "predictions_frozen",
        "source_ids": [source_id for source_id, _ in ordered],
        "predictions_sha256": canonical_digest(bindings),
        "ordered_prediction_bindings_sha256": canonical_digest(bindings),
        "inputs_file_sha256": file_sha256(inputs_path),
        "sources": len(bindings),
        "evidence_and_matrix_complete": True,
        "controlled_diagnostics_complete": True,
        "natural_diagnostics_complete": True,
        "controlled_diagnostics_set_sha256": canonical_digest([
            {"source_id": row["source_id"],
             "file_sha256": controlled[row["source_id"]]["file_sha256"]}
            for row in inputs
        ]),
        "natural_diagnostics_set_sha256": canonical_digest([
            {"source_id": row["source_id"],
             "file_sha256": natural[row["source_id"]]["file_sha256"]}
            for row in inputs
        ]),
        "gold_loaded": False,
        "raw_text_published": False,
    }


def _informative_evidence(payload: dict) -> bool:
    declared = payload.get("informative_evidence")
    if isinstance(declared, bool):
        return declared
    evidence = payload.get("evidence", payload)
    if not isinstance(evidence, dict):
        raise ManifestError("Evidence payload has no evidence record")
    decision = evidence.get("decision", {})
    omissions = evidence.get("omissions", [])
    selected, recheck = evidence.get("selected"), evidence.get("recheck")
    return bool(decision.get("label") in {"A", "B", "C", "D"} and omissions and
                selected and recheck and selected.get("label") in {"A", "B", "C", "D"} and
                selected.get("label") == recheck.get("label"))


def _hex_digest(value: object, location: str) -> str:
    if not isinstance(value, str) or len(value) != 64 \
            or any(character not in "0123456789abcdef" for character in value):
        raise ManifestError(f"Missing or invalid SHA256 at {location}")
    return value


def _validate_controlled_diagnostic(record: dict, split: str, source_id: str,
                                    input_sha: str) -> dict:
    if (record.get("schema") != "trustxai-step6-controlled-diagnostics-2" or
            record.get("split") != split or record.get("source_id") != source_id or
            record.get("evidence_input_sha256") != input_sha or
            record.get("matrix_file_sha256") is not None):
        raise ManifestError(f"Controlled diagnostic binding mismatch for {source_id}")
    signature = _hex_digest(record.get("config_signature"),
                            f"controlled diagnostic {source_id} config")
    variants = record.get("variants")
    if not isinstance(variants, list) or len(variants) != 12:
        raise ManifestError(f"Controlled diagnostic {source_id} must retain all 12 slots")
    if {row.get("slot") for row in variants if isinstance(row, dict)} != set(range(1, 13)):
        raise ManifestError(f"Controlled diagnostic {source_id} has invalid slot identities")
    expected_ids = {f"{source_id}-V{index:02d}" for index in range(1, 13)}
    if {row.get("variant_id") for row in variants} != expected_ids \
            or any(row.get("source_id") != source_id for row in variants):
        raise ManifestError(f"Controlled diagnostic {source_id} has invalid variant binding")
    threshold_keys = {str(value) for value in (0.60, 0.70, 0.80, 0.90, 0.95)}
    for variant in variants:
        status, decisions = variant.get("instantiation_status"), variant.get("decisions")
        if status == "not_instantiated":
            if variant.get("pair") is not None or decisions != {}:
                raise ManifestError(f"Uninstantiated controlled slot is inconsistent for {source_id}")
            continue
        if status != "instantiated" or not isinstance(decisions, dict) \
                or set(decisions) != threshold_keys:
            raise ManifestError(f"Controlled diagnostic decisions are incomplete for {source_id}")
        if any(not isinstance(value, dict) or
               set(value) != {"typed_plus_nli", "nli_only"}
               for value in decisions.values()):
            raise ManifestError(f"Controlled diagnostic methods are incomplete for {source_id}")
        pair = variant.get("pair")
        if pair is None or variant.get("pair_sha256") != canonical_digest(pair):
            raise ManifestError(f"Controlled diagnostic pair digest mismatch for {source_id}")
    return {"config_signature": signature, "controlled_slots": 12}


def _validate_natural_diagnostic(record: dict, split: str, source_id: str,
                                 input_sha: str, evidence_row: dict,
                                 matrix_row: dict) -> dict:
    if (record.get("schema") != "trustxai-step6-natural-diagnostics-1" or
            record.get("split") != split or record.get("source_id") != source_id or
            record.get("evidence_input_sha256") != input_sha or
            record.get("matrix_file_sha256") != matrix_row["checkpoint_file_sha256"]):
        raise ManifestError(f"Natural diagnostic binding mismatch for {source_id}")
    signature = _hex_digest(record.get("config_signature"),
                            f"natural diagnostic {source_id} config")
    threshold = record.get("frozen_threshold")
    matrix_threshold = matrix_row["payload"].get("config", {}).get("nli_threshold")
    if threshold not in {0.60, 0.70, 0.80, 0.90, 0.95} or threshold != matrix_threshold:
        raise ManifestError(f"Natural diagnostic threshold mismatch for {source_id}")
    records = record.get("records")
    if not isinstance(records, list):
        raise ManifestError(f"Natural diagnostic {source_id} has no records")
    finals = [row for row in records if isinstance(row, dict) and row.get("stage") == "final"]
    initials = [row for row in records if isinstance(row, dict) and row.get("stage") == "initial"]
    if (len(finals) != 6 or {row.get("condition") for row in finals} != set(CONDITIONS) or
            len({row.get("condition") for row in finals}) != 6):
        raise ManifestError(f"Natural diagnostic {source_id} requires six B0-B4/P finals")
    informative = _informative_evidence(evidence_row["payload"])
    expected_initials = 1 if informative else 0
    if len(initials) != expected_initials or any(row.get("condition") != "P" for row in initials):
        raise ManifestError(
            f"Natural diagnostic {source_id} has the wrong P-initial count for evidence availability")
    if any(row.get("automated_proxy_decision") not in {"accept", "reject", "abstain"}
           for row in records):
        raise ManifestError(f"Natural diagnostic decisions are incomplete for {source_id}")
    return {"config_signature": signature, "natural_final_rows": 6,
            "natural_P_initial_rows": expected_initials}


def _diagnostic_checkpoint_rows(directory: Path, split: str, mode: str,
                                evidence: dict[str, dict],
                                matrix: dict[str, dict]) -> dict[str, dict]:
    if mode not in {"controlled", "natural"}:
        raise ValueError("Unknown diagnostic mode")
    files = sorted(directory.glob("*.json")) if directory.is_dir() else []
    if {path.stem for path in files} != set(evidence):
        raise ManifestError(
            f"{mode.title()} diagnostics must contain all and only expected source checkpoints")
    output = {}
    for path in files:
        source_id = path.stem
        record = _read_object(path, f"{mode} diagnostic checkpoint")
        input_sha = evidence[source_id]["input_sha256"]
        if mode == "controlled":
            details = _validate_controlled_diagnostic(record, split, source_id, input_sha)
        else:
            details = _validate_natural_diagnostic(
                record, split, source_id, input_sha, evidence[source_id], matrix[source_id])
        output[source_id] = {"file_sha256": file_sha256(path), **details}
    return output


def write_prediction_freeze(path: Path, value: dict) -> None:
    leaks = raw_text_locations(value)
    if leaks:
        raise ManifestError("Refusing prediction freeze with raw-text keys: " + ", ".join(leaks[:5]))
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    except FileExistsError:
        existing = _read_object(path, "prediction freeze")
        if existing != value:
            raise ManifestError("Refusing to replace a different prediction-freeze record")
        return
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    path.chmod(0o444)


def _condition_output(payload: dict, condition: str) -> dict:
    conditions = payload.get("conditions")
    if not isinstance(conditions, dict) or set(conditions) != set(CONDITIONS):
        raise ManifestError("Matrix checkpoint does not contain exactly B0-B4/P")
    value = conditions[condition]
    if not isinstance(value, dict):
        raise ManifestError(f"Matrix condition {condition} is not an object")
    return value


def _shared_initial_verified(payload: dict) -> bool:
    values = [_condition_output(payload, condition).get("initial_generation_id")
              for condition in ("B1", "B2", "B3", "P")]
    present = [value for value in values if value is not None]
    # No shared initial is expected when evidence is unavailable.  If any
    # condition uses one, all four must name the same immutable generation.
    return not present or (len(present) == 4 and len(set(present)) == 1)


def build_matrix_manifest(private_root: Path, split: str) -> tuple[dict, list[dict]]:
    rows = _checkpoint_rows(private_root, split, "matrix")
    manifest = _common_manifest(split, "matrix", rows)
    if any(not _shared_initial_verified(row["payload"]) for row in rows):
        raise ManifestError("B1/B2/B3/P shared-initial identity failed verification")

    condition_statuses = {condition: {} for condition in CONDITIONS}
    narrative_calls = critic_calls = 0
    generation_cpu = generation_wall = 0.0
    repairs = {"B3": 0, "P": 0}
    repair_eligible = {"B3": 0, "P": 0}
    p_fallbacks = 0
    for row in rows:
        payload = row["payload"]
        cost = payload.get("cost", {})
        calls = cost.get("physical_narrative_calls")
        critics = cost.get("physical_critic_calls")
        if not isinstance(calls, int) or isinstance(calls, bool) or not 0 <= calls <= 6:
            raise ManifestError("Physical narrative call count is outside the corrected maximum")
        if not isinstance(critics, int) or isinstance(critics, bool) or not 0 <= critics <= 1:
            raise ManifestError("Physical critic call count is outside the protocol maximum")
        narrative_calls += calls
        critic_calls += critics
        generation_cpu += _numeric(cost.get("physical_generation_CPU_seconds"),
                                   "cost.physical_generation_CPU_seconds")
        generation_wall += _numeric(cost.get("physical_generation_wall_seconds"),
                                    "cost.physical_generation_wall_seconds")
        for condition in CONDITIONS:
            output = _condition_output(payload, condition)
            status = str(output.get("status", "missing"))
            condition_statuses[condition][status] = condition_statuses[condition].get(status, 0) + 1
        for condition in ("B3", "P"):
            output = _condition_output(payload, condition)
            applicable = output.get("llm_narrative_applicable") is True and \
                output.get("status") not in {"insufficient_evidence", "invalid_frozen_decision"}
            repair_eligible[condition] += applicable
            repairs[condition] += bool(applicable and output.get("repair_used") is True)
        p_fallbacks += _condition_output(payload, "P").get("status") in {
            "evidence_template", "fallback", "source_passages", "status_only"
        }

    manifest.update({
        "conditions": list(CONDITIONS),
        "shared_initial_per_source": True,
        "aggregate": {
            "condition_status_counts": condition_statuses,
            "physical_narrative_calls": narrative_calls,
            "physical_critic_calls": critic_calls,
            "physical_generation_CPU_seconds": generation_cpu,
            "physical_generation_wall_seconds": generation_wall,
            "repair_counts": repairs,
            "repair_eligible_sources": repair_eligible,
            "P_fallbacks": p_fallbacks,
        },
    })
    return manifest, rows


def _diagnostic_cpu_seconds(path: Path | None, explicit: float | None) -> float:
    if explicit is not None:
        return _numeric(explicit, "--diagnostics-cpu-seconds")
    if path is None:
        raise ManifestError(
            "A complete compute projection requires --diagnostics-cpu-seconds "
            "or --diagnostics-timing-json"
        )
    record = _read_object(path, "diagnostics timing")
    for key in ("CPU_seconds", "cpu_seconds", "diagnostics_CPU_seconds",
                "total_CPU_seconds"):
        if key in record:
            return _numeric(record[key], f"{path}:{key}")
    resource = record.get("resource_totals")
    if isinstance(resource, dict) and "CPU_seconds" in resource:
        return _numeric(resource["CPU_seconds"], f"{path}:resource_totals.CPU_seconds")
    timing = record.get("time")
    if isinstance(timing, dict) and "CPU_seconds" in timing:
        return _numeric(timing["CPU_seconds"], f"{path}:time.CPU_seconds")
    if "user_CPU_seconds" in record and "system_CPU_seconds" in record:
        return (_numeric(record["user_CPU_seconds"], f"{path}:user_CPU_seconds") +
                _numeric(record["system_CPU_seconds"], f"{path}:system_CPU_seconds"))
    raise ManifestError("Diagnostics timing JSON has no recognized CPU-seconds field")


def build_projection(evidence_manifest: dict, matrix_manifest: dict, *,
                     diagnostics_cpu_seconds: float, cpu_hour_limit: float = 24.0,
                     budget_amendment_reason: str | None = None) -> dict:
    if evidence_manifest.get("split") != "development" \
            or matrix_manifest.get("split") != "development":
        raise ManifestError("The refreshed projection requires development manifests")
    complete = evidence_manifest.get("status") == matrix_manifest.get("status") == "complete"
    completed = min(int(evidence_manifest.get("sources_completed", 0)),
                    int(matrix_manifest.get("sources_completed", 0)))
    if completed <= 0:
        raise ManifestError("No completed development source is available for projection")
    evidence_cpu = _numeric(evidence_manifest["resource_totals"]["CPU_seconds"],
                            "evidence CPU seconds")
    matrix_cpu = _numeric(matrix_manifest["resource_totals"]["CPU_seconds"],
                          "matrix CPU seconds")
    diagnostic_cpu = _numeric(diagnostics_cpu_seconds, "diagnostics CPU seconds")
    observed_cpu_hours = (evidence_cpu + matrix_cpu + diagnostic_cpu) / 3600.0
    projected_test_hours = observed_cpu_hours * EXPECTED_SOURCES["test"] / completed
    aggregate_hours = observed_cpu_hours + projected_test_hours
    limit = _numeric(cpu_hour_limit, "CPU-hour limit")
    within = aggregate_hours <= limit
    if not within and not (budget_amendment_reason and budget_amendment_reason.strip()):
        raise ManifestError(
            "Projected aggregate exceeds the CPU-hour limit; declare a pre-test "
            "budget amendment reason rather than silently changing the workload"
        )
    matrix_aggregate = matrix_manifest["aggregate"]
    repair_rates = {}
    for condition in ("B3", "P"):
        numerator = int(matrix_aggregate["repair_counts"][condition])
        denominator = int(matrix_aggregate["repair_eligible_sources"][condition])
        repair_rates[condition] = {
            "repairs": numerator,
            "eligible_sources": denominator,
            "rate": numerator / denominator if denominator else None,
        }
    projection = {
        "schema": PROJECTION_SCHEMA,
        "status": "refreshed_after_development" if complete else "development_incomplete",
        "unit": "aggregate process CPU-hours (user+system), distinct from elapsed wall time",
        "development_sources": 40,
        "test_sources": 60,
        "development_sources_observed": completed,
        "max_physical_joint_generations_per_source": 6,
        "worst_case_joint_generations_all_sources": 600,
        "research_communicator_context_tokens": 2048,
        "previous_400_call_maximum_superseded": True,
        "observed_development_CPU_hours": observed_cpu_hours,
        "projected_test_CPU_hours": projected_test_hours,
        "projected_aggregate_CPU_hours": aggregate_hours,
        "CPU_hour_limit": limit,
        "budget_gate_pass": within,
        "observed_development_repair_rates": repair_rates,
        "observed_components_CPU_seconds": {
            "target_inference_and_omissions": evidence_cpu,
            "natural_matrix": matrix_cpu,
            "checker_diagnostics_and_posthoc_scoring": diagnostic_cpu,
        },
        "projection_method": "Scale all observed development components by 60/40 for held-out test",
        "all_100_sources_retained": True,
        "test_sources_accessed": 0,
        "raw_text_published": False,
    }
    if not within:
        projection["budget_amendment"] = {
            "declared_before_test_access": True,
            "test_sources_accessed": 0,
            "reason": budget_amendment_reason.strip(),
            "workload_reduction": False,
            "all_100_sources_retained": True,
        }
    return projection


def raw_text_locations(value: object, path: str = "$") -> list[str]:
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).casefold() in RAW_TEXT_KEYS:
                found.append(f"{path}.{key}")
            found.extend(raw_text_locations(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(raw_text_locations(child, f"{path}[{index}]"))
    return found


def write_public(path: Path, value: dict) -> None:
    leaks = raw_text_locations(value)
    if leaks:
        raise ManifestError("Refusing public artifact with raw-text keys: " + ", ".join(leaks[:5]))
    atomic_json(path, value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("development", "test"), required=True)
    parser.add_argument("--private-root", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--diagnostics-timing-json", type=Path)
    parser.add_argument("--diagnostics-cpu-seconds", type=float)
    parser.add_argument("--cpu-hour-limit", type=float, default=24.0)
    parser.add_argument("--budget-amendment-reason")
    parser.add_argument("--freeze-predictions", action="store_true",
                        help="Write the immutable prediction digest required before gold release")
    parser.add_argument("--inputs", type=Path,
                        help="Ordered label-blind inputs; defaults to PRIVATE_ROOT/SPLIT_inputs.json")
    parser.add_argument("--prediction-freeze-output", type=Path)
    parser.add_argument("--controlled-diagnostics-dir", type=Path)
    parser.add_argument("--natural-diagnostics-dir", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output_dir or REPO / "research" / "step-06" / args.split
    evidence, evidence_rows = build_evidence_manifest(args.private_root, args.split)
    matrix, matrix_rows = build_matrix_manifest(args.private_root, args.split)
    write_public(output / "EVIDENCE_MANIFEST.json", evidence)
    write_public(output / "MATRIX_MANIFEST.json", matrix)
    written = [str(output / "EVIDENCE_MANIFEST.json"), str(output / "MATRIX_MANIFEST.json")]
    if args.split == "development":
        diagnostics_cpu = _diagnostic_cpu_seconds(
            args.diagnostics_timing_json, args.diagnostics_cpu_seconds)
        projection = build_projection(
            evidence, matrix, diagnostics_cpu_seconds=diagnostics_cpu,
            cpu_hour_limit=args.cpu_hour_limit,
            budget_amendment_reason=args.budget_amendment_reason,
        )
        write_public(output / "COMPUTE_PROJECTION.json", projection)
        written.append(str(output / "COMPUTE_PROJECTION.json"))
    if args.freeze_predictions:
        inputs = args.inputs or args.private_root / f"{args.split}_inputs.json"
        prediction_freeze = build_prediction_freeze(
            args.split, inputs, evidence_rows, matrix_rows,
            args.controlled_diagnostics_dir or args.private_root / args.split / "diagnostics",
            args.natural_diagnostics_dir or args.private_root / args.split / "natural-diagnostics",
        )
        destination = (args.prediction_freeze_output or
                       args.private_root / args.split / "PREDICTION_FREEZE.json")
        write_prediction_freeze(destination, prediction_freeze)
        written.append(str(destination))
    print(json.dumps({
        "split": args.split,
        "status": evidence["status"] if evidence["status"] == matrix["status"] else "incomplete",
        "sources": min(evidence["sources_completed"], matrix["sources_completed"]),
        "public_artifacts": written,
        "raw_text_published": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
