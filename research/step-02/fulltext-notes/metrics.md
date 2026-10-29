# Full-text audit: faithfulness and consistency metrics

Reviewed on26 October 2026. Four primary full texts were available and analysed, including methods, experiments, limitations and relevant appendices. Physical PDF page numbers are used. No code was executed and no published result was reproduced.

## [L21] On Measuring Faithfulness or Self-consistency of Natural Language Explanations

**Exact method.** CC-SHAP compares input-token contribution vectors for the answer and the generated explanation. SHAP contribution ratios are signed and normalized by the absolute-sum of input contributions for each generated token; ratios are averaged across output tokens. Final CC-SHAP is one minus cosine distance, i.e. cosine similarity, between the resulting prediction and explanation vectors. This avoids specially crafted editing-test inputs but SHAP itself still evaluates masked coalitions. The authors explicitly call the construct self-consistency, not established internal faithfulness.

**Evaluation and what the numbers mean.** Comparative Consistency Bank evaluates eight existing tests plus CC-SHAP across 11 autoregressive LLMs and five tasks, 100 examples/task (e-SNLI, ComVE, three BBH tasks). Base/chat Llama 2, Mistral, Falcon and GPT2 are included. Tests often disagree for the same task/model; CC-SHAP correlates most often with Counterfactual Edits, while some edit tests have both positive and negative correlations. Repeated-run variance was estimated only for seven models on ComVE, three runs. No human study was conducted.

**Limits and assumptions.** A graded output/input-contribution consistency score is not mechanistic ground truth. Results depend on SHAP masking, Monte Carlo approximation, aggregation and normalization. Very small contributions in long outputs require special handling (Appendix A.3). Requires repeated inference and next-token logits/probabilities, but not gradients or activation access. Authors report about four minutes/example for CC-SHAP and six–36 hours per model/task for the full test suite; these are paper-specific runtimes. English-only autoregressive experiments; model-size relationship not established. Human judgment cannot establish unknown internal reasoning, although humans can judge other defined evidence-consistency properties.

**Overlap with audience/claim preservation.** The paper compares prediction versus explanation contribution profiles and includes a generic paraphrasing intervention among prior CoT tests. It does not develop an audience-role transformation pipeline or verify final prose claims against a typed decision/attribution/counterfactual evidence record. Paraphrasing CoT followed by answer generation is not the same task as preserving supported claims after a fixed decision explanation is rewritten for an audience. This observation is bounded to this inspected paper, not the literature as a whole.

**Implication for candidate research gap.** A consistency benchmark, contribution-profile comparison and comparison of multiple faithfulness tests are established prior art. Any G1/G2 proposal should distinguish semantic supported-claim preservation from attribution-profile similarity. Do not claim that a checker score establishes complete internal faithfulness.

**Baseline feasibility.** Suitable as an optional per-instance consistency diagnostic when target-model probabilities and enough repeated inference are available. Expensive to run across every candidate and audience variant. Black-box text-only APIs without probability access cannot directly support the released metric. A simplified alternative must be labelled an adaptation.

**Locators**
- PDF pp1–4 §§1–3: construct and tests
- PDF pp5–6 §4.1, Equations1–5: SHAP normalization, multi-token aggregation, cosine score
- PDF pp7–8 §§5.1–5.3: models, tasks and comparisons; p8 footnote4: logit/probability access
- PDF pp9–10: conclusion and limitations, compute and variance
- PDF pp14–18 Appendix A.1/A.3/A.7/A.8: definition, long-output caveat and repeated-run/correlation detail
- PDF pp21–42 Appendix B: worked per-instance examples and contribution visualizations

**Corrections to the interim review**
- Do not describe CC-SHAP as having no input perturbations: it uses masked SHAP coalitions, though it does not require separately crafted counterfactual edits.
- Do not require gradients or hidden activations for CC-SHAP; repeated probability/logit queries are the relevant access requirement.
- Keep self-consistency distinct from mechanistic faithfulness.

