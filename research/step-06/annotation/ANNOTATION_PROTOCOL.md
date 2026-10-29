# Blinded semantic-preservation annotation protocol

Version 1.0 · frozen 27 October 2026

## Purpose

This audit asks whether an explanation accurately reports a fixed model-behavior record. It does **not** ask whether the model chose the medically correct diagnosis, whether an omitted finding is clinically causal, or whether the system should be used for a patient.

Two actual annotators independently review the same packets. One may be the researcher. The second must be an independent person. Author involvement, domain background and any likely style-based unblinding must be disclosed. An automated checker or another LLM is not an independent annotator.

## Evidence contract

Each item displays case findings and four mandatory evidence facts:

- **C1:** recorded option, exact supplied option name and model-suggestion qualification;
- **C2:** selected omitted-span identity and exact original/modified recorded answers;
- **C3:** attempted/available/valid counts, answer changes and recheck status;
- **C4:** limits concerning causation, untested edits and internal reasoning.

Judge only against that display. A general medical fact can be true but unsupported here. Do not use personal medical knowledge to repair missing evidence.

## Per-view judgment

Assign one status to C1–C4:

- `supported`: the full meaning follows without strengthening;
- `contradicted`: it conflicts with the evidence;
- `unsupported`: the evidence does not establish it;
- `missing`: the mandatory fact is absent;
- `unresolved`: the display is insufficient for a judgment; explain why.

Then inspect every other factual clause. Quote any addition and label it supported, contradicted, unsupported or unresolved. Apply scope flags where relevant. Fluency and correct keywords do not compensate for altered meaning.

Do not manually enter an overall pass. Analysis derives a complete supported view only when C1–C4 are supported and no added clause is contradicted, unsupported or unresolved. Both views must independently pass for a complete supported pair.

## Cross-view judgment

Compare View 1 and View 2 after rating them separately. For each C1–C4 meaning, record:

- `preserved`: same evidence and scope;
- `changed`: disagreement, strengthening or weakening;
- `missing`: absent from at least one view;
- `unresolved`: cannot be decided.

The neutral view labels deliberately hide novice/expert identity. Style can still reveal it; do not infer the experimental condition from style.

## Controlled variants

Controlled items look identical to natural items. The intended mutation and expected label are hidden. Judge the text actually shown. Construction intent will be compared with locked responses later. A mutation can fail to instantiate or introduce an unintended second fault; such cases must be reported rather than silently relabelled.

## Mechanical failures and templates

Missing, unparsable, blocked and status-only outputs fail LLM narrative yield mechanically. A deterministic fallback may still be rated for system semantic coverage, but it never counts as successful LLM narrative generation. These distinctions are applied from the sealed map after annotation; do not guess them.

Mechanical outputs with no view text and controlled diagnostic slots that
could not be instantiated are retained in the private sealed record and
planned denominator. They are not sent to raters and do not acquire invented
semantic labels.

## Workflow

1. Read this protocol, `RUBRIC.json` and the synthetic training examples.
2. Complete the qualification exercise without access to experimental outputs.
3. Sign the annotator declaration.
4. Review items independently in the assigned order. Do not discuss judgments or access the other response file.
5. Return a JSONL response conforming to `RESPONSE_SCHEMA.json` or use the blank CSV form.
6. Hash and lock both response files before condition/fault metadata are revealed.
7. Calculate pre-adjudication agreement. Resolve disagreements by a documented third reviewer or recorded consensus; never overwrite original responses.

Development and held-out test packets are separate. Development labels can calibrate the threshold. Held-out labels cannot change prompts, thresholds, membership, rubric or models.

For the paired H3 repair endpoint, the P-initial item is the exact stored
shared generation referenced by `P.initial_generation_id`; the P-final item is
the released repair/fallback outcome. Missing or unparseable initials are
mechanical failures and are not reconstructed for annotation.

## Reporting

Report raw agreement, Cohen's kappa for binary complete-pair and categorical claim decisions, disagreement counts/reasons and the adjudication method. Preserve source clustering in uncertainty analysis. If two real independent response sets are unavailable, label natural-output results `single-rater` or `automated estimate`; do not claim independent validation.

## Privacy and storage

Packets contain research cases and generated text. Store them under
`/workspace/thesis-runtime/clinical-cdss/step-06/annotation-private`, outside
Git. Public artifacts include only schemas, instructions, hashes, counts and
aggregate results. Do not place raw exam text or rater identities in the
repository.
