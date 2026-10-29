#!/usr/bin/env python3
"""Materialize label-blind Step 6 inputs from the pinned MedQA snapshot.

Gold extraction is deliberately a separate command that requires a completed
prediction-freeze record.  The research runner consumes only *_inputs.json.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
from pathlib import Path


MANIFEST_SHA256 = "730d9ecfa80b04f5bc466f74d9750a5be08c35c029dc32c63ee21d11f4e70bff"
MIRROR_REVISION = "0fb93dd23a7339b6dcd27e241cb9b5eca62d4d18"
SPLIT_COUNTS = {"development": 40, "test": 60}
LETTERS = ("A", "B", "C", "D")
SOURCE_RE = re.compile(r"^medqa-(train|test)-(\d{5})$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


def json_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def query_parts(question: str) -> tuple[str, int, int]:
    full = question.strip()
    starts = list(re.finditer(r"\b(?:Which of the following|What is|What would be|Which diagnosis)\b",
                              full, re.I))
    start = starts[-1].start() if starts else full.rfind(re.split(r"(?<=[.!?])\s+", full)[-1])
    stop = full.find("?", start)
    stop = stop + 1 if stop >= 0 else len(full)
    return full[start:stop], start, stop


def load_json(path: Path) -> object:
    return json.loads(path.read_text())


def validate_snapshot(clinical_root: Path, experiment_config: Path,
                      expected_revision: str = MIRROR_REVISION) -> dict[str, dict]:
    config = load_json(experiment_config)
    revision = config["dataset"]["mirror_revision"]
    if revision != expected_revision:
        raise ValueError(f"Unexpected dataset revision: {revision}")
    records = load_json(clinical_root / "DOWNLOAD_RECORDS.json")
    by_name = {record["file"]: record for record in records}
    for partition in ("train", "test"):
        name = f"phrases_no_exclude_{partition}.jsonl"
        path = clinical_root / name
        record = by_name.get(name)
        if not record or file_digest(path) != record.get("sha256"):
            raise ValueError(f"Pinned raw-file digest mismatch: {name}")
    return by_name


def load_raw_rows(clinical_root: Path, selected_ids: list[str]) -> dict[str, dict]:
    wanted: dict[str, set[int]] = {"train": set(), "test": set()}
    for source_id in selected_ids:
        match = SOURCE_RE.fullmatch(source_id)
        if not match:
            raise ValueError(f"Malformed source ID: {source_id}")
        wanted[match.group(1)].add(int(match.group(2)))
    rows: dict[str, dict] = {}
    for partition, indices in wanted.items():
        if not indices:
            continue
        with (clinical_root / f"phrases_no_exclude_{partition}.jsonl").open() as handle:
            for index, line in enumerate(handle):
                if index in indices:
                    rows[f"medqa-{partition}-{index:05d}"] = json.loads(line)
        missing = {f"medqa-{partition}-{index:05d}" for index in indices} - rows.keys()
        if missing:
            raise ValueError(f"Missing raw sources: {sorted(missing)}")
    return rows


def manifest_rows(manifest_path: Path, expected_sha: str | None) -> list[dict[str, str]]:
    if expected_sha and file_digest(manifest_path) != expected_sha:
        raise ValueError("Split manifest digest mismatch")
    with manifest_path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or len({row["source_id"] for row in rows}) != len(rows):
        raise ValueError("Split manifest is empty or has duplicate source IDs")
    return rows


def project_source(source_id: str, raw: dict, spans: list[dict], manifest: dict[str, str]) -> dict:
    if hashlib.sha256(raw["question"].encode()).hexdigest() != manifest["original_question_sha256"]:
        raise ValueError(f"Original question digest mismatch: {source_id}")
    if set(raw["options"]) != set(LETTERS):
        raise ValueError(f"Invalid options: {source_id}")
    options = {letter: raw["options"][letter] for letter in LETTERS}
    if json_digest(options) != manifest["options_sha256"]:
        raise ValueError(f"Option digest mismatch: {source_id}")
    question, question_start, question_end = query_parts(raw["question"])
    if len(spans) != int(manifest["span_count"]) or not 2 <= len(spans) <= 8:
        raise ValueError(f"Span count mismatch: {source_id}")
    previous_end = -1
    for span in spans:
        if set(span) != {"start", "end", "text"}:
            raise ValueError(f"Unexpected span fields: {source_id}")
        start, end = span["start"], span["end"]
        if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end <= start:
            raise ValueError(f"Invalid span offsets: {source_id}")
        if start < previous_end or raw["question"][start:end] != span["text"]:
            raise ValueError(f"Span text/offset mismatch: {source_id}")
        if not (end <= question_start or start >= question_end):
            raise ValueError(f"A source span overlaps the diagnostic query: {source_id}")
        previous_end = end
    projected = {"question": question, "contexts": [span["text"] for span in spans],
                 "options": options}
    if json_digest(projected) != manifest["input_sha256"]:
        raise ValueError(f"Projected input digest mismatch: {source_id}")
    result = {"source_id": source_id, **projected,
              "input_sha256": manifest["input_sha256"],
              "original_question_sha256": manifest["original_question_sha256"]}
    forbidden = {"answer", "answer_idx", "meta_info", "metamap_phrases", "correct_option", "gold"}
    if forbidden & result.keys():
        raise AssertionError("A prohibited evaluation field entered the projected input")
    return result


def materialize_inputs(split: str, clinical_root: Path, manifest_path: Path,
                       experiment_config: Path, output_root: Path,
                       expected_manifest_sha: str | None = MANIFEST_SHA256,
                       expected_count: int | None = None,
                       validate_raw_digests: bool = True) -> dict:
    if split not in SPLIT_COUNTS:
        raise ValueError("Only development and test are Step 6 splits")
    if validate_raw_digests:
        validate_snapshot(clinical_root, experiment_config)
    rows = manifest_rows(manifest_path, expected_manifest_sha)
    selected_manifest = [row for row in rows if row["partition"] == split]
    ids = load_json(clinical_root / "partition_ids.json")[split]
    if ids != sorted(ids) or ids != [row["source_id"] for row in selected_manifest]:
        raise ValueError(f"Partition IDs and manifest order disagree: {split}")
    required_count = SPLIT_COUNTS[split] if expected_count is None else expected_count
    if len(ids) != required_count:
        raise ValueError(f"Expected {required_count} {split} sources, found {len(ids)}")
    spans_by_id = load_json(clinical_root / "source_offsets.json")
    raw_rows = load_raw_rows(clinical_root, ids)
    manifest_by_id = {row["source_id"]: row for row in selected_manifest}
    output = [project_source(source_id, raw_rows[source_id], spans_by_id[source_id],
                             manifest_by_id[source_id]) for source_id in ids]
    destination = output_root / f"{split}_inputs.json"
    write_json_atomic(destination, output)
    return {"split": split, "sources": len(output), "path": str(destination),
            "sha256": file_digest(destination),
            "manifest_sha256": file_digest(manifest_path),
            "dataset_revision": MIRROR_REVISION, "contains_gold_fields": False}


def materialize_gold(split: str, clinical_root: Path, manifest_path: Path,
                     prediction_freeze_path: Path, output_root: Path,
                     expected_manifest_sha: str | None = MANIFEST_SHA256,
                     expected_count: int | None = None) -> dict:
    if split not in SPLIT_COUNTS:
        raise ValueError("Only development and test are Step 6 splits")
    rows = manifest_rows(manifest_path, expected_manifest_sha)
    ids = [row["source_id"] for row in rows if row["partition"] == split]
    required_count = SPLIT_COUNTS[split] if expected_count is None else expected_count
    if len(ids) != required_count:
        raise ValueError(f"Expected {required_count} {split} sources, found {len(ids)}")
    freeze = load_json(prediction_freeze_path)
    if (freeze.get("split") != split or freeze.get("status") != "predictions_frozen"
            or freeze.get("source_ids") != ids
            or not HEX64_RE.fullmatch(str(freeze.get("predictions_sha256", "")))):
        raise ValueError("A complete, ordered prediction-freeze record is required before gold extraction")
    raw_rows = load_raw_rows(clinical_root, ids)
    gold = {source_id: raw_rows[source_id]["answer_idx"] for source_id in ids}
    if any(label not in LETTERS for label in gold.values()):
        raise ValueError("Invalid gold option label")
    destination = output_root / f"{split}_gold.json"
    write_json_atomic(destination, gold)
    return {"split": split, "sources": len(gold), "path": str(destination),
            "sha256": file_digest(destination),
            "released_after_predictions_sha256": freeze["predictions_sha256"]}


def parser() -> argparse.ArgumentParser:
    project = Path(__file__).resolve().parents[3]
    default_runtime = Path(os.environ.get("TRUSTXAI_RUNTIME", "/workspace/thesis-runtime"))
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--clinical-root", type=Path,
                        default=default_runtime / "clinical-cdss")
    common.add_argument("--manifest", type=Path,
                        default=project / "research/step-04/clinical-cdss/SPLIT_MANIFEST.csv")
    common.add_argument("--experiment-config", type=Path,
                        default=project / "research/step-04/clinical-cdss/EXPERIMENT_CONFIG.json")
    common.add_argument("--output-root", type=Path,
                        default=default_runtime / "clinical-cdss/step-06/private")
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    inputs = sub.add_parser("inputs", parents=[common])
    inputs.add_argument("--split", choices=("development", "test", "all"), default="all")
    gold = sub.add_parser("gold", parents=[common])
    gold.add_argument("--split", choices=tuple(SPLIT_COUNTS), required=True)
    gold.add_argument("--prediction-freeze", type=Path, required=True)
    return root


def main() -> None:
    args = parser().parse_args()
    if args.command == "inputs":
        splits = tuple(SPLIT_COUNTS) if args.split == "all" else (args.split,)
        results = [materialize_inputs(split, args.clinical_root, args.manifest,
                                      args.experiment_config, args.output_root) for split in splits]
    else:
        results = [materialize_gold(args.split, args.clinical_root, args.manifest,
                                    args.prediction_freeze, args.output_root)]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