## [L23] A Causal Lens for Evaluating Faithfulness Metrics

**Exact method.** Causal Diagnosticity evaluates whether a metric ranks a faithful explanation above an unfaithful one for the same target answer. Controlled pairs are constructed using knowledge edits: primarily in-context editing (ICE), with MEMIT weight-editing ablations. Two edited knowledge settings preserve the answer while changing the intended reason. Pairwise correct ordering scores 1, ties0.5 and incorrect ordering0, averaged over examples. The main benchmark uses synthetic explanations to enforce the intended edit relationship.

**Evaluation and what the numbers mean.** Four tasks: fact checking from CounterFact, analogy, object counting and StrategyQA multi-hop reasoning. Main models are Qwen 2.5-7B and Gemma 2-9B-it. Metrics include post-hoc/CoT CC-SHAP, simulator-based scoring and continuous versions of Early Answering, Filler Tokens, Adding Mistakes and Paraphrasing. It studies corruption details, binary versus continuous scoring, ICE versus MEMIT and synthetic versus generated explanations; selected scaling tests use Qwen instruct 7/32/72B (larger AWQ variants). Table 1 Filler Tokens FactCheck diagnosticity is0.828 for Qwen and0.893 for Gemma in the specified ICE/synthetic setup. This is pair-ordering performance, not an explanation-correctness percentage applicable elsewhere.

**Limits and assumptions.** Faithful/unfaithful pair validity depends on edits actually taking effect and generalizing. Edit-success is assessed using whether the intended explanation has lower perplexity; this is explicitly an indicative proxy, not a complete portability/compositionality validation. Section5.3 states ICE Analogy edit reliability is below 50% and its diagnosticity findings are unreliable. The benchmark requires externally supplied explanations and per-instance scores, excluding tests that regenerate explanations (such as Counterfactual Edits) or depend on corpus-level scoring. Synthetic explanations reduce realism; differences from model-generated conditions and model-specific corruption sensitivity remain. CC-SHAP scaling experiments were excluded for cost.

**Overlap with audience/claim preservation.** Existing controlled faithful/unfaithful pair construction and diagnostic testing directly overlap G2 at the evaluation-principle level. The inspected paper does not define an audience-adaptation stage or preserve typed evidence claims through novice/expert rewriting; its intended causal labels depend on edited knowledge. A new controlled-fault benchmark alone cannot be treated as an unprecedented idea.

**Implication for candidate research gap.** Independent diagnosticity evaluation is established. G2 requires a distinct, justified target, such as final claim support under a frozen evidence record, and must acknowledge the relationship and limitations of synthetic construction. Do not represent the paper as providing unqualified ground truth about latent reasoning.

**Baseline feasibility.** Useful protocol inspiration and optional metric sanity tests. ICE-based controlled contexts are cheaper than weight editing, but require verifying edit adherence and preserving the target/evidence definition. MEMIT and large-model ablations increase compute. It is a metric-evaluation framework, not a directly interchangeable explanation-generation baseline.

**Locators**
- PDF pp2–4 §§2–3, Equations1–6: metric definitions, interventions, pair ordering and ties
- PDF pp4–6 §4: four tasks and data construction
- PDF pp6–9 §5/Table 1/Table 2: main experiments and diagnostics
- PDF p8 §5.3: explicit unreliable ICE Analogy finding and perplexity success proxy
- PDF p10 Limitations: supported metrics and edit portability assumptions
- PDF pp12–17 Appendices A–D: scaling, ICE/MEMIT templates, probability/corruption implementation
- PDF pp18–25 Appendices D–E: worked corruption examples, sensitivity, dataset prompts and task complexity

**Corrections to the interim review**
- Qualify controlled faithful/unfaithful labels by edit success; do not call them guaranteed causal ground truth.
- Report that the main knowledge edit is in-context fact injection, not necessarily parameter editing.
- Separate diagnostic pair ordering from direct supported-claim accuracy and from universal metric ranking.

## [L24] A Necessary Step toward Faithfulness: Measuring and Improving Consistency in Free-Text Explanations

