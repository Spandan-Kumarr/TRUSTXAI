> SUPERSEDED SMS DOCUMENT —27October2026: user requested healthcare. Earlier network blocker is resolved. Read healthcare-scope/HEALTHCARE_DIRECTION.md and current VALIDATION_AND_STATUS.json. This historical text is not the healthcare protocol.

# Step 4 — Task, Model and Experiment Protocol

**Project:** TRUSTXAI · Spandan Kumar Gope · 22MIP10039  
**Supervisor:** Dr. Rajit Nair  
**Prepared:** 27 October 2026 · Version 1.1  
**Status:** Data, model metadata and tokenizer verified; model-weight delivery and inference feasibility pending. No thesis experiment has run.

## 1. Selected study and resource boundary

The primary study is **SMS spam triage**: a prompted generative LLM classifies a public benchmark message as ham or spam. The application explains that recorded model decision to a general user and a technical reviewer. This is an offline research support workflow, not a live inbox integration or automatic deletion system. The approved thesis title is unchanged.

The accessible cloud machine has approximately 33 GiB RAM, five reported CPUs, about 30 GiB free disk, Python 3.12.14 and no visible CUDA GPU or nvidia-smi executable. This is the actual machine available to our tools. The student reports a MacBook Air M5; its RAM, MPS compatibility and inference speed have not been inspected. It is an optional future local environment, not an assumed cloud GPU or a prerequisite for the plan. No paid API or Colab account is required by this design.

CPU libraries have been installed in /workspace/thesis-runtime/venv. Imports of PyTorch, the Qwen2 architecture and the Transformers sequence-classification interface pass. This does not establish that the selected weights load or perform well. Hugging Face metadata/model cards and UCI data now return successful responses. Weight files redirect to us.aws.cdn.hf.co, which still returns proxy-policy 403. That exact additional host is saved in a new draft; saving did not apply or publish it. A stalled zero-byte weight transfer was stopped without using incomplete artifacts.

## 2. Why this task and dataset

| Candidate | Strength | Reason for present decision |
| --- | --- | --- |
| SMS spam triage | Short inputs; clear support workflow; manageable local perturbation costs. | Primary task; official archive and catalogue licence now verified. |
| Movie sentiment / ERASER | Strong connection to the base-paper literature and rationale annotations. | Reserve expansion; human rationales still are not target-LLM evidence, and decision-support context is less direct. |
| e-SNLI | Human explanations and many relevant method comparisons. | Reserve expansion; premise/hypothesis scope and multi-class explanation obligations add complexity. |
| Contract or clinical decisions | Potentially meaningful expert support tasks. | Domain expertise, study burden, document length and consequences exceed the initial CPU pilot scope. |

**Selected source:** UCI Machine Learning Repository, SMS Spam Collection, dataset ID 228. Primary metadata endpoint: https://archive.ics.uci.edu/api/dataset?id=228. Expected archive: https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip. The official archive has now been retrieved and hashed: 5, 574 records, 4, 827 ham and 747 spam, no malformed records. The current dataset page explicitly states CC BY 4.0; preserve attribution and the original archive copyright/disclaimer. Dataset DOI: 10.24432/C5CC84. Cite Almeida, Gómez Hidalgo and Yamakami, 2011, Contributions to the study of SMS spam filtering: new collection and results, DOI10.1145/2034691.2034742. No mirror was used.

If licence or source verification fails, do not silently substitute a scraped corpus. Record the issue and revise this protocol before sampling or testing. The task selection is a resource-justified research choice, not evidence that SMS classification is itself new or that this dataset has never appeared in pretraining.

## 3. Data preparation and source-level splits

Keep original data local outside the Git checkout; commit retrieval instructions, hashes and split manifests rather than raw messages. Public messages may contain identifiers; use clearly labelled synthetic/redacted examples for public screenshots, and re-run predictions if an input is changed. An explanation of the original message cannot be attached to a modified demo input as if it were the same case.

Preparation order, before model outcomes are inspected:

