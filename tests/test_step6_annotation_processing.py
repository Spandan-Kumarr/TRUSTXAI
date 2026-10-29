import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/step-06/scripts/process_annotations.py"
SPEC = importlib.util.spec_from_file_location("step6_annotation_processing", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def view(status: str = "supported") -> dict:
    return {
        "C1_status": status,
        "C2_status": "supported",
        "C3_status": "supported",
        "C4_status": "supported",
        "extra_claim_present": "no",
        "extra_claims": [],
        "scope_flags": [],
    }


def response(packet: dict, rater_id: str, *, first_status: str = "supported") -> dict:
    return {
        "schema_version": "1.0",
        "packet_id": packet["packet_id"],
        "item_id": packet["item_id"],
        "rater_id": rater_id,
        "reviewable": "yes",
        "view_1": view(first_status),
        "view_2": view(),
        "cross_view": {claim: "preserved" for claim in MODULE.CLAIMS},
        "needs_adjudication": "no",
        "notes": "",
    }


def declaration(rater_id: str, signature: str) -> str:
    return f"""# Annotator declaration

- Rater pseudonym: {rater_id}
- Date: 2026-10-29
- Relevant training/background: Independent test reviewer
- Relationship to the project: External reviewer
- Independent of the other rater: yes
- Read protocol and frozen rubric: yes
- Completed qualification exercise: yes
- Accessed condition labels, checker scores, intended mutations, benchmark gold labels or the other response file before lock: no
- Possible style-based unblinding observed: none
- Conflicts or other disclosures: none

I judged support against the displayed evidence contract.

Signature or authenticated acknowledgement: {signature}
"""


def make_fixture(tmp_path: Path, *, disagreement: bool = False) -> dict:
    annotation = ROOT / "research/step-06/annotation"
    response_schema = annotation / "RESPONSE_SCHEMA.json"
    rubric = annotation / "RUBRIC.json"
    lock_schema = annotation / "ANNOTATION_LOCK_SCHEMA.json"
    private = tmp_path / "private"
    seed = 20261029
    source = "synthetic-source-1"
    blind = MODULE._blind_source(source, seed)
    item_ids = ("I-1111111111111111", "I-2222222222222222")

    packet_paths = {}
    packet_rows = {}
    for rater in ("A", "B"):
        rows = []
        for item_id in item_ids:
            rows.append({
                "schema_version": "1.0",
                "partition": "development",
                "item_id": item_id,
                "source_blind_id": blind,
                "evidence": {"C1": "a", "C2": "b", "C3": "c", "C4": "d"},
                "view_1": "Explanation for view one.",
                "view_2": "Explanation for view two.",
                "packet_id": f"development-rater-{rater}-v1",
            })
        path = private / f"rater_{rater}.jsonl"
        write_jsonl(path, rows)
        packet_paths[rater] = path
        packet_rows[rater] = rows

    mapping = {
        "schema_version": "1.0",
        "partition": "development",
        "seed": seed,
        "status": "sealed_private_mapping_not_rater_material",
        "items": {
            item_ids[0]: {
                "item_type": "natural_output",
                "source_id": source,
                "audience_map": {"view_1": "novice", "view_2": "expert"},
                "logical_roles": [{
                    "logical_id": "L-1", "condition": "B1", "stage": "initial",
                    "output_status": "generated",
                }],
                "content_sha256": item_ids[0][2:] + "0" * 48,
            },
            item_ids[1]: {
                "item_type": "controlled_variant",
                "source_id": source,
                "audience_map": {"view_1": "novice", "view_2": "expert"},
                "variant_id": "V-1",
                "construction_intent": "faulty",
                "mutation_type": "synthetic_test",
                "content_sha256": item_ids[1][2:] + "0" * 48,
            },
        },
        "nonreviewable": [],
    }
    mapping_path = private / "sealed_mapping.json"
    write_json(mapping_path, mapping)

    manifest = {
        "schema_version": "1.0",
        "partition": "development",
        "status": "packets_built_not_annotated",
        "contains_rater_responses": False,
        "blinded_unique_item_count": 2,
        "controlled_variants_instantiated": 1,
        "nonreviewable_slot_count": 0,
        "deduplicated_natural_logical_rows": 0,
        "frozen_public_artifacts": {
            "response_schema_sha256": sha256(response_schema),
            "rubric_sha256": sha256(rubric),
            "annotation_lock_schema_sha256": sha256(lock_schema),
        },
        "private_outputs": {
            "rater_A_jsonl_sha256": sha256(packet_paths["A"]),
            "rater_B_jsonl_sha256": sha256(packet_paths["B"]),
            "sealed_mapping_json_sha256": sha256(mapping_path),
        },
    }
    manifest_path = tmp_path / "PACKET_MANIFEST-development.json"
    write_json(manifest_path, manifest)

    response_paths = {}
    declaration_paths = {}
    for rater, rater_id in (("A", "R-alpha"), ("B", "R-beta")):
        rows = [response(row, rater_id) for row in packet_rows[rater]]
        if disagreement and rater == "B":
            rows[0] = response(packet_rows[rater][0], rater_id, first_status="contradicted")
        response_path = private / f"responses_{rater}.jsonl"
        write_jsonl(response_path, rows)
        response_paths[rater] = response_path
        declaration_path = private / f"declaration_{rater}.md"
        declaration_path.write_text(declaration(rater_id, f"Signature {rater}"), encoding="utf-8")
        declaration_paths[rater] = declaration_path

    return {
        "packet_a": packet_paths["A"], "packet_b": packet_paths["B"],
        "response_a": response_paths["A"], "response_b": response_paths["B"],
        "declaration_a": declaration_paths["A"], "declaration_b": declaration_paths["B"],
        "mapping": mapping_path, "manifest": manifest_path,
        "response_schema": response_schema, "rubric": rubric, "lock_schema": lock_schema,
    }


def prepare(paths: dict, output: Path):
    return MODULE.prepare_annotations(
        partition="development", packet_a_path=paths["packet_a"],
        packet_b_path=paths["packet_b"], response_a_path=paths["response_a"],
        response_b_path=paths["response_b"], declaration_a_path=paths["declaration_a"],
        declaration_b_path=paths["declaration_b"], output_dir=output,
        manifest_path=paths["manifest"], response_schema_path=paths["response_schema"],
        rubric_path=paths["rubric"], lock_schema_path=paths["lock_schema"],
    )


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_prepare_and_lock_emit_hash_bound_analyzer_labels(tmp_path):
    paths = make_fixture(tmp_path)
    prepared = tmp_path / "prepared"
    record = prepare(paths, prepared)
    assert record["adjudication_queue"]["item_count"] == 0

    locked = tmp_path / "locked"
    provenance = MODULE.lock_annotations(
        prepared_dir=prepared, output_dir=locked, custodian="test-custodian",
        sealed_mapping_path=paths["mapping"],
    )
    assert provenance["natural_logical_label_count"] == 1
    assert provenance["controlled_variant_label_count"] == 1
    natural = read_jsonl(locked / MODULE.NATURAL_LABELS_NAME)
    controlled = read_jsonl(locked / MODULE.CONTROLLED_LABELS_NAME)
    assert natural[0]["pair_supported"] is True
    assert controlled[0]["truth"] == "supported"
    assert natural[0]["annotation_status"] == "independent_consensus"
    assert "construction_intent" not in controlled[0]
    lock_hash = sha256(locked / MODULE.LOCK_NAME)
    assert natural[0]["annotation_lock_sha256"] == lock_hash
    assert controlled[0]["annotation_lock_sha256"] == lock_hash


def test_disagreement_requires_complete_separate_adjudication(tmp_path):
    paths = make_fixture(tmp_path, disagreement=True)
    prepared = tmp_path / "prepared"
    record = prepare(paths, prepared)
    assert record["adjudication_queue"]["item_count"] == 1
    with pytest.raises(MODULE.AnnotationProcessingError, match="require a completed adjudication"):
        MODULE.lock_annotations(
            prepared_dir=prepared, output_dir=tmp_path / "rejected",
            custodian="test-custodian", sealed_mapping_path=paths["mapping"],
        )

    queue = read_jsonl(prepared / MODULE.ADJUDICATION_QUEUE_NAME)
    queue[0]["adjudicated_values"] = {
        field: values["rater_A"] for field, values in queue[0]["disputed_fields"].items()
    }
    queue[0]["reason"] = "Resolved against the displayed evidence."
    queue[0]["adjudicator_id"] = "ADJ-test"
    queue[0]["adjudicated_at"] = "2026-10-29T10:00:00+05:30"
    adjudication = tmp_path / "completed_adjudication.jsonl"
    write_jsonl(adjudication, queue)
    locked = tmp_path / "accepted"
    MODULE.lock_annotations(
        prepared_dir=prepared, output_dir=locked, custodian="test-custodian",
        sealed_mapping_path=paths["mapping"], adjudication_path=adjudication,
    )
    natural = read_jsonl(locked / MODULE.NATURAL_LABELS_NAME)
    assert natural[0]["annotation_status"] == "independent_adjudicated"


def test_prepare_rejects_same_rater_identity(tmp_path):
    paths = make_fixture(tmp_path)
    rows = read_jsonl(paths["response_b"])
    for row in rows:
        row["rater_id"] = "R-alpha"
    write_jsonl(paths["response_b"], rows)
    paths["declaration_b"].write_text(
        declaration("R-alpha", "Different signature"), encoding="utf-8")
    with pytest.raises(MODULE.AnnotationProcessingError, match="distinct real rater IDs"):
        prepare(paths, tmp_path / "prepared")


def test_prepare_rejects_incomplete_and_lock_rejects_changed_inputs(tmp_path):
    paths = make_fixture(tmp_path)
    rows = read_jsonl(paths["response_a"])
    write_jsonl(paths["response_a"], rows[:1])
    with pytest.raises(MODULE.AnnotationProcessingError, match="incomplete response coverage"):
        prepare(paths, tmp_path / "incomplete")

    paths = make_fixture(tmp_path / "second")
    prepared = tmp_path / "prepared"
    prepare(paths, prepared)
    paths["response_a"].write_text(
        paths["response_a"].read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(MODULE.AnnotationProcessingError, match="changed after agreement"):
        MODULE.lock_annotations(
            prepared_dir=prepared, output_dir=tmp_path / "locked",
            custodian="test-custodian", sealed_mapping_path=paths["mapping"],
        )
