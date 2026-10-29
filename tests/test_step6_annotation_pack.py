import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/step-06/scripts/build_annotation_packets.py"
SPEC = importlib.util.spec_from_file_location("step6_annotation_builder", SCRIPT)
BUILDER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BUILDER)


def evidence():
    return {
        "case_findings": [{"id": "S1", "text": "Invented private finding."}],
        "C1": "The recorded suggestion was A (Example option); it was not verified.",
        "C2": "Omitting S1 returned B instead of A.",
        "C3": "1 of 1 spans was tested; one label was valid; the recheck agreed.",
        "C4": "This does not prove causation, all edits, or complete reasoning.",
    }


def fixture_rows():
    views = {"novice": "Plain private explanation.", "expert": "Technical private explanation."}
    natural = [
        {"partition": "development", "source_id": "source-private-1", "logical_id": "logical-B1",
         "condition": "B1", "stage": "final", "output_status": "baseline_unchecked",
         "evidence_display": evidence(), "views": views},
        {"partition": "development", "source_id": "source-private-1", "logical_id": "logical-P-initial",
         "condition": "P", "stage": "initial", "output_status": "generated",
         "evidence_display": evidence(), "views": views},
    ]
    variants = [
        {"partition": "development", "source_id": "source-private-1", "variant_id": "variant-private-1",
         "construction_intent": "faulty", "mutation_type": "option_name",
         "evidence_display": evidence(),
         "views": {"novice": "The option was D.", "expert": "Recorded class: D."}}
    ]
    return natural, variants


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def run_fixture(tmp_path, suffix="one"):
    natural, variants = fixture_rows()
    natural_path = tmp_path / f"natural-{suffix}.jsonl"
    variant_path = tmp_path / f"variants-{suffix}.jsonl"
    write_jsonl(natural_path, natural)
    write_jsonl(variant_path, variants)
    private = tmp_path / f"private-{suffix}"
    public = tmp_path / f"manifest-{suffix}.json"
    manifest = BUILDER.build(natural_path, variant_path, private, public,
                             "development", fixture_mode=True)
    return private, public, manifest


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def test_builder_blinds_metadata_deduplicates_natural_text_and_never_fills_responses(tmp_path):
    private, public, manifest = run_fixture(tmp_path)
    assert manifest["status"] == "fixture_packets_built_not_annotated"
    assert manifest["private_input_counts"] == {"natural_logical_rows": 2, "controlled_variant_rows": 1}
    assert manifest["blinded_unique_item_count"] == 2
    assert manifest["deduplicated_natural_logical_rows"] == 1
    assert manifest["contains_rater_responses"] is False
    assert json.loads(public.read_text()) == manifest
    public_text = public.read_text()
    for private_value in ("source-private-1", "Invented private finding",
                          "Plain private explanation", "Technical private explanation"):
        assert private_value not in public_text

    packet = private / "development/rater_A.jsonl"
    rows = read_jsonl(packet)
    assert packet.stat().st_mode & 0o777 == 0o600
    assert (private / "development/sealed_mapping.json").stat().st_mode & 0o777 == 0o600
    assert len(rows) == 2
    for row in rows:
        assert set(row) == {"schema_version", "partition", "packet_id", "item_id",
                            "source_blind_id", "evidence", "view_1", "view_2"}
        serialized = json.dumps(row)
        for secret in ("source-private-1", '"condition"', '"stage"', "construction_intent", "mutation_type"):
            assert secret not in serialized
    assert not list(private.rglob("*response*"))

    sealed = json.loads((private / "development/sealed_mapping.json").read_text())
    natural_item = next(value for value in sealed["items"].values()
                        if value["item_type"] == "natural_output")
    assert len(natural_item["logical_roles"]) == 2
    variant_item = next(value for value in sealed["items"].values()
                        if value["item_type"] == "controlled_variant")
    assert variant_item["construction_intent"] == "faulty"


def test_packet_generation_is_byte_deterministic(tmp_path):
    private_a, public_a, manifest_a = run_fixture(tmp_path, "a")
    private_b, public_b, manifest_b = run_fixture(tmp_path, "b")
    assert manifest_a == manifest_b
    assert public_a.read_bytes() == public_b.read_bytes()
    for name in ("rater_A.jsonl", "rater_B.jsonl", "sealed_mapping.json"):
        assert (private_a / "development" / name).read_bytes() == (private_b / "development" / name).read_bytes()


