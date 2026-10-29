from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from trustxai.domain import CaseInput, digest, evidence_template, prepare_case
from trustxai.research_diagnostics import (
    FAULT_KINDS, SUPPORTED_KINDS, THRESHOLD_GRID,
    calibrate_thresholds, construct_variants, diagnostic_decision,
    natural_proxy_summary, score_natural_outputs, score_variants,
)


def evidence_record():
    prepared = prepare_case(CaseInput(
        case_text=("The first recorded finding contains enough words for one span. "
                   "The second recorded finding also contains enough words for another span."),
        question="Which of the following is the most likely diagnosis?",
        options={"A": "Alpha diagnosis", "B": "Beta diagnosis",
                 "C": "Gamma diagnosis", "D": "Delta diagnosis"},
        source_id="development-source-01",
    ))
    target = {"model": "test-target", "revision": "frozen"}
    signature = digest(target)
    for span in prepared["spans"]:
        assert prepared["case_text"][span["start"]:span["end"]] == span["text"]
    full_hash = digest({"question": prepared["question"],
                        "contexts": [row["text"] for row in prepared["spans"]],
                        "options": prepared["options"]})
    omission_hashes = {
        span["id"]: digest({"question": prepared["question"],
                            "contexts": [row["text"] for row in prepared["spans"]
                                         if row["id"] != span["id"]],
                            "options": prepared["options"]})
        for span in prepared["spans"]
    }
    omissions = [
        {"label": "B", "name": "Beta diagnosis", "raw": "B",
         "modified_input_sha256": omission_hashes["S1"], "span_id": "S1",
         "removed_characters": len(prepared["spans"][0]["text"]),
         "model_signature_sha256": signature, "changed": True},
        {"label": "A", "name": "Alpha diagnosis", "raw": "A",
         "modified_input_sha256": omission_hashes["S2"], "span_id": "S2",
         "removed_characters": len(prepared["spans"][1]["text"]),
         "model_signature_sha256": signature, "changed": False},
    ]
    return {
        **prepared,
        "target": target,
        "target_signature_sha256": signature,
        "decision": {"label": "A", "name": "Alpha diagnosis", "raw": "A",
                     "modified_input_sha256": full_hash,
                     "model_signature_sha256": signature},
        "omissions": omissions,
        "selected": omissions[0],
        "recheck": {"label": "B", "name": "Beta diagnosis", "raw": "B",
                    "modified_input_sha256": omission_hashes["S1"],
                    "model_signature_sha256": signature},
    }


def test_fixed_twelve_slots_and_explicit_construction_statuses():
    evidence = evidence_record()
    variants = construct_variants(evidence)
    assert len(variants) == 12
    assert [row["mutation_type"] for row in variants[:4]] == list(SUPPORTED_KINDS)
    assert [row["mutation_type"] for row in variants[4:]] == list(FAULT_KINDS)
    assert sum(row["construction_intent"] == "supported" for row in variants) == 4
    assert sum(row["construction_intent"] == "faulty" for row in variants) == 8
    assert all(row["independent_semantic_label"] is None for row in variants)
    assert all(row["label_status"].endswith("pending_independent_review") for row in variants)
    assert len({row["variant_id"] for row in variants}) == 12


def test_unavailable_mutations_keep_planned_slots_without_inventing_text():
    evidence = evidence_record()
    evidence["selected"] = None
    evidence["recheck"] = None
    variants = construct_variants(evidence)
    assert all(row["instantiation_status"] == "not_instantiated" for row in variants)
    assert all(row["pair"] is None and row["pair_sha256"] is None for row in variants)
    assert all("minimum informative evidence" in row["not_instantiated_reason"]
               for row in variants)
    assert len(variants) == 12


def test_unique_raw_nli_requests_are_scored_once_and_thresholds_are_derived():
    evidence = evidence_record()
    calls = []
    def scorer(pairs):
        calls.append(list(pairs))
        return [{"status": "scored", "entailment": 0.93,
                 "neutral": 0.06, "contradiction": 0.01} for _ in pairs]
    scored = score_variants(evidence, construct_variants(evidence), scorer,
                            evidence["target_signature_sha256"])
    assert len(calls) == 1
    assert len(calls[0]) == len(set(calls[0]))
    assert all(row["nli_complete"] for row in scored)
    assert all(row["min_entailment"] == 0.93 for row in scored)
    assert all(row["decisions"]["0.9"]["nli_only"] == "accept" for row in scored)
    assert all(row["decisions"]["0.95"]["nli_only"] == "reject" for row in scored)
    # Calibration consumes recorded scores and must not call the scorer again.
    result = calibrate_thresholds(scored)
    assert len(calls) == 1
    assert result["typed_plus_nli_selected_threshold"] == 0.9
    assert result["label_basis"].endswith("pending_independent_review")
    assert result["independent_semantic_validation"] is False


