import importlib.util
import json
from pathlib import Path

import pytest

from trustxai.domain import digest
from trustxai import research_freeze


SCRIPT = Path(__file__).parents[1] / "research/step-06/scripts/build_run_manifests.py"
SPEC = importlib.util.spec_from_file_location("step6_manifests", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n")


def payload(source_id, stage, shared=True):
    base = {
        "source_id": source_id,
        "input_sha256": "a" * 64,
        "time": {"CPU_seconds": 10.0, "wall_seconds": 3.0},
    }
    if stage == "evidence":
        base.update({
            "decision": {"label": "A"},
            "omissions": [{"span_id": "S1", "label": "B"}],
            "selected": {"span_id": "S1", "label": "B"},
            "recheck": {"label": "B"},
        })
    else:
        common = "shared" if shared else None
        conditions = {}
        for condition in MODULE.CONDITIONS:
            conditions[condition] = {
                "status": "generated",
                "llm_narrative_applicable": condition != "B4",
                "repair_used": condition in {"B3", "P"},
            }
            if condition in {"B1", "B2", "B3", "P"}:
                conditions[condition]["initial_generation_id"] = common
        if not shared:
            conditions["B1"]["initial_generation_id"] = "one"
            conditions["B2"]["initial_generation_id"] = "two"
        base.update({
            "conditions": conditions,
            "config": {"nli_threshold": 0.90},
            "cost": {
                "physical_narrative_calls": 6,
                "physical_critic_calls": 1,
                "physical_generation_CPU_seconds": 8.0,
                "physical_generation_wall_seconds": 2.0,
            },
        })
    return base


def runtime(tmp_path, count=40, shared=True):
    root = tmp_path / "private"
    signatures = {"evidence": "e" * 64, "matrix": "m" * 64}
    write_json(root / "RUN_SIGNATURE.json", {
        "schema": MODULE.RUNNER_SCHEMA,
        "signatures": signatures,
        "metadata": {},
    })
    for stage in ("evidence", "matrix"):
        for index in range(count):
            source_id = f"case-{index:02d}"
            item = payload(source_id, stage, shared)
            envelope = {
                "schema": MODULE.RUNNER_SCHEMA,
                "stage": stage,
                "partition": "development",
                "source_id": source_id,
                "input_sha256": "a" * 64,
                "stage_signature": signatures[stage],
                "payload_sha256": digest(item),
                "payload": item,
            }
            write_json(root / "development" / stage / f"{source_id}.json", envelope)
    return root


def diagnostic_runtime(root, count=40):
    thresholds = {str(value): {"typed_plus_nli": "accept", "nli_only": "accept"}
                  for value in (0.60, 0.70, 0.80, 0.90, 0.95)}
    pair = {"novice": {"C1": "a", "C2": "b", "C3": "c", "C4": "d"},
            "expert": {"C1": "a", "C2": "b", "C3": "c", "C4": "d"}}
    for index in range(count):
        source_id = f"case-{index:02d}"
        variants = [{
            "slot": slot,
            "variant_id": f"{source_id}-V{slot:02d}",
            "source_id": source_id,
            "instantiation_status": "instantiated",
            "pair": pair,
            "pair_sha256": MODULE.canonical_digest(pair),
            "decisions": thresholds,
        } for slot in range(1, 13)]
        controlled = {
            "schema": "trustxai-step6-controlled-diagnostics-2",
            "split": "development", "source_id": source_id,
            "evidence_input_sha256": "a" * 64,
            "matrix_file_sha256": None, "config_signature": "c" * 64,
            "variants": variants,
        }
        write_json(root / "development/diagnostics" / f"{source_id}.json", controlled)
        finals = [{"condition": condition, "stage": "final",
                   "automated_proxy_decision": "accept"}
                  for condition in MODULE.CONDITIONS]
        records = finals + [{"condition": "P", "stage": "initial",
                             "automated_proxy_decision": "accept"}]
        matrix_path = root / "development/matrix" / f"{source_id}.json"
        natural = {
            "schema": "trustxai-step6-natural-diagnostics-1",
            "split": "development", "source_id": source_id,
            "evidence_input_sha256": "a" * 64,
            "matrix_file_sha256": MODULE.file_sha256(matrix_path),
            "config_signature": "d" * 64, "frozen_threshold": 0.90,
            "records": records,
        }
        write_json(root / "development/natural-diagnostics" / f"{source_id}.json", natural)
    return root / "development/diagnostics", root / "development/natural-diagnostics"


def test_builds_freeze_compatible_complete_manifests_and_projection(tmp_path):
    root = runtime(tmp_path)
    evidence, _ = MODULE.build_evidence_manifest(root, "development")
    matrix, _ = MODULE.build_matrix_manifest(root, "development")
    projection = MODULE.build_projection(
        evidence, matrix, diagnostics_cpu_seconds=400.0, cpu_hour_limit=24.0)

    assert evidence["status"] == matrix["status"] == "complete"
    assert evidence["sources_expected"] == evidence["sources_completed"] == 40
    assert matrix["conditions"] == list(MODULE.CONDITIONS)
    assert matrix["shared_initial_per_source"] is True
    assert matrix["aggregate"]["physical_narrative_calls"] == 240
    assert projection["status"] == "refreshed_after_development"
    assert projection["max_physical_joint_generations_per_source"] == 6
    assert projection["worst_case_joint_generations_all_sources"] == 600
    assert projection["research_communicator_context_tokens"] == 2048
    assert projection["projected_aggregate_CPU_hours"] == pytest.approx(0.8333333333)
    assert not MODULE.raw_text_locations(evidence)
    assert not MODULE.raw_text_locations(matrix)
    assert not MODULE.raw_text_locations(projection)
    assert research_freeze._validate_complete_development(evidence, "evidence")
    assert research_freeze._validate_matrix(matrix)
    assert research_freeze.validate_projection(projection)


def test_detects_tampered_payload(tmp_path):
    root = runtime(tmp_path, count=1)
    path = root / "development/evidence/case-00.json"
    value = json.loads(path.read_text())
    value["payload"]["time"]["CPU_seconds"] = 999
    write_json(path, value)
    with pytest.raises(MODULE.ManifestError, match="payload digest mismatch"):
        MODULE.build_evidence_manifest(root, "development")


def test_rejects_nonshared_initial(tmp_path):
    root = runtime(tmp_path, count=1, shared=False)
    with pytest.raises(MODULE.ManifestError, match="shared-initial"):
        MODULE.build_matrix_manifest(root, "development")


def test_incomplete_set_is_not_claimed_complete(tmp_path):
    root = runtime(tmp_path, count=3)
    evidence, _ = MODULE.build_evidence_manifest(root, "development")
    matrix, _ = MODULE.build_matrix_manifest(root, "development")
    projection = MODULE.build_projection(
        evidence, matrix, diagnostics_cpu_seconds=0.0, cpu_hour_limit=24.0)
    assert evidence["status"] == "incomplete"
    assert projection["status"] == "development_incomplete"
    assert projection["development_sources_observed"] == 3


def test_over_budget_requires_and_records_pretest_amendment(tmp_path):
    root = runtime(tmp_path)
    evidence, _ = MODULE.build_evidence_manifest(root, "development")
    matrix, _ = MODULE.build_matrix_manifest(root, "development")
    with pytest.raises(MODULE.ManifestError, match="budget amendment"):
        MODULE.build_projection(
            evidence, matrix, diagnostics_cpu_seconds=100_000.0, cpu_hour_limit=24.0)
    projection = MODULE.build_projection(
        evidence, matrix, diagnostics_cpu_seconds=100_000.0, cpu_hour_limit=24.0,
        budget_amendment_reason="Measured development cost requires more CPU allocation.")
    assert projection["budget_gate_pass"] is False
    assert projection["budget_amendment"]["declared_before_test_access"] is True
    assert projection["budget_amendment"]["workload_reduction"] is False


def test_public_writer_refuses_raw_text_keys(tmp_path):
    with pytest.raises(MODULE.ManifestError, match="raw-text"):
        MODULE.write_public(tmp_path / "leak.json", {"question": "private"})
    assert not (tmp_path / "leak.json").exists()


def test_prediction_freeze_binds_all_checkpoints_in_input_order(tmp_path):
    root = runtime(tmp_path)
    controlled_dir, natural_dir = diagnostic_runtime(root)
    evidence, evidence_rows = MODULE.build_evidence_manifest(root, "development")
    matrix, matrix_rows = MODULE.build_matrix_manifest(root, "development")
    assert evidence["status"] == matrix["status"] == "complete"
    inputs = [{"source_id": f"case-{index:02d}", "input_sha256": "a" * 64}
              for index in reversed(range(40))]
    inputs_path = root / "development_inputs.json"
    write_json(inputs_path, inputs)
    freeze = MODULE.build_prediction_freeze(
        "development", inputs_path, evidence_rows, matrix_rows,
        controlled_dir, natural_dir)
    assert freeze["status"] == "predictions_frozen"
    assert freeze["source_ids"] == [row["source_id"] for row in inputs]
    assert len(freeze["predictions_sha256"]) == 64
    assert freeze["gold_loaded"] is False
    assert not MODULE.raw_text_locations(freeze)
    destination = root / "development/PREDICTION_FREEZE.json"
    MODULE.write_prediction_freeze(destination, freeze)
    assert destination.stat().st_mode & 0o222 == 0
    MODULE.write_prediction_freeze(destination, freeze)  # identical rerun is safe


def test_prediction_freeze_rejects_missing_or_mismatched_checkpoint(tmp_path):
    root = runtime(tmp_path)
    controlled_dir, natural_dir = diagnostic_runtime(root)
    _, evidence_rows = MODULE.build_evidence_manifest(root, "development")
    _, matrix_rows = MODULE.build_matrix_manifest(root, "development")
    inputs = [{"source_id": f"case-{index:02d}", "input_sha256": "a" * 64}
              for index in range(40)]
    inputs[0]["input_sha256"] = "b" * 64
    inputs_path = root / "development_inputs.json"
    write_json(inputs_path, inputs)
    with pytest.raises(MODULE.ManifestError, match="digest mismatch"):
        MODULE.build_prediction_freeze(
            "development", inputs_path, evidence_rows, matrix_rows,
            controlled_dir, natural_dir)


def test_prediction_freeze_requires_both_complete_diagnostic_sets(tmp_path):
    root = runtime(tmp_path)
    controlled_dir, natural_dir = diagnostic_runtime(root)
    _, evidence_rows = MODULE.build_evidence_manifest(root, "development")
    _, matrix_rows = MODULE.build_matrix_manifest(root, "development")
    inputs_path = root / "development_inputs.json"
    write_json(inputs_path, [{"source_id": f"case-{index:02d}",
                              "input_sha256": "a" * 64}
                             for index in range(40)])
    (natural_dir / "case-00.json").unlink()
    with pytest.raises(MODULE.ManifestError, match="all and only expected"):
        MODULE.build_prediction_freeze(
            "development", inputs_path, evidence_rows, matrix_rows,
            controlled_dir, natural_dir)