def test_builder_rejects_gold_or_checker_metadata_in_evidence(tmp_path):
    natural, variants = fixture_rows()
    natural[0]["evidence_display"]["correct_option"] = "A"
    natural_path, variant_path = tmp_path / "natural.jsonl", tmp_path / "variants.jsonl"
    write_jsonl(natural_path, natural)
    write_jsonl(variant_path, variants)
    with pytest.raises(ValueError, match="evidence_display keys"):
        BUILDER.build(natural_path, variant_path, tmp_path / "private", tmp_path / "manifest.json",
                      "development", fixture_mode=True)


def test_real_mode_enforces_protocol_counts_and_private_location(tmp_path):
    natural, variants = fixture_rows()
    natural_path, variant_path = tmp_path / "natural.jsonl", tmp_path / "variants.jsonl"
    write_jsonl(natural_path, natural)
    write_jsonl(variant_path, variants)
    with pytest.raises(ValueError, match="requires 40 sources"):
        BUILDER.build(natural_path, variant_path, tmp_path / "private", tmp_path / "manifest.json",
                      "development")
    with pytest.raises(ValueError, match="outside the Git repository"):
        BUILDER.build(natural_path, variant_path, ROOT / "research/private-packets",
                      tmp_path / "manifest.json", "development", fixture_mode=True)


def test_existing_responses_block_even_forced_packet_rebuild(tmp_path):
    private, _, _ = run_fixture(tmp_path)
    (private / "development/responses").mkdir()
    natural, variants = fixture_rows()
    natural_path, variant_path = tmp_path / "natural-next.jsonl", tmp_path / "variants-next.jsonl"
    write_jsonl(natural_path, natural)
    write_jsonl(variant_path, variants)
    with pytest.raises(FileExistsError, match="response-bearing"):
        BUILDER.build(natural_path, variant_path, private, tmp_path / "next-manifest.json",
                      "development", fixture_mode=True, force=True)


def test_public_instruments_are_blank_and_do_not_claim_humans_or_results():
    annotation = ROOT / "research/step-06/annotation"
    manifest = json.loads((annotation / "PACKET_MANIFEST.json").read_text())
    assert manifest["status"] == "pending_private_matrix_and_variant_exports"
    lock = json.loads((annotation / "templates/ANNOTATION_LOCK.json").read_text())
    lock_schema = json.loads((annotation / "ANNOTATION_LOCK_SCHEMA.json").read_text())
    Draft202012Validator(lock_schema).validate(lock)
    agreement = json.loads((annotation / "templates/AGREEMENT_REPORT.json").read_text())
    assert lock["status"] == "blank_template_not_a_completed_lock"
    assert lock["rater_count"] == 0
    assert lock["independent_annotation_ready"] is False
    assert agreement["rater_count"] == 0
    assert agreement["complete_pair_cohen_kappa"] is None
    assert "not executed" in (annotation / "PHASE_II_AUDIENCE_STUDY_STATUS.md").read_text().lower()
    training = json.loads((annotation / "TRAINING_EXAMPLES.json").read_text())
    assert training["status"] == "synthetic_training_only_not_experimental_data"
    for form in ("NATURAL_PAIR_FORM.csv", "CONTROLLED_VARIANT_FORM.csv", "ADJUDICATION_FORM.csv"):
        assert len((annotation / "forms" / form).read_text().splitlines()) == 1


def test_completed_lock_schema_requires_two_confirmed_real_response_sets():
    annotation = ROOT / "research/step-06/annotation"
    schema = json.loads((annotation / "ANNOTATION_LOCK_SCHEMA.json").read_text())
    lock = json.loads((annotation / "templates/ANNOTATION_LOCK.json").read_text())
    lock.update(status="locked", partition="test", locked_at="2026-10-28T10:00:00Z",
                custodian="R-custodian")
    errors = list(Draft202012Validator(schema).iter_errors(lock))
    assert errors
    messages = " ".join(error.message for error in errors)
    assert "2 was expected" in messages
    assert "True was expected" in messages


