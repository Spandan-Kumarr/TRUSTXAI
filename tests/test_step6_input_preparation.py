import csv
import hashlib
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "research/step-06/scripts/prepare_inputs.py"
SPEC = importlib.util.spec_from_file_location("step6_prepare_inputs", SCRIPT)
prepare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


@pytest.fixture
def snapshot(tmp_path):
    clinical = tmp_path / "clinical"
    output = tmp_path / "private"
    clinical.mkdir()
    question = ("A 40-year-old woman has fever. Examination shows a new rash. "
                "Which of the following is the most likely diagnosis?")
    query, qstart, _ = prepare.query_parts(question)
    contexts = [question[:33], question[33:qstart]]
    options = {"A": "Diagnosis A", "B": "Diagnosis B", "C": "Diagnosis C", "D": "Diagnosis D"}
    raw = {"question": question, "answer": "Diagnosis B", "answer_idx": "B",
           "options": options, "meta_info": "hidden metadata", "metamap_phrases": ["hidden"]}
    train = json.dumps(raw) + "\n"
    test = json.dumps({**raw, "answer": "Diagnosis C", "answer_idx": "C"}) + "\n"
    (clinical / "phrases_no_exclude_train.jsonl").write_text(train)
    (clinical / "phrases_no_exclude_test.jsonl").write_text(test)
    records = []
    for name, text in (("phrases_no_exclude_train.jsonl", train),
                       ("phrases_no_exclude_test.jsonl", test)):
        records.append({"file": name, "sha256": hashlib.sha256(text.encode()).hexdigest()})
    dump(clinical / "DOWNLOAD_RECORDS.json", records)
    ids = {"development": ["medqa-train-00000"], "test": ["medqa-test-00000"]}
    dump(clinical / "partition_ids.json", ids)
    offsets = [{"start": 0, "end": 33, "text": contexts[0]},
               {"start": 33, "end": qstart, "text": contexts[1]}]
    dump(clinical / "source_offsets.json", {ids["development"][0]: offsets,
                                              ids["test"][0]: offsets})
    config = tmp_path / "experiment.json"
    dump(config, {"dataset": {"mirror_revision": prepare.MIRROR_REVISION}})
    manifest = tmp_path / "manifest.csv"
    fields = ["source_id", "partition", "source_partition", "correct_option", "group_id",
              "input_sha256", "original_question_sha256", "options_sha256", "span_count",
              "prompt_tokens"]
    with manifest.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for split, source_id, label in (("development", ids["development"][0], "B"),
                                        ("test", ids["test"][0], "C")):
            inp = {"question": query, "contexts": contexts, "options": options}
            writer.writerow({"source_id": source_id, "partition": split,
                             "source_partition": source_id.split("-")[1],
                             "correct_option": label, "group_id": source_id,
                             "input_sha256": prepare.json_digest(inp),
                             "original_question_sha256": hashlib.sha256(question.encode()).hexdigest(),
                             "options_sha256": prepare.json_digest(options), "span_count": 2,
                             "prompt_tokens": 20})
    return clinical, manifest, config, output


def materialize(snapshot, split="development"):
    clinical, manifest, config, output = snapshot
    return prepare.materialize_inputs(split, clinical, manifest, config, output,
                                      expected_manifest_sha=None, expected_count=1)


def test_materialized_inputs_are_exact_and_label_blind(snapshot):
    report = materialize(snapshot)
    output = Path(report["path"])
    rows = json.loads(output.read_text())
    assert report["contains_gold_fields"] is False and report["sources"] == 1
    assert set(rows[0]) == {"source_id", "question", "contexts", "options",
                            "input_sha256", "original_question_sha256"}
    serialized = output.read_text()
    assert all(field not in serialized for field in
               ('"answer"', '"answer_idx"', '"meta_info"', '"metamap_phrases"', '"correct_option"'))
    assert rows[0]["input_sha256"] == prepare.json_digest({
        key: rows[0][key] for key in ("question", "contexts", "options")})
    assert not (output.parent / "development_gold.json").exists()


def test_corrupt_source_offset_is_rejected(snapshot):
    clinical, _, _, _ = snapshot
    offsets = json.loads((clinical / "source_offsets.json").read_text())
    offsets["medqa-train-00000"][0]["text"] = "altered finding"
    dump(clinical / "source_offsets.json", offsets)
    with pytest.raises(ValueError, match="Span text/offset mismatch"):
        materialize(snapshot)


def test_manifest_hash_and_raw_snapshot_hash_are_enforced(snapshot):
    clinical, manifest, config, output = snapshot
    with pytest.raises(ValueError, match="Split manifest digest mismatch"):
        prepare.materialize_inputs("development", clinical, manifest, config, output,
                                   expected_manifest_sha="0" * 64, expected_count=1)
    (clinical / "phrases_no_exclude_test.jsonl").write_text("{}\n")
    with pytest.raises(ValueError, match="Pinned raw-file digest mismatch"):
        materialize(snapshot)


def test_gold_requires_explicit_complete_prediction_freeze(snapshot):
    clinical, manifest, _, output = snapshot
    materialize(snapshot)
    freeze_path = output / "prediction_freeze.json"
    bad = {"split": "development", "status": "running",
           "source_ids": ["medqa-train-00000"], "predictions_sha256": "a" * 64}
    dump(freeze_path, bad)
    with pytest.raises(ValueError, match="prediction-freeze"):
        prepare.materialize_gold("development", clinical, manifest, freeze_path, output,
                                 expected_manifest_sha=None, expected_count=1)
    dump(freeze_path, {**bad, "status": "predictions_frozen"})
    report = prepare.materialize_gold("development", clinical, manifest, freeze_path, output,
                                      expected_manifest_sha=None, expected_count=1)
    assert json.loads(Path(report["path"]).read_text()) == {"medqa-train-00000": "B"}


def test_input_projection_does_not_depend_on_gold_values(snapshot):
    clinical, _, _, _ = snapshot
    before = json.loads(Path(materialize(snapshot)["path"]).read_text())
    raw = json.loads((clinical / "phrases_no_exclude_train.jsonl").read_text())
    raw.update(answer="Different hidden answer", answer_idx="D", meta_info="changed")
    text = json.dumps(raw) + "\n"
    (clinical / "phrases_no_exclude_train.jsonl").write_text(text)
    records = json.loads((clinical / "DOWNLOAD_RECORDS.json").read_text())
    next(row for row in records if row["file"].endswith("train.jsonl"))["sha256"] = hashlib.sha256(text.encode()).hexdigest()
    dump(clinical / "DOWNLOAD_RECORDS.json", records)
    after = json.loads(Path(materialize(snapshot)["path"]).read_text())
    assert before == after
