"""Immutable Step 6 freeze and label-blind held-out access controls.

This module records provenance and enforces experiment sequencing. It does not
run inference, inspect gold labels, or imply independent semantic validation.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
from typing import Iterable, Mapping, Sequence


FREEZE_SCHEMA = "trustxai.step6.freeze.v1"
ACCESS_SCHEMA = "trustxai.step6.test-access.v1"
THRESHOLD_GRID = (0.60, 0.70, 0.80, 0.90, 0.95)
CONDITIONS = ("B0", "B1", "B2", "B3", "B4", "P")
FORBIDDEN_TEST_FIELDS = {
    "answer", "answer_idx", "correct_option", "gold", "gold_label",
    "label", "prediction", "outcome", "is_correct",
}
RAW_TEXT_KEYS = {
    "question", "case_text", "contexts", "options", "prompt_text",
    "generated_text", "output_text", "novice", "expert",
}


class FreezeError(RuntimeError):
    """The experiment is not eligible for held-out access."""


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise FreezeError(f"Cannot read valid JSON: {path}") from error


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_file(path: Path, role: str) -> None:
    if not path.is_file():
        raise FreezeError(f"Missing required {role} artifact: {path}")


def _int_field(record: Mapping[str, object], names: Sequence[str], role: str) -> int:
    for name in names:
        value = record.get(name)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if isinstance(value, list):
            return len(value)
    raise FreezeError(f"{role} does not record a completed source count")


def _validate_complete_development(record: object, role: str) -> dict:
    if not isinstance(record, dict):
        raise FreezeError(f"{role} manifest must be a JSON object")
    if record.get("split") not in ("development", "dev"):
        raise FreezeError(f"{role} manifest is not development-only")
    if str(record.get("status", "")).casefold() not in {
        "complete", "completed", "development_complete",
    }:
        raise FreezeError(f"{role} is not marked complete")
    expected = _int_field(record, ("sources_expected", "expected_sources", "source_count"), role)
    completed = _int_field(record, ("sources_completed", "completed_sources", "source_ids"), role)
    if expected != 40 or completed != 40:
        raise FreezeError(f"{role} must contain all 40 development sources")
    if record.get("test_sources_accessed", 0) not in (0, False, None):
        raise FreezeError(f"{role} was recorded after held-out access")
    return dict(record)


def _validate_matrix(record: object) -> dict:
    matrix = _validate_complete_development(record, "development matrix")
    conditions = matrix.get("conditions")
    if not isinstance(conditions, list) or set(conditions) != set(CONDITIONS):
        raise FreezeError("Development matrix must contain B0-B4 and P")
    if matrix.get("shared_initial_per_source") is not True:
        raise FreezeError("Matrix does not certify shared B1/B2/B3/P initial generation")
    if matrix.get("gold_fields_entered_inference") is not False:
        raise FreezeError("Matrix must certify that gold fields never entered inference")
    return matrix


def _float_map(record: object, role: str) -> dict[float, float]:
    if not isinstance(record, dict):
        raise FreezeError(f"{role} must be an object keyed by threshold")
    values: dict[float, float] = {}
    for key, value in record.items():
        try:
            threshold = float(key)
        except (TypeError, ValueError) as error:
            raise FreezeError(f"Invalid threshold in {role}: {key}") from error
        if threshold not in THRESHOLD_GRID or not isinstance(value, (int, float)):
            raise FreezeError(f"Invalid value in {role} at {key}")
        values[threshold] = float(value)
    if set(values) != set(THRESHOLD_GRID):
        raise FreezeError(f"{role} must report the complete threshold grid")
    return values


def _validate_deviation(record: object, fallback: float) -> dict:
    if not isinstance(record, dict):
        raise FreezeError("A no-eligible-threshold freeze requires a deviation record")
    if record.get("declared_before_test_access") is not True:
        raise FreezeError("Threshold deviation was not declared before held-out access")
    if record.get("test_sources_accessed", 0) not in (0, False, None):
        raise FreezeError("Threshold deviation was recorded after held-out access")
    if float(record.get("fallback_threshold", -1)) != fallback:
        raise FreezeError("Deviation fallback threshold does not match the freeze")
    if not str(record.get("reason", "")).strip():
        raise FreezeError("Threshold deviation requires a reason")
    return dict(record)


def validate_calibration(record: object, *, fallback_threshold: float | None = None,
                         deviation: object | None = None) -> tuple[dict, float, dict | None]:
    calibration = _validate_complete_development(record, "development calibration")
    if calibration.get("variants_expected") != 480:
        raise FreezeError("Calibration must retain all 480 requested development slots")
    if calibration.get("threshold_grid") != list(THRESHOLD_GRID):
        raise FreezeError("Calibration threshold grid differs from the protocol")
    acceptance = _float_map(calibration.get("supported_acceptance_by_threshold"),
                            "supported acceptance")
    selected = calibration.get("selected_threshold")
    eligible = [threshold for threshold in THRESHOLD_GRID if acceptance[threshold] >= 0.90]
    if selected is not None:
        selected = float(selected)
        if selected not in THRESHOLD_GRID:
            raise FreezeError("Selected threshold is outside the frozen grid")
        if not eligible or selected != max(eligible):
            raise FreezeError("Selected threshold is not the highest setting retaining 90% support")
        if fallback_threshold is not None or deviation is not None:
            raise FreezeError("A qualifying threshold cannot also use a fallback deviation")
        return calibration, selected, None
    if eligible:
        raise FreezeError("Calibration omitted an available qualifying threshold")
    if fallback_threshold is None or float(fallback_threshold) not in THRESHOLD_GRID:
        raise FreezeError("No threshold qualified; an explicit grid fallback is required")
    fallback = float(fallback_threshold)
    return calibration, fallback, _validate_deviation(deviation, fallback)


def validate_projection(record: object) -> dict:
    if not isinstance(record, dict):
        raise FreezeError("Refreshed compute projection must be a JSON object")
    if record.get("status") != "refreshed_after_development":
        raise FreezeError("Compute projection was not refreshed after development")
    required_exact = {
        "development_sources": 40,
        "test_sources": 60,
        "max_physical_joint_generations_per_source": 6,
        "worst_case_joint_generations_all_sources": 600,
        "research_communicator_context_tokens": 2048,
    }
    for key, expected in required_exact.items():
        if record.get(key) != expected:
            raise FreezeError(f"Compute projection must record {key}={expected}")
    numeric = (
        "observed_development_CPU_hours", "projected_test_CPU_hours",
        "projected_aggregate_CPU_hours", "CPU_hour_limit",
    )
    if any(not isinstance(record.get(key), (int, float)) or isinstance(record.get(key), bool)
           or float(record[key]) < 0 for key in numeric):
        raise FreezeError("Compute projection has missing/invalid CPU-hour fields")
    computed = float(record["observed_development_CPU_hours"]) + float(record["projected_test_CPU_hours"])
    if abs(computed - float(record["projected_aggregate_CPU_hours"])) > 1e-6:
        raise FreezeError("Projected aggregate CPU hours do not match development plus test")
    within = float(record["projected_aggregate_CPU_hours"]) <= float(record["CPU_hour_limit"])
    if record.get("budget_gate_pass") is not within:
        raise FreezeError("Compute budget gate is inconsistent with recorded hours")
    if not within:
        amendment = record.get("budget_amendment")
        if not isinstance(amendment, dict) or amendment.get("declared_before_test_access") is not True \
                or not str(amendment.get("reason", "")).strip():
            raise FreezeError("Over-budget projection requires a pre-test allocation amendment")
    if not isinstance(record.get("observed_development_repair_rates"), dict):
        raise FreezeError("Projection must include observed development repair rates")
    return dict(record)


def default_artifacts(repo_root: Path) -> list[tuple[str, Path]]:
    """Every implementation/configuration input that must be fixed before test."""
    relative = {
        "clinical_protocol": "research/step-04/clinical-cdss/STEP_04_CLINICAL_PROTOCOL.md",
        "split_manifest": "research/step-04/clinical-cdss/SPLIT_MANIFEST.csv",
        "experiment_config": "research/step-04/clinical-cdss/EXPERIMENT_CONFIG.json",
        "classification_prompt": "research/step-04/clinical-cdss/CLASSIFICATION_PROMPT.json",
        "model_revisions": "research/step-04/evidence/MODEL_REVISIONS.json",
        "native_build": "research/step-04/clinical-cdss/evidence/NATIVE_BUILD_PROVENANCE.json",
        "native_communicator": "research/step-04/clinical-cdss/evidence/NATIVE_COMMUNICATION_MODEL.json",
        "application_environment": "research/step-05/APP_ENVIRONMENT.json",
        "python_requirements": "requirements-app.txt",
        "frontend_lock": "frontend/package-lock.json",
        "domain_schema": "backend/trustxai/domain.py",
        "checker_code": "backend/trustxai/checks.py",
        "model_code": "backend/trustxai/models.py",
        "research_runner": "backend/trustxai/research_runner.py",
        "diagnostic_builder": "backend/trustxai/research_diagnostics.py",
        "analysis_code": "backend/trustxai/research_analysis.py",
        "freeze_code": "backend/trustxai/research_freeze.py",
        "runner_cli": "research/step-06/scripts/run_matrix.py",
        "diagnostics_cli": "research/step-06/scripts/run_diagnostics.py",
        "analysis_cli": "research/step-06/scripts/analyze_results.py",
        "manifest_builder": "research/step-06/scripts/build_run_manifests.py",
        "freeze_cli": "research/step-06/scripts/freeze_test.py",
        "annotation_protocol": "research/step-06/annotation/ANNOTATION_PROTOCOL.md",
        "annotation_rubric": "research/step-06/annotation/RUBRIC.json",
        "annotation_schema": "research/step-06/annotation/RESPONSE_SCHEMA.json",
    }
    return [(role, repo_root / path) for role, path in relative.items()]


def artifact_records(artifacts: Iterable[tuple[str, Path]], repo_root: Path) -> list[dict]:
    records = []
    seen = set()
    for role, path in artifacts:
        if role in seen:
            raise FreezeError(f"Duplicate artifact role: {role}")
        seen.add(role)
        path = path.resolve()
        _require_file(path, role)
        try:
            display = str(path.relative_to(repo_root.resolve()))
        except ValueError:
            display = path.name
        records.append({"role": role, "path": display, "bytes": path.stat().st_size,
                        "sha256": sha256_file(path)})
    return sorted(records, key=lambda row: row["role"])


def _digest_record(path: Path, role: str) -> dict:
    _require_file(path, role)
    return {"role": role, "filename": path.name, "bytes": path.stat().st_size,
            "sha256": sha256_file(path)}


def _write_immutable(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(path, flags, 0o444)
    except FileExistsError as error:
        raise FreezeError(f"Refusing to overwrite immutable artifact: {path}") from error
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        path.chmod(0o444)
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def create_freeze(*, repo_root: Path, output: Path, development_evidence: Path,
                  development_matrix: Path, calibration_path: Path, projection_path: Path,
                  test_inputs: Path, artifacts: Iterable[tuple[str, Path]] | None = None,
                  fallback_threshold: float | None = None, deviation_path: Path | None = None,
                  recorded_at: str | None = None) -> dict:
    repo_root = repo_root.resolve()
    evidence = _validate_complete_development(read_json(development_evidence),
                                              "development evidence")
    matrix = _validate_matrix(read_json(development_matrix))
    deviation = read_json(deviation_path) if deviation_path else None
    calibration, threshold, accepted_deviation = validate_calibration(
        read_json(calibration_path), fallback_threshold=fallback_threshold, deviation=deviation)
    projection = validate_projection(read_json(projection_path))
    raw_fields = _raw_text_fields(projection)
    if accepted_deviation:
        raw_fields.extend(_raw_text_fields(accepted_deviation, "$.checker.deviation"))
    if raw_fields:
        raise FreezeError("Public freeze inputs contain raw case/output fields: " + ", ".join(raw_fields[:5]))
    test_inputs_record = _digest_record(test_inputs, "label-blind test inputs")
    frozen_artifacts = artifact_records(artifacts or default_artifacts(repo_root), repo_root)
    input_records = [
        _digest_record(development_evidence, "development_evidence_manifest"),
        _digest_record(development_matrix, "development_matrix_manifest"),
        _digest_record(calibration_path, "development_calibration"),
        _digest_record(projection_path, "refreshed_compute_projection"),
        test_inputs_record,
    ]
    if deviation_path:
        input_records.append(_digest_record(deviation_path, "pre_test_deviation"))
    label_status = calibration.get("label_status", "unspecified")
    independent = label_status == "independently_reviewed"
    freeze = {
        "schema": FREEZE_SCHEMA,
        "recorded_at": recorded_at or _utc_now(),
        "status": "locked_before_test_access",
        "seed": 20261027,
        "source_counts": {"development": 40, "test": 60},
        "conditions": list(CONDITIONS),
        "checker": {
            "threshold_grid": list(THRESHOLD_GRID),
            "selected_operating_threshold": threshold,
            "development_target_met": calibration.get("selected_threshold") is not None,
            "selection_label_status": label_status,
            "independent_semantic_validation": independent,
            "deviation": accepted_deviation,
        },
        "shared_generation_policy": {
            "shared_conditions": ["B1", "B2", "B3", "P"],
            "one_immutable_initial_per_source": True,
            "max_physical_joint_generations_per_source": 6,
            "corrected_worst_case_all_100_sources": 600,
            "previous_400_call_maximum_superseded": True,
        },
        "research_communicator_context_tokens": 2048,
        "compute_projection": projection,
        "development_completion": {
            "evidence_sources": 40,
            "matrix_sources": 40,
            "diagnostic_slots": calibration.get("variants_expected"),
            "test_sources_accessed": 0,
        },
        "frozen_artifacts": frozen_artifacts,
        "input_artifacts": sorted(input_records, key=lambda row: row["role"]),
        "test_inputs": test_inputs_record,
        "gold_fields_entered_inference": False,
        "test_outcomes_seen_at_freeze": False,
        "claim_boundaries": {
            "independent_H1_available": independent,
            "clinical_validation_established": False,
            "GPT_or_Gemini_comparison_run": False,
        },
    }
    payload = canonical_json(freeze)
    checksum = sha256_bytes(payload)
    checksum_path = output.with_suffix(output.suffix + ".sha256")
    if output.exists() or checksum_path.exists():
        raise FreezeError("Freeze output or checksum already exists; immutable freezes cannot be replaced")
    _write_immutable(output, payload)
    try:
        _write_immutable(checksum_path, f"{checksum}  {output.name}\n".encode())
    except BaseException:
        output.chmod(0o600)
        output.unlink()
        raise
    return freeze


def _no_write_bits(path: Path) -> bool:
    return not (path.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def verify_freeze(path: Path, *, expected_sha256: str | None = None) -> tuple[dict, str]:
    checksum_path = path.with_suffix(path.suffix + ".sha256")
    _require_file(path, "test freeze")
    _require_file(checksum_path, "test freeze checksum")
    if not _no_write_bits(path) or not _no_write_bits(checksum_path):
        raise FreezeError("Test freeze or checksum is mutable")
    actual = sha256_file(path)
    parts = checksum_path.read_text().strip().split()
    if len(parts) != 2 or parts[0] != actual or parts[1] != path.name:
        raise FreezeError("Test freeze checksum mismatch")
    if expected_sha256 and actual != expected_sha256:
        raise FreezeError("Test freeze does not match the expected locked hash")
    record = read_json(path)
    if not isinstance(record, dict) or record.get("schema") != FREEZE_SCHEMA \
            or record.get("status") != "locked_before_test_access":
        raise FreezeError("Unrecognized or unlocked test freeze")
    if record.get("test_outcomes_seen_at_freeze") is not False:
        raise FreezeError("Freeze was not created before test outcomes")
    return record, actual


def _forbidden_fields(value: object, path: str = "$") -> list[str]:
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).casefold() in FORBIDDEN_TEST_FIELDS:
                found.append(f"{path}.{key}")
            found.extend(_forbidden_fields(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_forbidden_fields(child, f"{path}[{index}]"))
    return found


def _raw_text_fields(value: object, path: str = "$") -> list[str]:
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).casefold() in RAW_TEXT_KEYS:
                found.append(f"{path}.{key}")
            found.extend(_raw_text_fields(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_raw_text_fields(child, f"{path}[{index}]"))
    return found


def load_label_blind_test_inputs(*, freeze_path: Path, inputs_path: Path,
                                 access_record_path: Path,
                                 expected_freeze_sha256: str | None = None,
                                 accessed_at: str | None = None) -> list[dict]:
    freeze, freeze_hash = verify_freeze(freeze_path, expected_sha256=expected_freeze_sha256)
    if sha256_file(inputs_path) != freeze.get("test_inputs", {}).get("sha256"):
        raise FreezeError("Held-out inputs do not match the frozen label-blind file")
    inputs = read_json(inputs_path)
    if not isinstance(inputs, list) or len(inputs) != 60 or not all(isinstance(row, dict) for row in inputs):
        raise FreezeError("Held-out input file must contain exactly 60 records")
    forbidden = _forbidden_fields(inputs)
    if forbidden:
        raise FreezeError("Held-out input file contains forbidden outcome fields: " + ", ".join(forbidden[:5]))
    access = {
        "schema": ACCESS_SCHEMA,
        "event": "label_blind_test_inputs_first_opened",
        "accessed_at": accessed_at or _utc_now(),
        "freeze_sha256": freeze_hash,
        "test_inputs_sha256": sha256_file(inputs_path),
        "source_count": 60,
        "gold_loaded": False,
        "predictions_loaded": False,
        "outcomes_exposed": False,
    }
    if access_record_path.exists():
        existing = read_json(access_record_path)
        if not isinstance(existing, dict) or existing.get("schema") != ACCESS_SCHEMA \
                or existing.get("freeze_sha256") != freeze_hash \
                or existing.get("test_inputs_sha256") != access["test_inputs_sha256"]:
            raise FreezeError("Existing test-access record does not match this freeze/input file")
    else:
        _write_immutable(access_record_path, canonical_json(access))
    return inputs
