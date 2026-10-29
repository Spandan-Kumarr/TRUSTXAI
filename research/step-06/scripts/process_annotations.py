#!/usr/bin/env python3
"""Validate, adjudicate, and lock Step 6 human semantic annotations.

``prepare`` validates two complete independent response files while blinded,
records pre-adjudication agreement, and creates an adjudication queue.
``lock`` consumes a completed human adjudication record, persists the response
lock, then opens the sealed mapping and writes analyzer-ready semantic labels.
No rating is defaulted or inferred from construction intent.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator


SCRIPT_PATH = Path(__file__).resolve()
REPOSITORY_ROOT = SCRIPT_PATH.parents[3]
ANNOTATION_ROOT = REPOSITORY_ROOT / "research" / "step-06" / "annotation"
SCHEMA_VERSION = "1.0"
CLAIMS = ("C1", "C2", "C3", "C4")
VIEWS = ("view_1", "view_2")
PACKET_KEYS = {
    "schema_version", "partition", "item_id", "source_blind_id",
    "evidence", "view_1", "view_2", "packet_id",
}
ITEM_ID_RE = re.compile(r"^I-[0-9a-f]{16}$")
SOURCE_BLIND_RE = re.compile(r"^S-[0-9a-f]{16}$")
RATER_ID_RE = re.compile(r"^R-[A-Za-z0-9_-]+$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

PREPARE_RECORD_NAME = "PREPARE_RECORD.json"
AGREEMENT_REPORT_NAME = "AGREEMENT_REPORT.json"
ADJUDICATION_QUEUE_NAME = "ADJUDICATION_QUEUE.jsonl"
LOCK_NAME = "ANNOTATION_LOCK.json"
NATURAL_LABELS_NAME = "NATURAL_SEMANTIC_LABELS.jsonl"
CONTROLLED_LABELS_NAME = "CONTROLLED_VARIANT_SEMANTIC_LABELS.jsonl"
PROVENANCE_NAME = "CONSENSUS_PROVENANCE.json"
ADJUDICATION_RECORD_NAME = "ADJUDICATION_RECORD.jsonl"


class AnnotationProcessingError(ValueError):
    """A human-annotation input violates the frozen workflow contract."""


def _reject_duplicate_keys(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AnnotationProcessingError(f"Duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _json_loads(text: str, *, label: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except AnnotationProcessingError:
        raise
    except json.JSONDecodeError as error:
        raise AnnotationProcessingError(
            f"{label}: invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error


def _read_json(path: Path, *, label: str) -> Any:
    try:
        return _json_loads(path.read_text(encoding="utf-8"), label=label)
    except (OSError, UnicodeError) as error:
        raise AnnotationProcessingError(f"{label}: cannot read {path}: {error}") from error


def _read_jsonl(path: Path, *, label: str, allow_empty: bool = False) -> list[dict[str, Any]]:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise AnnotationProcessingError(f"{label}: cannot read {path}: {error}") from error
    if not raw:
        if allow_empty:
            return []
        raise AnnotationProcessingError(f"{label}: JSONL file is empty")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            raise AnnotationProcessingError(f"{label}: blank JSONL line {number}")
        value = _json_loads(line, label=f"{label} line {number}")
        if not isinstance(value, dict):
            raise AnnotationProcessingError(f"{label} line {number}: expected a JSON object")
        rows.append(value)
    if not rows and not allow_empty:
        raise AnnotationProcessingError(f"{label}: JSONL file has no rows")
    return rows


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def _jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(
        (_canonical_json(dict(row)) + "\n").encode("utf-8") for row in rows
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()
    except OSError as error:
        raise AnnotationProcessingError(f"Cannot hash {path}: {error}") from error


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_timestamp(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AnnotationProcessingError(f"{label}: a non-empty timestamp is required")
    value = value.strip()
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise AnnotationProcessingError(f"{label}: invalid ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise AnnotationProcessingError(f"{label}: timestamp must include a timezone")
    return value


def _assert_no_fill(value: Any, *, label: str) -> None:
    if isinstance(value, str) and "__FILL__" in value:
        raise AnnotationProcessingError(f"{label}: contains an uncompleted __FILL__ marker")
    if isinstance(value, dict):
        for key, child in value.items():
            _assert_no_fill(child, label=f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_fill(child, label=f"{label}[{index}]")


def _validate_schema(instance: Any, schema: Mapping[str, Any], *, label: str) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as error:
        raise AnnotationProcessingError(f"{label}: invalid JSON Schema: {error}") from error
    errors = sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda item: tuple(str(part) for part in item.absolute_path),
    )
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        raise AnnotationProcessingError(f"{label}.{location}: {error.message}")


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _validate_private_output(path: Path) -> None:
    if _is_within(path, REPOSITORY_ROOT):
        raise AnnotationProcessingError(
            f"Private annotation output must be outside the Git repository: {path}"
        )


def _write_new(path: Path, payload: bytes, *, mode: int = 0o600) -> None:
    """Create one artifact without following or replacing an existing path."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    except FileExistsError as error:
        raise AnnotationProcessingError(f"Refusing to overwrite existing artifact: {path}") from error
    except OSError as error:
        raise AnnotationProcessingError(f"Cannot create {path}: {error}") from error
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        path.chmod(mode)
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def _input_record(path: Path) -> dict[str, str]:
    path = path.resolve()
    if not path.is_file():
        raise AnnotationProcessingError(f"Required input is not a regular file: {path}")
    return {"path": str(path), "sha256": _sha256_file(path)}


