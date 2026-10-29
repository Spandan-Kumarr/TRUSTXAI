import importlib.util
import json
from pathlib import Path
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/step-06/scripts/package_rater_materials.py"
SPEC = importlib.util.spec_from_file_location("step6_rater_packaging", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def packet(partition, rater, item="I-0123456789abcdef"):
    return {
        "schema_version": "1.0", "partition": partition,
        "packet_id": f"{partition}-rater-{rater}-v1", "item_id": item,
        "source_blind_id": "S-0123456789abcdef",
        "evidence": {"case_findings": [{"id": "S1", "text": "Private finding."}],
                     "C1": "a", "C2": "b", "C3": "c", "C4": "d"},
        "view_1": f"Private {rater} view one.",
        "view_2": f"Private {rater} view two.",
    }


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))


def fixture(tmp_path):
    private = tmp_path / "private"
    for partition in MODULE.PARTITIONS:
        for rater in MODULE.RATERS:
            write_jsonl(private / partition / f"rater_{rater}.jsonl",
                        [packet(partition, rater)])
    return private


def test_separate_archives_exclude_other_rater_and_sealed_metadata(tmp_path):
    private = fixture(tmp_path)
    output, public = tmp_path / "distribution", tmp_path / "public.json"
    value = MODULE.package(private, output, public)
    assert value["status"] == "private_packages_ready_not_annotated"
    assert json.loads(public.read_text()) == value
    assert value["public_manifest_contains_raw_text"] is False
    assert value["private_archives_contain_research_text"] is True
    assert "contains_raw_text" not in value
    for rater, other in (("A", "B"), ("B", "A")):
        archive = output / f"TRUSTXAI_RATER_{rater}.zip"
        assert archive.stat().st_mode & 0o777 == 0o600
        with zipfile.ZipFile(archive) as zipped:
            assert zipped.testzip() is None
            names = zipped.namelist()
            assert all(f"RATER_{rater}" in name for name in names)
            assert not any(f"rater_{other.lower()}" in name.casefold() for name in names)
            assert not any("sealed" in name.casefold() for name in names)
            assert len([name for name in names if name.endswith("RATER_FORM.html")]) == 1
            development = zipped.read(f"TRUSTXAI_RATER_{rater}/packets/development.jsonl")
            assert b'"condition"' not in development
            assert b'"source_id"' not in development
            template = zipped.read(
                f"TRUSTXAI_RATER_{rater}/responses/development_RESPONSES_TEMPLATE.jsonl")
            assert b"__FILL__" in template
            form = zipped.read(f"TRUSTXAI_RATER_{rater}/RATER_FORM.html").decode()
            assert "Content-Security-Policy" in form
            assert "Save progress" in form and "Resume progress" in form
            assert "Export development JSONL" in form and "Export test JSONL" in form
            assert "localStorage" in form
            assert "fetch(" not in form
            assert "XMLHttpRequest" not in form
            assert "WebSocket" not in form
            assert "<script src=" not in form
            assert f'"packet_id":"development-rater-{rater}-v1"' in form
            assert f'"packet_id":"test-rater-{rater}-v1"' in form
            assert f"rater-{other}-v1" not in form
            assert f"Private {other} view" not in form
            embedded = form.split("const ASSIGNMENT=", 1)[1].split(";\nconst CLAIMS", 1)[0]
            assignment = json.loads(embedded)
            assert assignment["rater_slot"] == rater
            assert set(assignment["partitions"]) == set(MODULE.PARTITIONS)
            for partition, rows in assignment["partitions"].items():
                assert len(rows) == 1
                assert set(rows[0]) == MODULE.PACKET_KEYS
                assert rows[0]["packet_id"] == f"{partition}-rater-{rater}-v1"
                assert not MODULE.forbidden_locations(rows[0])


def test_archive_bytes_are_deterministic(tmp_path):
    private = fixture(tmp_path)
    one, two = tmp_path / "one", tmp_path / "two"
    MODULE.package(private, one, tmp_path / "one.json")
    MODULE.package(private, two, tmp_path / "two.json")
    for rater in MODULE.RATERS:
        assert (one / f"TRUSTXAI_RATER_{rater}.zip").read_bytes() == \
               (two / f"TRUSTXAI_RATER_{rater}.zip").read_bytes()


def test_rejects_sealed_key_or_mismatched_item_sets(tmp_path):
    private = fixture(tmp_path)
    path = private / "development/rater_A.jsonl"
    value = packet("development", "A")
    value["condition"] = "P"
    write_jsonl(path, [value])
    with pytest.raises(MODULE.PackageError, match="Unexpected packet keys"):
        MODULE.package(private, tmp_path / "out", tmp_path / "public.json")

    private = fixture(tmp_path / "second")
    write_jsonl(private / "test/rater_B.jsonl",
                [packet("test", "B", "I-fedcba9876543210")])
    with pytest.raises(MODULE.PackageError, match="item sets differ"):
        MODULE.package(private, tmp_path / "out2", tmp_path / "public2.json")


def test_rejects_nonopaque_identifiers(tmp_path):
    private = fixture(tmp_path)
    value = packet("development", "A")
    value["item_id"] = "I-readable-source-name"
    write_jsonl(private / "development/rater_A.jsonl", [value])
    with pytest.raises(MODULE.PackageError, match="opaque item ID"):
        MODULE.package(private, tmp_path / "out", tmp_path / "public.json")


def test_offline_form_escapes_script_terminators():
    rows = {
        partition: [packet(partition, "A")] for partition in MODULE.PARTITIONS
    }
    rows["development"][0]["view_1"] = "Text </script><script>bad()</script>"
    form = MODULE.offline_form(rows, "A").decode()
    assert "Text </script><script>bad()" not in form
    assert "Text \\u003c/script\\u003e\\u003cscript\\u003ebad()" in form


def test_refuses_private_archives_inside_repository(tmp_path):
    private = fixture(tmp_path)
    with pytest.raises(MODULE.PackageError, match="outside the Git repository"):
        MODULE.package(private, ROOT / "research/private-rater-output",
                       tmp_path / "public.json")
