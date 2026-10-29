# Step 4 — Diagnostic CDSS Research Protocol

**Thesis:** A Trustworthy & Explainable AI Framework for Large Language Model-Based Decision Support Systems  
**Student:** Spandan Kumar Gope · 22MIP10039 · VIT Bhopal  
**Supervisor:** Dr. Rajit Nair  
**Version:** Clinical 1.0 · 27 October 2026  
**Status:** Measured feasibility gates passed; application and thesis experiments not yet implemented

## 1. Confirmed application and research question

The application is a Healthcare Clinical Decision Support System research prototype. Its primary task is **most-likely-diagnosis selection from four supplied clinical options**, using an exam-style clinical vignette. It will present a recorded model suggestion, the source case findings, measured input-omission observations and two audience explanations in a ChatGPT/Codex-inspired conversation interface. The approved broad thesis title is retained.

The research question is whether typed, source-bound behavioral evidence, a shared claim plan and final-text checking/repair improve supported explanations compared with matched grounded prompting. The study measures preservation of recorded model behavior. Agreement with a benchmark diagnosis and preservation of an explanation's evidence are separate outcomes. A medically wrong model choice can have an accurately reported audit; report results separately for correct and incorrect choices.

The validated task uses supplied candidate options. Unrestricted differential-diagnosis generation, treatment recommendations, patient outcomes, live EHR integration and clinical deployment are not established by this experiment. The intended interface shows model suggestions and review status; it does not invent a calibrated confidence percentage. Any human-understanding or clinical-utility claim requires a separate actual study.

The user confirmed local-only execution without GPT/Gemini API access or budget. These providers have no executed results. TRUSTXAI is a framework rather than a competing foundation model. Its primary comparison holds the decision and communication models fixed and changes the explanation/checking procedure.

## 2. Dataset provenance and task-specific cohort

MedQA was introduced by Jin et al., *What Disease Does This Patient Have? A Large-Scale Open Domain Question Answering Dataset from Medical Exams*. The 2020 arXiv manuscript 2009.13081 was inspected; publication metadata for Applied Sciences 2021, DOI 10.3390/app11146421, was independently verified. The original task mixes short knowledge questions and clinical vignettes, so the entire benchmark is not labelled a diagnosis-only patient cohort.

The author repository is https://github.com/jind11/MedQA, code revision 27b02f66aac217933c9648a06f82e9f720377925. Its Git tree contains code/documentation; its README links the question corpus externally. Question files here were retrieved from the explicitly identified public mirror https://huggingface.co/datasets/GBaker/MedQA-USMLE-4-options at revision 0fb93dd23a7339b6dcd27e241cb9b5eca62d4d18. This mirror is not represented as the original author release.

Actual files contain 10,178 training and 1,273 test questions, matching the original paper's train/test counts. The author's separate 1,272-question development partition is not supplied by this mirror; our research development sample is drawn from the training file. The mirror card declares CC BY 4.0, while the author code repository has an MIT software licence. These declarations have different scopes. Preserve notices and citations; raw exam text and the optional research-only textbook corpus are not redistributed in the public pack. The original paper's research-use-only textbook statement does not establish unrestricted textbook rights, and textbooks are not used here.

The final diagnosis-only cohort has 917 candidate training and 117 candidate test cases before grouping/eligibility. After archived exploratory sources and declared budgets are excluded, 877 training and 117 test cases remain. The final grouping found 0 exact repeats and 0 near-duplicate edges, with 0 cross-partition cases quarantined. The 24/40/60 manifest has no overlapping source components. Maximum selected task prompt: 552 tokens; cap: 1,536. Manifest SHA256: 730d9ecfa80b04f5bc466f74d9750a5be08c35c029dc32c63ee21d11f4e70bff. All these operations preceded primary feasibility predictions.

Only the clinical case spans, the diagnostic question and all four candidate options enter inference prompts. The fields answer, answer_idx, meta_info and metamap_phrases are excluded by an explicit projection. An injected-sentinel check verifies that these excluded fields cannot enter a model request. Providing all candidate answers is the normal multiple-choice task; the correct-option identity is withheld. Gold labels are loaded for metrics after predictions have been saved.

Clinical eligibility uses a patient/age cue and a positive grammatical request for the most likely/probable diagnosis. Procedural, treatment, mechanism, pathology-feature and supporting-finding questions are excluded. The query ends at its question mark; any subsequent laboratory table remains clinical case evidence. The case is split into sentence-like contiguous source spans, short fragments are merged, and longer cases are merged deterministically to at most eight spans. All clinical text is preserved; no token truncation is used. Span offsets bind to the normalized source question. These units are input spans, not medically certified atomic findings.