**Exact method.** PEX consistency measures how an explanation favors a prediction over its negation. Although the original definition is a sequence-likelihood ratio, experiments use adjusted PEX (Eq4): posterior label log-odds with explanation appended minus prior label log-odds without it. Models are first supervised-fine-tuned for binary opinion-spam classification; sampled explanations are ranked by PEX to construct preference pairs, then DPO trains the explanation model. Evaluation trains student models to simulate teacher predictions, using teacher explanations during student training but not at test time.

**Evaluation and what the numbers mean.** TripAdvisor: 1,600 reviews split 960/320/320; Amazon: 2,000 selected reviews split 1,200/400/400. Mistral7B, Llama 2-13B and Yi1.5-9B are used. DPO data sampling generates40 explanations at temperature 1.0 and 40 at 1.2 per training review/prediction; preferred/dispreferred subsets differ by dataset. Student simulation uses 10 or 20 validation examples, five training passes, reporting held-out test F1 against teacher predictions. Table 2 Amazon Yi1.5 simulation F1 increases75.5 (SFT explanations)→85.2 (DPO explanations), a 9.7 point improvement, not an independently measured percentage of internal faithfulness or human utility. Zero-explanation baseline there is 67.8. Tests use related-sample t-tests and confidence intervals in appendices.

**Limits and assumptions.** Requires output probabilities; cannot directly score completely black-box text-only models. PEX is a contrastive support/consistency construct, not semantic proof that all prose claims are supported by the original input or that latent reasoning is accurately exposed. Experiments are binary classification; multiclass extension is future work. The simulation endpoint is system-level, not an individual explanation verification certificate, and assumes simulation is a useful proxy. SFT/DPO and student training impose substantial compute. Authors report SFT/DPO on one RTX A6000 for roughly 24 h per described training configuration; student training 1–2 h. Qualitative examples and average PEX do not establish all outputs are consistent.

**Overlap with audience/claim preservation.** Prediction-explanation contrastive consistency and optimization are already explicit prior art. The inspected method does not perform novice/expert audience transformations, validate concrete counterfactual claims, or check all final prose claims against an independent structured target-model evidence record. Its metric may be relevant as one partial diagnostic but does not substitute for those defined targets.

**Implication for candidate research gap.** A proposal cannot claim novelty merely for a prediction-explanation consistency score or optimizing explanations against such a score. G1 should state which evidence-supported claim types, transformations and independent checks go beyond this probability-based contrastive consistency.

**Baseline feasibility.** A scoring-only adapted PEX condition may be feasible if the same target model exposes label probabilities and a binary task is selected. Reproducing the original DPO method requires task SFT, sampled preferences, model training and simulator training; it is not a cheap training-free baseline. Scope/budget exclusions must be explicit.

**Locators**
- PDF pp2–5 §§3–4, especially p4 Eqs 1–4: original and adjusted PEX; p5 DPO and simulator design
- PDF pp6–8 §§5–6/Table 2: datasets, sampling, training sizes and F1 outcomes
- PDF p7 §6.1: >2consistent-threshold discussion versus reported <0inconsistency rates
- PDF p9 Limitations: black-box access, binary scope and system-level evaluation
- PDF pp13–15 Appendices A.1–A.6: prompts, LoRA/compute, student training and interval tables

**Corrections to the interim review**
- Identify adjusted PEX Eq4 as the implemented experimental score rather than only the original sequence-probability ratio.
- The reported up-to-9.7 improvement is simulation F1 points; do not label it universal faithfulness gain or human-study improvement.
- The paper distinguishes a >2 consistent-score criterion from reported fractions with PEX <0; avoid conflating these thresholds.

## [L31] Towards Faithful Natural Language Explanations: A Study Using Activation Patching in Large Language Models

