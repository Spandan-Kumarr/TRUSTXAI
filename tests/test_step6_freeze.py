import json
from pathlib import Path

import pytest

from trustxai.research_freeze import (
    FreezeError, THRESHOLD_GRID, create_freeze, default_artifacts,
    load_label_blind_test_inputs, verify_freeze,
)


def write(path: Path, value) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")
    return path


@pytest.fixture
def freeze_inputs(tmp_path):
    evidence = write(tmp_path / "development-evidence.json", {
        "split": "development", "status": "complete",
        "sources_expected": 40, "sources_completed": 40,
        "test_sources_accessed": 0,
    })
    matrix = write(tmp_path / "development-matrix.json", {
        "split": "development", "status": "complete",
        "sources_expected": 40, "sources_completed": 40,
        "test_sources_accessed": 0,
        "conditions": ["B0", "B1", "B2", "B3", "B4", "P"],
        "shared_initial_per_source": True,
        "gold_fields_entered_inference": False,
    })
    calibration = write(tmp_path / "calibration.json", {
        "split": "development", "status": "complete",
        "sources_expected": 40, "sources_completed": 40,
        "test_sources_accessed": 0, "variants_expected": 480,
        "threshold_grid": list(THRESHOLD_GRID),
        "supported_acceptance_by_threshold": {
            "0.6": 0.98, "0.7": 0.96, "0.8": 0.93, "0.9": 0.91, "0.95": 0.87,
        },
        "selected_threshold": 0.9,
        "label_status": "automated_construction_intent",
    })
    projection = write(tmp_path / "projection.json", {
        "status": "refreshed_after_development",
        "development_sources": 40, "test_sources": 60,
        "max_physical_joint_generations_per_source": 6,
        "worst_case_joint_generations_all_sources": 600,
        "research_communicator_context_tokens": 2048,
        "observed_development_CPU_hours": 7.0,
        "projected_test_CPU_hours": 10.0,
        "projected_aggregate_CPU_hours": 17.0,
        "CPU_hour_limit": 24.0,
        "budget_gate_pass": True,
        "observed_development_repair_rates": {"B3": 0.4, "P": 0.6},
    })
    test_inputs = write(tmp_path / "test-inputs.json", [
        {
            "source_id": f"opaque-{index:03d}",
            "question": "Which diagnosis is most likely?",
            "contexts": ["Finding one. ", "Finding two."],
            "options": {"A": "A condition", "B": "B condition", "C": "C condition", "D": "D condition"},
            "input_sha256": f"hash-{index}",
        }
        for index in range(60)
    ])
    artifact = tmp_path / "frozen-code.py"
    artifact.write_text("FROZEN = True\n")
    return {
        "repo_root": tmp_path,
        "output": tmp_path / "STEP_06_FREEZE.json",
        "development_evidence": evidence,
        "development_matrix": matrix,
        "calibration_path": calibration,
        "projection_path": projection,
        "test_inputs": test_inputs,
        "artifacts": [("test_code", artifact)],
        "recorded_at": "2026-10-27T16:00:00+05:30",
    }


def test_complete_development_can_create_and_verify_immutable_freeze(freeze_inputs):
    record = create_freeze(**freeze_inputs)
    path = freeze_inputs["output"]
    verified, digest = verify_freeze(path)
    assert verified == record
    assert record["checker"]["selected_operating_threshold"] == 0.9
    assert record["checker"]["independent_semantic_validation"] is False
    assert record["shared_generation_policy"]["max_physical_joint_generations_per_source"] == 6
    assert record["shared_generation_policy"]["corrected_worst_case_all_100_sources"] == 600
    assert len(digest) == 64
    assert path.stat().st_mode & 0o222 == 0
    assert path.with_suffix(".json.sha256").stat().st_mode & 0o222 == 0
    with pytest.raises(FreezeError, match="cannot be replaced"):
        create_freeze(**freeze_inputs)


def test_default_freeze_inventory_binds_manifest_builder():
    repo_root = Path(__file__).resolve().parents[1]
    inventory = dict(default_artifacts(repo_root))
    expected = repo_root / "research/step-06/scripts/build_run_manifests.py"
    assert inventory["manifest_builder"] == expected
    assert expected.is_file()


def test_incomplete_or_nonshared_development_is_refused(freeze_inputs):
    evidence = json.loads(freeze_inputs["development_evidence"].read_text())
    evidence["sources_completed"] = 39
    write(freeze_inputs["development_evidence"], evidence)
    with pytest.raises(FreezeError, match="all 40"):
        create_freeze(**freeze_inputs)

    evidence["sources_completed"] = 40
    write(freeze_inputs["development_evidence"], evidence)
    matrix = json.loads(freeze_inputs["development_matrix"].read_text())
    matrix["shared_initial_per_source"] = False
    write(freeze_inputs["development_matrix"], matrix)
    with pytest.raises(FreezeError, match="shared"):
        create_freeze(**freeze_inputs)


def test_highest_eligible_threshold_is_enforced(freeze_inputs):
    calibration = json.loads(freeze_inputs["calibration_path"].read_text())
    calibration["selected_threshold"] = 0.8
    write(freeze_inputs["calibration_path"], calibration)
    with pytest.raises(FreezeError, match="highest"):
        create_freeze(**freeze_inputs)


