# Cross-Refine and FaithLM full-text audit

Read full text and appendices from downloaded officialACL PDFs; no experiments run. PhysicalPDF page numbers are used.

## L25 — Cross-Refine: Improving Natural Language Explanation Generation by Learning in Tandem

Two LLM roles: generator produces a CoT NLE using FEB-style few-shot examples; critic assesses need for improvement, generates feedback and a suggested explanation; generator cross-references both to produce a refinement. It is not inherently iterative (Limitations), although authors propose adaptive extension. Section3.1 explicitly permits correcting BOTH prediction and explanation, so it is not a fixed-decision explanation-only procedure. Same weights may play both roles in self Cross-Refine. FiXer contains60 demonstrations constructed with Llama3-8B, ChatGPT feedback/suggestions, manual review and postprocessing; in-context prompts use limited examples.

### Evaluation
{
  "tasks": [
    "e-SNLI natural-language inference",
    "ECQA commonsense QA",
    "HealthFC evidence-based health fact checking, English and German"
  ],
  "models": [
    "Qwen2-7B",
    "Mixtral-8x7B",
    "Llama3-70B"
  ],
  "baseline": "Self-Refine; compares role/model combinations and ablates feedback/suggestion components.",
  "automatic_metrics": [
    "BLEURT",
    "BARTScore",
    "TIGERScore; for German uses BERTScore, BARTScore and MoverScore"
  ],
  "human_study": "32 English-native annotators,2 ratings per explanation;10 selected explanations per setting for ECQA/HealthFC. Human dimensions are perceived faithfulness (binary hallucination/misinformation judgment), coherence and insightfulness (5-point). HealthFC selection filters20–50tokens,bigram diversity>=0.8,digit ratio<=0.3,question/explanation embedding similarity>=0.6 before random sampling. Krippendorff alpha reported0.45ECQA/0.39HealthFC. These are selected subjective outcomes, not independent internal-faithfulness tests.",
  "result_caution": "Automatic improvements are not uniform: mismatched models underperform Self-Refine on HealthFC; same-model role variant is better. Table2 may reflect plausibility/knowledge limitations of annotators; no transferable effect assumed.",
  "resources": "GPTQ quantized models on one RTX A6000/A100/H100. Full-dataset reported stage runtimes range hours; e.g Qwen2 ECQA feedback2h/refinement5h,HealthFC6h/14h,Table8; not per-query estimates."
}

### Limits
- Authors acknowledge context limits, small in-context demonstration collections and English/German evaluation.
- Human study small and filtered; paper does not report retention coverage of generation filters, so perceived ratings cannot be treated as unconditional coverage.
- Subjective perceived faithfulness is not same-target behavioral or internal causal fidelity.
- Section6.2 describes binary perceived faithfulness but later IAA explanation inconsistently calls perceived faithfulness5-point; preserve actual stated protocol and flag reproduction detail.
- General-purpose critics may introduce hallucinations on unfamiliar medical content.

### Evidence-preservation overlap
Already provides a critic-based final refinement, examples of correcting errors, evaluation and study-selection quality filters. In the inspected full text and appendix descriptions, no novice/expert audience rewrite stage, structured claim-to-evidence contract, post-adaptation claim verification, risk/coverage release gate or evidence-preservation metric was identified. This is a bounded observation about this paper, not a field-wide absence claim. German generation is language adaptation, not user-expertise adaptation.

### Implications
Critic/generator separation, extra feedback+suggestions, correction and conversational NLE refinement cannot themselves support novelty. A fixed-decision audience-preservation protocol is distinguishable, but requires comparison with other prior work; changing predictions must be controlled in any adapted baseline.

### Baseline feasibility
Potential useful7B role-prompting comparator, but faithful reproduction needsFiXer and exact prompt stages; must control multiple model calls and whether original decision is frozen. Original70B/MoE combinations add cost; adapting Qwen/model/prompt is an adaptation, not exact reproduction.

### Locators
- PDFp3 section3.1–3.2: pipeline and possible answer correction
- PDFp4 section4.1–4.5: datasets/models/demonstrations
- PDFp5 section5.1–5.2: metric and human-study protocol
- PDFpp6–7 section6.1–6.3,Tables1–4: conditions and mixed results
- PDFp9 Limitations: not inherently iterative
- PDFpp15–16 AppendicesC,D,H andTables7–9: resources,FiXer and selection filters

### Corrections to interim
- Describe Cross-Refine as one cross-refinement pass, not inherently iterative.
- Its example can change prediction as well as explanation; freeze decisions explicitly for this thesis.
- Human perceived faithfulness is a hallucination/misinformation judgment, not a direct test of target-model reasoning.
- FiXer demonstrations are human-reviewed despite no supervised model training.

## L35 — FaithLM: Towards Faithful Explanations for Large Language Models

Separates unchanged target predictor f from explanation generator g_E, includingAPI targets in stated formulation. For explanationE, a strong LLM produces an opposite-semantics contrary hint notE; target is queried with hint plus original input. Score is target prediction sensitivity f(X)-f(X|notE), described as output logits/calibrated probabilities; section3.1 also mentions scoring nonzero-attribution tokens. Algorithm1 repeatedly generates explanations informed by trajectory of explanations/scores until fixed budget or decision flip. Algorithm2 optimizes an elicitation prompt by average score over held-out training examples. A theorem connects contrary-hint sensitivity to causal faithfulness under explicit equivalence-of-hint-to-do-intervention and irrelevant-text invariance assumptions.

