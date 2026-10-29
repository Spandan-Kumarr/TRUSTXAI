import importlib.util
import json
from pathlib import Path

import pytest

from trustxai.research_analysis import (
    AnalysisContractError,
    IndependentLabelsIncomplete,
    analyze_h1,
    analyze_h2,
    analyze_h3,
    cost_summary,
    diagnostic_metrics,
    exact_mcnemar,
    holm_adjust,
    omission_summary,
    paired_sign_flip_p,
    stratified_paired_bootstrap,
)


def source_rows():
    return [
        {"source_id":"sA", "correct_option":"A", "predicted_option":"A"},
        {"source_id":"sB", "correct_option":"B", "predicted_option":"invalid"},
        {"source_id":"sC", "correct_option":"C", "predicted_option":"D"},
        {"source_id":"sD", "correct_option":"D", "predicted_option":"D"},
    ]


def narrative(source, condition, supported, *, status="generated", stage=None, annotation="independent_consensus"):
    return {"source_id":source, "condition":condition, "stage":stage,
            "output_kind":"llm_narrative" if status == "generated" else "template",
            "release_status":status, "parseable":True, "blocked":False,
            "pair_supported":supported, "annotation_status":annotation}


def test_exact_mcnemar_and_holm_are_deterministic_and_exact():
    result = exact_mcnemar([True, True, True], [False, False, False])
    assert result["a_only"] == 3 and result["discordant"] == 3
    assert result["two_sided_exact_p"] == .25
    assert exact_mcnemar([True], [True])["two_sided_exact_p"] == 1
    assert holm_adjust({"a":.01, "b":.04, "c":.03}) == {"a":.03, "b":.06, "c":.06}
    assert paired_sign_flip_p([0, 0])["two_sided_p"] == 1


def test_stratified_paired_bootstrap_keeps_pairing_and_strata():
    rows = [{"correct_option":letter, "a":1, "b":0} for letter in "ABCD" for _ in range(2)]
    first = stratified_paired_bootstrap(rows, "a", "b", replicates=50, seed=7)
    second = stratified_paired_bootstrap(rows, "a", "b", replicates=50, seed=7)
    assert first == second
    assert first["estimate"] == 1 and first["ci95"] == [1, 1]
    assert first["strata"] == {letter:2 for letter in "ABCD"}


def test_h1_uses_all_source_denominator_and_fallbacks_fail():
    rows = [
        narrative("sA", "P", True), narrative("sA", "B1", None, status="evidence_template"),
        narrative("sB", "P", False), narrative("sB", "B1", True),
        narrative("sD", "P", None, status="evidence_template"),
    ]
    result = analyze_h1(rows, source_rows(), expected_n=4, replicates=40)
    assert result["denominator"] == 4
    assert result["P_successes"] == result["B1_successes"] == 1
    assert result["mcnemar"]["a_only"] == result["mcnemar"]["b_only"] == 1
    outcomes = {row["source_id"]:row for row in result["source_outcomes"]}
    assert outcomes["sC"] == {"source_id":"sC", "correct_option":"C", "P":False, "B1":False}
    assert not outcomes["sD"]["P"]


def test_generated_h1_output_requires_real_independent_label():
    rows = [narrative("sA", "P", True, annotation="automated_proxy")]
    with pytest.raises(IndependentLabelsIncomplete):
        analyze_h1(rows, source_rows(), expected_n=4, replicates=5)
    proxy = analyze_h1(rows, source_rows(), require_independent=False, expected_n=4, replicates=5)
    assert proxy["analysis_status"] == "non_independent_proxy"


def diagnostic_variant_rows():
    rows = []
    for source in source_rows():
        sid = source["source_id"]
        for method in ("typed_nli", "nli_only"):
            rows.extend([
                {"source_id":sid, "variant_id":"supported", "method":method, "truth":"supported",
                 "decision":"accept", "annotation_status":"independent_consensus"},
                {"source_id":sid, "variant_id":"faulty", "method":method, "truth":"faulty",
                 "decision":"reject" if method == "typed_nli" else "accept",
                 "annotation_status":"independent_consensus"},
            ])
    return rows


