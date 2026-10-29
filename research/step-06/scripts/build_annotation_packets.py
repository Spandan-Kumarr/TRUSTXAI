#!/usr/bin/env python3
"""Build deterministic blinded annotation packets without creating judgments.

The inputs are private JSONL exports produced by the frozen research runner.
Raw packet text and the sealed mapping remain outside Git. The public output is
limited to counts and SHA-256 digests.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
from typing import Any


SCHEMA_VERSION = "1.0"
BASE_SEED = 20261027
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
ANNOTATION_ROOT = REPO_ROOT / "research/step-06/annotation"
CONDITIONS = {"B0", "B1", "B2", "B3", "B4", "P"}
FAULT_TYPES = {
    "option_name",
    "span_binding",
    "changed_result",
    "counts",
    "recheck_status",
    "all_interventions",
    "unsupported_clinical_clause",
    "missing_limitation",
}
FAULT_TYPE_ALIASES = {
    # Accept names from the early public instrument while emitting the names
    # used by the frozen diagnostic runner.
    "omitted_span_binding": "span_binding",
    "changed_answer_result": "changed_result",
    "test_flip_counts": "counts",
    "all_interventions_generalization": "all_interventions",
}
MECHANICAL_STATUSES = {
    "missing", "unparseable", "blocked", "status_only",
    "invalid_frozen_decision", "insufficient_evidence",
}
OUTPUT_STATUSES = MECHANICAL_STATUSES | {
    "generated", "baseline_unchecked", "fallback_template", "evidence_template",
}
FORBIDDEN_EVIDENCE_KEYS = {
    "answer", "answer_idx", "correct_answer", "correct_option", "gold", "gold_label",
    "condition", "checker", "nli", "repair", "prompt", "model", "construction_intent",
    "mutation_type",
}
NATURAL_KEYS = {
    "partition", "source_id", "logical_id", "condition", "stage", "output_status",
    "evidence_display", "views",
}
VARIANT_KEYS = {
    "partition", "source_id", "variant_id", "construction_intent", "mutation_type",
    "evidence_display", "views",
}
VARIANT_OPTIONAL_KEYS = {"instantiation_status", "not_instantiated_reason"}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{path.name}:{line_number}: invalid JSON: {error}") from error
            if not isinstance(row, dict):
                raise ValueError(f"{path.name}:{line_number}: each row must be an object")
            rows.append(row)
    if not rows:
        raise ValueError(f"{path}: no records")
    return rows


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{label}: invalid JSON in {path}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label}: {path} must contain one object")
    return value


def runtime_files(directory: Path, label: str) -> list[Path]:
    files = sorted(path for path in directory.glob("*.json") if path.is_file())
    if not files:
        raise ValueError(f"{label}: no JSON artifacts found in {directory}")
    return files


def unwrap_runner_checkpoint(path: Path, stage: str, partition: str) -> dict[str, Any]:
    envelope = read_json(path, stage)
    payload = envelope.get("payload")
    expected = {
        "schema": "trustxai-step6-matrix-v1",
        "stage": stage,
        "partition": partition,
    }
    if any(envelope.get(key) != value for key, value in expected.items()):
        raise ValueError(f"{path}: runner checkpoint identity mismatch")
    if not isinstance(payload, dict) or envelope.get("payload_sha256") != sha256_value(payload):
        raise ValueError(f"{path}: runner checkpoint payload digest mismatch")
    for key in ("source_id", "input_sha256"):
        if envelope.get(key) != payload.get(key):
            raise ValueError(f"{path}: runner checkpoint {key} binding mismatch")
    return payload


def evidence_display_from_payload(payload: dict[str, Any], label: str) -> dict[str, Any]:
    evidence, facts = payload.get("evidence"), payload.get("facts")
    if not isinstance(evidence, dict) or not isinstance(facts, dict):
        raise ValueError(f"{label}: evidence checkpoint lacks evidence/facts")
    if set(facts) != {"C1", "C2", "C3", "C4"} or not all(
            isinstance(facts[key], str) and facts[key].strip() for key in facts):
        raise ValueError(f"{label}: canonical C1-C4 facts are malformed")
    findings = []
    for index, span in enumerate(evidence.get("spans", [])):
        if not isinstance(span, dict) or not all(
                isinstance(span.get(key), str) and span[key] for key in ("id", "text")):
            raise ValueError(f"{label}: evidence span {index} is malformed")
        finding = {"id": span["id"], "text": span["text"]}
        for key in ("start", "end"):
            # The public input contract does not require offsets and the
            # validator intentionally permits only strings there.  Omit the
            # runner's integer offsets rather than weakening that contract.
            if isinstance(span.get(key), str) and span[key]:
                finding[key] = span[key]
        findings.append(finding)
    if not findings:
        raise ValueError(f"{label}: evidence checkpoint has no case findings")
    return {"case_findings": findings, **facts}


def flatten_pair(pair: Any, label: str) -> dict[str, str] | None:
    if pair is None:
        return None
    if not isinstance(pair, dict) or set(pair) != {"novice", "expert"}:
        raise ValueError(f"{label}: pair must contain novice and expert")
    output: dict[str, str] = {}
    for audience in ("novice", "expert"):
        claims = pair[audience]
        if not isinstance(claims, dict) or set(claims) != {"C1", "C2", "C3", "C4"}:
            raise ValueError(f"{label}: {audience} pair needs exactly C1-C4")
        if not all(isinstance(claims[key], str) and claims[key].strip() for key in claims):
            raise ValueError(f"{label}: {audience} contains an empty claim")
        output[audience] = "\n".join(f"{key}: {claims[key]}" for key in ("C1", "C2", "C3", "C4"))
    return output


def p_initial_natural_row(payload: dict[str, Any], evidence_display: dict[str, Any],
                          partition: str, label: str) -> dict[str, Any]:
    """Resolve the exact shared P initial generation for paired H3 review.

    The row is always present.  When no initial generation was attempted (for
    example because informative evidence was unavailable), it is an explicit
    mechanical ``missing`` row and will be sealed rather than sent to raters.
    """
    source_id = payload["source_id"]
    conditions = payload["conditions"]
    p_condition = conditions["P"]
    initial_id = p_condition.get("initial_generation_id")
    shared_ids = {
        conditions[name].get("initial_generation_id")
        for name in ("B1", "B2", "B3", "P")
        if conditions[name].get("initial_generation_id") is not None
    }
    row = {
        "partition": partition,
        "source_id": source_id,
        "logical_id": f"{source_id}-P-initial",
        "condition": "P",
        "stage": "initial",
        "evidence_display": evidence_display,
    }
    if initial_id is None:
        if shared_ids:
            raise ValueError(f"{label}: P lacks the shared initial generation used by peer conditions")
        return {**row, "output_status": "missing", "views": None}
    if shared_ids != {initial_id}:
        raise ValueError(f"{label}: B1/B2/B3/P do not identify one exact shared initial")
    generations = payload.get("generations")
    if not isinstance(generations, list):
        raise ValueError(f"{label}: matrix lacks generation records for P initial")
    matches = [generation for generation in generations
               if isinstance(generation, dict) and generation.get("generation_id") == initial_id]
    if len(matches) != 1:
        raise ValueError(f"{label}: P initial generation ID must resolve exactly once")
    output = matches[0].get("output")
    text = output.get("text") if isinstance(output, dict) else None
    try:
        pair = json.loads(text) if isinstance(text, str) else None
    except json.JSONDecodeError:
        pair = None
    if pair is None:
        return {**row, "output_status": "unparseable", "views": None}
    try:
        views = flatten_pair(pair, f"{label}:P-initial")
    except ValueError:
        return {**row, "output_status": "unparseable", "views": None}
    return {**row, "output_status": "generated", "views": views}


def normalize_runtime_artifacts(runtime_root: Path, private_root: Path,
                                partition: str) -> tuple[Path, Path]:
    """Create private normalized exports from frozen runner checkpoints.

    The normalized text remains outside Git and is immediately consumed by
    :func:`build`.  This removes any manual copy/edit step between prediction,
    diagnostics and blinded packet construction.
    """
    matrix_dir = runtime_root / partition / "matrix"
    evidence_dir = runtime_root / partition / "evidence"
    diagnostics_dir = runtime_root / partition / "diagnostics"
    evidence_by_source: dict[str, dict[str, Any]] = {}
    display_by_source: dict[str, dict[str, Any]] = {}
    for path in runtime_files(evidence_dir, "evidence"):
        payload = unwrap_runner_checkpoint(path, "evidence", partition)
        source_id = payload["source_id"]
        if source_id in evidence_by_source:
            raise ValueError(f"duplicate evidence source {source_id}")
        evidence_by_source[source_id] = payload
        display_by_source[source_id] = evidence_display_from_payload(payload, path.name)

    natural: list[dict[str, Any]] = []
    matrix_sources: set[str] = set()
    for path in runtime_files(matrix_dir, "matrix"):
        payload = unwrap_runner_checkpoint(path, "matrix", partition)
        source_id = payload["source_id"]
        if source_id in matrix_sources:
            raise ValueError(f"duplicate matrix source {source_id}")
        matrix_sources.add(source_id)
        evidence_payload = evidence_by_source.get(source_id)
        if evidence_payload is None or evidence_payload["input_sha256"] != payload["input_sha256"]:
            raise ValueError(f"{path}: matrix has no matching evidence checkpoint")
        conditions = payload.get("conditions")
        if not isinstance(conditions, dict) or set(conditions) != CONDITIONS:
            raise ValueError(f"{path}: matrix needs exactly B0-B4/P")
        for condition in sorted(CONDITIONS):
            result = conditions[condition]
            if not isinstance(result, dict) or result.get("status") not in OUTPUT_STATUSES:
                raise ValueError(f"{path}: {condition} has an unsupported output status")
            natural.append({
                "partition": partition,
                "source_id": source_id,
                "logical_id": f"{source_id}-{condition}-final",
                "condition": condition,
                "stage": "final",
                "output_status": result["status"],
                "evidence_display": display_by_source[source_id],
                "views": flatten_pair(result.get("views"), f"{path.name}:{condition}"),
            })
        natural.append(p_initial_natural_row(
            payload, display_by_source[source_id], partition, path.name))
    if matrix_sources != set(evidence_by_source):
        raise ValueError("matrix and evidence directories contain different source sets")

    variants: list[dict[str, Any]] = []
    diagnostic_sources: set[str] = set()
    for path in runtime_files(diagnostics_dir, "diagnostics"):
        document = read_json(path, "diagnostics")
        source_id = document.get("source_id")
        if not isinstance(source_id, str) or source_id in diagnostic_sources:
            raise ValueError(f"{path}: missing or duplicate diagnostic source")
        diagnostic_sources.add(source_id)
        evidence_payload = evidence_by_source.get(source_id)
        if (evidence_payload is None or
                document.get("evidence_input_sha256") != evidence_payload["input_sha256"]):
            raise ValueError(f"{path}: diagnostics have no matching evidence checkpoint")
        rows = document.get("variants")
        if not isinstance(rows, list):
            raise ValueError(f"{path}: diagnostics lack controlled variants")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"{path}: malformed controlled variant")
            status = row.get("instantiation_status")
            variants.append({
                "partition": partition,
                "source_id": source_id,
                "variant_id": row.get("variant_id"),
                "construction_intent": row.get("construction_intent"),
                "mutation_type": FAULT_TYPE_ALIASES.get(
                    row.get("mutation_type"), row.get("mutation_type")),
                "instantiation_status": status,
                "not_instantiated_reason": row.get("not_instantiated_reason"),
                "evidence_display": display_by_source[source_id],
                "views": flatten_pair(row.get("pair"), f"{path.name}:{row.get('variant_id')}"),
            })
    if diagnostic_sources != matrix_sources:
        raise ValueError("diagnostics and matrix directories contain different source sets")

    normalized = private_root / partition / "normalized_exports"
    natural_path = normalized / "natural.jsonl"
    variant_path = normalized / "controlled_variants.jsonl"
    write_jsonl(natural_path, natural)
    write_jsonl(variant_path, variants)
    return natural_path, variant_path


def require_exact_keys(row: dict[str, Any], allowed: set[str], label: str) -> None:
    missing = allowed - row.keys()
    extra = row.keys() - allowed
    if missing or extra:
        raise ValueError(f"{label}: schema mismatch; missing={sorted(missing)}, extra={sorted(extra)}")


def require_keys_with_optional(row: dict[str, Any], required: set[str], optional: set[str],
                               label: str) -> None:
    missing = required - row.keys()
    extra = row.keys() - required - optional
    if missing or extra:
        raise ValueError(f"{label}: schema mismatch; missing={sorted(missing)}, extra={sorted(extra)}")


def validate_evidence(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label}: evidence_display must be an object")
    expected = {"case_findings", "C1", "C2", "C3", "C4"}
    if set(value) != expected:
        raise ValueError(f"{label}: evidence_display keys must be {sorted(expected)}")
    for claim in ("C1", "C2", "C3", "C4"):
        if not isinstance(value[claim], str) or not value[claim].strip():
            raise ValueError(f"{label}: {claim} must be non-empty text")
    findings = value["case_findings"]
    if not isinstance(findings, list):
        raise ValueError(f"{label}: case_findings must be a list")
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict) or not {"id", "text"} <= finding.keys():
            raise ValueError(f"{label}: case finding {index} needs id and text")
        if set(finding) - {"id", "text", "start", "end"}:
            raise ValueError(f"{label}: case finding {index} contains an unapproved key")
        if not all(isinstance(finding[key], str) and finding[key] for key in ("id", "text")):
            raise ValueError(f"{label}: case finding {index} id/text must be non-empty")
    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, item in node.items():
                if key.lower() in FORBIDDEN_EVIDENCE_KEYS:
                    raise ValueError(f"{label}: forbidden evidence key {key!r}")
                walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(value)
    return value


def validate_views(value: Any, status: str | None, label: str) -> dict[str, str] | None:
    if value is None:
        if status is not None and status not in MECHANICAL_STATUSES:
            raise ValueError(f"{label}: null views require a mechanical output status")
        return None
    if not isinstance(value, dict) or set(value) != {"novice", "expert"}:
        raise ValueError(f"{label}: views must contain exactly novice and expert")
    if not all(isinstance(value[key], str) and value[key].strip() for key in value):
        raise ValueError(f"{label}: both views must be non-empty text")
    if status in MECHANICAL_STATUSES:
        raise ValueError(f"{label}: mechanical status cannot contain views")
    return value


def validate_inputs(natural: list[dict[str, Any]], variants: list[dict[str, Any]],
                    partition: str, fixture_mode: bool) -> None:
    logical_ids: set[str] = set()
    variant_ids: set[str] = set()
    natural_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    variants_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for index, row in enumerate(natural):
        label = f"natural[{index}]"
        require_exact_keys(row, NATURAL_KEYS, label)
        if row["partition"] != partition:
            raise ValueError(f"{label}: partition mismatch")
        if not isinstance(row["source_id"], str) or not row["source_id"]:
            raise ValueError(f"{label}: source_id must be non-empty text")
        if row["condition"] not in CONDITIONS:
            raise ValueError(f"{label}: unknown condition")
        if row["output_status"] not in OUTPUT_STATUSES:
            raise ValueError(f"{label}: unknown output_status")
        if not isinstance(row["logical_id"], str) or row["logical_id"] in logical_ids:
            raise ValueError(f"{label}: logical_id must be globally unique")
        logical_ids.add(row["logical_id"])
        validate_evidence(row["evidence_display"], label)
        validate_views(row["views"], row["output_status"], label)
        natural_by_source[row["source_id"]].append(row)

    for index, row in enumerate(variants):
        label = f"variant[{index}]"
        require_keys_with_optional(row, VARIANT_KEYS, VARIANT_OPTIONAL_KEYS, label)
        if row["partition"] != partition:
            raise ValueError(f"{label}: partition mismatch")
        if not isinstance(row["source_id"], str) or not row["source_id"]:
            raise ValueError(f"{label}: source_id must be non-empty text")
        if row["construction_intent"] not in {"supported", "faulty"}:
            raise ValueError(f"{label}: construction_intent must be supported or faulty")
        if not isinstance(row["variant_id"], str) or row["variant_id"] in variant_ids:
            raise ValueError(f"{label}: variant_id must be globally unique")
        if not isinstance(row["mutation_type"], str) or not row["mutation_type"]:
            raise ValueError(f"{label}: mutation_type must be non-empty text")
        status = row.get("instantiation_status", "instantiated")
        if status not in {"instantiated", "not_instantiated"}:
            raise ValueError(f"{label}: unknown instantiation_status")
        variant_ids.add(row["variant_id"])
        validate_evidence(row["evidence_display"], label)
        if status == "instantiated":
            if row.get("not_instantiated_reason") not in (None, ""):
                raise ValueError(f"{label}: an instantiated variant cannot have a missing-slot reason")
            if validate_views(row["views"], None, label) is None:
                raise ValueError(f"{label}: an instantiated controlled variant needs both views")
        else:
            if row["views"] is not None:
                raise ValueError(f"{label}: a missing controlled slot cannot contain views")
            if not isinstance(row.get("not_instantiated_reason"), str) or not row["not_instantiated_reason"].strip():
                raise ValueError(f"{label}: a missing controlled slot needs a reason")
        variants_by_source[row["source_id"]].append(row)

    if set(natural_by_source) != set(variants_by_source):
        raise ValueError("natural and controlled exports must contain the same sources")
    if fixture_mode:
        return

    expected_sources = 40 if partition == "development" else 60
    if len(natural_by_source) != expected_sources:
        raise ValueError(f"{partition} requires {expected_sources} sources")
    for source_id in sorted(natural_by_source):
        final_conditions = Counter(row["condition"] for row in natural_by_source[source_id]
                                   if row["stage"] == "final")
        if final_conditions != Counter({condition: 1 for condition in CONDITIONS}):
            raise ValueError(f"{source_id}: requires one final row for every condition")
        rows = variants_by_source[source_id]
        intents = Counter(row["construction_intent"] for row in rows)
        if intents != Counter({"supported": 4, "faulty": 8}):
            raise ValueError(f"{source_id}: requires four supported and eight faulty variants")
        fault_types = {
            FAULT_TYPE_ALIASES.get(row["mutation_type"], row["mutation_type"])
            for row in rows if row["construction_intent"] == "faulty"
        }
        if fault_types != FAULT_TYPES:
            raise ValueError(f"{source_id}: faulty variants do not match the frozen eight families")
        supported_types = [row["mutation_type"] for row in rows if row["construction_intent"] == "supported"]
        if len(set(supported_types)) != 4:
            raise ValueError(f"{source_id}: supported mutation types must be four distinct controls")


def blind_source(source_id: str, seed: int) -> str:
    value = hashlib.sha256(f"{seed}:source:{source_id}".encode()).hexdigest()[:16]
    return "S-" + value


def order_views(item_id: str, views: dict[str, str] | None, seed: int) -> tuple[dict[str, Any], dict[str, str | None]]:
    if views is None:
        return {"view_1": None, "view_2": None}, {"view_1": None, "view_2": None}
    swap = int(hashlib.sha256(f"{seed}:view:{item_id}".encode()).hexdigest(), 16) % 2
    audiences = ("expert", "novice") if swap else ("novice", "expert")
    return ({"view_1": views[audiences[0]], "view_2": views[audiences[1]]},
            {"view_1": audiences[0], "view_2": audiences[1]})


def build_items(natural: list[dict[str, Any]], variants: list[dict[str, Any]],
                partition: str, seed: int) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    items: list[dict[str, Any]] = []
    sealed: dict[str, Any] = {}
    nonreviewable: list[dict[str, Any]] = []
    natural_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in natural:
        key = sha256_value({"source_id": row["source_id"], "evidence": row["evidence_display"],
                            "views": row["views"]})
        natural_groups[key].append(row)

    for key in sorted(natural_groups):
        rows = sorted(natural_groups[key], key=lambda row: row["logical_id"])
        first = rows[0]
        if first["views"] is None:
            nonreviewable.append({
                "item_type": "mechanical_natural_output",
                "source_id": first["source_id"],
                "logical_roles": [
                    {name: row[name] for name in ("logical_id", "condition", "stage", "output_status")}
                    for row in rows
                ],
                "content_sha256": key,
                "disposition": "mechanical_failure_not_sent_to_raters",
            })
            continue
        item_id = "I-" + key[:16]
        ordered, audience_map = order_views(item_id, first["views"], seed)
        item = {
            "schema_version": SCHEMA_VERSION,
            "partition": partition,
            "item_id": item_id,
            "source_blind_id": blind_source(first["source_id"], seed),
            "evidence": first["evidence_display"],
            **ordered,
        }
        items.append(item)
        sealed[item_id] = {
            "item_type": "natural_output",
            "source_id": first["source_id"],
            "audience_map": audience_map,
            "logical_roles": [
                {key: row[key] for key in ("logical_id", "condition", "stage", "output_status")}
                for row in rows
            ],
            "content_sha256": key,
        }

    for row in sorted(variants, key=lambda value: value["variant_id"]):
        if row.get("instantiation_status", "instantiated") == "not_instantiated":
            nonreviewable.append({
                "item_type": "controlled_variant_missing_slot",
                "source_id": row["source_id"],
                "variant_id": row["variant_id"],
                "construction_intent": row["construction_intent"],
                "mutation_type": row["mutation_type"],
                "not_instantiated_reason": row["not_instantiated_reason"],
                "disposition": "not_instantiated_not_sent_to_raters",
            })
            continue
        key = sha256_value({"type": "controlled_variant", "source_id": row["source_id"],
                            "variant_id": row["variant_id"], "evidence": row["evidence_display"],
                            "views": row["views"]})
        item_id = "I-" + key[:16]
        if item_id in sealed:
            raise ValueError("item-id collision")
        ordered, audience_map = order_views(item_id, row["views"], seed)
        items.append({
            "schema_version": SCHEMA_VERSION,
            "partition": partition,
            "item_id": item_id,
            "source_blind_id": blind_source(row["source_id"], seed),
            "evidence": row["evidence_display"],
            **ordered,
        })
        sealed[item_id] = {
            "item_type": "controlled_variant",
            "source_id": row["source_id"],
            "audience_map": audience_map,
            "variant_id": row["variant_id"],
            "construction_intent": row["construction_intent"],
            "mutation_type": row["mutation_type"],
            "content_sha256": key,
        }
    if len({item["item_id"] for item in items}) != len(items):
        raise ValueError("duplicate item ID")
    return items, sealed, nonreviewable


def write_json(path: Path, value: Any, *, private: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    if private:
        temporary.chmod(0o600)
    temporary.replace(path)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(canonical_bytes(row).decode() + "\n")
    temporary.chmod(0o600)
    temporary.replace(path)


def build(natural_path: Path, variant_path: Path, private_root: Path, public_manifest: Path,
          partition: str, seed: int = BASE_SEED, fixture_mode: bool = False,
          force: bool = False) -> dict[str, Any]:
    try:
        private_root.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise ValueError("private packets must be written outside the Git repository")
    natural = read_jsonl(natural_path)
    variants = read_jsonl(variant_path)
    validate_inputs(natural, variants, partition, fixture_mode)
    items, sealed, nonreviewable = build_items(natural, variants, partition, seed)
    target = private_root / partition
    packet_paths = {rater: target / f"rater_{rater}.jsonl" for rater in ("A", "B")}
    sealed_path = target / "sealed_mapping.json"
    protected = [*packet_paths.values(), sealed_path]
    if (target / "responses").exists() or (target / "ANNOTATION_LOCK.json").exists():
        raise FileExistsError("locked or response-bearing annotation directory cannot be rebuilt")
    if not force and any(path.exists() for path in protected):
        raise FileExistsError("private packet exists; use --force only before annotation begins")

    for rater, offset in (("A", 101), ("B", 202)):
        ordered = [dict(item, packet_id=f"{partition}-rater-{rater}-v1") for item in items]
        random.Random(seed + offset).shuffle(ordered)
        write_jsonl(packet_paths[rater], ordered)
    write_json(sealed_path, {
        "schema_version": SCHEMA_VERSION,
        "partition": partition,
        "status": "sealed_private_mapping_not_rater_material",
        "seed": seed,
        "items": sealed,
        "nonreviewable": nonreviewable,
    }, private=True)

    source_count = len({row["source_id"] for row in natural})
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "status": "fixture_packets_built_not_annotated" if fixture_mode else "packets_built_not_annotated",
        "partition": partition,
        "seed": seed,
        "source_count": source_count,
        "private_input_counts": {"natural_logical_rows": len(natural), "controlled_variant_rows": len(variants)},
        "blinded_unique_item_count": len(items),
        "nonreviewable_slot_count": len(nonreviewable),
        "controlled_variants_instantiated": sum(
            row.get("instantiation_status", "instantiated") == "instantiated" for row in variants
        ),
        "controlled_variants_not_instantiated": sum(
            row.get("instantiation_status", "instantiated") == "not_instantiated" for row in variants
        ),
        "deduplicated_natural_logical_rows": len(natural) - sum(
            1 for value in sealed.values() if value["item_type"] == "natural_output"
        ),
        "inputs": {
            "natural_jsonl_sha256": sha256_file(natural_path),
            "controlled_variants_jsonl_sha256": sha256_file(variant_path),
        },
        "frozen_public_artifacts": {
            "builder_sha256": sha256_file(SCRIPT_PATH),
            "rubric_sha256": sha256_file(ANNOTATION_ROOT / "RUBRIC.json"),
            "response_schema_sha256": sha256_file(ANNOTATION_ROOT / "RESPONSE_SCHEMA.json"),
            "annotation_lock_schema_sha256": sha256_file(ANNOTATION_ROOT / "ANNOTATION_LOCK_SCHEMA.json"),
            "randomization_sha256": sha256_file(ANNOTATION_ROOT / "RANDOMIZATION.json")
        },
        "private_outputs": {
            "rater_A_jsonl_sha256": sha256_file(packet_paths["A"]),
            "rater_B_jsonl_sha256": sha256_file(packet_paths["B"]),
            "sealed_mapping_json_sha256": sha256_file(sealed_path),
        },
        "contains_raw_text": False,
        "contains_source_ids": False,
        "contains_rater_responses": False,
        "independent_annotation_complete": False,
    }
    write_json(public_manifest, manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_argument_group("private inputs")
    source.add_argument("--runtime-root", type=Path,
                        help="Step-6 private runtime root; consumes evidence/matrix/diagnostics directly")
    source.add_argument("--natural", type=Path, help="Already-normalized private natural-output JSONL")
    source.add_argument("--variants", type=Path, help="Already-normalized private controlled-variant JSONL")
    parser.add_argument("--private-root", type=Path, required=True, help="Private output root outside Git")
    parser.add_argument("--public-manifest", type=Path, required=True, help="Public counts-and-hashes manifest")
    parser.add_argument("--partition", choices=("development", "test"), required=True)
    parser.add_argument("--seed", type=int, default=BASE_SEED)
    parser.add_argument("--force", action="store_true", help="Replace packets only before annotation begins")
    parser.add_argument("--fixture-mode", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        args.private_root.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise ValueError("private packets must be written outside the Git repository")
    direct = args.runtime_root is not None
    normalized = args.natural is not None or args.variants is not None
    if direct == normalized:
        raise ValueError("Use either --runtime-root or both --natural and --variants")
    if direct:
        target = args.private_root / args.partition
        if (target / "responses").exists() or (target / "ANNOTATION_LOCK.json").exists():
            raise FileExistsError("locked or response-bearing annotation directory cannot be rebuilt")
        protected = [target / "rater_A.jsonl", target / "rater_B.jsonl",
                     target / "sealed_mapping.json"]
        if not args.force and any(path.exists() for path in protected):
            raise FileExistsError("private packet exists; use --force only before annotation begins")
        natural_path, variant_path = normalize_runtime_artifacts(
            args.runtime_root, args.private_root, args.partition)
    else:
        if args.natural is None or args.variants is None:
            raise ValueError("Both --natural and --variants are required")
        natural_path, variant_path = args.natural, args.variants
    manifest = build(natural_path, variant_path, args.private_root, args.public_manifest,
                     args.partition, args.seed, args.fixture_mode, args.force)
    print(json.dumps({"status": manifest["status"], "items": manifest["blinded_unique_item_count"],
                      "manifest": str(args.public_manifest)}))


if __name__ == "__main__":
    main()
