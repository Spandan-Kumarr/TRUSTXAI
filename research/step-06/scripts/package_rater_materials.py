#!/usr/bin/env python3
"""Create separate, private Step-6 annotation distributions for two raters.

The archives contain raw research cases and generated text.  They must remain
outside Git.  Only a counts-and-digests manifest is written to the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
import zipfile


REPO = Path(__file__).resolve().parents[3]
ANNOTATION = REPO / "research/step-06/annotation"
RATERS = ("A", "B")
PARTITIONS = ("development", "test")
PACKET_KEYS = {
    "schema_version", "partition", "packet_id", "item_id", "source_blind_id",
    "evidence", "view_1", "view_2",
}
FORBIDDEN_KEYS = {
    "source_id", "logical_id", "condition", "stage", "construction_intent",
    "mutation_type", "variant_id", "gold", "gold_label", "correct_option",
    "answer", "answer_idx", "prediction", "checker", "automated_score",
    "sealed_mapping", "audience_map",
}
MATERIALS = {
    "README_FIRST.md": ANNOTATION / "RATER_INSTRUCTIONS.md",
    "ANNOTATION_PROTOCOL.md": ANNOTATION / "ANNOTATION_PROTOCOL.md",
    "RUBRIC.json": ANNOTATION / "RUBRIC.json",
    "RESPONSE_SCHEMA.json": ANNOTATION / "RESPONSE_SCHEMA.json",
    "TRAINING_EXAMPLES.json": ANNOTATION / "TRAINING_EXAMPLES.json",
    "ANNOTATOR_DECLARATION.md": ANNOTATION / "templates/ANNOTATOR_DECLARATION.md",
    "RESPONSE_FORM.csv": ANNOTATION / "forms/NATURAL_PAIR_FORM.csv",
}
FORM_TEMPLATE = ANNOTATION / "RATER_FORM_TEMPLATE.html"


class PackageError(RuntimeError):
    pass


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise PackageError(f"Missing private rater packet: {path}")
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                value = json.loads(line)
            except ValueError as error:
                raise PackageError(f"Invalid JSON at {path}:{line_number}") from error
            if not isinstance(value, dict):
                raise PackageError(f"Packet row is not an object at {path}:{line_number}")
            rows.append(value)
    if not rows:
        raise PackageError(f"Empty rater packet: {path}")
    return rows


def forbidden_locations(value: object, location: str = "$") -> list[str]:
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).casefold() in FORBIDDEN_KEYS:
                found.append(f"{location}.{key}")
            found.extend(forbidden_locations(child, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(forbidden_locations(child, f"{location}[{index}]"))
    return found


def validate_packet(rows: list[dict], partition: str, rater: str) -> None:
    expected_packet = f"{partition}-rater-{rater}-v1"
    ids = []
    for index, row in enumerate(rows):
        if set(row) != PACKET_KEYS:
            raise PackageError(f"Unexpected packet keys at {partition}/{rater}/{index}")
        if row.get("schema_version") != "1.0" or row.get("partition") != partition \
                or row.get("packet_id") != expected_packet:
            raise PackageError(f"Packet binding mismatch at {partition}/{rater}/{index}")
        if not isinstance(row.get("item_id"), str) \
                or re.fullmatch(r"I-[0-9a-f]{16}", row["item_id"]) is None:
            raise PackageError("Missing opaque item ID")
        if not isinstance(row.get("source_blind_id"), str) \
                or re.fullmatch(r"S-[0-9a-f]{16}", row["source_blind_id"]) is None:
            raise PackageError("Missing opaque source ID")
        leaks = forbidden_locations(row)
        if leaks:
            raise PackageError("Packet exposes sealed metadata: " + ", ".join(leaks[:3]))
        ids.append(row["item_id"])
    if len(set(ids)) != len(ids):
        raise PackageError(f"Duplicate item ID in {partition} rater {rater}")


def response_template(rows: list[dict], rater: str) -> bytes:
    """Return deliberately incomplete rows; `__FILL__` cannot pass the schema."""
    output = []
    for packet in rows:
        view = {
            "C1_status": "__FILL__", "C2_status": "__FILL__",
            "C3_status": "__FILL__", "C4_status": "__FILL__",
            "extra_claim_present": "__FILL__", "extra_claims": [],
            "scope_flags": [],
        }
        output.append({
            "schema_version": "1.0", "packet_id": packet["packet_id"],
            "item_id": packet["item_id"], "rater_id": f"R-{rater}-REPLACE_ME",
            "reviewable": "__FILL__", "view_1": dict(view), "view_2": dict(view),
            "cross_view": {claim: "__FILL__" for claim in ("C1", "C2", "C3", "C4")},
            "needs_adjudication": "__FILL__", "notes": "",
        })
    return b"".join(canonical(row) for row in output)


def offline_form(packets: dict[str, list[dict]], rater: str) -> bytes:
    """Build a self-contained form bound to one rater's two packets."""
    if not FORM_TEMPLATE.is_file():
        raise PackageError(f"Missing offline form template: {FORM_TEMPLATE}")
    payload = {
        "rater_slot": rater,
        "partitions": {partition: packets[partition] for partition in PARTITIONS},
    }
    embedded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    # Prevent experimental text from terminating the inline script block.
    embedded = (embedded.replace("<", "\\u003c").replace(">", "\\u003e")
                .replace("&", "\\u0026").replace("\u2028", "\\u2028")
                .replace("\u2029", "\\u2029"))
    template = FORM_TEMPLATE.read_text(encoding="utf-8")
    marker = "__ASSIGNMENT_JSON__"
    if template.count(marker) != 1:
        raise PackageError("Offline form template must contain exactly one assignment marker")
    return template.replace(marker, embedded).encode("utf-8")