def test_no_eligible_threshold_requires_explicit_pretest_deviation(freeze_inputs):
    calibration = json.loads(freeze_inputs["calibration_path"].read_text())
    calibration["supported_acceptance_by_threshold"] = {
        str(value): 0.75 for value in THRESHOLD_GRID
    }
    calibration["selected_threshold"] = None
    write(freeze_inputs["calibration_path"], calibration)
    with pytest.raises(FreezeError, match="fallback"):
        create_freeze(**freeze_inputs)

    deviation = write(freeze_inputs["repo_root"] / "deviation.json", {
        "declared_before_test_access": True,
        "test_sources_accessed": 0,
        "fallback_threshold": 0.6,
        "reason": "No grid threshold retained the planned supported-variant acceptance; 0.60 is a declared fallback and the gate failure remains reported.",
    })
    freeze_inputs.update(fallback_threshold=0.6, deviation_path=deviation)
    record = create_freeze(**freeze_inputs)
    assert record["checker"]["development_target_met"] is False
    assert record["checker"]["selected_operating_threshold"] == 0.6
    assert record["checker"]["deviation"]["declared_before_test_access"] is True


@pytest.mark.parametrize(("field", "value"), [
    ("max_physical_joint_generations_per_source", 4),
    ("worst_case_joint_generations_all_sources", 400),
    ("research_communicator_context_tokens", 4096),
])
def test_old_compute_projection_cannot_lock_test(freeze_inputs, field, value):
    projection = json.loads(freeze_inputs["projection_path"].read_text())
    projection[field] = value
    write(freeze_inputs["projection_path"], projection)
    with pytest.raises(FreezeError, match=field):
        create_freeze(**freeze_inputs)


def test_over_budget_projection_needs_pretest_allocation_amendment(freeze_inputs):
    projection = json.loads(freeze_inputs["projection_path"].read_text())
    projection.update(projected_test_CPU_hours=20.0, projected_aggregate_CPU_hours=27.0,
                      budget_gate_pass=False)
    write(freeze_inputs["projection_path"], projection)
    with pytest.raises(FreezeError, match="allocation amendment"):
        create_freeze(**freeze_inputs)
    projection["budget_amendment"] = {
        "declared_before_test_access": True,
        "reason": "Preserve every planned case and checkpoint before the revised ceiling.",
    }
    write(freeze_inputs["projection_path"], projection)
    record = create_freeze(**freeze_inputs)
    assert record["compute_projection"]["budget_gate_pass"] is False


def test_public_freeze_rejects_raw_case_or_output_text(freeze_inputs):
    projection = json.loads(freeze_inputs["projection_path"].read_text())
    projection["case_text"] = "Raw held-out text must remain outside Git."
    write(freeze_inputs["projection_path"], projection)
    with pytest.raises(FreezeError, match="raw case/output"):
        create_freeze(**freeze_inputs)


def test_mutable_or_tampered_freeze_is_refused(freeze_inputs):
    create_freeze(**freeze_inputs)
    path = freeze_inputs["output"]
    path.chmod(0o644)
    with pytest.raises(FreezeError, match="mutable"):
        verify_freeze(path)
    path.chmod(0o444)
    checksum = path.with_suffix(".json.sha256")
    checksum.chmod(0o644)
    checksum.write_text("0" * 64 + f"  {path.name}\n")
    checksum.chmod(0o444)
    with pytest.raises(FreezeError, match="mismatch"):
        verify_freeze(path)


def test_first_label_blind_test_access_is_recorded_once(freeze_inputs):
    create_freeze(**freeze_inputs)
    access = freeze_inputs["repo_root"] / "private" / "TEST_ACCESS.json"
    rows = load_label_blind_test_inputs(
        freeze_path=freeze_inputs["output"], inputs_path=freeze_inputs["test_inputs"],
        access_record_path=access, accessed_at="2026-10-28T09:00:00+05:30")
    assert len(rows) == 60
    first = access.read_bytes()
    event = json.loads(first)
    assert event["outcomes_exposed"] is False
    assert event["gold_loaded"] is False
    assert event["predictions_loaded"] is False
    assert access.stat().st_mode & 0o222 == 0
    load_label_blind_test_inputs(
        freeze_path=freeze_inputs["output"], inputs_path=freeze_inputs["test_inputs"],
        access_record_path=access, accessed_at="2099-01-01T00:00:00Z")
    assert access.read_bytes() == first


def test_test_loader_rejects_outcome_fields_without_recording_access(freeze_inputs):
    rows = json.loads(freeze_inputs["test_inputs"].read_text())
    rows[0]["answer_idx"] = "A"
    write(freeze_inputs["test_inputs"], rows)
    create_freeze(**freeze_inputs)
    access = freeze_inputs["repo_root"] / "TEST_ACCESS.json"
    with pytest.raises(FreezeError, match="forbidden outcome fields"):
        load_label_blind_test_inputs(
            freeze_path=freeze_inputs["output"], inputs_path=freeze_inputs["test_inputs"],
            access_record_path=access)
    assert not access.exists()


def test_test_loader_requires_exact_frozen_input_digest(freeze_inputs):
    create_freeze(**freeze_inputs)
    path = freeze_inputs["test_inputs"]
    rows = json.loads(path.read_text())
    rows[0]["question"] += " changed"
    write(path, rows)
    with pytest.raises(FreezeError, match="do not match"):
        load_label_blind_test_inputs(
            freeze_path=freeze_inputs["output"], inputs_path=path,
            access_record_path=freeze_inputs["repo_root"] / "TEST_ACCESS.json")