## 3. Source partitions and scope corrections

| Research pool | Sources | Correct-option positions | Source partition and purpose |
| --- | --- | --- | --- |
| Feasibility | 24 | 6 each, A–D | Training file; model/resource/format suitability only. |
| Development | 40 | 10 each, A–D | Training file; prompts, rubric, diagnostics and checker thresholds. |
| Test | 60 | 15 each, A–D | Published test file; frozen Phase I pilot comparisons. |

Sampling uses seed 20261027 and source-component separation. Exact question and near-duplicate text groups do not cross research pools. The balance concerns **answer positions, not disease classes**. Letter macro-F1, balanced accuracy and recall diagnose option bias; they are not disease-specific clinical adequacy metrics. This 60-case subset is not the complete MedQA test and cannot be compared directly with full-benchmark leaderboard accuracy. No guarantee of absence from model pretraining is made.

The first exploratory keyword cohort mixed diagnosis, workup and mechanism questions; its 16/24 result is archived and is not the primary diagnosis-only result. A subsequent query audit still found non-diagnosis requests, and that partial attempt was stopped without a completed quality assessment. All 48 sources from these exploratory selections are excluded from the new feasibility/development pools. These corrections were based on question semantics, with no final-test predictions available. Source manifests, partial attempts and reasons are retained. PubMedQA and SMS work remain separate supporting/historical tasks and their scores do not transfer to clinical diagnosis.

The current test is allocated but **not yet locked**: final development prompts, annotation rubric and thresholds remain unfinished. Cohort/prompt hashes are recorded before primary feasibility inference. Changing dataset membership in response to final-test outcomes is not permitted by this protocol.

## 4. Selected local model profiles and measured gates

The selected fixed target is **Qwen/Qwen3-4B-Instruct-2507**, revision cdbee75f17c01a7cc42f958dc650907174af0554, CPU FP32 with four threads. Its primary diagnosis-only feasibility pool has 24 fresh cases, six per correct option position, disjoint from all 48 archived exploratory selections. It returned **16/24 correct (66.7%)**, option-position macro-F1 **0.6702**, and 24/24 valid letters. Median response: **12.12 seconds**; peak RSS: **18.91 GiB**. Position recalls A/B/C/D are 0.833, 0.667, 0.500, 0.667. This is operational feasibility, not final-test accuracy or clinical validation.

The communication model is **Qwen/Qwen3-1.7B-GGUF Q8_0**, official publisher revision 90862c4b9d2787eaed51d12237eafdfe7c5f6077, using llama-cpp-python 0.3.16 on CPU with two decode and four prefill threads. Exact published artifact SHA256 is recorded; its original conversion commit is not established. The reference tokenizer was checked for exact native token IDs, and each actual generation also checks them. Models and roles are separated; communication does not change the frozen target decision.

On the fixed eight feasibility cases, 16 preselected omissions were evaluated; 3 changed the model answer and 8/8 selected-result rechecks agreed. Informative evidence was available for 8/8 cases. Joint JSON was valid for **8/8** requested pairs; median generation was **19.77 seconds**, with native-phase peak RSS **2.39 GiB**. These measurements cover runtime and format. They do not establish that every generated sentence preserves its evidence. No repair, independent semantic audit, H1/H2/H3 comparison or final-test inference has run.

The fixed target uses a pinned Qwen3-4B-Instruct-2507 model, greedy no-thinking generation and at most eight new tokens. After whitespace stripping and uppercase normalization, only exact A/B/C/D is valid. Invalid answers remain in the denominator, count incorrect and receive no silent likelihood fallback or decision repair.

CPU hardware changed after an environment restart: the current machine exposes AVX2 but not AVX512-BF16. A BF16 attempt was stopped after very slow preliminary queries. The selected profile must therefore be measured on this actual machine rather than inheriting earlier timing results. Target evidence extraction and audience communication run in separate phases to control memory. The MacBook Air M5 is user-reported; its RAM, MPS compatibility and performance have not been inspected.

The operational floors were declared before primary clinical inference: option-selection accuracy/balanced accuracy at least 0.50; option-position macro-F1 at least 0.40; positive recall for every position; valid decisions at least 0.95; median target response at most 20 seconds; peak RSS at most 24 GiB. The eight-case rendering test requires valid joint JSON at least 0.80 and median joint generation at most 180 seconds. Projected fixed workload must fit 24 aggregate process CPU-hours. These are feasibility gates, not clinical safety or significance claims.

## 5. Recorded decision and bounded omission evidence