1. Download from the verified primary source, preserve bytes and record SHA-256, metadata and licence.
2. Parse labels and messages; retain original text and stable source identifiers. Reject malformed records with explicit counts.
3. Group normalized exact duplicates using Unicode NFC, case-folding and collapsed whitespace, while retaining original inference text. Quarantine conflicting-label exact or near-connected groups and report them. This clarification was made before model outcome inspection; neither kind was found in the retrieved corpus.
4. Cluster near duplicates by word-set Jaccard similarity at least 0.90 using connected components; do not split a component across study partitions. This guards against repeated short templates, but does not prove absence of all semantic overlap. It is an unsupervised corpus check, not model-outcome selection.
5. Eligible inputs contain 8–60 whitespace-delimited spans and fit within the chosen tokenizer's 256-token message budget without truncation. Report exclusions and the resulting length/class distribution. The study population is bounded short messages, not all SMS traffic.
6. Assign whole components to disjoint feasibility, development and test pools with seed 20261027, stratified by ham/spam where feasible. Select one representative per component before prediction. If the required distinct groups are unavailable, amend counts before final inference rather than relaxing leakage rules silently.
7. Publish hashed manifests and aggregate counts. All variants, counterfactuals and diagnostics inherit their parent source split.

| Partition | Planned sources | Per class | Permitted use |
| --- | --- | --- | --- |
| Feasibility | 20 | 10 ham, 10 spam | Load/latency, prompt format and model suitability; never final-test evidence. |
| Development | 40 | 20 ham, 20 spam | Prompt, checker threshold and rubric development. |
| Locked test | 60 | 30 ham, 30 spam | Prespecified Phase I pilot comparisons; no tuning on these outcomes. |

The balanced test supports comparisons across source classes. Its aggregate accuracy does not estimate natural spam prevalence or production performance. Report per-class results, macro-F1 and balanced accuracy. Executed preparation found 5, 159 normalized exact groups (415 repeated rows collapsed), 56 near-duplicate edges and 5, 109 near components. After word/token budgets, 3, 696 eligible independent groups remain: 3, 114 ham and 582 spam. The20/40/60 balanced source manifests have no cross-partition group overlap. The manifest hash is retained; no test source has been scored by the model. The corpus is not used to fine-tune the target LLM. No guarantee of unseen pretraining data is made.

This is a **60-source Phase I pilot**, not a power-guaranteed definitive study. A larger, separately declared Phase II cohort can improve precision and external validity. Do not combine exploratory later samples with the original test without labelling the change.

## 4. Model selection and activation gates

| Role | Selected candidate | Operating profile and verification |
| --- | --- | --- |
| Target and communication LLM | Qwen/Qwen2.5-1.5B-Instruct | Local CPU FP32; separate prompts/roles; one loaded model can serve both. Card, Apache 2.0 licence and revision verified; weight delivery blocked. |
| Prespecified smaller fallback | Qwen/Qwen2.5-0.5B-Instruct | Use only if the feasibility gates fail before test lock; document the chosen profile. Not an automatic post-result replacement. |
| Semantic entailment checker | cross-encoder/nli-deberta-v3-base | CPU sequence classifier for sentence support/coverage; verify repository, licence, revision and label mapping before use. NLI predictions are fallible. |
| General-critic baseline | Same selected Qwen model | Evidence-aware critic prompt; shared weights disclosed; not independent ground truth. |
| Independent evaluation | Actual blinded semantic annotation plus controlled diagnostics | No invented participants or an LLM judge presented as human evidence. |

All three candidate repositories have now been verified public and ungated. Metadata access is not proof of weight access. The Qwen GitHub README URL inspected now serves Qwen3 content; it is **not** accepted as the specific Qwen2.5 model card/licence. The specific versioned Hugging Face cards have now been captured; the NLI card declares Apache 2.0 although a standalone LICENSE file was not retrieved. The older small model family is chosen for bounded resources, not claimed state of the art.

Before any final test, record exact repository revisions, weight/config/tokenizer checksums, licences and library versions. Revision fields and data hashes are now populated; checker thresholds and inference gates remain unset. Qwen1.5B revision: 989aa7980e4cf806f80c7fef2b1adb7bc71aa306; Qwen0.5B: 7ae557604adf67be50417f59c2c2f167def9a775; NLI: 6c749ce3425cd33b46d187e45b92bbf96ee12ec7. The official software runtime currently installed is PyTorch 2.8.0+cpu, Transformers 4.57.1 and huggingface_hub 0.36.0, with a full dependency freeze saved.

### Feasibility gates, checked only on the feasibility pool

- Load within a 24 GiB resident-memory budget without swapping or silent quantization.
- Verify label tokenization and exact scoring; no assumed single-token label if the tokenizer differs.
- Median target scoring at most 5 seconds for bounded prompts and median two-view generation at most 120 seconds under the stated profile.
- At least 80% valid two-view JSON on ten prespecified feasibility sources, without manually editing outputs.
- Target balanced accuracy at least 0.65 on the 20-source pool. This noisy operational check is not a significant performance claim.
- Use observed call counts/timings to estimate the full run. Do not launch an unaffordable matrix based on architecture imports alone. The initial operational ceiling is 24 CPU-hours for the planned matrix; if the measured estimate exceeds it, revise the profile or scope before test lock, without hiding quality failures.