def test_supported_constructions_pass_typed_binding_but_faults_exercise_guards():
    evidence = evidence_record()
    scored = score_variants(
        evidence, construct_variants(evidence),
        lambda pairs: [{"status": "scored", "entailment": 0.99,
                        "neutral": 0.005, "contradiction": 0.005} for _ in pairs],
        evidence["target_signature_sha256"],
    )
    supported = [row for row in scored if row["construction_intent"] == "supported"]
    assert all(not row["typed_issues"] for row in supported)
    faults = {row["mutation_type"]: row for row in scored
              if row["construction_intent"] == "faulty"}
    assert any(issue["code"] == "decision_binding" for issue in faults["option_name"]["typed_issues"])
    assert any(issue["code"] == "span_binding" for issue in faults["span_binding"]["typed_issues"])
    assert any(issue["code"] == "count_binding" for issue in faults["counts"]["typed_issues"])
    assert any(issue["code"] == "missing_scope" for issue in faults["missing_limitation"]["typed_issues"])
    assert faults["unsupported_clinical_clause"]["decisions"]["0.9"]["typed_plus_nli"] == "accept"
    # The deliberately permissive fake demonstrates why NLI behavior still needs review.


def _calibration_rows(supported_acceptance_by_threshold):
    rows = []
    for index in range(10):
        decisions = {}
        for threshold in THRESHOLD_GRID:
            accepted_count = supported_acceptance_by_threshold[threshold]
            decisions[str(threshold)] = {
                "typed_plus_nli": "accept" if index < accepted_count else "reject",
                "nli_only": "accept",
            }
        rows.append({"source_id": f"S{index}", "variant_id": f"S{index}-V1",
                     "construction_intent": "supported", "mutation_type": "exact_canonical",
                     "instantiation_status": "instantiated", "decisions": decisions})
    return rows


def test_selects_highest_eligible_threshold_and_higher_tie_for_nli_only():
    rows = _calibration_rows({0.6: 10, 0.7: 10, 0.8: 9, 0.9: 9, 0.95: 8})
    result = calibrate_thresholds(rows)
    assert result["typed_plus_nli_selected_threshold"] == 0.9
    # NLI-only acceptance is 1.0 at every point; equal-distance ties choose higher.
    assert result["nli_only_matched_threshold"] == 0.95


def test_records_no_eligible_threshold_instead_of_silently_choosing_one():
    rows = _calibration_rows({value: 8 for value in THRESHOLD_GRID})
    result = calibrate_thresholds(rows)
    assert result["typed_plus_nli_selected_threshold"] is None
    assert result["typed_plus_nli_selection_status"] == "no_eligible_threshold"
    assert result["nli_only_matched_threshold"] is None


def test_unresolved_nli_is_always_abstention_never_acceptance():
    assert diagnostic_decision([], [], 0.6) == "abstain"
    unresolved = [{"status": "unresolved", "reason": "over context"}]
    assert diagnostic_decision([], unresolved, 0.6) == "abstain"
    assert diagnostic_decision([{"code": "count_binding"}], unresolved, 0.6) == "abstain"


def test_full_development_calibration_emits_freeze_compatible_completion_fields():
    rows = []
    for source_index in range(40):
        for slot_index in range(12):
            supported = slot_index < 4
            decisions = {
                str(threshold): {
                    "typed_plus_nli": "accept" if supported else "reject",
                    "nli_only": "accept" if supported else "reject",
                }
                for threshold in THRESHOLD_GRID
            }
            rows.append({
                "source_id": f"source-{source_index:02d}",
                "variant_id": f"source-{source_index:02d}-V{slot_index + 1:02d}",
                "construction_intent": "supported" if supported else "faulty",
                "mutation_type": (SUPPORTED_KINDS + FAULT_KINDS)[slot_index],
                "instantiation_status": "instantiated",
                "decisions": decisions,
            })
    result = calibrate_thresholds(rows)
    assert result["status"] == "complete"
    assert result["sources_completed"] == 40
    assert result["variants_expected"] == result["variants_completed"] == 480
    assert result["selected_threshold"] == result["typed_plus_nli_selected_threshold"] == 0.95
    assert result["supported_acceptance_by_threshold"] == {
        str(value): 1.0 for value in THRESHOLD_GRID
    }


def test_natural_outputs_are_scored_posthoc_without_rewriting_matrix_pairs():
    evidence = evidence_record()
    pair = evidence_template(evidence)
    outputs = [
        {"condition": condition, "stage": "final",
         "release_status": "evidence_template" if condition in {"B4", "P"} else "generated",
         "generation_id": None if condition == "B4" else f"generation-{condition}",
         "pair": deepcopy(pair)}
        for condition in ("B0", "B1", "B2", "B3", "B4", "P")
    ]
    before = deepcopy(outputs)
    records = score_natural_outputs(
        evidence, outputs,
        lambda pairs: [{"status": "scored", "entailment": 0.99,
                        "neutral": 0.005, "contradiction": 0.005} for _ in pairs],
        0.9, evidence["target_signature_sha256"],
    )
    assert outputs == before
    assert {row["condition"] for row in records} == {"B0", "B1", "B2", "B3", "B4", "P"}
    endpoints = {row["condition"]: row["automated_proxy_llm_pair_endpoint"]
                 for row in records}
    assert endpoints["B4"] == "not_applicable"
    assert endpoints["P"] == "fail"  # deterministic fallback is not generated LLM yield
    assert all(endpoints[name] == "pass" for name in ("B0", "B1", "B2", "B3"))
    summary = natural_proxy_summary(records)
    assert summary["independent_semantic_validation"] is False
    assert summary["conditions"]["B4"]["automated_proxy_llm_pair_yield"] is None
    assert summary["conditions"]["P"]["automated_proxy_llm_pair_yield"] == 0.0


