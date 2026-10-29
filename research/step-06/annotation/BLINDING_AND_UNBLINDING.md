# Blinding and unblinding procedure

Rater packets expose an opaque item ID, an opaque source ID, the displayed evidence contract and two neutrally labelled views. They do not expose condition, prompt, model, generation stage, repair/gate status, automated scores, benchmark answer, intended controlled label or mutation family.

`sealed_mapping.json` is private. Only the experiment custodian may access it before response lock. Raters must not receive the original matrix/variant exports or use source IDs to search other artifacts. Hash-derived opaque IDs provide reproducibility, not cryptographic anonymity.

The sealed map also records mechanical natural failures and non-instantiated
controlled slots under `nonreviewable`. They are included in operational
denominators after unblinding but have no rater response and no fabricated
semantic label.

Before unblinding:

1. validate every response against `RESPONSE_SCHEMA.json`;
2. compute SHA-256 for both original response files;
3. complete `ANNOTATION_LOCK.json` with annotator declarations and file hashes;
4. copy the locked files to a read-only or versioned location;
5. compute and record pre-adjudication agreement.

Validate the completed lock against `ANNOTATION_LOCK_SCHEMA.json`. A lock may
set `status` to `locked` and `independent_annotation_ready` to `true` only for
two distinct real raters whose response and declaration hashes are present,
whose independence is confirmed, whose responses pass `RESPONSE_SCHEMA.json`,
and whose pre-adjudication agreement has already been recorded. The two rater
IDs must also be compared directly because JSON Schema cannot express that
cross-field inequality.

After lock, join responses to `sealed_mapping.json`. Calculate construction realization separately from construction intent. Preserve both original response files. Adjudication creates a third record and must not replace either rater's data.

Full condition blinding cannot be guaranteed because template structure or writing style may reveal a method. Report this limitation and any actual unblinding disclosed by annotators.
