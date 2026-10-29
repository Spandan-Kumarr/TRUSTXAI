# Step 6 annotation package

This directory contains the frozen public instructions and blank instruments for independent semantic-preservation review. It contains no reviewer, participant or experimental result.

Private inputs and packets must remain under `/workspace/thesis-runtime`, outside Git. The builder rejects a private output path inside the repository.

The normal workflow consumes the frozen runner checkpoints and diagnostic
artifacts directly. It verifies every runner-envelope payload hash, binds the
matrix and diagnostics to the same evidence input, converts C1–C4 dictionaries
to neutral view text, and writes its normalized intermediate JSONL under the
private annotation directory. No manual copy or edit step is required.
For H3 it also resolves the exact P shared-initial generation by its immutable
`initial_generation_id` and exports that row with `stage: "initial"`; the six
condition outcomes remain `stage: "final"`.

## Private input contract

Natural-output JSONL uses exactly these fields:

```json
{
  "partition": "development",
  "source_id": "private-source-id",
  "logical_id": "unique-logical-output-id",
  "condition": "B1",
  "stage": "final",
  "output_status": "generated",
  "evidence_display": {
    "case_findings": [{"id": "S1", "text": "private finding"}],
    "C1": "recorded decision fact",
    "C2": "selected omission fact",
    "C3": "coverage and recheck fact",
    "C4": "interpretation limits"
  },
  "views": {"novice": "private output", "expert": "private output"}
}
```

`views` may be `null` only for a mechanical status: `missing`, `unparseable`,
`blocked`, `status_only`, `invalid_frozen_decision` or
`insufficient_evidence`. Other permitted statuses are `generated`,
`baseline_unchecked`, `fallback_template` and `evidence_template`.

Controlled-variant JSONL uses exactly:

```json
{
  "partition": "development",
  "source_id": "private-source-id",
  "variant_id": "unique-variant-id",
  "construction_intent": "faulty",
  "mutation_type": "option_name",
  "instantiation_status": "instantiated",
  "not_instantiated_reason": null,
  "evidence_display": {"case_findings": [], "C1": "...", "C2": "...", "C3": "...", "C4": "..."},
  "views": {"novice": "private variant", "expert": "private variant"}
}
```

The eight frozen faulty mutation types are `option_name`, `span_binding`,
`changed_result`, `counts`, `recheck_status`, `all_interventions`,
`unsupported_clinical_clause` and `missing_limitation`. The earlier aliases
`omitted_span_binding`, `changed_answer_result`, `test_flip_counts` and
`all_interventions_generalization` remain readable for reproducibility. Each
source also requires four distinct supported-control mutation types.

When a planned diagnostic cannot be constructed, retain its requested slot
with `instantiation_status: "not_instantiated"`, a non-empty
`not_instantiated_reason`, and `views: null`. Such a slot stays in the planned
denominator and private sealed map, but it is never shown to a rater or treated
as a semantic judgment.

Benchmark answer fields, checker scores and experiment metadata are prohibited from `evidence_display`.

## Build packets

```sh
/workspace/thesis-runtime/venv/bin/python \
  research/step-06/scripts/build_annotation_packets.py \
  --runtime-root /workspace/thesis-runtime/clinical-cdss/step-06/private \
  --private-root /workspace/thesis-runtime/clinical-cdss/step-06/annotation-private \
  --public-manifest research/step-06/annotation/PACKET_MANIFEST-development.json \
  --partition development
```

For a reproducibility check against an already normalized export, replace
`--runtime-root` with both `--natural PATH` and `--variants PATH`.

Run the test partition only after the development rubric/threshold/configuration freeze, using a separate test manifest. The builder enforces 40/60 source counts, one final B0–B4/P row per source, and 4 supported plus 8 faulty requested variant slots per source. It deduplicates identical natural texts for judgment while retaining their logical roles in the sealed map. Mechanical natural failures and non-instantiated controlled slots remain sealed as nonreviewable outcomes and do not enter rater packets.

Every source also carries one P-initial logical row for paired H3 analysis. If
the shared initial was never attempted, the row is explicitly `missing` and is
kept only in the sealed nonreviewable record. If its stored output is invalid,
it is explicitly `unparseable`. Neither case receives an invented judgment.

`--force` may replace unannotated packets. It cannot rebuild a directory containing `responses/` or `ANNOTATION_LOCK.json`. The builder never creates or fills rater responses.

## Distribute and process ratings

`package_rater_materials.py` creates separate private Rater A/B archives outside Git. Each archive contains that rater's development/test assignment, a self-contained offline form, the frozen public instruments and blank response/declaration templates. Archive hashes and item counts are recorded in `RATER_DISTRIBUTION_MANIFEST.json`; research text remains private.

After two real raters return complete files, `process_annotations.py prepare` validates packet bindings, response schemas, distinct identities, declarations, exact coverage and frozen hashes, then records agreement and creates a separate adjudication queue while still blinded. `process_annotations.py lock` accepts only a complete adjudication record, writes the response lock before opening the sealed mapping and emits canonical semantic-label JSONL for formal analysis. See `RATER_WORKFLOW.md` for commands.

## Interpretation

Packet creation is not annotation. `PACKET_MANIFEST.json` remains a pending placeholder until real matrix exports exist. Independent validation requires two locked human response files. The audience study remains explicitly unexecuted in `PHASE_II_AUDIENCE_STUDY_STATUS.md`.

`ANNOTATION_LOCK_SCHEMA.json` is the executable minimum gate for declaring an
independent annotation lock. The response processor additionally enforces
distinct rater IDs, unchanged original files, exact packet coverage,
pre-adjudication agreement and complete separate adjudication. Until those
checks pass, `independent_annotation_ready` remains `false`; automated results
may be reported only as non-independent diagnostics or proxies.
