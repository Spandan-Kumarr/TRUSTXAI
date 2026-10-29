# Step 4 — Clinical Feasibility Report

**TRUSTXAI · Spandan Kumar Gope · 22MIP10039**  
**27 October 2026 · Clinical 1.0**  
**Status:** Measured feasibility gates passed; application and thesis experiments not yet implemented.

## What was actually tested

The confirmed application is a diagnostic Clinical Decision Support System research prototype with a ChatGPT/Codex-inspired interface. The benchmark task selects the most likely diagnosis from four supplied options. An exam-vignette benchmark is not real-patient clinical validation. The user confirmed no API access/budget; no GPT/Gemini outputs or comparison results exist.

The primary diagnosis-only cohort was refined by question semantics before its predictions. Two exploratory selections are archived. The final 24-case feasibility pool excludes all 48 earlier source IDs. The old broader-cohort 16/24 score and the primary 16/24 score belong to different samples and must not be pooled or treated as replicated final-test performance.

The final diagnosis-only cohort has 917 candidate training and 117 candidate test cases before grouping/eligibility. After archived exploratory sources and declared budgets are excluded, 877 training and 117 test cases remain. The final grouping found 0 exact repeats and 0 near-duplicate edges, with 0 cross-partition cases quarantined. The 24/40/60 manifest has no overlapping source components. Maximum selected task prompt: 552 tokens; cap: 1,536. Manifest SHA256: 730d9ecfa80b04f5bc466f74d9750a5be08c35c029dc32c63ee21d11f4e70bff. All these operations preceded primary feasibility predictions.

## Observed gates

| Check | Required | Actual observation |
| --- | --- | --- |
| Diagnostic-option accuracy | At least 0.50 on 24 sources | 16/24 = 0.667 |
| Position macro-F1 | At least 0.40; all positions nonzero recall | 0.6702; all positive |
| Valid answer letters | At least 95% | 100% |
| Median target response | At most 20 seconds | 12.12 seconds |
| Joint JSON format | At least 80% on 8 requested sources | 8/8 = 1.000 |
| Median pair generation | At most 180 seconds | 19.77 seconds |
| Peak inference RSS | At most 24 GiB | 18.91 GiB across separately loaded phases |
| Projected fixed workload | At most 24 aggregate CPU-hours | 21.10 CPU-hours with headroom |

The selected fixed target is **Qwen/Qwen3-4B-Instruct-2507**, revision cdbee75f17c01a7cc42f958dc650907174af0554, CPU FP32 with four threads. Its primary diagnosis-only feasibility pool has 24 fresh cases, six per correct option position, disjoint from all 48 archived exploratory selections. It returned **16/24 correct (66.7%)**, option-position macro-F1 **0.6702**, and 24/24 valid letters. Median response: **12.12 seconds**; peak RSS: **18.91 GiB**. Position recalls A/B/C/D are 0.833, 0.667, 0.500, 0.667. This is operational feasibility, not final-test accuracy or clinical validation.

The communication model is **Qwen/Qwen3-1.7B-GGUF Q8_0**, official publisher revision 90862c4b9d2787eaed51d12237eafdfe7c5f6077, using llama-cpp-python 0.3.16 on CPU with two decode and four prefill threads. Exact published artifact SHA256 is recorded; its original conversion commit is not established. The reference tokenizer was checked for exact native token IDs, and each actual generation also checks them. Models and roles are separated; communication does not change the frozen target decision.

On the fixed eight feasibility cases, 16 preselected omissions were evaluated; 3 changed the model answer and 8/8 selected-result rechecks agreed. Informative evidence was available for 8/8 cases. Joint JSON was valid for **8/8** requested pairs; median generation was **19.77 seconds**, with native-phase peak RSS **2.39 GiB**. These measurements cover runtime and format. They do not establish that every generated sentence preserves its evidence. No repair, independent semantic audit, H1/H2/H3 comparison or final-test inference has run.

## Hardware and failed attempts

The cloud restarted during this work. The current CPU has AVX2 without AVX512-BF16; preliminary BF16 clinical queries took 65–77 seconds and that incomplete profile was stopped. The selected target uses FP32. A native Q8 communication model was built from pinned public source for CPU compatibility; no TLS, source hash or model-integrity check was disabled. Target and communication run in separate phases, rather than claiming a measured simultaneous-memory figure. The user's MacBook Air M5 was not benchmarked.

The original diagnosis-keyword filter admitted workup, mechanism and treatment questions. Manual question review corrected this with positive diagnostic-request grammar, and laboratory tables after a question were moved into case evidence. These are disclosed scope/input corrections, not exclusions based on final-test outcomes. Source text, exploratory outputs and manifests are preserved outside the active protocol. The final cohort/prompt hash was frozen before its primary predictions.

## Budget and next boundary

The fixed workload estimates evidence for 40 development plus 60 test cases, at most 400 unique joint narrative generations after exact shared-initial reuse, 100 natural-output critic calls, 1,200 diagnostic pairs and up to 160 natural P/development check pairs. Exact NLI-input keys were counted on 96 unreviewed cost-layout variants derived from the eight feasibility records; they are not semantically labelled diagnostic results. No cross-source cache benefit is assumed. Original-query mean cost is used as a floor for omitted/rechecked queries.

The measured-cost projection is **21.10 aggregate process CPU-hours**, including 25% headroom; estimated elapsed time is **7.32 hours**. The 24-CPU-hour expected-cost gate passed: **True**. This is a projection, not an executed matrix. An uncached full-output/full-context stress scenario is **77.86 CPU-hours**, so the budget is not a worst-case guarantee. A changed diagnostic layout requires a fresh projection. Checkpoint before the ceiling, preserve pending cases and document any allocation change; do not drop hard cases. Extra exploratory tuning and human annotation are outside this fixed-workload estimate and must be logged separately.

All observed feasibility gates passed: **True**. Neither the JSON parser nor the native tokenizer probe establishes semantic explanation correctness. There are zero development/test target predictions, zero completed six-condition thesis comparisons and zero recruited independent annotators. Medical effectiveness, calibrated confidence, patient benefit and superiority over GPT/Gemini have not been established.

The strongest planned comparison uses the same target, communicator and shared initial pair for grounded blind rewrite versus TRUSTXAI checking/repair. Independent evidence-based labels are still needed. Templates are a strong semantic-output comparator; their LLM-generation yield is not applicable, and a template fallback is not counted as successful generated narrative.

Step 5 implements the actual application, full all-span evidence pipeline, checkers, repair and baseline adapters. The design brief specifies a sidebar, conversation, rounded composer, light/dark themes and an evidence drawer. Application code, a final research paper and Review 2 slides are not represented as completed by this report.
