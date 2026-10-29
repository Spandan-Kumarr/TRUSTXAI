# Step 6 delivery record

**Thesis:** A Trustworthy & Explainable AI Framework for Large Language Model-Based Decision Support Systems  
**Application:** local diagnostic clinical decision-support research prototype  
**Execution completed:** 29 October 2026 (Asia/Kolkata)  
**Scope:** all computational work before paper and Review 2 presentation

## What was executed

The study used the fixed 40-source development and 60-source held-out partitions. Inference inputs contained only the clinical question, two-to-eight source spans and four candidate diagnoses. Gold answer fields were released only after evidence, matrix, controlled diagnostics and natural diagnostics were complete and bound by an immutable prediction digest.

For every source, the target model recorded its option, queried every one-span omission and repeated the selected omission uncached. The six-condition matrix executed B0, B1, B2, B3, B4 and P. B1/B2/B3/P shared one exact initial generation; physical narrative calls were capped at six per source. P allowed one repair and then a labelled evidence template. A template did not count as LLM narrative success.

The development run completed 40 evidence and 40 matrix checkpoints. Calibration scored 480 requested controlled slots. No grid threshold retained the required 90% supported-intent acceptance; all retained 0%. A pre-test deviation fixed 0.60, the least selective prespecified value, without claiming target attainment. The immutable test freeze was then created and verified at SHA-256 `10beddd73bf032819310d9bf2924dbfbffde580b835f6509f205b2c651120518`.

The held-out run completed 60 evidence checkpoints, 60 matrix checkpoints, 720 controlled slots and 420 natural logical rows. Its prediction freeze bound all four artifact families before gold release. Aggregate process CPU was approximately 22.19 hours across runner and diagnostic stages, within the refreshed 24-hour allocation. The matrix used 582 physical narrative calls and 100 critic calls over both splits.

## Results that can be reported

The held-out target selected the benchmark option correctly for 47/60 sources (78.33%). Balanced accuracy was 0.7833, option-position macro-F1 0.7865 and valid-output rate 100%. Recalls by correct option position A/B/C/D were 0.8667/0.8667/0.6667/0.7333. These are option-position controls on a 60-case diagnosis subset, not disease-class clinical validation or a full MedQA leaderboard score.

All 60 test sources met the informative-evidence rule. The run recorded 407 valid omission labels, 54 answer changes across 32 sources and 60/60 selected-result recheck agreements. These are input-removal observations; they do not prove clinical causation or reveal complete internal reasoning.

The automated explanation checker failed its supported-output coverage target. On held-out controlled variants, typed-plus-NLI and NLI-only each rejected all 240 supported-intent and all 480 faulty-intent slots. On natural outputs, the automated proxy accepted 0/60 B1 pairs and 0/60 P pairs. P fell back to a deterministic evidence template for all 60 held-out sources. H1 automated difference was 0.0 with exact McNemar p=1.0 and stratified bootstrap 95% interval [0.0, 0.0]. This proxy result reflects the checker's extreme false-rejection behavior and cannot substitute for semantic human judgments.

## Work requiring real people

The prepared private packets and public manifests support two blinded independent raters, agreement measurement and adjudication. Formal H1/H2/H3 are deliberately marked `not_run_requires_two_independent_raters` until those response files are complete and locked. Development and test packets contain 596 and 896 unique review items. No rater response, clinical-expert judgment, participant outcome or ethics/consent determination was invented.

Two separate private distribution ZIPs are ready under `/workspace/thesis-runtime/clinical-cdss/step-06/rater-distribution`. Each contains only that rater's blinded assignment, the frozen rubric/protocol, a declaration and a self-contained offline form with save/resume and validated JSONL export. The public distribution manifest records archive and packet hashes. `scripts/process_annotations.py` is the fail-closed custody boundary: it verifies packet, schema, declaration and response hashes; rejects incomplete or same-identity submissions; records agreement before unblinding; requires a separate complete adjudication record; persists the annotation lock; and emits canonical natural and controlled semantic labels for `analyze_results.py`.

The optional audience-understanding study, clinical utility/safety evaluation, GPT/Gemini comparison and deployment evaluation remain outside the completed computational scope. These limitations must remain visible in the paper and presentation.

## Validation and deliverables

- 195 backend/research tests pass, including ten annotation-distribution and response-lock tests added after the frozen held-out run. These workflow-only additions did not alter frozen inference or diagnostic artifacts.
- The final frontend production build passed and all four Playwright browser tests passed.
- The test freeze verified its checksum and code/artifact hashes.
- Public manifests reject raw-text keys and contain aggregate counts/hashes only.
- Private checkpoint and packet files stay outside Git under `/workspace/thesis-runtime`.
- `STEP_06_EVALUATION_PACK.zip` contains the public Step 6 record and no private runtime text.
- The research paper has not been written because the requested sequence places it after complete research; formal semantic results still require two real raters. The Review 2 presentation remains deferred until after supervisor review of that paper.
