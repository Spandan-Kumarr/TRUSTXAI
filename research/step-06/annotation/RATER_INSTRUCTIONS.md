# TRUSTXAI blinded rater instructions

You are reviewing whether two explanation views accurately preserve the **displayed model-behavior evidence**. You are not diagnosing a patient and must not use outside medical knowledge to correct or strengthen the text.

1. Read `ANNOTATION_PROTOCOL.md`, `RUBRIC.json` and `TRAINING_EXAMPLES.json`.
2. Complete and sign `ANNOTATOR_DECLARATION.md` before opening experimental packets.
3. Work independently. Do not contact the other rater, inspect another packet, search opaque IDs, or access benchmark answers, method labels, checker scores or intended mutations.
4. Open `RATER_FORM.html` locally in a current browser. It already contains only your assigned development and test packets and does not use the network. Review development first, then test, in the supplied order.
5. For each view, judge C1–C4 against the displayed evidence. Record every added factual clause and applicable scope flag. Then compare the two views for cross-view preservation.
6. Enter one pseudonym matching `R-[A-Za-z0-9_-]+`. Use **Save progress** regularly; it downloads a private JSON checkpoint. **Resume progress** accepts only a checkpoint bound to this exact assignment. Browser storage is only a convenience and is not your backup.
7. Export separate development and test JSONL files. The form refuses export until every selected row is complete and schema-shaped. The files in `responses/` are blank fallback templates only; every `__FILL__` must be replaced if you use them instead of the form.
8. Use `unresolved` only when the displayed material cannot support a decision and explain why in `notes`. Mark `reviewable=no` only for a real display/packet defect; explain it.
9. Return the two exported response JSONL files and signed declaration to the study custodian. Do not edit your responses after return unless a correction is separately versioned.

The packet contains research exam cases and generated text. Store it privately and do not upload it to Git or a public service. Do not give clinical advice based on the material.

Your response is not an overall quality score. A complete supported pair is derived later: both views must preserve supported C1–C4 and contain no unsupported, contradicted or unresolved additions.
