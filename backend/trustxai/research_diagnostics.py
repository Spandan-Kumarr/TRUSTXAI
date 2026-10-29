"""Controlled Step 6 checker diagnostics.

Construction intent is useful for a controlled software diagnostic, but it is
not independent semantic ground truth.  This module deliberately records that
boundary on every output and never reads benchmark gold labels.
"""
from __future__ import annotations

from copy import deepcopy
import re
from typing import Callable, Iterable

from .checks import sentence_parts, structural_issues
from .domain import (LETTERS, canonical_facts, digest, evidence_available,
                     evidence_template, valid_pair)


THRESHOLD_GRID = (0.60, 0.70, 0.80, 0.90, 0.95)
SUPPORTED_KINDS = (
    "exact_canonical",
    "audience_simplification",
    "harmless_reordering",
    "allowed_numeric_wording",
)
FAULT_KINDS = (
    "option_name",
    "span_binding",
    "changed_result",
    "counts",
    "recheck_status",
    "all_interventions",
    "unsupported_clinical_clause",
    "missing_limitation",
)
NUMBER_WORDS = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
    "5": "five", "6": "six", "7": "seven", "8": "eight",
}


def _canonical_pair(evidence: dict) -> dict:
    facts = canonical_facts(evidence)
    return {"novice": dict(facts), "expert": dict(facts)}


def _pair_with(evidence: dict, claim: str, text: str) -> dict:
    pair = _canonical_pair(evidence)
    for audience in pair:
        pair[audience][claim] = text
    return pair


def _numeric_words(text: str) -> str:
    return re.sub(r"\b[0-8]\b", lambda match: NUMBER_WORDS[match.group()], text)


def _next_letter(actual: str, excluded: Iterable[str] = ()) -> str:
    blocked = {actual, *excluded}
    return next(letter for letter in LETTERS if letter not in blocked)


def _slot(source_id: str, index: int, label: str, kind: str,
          pair: dict | None, reason: str | None = None) -> dict:
    status = "instantiated" if pair is not None else "not_instantiated"
    return {
        "slot": index,
        "variant_id": f"{source_id}-V{index:02d}",
        "source_id": source_id,
        "construction_intent": label,
        "mutation_type": kind,
        "instantiation_status": status,
        "not_instantiated_reason": reason,
        "pair": pair,
        "pair_sha256": digest(pair) if pair is not None else None,
        "independent_semantic_label": None,
        "label_status": "construction_intent_only_pending_independent_review",
    }