def _validate_digest(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
        raise AnnotationProcessingError(f"{label}: expected a lowercase SHA-256 digest")
    return value


def _validate_manifest(
    manifest_path: Path, *, partition: str, packet_a_path: Path,
    packet_b_path: Path, response_schema_path: Path, rubric_path: Path,
    lock_schema_path: Path,
) -> dict[str, Any]:
    manifest = _read_json(manifest_path, label="packet manifest")
    if not isinstance(manifest, dict):
        raise AnnotationProcessingError("Packet manifest must be a JSON object")
    if manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("partition") != partition:
        raise AnnotationProcessingError("Use the partition-specific frozen packet manifest")
    if manifest.get("status") != "packets_built_not_annotated":
        raise AnnotationProcessingError("Packet manifest has an unexpected status")
    if manifest.get("contains_rater_responses") is not False:
        raise AnnotationProcessingError("Manifest must describe blinded packets, not responses")
    frozen, private = manifest.get("frozen_public_artifacts"), manifest.get("private_outputs")
    if not isinstance(frozen, dict) or not isinstance(private, dict):
        raise AnnotationProcessingError("Packet manifest lacks frozen artifact digests")
    for key, path in (
        ("response_schema_sha256", response_schema_path),
        ("rubric_sha256", rubric_path),
        ("annotation_lock_schema_sha256", lock_schema_path),
    ):
        expected = _validate_digest(frozen.get(key), label=f"manifest.{key}")
        actual = _sha256_file(path)
        if expected != actual:
            raise AnnotationProcessingError(f"Frozen artifact hash mismatch for {path.name}")
    for key, path in (
        ("rater_A_jsonl_sha256", packet_a_path),
        ("rater_B_jsonl_sha256", packet_b_path),
    ):
        expected = _validate_digest(private.get(key), label=f"manifest.private_outputs.{key}")
        if expected != _sha256_file(path):
            raise AnnotationProcessingError(f"Packet hash mismatch for {path.name}")
    _validate_digest(private.get("sealed_mapping_json_sha256"),
                     label="manifest.private_outputs.sealed_mapping_json_sha256")
    count = manifest.get("blinded_unique_item_count")
    if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
        raise AnnotationProcessingError("Manifest blinded_unique_item_count must be positive")
    return manifest


def _packet_index(rows: Sequence[dict[str, Any]], *, partition: str, rater: str):
    expected_packet_id = f"{partition}-rater-{rater}-v1"
    indexed: dict[str, dict[str, Any]] = {}
    for number, row in enumerate(rows, 1):
        label = f"rater {rater} packet line {number}"
        if set(row) != PACKET_KEYS:
            raise AnnotationProcessingError(f"{label}: packet keys differ from the frozen contract")
        _assert_no_fill(row, label=label)
        if row.get("schema_version") != SCHEMA_VERSION or row.get("partition") != partition:
            raise AnnotationProcessingError(f"{label}: schema version or partition mismatch")
        if row.get("packet_id") != expected_packet_id:
            raise AnnotationProcessingError(f"{label}: expected packet_id {expected_packet_id!r}")
        item_id = row.get("item_id")
        if not isinstance(item_id, str) or not ITEM_ID_RE.fullmatch(item_id) or item_id in indexed:
            raise AnnotationProcessingError(f"{label}: invalid or duplicate opaque item ID")
        blind_id = row.get("source_blind_id")
        if not isinstance(blind_id, str) or not SOURCE_BLIND_RE.fullmatch(blind_id):
            raise AnnotationProcessingError(f"{label}: invalid opaque source ID")
        if not isinstance(row.get("evidence"), dict):
            raise AnnotationProcessingError(f"{label}: evidence must be an object")
        if not isinstance(row.get("view_1"), str) or not isinstance(row.get("view_2"), str):
            raise AnnotationProcessingError(f"{label}: both views must be text")
        indexed[item_id] = row
    return indexed, expected_packet_id


def _validate_packets(packet_a_path: Path, packet_b_path: Path, *, partition: str,
                      expected_count: int):
    if packet_a_path.resolve() == packet_b_path.resolve():
        raise AnnotationProcessingError("Rater packet paths must be distinct")
    indexed_a, packet_id_a = _packet_index(
        _read_jsonl(packet_a_path, label="rater A packet"), partition=partition, rater="A")
    indexed_b, packet_id_b = _packet_index(
        _read_jsonl(packet_b_path, label="rater B packet"), partition=partition, rater="B")
    if len(indexed_a) != expected_count or len(indexed_b) != expected_count:
        raise AnnotationProcessingError(
            f"Packet count mismatch: manifest={expected_count}, A={len(indexed_a)}, B={len(indexed_b)}")
    if set(indexed_a) != set(indexed_b):
        raise AnnotationProcessingError("Rater packets do not contain the same item IDs")
    for item_id in sorted(indexed_a):
        left = {key: value for key, value in indexed_a[item_id].items() if key != "packet_id"}
        right = {key: value for key, value in indexed_b[item_id].items() if key != "packet_id"}
        if left != right:
            raise AnnotationProcessingError(f"Rater packets differ for item {item_id}")
    return indexed_a, indexed_b, packet_id_a, packet_id_b


def _semantic_response_checks(row: Mapping[str, Any], *, label: str) -> None:
    unresolved = False
    for view_name in VIEWS:
        view = row[view_name]
        present, extras = view["extra_claim_present"], view["extra_claims"]
        if present == "yes" and not extras:
            raise AnnotationProcessingError(
                f"{label}.{view_name}: extra_claim_present=yes requires a recorded claim")
        if present == "no" and extras:
            raise AnnotationProcessingError(
                f"{label}.{view_name}: extra_claim_present=no requires an empty list")
        unresolved |= present == "unresolved"
        unresolved |= any(view[f"{claim}_status"] == "unresolved" for claim in CLAIMS)
        unresolved |= any(extra["status"] == "unresolved" for extra in extras)
    unresolved |= any(row["cross_view"][claim] == "unresolved" for claim in CLAIMS)
    if (row["reviewable"] == "no" or row["needs_adjudication"] == "yes" or unresolved) \
            and not row["notes"].strip():
        raise AnnotationProcessingError(
            f"{label}: review defects, unresolved ratings, and adjudication flags require notes")


def _response_index(path: Path, *, label: str, packet: Mapping[str, Mapping[str, Any]],
                    expected_packet_id: str, schema: Mapping[str, Any]):
    indexed: dict[str, dict[str, Any]] = {}
    rater_ids: set[str] = set()
    for number, row in enumerate(_read_jsonl(path, label=label), 1):
        row_label = f"{label} line {number}"
        _assert_no_fill(row, label=row_label)
        _validate_schema(row, schema, label=row_label)
        _semantic_response_checks(row, label=row_label)
        item_id = row["item_id"]
        if item_id in indexed:
            raise AnnotationProcessingError(f"{row_label}: duplicate response for {item_id}")
        if item_id not in packet:
            raise AnnotationProcessingError(f"{row_label}: item is not assigned: {item_id}")
        if row["packet_id"] != expected_packet_id:
            raise AnnotationProcessingError(f"{row_label}: response packet binding mismatch")
        indexed[item_id] = row
        rater_ids.add(row["rater_id"])
    missing = set(packet) - set(indexed)
    if missing or len(indexed) != len(packet):
        raise AnnotationProcessingError(
            f"{label}: incomplete response coverage ({len(indexed)}/{len(packet)})")
    if len(rater_ids) != 1:
        raise AnnotationProcessingError(f"{label}: every row must use one stable rater ID")
    rater_id = next(iter(rater_ids))
    if not RATER_ID_RE.fullmatch(rater_id):
        raise AnnotationProcessingError(f"{label}: invalid rater ID")
    return indexed, rater_id


DECLARATION_FIELDS = {
    "rater pseudonym": "rater_id",
    "date": "date",
    "relevant training/background": "background",
    "relationship to the project": "relationship",
    "independent of the other rater": "independent",
    "read protocol and frozen rubric": "protocol_read",
    "completed qualification exercise": "qualification",
    "accessed condition labels, checker scores, intended mutations, benchmark gold labels or the other response file before lock": "accessed_blinded_material",
    "possible style-based unblinding observed": "style_disclosure",
    "conflicts or other disclosures": "conflicts",
}


def _parse_declaration(path: Path, *, expected_rater_id: str, label: str) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise AnnotationProcessingError(f"{label}: cannot read declaration: {error}") from error
    if not text.strip() or "__FILL__" in text:
        raise AnnotationProcessingError(f"{label}: declaration is blank or incomplete")
    parsed: dict[str, str] = {}
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        match = re.match(r"^\s*-\s*([^:]+):\s*(.*?)\s*$", line)
        if not match:
            continue
        field = re.sub(r"\s+", " ", match.group(1).strip().casefold())
        if field in DECLARATION_FIELDS:
            key = DECLARATION_FIELDS[field]
            if key in parsed:
                raise AnnotationProcessingError(f"{label}: duplicate field at line {number}")
            parsed[key] = match.group(2).strip()
    signature = ""
    for index, line in enumerate(lines):
        match = re.match(r"^\s*Signature or authenticated acknowledgement:\s*(.*?)\s*$",
                         line, flags=re.IGNORECASE)
        if match:
            signature = match.group(1).strip()
            if not signature:
                signature = next((item.strip() for item in lines[index + 1:] if item.strip()), "")
            break
    parsed["signature"] = signature
    required = set(DECLARATION_FIELDS.values()) | {"signature"}
    missing = sorted(key for key in required if not parsed.get(key, "").strip())
    if missing:
        raise AnnotationProcessingError(
            f"{label}: declaration fields must be completed (missing {', '.join(missing)})")
    if parsed["rater_id"] != expected_rater_id:
        raise AnnotationProcessingError(f"{label}: pseudonym does not match response rater ID")
    expected = {"independent": "yes", "protocol_read": "yes", "qualification": "yes",
                "accessed_blinded_material": "no"}
    for key, answer in expected.items():
        if parsed[key].strip().casefold() != answer:
            raise AnnotationProcessingError(f"{label}: {key} must be explicitly {answer!r}")
    return parsed


def _normalized_extra_claims(value: Sequence[Mapping[str, Any]]) -> tuple[tuple[str, str], ...]:
    # Free-text reasons are audit narratives, not rating dimensions. Quotes and
    # statuses affect the semantic judgment and therefore require adjudication.
    return tuple(sorted((str(item["quote"]), str(item["status"])) for item in value))


def _get_path(row: Mapping[str, Any], path: str) -> Any:
    value: Any = row
    for part in path.split("."):
        if not isinstance(value, Mapping) or part not in value:
            raise AnnotationProcessingError(f"Missing rating field {path}")
        value = value[part]
    return value


def _set_path(row: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    target: dict[str, Any] = row
    for part in parts[:-1]:
        child = target.get(part)
        if not isinstance(child, dict):
            raise AnnotationProcessingError(f"Cannot adjudicate unknown field {path}")
        target = child
    if parts[-1] not in target:
        raise AnnotationProcessingError(f"Cannot adjudicate unknown field {path}")
    target[parts[-1]] = deepcopy(value)


def _comparison_value(row: Mapping[str, Any], path: str) -> Any:
    value = _get_path(row, path)
    if path.endswith(".scope_flags"):
        return sorted(value)
    if path.endswith(".extra_claims"):
        return [list(item) for item in _normalized_extra_claims(value)]
    return value


RATING_PATHS = (
    "reviewable",
    *(f"{view}.{claim}_status" for view in VIEWS for claim in CLAIMS),
    *(f"{view}.extra_claim_present" for view in VIEWS),
    *(f"{view}.extra_claims" for view in VIEWS),
    *(f"{view}.scope_flags" for view in VIEWS),
    *(f"cross_view.{claim}" for claim in CLAIMS),
    "needs_adjudication",
)


def _view_supported(view: Mapping[str, Any]) -> bool:
    if any(view[f"{claim}_status"] != "supported" for claim in CLAIMS):
        return False
    if view["extra_claim_present"] == "unresolved":
        return False
    return all(item["status"] == "supported" for item in view["extra_claims"])


def _pair_supported(row: Mapping[str, Any]) -> bool:
    return row["reviewable"] == "yes" and all(_view_supported(row[view]) for view in VIEWS)


def _has_unresolved(row: Mapping[str, Any]) -> bool:
    if row["reviewable"] == "no":
        return True
    for view_name in VIEWS:
        view = row[view_name]
        if view["extra_claim_present"] == "unresolved":
            return True
        if any(view[f"{claim}_status"] == "unresolved" for claim in CLAIMS):
            return True
        if any(item["status"] == "unresolved" for item in view["extra_claims"]):
            return True
    return any(row["cross_view"][claim] == "unresolved" for claim in CLAIMS)


def _resolution_paths(row_a: Mapping[str, Any], row_b: Mapping[str, Any]):
    paths: set[str] = set()
    reasons: set[str] = set()
    for path in RATING_PATHS:
        if _comparison_value(row_a, path) != _comparison_value(row_b, path):
            paths.add(path)
            reasons.add("rater_disagreement")
    if row_a["reviewable"] == "no" or row_b["reviewable"] == "no":
        paths.add("reviewable")
        reasons.add("unreviewable")
    if row_a["needs_adjudication"] == "yes" or row_b["needs_adjudication"] == "yes":
        paths.add("needs_adjudication")
        reasons.add("rater_requested_adjudication")
    for row in (row_a, row_b):
        for view_name in VIEWS:
            view = row[view_name]
            for claim in CLAIMS:
                if view[f"{claim}_status"] == "unresolved":
                    paths.add(f"{view_name}.{claim}_status")
                    reasons.add("unresolved_rating")
            if view["extra_claim_present"] == "unresolved":
                paths.update({f"{view_name}.extra_claim_present", f"{view_name}.extra_claims"})
                reasons.add("unresolved_rating")
            if any(item["status"] == "unresolved" for item in view["extra_claims"]):
                paths.add(f"{view_name}.extra_claims")
                reasons.add("unresolved_rating")
        for claim in CLAIMS:
            if row["cross_view"][claim] == "unresolved":
                paths.add(f"cross_view.{claim}")
                reasons.add("unresolved_rating")
    # These combinations contradict the recorded rubric fields. Queue enough
    # fields for a human to resolve them without changing the frozen endpoint.
    for view_name in VIEWS:
        for row in (row_a, row_b):
            if _view_supported(row[view_name]) and row[view_name]["scope_flags"]:
                paths.update(f"{view_name}.{claim}_status" for claim in CLAIMS)
                paths.update({f"{view_name}.extra_claim_present", f"{view_name}.extra_claims",
                              f"{view_name}.scope_flags"})
                reasons.add("internally_inconsistent_scope_flag")
    for row in (row_a, row_b):
        if all(_view_supported(row[view]) for view in VIEWS):
            for claim in CLAIMS:
                if row["cross_view"][claim] != "preserved":
                    paths.update({f"view_1.{claim}_status", f"view_2.{claim}_status",
                                  f"cross_view.{claim}"})
                    reasons.add("internally_inconsistent_cross_view")
    return paths, reasons


def _kappa(left: Sequence[Any], right: Sequence[Any]) -> dict[str, Any]:
    if len(left) != len(right) or not left:
        raise AnnotationProcessingError("Agreement dimensions require equal non-empty ratings")
    left = [_canonical_json(value) for value in left]
    right = [_canonical_json(value) for value in right]
    agreements = sum(a == b for a, b in zip(left, right))
    count = len(left)
    observed = agreements / count
    counts_a, counts_b = Counter(left), Counter(right)
    expected = sum((counts_a[key] / count) * (counts_b[key] / count)
                   for key in set(counts_a) | set(counts_b))
    if math.isclose(expected, 1.0, rel_tol=0.0, abs_tol=1e-15):
        kappa, status = None, "undefined_zero_expected_disagreement"
    else:
        kappa, status = (observed - expected) / (1.0 - expected), "computed"
    return {
        "observations": count, "agreements": agreements, "agreement": observed,
        "percent_agreement": observed * 100.0, "cohen_kappa": kappa,
        "kappa_status": status, "expected_agreement": expected,
    }


def _agreement_dimensions(responses_a: Mapping[str, Mapping[str, Any]],
                          responses_b: Mapping[str, Mapping[str, Any]]):
    item_ids = sorted(responses_a)
    dimensions: dict[str, dict[str, Any]] = {}

    def add(name: str, getter) -> None:
        left: list[Any] = []
        right: list[Any] = []
        for item_id in item_ids:
            values_a, values_b = getter(responses_a[item_id]), getter(responses_b[item_id])
            left.extend(values_a if isinstance(values_a, list) else [values_a])
            right.extend(values_b if isinstance(values_b, list) else [values_b])
        dimensions[name] = _kappa(left, right)

    add("claim_status", lambda row: [row[view][f"{claim}_status"]
                                     for view in VIEWS for claim in CLAIMS])
    for view in VIEWS:
        for claim in CLAIMS:
            add(f"{view}.{claim}_status", lambda row, v=view, c=claim: row[v][f"{c}_status"])
    add("cross_view", lambda row: [row["cross_view"][claim] for claim in CLAIMS])
    for claim in CLAIMS:
        add(f"cross_view.{claim}", lambda row, c=claim: row["cross_view"][c])
    add("extra_claim_present", lambda row: [row[view]["extra_claim_present"] for view in VIEWS])
    add("extra_claim_endpoint", lambda row: [
        "supported" if _view_supported(row[view]) else "not_complete_supported" for view in VIEWS])
    add("scope_flags_exact", lambda row: [sorted(row[view]["scope_flags"]) for view in VIEWS])
    add("reviewable", lambda row: row["reviewable"])
    add("needs_adjudication", lambda row: row["needs_adjudication"])
    add("complete_supported_view", lambda row: [_view_supported(row[view]) for view in VIEWS])
    add("complete_supported_pair", _pair_supported)
    return dimensions


def _build_queue(responses_a: Mapping[str, Mapping[str, Any]],
                 responses_b: Mapping[str, Mapping[str, Any]], *, partition: str,
                 response_a_sha256: str, response_b_sha256: str):
    queue: list[dict[str, Any]] = []
    for item_id in sorted(responses_a):
        row_a, row_b = responses_a[item_id], responses_b[item_id]
        paths, reasons = _resolution_paths(row_a, row_b)
        if not paths and not reasons:
            continue
        disputed = {path: {"rater_A": deepcopy(_get_path(row_a, path)),
                           "rater_B": deepcopy(_get_path(row_b, path))}
                    for path in sorted(paths)}
        queue.append({
            "schema_version": SCHEMA_VERSION, "partition": partition, "item_id": item_id,
            "rater_A_response_sha256": response_a_sha256,
            "rater_B_response_sha256": response_b_sha256,
            "queue_reasons": sorted(reasons), "disputed_fields": disputed,
            "adjudicated_values": None, "reason": None, "adjudicator_id": None,
            "adjudicated_at": None,
        })
    return queue


def _prepare_context(*, partition: str, packet_a_path: Path, packet_b_path: Path,
                     response_a_path: Path, response_b_path: Path,
                     declaration_a_path: Path, declaration_b_path: Path,
                     manifest_path: Path, response_schema_path: Path, rubric_path: Path,
                     lock_schema_path: Path, created_at: str):
    if partition not in {"development", "test"}:
        raise AnnotationProcessingError("Partition must be development or test")
    paths = {
        "packet_a": packet_a_path, "packet_b": packet_b_path,
        "response_a": response_a_path, "response_b": response_b_path,
        "declaration_a": declaration_a_path, "declaration_b": declaration_b_path,
        "manifest": manifest_path, "response_schema": response_schema_path,
        "rubric": rubric_path, "lock_schema": lock_schema_path,
    }
    inputs = {name: _input_record(path) for name, path in paths.items()}
    if inputs["response_a"]["path"] == inputs["response_b"]["path"]:
        raise AnnotationProcessingError("Rater response paths must be distinct")
    if inputs["declaration_a"]["path"] == inputs["declaration_b"]["path"]:
        raise AnnotationProcessingError("Rater declaration paths must be distinct")
    response_schema = _read_json(response_schema_path, label="response schema")
    lock_schema = _read_json(lock_schema_path, label="annotation lock schema")
    if not isinstance(response_schema, dict) or not isinstance(lock_schema, dict):
        raise AnnotationProcessingError("Response and lock schemas must be objects")
    try:
        Draft202012Validator.check_schema(response_schema)
        Draft202012Validator.check_schema(lock_schema)
    except Exception as error:
        raise AnnotationProcessingError(f"Frozen JSON Schema is invalid: {error}") from error
    rubric = _read_json(rubric_path, label="rubric")
    if not isinstance(rubric, dict) or rubric.get("claim_ids") != list(CLAIMS):
        raise AnnotationProcessingError("Frozen rubric claim IDs do not match C1-C4")
    manifest = _validate_manifest(
        manifest_path, partition=partition, packet_a_path=packet_a_path,
        packet_b_path=packet_b_path, response_schema_path=response_schema_path,
        rubric_path=rubric_path, lock_schema_path=lock_schema_path)
    packet_a, packet_b, packet_id_a, packet_id_b = _validate_packets(
        packet_a_path, packet_b_path, partition=partition,
        expected_count=manifest["blinded_unique_item_count"])
    responses_a, rater_a_id = _response_index(
        response_a_path, label="rater A responses", packet=packet_a,
        expected_packet_id=packet_id_a, schema=response_schema)
    responses_b, rater_b_id = _response_index(
        response_b_path, label="rater B responses", packet=packet_b,
        expected_packet_id=packet_id_b, schema=response_schema)
    if rater_a_id == rater_b_id:
        raise AnnotationProcessingError("Two distinct real rater IDs are required")
    if inputs["response_a"]["sha256"] == inputs["response_b"]["sha256"]:
        raise AnnotationProcessingError("The two original response files must be distinct")
    declaration_a = _parse_declaration(
        declaration_a_path, expected_rater_id=rater_a_id, label="rater A declaration")
    declaration_b = _parse_declaration(
        declaration_b_path, expected_rater_id=rater_b_id, label="rater B declaration")
    if inputs["declaration_a"]["sha256"] == inputs["declaration_b"]["sha256"]:
        raise AnnotationProcessingError("The two signed declarations must be distinct")
    dimensions = _agreement_dimensions(responses_a, responses_b)
    queue = _build_queue(
        responses_a, responses_b, partition=partition,
        response_a_sha256=inputs["response_a"]["sha256"],
        response_b_sha256=inputs["response_b"]["sha256"])
    actual_disagreements = sum(
        any(_comparison_value(responses_a[item_id], path) !=
            _comparison_value(responses_b[item_id], path) for path in RATING_PATHS)
        for item_id in responses_a)
    agreement = {
        "schema_version": SCHEMA_VERSION, "status": "pre_adjudication_recorded",
        "partition": partition, "recorded_at": created_at, "rater_count": 2,
        "items_assigned": len(packet_a), "items_completed_by_both": len(responses_a),
        "raw_claim_agreement": dimensions["claim_status"]["agreement"],
        "claim_status_cohen_kappa": dimensions["claim_status"]["cohen_kappa"],
        "raw_complete_view_agreement": dimensions["complete_supported_view"]["agreement"],
        "complete_view_cohen_kappa": dimensions["complete_supported_view"]["cohen_kappa"],
        "raw_complete_pair_agreement": dimensions["complete_supported_pair"]["agreement"],
        "complete_pair_cohen_kappa": dimensions["complete_supported_pair"]["cohen_kappa"],
        "disagreement_count": len(queue), "rating_disagreement_count": actual_disagreements,
        "adjudication_method": "pending separate completed adjudication record",
        "adjudicated_count": 0,
        "style_based_unblinding_disclosures": [
            {"rater": "A", "disclosure": declaration_a["style_disclosure"]},
            {"rater": "B", "disclosure": declaration_b["style_disclosure"]}],
        "dimensions": dimensions,
        "response_sha256": {"rater_A": inputs["response_a"]["sha256"],
                            "rater_B": inputs["response_b"]["sha256"]},
        "notes": ("Pre-adjudication values come from the two original response files. "
                  "Kappa is null when expected agreement is one."),
    }
    return {
        "inputs": inputs, "manifest": manifest, "response_schema": response_schema,
        "lock_schema": lock_schema, "packet_a": packet_a, "packet_b": packet_b,
        "responses_a": responses_a, "responses_b": responses_b,
        "rater_a_id": rater_a_id, "rater_b_id": rater_b_id,
        "declaration_a": declaration_a, "declaration_b": declaration_b,
        "agreement": agreement, "queue": queue,
    }


def prepare_annotations(*, partition: str, packet_a_path: Path, packet_b_path: Path,
                        response_a_path: Path, response_b_path: Path,
                        declaration_a_path: Path, declaration_b_path: Path,
                        output_dir: Path, manifest_path: Path | None = None,
                        response_schema_path: Path | None = None,
                        rubric_path: Path | None = None,
                        lock_schema_path: Path | None = None) -> dict[str, Any]:
    """Validate two response sets and create blinded pre-adjudication artifacts."""
    output_dir = output_dir.resolve()
    _validate_private_output(output_dir)
    manifest_path = (manifest_path or ANNOTATION_ROOT / f"PACKET_MANIFEST-{partition}.json").resolve()
    response_schema_path = (response_schema_path or ANNOTATION_ROOT / "RESPONSE_SCHEMA.json").resolve()
    rubric_path = (rubric_path or ANNOTATION_ROOT / "RUBRIC.json").resolve()
    lock_schema_path = (lock_schema_path or ANNOTATION_ROOT / "ANNOTATION_LOCK_SCHEMA.json").resolve()
    created_at = _utc_now()
    context = _prepare_context(
        partition=partition, packet_a_path=packet_a_path.resolve(),
        packet_b_path=packet_b_path.resolve(), response_a_path=response_a_path.resolve(),
        response_b_path=response_b_path.resolve(), declaration_a_path=declaration_a_path.resolve(),
        declaration_b_path=declaration_b_path.resolve(), manifest_path=manifest_path,
        response_schema_path=response_schema_path, rubric_path=rubric_path,
        lock_schema_path=lock_schema_path, created_at=created_at)
    agreement_bytes, queue_bytes = _json_bytes(context["agreement"]), _jsonl_bytes(context["queue"])
    common = packet_a_path.resolve().parent if packet_a_path.resolve().parent == packet_b_path.resolve().parent else None
    record = {
        "schema_version": SCHEMA_VERSION, "status": "prepared_pre_adjudication",
        "partition": partition, "created_at": created_at,
        "rater_A_id": context["rater_a_id"], "rater_B_id": context["rater_b_id"],
        "items_assigned": len(context["packet_a"]), "inputs": context["inputs"],
        "agreement_report": {"file": AGREEMENT_REPORT_NAME,
                             "sha256": _sha256_bytes(agreement_bytes)},
        "adjudication_queue": {"file": ADJUDICATION_QUEUE_NAME,
                               "sha256": _sha256_bytes(queue_bytes),
                               "item_count": len(context["queue"])},
        "suggested_sealed_mapping": str((common / "sealed_mapping.json").resolve()) if common else None,
    }
    targets = [output_dir / PREPARE_RECORD_NAME, output_dir / AGREEMENT_REPORT_NAME,
               output_dir / ADJUDICATION_QUEUE_NAME]
    existing = [str(path) for path in targets if path.exists() or path.is_symlink()]
    if existing:
        raise AnnotationProcessingError("Refusing to overwrite preparation artifacts: " + ", ".join(existing))
    _write_new(output_dir / AGREEMENT_REPORT_NAME, agreement_bytes)
    _write_new(output_dir / ADJUDICATION_QUEUE_NAME, queue_bytes)
    _write_new(output_dir / PREPARE_RECORD_NAME, _json_bytes(record))
    return record


def _load_prepare_record(prepared_dir: Path) -> dict[str, Any]:
    record = _read_json(prepared_dir / PREPARE_RECORD_NAME, label="prepare record")
    required = {
        "schema_version", "status", "partition", "created_at", "rater_A_id", "rater_B_id",
        "items_assigned", "inputs", "agreement_report", "adjudication_queue",
        "suggested_sealed_mapping",
    }
    if not isinstance(record, dict) or set(record) != required:
        raise AnnotationProcessingError("Prepare record fields differ from the processor contract")
    if record.get("schema_version") != SCHEMA_VERSION or record.get("status") != "prepared_pre_adjudication":
        raise AnnotationProcessingError("Prepare record has an invalid version or status")
    _validate_timestamp(record.get("created_at"), label="prepare record created_at")
    if record.get("partition") not in {"development", "test"}:
        raise AnnotationProcessingError("Prepare record partition is invalid")
    expected_inputs = {
        "packet_a", "packet_b", "response_a", "response_b", "declaration_a", "declaration_b",
        "manifest", "response_schema", "rubric", "lock_schema",
    }
    inputs = record.get("inputs")
    if not isinstance(inputs, dict) or set(inputs) != expected_inputs:
        raise AnnotationProcessingError("Prepare record input bindings are incomplete")
    for name, binding in inputs.items():
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
            raise AnnotationProcessingError(f"Prepare record input binding is malformed: {name}")
        _validate_digest(binding.get("sha256"), label=f"prepare.inputs.{name}.sha256")
        path = Path(binding.get("path", ""))
        if not path.is_absolute() or not path.is_file():
            raise AnnotationProcessingError(f"Prepared input no longer exists: {name}")
        if _sha256_file(path) != binding["sha256"]:
            raise AnnotationProcessingError(f"Prepared input changed after agreement: {name}")
    return record


def _revalidate_preparation(prepared_dir: Path, record: Mapping[str, Any]):
    inputs = record["inputs"]
    context = _prepare_context(
        partition=record["partition"], packet_a_path=Path(inputs["packet_a"]["path"]),
        packet_b_path=Path(inputs["packet_b"]["path"]),
        response_a_path=Path(inputs["response_a"]["path"]),
        response_b_path=Path(inputs["response_b"]["path"]),
        declaration_a_path=Path(inputs["declaration_a"]["path"]),
        declaration_b_path=Path(inputs["declaration_b"]["path"]),
        manifest_path=Path(inputs["manifest"]["path"]),
        response_schema_path=Path(inputs["response_schema"]["path"]),
        rubric_path=Path(inputs["rubric"]["path"]),
        lock_schema_path=Path(inputs["lock_schema"]["path"]),
        created_at=record["created_at"])
    if context["rater_a_id"] != record["rater_A_id"] or context["rater_b_id"] != record["rater_B_id"]:
        raise AnnotationProcessingError("Prepared rater identity binding changed")
    if len(context["packet_a"]) != record["items_assigned"]:
        raise AnnotationProcessingError("Prepared item count changed")
    for binding, expected_file, payload, label in (
        (record["agreement_report"], AGREEMENT_REPORT_NAME, _json_bytes(context["agreement"]),
         "agreement report"),
        (record["adjudication_queue"], ADJUDICATION_QUEUE_NAME, _jsonl_bytes(context["queue"]),
         "adjudication queue"),
    ):
        if not isinstance(binding, dict) or binding.get("file") != expected_file:
            raise AnnotationProcessingError(f"Prepare record {label} binding is malformed")
        _validate_digest(binding.get("sha256"), label=f"prepare.{label}.sha256")
        artifact = prepared_dir / expected_file
        if not artifact.is_file() or _sha256_file(artifact) != binding["sha256"]:
            raise AnnotationProcessingError(f"Prepared {label} is missing or changed")
        if _sha256_bytes(payload) != binding["sha256"]:
            raise AnnotationProcessingError(f"Prepared {label} cannot be reproduced")
    if record["adjudication_queue"].get("item_count") != len(context["queue"]):
        raise AnnotationProcessingError("Prepared adjudication queue count is inconsistent")
    return context


ADJUDICATION_KEYS = {
    "schema_version", "partition", "item_id", "rater_A_response_sha256",
    "rater_B_response_sha256", "queue_reasons", "disputed_fields",
    "adjudicated_values", "reason", "adjudicator_id", "adjudicated_at",
}


def _consume_adjudication(context: Mapping[str, Any], *, adjudication_path: Path | None):
    expected = {row["item_id"]: row for row in context["queue"]}
    if expected and adjudication_path is None:
        raise AnnotationProcessingError(
            f"{len(expected)} queued item(s) require a completed adjudication JSONL")
    if adjudication_path is None:
        rows: list[dict[str, Any]] = []
        raw = b""
    else:
        if not adjudication_path.is_file():
            raise AnnotationProcessingError(f"Completed adjudication does not exist: {adjudication_path}")
        raw = adjudication_path.read_bytes()
        rows = _read_jsonl(adjudication_path, label="completed adjudication",
                           allow_empty=not expected)
    indexed: dict[str, dict[str, Any]] = {}
    for number, row in enumerate(rows, 1):
        label = f"completed adjudication line {number}"
        if set(row) != ADJUDICATION_KEYS:
            raise AnnotationProcessingError(f"{label}: fields differ from the queue contract")
        _assert_no_fill(row, label=label)
        item_id = row.get("item_id")
        if not isinstance(item_id, str) or item_id in indexed:
            raise AnnotationProcessingError(f"{label}: missing or duplicate item ID")
        if item_id not in expected:
            raise AnnotationProcessingError(f"{label}: item was not queued")
        template = expected[item_id]
        bound = ("schema_version", "partition", "item_id", "rater_A_response_sha256",
                 "rater_B_response_sha256", "queue_reasons", "disputed_fields")
        if any(row.get(field) != template.get(field) for field in bound):
            raise AnnotationProcessingError(f"{label}: original queue bindings changed")
        values = row.get("adjudicated_values")
        if not isinstance(values, dict) or set(values) != set(template["disputed_fields"]):
            raise AnnotationProcessingError(
                f"{label}: resolve every queued field exactly once")
        if any(value is None for value in values.values()):
            raise AnnotationProcessingError(f"{label}: adjudicated values cannot be null")
        if not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise AnnotationProcessingError(f"{label}: a human reason is required")
        if not isinstance(row.get("adjudicator_id"), str) or not row["adjudicator_id"].strip():
            raise AnnotationProcessingError(f"{label}: an adjudicator ID is required")
        _validate_timestamp(row.get("adjudicated_at"), label=f"{label}.adjudicated_at")
        indexed[item_id] = row
    if set(indexed) != set(expected):
        raise AnnotationProcessingError(
            f"Completed adjudication is incomplete ({len(indexed)}/{len(expected)})")

    consensus: dict[str, dict[str, Any]] = {}
    for item_id in sorted(context["responses_a"]):
        value = deepcopy(context["responses_a"][item_id])
        if item_id in indexed:
            for path, adjudicated in indexed[item_id]["adjudicated_values"].items():
                _set_path(value, path, adjudicated)
        for view in VIEWS:
            value[view]["scope_flags"] = sorted(value[view]["scope_flags"])
            value[view]["extra_claims"] = sorted(
                value[view]["extra_claims"], key=_canonical_json)
        _validate_schema(value, context["response_schema"], label=f"consensus {item_id}")
        _semantic_response_checks(value, label=f"consensus {item_id}")
        if _has_unresolved(value):
            raise AnnotationProcessingError(
                f"Consensus {item_id} remains unreviewable or unresolved; no label can be invented")
        if value["needs_adjudication"] != "no":
            raise AnnotationProcessingError(f"Consensus {item_id} still requests adjudication")
        for view_name in VIEWS:
            if _view_supported(value[view_name]) and value[view_name]["scope_flags"]:
                raise AnnotationProcessingError(
                    f"Consensus {item_id}/{view_name} passes with a contradictory scope flag")
        if all(_view_supported(value[view]) for view in VIEWS):
            changed = [claim for claim in CLAIMS
                       if value["cross_view"][claim] != "preserved"]
            if changed:
                raise AnnotationProcessingError(
                    f"Consensus {item_id} has passing views but changed cross-view claims: {changed}")
        consensus[item_id] = value
    return consensus, raw, set(indexed)


def _blind_source(source_id: str, seed: int) -> str:
    digest = hashlib.sha256(f"{seed}:source:{source_id}".encode()).hexdigest()[:16]
    return "S-" + digest


def _validate_sealed_mapping(mapping_path: Path, *, context: Mapping[str, Any],
                             partition: str) -> dict[str, Any]:
    expected_hash = context["manifest"]["private_outputs"]["sealed_mapping_json_sha256"]
    if _sha256_file(mapping_path) != expected_hash:
        raise AnnotationProcessingError("Sealed mapping hash mismatch")
    mapping = _read_json(mapping_path, label="sealed mapping")
    expected_top = {"schema_version", "partition", "seed", "status", "items", "nonreviewable"}
    if not isinstance(mapping, dict) or set(mapping) != expected_top:
        raise AnnotationProcessingError("Sealed mapping fields differ from builder contract")
    if mapping.get("schema_version") != SCHEMA_VERSION or mapping.get("partition") != partition:
        raise AnnotationProcessingError("Sealed mapping version or partition mismatch")
    if mapping.get("status") != "sealed_private_mapping_not_rater_material":
        raise AnnotationProcessingError("Sealed mapping status is invalid")
    seed, items = mapping.get("seed"), mapping.get("items")
    if not isinstance(seed, int) or isinstance(seed, bool) or not isinstance(items, dict):
        raise AnnotationProcessingError("Sealed mapping seed/items are malformed")
    if set(items) != set(context["packet_a"]):
        raise AnnotationProcessingError("Sealed mapping does not exactly cover packet items")
    natural_keys: set[tuple[str, str, str]] = set()
    logical_ids: set[str] = set()
    controlled_keys: set[tuple[str, str]] = set()
    for item_id, sealed in items.items():
        if not isinstance(sealed, dict):
            raise AnnotationProcessingError(f"Sealed item {item_id} must be an object")
        digest, source_id = sealed.get("content_sha256"), sealed.get("source_id")
        if not isinstance(digest, str) or not HEX64_RE.fullmatch(digest) \
                or digest[:16] != item_id[2:]:
            raise AnnotationProcessingError(f"Sealed item {item_id} has invalid content binding")
        if not isinstance(source_id, str) or not source_id:
            raise AnnotationProcessingError(f"Sealed item {item_id} lacks source ID")
        if context["packet_a"][item_id]["source_blind_id"] != _blind_source(source_id, seed):
            raise AnnotationProcessingError(f"Sealed source binding mismatch for {item_id}")
        audience = sealed.get("audience_map")
        if not isinstance(audience, dict) or set(audience) != set(VIEWS) \
                or set(audience.values()) != {"novice", "expert"}:
            raise AnnotationProcessingError(f"Sealed item {item_id} has invalid audience map")
        if sealed.get("item_type") == "natural_output":
            expected = {"item_type", "source_id", "audience_map", "logical_roles", "content_sha256"}
            if set(sealed) != expected or not isinstance(sealed.get("logical_roles"), list) \
                    or not sealed["logical_roles"]:
                raise AnnotationProcessingError(f"Natural sealed item {item_id} is malformed")
            for role in sealed["logical_roles"]:
                fields = {"logical_id", "condition", "stage", "output_status"}
                if not isinstance(role, dict) or set(role) != fields \
                        or not all(isinstance(role[key], str) and role[key] for key in fields):
                    raise AnnotationProcessingError(f"Natural role for {item_id} is malformed")
                key = (source_id, role["condition"], role["stage"])
                if role["logical_id"] in logical_ids or key in natural_keys:
                    raise AnnotationProcessingError(f"Duplicate natural label key for {item_id}")
                logical_ids.add(role["logical_id"])
                natural_keys.add(key)
        elif sealed.get("item_type") == "controlled_variant":
            expected = {"item_type", "source_id", "audience_map", "variant_id",
                        "construction_intent", "mutation_type", "content_sha256"}
            if set(sealed) != expected or sealed.get("construction_intent") not in {"supported", "faulty"} \
                    or not isinstance(sealed.get("variant_id"), str) or not sealed["variant_id"]:
                raise AnnotationProcessingError(f"Controlled sealed item {item_id} is malformed")
            key = (source_id, sealed["variant_id"])
            if key in controlled_keys:
                raise AnnotationProcessingError(f"Duplicate controlled label key for {item_id}")
            controlled_keys.add(key)
        else:
            raise AnnotationProcessingError(f"Unknown sealed item type for {item_id}")
    if len(controlled_keys) != context["manifest"].get("controlled_variants_instantiated"):
        raise AnnotationProcessingError("Sealed controlled count differs from manifest")
    if not isinstance(mapping.get("nonreviewable"), list) or \
            len(mapping["nonreviewable"]) != context["manifest"].get("nonreviewable_slot_count"):
        raise AnnotationProcessingError("Sealed nonreviewable count differs from manifest")
    mechanical_roles = 0
    for row in mapping["nonreviewable"]:
        if not isinstance(row, dict):
            raise AnnotationProcessingError("Malformed sealed nonreviewable record")
        if row.get("item_type") == "mechanical_natural_output":
            roles = row.get("logical_roles")
            if not isinstance(roles, list) or not roles:
                raise AnnotationProcessingError("Mechanical natural record lacks logical roles")
            mechanical_roles += len(roles)
    reviewable_natural_items = sum(
        row.get("item_type") == "natural_output" for row in items.values())
    deduplicated_rows = len(natural_keys) + mechanical_roles - reviewable_natural_items
    if deduplicated_rows != context["manifest"].get("deduplicated_natural_logical_rows"):
        raise AnnotationProcessingError("Sealed natural deduplication count differs from manifest")
    return mapping


def _build_labels(*, mapping: Mapping[str, Any], consensus: Mapping[str, Mapping[str, Any]],
                  adjudicated_items: set[str], lock_sha256: str, partition: str):
    natural: list[dict[str, Any]] = []
    controlled: list[dict[str, Any]] = []
    for item_id in sorted(mapping["items"]):
        sealed = mapping["items"][item_id]
        pair_supported = _pair_supported(consensus[item_id])
        status = ("independent_adjudicated" if item_id in adjudicated_items
                  else "independent_consensus")
        provenance = {
            "schema_version": SCHEMA_VERSION, "partition": partition, "item_id": item_id,
            "annotation_status": status, "independent_rater_count": 2,
            "annotation_lock_sha256": lock_sha256,
        }
        if sealed["item_type"] == "natural_output":
            for role in sealed["logical_roles"]:
                natural.append({
                    **provenance, "logical_id": role["logical_id"],
                    "source_id": sealed["source_id"], "condition": role["condition"],
                    "stage": role["stage"], "pair_supported": pair_supported,
                })
        else:
            # Construction intent is not consulted: truth describes realized,
            # independently resolved semantics of the instantiated text.
            controlled.append({
                **provenance, "source_id": sealed["source_id"],
                "variant_id": sealed["variant_id"],
                "truth": "supported" if pair_supported else "faulty",
            })
    natural.sort(key=lambda row: (row["source_id"], row["condition"], row["stage"],
                                  row["logical_id"]))
    controlled.sort(key=lambda row: (row["source_id"], row["variant_id"]))
    if len({(row["source_id"], row["condition"], row["stage"]) for row in natural}) != len(natural):
        raise AnnotationProcessingError("Natural labels contain duplicate analyzer keys")
    if len({(row["source_id"], row["variant_id"]) for row in controlled}) != len(controlled):
        raise AnnotationProcessingError("Controlled labels contain duplicate analyzer keys")
    return natural, controlled


def lock_annotations(*, prepared_dir: Path, output_dir: Path, custodian: str,
                     sealed_mapping_path: Path | None = None,
                     adjudication_path: Path | None = None,
                     notes: str = "") -> dict[str, Any]:
    """Lock unchanged responses, then unblind and emit consensus labels."""
    prepared_dir, output_dir = prepared_dir.resolve(), output_dir.resolve()
    _validate_private_output(output_dir)
    if not custodian.strip():
        raise AnnotationProcessingError("A non-empty custodian identifier is required")
    record = _load_prepare_record(prepared_dir)
    context = _revalidate_preparation(prepared_dir, record)
    if sealed_mapping_path is None:
        suggested = record.get("suggested_sealed_mapping")
        if not suggested:
            raise AnnotationProcessingError("Pass --sealed-mapping; no prepared path exists")
        sealed_mapping_path = Path(suggested)
    sealed_mapping_path = sealed_mapping_path.resolve()
    if adjudication_path is not None:
        adjudication_path = adjudication_path.resolve()
        if adjudication_path == (prepared_dir / ADJUDICATION_QUEUE_NAME).resolve():
            raise AnnotationProcessingError(
                "Do not overwrite the original queue; use a separate completed file")
    consensus, adjudication_bytes, adjudicated_items = _consume_adjudication(
        context, adjudication_path=adjudication_path)

    final_paths = [output_dir / name for name in (
        LOCK_NAME, NATURAL_LABELS_NAME, CONTROLLED_LABELS_NAME, PROVENANCE_NAME,
        ADJUDICATION_RECORD_NAME)]
    locked_inputs = output_dir / "locked_inputs"
    if locked_inputs.exists() or locked_inputs.is_symlink():
        raise AnnotationProcessingError(f"Refusing to reuse locked input directory: {locked_inputs}")
    existing = [str(path) for path in final_paths if path.exists() or path.is_symlink()]
    if existing:
        raise AnnotationProcessingError("Refusing to overwrite lock artifacts: " + ", ".join(existing))

    operation_at = _utc_now()
    lock = {
        "schema_version": SCHEMA_VERSION, "status": "locked",
        "partition": record["partition"], "rater_count": 2,
        "rater_A_id": context["rater_a_id"], "rater_B_id": context["rater_b_id"],
        "raters_distinct": True, "rater_A_independence_confirmed": True,
        "rater_B_independence_confirmed": True,
        "rubric_sha256": context["inputs"]["rubric"]["sha256"],
        "packet_manifest_sha256": context["inputs"]["manifest"]["sha256"],
        "rater_A_response_sha256": context["inputs"]["response_a"]["sha256"],
        "rater_B_response_sha256": context["inputs"]["response_b"]["sha256"],
        "rater_A_declaration_sha256": context["inputs"]["declaration_a"]["sha256"],
        "rater_B_declaration_sha256": context["inputs"]["declaration_b"]["sha256"],
        "response_schema_validation_passed": True,
        "pre_adjudication_agreement_recorded": True,
        "independent_annotation_ready": True, "locked_at": operation_at,
        "custodian": custodian.strip(), "unblinded_at": operation_at,
        "notes": (
            "The processor persisted this response lock before reading the sealed mapping. "
            "Original responses and declarations remain separate and hash-bound."
            + (f" {notes.strip()}" if notes.strip() else "")),
    }
    if lock["rater_A_id"] == lock["rater_B_id"]:
        raise AnnotationProcessingError("Annotation lock cannot contain the same rater twice")
    _validate_schema(lock, context["lock_schema"], label="annotation lock")
    lock_bytes = _json_bytes(lock)
    lock_sha256 = _sha256_bytes(lock_bytes)

    # The workflow boundary: the immutable response lock is on disk before
    # the processor opens or parses the sealed mapping.
    _write_new(output_dir / LOCK_NAME, lock_bytes, mode=0o400)
    mapping = _validate_sealed_mapping(
        sealed_mapping_path, context=context, partition=record["partition"])
    natural, controlled = _build_labels(
        mapping=mapping, consensus=consensus, adjudicated_items=adjudicated_items,
        lock_sha256=lock_sha256, partition=record["partition"])
    natural_bytes, controlled_bytes = _jsonl_bytes(natural), _jsonl_bytes(controlled)
    provenance = {
        "schema_version": SCHEMA_VERSION, "status": "locked_consensus_labels",
        "partition": record["partition"], "annotation_lock_sha256": lock_sha256,
        "agreement_report_sha256": record["agreement_report"]["sha256"],
        "adjudication_queue_sha256": record["adjudication_queue"]["sha256"],
        "adjudication_record_sha256": _sha256_bytes(adjudication_bytes),
        "sealed_mapping_sha256": _sha256_file(sealed_mapping_path),
        "natural_labels_sha256": _sha256_bytes(natural_bytes),
        "controlled_labels_sha256": _sha256_bytes(controlled_bytes),
        "reviewed_item_count": len(consensus),
        "adjudicated_item_count": len(adjudicated_items),
        "natural_logical_label_count": len(natural),
        "controlled_variant_label_count": len(controlled),
        "nonreviewable_label_count": 0,
    }
    _write_new(output_dir / NATURAL_LABELS_NAME, natural_bytes, mode=0o400)
    _write_new(output_dir / CONTROLLED_LABELS_NAME, controlled_bytes, mode=0o400)
    _write_new(output_dir / ADJUDICATION_RECORD_NAME, adjudication_bytes, mode=0o400)
    _write_new(output_dir / PROVENANCE_NAME, _json_bytes(provenance), mode=0o400)
    locked_inputs.mkdir(mode=0o700)
    copies = {
        "rater_A_responses.jsonl": Path(context["inputs"]["response_a"]["path"]),
        "rater_B_responses.jsonl": Path(context["inputs"]["response_b"]["path"]),
        "rater_A_declaration.md": Path(context["inputs"]["declaration_a"]["path"]),
        "rater_B_declaration.md": Path(context["inputs"]["declaration_b"]["path"]),
        "PRE_ADJUDICATION_AGREEMENT.json": prepared_dir / AGREEMENT_REPORT_NAME,
    }
    for name, source in copies.items():
        _write_new(locked_inputs / name, source.read_bytes(), mode=0o400)
    return provenance


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare", help="validate responses and build queue")
    prepare.add_argument("--partition", required=True, choices=("development", "test"))
    for flag in ("packet-a", "packet-b", "responses-a", "responses-b",
                 "declaration-a", "declaration-b", "output-dir"):
        prepare.add_argument(f"--{flag}", type=Path, required=True)
    prepare.add_argument("--manifest", type=Path)
    prepare.add_argument("--response-schema", type=Path,
                         default=ANNOTATION_ROOT / "RESPONSE_SCHEMA.json")
    prepare.add_argument("--rubric", type=Path, default=ANNOTATION_ROOT / "RUBRIC.json")
    prepare.add_argument("--lock-schema", type=Path,
                         default=ANNOTATION_ROOT / "ANNOTATION_LOCK_SCHEMA.json")
    lock = subparsers.add_parser("lock", help="lock responses and emit consensus labels")
    lock.add_argument("--prepared-dir", type=Path, required=True)
    lock.add_argument("--output-dir", type=Path,
                      help="defaults to --prepared-dir; must be outside Git")
    lock.add_argument("--sealed-mapping", type=Path)
    lock.add_argument("--adjudication", type=Path,
                      help="completed copy of the queue; omit only for an empty queue")
    lock.add_argument("--custodian", required=True)
    lock.add_argument("--notes", default="")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            record = prepare_annotations(
                partition=args.partition, packet_a_path=args.packet_a,
                packet_b_path=args.packet_b, response_a_path=args.responses_a,
                response_b_path=args.responses_b, declaration_a_path=args.declaration_a,
                declaration_b_path=args.declaration_b, output_dir=args.output_dir,
                manifest_path=(args.manifest or
                               ANNOTATION_ROOT / f"PACKET_MANIFEST-{args.partition}.json"),
                response_schema_path=args.response_schema, rubric_path=args.rubric,
                lock_schema_path=args.lock_schema)
            result = {
                "status": record["status"], "partition": record["partition"],
                "items_assigned": record["items_assigned"],
                "queued_for_adjudication": record["adjudication_queue"]["item_count"],
                "output_dir": str(args.output_dir.resolve()),
            }
        else:
            output_dir = args.output_dir or args.prepared_dir
            provenance = lock_annotations(
                prepared_dir=args.prepared_dir, output_dir=output_dir,
                custodian=args.custodian, sealed_mapping_path=args.sealed_mapping,
                adjudication_path=args.adjudication, notes=args.notes)
            result = {
                "status": provenance["status"], "partition": provenance["partition"],
                "natural_labels": provenance["natural_logical_label_count"],
                "controlled_labels": provenance["controlled_variant_label_count"],
                "output_dir": str(output_dir.resolve()),
            }
    except AnnotationProcessingError as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
