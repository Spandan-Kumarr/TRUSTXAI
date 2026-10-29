"""Frozen, source-level analyses for the Step 6 clinical-CDSS study.

This module consumes structured records only.  It never reads case prose and it
does not infer semantic labels from model/checker output.  Formal H1/H2/H3
analyses fail closed when an independently reviewed label is required but
missing.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import math
import random
import statistics
from typing import Iterable, Mapping, Sequence


LETTERS = ("A", "B", "C", "D")
INDEPENDENT_LABEL_STATUSES = {
    "independent_consensus",
    "independent_adjudicated",
}
H1_CONDITIONS = ("P", "B1")
H2_METHODS = ("typed_plus_nli", "nli_only")
H2_DECISIONS = ("accept", "reject", "abstain", "missing")


class AnalysisContractError(ValueError):
    """A structured analysis input violates the frozen record contract."""


class IndependentLabelsIncomplete(AnalysisContractError):
    """Formal semantic analysis was requested without complete independent labels."""


def _ratio(numerator: int | float, denominator: int | float):
    return numerator / denominator if denominator else None


def _percentile(values: Sequence[float], probability: float) -> float:
    """Linear percentile (the NumPy default), implemented without NumPy."""
    if not values:
        raise AnalysisContractError("A percentile requires at least one value")
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def exact_mcnemar(a: Sequence[bool], b: Sequence[bool]) -> dict:
    """Two-sided exact McNemar/binomial inference for paired binary outcomes.

    ``a_only`` is the number of pairs won by ``a`` and ``b_only`` the number
    won by ``b``.  For p=0.5 the two-sided exact binomial probability is twice
    the lower tail, clipped at one.
    """
    if len(a) != len(b):
        raise AnalysisContractError("Paired McNemar inputs have different lengths")
    a_only = sum(bool(av) and not bool(bv) for av, bv in zip(a, b))
    b_only = sum(bool(bv) and not bool(av) for av, bv in zip(a, b))
    both = sum(bool(av) and bool(bv) for av, bv in zip(a, b))
    neither = len(a) - a_only - b_only - both
    discordant = a_only + b_only
    if discordant == 0:
        p_value = 1.0
    else:
        tail = sum(math.comb(discordant, k) for k in range(min(a_only, b_only) + 1)) / (2**discordant)
        p_value = min(1.0, 2 * tail)
    return {
        "n": len(a),
        "both_success": both,
        "a_only": a_only,
        "b_only": b_only,
        "neither_success": neither,
        "discordant": discordant,
        "two_sided_exact_p": p_value,
    }


def holm_adjust(p_values: Mapping[str, float]) -> dict[str, float]:
    """Holm step-down adjusted p-values, retaining hypothesis identifiers."""
    for identifier, value in p_values.items():
        if not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
            raise AnalysisContractError(f"Invalid p-value for {identifier}")
    ordered = sorted(p_values.items(), key=lambda item: (item[1], item[0]))
    adjusted, running = {}, 0.0
    count = len(ordered)
    for rank, (identifier, value) in enumerate(ordered):
        running = max(running, min(1.0, (count - rank) * float(value)))
        adjusted[identifier] = running
    return {identifier: adjusted[identifier] for identifier in p_values}


def paired_sign_flip_p(
    differences: Sequence[float], *, permutations: int = 100000, seed: int = 20261027
) -> dict:
    """Two-sided paired source-level sign-flip inference."""
    all_values = [float(value) for value in differences]
    values = [value for value in all_values if value != 0.0]
    if not values:
        return {"nonzero_pairs": 0, "observed_mean": 0.0, "two_sided_p": 1.0,
                "method": "all paired differences are zero"}
    observed, tolerance = abs(statistics.fmean(all_values)), 1e-15
    if len(values) <= 20:
        total, extreme = 2 ** len(values), 0
        for assignment in range(total):
            value = sum(item if assignment & (1 << index) else -item
                        for index, item in enumerate(values)) / len(all_values)
            extreme += abs(value) + tolerance >= observed
        p_value, method, used = extreme / total, "exact source-level sign-flip", total
    else:
        if permutations < 1:
            raise AnalysisContractError("Sign-flip permutations must be positive")
        rng, extreme = random.Random(seed), 0
        for _ in range(permutations):
            value = sum(item if rng.getrandbits(1) else -item for item in values) / len(all_values)
            extreme += abs(value) + tolerance >= observed
        p_value, method, used = ((extreme + 1) / (permutations + 1),
                                 "Monte Carlo source-level sign-flip", permutations)
    return {"nonzero_pairs": len(values), "observed_mean": statistics.fmean(all_values),
            "two_sided_p": p_value, "method": method, "assignments_or_permutations": used,
            "seed": None if method.startswith("exact") else seed}


def stratified_paired_bootstrap(
    rows: Sequence[Mapping],
    a_key: str,
    b_key: str,
    *,
    stratum_key: str = "correct_option",
    replicates: int = 5000,
    seed: int = 20261027,
) -> dict:
    """Percentile CI for a paired mean difference, resampling source rows by stratum."""
    if not rows:
        raise AnalysisContractError("Bootstrap rows are empty")
    if replicates < 1:
        raise AnalysisContractError("Bootstrap replicates must be positive")
    strata: dict[str, list[Mapping]] = defaultdict(list)
    for row in rows:
        if stratum_key not in row or a_key not in row or b_key not in row:
            raise AnalysisContractError("Bootstrap row is missing a stratum or paired outcome")
        strata[str(row[stratum_key])].append(row)
    rng = random.Random(seed)
    draws = []
    for _ in range(replicates):
        differences = []
        for key in sorted(strata):
            group = strata[key]
            for _ in range(len(group)):
                sampled = group[rng.randrange(len(group))]
                differences.append(float(sampled[a_key]) - float(sampled[b_key]))
        draws.append(statistics.fmean(differences))
    estimate = statistics.fmean(float(row[a_key]) - float(row[b_key]) for row in rows)
    return {
        "estimate": estimate,
        "ci95": [_percentile(draws, 0.025), _percentile(draws, 0.975)],
        "replicates": replicates,
        "seed": seed,
        "strata": {key: len(value) for key, value in sorted(strata.items())},
        "method": "paired source bootstrap; percentile interval; resampled within correct-option strata",
    }


def _source_map(sources: Sequence[Mapping], expected_n: int | None = None) -> dict[str, Mapping]:
    mapped = {}
    for source in sources:
        identifier = str(source.get("source_id", ""))
        if not identifier or identifier in mapped:
            raise AnalysisContractError("Source IDs must be present and unique")
        option = source.get("correct_option")
        if option not in LETTERS:
            raise AnalysisContractError(f"Source {identifier} has no A-D correct-option stratum")
        mapped[identifier] = source
    if expected_n is not None and len(mapped) != expected_n:
        raise AnalysisContractError(f"Expected {expected_n} sources, received {len(mapped)}")
    if expected_n in (40, 60):
        counts = Counter(source["correct_option"] for source in mapped.values())
        expected_per_option = expected_n // 4
        if any(counts[option] != expected_per_option for option in LETTERS):
            raise AnalysisContractError(
                f"Frozen {expected_n}-source set must contain {expected_per_option} A-D positions each"
            )
    return mapped


def _independent(row: Mapping) -> bool:
    status = row.get("annotation_status")
    if status in INDEPENDENT_LABEL_STATUSES:
        return True
    # A generic ``independent`` marker is accepted only when the record also
    # proves that at least two raters contributed.  This prevents a lone
    # review from being promoted to the formal two-rater endpoint by naming
    # convention alone.
    return status == "independent" and int(row.get("independent_rater_count", 0)) >= 2


def _h2_method(row: Mapping) -> str | None:
    """Normalize the early implementation alias without changing the endpoint."""
    value = row.get("method")
    return "typed_plus_nli" if value == "typed_nli" else value


def h1_success(row: Mapping | None, *, require_independent: bool = True) -> bool:
    """Apply the all-requested-source H1 rule to one condition record."""
    if not row or row.get("condition") == "B4":
        return False
    eligible_narrative = (
        row.get("output_kind") == "llm_narrative"
        and row.get("release_status") == "generated"
        and row.get("parseable") is True
        and row.get("blocked") is not True
    )
    if not eligible_narrative:
        return False
    if require_independent and not _independent(row):
        raise IndependentLabelsIncomplete(
            f"Generated output {row.get('source_id')}/{row.get('condition')} lacks an independent label"
        )
    label = row.get("pair_supported")
    if not isinstance(label, bool):
        raise IndependentLabelsIncomplete(
            f"Generated output {row.get('source_id')}/{row.get('condition')} has no binary support label"
        )
    return label


def analyze_h1(
    records: Sequence[Mapping],
    sources: Sequence[Mapping],
    *,
    require_independent: bool = True,
    expected_n: int | None = None,
    replicates: int = 5000,
    seed: int = 20261027,
) -> dict:
    source_map = _source_map(sources, expected_n)
    indexed = {}
    for row in records:
        condition = row.get("condition")
        source_id = row.get("source_id")
        if condition not in H1_CONDITIONS:
            continue
        if row.get("stage") not in (None, "final"):
            continue
        key = (source_id, condition)
        if key in indexed:
            raise AnalysisContractError(f"Duplicate H1 record {source_id}/{condition}")
        if source_id not in source_map:
            raise AnalysisContractError(f"Unknown H1 source {source_id}")
        indexed[key] = row
    paired = []
    for source_id, source in source_map.items():
        p_value = h1_success(indexed.get((source_id, "P")), require_independent=require_independent)
        b1_value = h1_success(indexed.get((source_id, "B1")), require_independent=require_independent)
        paired.append({"source_id": source_id, "correct_option": source["correct_option"],
                       "P": p_value, "B1": b1_value})
    p = [row["P"] for row in paired]
    b1 = [row["B1"] for row in paired]
    test = exact_mcnemar(p, b1)
    by_target_outcome = {}
    for label, target_correct in (("target_correct", True), ("target_incorrect", False)):
        subset = [row for row in paired if (
            source_map[row["source_id"]].get("predicted_option")
            == source_map[row["source_id"]].get("correct_option")) is target_correct]
        # Omit the split rather than silently treating missing predictions as
        # incorrect.  The option-selection export is expected after the
        # prediction freeze and gold release.
        subset = [row for row in subset
                  if source_map[row["source_id"]].get("predicted_option") is not None]
        by_target_outcome[label] = {
            "sources": len(subset),
            "P_successes": sum(row["P"] for row in subset),
            "B1_successes": sum(row["B1"] for row in subset),
            "P_yield": _ratio(sum(row["P"] for row in subset), len(subset)),
            "B1_yield": _ratio(sum(row["B1"] for row in subset), len(subset)),
        }
    return {
        "analysis_status": "independent" if require_independent else "non_independent_proxy",
        "endpoint": "complete supported LLM narrative-pair yield",
        "denominator": len(paired),
        "P_successes": sum(p),
        "B1_successes": sum(b1),
        "P_yield": _ratio(sum(p), len(p)),
        "B1_yield": _ratio(sum(b1), len(b1)),
        "B4_LLM_narrative_yield": None,
        "paired_difference_P_minus_B1": _ratio(sum(p) - sum(b1), len(p)),
        "mcnemar": test,
        "bootstrap": stratified_paired_bootstrap(paired, "P", "B1", replicates=replicates, seed=seed),
        "by_frozen_target_outcome": by_target_outcome,
        "failure_rule": "missing, unparseable, blocked, status-only and fallback/template outputs fail",
        "source_outcomes": paired,
    }


def _h2_counts(rows: Sequence[Mapping], method: str) -> dict:
    selected = [row for row in rows if _h2_method(row) == method]
    counts = {truth: Counter() for truth in ("supported", "faulty")}
    for row in selected:
        truth, decision = row.get("truth"), row.get("decision")
        if truth not in counts or decision not in H2_DECISIONS:
            raise AnalysisContractError("H2 rows require supported/faulty truth and a declared decision")
        counts[truth][decision] += 1
    output = {"method": method, "counts": {key: dict(value) for key, value in counts.items()}}
    supported_total = sum(counts["supported"].values())
    faulty_total = sum(counts["faulty"].values())
    supported_evaluable = supported_total - counts["supported"]["missing"]
    faulty_evaluable = faulty_total - counts["faulty"]["missing"]
    output["requested_supported"] = supported_total
    output["requested_faulty"] = faulty_total
    output["coverage"] = _ratio(supported_evaluable + faulty_evaluable, supported_total + faulty_total)
    output["false_acceptance_requested"] = _ratio(counts["faulty"]["accept"], faulty_total)
    output["false_acceptance_evaluable"] = _ratio(counts["faulty"]["accept"], faulty_evaluable)
    output["false_rejection_requested"] = _ratio(counts["supported"]["reject"], supported_total)
    output["false_rejection_evaluable"] = _ratio(counts["supported"]["reject"], supported_evaluable)
    output["supported_acceptance_requested"] = _ratio(counts["supported"]["accept"], supported_total)
    output["supported_acceptance_evaluable"] = _ratio(counts["supported"]["accept"], supported_evaluable)
    output["abstention_requested"] = _ratio(
        counts["supported"]["abstain"] + counts["faulty"]["abstain"], supported_total + faulty_total
    )
    output["missing_slots"] = counts["supported"]["missing"] + counts["faulty"]["missing"]
    return output


def _h2_source_metric(rows: Sequence[Mapping], source_ids: Sequence[str], method: str, metric: str) -> float:
    expanded = []
    by_source = defaultdict(list)
    for row in rows:
        by_source[row["source_id"]].append(row)
    for source_id in source_ids:
        expanded.extend(by_source[source_id])
    value = _h2_counts(expanded, method)[metric]
    return 0.0 if value is None else float(value)


def analyze_h2(
    records: Sequence[Mapping],
    sources: Sequence[Mapping],
    *,
    require_independent: bool = True,
    expected_n: int | None = None,
    replicates: int = 5000,
    seed: int = 20261027,
) -> dict:
    source_map = _source_map(sources, expected_n)
    seen = set()
    method_slots = {method: set() for method in H2_METHODS}
    slot_truth = {}
    for row in records:
        source_id = row.get("source_id")
        if source_id not in source_map:
            raise AnalysisContractError(f"Unknown H2 source {source_id}")
        method = _h2_method(row)
        if method not in H2_METHODS:
            raise AnalysisContractError("Unknown H2 method")
        key = (source_id, row.get("variant_id"), method)
        if key in seen:
            raise AnalysisContractError(f"Duplicate H2 record {key}")
        seen.add(key)
        method_slots[method].add((source_id, row.get("variant_id")))
        slot = (source_id, row.get("variant_id"))
        if slot in slot_truth and slot_truth[slot] != row.get("truth"):
            raise AnalysisContractError(f"H2 methods disagree on the truth label for {slot}")
        slot_truth[slot] = row.get("truth")
        if row.get("nli_status") == "unresolved" and row.get("decision") == "accept":
            raise AnalysisContractError(f"Unresolved NLI input cannot be accepted for {key}")
        if row.get("decision") != "missing":
            if require_independent and not _independent(row):
                raise IndependentLabelsIncomplete(f"H2 variant {key} lacks independent review")
            if row.get("truth") not in ("supported", "faulty"):
                raise IndependentLabelsIncomplete(f"H2 variant {key} lacks a binary truth label")
    if method_slots["typed_plus_nli"] != method_slots["nli_only"]:
        raise AnalysisContractError("H2 methods do not contain the same source/variant slots")
    represented = {source_id for source_id, _ in method_slots["typed_plus_nli"]}
    if represented != set(source_map):
        raise AnalysisContractError("H2 records do not cover the frozen source set")
    if expected_n in (40, 60):
        per_source = Counter(source_id for source_id, _ in method_slots["typed_plus_nli"])
        if any(per_source[source_id] != 12 for source_id in source_map):
            raise AnalysisContractError("H2 requires all 12 planned diagnostic slots per frozen source")
    # When the exporter supplies a score signature, both ablations must point
    # to the same checker outputs.  H2 changes only deterministic typed guards;
    # recomputing NLI would violate the frozen same-score comparison.
    by_slot: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    for row in records:
        signature = row.get("score_signature")
        if signature is not None:
            by_slot[(row["source_id"], row.get("variant_id"))][_h2_method(row)] = signature
    for slot, signatures in by_slot.items():
        if len(signatures) == 2 and len(set(signatures.values())) != 1:
            raise AnalysisContractError(f"H2 methods do not reuse the same NLI scores for {slot}")
    summaries = {method: _h2_counts(records, method) for method in H2_METHODS}
    strata = defaultdict(list)
    for source_id, source in source_map.items():
        strata[source["correct_option"]].append(source_id)
    metrics = ("false_acceptance_requested", "false_rejection_requested",
               "supported_acceptance_requested", "abstention_requested")
    rng = random.Random(seed)
    draws = {metric: [] for metric in metrics}
    for _ in range(replicates):
        sampled = []
        for option in sorted(strata):
            group = strata[option]
            sampled.extend(group[rng.randrange(len(group))] for _ in range(len(group)))
        for metric in metrics:
            typed = _h2_source_metric(records, sampled, "typed_plus_nli", metric)
            nli = _h2_source_metric(records, sampled, "nli_only", metric)
            draws[metric].append(typed - nli)
    differences, tests = {}, {}
    for metric in metrics:
        left, right = summaries["typed_plus_nli"][metric], summaries["nli_only"][metric]
        per_source = [
            _h2_source_metric(records, [source_id], "typed_plus_nli", metric)
            - _h2_source_metric(records, [source_id], "nli_only", metric)
            for source_id in source_map
        ]
        differences[metric] = {
            "typed_nli_minus_nli_only": None if left is None or right is None else left - right,
            "ci95": [_percentile(draws[metric], 0.025), _percentile(draws[metric], 0.975)],
        }
        tests[metric] = paired_sign_flip_p(per_source, seed=seed + len(tests))
    return {
        "analysis_status": "independent" if require_independent else "non_independent_proxy",
        "methods": summaries,
        "paired_source_bootstrap": {
            "replicates": replicates,
            "seed": seed,
            "strata": {key: len(value) for key, value in sorted(strata.items())},
            "differences": differences,
            "method": "source-cluster bootstrap; all diagnostic variants retained with each sampled source",
        },
        "paired_source_tests": tests,
    }


def diagnostic_metrics(sources: Sequence[Mapping], *, expected_n: int | None = None) -> dict:
    source_map = _source_map(sources, expected_n)
    matrix = {truth: Counter() for truth in LETTERS}
    for source in source_map.values():
        prediction = source.get("predicted_option")
        prediction = prediction if prediction in LETTERS else "invalid"
        matrix[source["correct_option"]][prediction] += 1
    recalls, f1s = {}, {}
    for label in LETTERS:
        tp = matrix[label][label]
        fn = sum(matrix[label][prediction] for prediction in (*LETTERS, "invalid") if prediction != label)
        fp = sum(matrix[truth][label] for truth in LETTERS if truth != label)
        recalls[label] = _ratio(tp, tp + fn) or 0.0
        precision = _ratio(tp, tp + fp) or 0.0
        f1s[label] = 0.0 if precision + recalls[label] == 0 else 2 * precision * recalls[label] / (precision + recalls[label])
    correct = sum(matrix[label][label] for label in LETTERS)
    valid = sum(matrix[truth][prediction] for truth in LETTERS for prediction in LETTERS)
    return {
        "sources": len(source_map),
        "correct": correct,
        "accuracy": _ratio(correct, len(source_map)),
        "balanced_accuracy": statistics.fmean(recalls.values()),
        "macro_F1": statistics.fmean(f1s.values()),
        "recall_by_correct_option": recalls,
        "valid_decision_fraction": _ratio(valid, len(source_map)),
        "confusion_matrix": {
            "rows_true": list(LETTERS),
            "columns_predicted": [*LETTERS, "invalid"],
            "values": [[matrix[truth][prediction] for prediction in (*LETTERS, "invalid")] for truth in LETTERS],
        },
        "interpretation": "option-position diagnostics, not disease-class performance",
    }


def omission_summary(records: Sequence[Mapping], *, expected_n: int | None = None) -> dict:
    if expected_n is not None and len(records) != expected_n:
        raise AnalysisContractError(f"Expected {expected_n} omission records, received {len(records)}")
    totals = Counter()
    transitions = Counter()
    per_source = []
    for row in records:
        original = row.get("original_label")
        available = int(row.get("available_spans", len(row.get("spans", []))))
        omissions = list(row.get("omissions", []))
        valid = [item for item in omissions if item.get("label") in LETTERS]
        changed = [item for item in valid if original in LETTERS and item["label"] != original]
        for item in omissions:
            transitions[f"{original if original in LETTERS else 'invalid'}->{item.get('label') if item.get('label') in LETTERS else 'invalid'}"] += 1
        recheck = row.get("recheck") or {}
        selected = row.get("selected") or {}
        recheck_attempted = bool(recheck)
        recheck_agreed = recheck_attempted and recheck.get("label") in LETTERS and recheck.get("label") == selected.get("label")
        informative = original in LETTERS and bool(valid) and recheck_agreed
        per_source.append({"source_id": row.get("source_id"), "available_spans": available,
                           "attempted": len(omissions), "valid": len(valid), "changes": len(changed),
                           "any_change": bool(changed), "recheck_attempted": recheck_attempted,
                           "recheck_agreed": recheck_agreed, "informative_evidence": informative})
        totals.update(available=available, attempted=len(omissions), valid=len(valid), changes=len(changed),
                      sources_any_change=bool(changed), recheck_attempted=recheck_attempted,
                      recheck_agreed=recheck_agreed, informative=informative)
    n = len(records)
    return {
        "sources": n,
        "available_spans": totals["available"],
        "omission_attempts": totals["attempted"],
        "valid_omission_labels": totals["valid"],
        "answer_changes": totals["changes"],
        "sources_with_any_change": totals["sources_any_change"],
        "selected_rechecks_attempted": totals["recheck_attempted"],
        "selected_rechecks_agreed": totals["recheck_agreed"],
        "recheck_agreement_among_attempts": _ratio(totals["recheck_agreed"], totals["recheck_attempted"]),
        "recheck_agreement_all_sources": _ratio(totals["recheck_agreed"], n),
        "informative_evidence_sources": totals["informative"],
        "informative_evidence_fraction": _ratio(totals["informative"], n),
        "transitions": dict(sorted(transitions.items())),
        "per_source": per_source,
        "interpretation": "input-removal observations; not clinical causation",
    }


def analyze_h3(
    records: Sequence[Mapping],
    sources: Sequence[Mapping],
    *,
    require_independent: bool = True,
    expected_n: int | None = None,
    replicates: int = 5000,
    seed: int = 20261027,
) -> dict:
    source_map = _source_map(sources, expected_n)
    indexed = {}
    for row in records:
        if row.get("condition") != "P" or row.get("stage") not in ("initial", "final"):
            continue
        key = (row.get("source_id"), row.get("stage"))
        if key in indexed:
            raise AnalysisContractError(f"Duplicate H3 record {key}")
        indexed[key] = row
    paired = []
    for source_id, source in source_map.items():
        initial = h1_success(indexed.get((source_id, "initial")), require_independent=require_independent)
        final = h1_success(indexed.get((source_id, "final")), require_independent=require_independent)
        paired.append({"source_id": source_id, "correct_option": source["correct_option"],
                       "final": final, "initial": initial})
    final = [row["final"] for row in paired]
    initial = [row["initial"] for row in paired]
    return {
        "analysis_status": "independent" if require_independent else "non_independent_proxy",
        "initial_successes": sum(initial),
        "final_successes": sum(final),
        "paired_change": _ratio(sum(final) - sum(initial), len(paired)),
        "mcnemar": exact_mcnemar(final, initial),
        "bootstrap": stratified_paired_bootstrap(paired, "final", "initial", replicates=replicates, seed=seed),
        "source_outcomes": paired,
    }


def summarize_numbers(values: Iterable[float]) -> dict:
    values = [float(value) for value in values]
    if not values:
        return {"n": 0, "total": 0.0, "mean": None, "median": None, "q1": None, "q3": None, "p95": None}
    return {"n": len(values), "total": sum(values), "mean": statistics.fmean(values),
            "median": statistics.median(values), "q1": _percentile(values, .25),
            "q3": _percentile(values, .75), "p95": _percentile(values, .95)}


def cost_summary(records: Sequence[Mapping]) -> dict:
    """Report actual physical and logical standalone cost without double counting shared calls."""
    physical_ids, physical = set(), []
    logical = defaultdict(list)
    for row in records:
        call_id = row.get("physical_call_id")
        if not call_id or call_id in physical_ids:
            raise AnalysisContractError("Physical cost call IDs must be present and unique")
        physical_ids.add(call_id)
        physical.append(row)
        charged = row.get("charged_conditions") or [row.get("condition")]
        for condition in charged:
            if not condition:
                raise AnalysisContractError("Every cost call needs a logical condition")
            logical[str(condition)].append(row)
    fields = ("wall_seconds", "CPU_seconds", "prompt_tokens", "new_tokens")
    summarize = lambda rows: {
        "calls": len(rows),
        **{field: summarize_numbers(row.get(field, 0) for row in rows) for field in fields},
        "cache_hits": sum(bool(row.get("cache_hit")) for row in rows),
    }
    by_component = defaultdict(list)
    for row in physical:
        by_component[str(row.get("component", "unspecified"))].append(row)
    rss_values = [float(row["peak_process_RSS_GiB"]) for row in physical
                  if isinstance(row.get("peak_process_RSS_GiB"), (int, float))]
    return {
        "actual_physical_matrix": summarize(physical),
        "actual_by_component": {key: summarize(value) for key, value in sorted(by_component.items())},
        "logical_standalone_by_condition": {key: summarize(value) for key, value in sorted(logical.items())},
        "peak_process_RSS_GiB": max(rss_values) if rss_values else None,
        "accounting_note": "shared physical calls count once in matrix cost and once for each charged condition in standalone cost",
    }