def construct_variants(evidence: dict) -> list[dict]:
    """Return four supported-intent and eight faulty-intent planned slots.

    A slot that cannot be realized stays in the fixed denominator with a null
    pair and an explicit reason.  It is never silently replaced by another
    mutation.
    """
    source_id = evidence.get("source_id") or evidence["input_sha256"][:16]
    if not evidence_available(evidence):
        kinds = (*SUPPORTED_KINDS, *FAULT_KINDS)
        return [
            _slot(source_id, index, "supported" if index <= 4 else "faulty",
                  kind, None, "The source lacks the protocol's minimum informative evidence")
            for index, kind in enumerate(kinds, start=1)
        ]
    canonical = _canonical_pair(evidence)
    template = evidence_template(evidence)
    # Reorder claim fields while retaining the declared numeric role order
    # inside C3.  The checker intentionally treats tested/available/valid/
    # changed as an ordered binding, so scrambling that sentence is not a
    # supported transformation.
    reordered = {audience: {claim: canonical[audience][claim]
                            for claim in ("C4", "C2", "C1", "C3")}
                 for audience in ("novice", "expert")}
    numeric = deepcopy(canonical)
    for audience in numeric:
        numeric[audience]["C3"] = _numeric_words(numeric[audience]["C3"])

    slots = [
        _slot(source_id, 1, "supported", SUPPORTED_KINDS[0], canonical),
        _slot(source_id, 2, "supported", SUPPORTED_KINDS[1], template),
        _slot(source_id, 3, "supported", SUPPORTED_KINDS[2], reordered),
        _slot(source_id, 4, "supported", SUPPORTED_KINDS[3], numeric),
    ]

    decision = evidence["decision"]
    selected = evidence.get("selected")
    recheck = evidence.get("recheck")
    wrong = _next_letter(decision.get("label", "invalid"))
    wrong_c1 = (f"Recorded model suggestion: {wrong} ({evidence['options'][wrong]}). "
                "It is not a verified diagnosis.")
    slots.append(_slot(source_id, 5, "faulty", FAULT_KINDS[0],
                       _pair_with(evidence, "C1", wrong_c1)))

    alternate_span = next((span["id"] for span in evidence["spans"]
                           if not selected or span["id"] != selected["span_id"]), None)
    if selected and alternate_span:
        c2 = canonical["expert"]["C2"].replace(selected["span_id"], alternate_span)
        slots.append(_slot(source_id, 6, "faulty", FAULT_KINDS[1],
                           _pair_with(evidence, "C2", c2)))
    else:
        slots.append(_slot(source_id, 6, "faulty", FAULT_KINDS[1], None,
                           "No selected omission and alternate span were available"))

    if selected:
        wrong_result = _next_letter(selected["label"], (decision.get("label"),))
        c2 = (f"Omitting {selected['span_id']} returned {wrong_result} instead of "
              f"{decision.get('label', 'invalid')}.")
        slots.append(_slot(source_id, 7, "faulty", FAULT_KINDS[2],
                           _pair_with(evidence, "C2", c2)))
    else:
        slots.append(_slot(source_id, 7, "faulty", FAULT_KINDS[2], None,
                           "No selected omission result was available"))

    valid = [row for row in evidence["omissions"] if row["label"] in LETTERS]
    changed = sum(bool(row["changed"]) for row in valid)
    attempted = len(evidence["omissions"])
    wrong_attempted = attempted
    wrong_changed = changed + 1 if changed < len(valid) else max(0, changed - 1)
    if not valid:  # A zero-of-zero changed count cannot be altered coherently.
        wrong_attempted = attempted + 1 if attempted < 8 else attempted - 1
    c3 = (f"{wrong_attempted} of {len(evidence['spans'])} case spans tested "
          f"by one-span omission; {len(valid)} valid labels; {wrong_changed} answer changes. "
          + ("The selected-result recheck agreed." if selected and recheck and
             selected["label"] == recheck.get("label") else
             "The selected-result recheck did not agree."))
    slots.append(_slot(source_id, 8, "faulty", FAULT_KINDS[3],
                       _pair_with(evidence, "C3", c3)))

    if selected and recheck:
        actual_agrees = selected["label"] == recheck.get("label")
        c3 = canonical["expert"]["C3"].replace(
            "The selected-result recheck agreed." if actual_agrees else
            "The selected-result recheck did not agree.",
            "The selected-result recheck did not agree." if actual_agrees else
            "The selected-result recheck agreed.")
        slots.append(_slot(source_id, 9, "faulty", FAULT_KINDS[4],
                           _pair_with(evidence, "C3", c3)))
    else:
        slots.append(_slot(source_id, 9, "faulty", FAULT_KINDS[4], None,
                           "No selected-result recheck was available"))

    slots.extend([
        _slot(source_id, 10, "faulty", FAULT_KINDS[5], _pair_with(
            evidence, "C4", "These omission tests prove the result for every possible edit "
            "and reveal the model's complete internal reasoning.")),
        _slot(source_id, 11, "faulty", FAULT_KINDS[6], _pair_with(
            evidence, "C1", canonical["expert"]["C1"] +
            " This diagnosis requires immediate emergency surgery.")),
        _slot(source_id, 12, "faulty", FAULT_KINDS[7], _pair_with(
            evidence, "C4", "No additional limitation was recorded.")),
    ])
    assert len(slots) == 12
    assert sum(row["construction_intent"] == "supported" for row in slots) == 4
    assert sum(row["construction_intent"] == "faulty" for row in slots) == 8
    return slots