### Evaluation
{
  "datasets": "ECQA first500instances due API cost; TriviaQA-LongBench300triples; BalancedCOPA500questions. AppendixG addsMedMCQA and closed-model targets; exact additional subset size not stated in cited table.",
  "models": "Main targetsVicuna7B/Phi2; main explainers and contrary-hint generatorsGPT3.5Turbo/Claude2. Appendix addsGPT3.5/Claude2targets. Sizes of proprietary models are not independently established; do not copy appendix assertion that both are>=70B.",
  "baselines": [
    "SelfExp single-pass prompt explanations",
    "Self-consistency CoT-based explanations"
  ],
  "metrics": "Same contrary-hint fidelity score used to optimize and evaluate; truthfulness primarily similarity to ground-truth explanations, judged byGPT4o/RoBERTaLarge/XLNetLarge. Contrary-hint quality tested on100sampledECQA/COPA cases via semantic relation classifiers; this is not a user study. Main results show fidelity curves over optimization20steps; no precise numeric graph values inferred here.",
  "reported_resources": "AppendixF reports oneNVIDIAA40~46GB; GPT3.5cost/time estimates~$0.01/~3s ECQA/COPA and~$0.04/~5sTriviaQA, but unit and iteration inclusion are not sufficiently clear for budgeting; do not transfer these costs to thesis.",
  "reproduction_discrepancies": "Mainsection4.2/AppendixC say30examples per prompt-optimization step; section4.3 says15. Algorithm2/main text mentions20 or50step limits whereas Table2 gives50ECQA/100TriviaQA/100COPA. Reported runs averaged3 with grid search; exact fixed protocol should be resolved with release before reproducing."
}

### Limits
- Theorem is conditional on semantic hint implementing a causal do-intervention and target invariance to irrelevant text. These assumptions are not automatically satisfied by realLLM prompting; sensitivity may also reflect suggestion compliance. It is not unconditional certification of internal causal reasoning.
- Optimization/evaluation share contrary-hint score; independent diagnostic checks are needed before universalfaithfulness claims.
- Generation and opposite-hint quality matter; AppendixK.3 explicitly shows a purported contrary hint that reaffirms the original rationale and fails to flip prediction.
- Authors emphasize increased compute/carbon cost due iteration; main empirical focusMCQ tasks, future workopen-ended/multilingual.
- Reference/NLI similarity and GPTjudgments are not human understanding or appropriate reliance.
- API-only model-agnostic claim must be reconciled with score requirements for logits/calibrated probabilities and section3.1saliency mention.
- The publicREADME previously inspected is minimal, so availability of complete reproducible implementation remains unresolved.

### Evidence-preservation overlap
Already repeatedly evaluates and refines final generated explanations with target-model queries, and separately evaluates opposite-hint semantics and reference-explanation similarity. Thus cannot claim first post-generation behavioral check. In the inspected full text/appendices no explicit novice/expert audience adaptation experiment, structured per-claim evidence preservation across audience rewrites, release abstention/coverage objective or cost-controlled claim-release policy was identified. Its stopping condition may end without a flip and case study reportsfailure; not a validity guarantee.

### Implications
High-priority nearest comparator for fixed-target explanation optimization. Candidate distinction is preservation of supported decision evidence under audience transformations with independent claim diagnostics; a contrary-hint loop or model-based rewriting alone is already prior art. Any comparison must state conditional meaning of its metric rather than treating it as ground truth.

### Baseline feasibility
Conceptual black-box comparator possible if target returns usable output scores; needs opposite-hint generator and up-to20explanation iterations plus prompt optimization50–100rounds. For small prototype, fixed-budget adapted reproduction should be clearly labelled. Resolve contradictory schedule/sample statements and minimal code release before claiming exact reproduction.

### Locators
- PDFp2 section2.1: distinct target/explainer roles
- PDFpp3–4 section3.1: score, contrary-hint semantics,theorem assumptions
- PDFp5 Algorithms1–2 and sections3.2–3.3: iteration/earlystop
- PDFpp6–8 section4: baseline,data,metrics and contrary-hint quality
- PDFp9 section6: computational/environmental limitation
- PDFp12 AppendixA–B: conditional proof and dataset sizes
- PDFpp13–14 AppendicesC–F,Tables2–5: sample/schedule/resources
- PDFpp15–17 AppendixG: additionaldomain/model results and scope
- PDFp18 AppendixI,Table9: evaluator prompts; GTprompt hasG2/G3 both irrelevant contents
- PDFp23 AppendixK.3: contrary-hint failure case

### Corrections to interim
- Full text confirms fixed target predictor and iterative post-generation scoring; do not position target-query checking alone as new.
- Theoretical validity is conditional; do not repeat as an unqualified causal guarantee.
- Truthfulness primarily automated similarity/semantic consistency against reference rationales, not direct human outcomes.
- Prompt optimization budget/sample inconsistencies require resolution; exact reproduction not yet established.