Freeze the model decision for the exact case, option ordering, prompt, model revision and decoding profile. Each source case span has an S1/S2/... identifier. Omit one span while preserving the diagnostic question, all options and remaining span identities; query the same target afresh. Store the original and modified input hashes, observed labels, invalid responses and resource measurements.

For the feasibility rendering pilot, test only the preselected first and last spans, independently of model correctness. The canonical explanation states the actual tested count out of the available spans. This is a resource/format probe, not a complete all-span sensitivity experiment. The later full pipeline tests every eligible span, up to eight.

Among valid answer-changing omissions select the shortest omitted span by characters, earliest index on ties. If none changes the answer, select the shortest valid nonflip. Repeat the selected modified input uncached and record agreement. Report all option transitions and any-label changes; a four-way choice has no unique opposite class. A nonflip is useful observed evidence, but it does not establish global robustness.

These are input-removal tests. They do not simulate a medically plausible patient intervention, prove causation or expose complete internal reasoning. A source span may contain several findings. No generated medical fact is inserted to create a counterfactual. Minimum informative evidence requires a valid original answer, at least one valid omission result and an agreeing recheck. Unresolved/status-only cases remain in the all-requested-source denominator.

## 6. Shared claim plan, checking and repair

The canonical plan contains four essential facts: C1, the recorded option and exact source option name with its model-status qualification; C2, the selected omitted-span identity and original/modified answers; C3, attempted/available spans, valid outputs, answer changes and recheck status; C4, limits on clinical causation, untested edits and internal reasoning. Both audience views preserve all four. Case findings appear separately so the narrative need not invent clinical justifications.

Generate one JSON object with novice/expert objects, each containing C1–C4 text strings, at most 384 new tokens. Generated field names are not proof. Structural checks must validate case/model binding, source option names, labels, counts, span identity, recheck status and required limitations, and inspect extra clauses within correctly linked fields.

A pinned DeBERTa NLI model supplies fallible support and coverage checks, alongside deterministic guards. Its native mapping is contradiction/entailment/neutral = 0/1/2. Its existing four synthetic plumbing examples establish neither biomedical accuracy nor checker reliability. A claim can be medically true in general yet unsupported by the stored evidence; this study's support endpoint concerns the declared evidence contract.

NLI inputs are limited to 512 tokens without truncation. At most 32 rendered-clause support checks plus eight coverage checks are allowed per pair; overlong/unresolved inputs are blocked. Cache only exact model-input token pairs with the frozen model signature. Case/provenance guards still run for every record; target consistency queries remain uncached.

Develop thresholds on 40 sources using controlled positives/faults and independently reviewed labels. Use the grid 0.60, 0.70, 0.80, 0.90, 0.95 and select the most selective setting retaining at least 90% of supported development variants. H2 compares typed checks plus NLI with NLI-only using the same scores. If the acceptance target cannot be reached, report that instead of asserting matched acceptance.

Allow one joint feedback-guided repair, capped at 384 tokens, then rerun complete checks. Otherwise show a labelled deterministic evidence template. A fallback can be useful system output but is not successful LLM narrative generation. No checker, repair or semantic-preservation experiment has been completed by a JSON/runtime feasibility test.

## 7. Baselines, reuse and fair accounting

| Condition | Procedure | Maximum narrative calls per source |
| --- | --- | --- |
| B0 | Frozen-decision explanation without audit evidence; contextual lower baseline. | 1 |
| B1 | Grounded initial pair and one blind second draft; use second, no best-of selection. | 2 |
| B2 | Initial pair plus omission-span feedback rewrite; explicit adaptation of prior refinement. | 2 |
| B3 | Generic evidence-aware critic/gate and at most one repair. | 2 plus one critic |
| B4 | Deterministic audience templates with the same evidence and limits. | 0 |
| P | Typed plan, structural/NLI checks, one repair and labelled fallback. | 2 |

Primary comparison: P versus B1 on all 60 requested sources. B1/B2/B3/P share one immutable initial pair only when their complete prompts, evidence, model and greedy settings match exactly. This gives at most six physical joint generations per test source while retaining nine logical opportunities across conditions. Charge the common initial cost to each condition in standalone comparisons; separately report whole-matrix shared cost. The initial plan itself is not credited as the causal advantage in this matched comparison.

Gating alone cannot improve independently assessed complete supported LLM-pair yield. Any improvement must arise from better output or successful repair; rejecting correct pairs can reduce yield. Reuse P's recorded initial output for its no-repair ablation. Baselines adapted to the local models and omission spans are not claimed exact reproductions of SR-NLE, Cross-Refine, FaithLM or the base papers.

## 8. Diagnostics and independent semantic audit