def _zip_bytes(entries: dict[str, bytes]) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name in sorted(entries):
                if name.startswith("/") or ".." in Path(name).parts:
                    raise PackageError(f"Unsafe archive entry: {name}")
                info = zipfile.ZipInfo(name, date_time=(2026, 10, 29, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o600 << 16
                archive.writestr(info, entries[name])
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise PackageError("Archive integrity check failed")
        return temporary.read_bytes()
    finally:
        temporary.unlink(missing_ok=True)


def package(private_root: Path, output_root: Path, public_manifest: Path) -> dict:
    for path, role in ((private_root, "private input"), (output_root, "distribution output")):
        try:
            path.resolve().relative_to(REPO.resolve())
        except ValueError:
            pass
        else:
            raise PackageError(f"{role} must stay outside the Git repository")
    for name, path in MATERIALS.items():
        if not path.is_file():
            raise PackageError(f"Missing public rater material {name}: {path}")

    packets: dict[str, dict[str, tuple[Path, list[dict]]]] = {rater: {} for rater in RATERS}
    for partition in PARTITIONS:
        by_rater = {}
        for rater in RATERS:
            path = private_root / partition / f"rater_{rater}.jsonl"
            rows = read_jsonl(path)
            validate_packet(rows, partition, rater)
            packets[rater][partition] = (path, rows)
            by_rater[rater] = {row["item_id"] for row in rows}
        if by_rater["A"] != by_rater["B"]:
            raise PackageError(f"Rater item sets differ for {partition}")

    output_root.mkdir(parents=True, exist_ok=True)
    output_root.chmod(0o700)
    archive_records = {}
    for rater in RATERS:
        prefix = f"TRUSTXAI_RATER_{rater}"
        entries = {f"{prefix}/{name}": path.read_bytes() for name, path in MATERIALS.items()}
        form_packets = {partition: packets[rater][partition][1] for partition in PARTITIONS}
        entries[f"{prefix}/RATER_FORM.html"] = offline_form(form_packets, rater)
        counts, packet_hashes = {}, {}
        for partition in PARTITIONS:
            path, rows = packets[rater][partition]
            packet_name = f"{prefix}/packets/{partition}.jsonl"
            entries[packet_name] = path.read_bytes()
            entries[f"{prefix}/responses/{partition}_RESPONSES_TEMPLATE.jsonl"] = response_template(rows, rater)
            counts[partition] = len(rows)
            packet_hashes[partition] = sha256_file(path)
        package_manifest = {
            "schema": "trustxai.step6.rater-package.v1", "rater_slot": rater,
            "packet_counts": counts, "packet_sha256": packet_hashes,
            "contains_sealed_mapping": False, "contains_other_rater_packet": False,
            "contains_gold_or_condition_labels": False, "responses_present": False,
            "response_templates_are_incomplete": True,
            "offline_form_embeds_only_this_assignment": True,
            "offline_form_supports_private_resume_and_jsonl_export": True,
        }
        entries[f"{prefix}/PACKAGE_MANIFEST.json"] = canonical(package_manifest)
        data = _zip_bytes(entries)
        destination = output_root / f"TRUSTXAI_RATER_{rater}.zip"
        temporary = destination.with_suffix(".zip.tmp")
        temporary.write_bytes(data); temporary.chmod(0o600); temporary.replace(destination)
        archive_records[rater] = {
            "filename": destination.name, "bytes": destination.stat().st_size,
            "sha256": sha256_file(destination), "packet_counts": counts,
            "packet_sha256": packet_hashes, "archive_entries": len(entries),
        }

    manifest = {
        "schema": "trustxai.step6.rater-distribution.v1",
        "status": "private_packages_ready_not_annotated",
        "created_on": "2026-10-29", "archives": archive_records,
        "public_manifest_contains_raw_text": False,
        "private_archives_contain_research_text": True,
        "contains_rater_responses": False,
        "private_archives_outside_git": True,
        "separate_raters_required": True,
    }
    public_manifest.parent.mkdir(parents=True, exist_ok=True)
    public_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--public-manifest", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = arguments()
    value = package(args.private_root, args.output_root, args.public_manifest)
    print(json.dumps({"status": value["status"], "archives": value["archives"]}, sort_keys=True))


if __name__ == "__main__":
    main()