def _nli_requests(pair: dict, evidence: dict) -> tuple[list[tuple[str, str]], list[dict]]:
    facts = canonical_facts(evidence)
    requests, references = [], []
    for audience, view in pair.items():
        clauses = sum((sentence_parts(view[cid]) for cid in ("C1", "C2", "C3", "C4")), [])
        if len(clauses) > 16:
            return [], [{"audience": audience, "claim": "all", "direction": "support",
                         "precheck": "clause_budget"}]
        for claim in ("C1", "C2", "C3", "C4"):
            for clause in sentence_parts(view[claim]):
                requests.append((facts[claim], clause))
                references.append({"audience": audience, "claim": claim,
                                   "direction": "support"})
            requests.append((" ".join(view.values()), facts[claim]))
            references.append({"audience": audience, "claim": claim,
                               "direction": "coverage"})
    return requests, references


def score_variants(evidence: dict, variants: list[dict],
                   scorer: Callable[[list[tuple[str, str]]], list[dict]],
                   expected_target_signature: str | None = None) -> list[dict]:
    """Score all unique NLI text pairs once and bind scores back to variants."""
    planned, unique, locations = [], [], {}
    for variant in variants:
        record = deepcopy(variant)
        pair = record["pair"]
        if pair is None:
            record.update(typed_issues=[], nli=[], nli_complete=False,
                          min_entailment=None, decisions={})
            planned.append(record)
            continue
        typed = structural_issues(pair, evidence, evidence["input_sha256"],
                                  expected_target_signature)
        requests, refs = _nli_requests(pair, evidence) if valid_pair(pair) else ([], [])
        keys = []
        for request in requests:
            key = digest(request)
            if key not in locations:
                locations[key] = len(unique)
                unique.append(request)
            keys.append(key)
        record.update(typed_issues=typed, _nli_keys=keys, _nli_refs=refs)
        planned.append(record)

    raw_scores = scorer(unique) if unique else []
    complete_batch = len(raw_scores) == len(unique)
    score_by_key = {key: raw_scores[index] for key, index in locations.items()
                    if index < len(raw_scores)}
    output = []
    for record in planned:
        keys = record.pop("_nli_keys", [])
        refs = record.pop("_nli_refs", [])
        if record["pair"] is None:
            output.append(record)
            continue
        nli = []
        for ref, key in zip(refs, keys):
            score = score_by_key.get(key, {"status": "unresolved",
                                           "reason": "Incomplete checker result"})
            nli.append({**ref, **score, "request_sha256": key})
        scored = bool(nli) and complete_batch and len(nli) == len(refs) and all(
            row.get("status") == "scored" and isinstance(row.get("entailment"), (int, float))
            for row in nli)
        record.update(
            nli=nli,
            nli_complete=scored,
            min_entailment=min((row["entailment"] for row in nli), default=None)
                           if scored else None,
            decisions={str(value): {
                "typed_plus_nli": diagnostic_decision(record["typed_issues"], nli, value),
                "nli_only": diagnostic_decision([], nli, value),
            } for value in THRESHOLD_GRID},
        )
        output.append(record)
    return output


def diagnostic_decision(typed_issues: list[dict], nli: list[dict], threshold: float) -> str:
    if not nli or any(row.get("status") != "scored" or
                      not isinstance(row.get("entailment"), (int, float)) for row in nli):
        return "abstain"
    if typed_issues:
        return "reject"
    return "accept" if all(row["entailment"] >= threshold for row in nli) else "reject"


