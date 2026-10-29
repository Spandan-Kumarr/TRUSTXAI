#!/usr/bin/env python3
"""Run controlled and post-hoc natural-output Step 6 diagnostics.

Raw cases, variants, explanations, and NLI rows stay below the private runtime
root. Only aggregate, text-free summaries are written to the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "backend"))
PROHIBITED_KEYS = {"answer", "answer_idx", "gold", "gold_label", "correct_option"}


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     delete=False, prefix=path.name + ".") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def assert_label_blind(value, location="record") -> None:
    if isinstance(value, dict):
        forbidden = PROHIBITED_KEYS.intersection(value)
        if forbidden:
            raise ValueError(f"Gold-like fields {sorted(forbidden)} found in {location}")
        for key, child in value.items():
            assert_label_blind(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_label_blind(child, f"{location}[{index}]")


def unwrap_evidence(value: dict) -> dict:
    if "payload" in value and isinstance(value["payload"], dict):
        value = value["payload"]
    if "evidence" in value:
        return value["evidence"]
    if isinstance(value.get("result"), dict) and "evidence" in value["result"]:
        return value["result"]["evidence"]
    return value


def unwrap_matrix(value: dict) -> dict:
    return value["payload"] if isinstance(value.get("payload"), dict) else value


def read_freeze(path: Path | None, split: str,
                expected_sha256: str | None = None) -> dict | None:
    if split != "test":
        return None
    if path is None:
        raise ValueError("Held-out diagnostics require an immutable Step 6 freeze")
    if not expected_sha256:
        raise ValueError(
            "Held-out diagnostics require the caller-reviewed --freeze-sha256")
    from trustxai.research_freeze import sha256_file, verify_freeze
    record, file_sha256 = verify_freeze(path, expected_sha256=expected_sha256)
    frozen = {
        row.get("role"): row for row in record.get("frozen_artifacts", [])
        if isinstance(row, dict) and isinstance(row.get("role"), str)
    }
    current_artifacts = {
        "diagnostic_builder": REPO / "backend/trustxai/research_diagnostics.py",
        "diagnostics_cli": Path(__file__).resolve(),
    }
    for role, current_path in current_artifacts.items():
        row = frozen.get(role)
        expected_path = str(current_path.relative_to(REPO))
        if not isinstance(row, dict) or row.get("path") != expected_path:
            raise ValueError(f"Held-out freeze does not bind the current {role} path")
        if row.get("sha256") != sha256_file(current_path):
            raise ValueError(f"Current {role} differs from the immutable held-out freeze")
    threshold = record.get("checker", {}).get("selected_operating_threshold")
    if not isinstance(threshold, (int, float)) or isinstance(threshold, bool):
        raise ValueError("Held-out freeze lacks a numeric checker operating threshold")
    return {"record": record, "file_sha256": file_sha256,
            "threshold": float(threshold)}


def evidence_files(directory: Path) -> list[Path]:
    files = sorted(path for path in directory.glob("*.json") if path.is_file())
    if not files:
        raise ValueError(f"No evidence JSON files found in {directory}")
    return files


def _exact_pair(text):
    """Parse the stored generation exactly; do not repair or normalize it."""
    from trustxai.domain import valid_pair
    try:
        value = json.loads(text)
    except (TypeError, ValueError):
        return None
    return value if valid_pair(value) else None


def matrix_items(path: Path, source_id: str, input_sha256: str,
                 informative_evidence: bool) -> list[dict]:
    if not path.is_file():
        raise ValueError(f"Missing natural-output matrix checkpoint: {path}")
    matrix = unwrap_matrix(json.loads(path.read_text()))
    if (matrix.get("source_id") != source_id or
            matrix.get("input_sha256") != input_sha256):
        raise ValueError(f"Matrix checkpoint is not bound to {source_id}")
    conditions = matrix.get("conditions")
    expected = ("B0", "B1", "B2", "B3", "B4", "P")
    if not isinstance(conditions, dict) or set(conditions) != set(expected):
        raise ValueError(f"Matrix checkpoint does not contain exact B0-B4/P conditions: {path}")
    # Read each final released pair. This program never rewrites the matrix.
    items = [{
        "condition": condition,
        "stage": "final",
        "release_status": conditions[condition].get("status"),
        "generation_id": conditions[condition].get("final_generation_id"),
        "pair": conditions[condition].get("views"),
    } for condition in expected]
    p_initial_id = conditions["P"].get("initial_generation_id")
    if not informative_evidence:
        if p_initial_id is not None:
            raise ValueError(
                f"Non-informative source {source_id} unexpectedly has a P shared initial")
        return items
    if not isinstance(p_initial_id, str) or not p_initial_id:
        raise ValueError(f"Informative source {source_id} lacks the P shared-initial ID")
    generations = matrix.get("generations")
    if not isinstance(generations, list):
        raise ValueError(f"Informative source {source_id} lacks generation provenance")
    matches = [row for row in generations if isinstance(row, dict) and
               row.get("generation_id") == p_initial_id]
    if len(matches) != 1:
        raise ValueError(
            f"P shared-initial ID for {source_id} must resolve to exactly one generation")
    generation = matches[0]
    if (generation.get("stage") != "shared_initial_B1_B2_B3_P" or
            generation.get("kind") != "narrative" or
            not isinstance(generation.get("output"), dict) or
            not isinstance(generation["output"].get("text"), str)):
        raise ValueError(f"P shared-initial provenance is invalid for {source_id}")
    initial_pair = _exact_pair(generation["output"]["text"])
    items.append({
        "condition": "P",
        "stage": "initial",
        "release_status": "generated" if initial_pair is not None else "unparseable",
        "generation_id": p_initial_id,
        "pair": initial_pair,
    })
    if len(items) != 7:
        raise RuntimeError("Natural diagnostics require six finals plus one P initial")
    return items


def parse_args() -> argparse.Namespace:
    default_private = Path(os.environ.get(
        "TRUSTXAI_STEP6_PRIVATE",
        "/workspace/thesis-runtime/clinical-cdss/step-06/private",
    ))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("development", "test"), required=True)
    parser.add_argument("--mode", choices=("controlled", "natural"), default="controlled")
    parser.add_argument("--private-root", type=Path, default=default_private)
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--matrix-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--freeze", type=Path)
    parser.add_argument("--freeze-sha256",
                        help="Exact caller-reviewed SHA256 of the immutable test freeze")
    parser.add_argument("--threshold", type=float,
                        choices=(0.60, 0.70, 0.80, 0.90, 0.95),
                        help="Frozen threshold required for development natural-output scoring")
    parser.add_argument("--public-output", type=Path)
    parser.add_argument("--limit", type=int, default=None,
                        help="Development debugging only; forbidden for held-out test")
    parser.set_defaults(repo=REPO)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.split == "test" and args.limit is not None:
        raise ValueError("A held-out run cannot silently reduce its requested denominator")
    freeze = read_freeze(args.freeze, args.split, args.freeze_sha256)
    if args.split == "development" and (args.freeze is not None or
                                         args.freeze_sha256 is not None):
        raise ValueError("Freeze arguments are reserved for the held-out test")
    frozen_threshold = freeze["threshold"] if freeze else None
    if args.mode == "natural":
        threshold = frozen_threshold if frozen_threshold is not None else args.threshold
        if threshold is None:
            raise ValueError("Development natural-output scoring requires --threshold")
        if (args.threshold is not None and frozen_threshold is not None and
                float(args.threshold) != frozen_threshold):
            raise ValueError("Requested threshold differs from the immutable held-out freeze")
    else:
        threshold = None

    evidence_dir = args.evidence_dir or args.private_root / args.split / "evidence"
    matrix_dir = args.matrix_dir or args.private_root / args.split / "matrix"
    default_leaf = "diagnostics" if args.mode == "controlled" else "natural-diagnostics"
    output_dir = args.output_dir or args.private_root / args.split / default_leaf
    cache_dir = args.private_root / "checker-cache"
    os.environ.setdefault("TRUSTXAI_APP_DATA", str(cache_dir))
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

    from trustxai import store
    from trustxai.domain import canonical_facts, digest, evidence_available
    from trustxai.models import LocalModels
    from trustxai.research_diagnostics import (
        THRESHOLD_GRID, calibrate_thresholds, construct_variants,
        natural_proxy_summary, public_summary, score_natural_outputs,
        score_variants,
    )

    store.initialize()
    models = LocalModels()
    checker_revision = models.manifests["cross-encoder/nli-deberta-v3-base"]["revision"]
    config_signature = digest({
        "schema": "trustxai-step6-diagnostics-2",
        "mode": args.mode,
        "threshold_grid": THRESHOLD_GRID,
        "operating_threshold": threshold,
        "checker": checker_revision,
        "construction_labels": "pending_independent_review",
    })
    files = evidence_files(evidence_dir)
    if args.limit is not None:
        files = files[:args.limit]
    all_records = []
    source_bindings = []
    for index, path in enumerate(files, start=1):
        evidence = unwrap_evidence(json.loads(path.read_text()))
        assert_label_blind(evidence, path.name)
        source_id = evidence.get("source_id") or evidence["input_sha256"][:16]
        destination = output_dir / f"{source_id}.json"
        matrix_sha256 = None
        if args.mode == "natural":
            matrix_path = matrix_dir / f"{source_id}.json"
            matrix_sha256 = (hashlib.sha256(matrix_path.read_bytes()).hexdigest()
                             if matrix_path.is_file() else None)
        if destination.exists():
            result = json.loads(destination.read_text())
            if (result.get("config_signature") != config_signature or
                    result.get("evidence_input_sha256") != evidence["input_sha256"] or
                    result.get("matrix_file_sha256") != matrix_sha256):
                raise RuntimeError(f"Refusing incompatible checkpoint {destination}")
        elif args.mode == "controlled":
            records = score_variants(
                evidence, construct_variants(evidence), models.score_pairs,
                evidence.get("target_signature_sha256"),
            )
            result = {
                "schema": "trustxai-step6-controlled-diagnostics-2",
                "split": args.split,
                "source_id": source_id,
                "evidence_input_sha256": evidence["input_sha256"],
                "matrix_file_sha256": None,
                "config_signature": config_signature,
                "evidence": evidence,
                "facts": canonical_facts(evidence),
                "label_status": "construction_intent_only_pending_independent_review",
                "independent_semantic_validation": False,
                "variants": records,
            }
            atomic_json(destination, result)
        else:
            items = matrix_items(
                matrix_dir / f"{source_id}.json", source_id,
                evidence["input_sha256"], evidence_available(evidence),
            )
            records = score_natural_outputs(
                evidence, items, models.score_pairs, float(threshold),
                evidence.get("target_signature_sha256"),
            )
            result = {
                "schema": "trustxai-step6-natural-diagnostics-1",
                "split": args.split,
                "source_id": source_id,
                "evidence_input_sha256": evidence["input_sha256"],
                "matrix_file_sha256": matrix_sha256,
                "config_signature": config_signature,
                "frozen_threshold": threshold,
                "independent_semantic_validation": False,
                "records": records,
            }
            atomic_json(destination, result)
        records = result["variants"] if args.mode == "controlled" else result["records"]
        all_records.extend(records)
        source_bindings.append({
            "source_id": source_id,
            "input_sha256": evidence["input_sha256"],
            "checkpoint_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        })
        print(f"{args.mode.title()} diagnostics {index}/{len(files)} {source_id}", flush=True)

    calibration = (calibrate_thresholds(all_records)
                   if args.mode == "controlled" and args.split == "development" else None)
    if args.mode == "controlled":
        summary = public_summary(all_records, calibration)
        default_name = "CHECKER_DIAGNOSTICS.json"
        if calibration:
            atomic_json(args.private_root / args.split / "calibration.json", calibration)
    else:
        summary = natural_proxy_summary(all_records)
        summary.update({
            "sources": len(source_bindings),
            "requested_final_pairs": sum(row.get("stage") == "final"
                                         for row in all_records),
            "requested_P_initial_pairs": sum(
                row.get("condition") == "P" and row.get("stage") == "initial"
                for row in all_records),
            "requested_logical_rows": len(all_records),
        })
        default_name = "NATURAL_OUTPUT_DIAGNOSTICS.json"
    summary.update({
        "schema": f"trustxai-step6-{args.mode}-summary-2",
        "split": args.split,
        "mode": args.mode,
        "source_ids_sha256": digest(sorted(row["source_id"] for row in source_bindings)),
        "private_checkpoints_sha256": digest(source_bindings),
        "frozen_threshold": threshold if args.mode == "natural" else frozen_threshold,
        "freeze_file_sha256": freeze["file_sha256"] if freeze else None,
        "raw_text_published": False,
    })
    public_path = args.public_output or (
        args.repo / "research" / "step-06" / args.split / default_name)
    atomic_json(public_path, summary)
    print(json.dumps({
        "mode": args.mode,
        "sources": len(source_bindings),
        "records": len(all_records),
        "public_output": str(public_path),
        "selected_threshold": (calibration or {}).get("selected_threshold", threshold),
        "independent_semantic_validation": False,
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
