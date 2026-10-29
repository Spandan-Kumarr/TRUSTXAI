# Custodian workflow for independent annotation

The private distribution directory contains `TRUSTXAI_RATER_A.zip` and `TRUSTXAI_RATER_B.zip`. Give each archive to a different real person. Never give either rater the sealed mapping, the other archive, benchmark gold, automated scores or condition/fault labels.

Before distribution, record each archive SHA-256 from `RATER_DISTRIBUTION_MANIFEST.json`. Each archive includes a private, self-contained `RATER_FORM.html`; it embeds only that assignment, works offline and exports separate development/test JSONL. Instruct raters to keep downloaded progress files private. Obtain one signed declaration per rater. The two pseudonyms must be different, and both people must confirm that they worked independently and did not access hidden metadata or the other response set.

Raters return two response files each: development and test. Preserve their original bytes. Do not treat a progress checkpoint or a blank template as a response. Validate completeness, assignment binding and schema before unblinding. Hash and lock both original response sets and declarations. Compute and record pre-adjudication agreement before revealing the sealed mapping or discussing disagreements.

Adjudication must create a separate record; it must not replace either original response. Only after agreement and adjudication are recorded may the custodian unblind item roles and create consensus natural-output and controlled-variant labels for formal analysis.

Packet construction and ZIP creation do not count as annotation. Until both real response sets are locked, formal H1/H2/H3 remain pending.

## Processor commands after files are returned

Keep the returned files outside the repository. The example below assumes the unchanged files are stored under `/workspace/thesis-runtime/clinical-cdss/step-06/returned-ratings` with one declaration per rater. Run the workflow separately for `development` and `test`.

```sh
cd /workspace/TRUSTXAI

/workspace/thesis-runtime/venv/bin/python research/step-06/scripts/process_annotations.py prepare \
  --partition development \
  --packet-a /workspace/thesis-runtime/clinical-cdss/step-06/annotation-private/development/rater_A.jsonl \
  --packet-b /workspace/thesis-runtime/clinical-cdss/step-06/annotation-private/development/rater_B.jsonl \
  --responses-a /workspace/thesis-runtime/clinical-cdss/step-06/returned-ratings/RATER_A_development.jsonl \
  --responses-b /workspace/thesis-runtime/clinical-cdss/step-06/returned-ratings/RATER_B_development.jsonl \
  --declaration-a /workspace/thesis-runtime/clinical-cdss/step-06/returned-ratings/RATER_A_declaration.md \
  --declaration-b /workspace/thesis-runtime/clinical-cdss/step-06/returned-ratings/RATER_B_declaration.md \
  --output-dir /workspace/thesis-runtime/clinical-cdss/step-06/annotation-processed/development
```

The command writes `AGREEMENT_REPORT.json`, the immutable preparation record and `ADJUDICATION_QUEUE.jsonl`. Preserve the queue, make a separate copy named `COMPLETED_ADJUDICATION.jsonl`, and have a real adjudicator fill every queued `adjudicated_values`, `reason`, `adjudicator_id` and `adjudicated_at` field. If the queue is empty, no adjudication file is needed.

```sh
/workspace/thesis-runtime/venv/bin/python research/step-06/scripts/process_annotations.py lock \
  --prepared-dir /workspace/thesis-runtime/clinical-cdss/step-06/annotation-processed/development \
  --sealed-mapping /workspace/thesis-runtime/clinical-cdss/step-06/annotation-private/development/sealed_mapping.json \
  --adjudication /workspace/thesis-runtime/clinical-cdss/step-06/returned-ratings/development_COMPLETED_ADJUDICATION.jsonl \
  --custodian R-CUSTODIAN
```

Repeat both commands with `--partition test` and the corresponding `test` packet, response, output and sealed-mapping paths. Omit `--adjudication` only when the generated queue contains zero rows. The processor refuses paths inside Git for private outputs and never overwrites an existing preparation or lock artifact.
