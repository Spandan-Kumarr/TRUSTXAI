#!/usr/bin/env python3
"""Create aggregate Step 6 results without copying case or model-output text.

Accepted layouts under --records-dir:

* SOURCE_RECORDS.jsonl, NATURAL_OUTPUTS.jsonl, DIAGNOSTIC_VARIANTS.jsonl,
  OMISSION_RECORDS.jsonl and COST_RECORDS.jsonl (lower-case names also work); or
* one JSON per source in evidence/, matrix/ and diagnostics/.  Per-source
  documents expose source_record/omission_record, natural_outputs/cost_records,
  and diagnostic_variants respectively.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "backend"))

from trustxai.research_analysis import (  # noqa: E402
    AnalysisContractError,
    IndependentLabelsIncomplete,
    analyze_h1,
    analyze_h2,
    analyze_h3,
    cost_summary,
    diagnostic_metrics,
    holm_adjust,
    omission_summary,
)


RAW_KEYS = {
    "case_text", "question", "options", "text", "raw", "prompt", "content",
    "novice", "expert", "views", "pair", "evidence", "facts", "output",
    "generation", "previous", "feedback", "system", "user",
    "source_outcomes", "per_source",
}

KIND_LAYOUT = {
    "sources": ("SOURCE_RECORDS", "evidence", ("source_records", "source_record")),
    "natural": ("NATURAL_OUTPUTS", "matrix", ("natural_outputs", "natural_output")),
    "diagnostics": ("DIAGNOSTIC_VARIANTS", "diagnostics", ("diagnostic_variants", "diagnostic_variant", "variants")),
    "omissions": ("OMISSION_RECORDS", "evidence", ("omission_records", "omission_record")),
    "costs": ("COST_RECORDS", "matrix", ("cost_records", "cost_record")),
}

CONDITIONS = ("B0", "B1", "B2", "B3", "B4", "P")
LETTERS = ("A", "B", "C", "D")
MECHANICAL_FAILURES = {
    "missing", "unparseable", "blocked", "status_only", "insufficient_evidence",
    "invalid_frozen_decision",
}


def _read_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise AnalysisContractError(f"{path}:{line_number} is not an object")
                rows.append(value)
    return rows


def _extract(document, keys: tuple[str, ...]) -> list[dict]:
    if isinstance(document, list):
        return [value for value in document if isinstance(value, dict)]
    if not isinstance(document, dict):
        return []
    for key in keys:
        if key in document:
            value = document[key]
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
            if isinstance(value, dict):
                return [value]
    return []


def _unwrap(document):
    """Return a verified-runner payload without weakening its on-disk envelope."""
    if isinstance(document, dict) and isinstance(document.get("payload"), dict):
        return document["payload"]
    return document


def _valid_pair(value) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"novice", "expert"}
        and all(isinstance(value[audience], dict)
                and set(value[audience]) == {"C1", "C2", "C3", "C4"}
                and all(isinstance(text, str) and text.strip()
                        for text in value[audience].values())
                for audience in ("novice", "expert"))
    )


def _parse_pair(text):
    try:
        value = json.loads(text)
    except (TypeError, ValueError):
        return None
    return value if _valid_pair(value) else None


def _runner_source(payload: dict) -> list[dict]:
    evidence = payload.get("evidence")
    if not isinstance(evidence, dict) or not isinstance(evidence.get("decision"), dict):
        return []
    return [{
        "source_id": payload.get("source_id", evidence.get("source_id")),
        "predicted_option": evidence["decision"].get("label"),
        "input_sha256": payload.get("input_sha256", evidence.get("input_sha256")),
    }]


def _runner_omission(payload: dict) -> list[dict]:
    evidence = payload.get("evidence")
    if not isinstance(evidence, dict) or not isinstance(evidence.get("decision"), dict):
        return []
    return [{
        "source_id": payload.get("source_id", evidence.get("source_id")),
        "original_label": evidence["decision"].get("label"),
        "available_spans": len(evidence.get("spans", [])),
        "omissions": [{"label": row.get("label"), "span_id": row.get("span_id")}
                      for row in evidence.get("omissions", [])],
        "selected": ({"label": evidence["selected"].get("label"),
                      "span_id": evidence["selected"].get("span_id")}
                     if isinstance(evidence.get("selected"), dict) else None),
        "recheck": ({"label": evidence["recheck"].get("label")}
                    if isinstance(evidence.get("recheck"), dict) else None),
    }]


def _release_status(raw_status: str | None) -> str:
    # A parsed baseline is an LLM generation whose semantic support is decided
    # by the independent annotation (or separately identified proxy), even
    # though the baseline deliberately had no automated release gate.
    return "generated" if raw_status in {"generated", "baseline_unchecked"} else str(raw_status or "missing")


def _runner_natural(payload: dict) -> list[dict]:
    conditions = payload.get("conditions")
    if not isinstance(conditions, dict):
        return []
    source_id = payload.get("source_id")
    rows = []
    for condition in CONDITIONS:
        value = conditions.get(condition, {})
        views = value.get("views")
        raw_status = value.get("status", "missing")
        applicable = value.get("llm_narrative_applicable", condition != "B4")
        rows.append({
            "source_id": source_id,
            "logical_id": f"{source_id}:{condition}:final",
            "condition": condition,
            "stage": "final",
            "output_kind": "llm_narrative" if applicable else "deterministic_template",
            "release_status": _release_status(raw_status),
            "raw_release_status": raw_status,
            "parseable": _valid_pair(views),
            "blocked": raw_status in MECHANICAL_FAILURES,
            "pair_sha256": _digest(views) if views is not None else None,
            "views": views,
            "pair_supported": None,
            "annotation_status": "pending_independent_annotation",
        })
    # H3 evaluates the exact common initial used by P.  It is a separate
    # logical row even when the annotation packet deduplicates identical text
    # shared across B1/B2/B3/P.
    p = conditions.get("P", {})
    initial_id = p.get("initial_generation_id")
    generation = next((row for row in payload.get("generations", [])
                       if row.get("generation_id") == initial_id), None)
    if initial_id:
        pair = _parse_pair((generation or {}).get("output", {}).get("text"))
        rows.append({
            "source_id": source_id,
            "logical_id": f"{source_id}:P:initial",
            "condition": "P", "stage": "initial", "output_kind": "llm_narrative",
            "release_status": "generated" if pair is not None else "unparseable",
            "raw_release_status": "shared_initial",
            "parseable": pair is not None, "blocked": pair is None,
            "pair_sha256": _digest(pair) if pair is not None else None,
            "views": pair, "pair_supported": None,
            "annotation_status": "pending_independent_annotation",
        })
    return rows


def _charged_conditions(stage: str) -> list[str]:
    if stage == "shared_initial_B1_B2_B3_P":
        return ["B1", "B2", "B3", "P"]
    if stage.startswith("B0"):
        return ["B0"]
    if stage.startswith("B1"):
        return ["B1"]
    if stage.startswith("B2"):
        return ["B2"]
    if stage.startswith("B3"):
        return ["B3"]
    if stage.startswith("P"):
        return ["P"]
    raise AnalysisContractError(f"Unknown physical generation stage {stage!r}")


def _runner_costs(payload: dict) -> list[dict]:
    if not isinstance(payload.get("generations"), list):
        return []
    source_id = payload.get("source_id")
    rows = []
    for generation in payload["generations"]:
        stage = str(generation.get("stage", ""))
        output = generation.get("output", {})
        row = {
            "physical_call_id": f"{source_id}:{generation.get('generation_id')}",
            "source_id": source_id,
            "component": stage,
            "call_kind": generation.get("kind"),
            "charged_conditions": _charged_conditions(stage),
            "wall_seconds": output.get("seconds", 0),
            "CPU_seconds": output.get("CPU_seconds", 0),
            "prompt_tokens": output.get("prompt_tokens", 0),
            "new_tokens": output.get("new_tokens", 0),
            "cache_hit": False,
        }
        if isinstance(output.get("peak_process_RSS_GiB"), (int, float)):
            row["peak_process_RSS_GiB"] = output["peak_process_RSS_GiB"]
        rows.append(row)
    return rows


def _derive_runner_rows(document, kind: str) -> list[dict]:
    payload = _unwrap(document)
    if not isinstance(payload, dict):
        return []
    if kind == "sources":
        return _runner_source(payload)
    if kind == "omissions":
        return _runner_omission(payload)
    if kind == "natural":
        return _runner_natural(payload)
    if kind == "costs":
        return _runner_costs(payload)
    if kind == "diagnostics" and isinstance(payload.get("variants"), list):
        return [row for row in payload["variants"] if isinstance(row, dict)]
    return []


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def load_records(root: Path, kind: str) -> tuple[list[dict], list[str]]:
    stem, directory, keys = KIND_LAYOUT[kind]
    candidates = [root / f"{stem}.jsonl", root / f"{stem.lower()}.jsonl",
                  root / f"{stem}.json", root / f"{stem.lower()}.json"]
    for path in candidates:
        if path.is_file():
            rows = _read_jsonl(path) if path.suffix == ".jsonl" else _extract(_read_json(path), keys + ("records",))
            return rows, [str(path.relative_to(root))]
    rows, paths = [], []
    folder = root / directory
    if folder.is_dir():
        for path in sorted(folder.glob("*.json")):
            document = _read_json(path)
            extracted = _extract(_unwrap(document), keys)
            if not extracted:
                extracted = _derive_runner_rows(document, kind)
            if extracted:
                rows.extend(extracted)
                paths.append(str(path.relative_to(root)))
    return rows, paths


def _read_rows_path(path: Path) -> list[dict]:
    if path.is_dir():
        files = sorted(candidate for candidate in path.glob("*.json") if candidate.is_file())
        if not files:
            raise AnalysisContractError(f"Natural-proxy directory has no JSON checkpoints: {path}")
        rows, seen_sources = [], set()
        for checkpoint in files:
            document = _read_json(checkpoint)
            if not isinstance(document, dict) or not isinstance(document.get("records"), list):
                raise AnalysisContractError(
                    f"Natural-proxy checkpoint lacks a records array: {checkpoint}")
            source_id, split = document.get("source_id"), document.get("split")
            if not isinstance(source_id, str) or not source_id or source_id in seen_sources:
                raise AnalysisContractError(
                    f"Natural-proxy checkpoints need unique non-empty source IDs: {checkpoint}")
            if checkpoint.stem != source_id:
                raise AnalysisContractError(
                    f"Natural-proxy filename/source binding mismatch: {checkpoint}")
            if split not in {"development", "test"}:
                raise AnalysisContractError(f"Natural-proxy checkpoint has an invalid split: {checkpoint}")
            seen_sources.add(source_id)
            source_rows = document["records"]
            if any(not isinstance(row, dict) for row in source_rows):
                raise AnalysisContractError(f"Natural-proxy records must be objects: {checkpoint}")
            for row in source_rows:
                if row.get("source_id") not in (None, source_id):
                    raise AnalysisContractError(
                        f"Natural-proxy row/source binding mismatch: {checkpoint}")
                rows.append({**row, "source_id": source_id, "split": split})
        return rows
    if not path.is_file():
        raise AnalysisContractError(f"Label/proxy file does not exist: {path}")
    value = _read_jsonl(path) if path.suffix == ".jsonl" else _read_json(path)
    if isinstance(value, dict):
        for key in ("records", "natural_outputs", "diagnostic_variants", "labels"):
            if isinstance(value.get(key), list):
                value = value[key]
                break
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise AnalysisContractError(f"Expected an array/JSONL of objects: {path}")
    return value


def validate_natural_proxy_bindings(rows: list[dict], sources: list[dict], *,
                                    expected_n: int, expected_split: str | None,
                                    expected_p_initial_source_ids: set[str] | None = None) -> None:
    """Bind post-hoc proxy checkpoints to the exact frozen source cohort."""
    source_ids = [row.get("source_id") for row in sources]
    if len(source_ids) != expected_n or len(set(source_ids)) != expected_n:
        raise AnalysisContractError("Frozen source cohort is incomplete or contains duplicate IDs")
    proxy_ids = {row.get("source_id") for row in rows}
    if proxy_ids != set(source_ids):
        raise AnalysisContractError(
            f"Natural-proxy source set mismatch: expected {expected_n}, received {len(proxy_ids)}")
    expected_initial = set(expected_p_initial_source_ids or ())
    if not expected_initial <= set(source_ids):
        raise AnalysisContractError("Expected P-initial proxy IDs are outside the frozen source cohort")
    seen = set()
    per_source = {source_id: set() for source_id in source_ids}
    for row in rows:
        key = (row.get("source_id"), row.get("condition"), row.get("stage", "final"))
        if key in seen:
            raise AnalysisContractError(f"Duplicate natural-proxy logical row: {key}")
        seen.add(key)
        if (row.get("condition") not in CONDITIONS or
                row.get("stage", "final") not in {"initial", "final"} or
                (row.get("stage", "final") == "initial" and row.get("condition") != "P")):
            raise AnalysisContractError(f"Unexpected natural-proxy logical row: {key}")
        if expected_split in {"development", "test"} and row.get("split") not in (None, expected_split):
            raise AnalysisContractError(
                f"Natural-proxy split mismatch for {row.get('source_id')}: {row.get('split')}")
        per_source[row["source_id"]].add((row["condition"], row.get("stage", "final")))
    finals = {(condition, "final") for condition in CONDITIONS}
    for source_id, logical_rows in per_source.items():
        required = finals | ({("P", "initial")} if source_id in expected_initial else set())
        if logical_rows != required:
            expectation = "six finals plus P initial" if source_id in expected_initial else "six finals and no P initial"
            raise AnalysisContractError(
                f"Natural-proxy checkpoint for {source_id} requires {expectation}")


def _default_gold(records_root: Path) -> Path | None:
    split = records_root.name
    for candidate in (records_root / f"{split}_gold.json",
                      records_root.parent / f"{split}_gold.json"):
        if candidate.is_file():
            return candidate
    return None


def attach_gold(sources: list[dict], gold_path: Path | None,
                *, expected_n: int) -> list[dict]:
    """Bind post-freeze gold to frozen decisions without exporting case text."""
    if gold_path is None:
        if all(row.get("correct_option") in LETTERS for row in sources):
            return sources
        raise AnalysisContractError(
            "Post-prediction gold is required; pass --gold after predictions are frozen")
    gold = _read_json(gold_path)
    if not isinstance(gold, dict) or any(value not in LETTERS for value in gold.values()):
        raise AnalysisContractError("Gold must be a source_id -> A/B/C/D object")
    by_source = {}
    for row in sources:
        source_id = row.get("source_id")
        if not source_id or source_id in by_source:
            raise AnalysisContractError("Frozen source records need unique source IDs")
        by_source[source_id] = dict(row)
    if len(by_source) != expected_n or set(by_source) != set(gold):
        raise AnalysisContractError(
            f"Gold/source identity mismatch: decisions={len(by_source)}, gold={len(gold)}, expected={expected_n}")
    for source_id, label in gold.items():
        by_source[source_id]["correct_option"] = label
    return [by_source[row["source_id"]] for row in sources]


def overlay_natural_labels(records: list[dict], labels: list[dict]) -> list[dict]:
    """Attach locked independent or explicit automated-proxy pair judgments."""
    indexed = {}
    for row in labels:
        key = (row.get("source_id"), row.get("condition"), row.get("stage", "final"))
        if not all(key) or key in indexed:
            raise AnalysisContractError(f"Duplicate or incomplete natural label key: {key}")
        indexed[key] = row
    output = []
    for record in records:
        value = dict(record)
        label = indexed.get((record.get("source_id"), record.get("condition"),
                             record.get("stage", "final")))
        if label is not None:
            supported = label.get("pair_supported")
            if not isinstance(supported, bool):
                endpoint = label.get("automated_proxy_llm_pair_endpoint")
                supported = endpoint == "pass" if endpoint in {"pass", "fail"} else None
            value["pair_supported"] = supported
            proxy_record = (
                str(label.get("analysis_status", "")).startswith("automated_proxy")
                or "automated_proxy_decision" in label
                or "automated_proxy_llm_pair_endpoint" in label
            )
            value["annotation_status"] = label.get(
                "annotation_status",
                "automated_proxy" if proxy_record else "pending_independent_annotation",
            )
            if label.get("independent_rater_count") is not None:
                value["independent_rater_count"] = label["independent_rater_count"]
            if label.get("annotation_lock_sha256") is not None:
                value["annotation_lock_sha256"] = label["annotation_lock_sha256"]
        output.append(value)
    return output


def _semantic_truth(row: dict, label: dict | None, annotation_mode: str) -> tuple[str, str, int | None]:
    if annotation_mode == "automated_proxy":
        return row.get("construction_intent"), "automated_proxy_construction_intent", None
    source = label or row
    truth = source.get("truth", source.get("independent_semantic_label"))
    if truth is None and isinstance(source.get("pair_supported"), bool):
        truth = "supported" if source["pair_supported"] else "faulty"
    if isinstance(truth, dict):
        truth = truth.get("truth", truth.get("label"))
    status = source.get("annotation_status", source.get("label_status",
                        "pending_independent_annotation"))
    return truth, status, source.get("independent_rater_count")


def diagnostic_analysis_rows(records: list[dict], *, threshold: float,
                             annotation_mode: str,
                             labels: list[dict] | None = None) -> list[dict]:
    """Expand one scored variant into the frozen typed+NLI/NLI-only pair."""
    label_index = {(row.get("source_id"), row.get("variant_id")): row
                   for row in (labels or [])}
    if len(label_index) != len(labels or []):
        raise AnalysisContractError("Duplicate controlled-variant semantic label")
    output = []
    key = str(float(threshold))
    for row in records:
        if row.get("method"):
            value = dict(row)
            if annotation_mode == "automated_proxy":
                value["truth"] = value.get("construction_intent", value.get("truth"))
                value["annotation_status"] = "automated_proxy_construction_intent"
            output.append(value)
            continue
        if not row.get("source_id") or not row.get("variant_id"):
            raise AnalysisContractError("Controlled diagnostic row lacks source_id/variant_id")
        truth, status, rater_count = _semantic_truth(
            row, label_index.get((row["source_id"], row["variant_id"])), annotation_mode)
        if truth not in {"supported", "faulty"}:
            # Retain construction intent only to preserve the planned slot and
            # make the formal gate fail closed on the annotation status.
            truth = row.get("construction_intent")
        decisions = row.get("decisions", {}).get(key, {})
        instantiated = row.get("instantiation_status") == "instantiated"
        score_signature = _digest([
            {name: item.get(name) for name in
             ("request_sha256", "status", "entailment", "neutral", "contradiction")}
            for item in row.get("nli", [])
        ])
        for method in ("typed_plus_nli", "nli_only"):
            decision = decisions.get(method, "missing") if instantiated else "missing"
            value = {
                "source_id": row["source_id"], "variant_id": row["variant_id"],
                "method": method, "truth": truth, "decision": decision,
                "annotation_status": status, "score_signature": score_signature,
                "nli_status": "scored" if row.get("nli_complete") else "unresolved",
                "instantiation_status": row.get("instantiation_status"),
            }
            if rater_count is not None:
                value["independent_rater_count"] = rater_count
            output.append(value)
    return output


def _public(value):
    """Defense in depth: strip raw text fields from aggregate/public output."""
    if isinstance(value, dict):
        return {key: _public(item) for key, item in value.items() if key not in RAW_KEYS}
    if isinstance(value, list):
        return [_public(item) for item in value]
    return value


def _write(path: Path, value) -> None:
    path.write_text(json.dumps(_public(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_or_block(function, *args, block_prefix="independent", **kwargs):
    try:
        return function(*args, **kwargs)
    except IndependentLabelsIncomplete as error:
        return {"analysis_status": f"blocked_{block_prefix}_labels", "reason": str(error)}
    except AnalysisContractError as error:
        return {"analysis_status": "blocked_contract_error", "reason": str(error)}


def _optional_records(explicit: Path | None, records_root: Path,
                      names: tuple[str, ...]) -> tuple[list[dict], str | None]:
    candidates = ([explicit] if explicit else []) + [records_root / name for name in names]
    for candidate in candidates:
        if candidate is not None and (candidate.is_file() or candidate.is_dir()):
            return _read_rows_path(candidate), str(candidate)
    return [], None


def _artifact_ref(path: Path | str | None) -> dict:
    if path is None:
        return {"present": False, "sha256": None}
    value = Path(path)
    if value.is_file():
        return {"present": True, "kind": "file",
                "sha256": hashlib.sha256(value.read_bytes()).hexdigest()}
    if value.is_dir():
        identities = [{"name": candidate.name,
                       "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest()}
                      for candidate in sorted(value.glob("*.json")) if candidate.is_file()]
        return {"present": True, "kind": "checkpoint_directory",
                "file_count": len(identities), "sha256": _digest(identities)}
    return {"present": False, "kind": None, "sha256": None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records-dir", type=Path, required=True,
                        help="Frozen runtime-record directory; aggregate JSONL or evidence/matrix/diagnostics subdirectories")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="New/existing directory for aggregate JSON outputs; no raw text is copied")
    parser.add_argument("--annotation-mode", choices=("independent", "single_rater", "automated_proxy"),
                        default="independent")
    parser.add_argument("--gold", type=Path,
                        help="Post-prediction source_id->A/B/C/D JSON; never an inference input")
    parser.add_argument("--natural-labels", type=Path,
                        help="Locked unblinded natural semantic labels (independent mode)")
    parser.add_argument("--variant-labels", type=Path,
                        help="Locked unblinded controlled-variant semantic labels (independent mode)")
    parser.add_argument("--natural-proxy", type=Path,
                        help="Post-hoc automated natural-output proxy JSON/JSONL")
    parser.add_argument("--diagnostic-threshold", type=float,
                        help="Frozen typed+NLI operating threshold; otherwise read from calibration/freeze")
    parser.add_argument("--expected-sources", type=int, default=60)
    parser.add_argument("--replicates", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20261027)
    args = parser.parse_args()

    if args.expected_sources in (40, 60):
        if args.replicates != 5000:
            parser.error("Frozen development/test analysis requires exactly 5,000 bootstrap replicates")
        if args.seed != 20261027:
            parser.error("Frozen development/test analysis requires seed 20261027")

    records_root, output = args.records_dir.resolve(), args.output_dir.resolve()
    if not records_root.is_dir():
        parser.error(f"records directory does not exist: {records_root}")
    output.mkdir(parents=True, exist_ok=True)
    loaded = {kind: load_records(records_root, kind) for kind in KIND_LAYOUT}
    sources = loaded["sources"][0]
    if not sources:
        parser.error("No source records found")
    try:
        sources = attach_gold(sources, args.gold or _default_gold(records_root),
                              expected_n=args.expected_sources)
    except AnalysisContractError as error:
        parser.error(str(error))

    natural = loaded["natural"][0]
    natural_label_rows, natural_label_path = _optional_records(
        args.natural_labels, records_root,
        ("NATURAL_SEMANTIC_LABELS.jsonl", "natural_semantic_labels.jsonl"),
    )
    natural_proxy_rows, natural_proxy_path = _optional_records(
        args.natural_proxy, records_root,
        ("natural-diagnostics", "NATURAL_AUTOMATED_PROXY.jsonl", "natural_automated_proxy.jsonl"),
    )
    if args.annotation_mode == "automated_proxy":
        if natural_proxy_rows:
            try:
                validate_natural_proxy_bindings(
                    natural_proxy_rows, sources, expected_n=args.expected_sources,
                    expected_split=records_root.name if records_root.name in {"development", "test"} else None,
                    expected_p_initial_source_ids={
                        row["source_id"] for row in natural
                        if row.get("condition") == "P" and row.get("stage") == "initial"
                    },
                )
            except AnalysisContractError as error:
                parser.error(str(error))
        natural = overlay_natural_labels(natural, natural_proxy_rows)
    elif natural_label_rows:
        natural = overlay_natural_labels(natural, natural_label_rows)

    threshold = args.diagnostic_threshold
    if threshold is None:
        for candidate in (records_root / "calibration.json",
                          records_root.parent / "development" / "calibration.json",
                          records_root / "freeze.json", records_root.parent / "freeze.json"):
            if candidate.is_file():
                value = _read_json(candidate)
                threshold = value.get("selected_threshold",
                    value.get("typed_plus_nli_selected_threshold",
                    value.get("checker", {}).get("selected_operating_threshold")))
                if isinstance(threshold, (int, float)):
                    break
    if threshold not in {0.60, 0.70, 0.80, 0.90, 0.95}:
        parser.error("A frozen diagnostic threshold from 0.60,0.70,0.80,0.90,0.95 is required")
    variant_label_rows, variant_label_path = _optional_records(
        args.variant_labels, records_root,
        ("CONTROLLED_VARIANT_SEMANTIC_LABELS.jsonl", "controlled_variant_semantic_labels.jsonl"),
    )
    try:
        diagnostic_rows = diagnostic_analysis_rows(
            loaded["diagnostics"][0], threshold=float(threshold),
            annotation_mode=args.annotation_mode,
            labels=variant_label_rows if args.annotation_mode != "automated_proxy" else None,
        )
    except AnalysisContractError as error:
        parser.error(str(error))

    require_independent = args.annotation_mode == "independent"
    common = dict(require_independent=require_independent, expected_n=args.expected_sources,
                  replicates=args.replicates, seed=args.seed)

    block_prefix = "independent" if require_independent else "proxy"
    h1 = (_run_or_block(analyze_h1, natural, sources, block_prefix=block_prefix, **common)
          if natural else {"analysis_status":"unavailable"})
    h2 = (_run_or_block(analyze_h2, diagnostic_rows, sources,
                        block_prefix=block_prefix, **common)
          if diagnostic_rows else {"analysis_status":"unavailable"})
    h3 = (_run_or_block(analyze_h3, natural, sources, block_prefix=block_prefix, **common)
          if natural else {"analysis_status":"unavailable"})
    if args.annotation_mode == "single_rater":
        for value in (h1, h2, h3):
            if value.get("analysis_status") == "non_independent_proxy":
                value["analysis_status"] = "single_rater_exploratory"
    elif args.annotation_mode == "automated_proxy":
        h1["semantic_label_basis"] = "post-hoc automated natural-output checker; not independent semantic review"
        h2["semantic_label_basis"] = "controlled construction intent; not independent semantic truth"
        h3["semantic_label_basis"] = "post-hoc automated natural-output checker; not independent semantic review"
    diagnostic = _run_or_block(diagnostic_metrics, sources, expected_n=args.expected_sources)
    omissions = (_run_or_block(omission_summary, loaded["omissions"][0], expected_n=args.expected_sources)
                 if loaded["omissions"][0] else {"analysis_status":"unavailable"})
    costs = _run_or_block(cost_summary, loaded["costs"][0]) if loaded["costs"][0] else {"analysis_status":"unavailable"}

    formal = {}
    if h2.get("analysis_status") == "independent":
        for metric, result in h2["paired_source_tests"].items():
            formal[f"H2_{metric}"] = result["two_sided_p"]
    if h3.get("analysis_status") == "independent":
        formal["H3_repair_yield"] = h3["mcnemar"]["two_sided_exact_p"]
    holm = {"analysis_status":"independent", "family": list(formal),
            "unadjusted": formal, "holm_adjusted": holm_adjust(formal)} if formal else {
                "analysis_status":"blocked_or_unavailable", "family": []}

    if args.annotation_mode == "independent":
        hypothesis_outputs = {
            "H1_PRIMARY.json": h1,
            "H2_CHECKER.json": h2,
            "H3_REPAIR.json": h3,
        }
    else:
        proxy_names = ({
            "H1_AUTOMATED_PROXY.json": h1,
            "H2_CONSTRUCTION_INTENT_PROXY.json": h2,
            "H3_AUTOMATED_PROXY.json": h3,
        } if args.annotation_mode == "automated_proxy" else {
            "H1_SINGLE_RATER_EXPLORATORY.json": h1,
            "H2_SINGLE_RATER_EXPLORATORY.json": h2,
            "H3_SINGLE_RATER_EXPLORATORY.json": h3,
        })
        hypothesis_outputs = {
            "H1_PRIMARY.json": {"analysis_status": "not_run_requires_two_independent_raters",
                                "proxy_or_exploratory_output": next(iter(proxy_names))},
            "H2_CHECKER.json": {"analysis_status": "not_run_requires_two_independent_raters",
                                "proxy_or_exploratory_output": list(proxy_names)[1]},
            "H3_REPAIR.json": {"analysis_status": "not_run_requires_two_independent_raters",
                               "proxy_or_exploratory_output": list(proxy_names)[2]},
            **proxy_names,
        }
    outputs = {
        **hypothesis_outputs,
        "DIAGNOSTIC_ACCURACY.json": diagnostic,
        "OMISSION_AUDIT.json": omissions,
        "COSTS.json": costs,
        "HOLM_SECONDARY.json": holm,
    }
    for filename, value in outputs.items():
        _write(output / filename, value)
    status = {
        "analysis_status": args.annotation_mode,
        "formal_hypotheses_completed": args.annotation_mode == "independent" and all(
            value.get("analysis_status") == "independent" for value in (h1, h2, h3)),
        "semantic_label_boundary": (
            "two-rater independent consensus/adjudication"
            if args.annotation_mode == "independent" else
            "automated construction-intent/proxy; not independent semantic ground truth"
            if args.annotation_mode == "automated_proxy" else
            "single-rater exploratory; not a formal endpoint"
        ),
        "records_layout": records_root.name,
        "expected_sources": args.expected_sources,
        "bootstrap_replicates": args.replicates,
        "seed": args.seed,
        "frozen_operating_threshold": threshold,
        "inputs": {
            **{kind: {"records": len(rows), "file_count": len(paths),
                      "file_identity_list_sha256": _digest(paths)}
               for kind, (rows, paths) in loaded.items()},
            "post_prediction_gold": _artifact_ref(args.gold or _default_gold(records_root)),
            "natural_semantic_labels": _artifact_ref(natural_label_path),
            "natural_automated_proxy": _artifact_ref(natural_proxy_path),
            "controlled_variant_semantic_labels": _artifact_ref(variant_label_path),
        },
        "outputs": {filename: value.get("analysis_status", "complete") if isinstance(value, dict) else "complete"
                    for filename, value in outputs.items()},
        "raw_text_exported": False,
    }
    _write(output / "RESULTS_SUMMARY.json", status)
    blocked = any(value.get("analysis_status", "").startswith("blocked_")
                  for value in (h1, h2, h3))
    return 2 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