def test_missing_controlled_slot_is_counted_but_never_sent_to_raters(tmp_path):
    natural, variants = fixture_rows()
    variants[0].update(
        instantiation_status="not_instantiated",
        not_instantiated_reason="No selected omission was available",
        views=None,
    )
    natural_path, variant_path = tmp_path / "natural.jsonl", tmp_path / "variants.jsonl"
    write_jsonl(natural_path, natural)
    write_jsonl(variant_path, variants)
    private, public = tmp_path / "private", tmp_path / "manifest.json"
    manifest = BUILDER.build(natural_path, variant_path, private, public,
                             "development", fixture_mode=True)
    assert manifest["controlled_variants_not_instantiated"] == 1
    assert manifest["controlled_variants_instantiated"] == 0
    assert manifest["nonreviewable_slot_count"] == 1
    packet_text = (private / "development/rater_A.jsonl").read_text()
    assert "variant-private-1" not in packet_text
    sealed = json.loads((private / "development/sealed_mapping.json").read_text())
    missing = sealed["nonreviewable"][0]
    assert missing["disposition"] == "not_instantiated_not_sent_to_raters"
    assert missing["not_instantiated_reason"] == "No selected omission was available"


def _checkpoint(stage, partition, payload):
    return {
        "schema": "trustxai-step6-matrix-v1",
        "stage": stage,
        "partition": partition,
        "source_id": payload["source_id"],
        "input_sha256": payload["input_sha256"],
        "stage_signature": "f" * 64,
        "payload_sha256": BUILDER.sha256_value(payload),
        "payload": payload,
    }


def test_runtime_checkpoints_normalize_directly_without_manual_adapter(tmp_path):
    source_id, input_sha = "private-source-1", "a" * 64
    pair = {
        audience: {f"C{i}": f"{audience} claim {i}." for i in range(1, 5)}
        for audience in ("novice", "expert")
    }
    evidence_payload = {
        "source_id": source_id,
        "input_sha256": input_sha,
        "evidence": {"spans": [{"id": "S1", "text": "Private finding text.",
                                  "start": 0, "end": 21}]},
        "facts": {f"C{i}": f"Evidence fact {i}." for i in range(1, 5)},
    }
    conditions = {
        condition: {"status": "baseline_unchecked", "views": pair}
        for condition in BUILDER.CONDITIONS
    }
    conditions["B4"] = {"status": "evidence_template", "views": pair}
    conditions["B0"] = {"status": "invalid_frozen_decision", "views": None}
    shared_id = "shared-initial-generation"
    for condition in ("B1", "B2", "B3", "P"):
        conditions[condition]["initial_generation_id"] = shared_id
    matrix_payload = {"source_id": source_id, "input_sha256": input_sha,
                      "conditions": conditions,
                      "generations": [{"generation_id": shared_id,
                                       "output": {"text": json.dumps(pair)}}]}
    runtime = tmp_path / "runtime"
    for stage, payload in (("evidence", evidence_payload), ("matrix", matrix_payload)):
        path = runtime / "development" / stage / f"{source_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(_checkpoint(stage, "development", payload)))
    diagnostics = {
        "source_id": source_id,
        "evidence_input_sha256": input_sha,
        "variants": [
            {"variant_id": f"{source_id}-V01", "construction_intent": "supported",
             "mutation_type": "exact_canonical", "instantiation_status": "instantiated",
             "not_instantiated_reason": None, "pair": pair},
            {"variant_id": f"{source_id}-V06", "construction_intent": "faulty",
             "mutation_type": "span_binding", "instantiation_status": "not_instantiated",
             "not_instantiated_reason": "No alternate span", "pair": None},
        ],
    }
    diagnostic_path = runtime / "development/diagnostics" / f"{source_id}.json"
    diagnostic_path.parent.mkdir(parents=True)
    diagnostic_path.write_text(json.dumps(diagnostics))

    private = tmp_path / "annotation-private"
    natural_path, variants_path = BUILDER.normalize_runtime_artifacts(
        runtime, private, "development")
    natural, variants = BUILDER.read_jsonl(natural_path), BUILDER.read_jsonl(variants_path)
    assert len(natural) == 7
    assert len(variants) == 2
    assert next(row for row in natural if row["condition"] == "B0")["views"] is None
    p_initial = next(row for row in natural
                     if row["condition"] == "P" and row["stage"] == "initial")
    assert p_initial["output_status"] == "generated"
    assert "C4: novice claim 4." in p_initial["views"]["novice"]
    assert next(row for row in variants if row["instantiation_status"] == "not_instantiated")["views"] is None
    assert "C1: novice claim 1." in next(row for row in natural if row["views"])["views"]["novice"]

    manifest = BUILDER.build(natural_path, variants_path, private,
                             tmp_path / "public.json", "development", fixture_mode=True)
    assert manifest["nonreviewable_slot_count"] == 2
    packet = (private / "development/rater_A.jsonl").read_text()
    assert source_id not in packet
    assert "construction_intent" not in packet
    assert "mutation_type" not in packet