**Exact method.** Causal Faithfulness (CaF) replaces SHAP-style contribution profiles with activation-patching indirect effects. Clean, corrupted and patched forward passes create token×layer matrices for the answer and post-hoc explanation; effects are averaged across generated tokens. CaF is cosine similarity of the two matrices, with variants aggregating token or layer axes or patching windows. Symmetric Token Replacement (STR) uses manually constructed equal-token-length counterfactual spans rather than Gaussian embedding noise.

**Evaluation and what the numbers mean.** Main tests use six Gemma 2 variants (2B/9B/27B, base and instruct), three tasks (CoS-E, e-SNLI, adapted ComVE),100 examples/task and three seeds. Base models get 3-shot prompts while chat models are zero-shot. e-SNLI excludes neutral examples; ComVE is adapted to single-statement illogicality confirmation and a logical statement as counterfactual. Comparisons are CFF and CC-SHAP. Table 1 values are multiplied by100 continuous scores, not percentages of truly faithful outputs. Plausibility is assessed with GPT-4o over six criteria, three ratings/example, using supplied gold explanations; this is not a new participant study.

**Limits and assumptions.** Requires internal hidden-state intervention and output probabilities; approximately T×L patching forward passes, in addition to clean/corrupted processing and output-token effects. Equal token-length replacements depend on tokenizer; manually edited gold-rationale spans and corrupted-span-onward visibility limit task coverage. Claims of lower OOD corruption risk are shown in selected controlled tasks, not a theorem that all STR inputs are in-distribution. Models are one family; different base/chat prompting and limited samples qualify generalization. GPT-4o plausibility is not participant understanding or appropriate reliance. Internal causal-attribution agreement remains a designed proxy; authors acknowledge full mechanistic faithfulness remains a larger challenge.

**Overlap with audience/claim preservation.** This is more internal evidence than surface output checks, but it does not implement claim-level final narrative verification, audience rewriting, validated recourse semantics or risk/coverage rejection. It provides a possible expensive diagnostic reference for target-model explanation correspondence, not a substitute for evidence-preservation auditing.

**Implication for candidate research gap.** Layer-aware attribution consistency is established prior art. Avoid claiming a completely new internal-faithfulness metric without comparison; do not equate a final prose evidence checker with CaF. G1 can distinguish its evidence-preservation target, while acknowledging that the underlying attribution record remains imperfect.

**Baseline feasibility.** Suitable optional white-box diagnostic if compute and manually aligned counterfactual spans are available. Poor default for text-only APIs or unrestricted task data because of hidden-state access, token alignment and cost. Cannot infer feasible runtime from model parameter count alone.

**Locators**
- PDF pp3–6 §§3.1–4.2, Equations2–3: patching and cosine CaF
- PDF pp5–8 §§5.1–5.5/Table 1: experiments, metric comparisons and GPT-4o plausibility
- PDF p9 §7 Limitations: T×Lpasses, equal-length replacements and span visibility
- PDF p11 Appendix A.1: manual edits, e-SNLI neutral exclusion, ComVE adaptation, temperature 1.0/top-p 0.95
- PDF pp11–13 Appendix A.2/Table 2: six-criterion model-judged plausibility
- PDF pp14–23 Appendix B: causal-matrix examples/visualizations across model variants

**Corrections to the interim review**
- Plausibility evaluation uses GPT-4o, not actual human participants.
- Do not describe activation patching as requiring no interventions or as proving elimination of OOD issues in all settings.
- State manual equal-token-length replacements, specific task adaptations and white-box requirements.
- CaF values scaled by100 remain continuous scores, not percent faithful explanations.

## Cross-paper conclusion

Behavioral self-consistency, prediction-support log odds, contribution-profile alignment and activation-patching alignment are distinct constructs. None of the four inspected full papers develops the exact fixed-decision audience-rewriting/typed-claim preservation pipeline proposed as a candidate in Step2, but this bounded observation is not an exhaustive novelty proof. Diagnostic testing itself is established by Causal Diagnosticity and others. A practical thesis should use independent held-out support labels for its defined claim target, report valid paraphrases as well as injected errors, keep coverage/cost visible, and label latent-faithfulness claims conservatively.