If 1.5B is too slow but 0.5B passes all gates, activate the smaller profile before development/test lock. If quality fails, shrinking the model is not a justified quality fix: inspect prompts and tokenization using feasibility data and obtain an adequate runtime/model before claiming readiness. Log any revised gate or configuration with reasons. No final-test inference has run.

The MacBook can later be benchmarked as a separate CPU/MPS profile, with actual memory and compatible package versions recorded. Do not install Linux CPU wheels on macOS or mix CPU and MPS timings as one environment.

## 5. Exact target classifier and evidence quantity

The classification prompt defines A = ham and B = spam and quotes the message as task data. It asks for one category. A fixed chat template and assistant prefix define the scored continuation. The target is the constrained-label likelihood classifier, not unrestricted chat generation. Tokenizer-only preflight on the20 feasibility sources confirms stable prefixes, distinct single-token labels A=32/B=33, and a maximum 152-token prompt context. This validates the single-token scoring fast path for this exact prompt, not actual model scores or accuracy.

Compute the full continuation log-likelihood for A and B, using their actual token sequences; do not compare only the first token unless both are verified distinct single-token labels in that context. Choose the larger score, with the fixed tie rule A. Record both log-scores and the chosen label. Closed-set normalization is not calibrated real-world confidence.

Define spam support s(x) = log P(B | prompt(x)) minus log P(A | prompt(x)). For an explanation of ham, reverse the sign so the score always refers to the recorded decision class. Task prompt, target revision and scoring remain identical for edited inputs.

**Evidence method:** deletion-based local sensitivity. For each complete whitespace span, delete that span, normalize only the removal's boundary whitespace, and rescore. The local effect is the original decision-class log-odds score minus the score after deletion. Store exact offsets, original/edited text hashes and both scores.

A positive value means deletion reduced this decision-class score under this intervention. It is not a Shapley value, gradient attribution, causal explanation or calibrated probability effect. Deletion can produce unnatural text. Keep that limitation in the evidence and explanation plan.

Measure every eligible span, at most 60; choose the largest absolute effect with earliest-span tie-break. For display, round to four decimals. Treat absolute effects below 0.0001 as numerically near zero; do not claim direction in that case. This is a display/numerical convention, not statistical significance. Required numeric text must match the canonical rounded value and log-odds units; a 0.42 score must not become “42% certain.”

## 6. Counterfactual evidence and mandatory claims

Generate at most three distinct candidate edits per source, each with a separate recorded seed and an output limit of 96 new tokens. The requested target is the opposite label. Enforce a word-level edit-distance cap of min(6, max(1, floor(0.25 times original span count))). This is a bounded search constraint, not proof of minimum edits.

Classify each candidate by independent target scoring, not an original/edited paired yes/no judgment. Re-score the chosen candidate once without the prediction cache to check consistency. If successful, select minimum edit distance with earliest-candidate tie-break. Stop after three attempts; preserve failed and invalid attempts. Candidate generation must not change the frozen original decision.

Record desired-target success and any flip separately, although they coincide for valid binary labels in this task. Do not infer that their difference has been empirically demonstrated here. Duplicate/invalid candidates consume attempt budget. Report edit extent, observed outcomes and semantic-assessment status; a successful flip is not proof of a realistic or actionable edit.

The fixed mandatory plan contains: (1) original model decision; (2) the selected measured deletion result and its intervention scope; (3) exact tested counterfactual outcome or bounded search-failure status; (4) the limitation that these observations do not prove real-world causation, all-edit outcomes or full internal reasoning. Both audience narratives express the same facts and quantities. Technical panels may expand provenance separately.

Minimum informative evidence requires a valid target decision, at least one completed deletion test and at least one evaluated edited candidate. A status-only record or failed inference cannot count as an informative narrative success. Keep such cases in the requested-case denominator. Counterfactual success is not required for eligibility: an actual failed edit remains useful observed evidence.

## 7. Rendering and final-text checking

Use the same selected LLM for both communication roles, with CPU greedy decoding and recorded seed 20261027. Initial two-view output is one structured generation, capped at 512 new tokens. Each view contains four linked claim sentences in a fixed JSON schema. Core quantities and qualifiers are identical; audience style differs. Expert-only new narrative facts are excluded from this paired pilot.