def score_natural_outputs(evidence: dict, outputs: list[dict],
                          scorer: Callable[[list[tuple[str, str]]], list[dict]],
                          threshold: float,
                          expected_target_signature: str | None = None) -> list[dict]:
    """Post-hoc automated proxy checks that never alter natural outputs.

    Each input item must name ``condition`` and provide ``pair`` (or ``views``),
    plus its actual release status.  B4 remains outside the LLM narrative-yield
    endpoint, and a P template/fallback remains a generated-yield failure even
    when its deterministic text is structurally complete.
    """
    if threshold not in THRESHOLD_GRID:
        raise ValueError("Natural-output proxy scoring requires a frozen grid threshold")
    planned, unique, locations = [], [], {}
    for item in outputs:
        condition = item.get("condition")
        if condition not in {"B0", "B1", "B2", "B3", "B4", "P"}:
            raise ValueError("Every natural output needs a declared B0-B4/P condition")
        pair = item.get("pair", item.get("views"))
        typed, requests, refs = [], [], []
        if valid_pair(pair):
            typed = structural_issues(pair, evidence, evidence["input_sha256"],
                                      expected_target_signature)
            requests, refs = _nli_requests(pair, evidence)
        keys = []
        for request in requests:
            key = digest(request)
            if key not in locations:
                locations[key] = len(unique)
                unique.append(request)
            keys.append(key)
        planned.append({
            "condition": condition,
            "stage": item.get("stage", "final"),
            "release_status": item.get("release_status"),
            "generation_id": item.get("generation_id"),
            "pair": pair,
            "pair_sha256": digest(pair) if pair is not None else None,
            "valid_pair_schema": valid_pair(pair),
            "typed_issues": typed,
            "_nli_keys": keys,
            "_nli_refs": refs,
        })
    raw_scores = scorer(unique) if unique else []
    batch_complete = len(raw_scores) == len(unique)
    score_by_key = {key: raw_scores[index] for key, index in locations.items()
                    if index < len(raw_scores)}
    records = []
    for record in planned:
        keys, refs = record.pop("_nli_keys"), record.pop("_nli_refs")
        nli = [{**ref, **score_by_key.get(
            key, {"status": "unresolved", "reason": "Incomplete checker result"}),
                "request_sha256": key} for ref, key in zip(refs, keys)]
        if not batch_complete and nli:
            # A partial scorer response is an unresolved batch, even for rows
            # that happened to receive a positional value.
            for row in nli:
                row.update(status="unresolved", reason="Incomplete checker result")
                row.pop("entailment", None)
        decision = (diagnostic_decision(record["typed_issues"], nli, threshold)
                    if record["valid_pair_schema"] else "reject")
        condition, status = record["condition"], record["release_status"]
        fallback = condition == "P" and status in {
            "evidence_template", "fallback", "source_passages", "status_only"
        }
        generated_pair = condition != "B4" and record["valid_pair_schema"] and not fallback
        if condition == "B4":
            endpoint = "not_applicable"
        else:
            endpoint = "pass" if generated_pair and decision == "accept" else "fail"
        record.update(
            nli=nli,
            automated_proxy_decision=decision,
            frozen_threshold=threshold,
            generated_llm_pair=generated_pair,
            automated_proxy_llm_pair_endpoint=endpoint,
            independent_complete_supported_pair=None,
            analysis_status="automated_proxy_pending_independent_annotation",
        )
        records.append(record)
    return records


def natural_proxy_summary(records: list[dict]) -> dict:
    summary = {}
    for condition in ("B0", "B1", "B2", "B3", "B4", "P"):
        final = [row for row in records if row["condition"] == condition and
                 row.get("stage") == "final"]
        if condition == "B4":
            llm_yield = None
        else:
            llm_yield = (sum(row["automated_proxy_llm_pair_endpoint"] == "pass"
                             for row in final) / len(final)) if final else None
        summary[condition] = {
            "requested_sources": len(final),
            "automated_proxy_llm_pair_yield": llm_yield,
            "accepted": sum(row["automated_proxy_decision"] == "accept" for row in final),
            "rejected": sum(row["automated_proxy_decision"] == "reject" for row in final),
            "abstained": sum(row["automated_proxy_decision"] == "abstain" for row in final),
            "independent_result": None,
        }
    return {
        "analysis_status": "automated_proxy_pending_independent_annotation",
        "independent_semantic_validation": False,
        "conditions": summary,
    }


