#!/usr/bin/env python3
"""Fail-fast consistency checks for the supervisor-review manuscript."""
from pathlib import Path
import json
import re
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SOURCE = ROOT / "TRUSTXAI_IEEE_MANUSCRIPT.md"
DOCX = ROOT / "TRUSTXAI_IEEE_PAPER_SUPERVISOR_DRAFT.docx"
PDF = ROOT / "TRUSTXAI_IEEE_PAPER_SUPERVISOR_DRAFT.pdf"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


text = SOURCE.read_text(encoding="utf-8")
diagnostic = json.loads((REPO / "research/step-06/test/results/DIAGNOSTIC_ACCURACY.json").read_text())
omission = json.loads((REPO / "research/step-06/test/results/OMISSION_AUDIT.json").read_text())
checker = json.loads((REPO / "research/step-06/test/results/H2_CONSTRUCTION_INTENT_PROXY.json").read_text())

require(f"{diagnostic['correct']} of {diagnostic['sources']}" in text, "diagnostic numerator/denominator missing")
require("78.33%" in text and "0.7865" in text, "diagnostic summary mismatch")
require(str(omission["valid_omission_labels"]) in text, "valid omission count missing")
require(str(omission["answer_changes"]) in text, "omission change count missing")
require("32 of 60" in text and "all 60 rechecks" in text, "source/recheck summary missing")
require(checker["methods"]["typed_plus_nli"]["requested_supported"] == 240, "checker manifest changed")
require("240 intended-supported" in text and "480 intended-faulty" in text, "checker counts missing")

references = {int(value) for value in re.findall(r"^\[(\d+)\]", text, flags=re.MULTILINE)}
body = text.split("## References", 1)[0]
citations = {int(value) for value in re.findall(r"\[(\d+)\]", body)}
require(references == set(range(1, 24)), f"reference numbering is incomplete: {sorted(references)}")
require(citations == references, f"uncited or missing references: refs={sorted(references)}, cites={sorted(citations)}")

for forbidden in (
    "state-of-the-art", "clinically safe", "clinically validated explanation",
    "outperforms GPT", "outperforms Gemini", "human raters confirmed",
):
    require(forbidden.casefold() not in text.casefold(), f"forbidden claim found: {forbidden}")

require(DOCX.is_file() and DOCX.stat().st_size > 100_000, "DOCX missing or unexpectedly small")
require(PDF.is_file() and PDF.stat().st_size > 100_000, "PDF missing or unexpectedly small")
subprocess.run(["unzip", "-tqq", str(DOCX)], check=True)
with tempfile.NamedTemporaryFile(suffix=".txt") as output:
    subprocess.run(["pdftotext", str(PDF), output.name], check=True)
    rendered = Path(output.name).read_text(errors="replace")
require("Paper Title" not in rendered and "Deepti Taori" not in rendered,
        "uploaded template guidance or unrelated authors remain")
require("TRUSTXAI" in rendered and "REFERENCES" in rendered, "rendered paper is incomplete")
require("[Supervisor Name]" in rendered, "expected author placeholder missing")
print("Paper validation passed: numerical anchors, citations, claim boundary, DOCX and PDF.")