Structural guards check input/model/class binding, exact labels, selected feature span, rounded numeric value/units, edited-input identity, required claim IDs and evidence availability. Generated IDs are not trusted proof: inspect every sentence, including extra text inside a correctly linked field.

The semantic checker uses canonical evidence sentences as premises and rendered sentences as hypotheses for support. For coverage, test whether each mandatory canonical fact is entailed by the final view. Use actual NLI configuration label names, not an assumed numeric label order. Batched CPU inference is capped at eight pairs; no silent truncation. Overlong claims are unresolved and blocked.

NLI support can miss extra clauses, scope changes or numerical errors. Deterministic guards complement it; neither is an oracle. No unsupported “confidence” or universal outcome assertion is authorized by an entailment score. Record supported, contradicted, unsupported and unresolved statuses and evaluate checker errors independently.

Threshold development uses the grid 0.60, 0.70, 0.80, 0.90, 0.95. Select the most selective setting that retains at least 90% of independently supported development variants; deterministic hard failures remain failures. Apply an analogous prespecified score threshold selection to the general critic. If a checker cannot reach the acceptance target, report that and avoid a falsely matched comparison. Scores are operating-point tools, not calibrated probabilities of truth.

Allow one joint repair using failed checks, capped at 512 new tokens, then recheck the whole pair. Release only a passing pair; otherwise show the labelled evidence template. A fallback is useful application output but not LLM narrative success. Thresholds, schema, prompts and repair settings are hashed and frozen before test generation.

## 8. Conditions and resource fairness

| ID | Condition | Planned test sources / generation policy |
| --- | --- | --- |
| B0 | Frozen-decision self-explanation without E | 60; one two-view generation; contextual lower baseline, not primary evidence of mechanism superiority. |
| B1 | Grounded prompting with E and the common plan, no final gate | 60; initial plus one blind rewrite; use the second output without checking/selecting the best. |
| B2 | Fixed-decision important-word feedback refinement | 60; initial plus one feedback-guided rewrite; deletion effects replace original paper attributions, explicitly an adaptation. |
| B3 | Generic evidence-aware critic plus repair/gate | 60; one initial pair, one critic call and at most one repair; disclose shared model weights. |
| B4 | Deterministic novice/expert templates | 60; zero narrative model calls; use the same evidence/qualifiers. |
| P | Proposed typed plan, guards, NLI checks and one repair | 60; one initial pair and at most one repair, plus logged checking. |

The primary comparison is P versus B1. B1's blind second draft controls the maximum narrative-generation opportunity without receiving checker feedback; it is still grounded prompting without a gate. Retain first drafts and report a one-draft B1 sensitivity analysis. Maximum generation calls are comparable, not necessarily equal token use or wall time; measure total cost.

**Important metric consequence:** gating alone cannot increase independently evaluated complete supported-pair yield. It can reduce unsafe releases but can also reject correct outputs. Yield improvement must come from better generation or successful repairs, not filtering away failed cases. H1 and H3 are therefore interpreted with repair and coverage results rather than attributing every effect to a checker.

For H3, reuse P's recorded initial pair and checks as the no-repair variant; no new generation or best-of selection. Shared-plan, provenance and final-check ablations are supporting diagnostics; expensive new full-matrix variants are deferred unless justified before test lock. Include a random-word feedback control on a predeclared subset if claiming important-word feedback superiority. Do not claim exact reproduction of SR-NLE, FaithLM or other papers under these adaptations.

## 9. Diagnostic construction and independent outcome audit

For each development and test source, prepare four supported variants and eight controlled faults: wrong decision label; reversed deletion direction; wrong score units/value; incorrect feature/class binding; wrong tested-edit outcome; failed search generalized to impossibility; unsupported extra clause under a correct claim link; and dropped mandatory limitation. Positive variants cover synonyms, harmless simplification, reordering and allowed numeric formatting.

That plans 480 development and 720 test diagnostic variants, grouped by their 40/60 parent inputs. Generated outputs and controlled faults are separate populations. Expected labels come from the stated construction and require semantic review; ambiguous fixtures cannot be silently relabelled to favor a checker. Final-test inputs and expected labels are hidden from the checker and renderer, and their schemas/filenames must not reveal the answer.

Natural-output audit covers the 60-source six-condition matrix: 720 planned view slots, including template outputs and explicit failure records. Actual generated-text counts are reported separately. Use two actual annotators, one of whom may be the researcher, working independently and blinded to condition labels where feasible. State author involvement and possible style-based unblinding. Adjudicate disagreements using the frozen rubric; document identities/roles, agreement and unresolved cases without inventing recruitment or consent.