def _load_diagnostics_cli():
    script = (Path(__file__).parents[1] /
              "research/step-06/scripts/run_diagnostics.py")
    spec = importlib.util.spec_from_file_location("step6_diagnostics_cli", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_matrix_adapter_adds_exact_shared_P_initial_without_modifying_checkpoint(tmp_path):
    module = _load_diagnostics_cli()
    evidence = evidence_record()
    pair = evidence_template(evidence)
    conditions = {
        condition: {
            "status": "generated" if condition == "P" else "baseline_unchecked",
            "views": deepcopy(pair),
            "final_generation_id": f"final-{condition}",
        }
        for condition in ("B0", "B1", "B2", "B3", "B4", "P")
    }
    conditions["B4"].update(status="evidence_template", final_generation_id=None)
    conditions["P"]["initial_generation_id"] = "shared-generation"
    payload = {
        "source_id": evidence["source_id"],
        "input_sha256": evidence["input_sha256"],
        "conditions": conditions,
        "generations": [{
            "generation_id": "shared-generation",
            "stage": "shared_initial_B1_B2_B3_P",
            "kind": "narrative",
            "output": {"text": json.dumps(pair)},
        }],
    }
    checkpoint = tmp_path / f"{evidence['source_id']}.json"
    checkpoint.write_text(json.dumps({"payload": payload}))
    original_bytes = checkpoint.read_bytes()

    items = module.matrix_items(
        checkpoint, evidence["source_id"], evidence["input_sha256"], True)
    assert checkpoint.read_bytes() == original_bytes
    assert len(items) == 7
    assert sum(row["stage"] == "final" for row in items) == 6
    initial = next(row for row in items if row["stage"] == "initial")
    assert initial == {
        "condition": "P", "stage": "initial", "release_status": "generated",
        "generation_id": "shared-generation", "pair": pair,
    }


def test_matrix_adapter_requires_P_initial_only_for_informative_evidence(tmp_path):
    module = _load_diagnostics_cli()
    evidence = evidence_record()
    pair = evidence_template(evidence)
    conditions = {
        condition: {"status": "insufficient_evidence", "views": deepcopy(pair),
                    "final_generation_id": None}
        for condition in ("B0", "B1", "B2", "B3", "B4", "P")
    }
    payload = {"source_id": evidence["source_id"],
               "input_sha256": evidence["input_sha256"],
               "conditions": conditions, "generations": []}
    checkpoint = tmp_path / f"{evidence['source_id']}.json"
    checkpoint.write_text(json.dumps({"payload": payload}))
    assert len(module.matrix_items(
        checkpoint, evidence["source_id"], evidence["input_sha256"], False)) == 6
    with pytest.raises(ValueError, match="lacks the P shared-initial ID"):
        module.matrix_items(
            checkpoint, evidence["source_id"], evidence["input_sha256"], True)


def test_heldout_freeze_requires_reviewed_sha_and_current_diagnostic_hashes(monkeypatch):
    module = _load_diagnostics_cli()
    from trustxai import research_freeze

    builder = module.REPO / "backend/trustxai/research_diagnostics.py"
    cli = Path(module.__file__).resolve()
    file_digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    record = {
        "checker": {"selected_operating_threshold": 0.9},
        "frozen_artifacts": [
            {"role": "diagnostic_builder",
             "path": str(builder.relative_to(module.REPO)),
             "sha256": file_digest(builder)},
            {"role": "diagnostics_cli",
             "path": str(cli.relative_to(module.REPO)),
             "sha256": file_digest(cli)},
        ],
    }
    calls = []

    def verified(path, *, expected_sha256=None):
        calls.append((path, expected_sha256))
        return record, "f" * 64

    monkeypatch.setattr(research_freeze, "verify_freeze", verified)
    freeze_path = Path("reviewed-freeze.json")
    with pytest.raises(ValueError, match="caller-reviewed"):
        module.read_freeze(freeze_path, "test")
    result = module.read_freeze(freeze_path, "test", "f" * 64)
    assert calls == [(freeze_path, "f" * 64)]
    assert result["threshold"] == 0.9 and result["file_sha256"] == "f" * 64

    record["frozen_artifacts"][0]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="diagnostic_builder differs"):
        module.read_freeze(freeze_path, "test", "f" * 64)