def test_absent_p_initial_is_sealed_as_mechanical_without_invented_judgment(tmp_path):
    natural, variants = fixture_rows()
    payload = {
        "source_id": "source-private-1",
        "conditions": {condition: {} for condition in BUILDER.CONDITIONS},
        "generations": [],
    }
    initial = BUILDER.p_initial_natural_row(
        payload, evidence(), "development", "fixture-matrix")
    assert initial["output_status"] == "missing"
    assert initial["views"] is None
    natural.append(initial)
    natural_path, variant_path = tmp_path / "natural.jsonl", tmp_path / "variants.jsonl"
    write_jsonl(natural_path, natural)
    write_jsonl(variant_path, variants)
    private = tmp_path / "private"
    manifest = BUILDER.build(natural_path, variant_path, private,
                             tmp_path / "manifest.json", "development", fixture_mode=True)
    assert manifest["nonreviewable_slot_count"] == 1
    sealed = json.loads((private / "development/sealed_mapping.json").read_text())
    mechanical = sealed["nonreviewable"][0]
    assert mechanical["item_type"] == "mechanical_natural_output"
    assert mechanical["logical_roles"][0]["logical_id"] == "source-private-1-P-initial"
    assert "source-private-1-P-initial" not in (private / "development/rater_A.jsonl").read_text()


def test_runtime_normalizer_rejects_tampered_checkpoint(tmp_path):
    runtime = tmp_path / "runtime"
    payload = {"source_id": "source-1", "input_sha256": "a" * 64,
               "evidence": {"spans": []}, "facts": {}}
    envelope = _checkpoint("evidence", "development", payload)
    envelope["payload_sha256"] = "0" * 64
    path = runtime / "development/evidence/source-1.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(envelope))
    with pytest.raises(ValueError, match="payload digest mismatch"):
        BUILDER.normalize_runtime_artifacts(runtime, tmp_path / "private", "development")


def test_real_development_contract_keeps_all_requested_missing_slots():
    natural, variants = [], []
    supported = ("exact_canonical", "audience_simplification",
                 "harmless_reordering", "allowed_numeric_wording")
    faults = ("option_name", "span_binding", "changed_result", "counts",
              "recheck_status", "all_interventions",
              "unsupported_clinical_clause", "missing_limitation")
    for source_index in range(40):
        source_id = f"source-{source_index:02d}"
        for condition in BUILDER.CONDITIONS:
            natural.append({
                "partition": "development", "source_id": source_id,
                "logical_id": f"{source_id}-{condition}", "condition": condition,
                "stage": "final", "output_status": "insufficient_evidence",
                "evidence_display": evidence(), "views": None,
            })
        for slot, kind in enumerate((*supported, *faults), start=1):
            variants.append({
                "partition": "development", "source_id": source_id,
                "variant_id": f"{source_id}-V{slot:02d}",
                "construction_intent": "supported" if slot <= 4 else "faulty",
                "mutation_type": kind, "instantiation_status": "not_instantiated",
                "not_instantiated_reason": "Minimum informative evidence unavailable",
                "evidence_display": evidence(), "views": None,
            })
    BUILDER.validate_inputs(natural, variants, "development", fixture_mode=False)