def test_h2_keeps_variant_clusters_and_reports_requested_rates():
    result = analyze_h2(diagnostic_variant_rows(), source_rows(), expected_n=4, replicates=40)
    assert result["methods"]["typed_plus_nli"]["false_acceptance_requested"] == 0
    assert result["methods"]["nli_only"]["false_acceptance_requested"] == 1
    difference = result["paired_source_bootstrap"]["differences"]["false_acceptance_requested"]
    assert difference["typed_nli_minus_nli_only"] == -1
    assert difference["ci95"] == [-1, -1]
    assert result["paired_source_tests"]["false_acceptance_requested"]["two_sided_p"] == .125


def test_h2_requires_same_slots_and_independent_truth():
    rows = diagnostic_variant_rows()
    rows.pop()
    with pytest.raises(AnalysisContractError, match="same source/variant slots"):
        analyze_h2(rows, source_rows(), expected_n=4, replicates=5)
    rows = diagnostic_variant_rows()
    rows[0]["annotation_status"] = "automated_proxy"
    with pytest.raises(IndependentLabelsIncomplete):
        analyze_h2(rows, source_rows(), expected_n=4, replicates=5)
    rows = diagnostic_variant_rows()
    rows[0].update(nli_status="unresolved", decision="accept")
    with pytest.raises(AnalysisContractError, match="Unresolved NLI"):
        analyze_h2(rows, source_rows(), expected_n=4, replicates=5)


def test_diagnostic_metrics_count_invalid_predictions_as_incorrect():
    result = diagnostic_metrics(source_rows(), expected_n=4)
    assert result["accuracy"] == .5
    assert result["valid_decision_fraction"] == .75
    assert result["balanced_accuracy"] == .5
    assert result["confusion_matrix"]["columns_predicted"] == ["A", "B", "C", "D", "invalid"]
    assert result["confusion_matrix"]["values"][1][-1] == 1


def test_omission_summary_retains_unresolved_sources_in_denominator():
    rows = [
        {"source_id":"sA", "original_label":"A", "available_spans":2,
         "omissions":[{"label":"B"},{"label":"A"}], "selected":{"label":"B"}, "recheck":{"label":"B"}},
        {"source_id":"sB", "original_label":"invalid", "available_spans":2,
         "omissions":[{"label":"invalid"}], "selected":None, "recheck":None},
    ]
    result = omission_summary(rows, expected_n=2)
    assert result["sources"] == 2 and result["available_spans"] == 4
    assert result["omission_attempts"] == 3 and result["answer_changes"] == 1
    assert result["informative_evidence_sources"] == 1
    assert result["recheck_agreement_all_sources"] == .5


def test_h3_pairs_before_after_and_template_final_fails():
    rows = [
        narrative("sA", "P", False, stage="initial"), narrative("sA", "P", True, stage="final"),
        narrative("sB", "P", True, stage="initial"), narrative("sB", "P", True, stage="final"),
        narrative("sC", "P", True, stage="initial"), narrative("sC", "P", None, status="evidence_template", stage="final"),
    ]
    result = analyze_h3(rows, source_rows(), expected_n=4, replicates=40)
    assert result["initial_successes"] == result["final_successes"] == 2
    assert result["mcnemar"]["a_only"] == result["mcnemar"]["b_only"] == 1


def test_cost_summary_separates_physical_and_standalone_accounting():
    rows = [
        {"physical_call_id":"shared", "component":"initial", "charged_conditions":["P","B1"],
         "wall_seconds":2, "CPU_seconds":3, "prompt_tokens":10, "new_tokens":5,
         "peak_process_RSS_GiB":2.2, "cache_hit":False},
        {"physical_call_id":"repair", "component":"repair", "charged_conditions":["P"],
         "wall_seconds":1, "CPU_seconds":2, "prompt_tokens":8, "new_tokens":4,
         "peak_process_RSS_GiB":2.5, "cache_hit":False},
    ]
    result = cost_summary(rows)
    assert result["actual_physical_matrix"]["calls"] == 2
    assert result["logical_standalone_by_condition"]["P"]["calls"] == 2
    assert result["logical_standalone_by_condition"]["B1"]["calls"] == 1
    assert result["peak_process_RSS_GiB"] == 2.5