Annotators judge final text against the frozen evidence, not merely the model's verdict. No release-gate score is its own ground truth. If the second annotator or required institutional process is unavailable, the implementation pilot can continue but natural semantic findings remain single-rater/automated estimates; do not present the planned independent audit as completed or definitive.

The separate human-understanding study (RQ4) is conditional Phase II work unless a real feasible protocol is approved and participants are available earlier. Semantic annotation and user-benefit measurement are different activities. Do not claim measured usability, appropriate reliance or comprehension from technical checks alone.

## 10. Metrics and statistical plan

H1: complete supported pair yield over all 60 requested sources. Both final narratives must satisfy the independent completeness/support rubric; blocked, missing, unparsable, status-only and fallback pairs count as failures. Record the primary paired P-minus-B1 difference.

Use a two-sided exact McNemar/binomial test on discordant source outcomes, alpha 0.05, for the single predeclared primary comparison. Report counts and a 95% paired-difference interval from 5, 000 source bootstrap samples stratified by original label. If no discordances occur, report that directly; do not fabricate evidence of superiority.

H2: report false acceptance on faulty variants and false rejection on supported variants, plus achieved supported-variant acceptance and abstention. Use source-cluster bootstrap rather than treating all 720 correlated variants as independent samples. A development acceptance target does not guarantee the same test acceptance rate.

H3: paired change from P's no-repair to final output; report extra calls/time. Use Holm adjustment for inferential H2/H3 tests if formal secondary significance is reported, while keeping the primary test separate. Report all prespecified comparisons and mixed outcomes.

Also report required-claim recall, extra-claim errors, omission and scope drift, initial versus final failures, narrative/fallback coverage, target macro-F1 and balanced accuracy, per-class outcomes and results separated by correct/incorrect target decisions. Counterfactuals need attempt coverage, any-flip/target-success rates, edit magnitude and semantic-assessment status.

No power guarantee is made for n=60. Wide intervals or nonsignificant results are inconclusive for small effects. Replicates, model outputs, claims and audience views are not extra independent source observations. If evidence extraction fails, retain that source in the overall system-yield denominator and separately report conditional renderer-only results on available evidence.

## 11. Locking, run order and amendment rules

Run order: primary-source/licence verification; dataset hashes/groups; feasibility pool and benchmark; model choice/revision freeze; development prompts and diagnostics; threshold/rubric selection; protocol/config hashes; locked-test generation; blinded audit; final analysis. Sampling can be performed reproducibly without exposing test examples to prompt development; do not open final outputs early.

Record package freeze, model/tokenizer revisions, prompts, all attempts, parser failures, source IDs, seeds, CPU threads, duration and memory. Use four Torch threads on the current five-CPU machine, one model-generation process and small batches; avoid concurrent duplicate LLM processes. Cache exact scoring/evidence keys and distinguish deliberate uncached consistency checks. Preserve model-signature/hash changes rather than reusing stale evidence.

An amendment changes version and states what was already observed. Test-driven model switching, dropping difficult cases, increasing sample size only until significance, or tuning thresholds on held-out failures is not the declared protocol. Later corrected analyses must be labelled rather than replacing failed results silently.

## 12. What is verified and what remains

**Verified now:** official dataset bytes/metadata/licence and 5574-record count; source-level preparation and disjoint group manifests; pinned public model cards/revisions/licence declarations; tokenizer-only label/context preflight on 20 feasibility sources; NLI config label order (contradiction, entailment, neutral); CPU runtime/compatible dependencies. Raw SMS remains outside the checkout.

**Not verified:** model weight integrity after download; target/NLI model loading; accuracy, speed, memory or JSON-generation gates; full counterfactual/rendering/checker inference; final thresholds; annotator availability. No target or NLI inference was run and no final-test outcomes were inspected. Planned diagnostic/rendered outputs have not been generated.

**External action needed:** Hugging Face metadata is accessible, but the actual weights redirect to **us.aws.cdn.hf.co**, where a standard HTTPS range read returns proxy tunnel 403. That exact host has been added to the draft with prior rules preserved. Review/save the new network change in environment settings and publish as indicated by the tool, then retry actual weight delivery. Saving a draft does not itself apply or publish it. This is not missing authentication: the repositories are public and ungated, so no token has been requested.

**Next-stage boundary:** Step 5 can elaborate architecture, but no dependent performance claims or final-test runs should rely on unverified access. This is a concrete protocol with a real remaining access prerequisite, not a completed experimental setup or result.