def _curve(records: list[dict], method: str, threshold: float) -> dict:
    instantiated = [row for row in records if row["instantiation_status"] == "instantiated"]
    supported = [row for row in instantiated if row["construction_intent"] == "supported"]
    faulty = [row for row in instantiated if row["construction_intent"] == "faulty"]
    key = str(threshold)
    decisions = lambda rows: [row["decisions"][key][method] for row in rows]
    support_d = decisions(supported)
    faulty_d = decisions(faulty)
    return {
        "threshold": threshold,
        "supported_slots": len(supported),
        "faulty_slots": len(faulty),
        "supported_acceptance": support_d.count("accept") / len(supported) if supported else None,
        "supported_rejection": support_d.count("reject") / len(supported) if supported else None,
        "faulty_acceptance": faulty_d.count("accept") / len(faulty) if faulty else None,
        "faulty_rejection": faulty_d.count("reject") / len(faulty) if faulty else None,
        "supported_abstention": support_d.count("abstain") / len(supported) if supported else None,
        "faulty_abstention": faulty_d.count("abstain") / len(faulty) if faulty else None,
    }


def calibrate_thresholds(records: list[dict], minimum_supported_acceptance: float = 0.90) -> dict:
    """Development-only calibration from already-scored construction labels."""
    curves = {
        method: [_curve(records, method, value) for value in THRESHOLD_GRID]
        for method in ("typed_plus_nli", "nli_only")
    }
    eligible = [row for row in curves["typed_plus_nli"]
                if row["supported_acceptance"] is not None and
                row["supported_acceptance"] >= minimum_supported_acceptance]
    selected = max((row["threshold"] for row in eligible), default=None)
    matched = None
    if selected is not None:
        target = next(row["supported_acceptance"] for row in curves["typed_plus_nli"]
                      if row["threshold"] == selected)
        matched = min(
            THRESHOLD_GRID,
            key=lambda value: (abs(next(row["supported_acceptance"] for row in
                                        curves["nli_only"] if row["threshold"] == value) - target),
                               -value),
        )
    source_count = len({row["source_id"] for row in records})
    supported_acceptance = {
        str(row["threshold"]): row["supported_acceptance"]
        for row in curves["typed_plus_nli"]
    }
    return {
        # These completion fields are consumed by the immutable held-out-test
        # freeze.  Partial/debug runs remain explicit and therefore cannot
        # accidentally authorize test access.
        "split": "development",
        "status": ("complete" if source_count == 40 and len(records) == 480
                   else "incomplete"),
        "sources_expected": 40,
        "sources_completed": source_count,
        "test_sources_accessed": 0,
        "variants_expected": 480,
        "variants_completed": len(records),
        "calibration_scope": "development_controlled_variants",
        "label_basis": "automated_construction_intent_pending_independent_review",
        "label_status": "automated_construction_intent",
        "independent_semantic_validation": False,
        "threshold_grid": list(THRESHOLD_GRID),
        "minimum_supported_acceptance": minimum_supported_acceptance,
        "typed_plus_nli_selected_threshold": selected,
        "selected_threshold": selected,
        "typed_plus_nli_selection_status": "eligible" if selected is not None else "no_eligible_threshold",
        "nli_only_matched_threshold": matched,
        "supported_acceptance_by_threshold": supported_acceptance,
        "curves": curves,
        "requested_slots": len(records),
        "instantiated_slots": sum(row["instantiation_status"] == "instantiated" for row in records),
        "missing_slots": sum(row["instantiation_status"] != "instantiated" for row in records),
    }


def public_summary(scored_records: list[dict], calibration: dict | None = None) -> dict:
    counts = {kind: {"requested": 0, "instantiated": 0} for kind in
              (*SUPPORTED_KINDS, *FAULT_KINDS)}
    for row in scored_records:
        counts[row["mutation_type"]]["requested"] += 1
        counts[row["mutation_type"]]["instantiated"] += (
            row["instantiation_status"] == "instantiated")
    return {
        "sources": len({row["source_id"] for row in scored_records}),
        "requested_variants": len(scored_records),
        "supported_requested": sum(row["construction_intent"] == "supported"
                                   for row in scored_records),
        "faulty_requested": sum(row["construction_intent"] == "faulty"
                                for row in scored_records),
        "slot_counts": counts,
        "label_status": "construction_intent_only_pending_independent_review",
        "independent_semantic_validation": False,
        "calibration": calibration,
    }