def test_cli_loader_accepts_per_source_directories_and_public_filter_removes_text(tmp_path):
    script = Path(__file__).parents[1] / "research/step-06/scripts/analyze_results.py"
    spec = importlib.util.spec_from_file_location("step6_analysis_cli", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "sA.json").write_text(json.dumps({"source_record":{"source_id":"sA","correct_option":"A"}}))
    rows, paths = module.load_records(tmp_path, "sources")
    assert rows == [{"source_id":"sA", "correct_option":"A"}] and len(paths) == 1
    assert module._public({"source_id":"sA", "case_text":"private", "nested":{"text":"private"}}) == {
        "source_id":"sA", "nested":{}}


def test_formal_gate_does_not_accept_a_bare_independent_marker():
    rows = diagnostic_variant_rows()
    for row in rows:
        row["annotation_status"] = "independent"
    with pytest.raises(IndependentLabelsIncomplete):
        analyze_h2(rows, source_rows(), expected_n=4, replicates=5)
    for row in rows:
        row["independent_rater_count"] = 2
    assert analyze_h2(rows, source_rows(), expected_n=4, replicates=5)["analysis_status"] == "independent"


def test_cli_derives_contracts_from_runner_envelopes_and_postfreeze_gold(tmp_path):
    script = Path(__file__).parents[1] / "research/step-06/scripts/analyze_results.py"
    spec = importlib.util.spec_from_file_location("step6_analysis_runtime", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pair = {audience:{f"C{i}":f"claim {i}" for i in range(1,5)}
            for audience in ("novice", "expert")}
    evidence = tmp_path / "evidence"; matrix = tmp_path / "matrix"; diagnostics = tmp_path / "diagnostics"
    evidence.mkdir(); matrix.mkdir(); diagnostics.mkdir()
    evidence_payload = {
        "source_id":"sA", "input_sha256":"a" * 64,
        "evidence": {"source_id":"sA", "input_sha256":"a" * 64,
            "decision":{"label":"B"}, "spans":[{"id":"S1"},{"id":"S2"}],
            "omissions":[{"span_id":"S1","label":"C"},{"span_id":"S2","label":"B"}],
            "selected":{"span_id":"S1","label":"C"}, "recheck":{"label":"C"}},
    }
    (evidence / "sA.json").write_text(json.dumps({"schema":"runner", "payload":evidence_payload}))
    conditions = {condition:{"status":"baseline_unchecked", "views":pair,
                             "llm_narrative_applicable":condition != "B4"}
                  for condition in module.CONDITIONS}
    conditions["B4"].update(status="evidence_template")
    conditions["P"].update(status="generated", initial_generation_id="g-common")
    matrix_payload = {"source_id":"sA", "conditions":conditions,
                      "generations":[{"generation_id":"g-common",
                          "stage":"shared_initial_B1_B2_B3_P", "kind":"narrative",
                          "output":{"text":json.dumps(pair), "seconds":1, "CPU_seconds":2,
                                    "prompt_tokens":3, "new_tokens":4}}]}
    (matrix / "sA.json").write_text(json.dumps({"schema":"runner", "payload":matrix_payload}))
    variant = {"source_id":"sA", "variant_id":"sA-V01", "construction_intent":"supported",
               "instantiation_status":"instantiated", "nli_complete":True,
               "nli":[{"request_sha256":"x", "status":"scored", "entailment":.99}],
               "decisions":{"0.9":{"typed_plus_nli":"accept", "nli_only":"accept"}}}
    (diagnostics / "sA.json").write_text(json.dumps({"variants":[variant]}))

    sources, _ = module.load_records(tmp_path, "sources")
    omissions, _ = module.load_records(tmp_path, "omissions")
    natural, _ = module.load_records(tmp_path, "natural")
    costs, _ = module.load_records(tmp_path, "costs")
    variants, _ = module.load_records(tmp_path, "diagnostics")
    gold = tmp_path / "gold.json"; gold.write_text(json.dumps({"sA":"A"}))
    assert module.attach_gold(sources, gold, expected_n=1)[0] == {
        "source_id":"sA", "predicted_option":"B", "input_sha256":"a" * 64,
        "correct_option":"A"}
    assert omissions[0]["available_spans"] == 2 and omissions[0]["recheck"]["label"] == "C"
    assert len(natural) == 7 and next(row for row in natural if row["condition"] == "B1")["release_status"] == "generated"
    assert costs[0]["charged_conditions"] == ["B1", "B2", "B3", "P"]
    expanded = module.diagnostic_analysis_rows(variants, threshold=.9,
                                               annotation_mode="automated_proxy")
    assert [row["method"] for row in expanded] == ["typed_plus_nli", "nli_only"]
    assert all(row["annotation_status"] == "automated_proxy_construction_intent" for row in expanded)

    proxy_dir = tmp_path / "natural-diagnostics"; proxy_dir.mkdir()
    proxy_records = [{"condition":condition, "stage":"final",
                      "automated_proxy_llm_pair_endpoint":"pass",
                      "analysis_status":"automated_proxy_pending_independent_annotation"}
                     for condition in module.CONDITIONS]
    proxy_records.append({"condition":"P", "stage":"initial",
                          "automated_proxy_llm_pair_endpoint":"fail",
                          "analysis_status":"automated_proxy_pending_independent_annotation"})
    (proxy_dir / "sA.json").write_text(json.dumps({
        "schema":"trustxai-step6-natural-diagnostics-1", "split":"development",
        "source_id":"sA", "records":proxy_records,
    }))
    loaded_proxy = module._read_rows_path(proxy_dir)
    assert len(loaded_proxy) == 7
    assert {row["source_id"] for row in loaded_proxy} == {"sA"}
    module.validate_natural_proxy_bindings(
        loaded_proxy, [{"source_id":"sA"}], expected_n=1, expected_split="development",
        expected_p_initial_source_ids={"sA"})
    with pytest.raises(AnalysisContractError, match="split mismatch"):
        module.validate_natural_proxy_bindings(
            loaded_proxy, [{"source_id":"sA"}], expected_n=1, expected_split="test",
            expected_p_initial_source_ids={"sA"})
    without_initial = [row for row in loaded_proxy if row["stage"] == "final"]
    module.validate_natural_proxy_bindings(
        without_initial, [{"source_id":"sA"}], expected_n=1,
        expected_split="development", expected_p_initial_source_ids=set())
    with pytest.raises(AnalysisContractError, match="plus P initial"):
        module.validate_natural_proxy_bindings(
            without_initial, [{"source_id":"sA"}], expected_n=1,
            expected_split="development", expected_p_initial_source_ids={"sA"})


def test_natural_proxy_directory_rejects_filename_and_source_set_mismatch(tmp_path):
    script = Path(__file__).parents[1] / "research/step-06/scripts/analyze_results.py"
    spec = importlib.util.spec_from_file_location("step6_analysis_proxy_binding", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    directory = tmp_path / "natural-diagnostics"; directory.mkdir()
    records = [{"condition":condition, "stage":"final"} for condition in module.CONDITIONS]
    records.append({"condition":"P", "stage":"initial"})
    (directory / "wrong-name.json").write_text(json.dumps({
        "split":"test", "source_id":"sA", "records":records,
    }))
    with pytest.raises(AnalysisContractError, match="filename/source"):
        module._read_rows_path(directory)
    (directory / "wrong-name.json").rename(directory / "sA.json")
    loaded = module._read_rows_path(directory)
    with pytest.raises(AnalysisContractError, match="source set mismatch"):
        module.validate_natural_proxy_bindings(
            loaded, [{"source_id":"sB"}], expected_n=1, expected_split="test",
            expected_p_initial_source_ids={"sB"})