Plan four supported and eight faulty joint-pair variants per development/test source: 480 development and 720 test variants. Faults cover the original option/name, omitted-span binding, changed-answer result, test/flip counts, recheck status, generalization to all interventions, an unsupported clinical clause and a missing limitation. These counts are planned. If source evidence cannot instantiate a diagnostic, record the missing slot rather than inventing observations.

The NLI-only H2 ablation reuses scores. The general LLM critic is retained for natural-output B3; develop it on the 40 initial development pairs and run it on 60 test cases, rather than generating a critic verdict for every diagnostic. Its output cap is 96 tokens. Its score is not independent truth.

The six-condition natural matrix plans 720 view slots, including explicit failures and templates. Two actual independent annotators should judge the frozen evidence-based rubric, one possibly the researcher, with author involvement and possible style-based unblinding disclosed. No annotator or clinical expert has been recruited. If independent annotation is unavailable, label results single-rater/automated and do not claim completed independent validation. The optional audience-understanding/appropriate-reliance study remains conditional Phase II work.

## 9. Endpoints and statistical plan

H1 is **complete supported LLM narrative-pair yield** over all 60 requested sources: both audience narratives preserve mandatory evidence without unsupported additions. Missing, unparseable, blocked, status-only and fallback pairs fail this endpoint. The primary paired difference is P minus B1, with two-sided exact McNemar/binomial inference on discordant source outcomes, alpha 0.05, and a 95% paired source-bootstrap interval using 5,000 replicates stratified by correct option position, seed 20261027.

B4 has no LLM generation, so its LLM narrative yield is not applicable. Report its semantic output coverage, cost and any actual user evaluation as a strong comparator. Also report complete supported system-output coverage including P's labelled templates, with informative-evidence requirements retained. This prevents an always-abstain system from appearing successful and avoids treating a template fallback as generated narrative success.

H2 measures false acceptance of faulty variants, false rejection of supported variants, achieved supported acceptance and abstention; bootstrap by source. H3 measures the paired before/after-repair change and extra cost. Use Holm adjustment for formal secondary H2/H3 tests, without a power guarantee for n = 60.

Report required-fact recall, extra claims, scope drift, initial/final failures, evidence availability, narrative/fallback coverage, option-selection accuracy and letter-bias controls, outcomes split by correct/incorrect target, omission transitions/retest agreement, tokens, CPU time, elapsed time and peak RSS. Views, claims and related diagnostic variants are not extra independent source observations. No final-test outcome may tune a prompt, threshold, model or sample membership.

## 10. Resource budget, interface and next stage

The fixed workload estimates evidence for 40 development plus 60 test cases, at most 400 unique joint narrative generations after exact shared-initial reuse, 100 natural-output critic calls, 1,200 diagnostic pairs and up to 160 natural P/development check pairs. Exact NLI-input keys were counted on 96 unreviewed cost-layout variants derived from the eight feasibility records; they are not semantically labelled diagnostic results. No cross-source cache benefit is assumed. Original-query mean cost is used as a floor for omitted/rechecked queries.

The measured-cost projection is **21.10 aggregate process CPU-hours**, including 25% headroom; estimated elapsed time is **7.32 hours**. The 24-CPU-hour expected-cost gate passed: **True**. This is a projection, not an executed matrix. An uncached full-output/full-context stress scenario is **77.86 CPU-hours**, so the budget is not a worst-case guarantee. A changed diagnostic layout requires a fresh projection. Checkpoint before the ceiling, preserve pending cases and document any allocation change; do not drop hard cases. Extra exploratory tuning and human annotation are outside this fixed-workload estimate and must be logged separately.

The interface requirement is recorded in design/UI_REQUIREMENTS.md: a ChatGPT/Codex-inspired sidebar, central conversation, rounded composer, light/dark themes and an expandable evidence pane, with TRUSTXAI branding. Ordinary explanations remain readable; source hashes, claim IDs and runtime details belong in the technical audit. Existing cases and model outputs stay bound to immutable inputs; editing creates a new case version.

Before final-test inference, freeze source/model revisions, artifact hashes, prompts, schema, rubric, thresholds, seeds and package versions. Raw cases and generated text remain outside Git. Public artifacts contain retrieval instructions, source IDs/hashes, measurements and scripts. No final test, six-condition study, independent semantic annotation, clinical benefit assessment, final paper or Review 2 slides have yet been completed.

Step 5 implements the application and full evidence/checker/repair pipeline. Develop on 40 sources, finish annotation/rubric/threshold work, then lock the 60-case test. Review 2 is 18–20 November 2026; the Phase I report deadline is before 25 November. The current deliverable is a protocol and measured feasibility record, not a completed research paper or a guarantee of publication or grades.
