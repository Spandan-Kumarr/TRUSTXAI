# Step 6 — Frozen computational evaluation

Step 6 executed the prespecified 40-source development and 60-source held-out MedQA study for the local diagnostic decision-support prototype. Raw cases, prompts, generations, checker rows, gold labels and blinded annotation packets remain under `/workspace/thesis-runtime`; this Git-facing directory contains code, hashes, aggregate measurements and no raw exam text.

The immutable held-out freeze is `STEP_06_FREEZE.json`, SHA-256 `10beddd73bf032819310d9bf2924dbfbffde580b835f6509f205b2c651120518`. It fixes the source manifests, local models, prompts, code, checker grid, 0.60 pre-test fallback deviation, seed, 2048-token research context and six-condition matrix before test access.

## Main computational results

| Measure | Development | Held-out test |
| --- | ---: | ---: |
| Sources | 40 | 60 |
| Correct target decisions | 29 (72.50%) | 47 (78.33%) |
| Valid target decisions | 40/40 | 60/60 |
| Option-position macro-F1 | 0.7171 | 0.7865 |
| Informative omission evidence | 40/40 | 60/60 |
| Omission queries | 286 | 407 |
| Answer-changing omissions | 35 | 54 |
| Sources with any answer change | 19 | 32 |
| Selected-result recheck agreement | 40/40 | 60/60 |
| Controlled diagnostic slots | 480 | 720 |
| Natural logical rows scored | 280 | 420 |

The checker calibration target failed. At each prespecified threshold (0.60, 0.70, 0.80, 0.90 and 0.95), typed-plus-NLI accepted 0/160 supported-intent development variants. The pre-test deviation therefore used the least selective grid value, 0.60, while explicitly recording that the ≥90% target was not met. On held-out controls, both typed-plus-NLI and NLI-only rejected all 240 supported-intent variants and all 480 faulty-intent variants: false acceptance 0%, false rejection 100%.

The automated natural-output proxy accepted no B1 or P pair on either split. P used its labelled evidence-template fallback for 40/40 development and 60/60 test sources. This establishes a severe checker-coverage failure; it does not establish explanation superiority or inferiority. Formal pair support needs the independent annotation workflow.

## Status boundary

- Computational execution, immutable freeze, gold-safe scoring, aggregate analysis, 5,000-replicate stratified bootstrap, exact McNemar implementation, manifests and blinded packet construction are complete.
- Development and test annotation packets contain 596 and 896 blinded review items per rater respectively. Separate Rater A and Rater B archives, offline forms, instructions, declarations and response templates are ready outside Git. They contain no responses.
- `scripts/process_annotations.py` validates two distinct complete response sets, records pre-adjudication agreement, creates a disagreement queue, locks adjudication and emits analyzer-ready labels without using construction intent as semantic truth.
- Formal H1/H2/H3 require two actual independent raters, agreement calculation and adjudication. Those judgments were not fabricated.
- The optional audience study, clinical expert validation, patient outcomes, live deployment and GPT/Gemini API comparisons were not run.
- Research-paper writing is waiting for the formal annotation result, in the sequence requested by the user. The Review 2 presentation remains deferred until after supervisor review of the paper.

See `STEP_06_DELIVERY.md` for the execution record, `annotation/RATER_WORKFLOW.md` for the exact external workflow and `VALIDATION_AND_STATUS.json` for machine-readable status.
