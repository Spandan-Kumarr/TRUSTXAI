# Full-text audit: grounded explanation generation and refinement

Reviewed on 26 October 2026. All four selected PDFs, including relevant methods, evaluations, limitations and appendices, were inspected. No published experiment was executed or reproduced. Physical PDF page locators are used.

## Main corrections to interim review

- Cross-Refine is a cross-refinement pass, not inherently iterative, and may alter the prediction as well as its explanation.
- SR-NLE holds the answer fixed but its reported unfaithfulness proxy is inserted-word string matching over label-changing intervention cases; its own appendix includes near-random word-feedback controls.
- FaithLM already performs iterative target-query checks of final generated explanations. Its causal validity theorem requires strong semantic-intervention assumptions, and its reported optimization details contain inconsistencies.
- Faithfulness Serum already judges final explanations for substantive hint dependence and validates its judge with people; it is incorrect to describe it as having no final-output semantic assessment.
- None of these inspected texts establishes the exact novice/expert rewriting-plus-general-claim-preservation release protocol proposed as a candidate. This bounded difference does not establish field-wide novelty.

## [L25] Cross-Refine: Improving Natural Language Explanation Generation by Learning in Tandem

**Full text reviewed:**
True

**Method:**
Two LLM roles: generator produces a CoT NLE using FEB-style few-shot examples; critic assesses need for improvement, generates feedback and a suggested explanation; generator cross-references both to produce a refinement. It is not inherently iterative (Limitations), although authors propose adaptive extension. Section3.1 explicitly permits correcting BOTH prediction and explanation, so it is not a fixed-decision explanation-only procedure. Same weights may play both roles in self Cross-Refine. FiXer contains60 demonstrations constructed with Llama3-8B, ChatGPT feedback/suggestions, manual review and postprocessing; in-context prompts use limited examples.

**Evaluation:**
**Tasks:**
- e-SNLI natural-language inference
- ECQA commonsense QA
- HealthFC evidence-based health fact checking, English and German

**Models:**
- Qwen2-7B
- Mixtral-8x7B
- Llama3-70B

**Baseline:**
Self-Refine; compares role/model combinations and ablates feedback/suggestion components.

**Automatic metrics:**
- BLEURT
- BARTScore
- TIGERScore; for German uses BERTScore, BARTScore and MoverScore

**Human study:**
32 English-native annotators,2 ratings per explanation;10 selected explanations per setting for ECQA/HealthFC. Human dimensions are perceived faithfulness (binary hallucination/misinformation judgment), coherence and insightfulness (5-point). HealthFC selection filters20–50tokens,bigram diversity>=0.8,digit ratio<=0.3,question/explanation embedding similarity>=0.6 before random sampling. Krippendorff alpha reported0.45ECQA/0.39HealthFC. These are selected subjective outcomes, not independent internal-faithfulness tests.

**Result caution:**
Automatic improvements are not uniform: mismatched models underperform Self-Refine on HealthFC; same-model role variant is better. Table2 may reflect plausibility/knowledge limitations of annotators; no transferable effect assumed.

**Resources:**
GPTQ quantized models on one RTX A6000/A100/H100. Full-dataset reported stage runtimes range hours; e.g Qwen2 ECQA feedback2h/refinement5h,HealthFC6h/14h,Table8; not per-query estimates.


**Limitations:**
- Authors acknowledge context limits, small in-context demonstration collections and English/German evaluation.
- Human study small and filtered; paper does not report retention coverage of generation filters, so perceived ratings cannot be treated as unconditional coverage.
- Subjective perceived faithfulness is not same-target behavioral or internal causal fidelity.
- Section6.2 describes binary perceived faithfulness but later IAA explanation inconsistently calls perceived faithfulness5-point; preserve actual stated protocol and flag reproduction detail.
- General-purpose critics may introduce hallucinations on unfamiliar medical content.

**Claim preservation overlap:**
Already provides a critic-based final refinement, examples of correcting errors, evaluation and study-selection quality filters. In the inspected full text and appendix descriptions, no novice/expert audience rewrite stage, structured claim-to-evidence contract, post-adaptation claim verification, risk/coverage release gate or evidence-preservation metric was identified. This is a bounded observation about this paper, not a field-wide absence claim. German generation is language adaptation, not user-expertise adaptation.

**Novelty implication:**
Critic/generator separation, extra feedback+suggestions, correction and conversational NLE refinement cannot themselves support novelty. A fixed-decision audience-preservation protocol is distinguishable, but requires comparison with other prior work; changing predictions must be controlled in any adapted baseline.

**Baseline feasibility:**
Potential useful7B role-prompting comparator, but faithful reproduction needsFiXer and exact prompt stages; must control multiple model calls and whether original decision is frozen. Original70B/MoE combinations add cost; adapting Qwen/model/prompt is an adaptation, not exact reproduction.

**Locators:**
- PDFp3 section3.1–3.2: pipeline and possible answer correction
- PDFp4 section4.1–4.5: datasets/models/demonstrations
- PDFp5 section5.1–5.2: metric and human-study protocol
- PDFpp6–7 section6.1–6.3,Tables1–4: conditions and mixed results
- PDFp9 Limitations: not inherently iterative
- PDFpp15–16 AppendicesC,D,H andTables7–9: resources,FiXer and selection filters

**Corrections to interim:**
- Describe Cross-Refine as one cross-refinement pass, not inherently iterative.
- Its example can change prediction as well as explanation; freeze decisions explicitly for this thesis.
- Human perceived faithfulness is a hallucination/misinformation judgment, not a direct test of target-model reasoning.
- FiXer demonstrations are human-reviewed despite no supervised model training.

## [L30] Self-Critique and Refinement for Faithful Natural Language Explanations

**Full text reviewed:**
True

**Method:**
**Target:**
A single instruction-tuned generative LLM predicts answer y; y is held fixed while the same LLM generates and refines its post-hoc explanation.

**Pipeline:**
Generate answer, generate initial explanation, then K feedback/refinement rounds. Natural-language feedback is regenerated from each current explanation; important-word feedback (IWF) is computed once and reused across rounds (Algorithm1). IWF variants are prompt ranking, final-layer mean-attention and Integrated Gradients.

**Attribution:**
Sequentially attribute each answer-span token to preceding input/output context; use absolute values, sum across answer tokens, then aggregate subword scores to words from task input excluding prompt tokens. Top5 words guide explanations; this is unsigned magnitude evidence, not signed contribution claims.

**Checks:**
Method refines from supplied feedback; the CT faithfulness test is an evaluation on label-changing inserted-word interventions. It does not apply a semantic claim verifier/release gate to every final explanation. Prompts request retaining correct content, but no mechanically enforced supported-claim contract is supplied.


**Evaluation:**
**Datasets:**
ComVE, ECQA, e-SNLI; first1000test examples from each. GPT-4o generates20coherent unique adjective/adverb insertion interventions per original, yielding20000intervened inputs per dataset/model. Manual intervention quality check150examples (50perdataset).

**Models:**
Falcon3-Instruct7B, Llama3.1-Instruct8B, Mistral-Instruct-v0.3 7B, Qwen2.5-Instruct7B; greedy generation, K≤3, top5words.

**Metric:**
Only counter instances whose prediction changes are scored. Unfaithfulness=Ncounter explanations that do not string-match the inserted word / Ncounter. This is influential-word acknowledgment, not arbitrary semantic claim support. Counter counts vary392–3058 by model/dataset (Appendix F.2 Table8).

**Baselines:**
Initial NLE; SC-NLE samples20explanations at T=1 and uses all-mpnet-base-v2 semantic-centroid voting; NLF vs IWF variants. G-TEX numbers are taken from a different paper and authors explicitly say not fully controlled. Random5word feedback is an appendix diagnostic on e-SNLI.

**Reported result:**
After3rounds, Table1 macro-average across12dataset-model conditions: Init54.81%unfaithfulness, SC49.74%, NLF47.58%, IWF-Pmt37.23%, IWF-Attn36.02%, IWF-IG36.30%; best reported absolute change18.79percentage points from Init. These are conditional CT proxy outcomes, not semantic verification accuracy or universal faithfulness.

**Critical control:**
AppendixF.6 Table12 e-SNLI: random-word feedback29.28% mean, IWF-Pmt30.10%, IWF-Attn27.69%, IWF-IG28.39%. Random trials use3seeds; result shows selected-word quality need not explain most improvement. Table13 acknowledgment-in-topN rates also compare to random.


**Limitations:**
- Authors: post-hoc explanations only; sole CT metric, no plausibility/completeness/reference alignment; underlying attention/IG reliability and baseline dependence; models only7–8B.
- IG uses EOS-embedding baseline. Selected500integrationsteps for Falcon/Llama/Mistral and1000forQwen make exact IG variant expensive; no actual compute configuration/runtime table is supplied in the inspected paper.
- Conditioning on label-changing interventions and lexical string matching limits construct validity. Length increases with refinement (Fig6); related surface overlap/length effects need independent controls.
- Paper itself acknowledges close-to-random important-word selection. Do not characterize random-feedback weakness as an undisclosed flaw or claim this paper proves causally faithful internal explanations.

**Claim preservation overlap:**
**Exists:**
Checks refined explanations after generation for inserted-word inclusion; refiner prompts instruct preserving correct parts and integrating feedback naturally (Tables21–22). Same fixed answer and reused attribution feedback are relevant prior art.

**Not found in inspected text:**
No novice/expert audience transformation experiment, general atomic factual/model-evidence claim audit, supported paraphrase versus contradiction diagnostic, or risk/coverage abstention release mechanism. The CT is a specific proxy rather than full semantic preservation.

**Scope caution:**
The absence assessment is limited to this inspected paper and its appendices; not evidence that the broader field lacks those features.


**Novelty implication:**
Attribution-guided post-hoc explanation refinement with fixed target answer is established. Any contribution should exceed this with a concrete preservation mechanism and independent diagnostics; include random-word feedback and length controls before asserting attribution superiority.

**Baseline feasibility:**
Prompt-based IWF is the most feasible lightweight direct comparator: one model, once-computed top5word ranking, K3refinements. Attention needs local internals; exact IG variant is substantially costlier. Clearly label prompt-IWF as prompted evidence, not grounded numerical attribution. Reproduce CT separately from any new claim-consistency metric.

**Locators:**
- PDFpp3–5, §§3.1–3.3: single-model architecture, equations1–9, absolute/summed attributions.
- PDFp6, §§4.3–4.5: CT string-match definition, interventions, SC-NLE and greedy/top5/K3 setup.
- PDFp7, Tables1–2 and §5.2: reported results and uncontrolled G-TEX comparison caveat.
- PDFp8, Fig6: explanation length versus proxy unfaithfulness.
- PDFp10, Limitations: sole evaluation proxy and attribution/model-scale caveats.
- PDFpp12–14, AppendicesA–E: dataset first1000, modelnames, EOSbaseline,500/1000IGsteps.
- PDFpp15–16, AppendixF.2/F.6, Tables8/12/13: counter denominators and random-word control.
- PDFp18, Algorithm1: IWF computed once, reused; answer fixed.
- PDFpp22–27, Tables17–22: all prompts and correct-content retention requests.

**Corrections to interim:**
- Prior code-inspection concern is confirmed in full-paper §4.3, not merely an implementation peculiarity.
- Important-word feedback is reused across rounds in Algorithm1; do not imply recomputing attribution every refinement is required.
- Add explicit random-word feedback and explanation-length controls; paper already includes the random diagnostic.
- Results are conditional influential-word mention rates over counter instances, not full semantic unsupported-claim detection or per-input release reliability.
- G-TEX cross-paper comparison cannot substantiate controlled head-to-head superiority.

## [L35] FaithLM: Towards Faithful Explanations for Large Language Models

**Full text reviewed:**
True

**Method:**
Separates unchanged target predictor f from explanation generator g_E, includingAPI targets in stated formulation. For explanationE, a strong LLM produces an opposite-semantics contrary hint notE; target is queried with hint plus original input. Score is target prediction sensitivity f(X)-f(X|notE), described as output logits/calibrated probabilities; section3.1 also mentions scoring nonzero-attribution tokens. Algorithm1 repeatedly generates explanations informed by trajectory of explanations/scores until fixed budget or decision flip. Algorithm2 optimizes an elicitation prompt by average score over held-out training examples. A theorem connects contrary-hint sensitivity to causal faithfulness under explicit equivalence-of-hint-to-do-intervention and irrelevant-text invariance assumptions.

**Evaluation:**
**Datasets:**
ECQA first500instances due API cost; TriviaQA-LongBench300triples; BalancedCOPA500questions. AppendixG addsMedMCQA and closed-model targets; exact additional subset size not stated in cited table.

**Models:**
Main targetsVicuna7B/Phi2; main explainers and contrary-hint generatorsGPT3.5Turbo/Claude2. Appendix addsGPT3.5/Claude2targets. Sizes of proprietary models are not independently established; do not copy appendix assertion that both are>=70B.

**Baselines:**
- SelfExp single-pass prompt explanations
- Self-consistency CoT-based explanations

**Metrics:**
Same contrary-hint fidelity score used to optimize and evaluate; truthfulness primarily similarity to ground-truth explanations, judged byGPT4o/RoBERTaLarge/XLNetLarge. Contrary-hint quality tested on100sampledECQA/COPA cases via semantic relation classifiers; this is not a user study. Main results show fidelity curves over optimization20steps; no precise numeric graph values inferred here.

**Reported resources:**
AppendixF reports oneNVIDIAA40~46GB; GPT3.5cost/time estimates~$0.01/~3s ECQA/COPA and~$0.04/~5sTriviaQA, but unit and iteration inclusion are not sufficiently clear for budgeting; do not transfer these costs to thesis.

**Reproduction discrepancies:**
Prompt optimization sample count: main section4.2/AppendixC say30perstep, section4.3 says15. Explanation-refinement20steps is a separate phase and coherent with Table2. For trigger-prompt optimization, Algorithm2 explanation text PDFp6 says20steps, section4.3 PDFp7 uniformly50rounds, Table2 says50ECQA/100TriviaQA/100COPA. Resolve exact intended schedule with authors/release. Runs reportedly averaged3 with grid search.


**Limitations:**
- Theorem is conditional on semantic hint implementing a causal do-intervention and target invariance to irrelevant text. These assumptions are not automatically satisfied by realLLM prompting; sensitivity may also reflect suggestion compliance. It is not unconditional certification of internal causal reasoning.
- Optimization/evaluation share contrary-hint score; independent diagnostic checks are needed before universalfaithfulness claims.
- Generation and opposite-hint quality matter; AppendixK.3 explicitly shows a purported contrary hint that reaffirms the original rationale and fails to flip prediction.
- Authors emphasize increased compute/carbon cost due iteration; main empirical focusMCQ tasks, future workopen-ended/multilingual.
- Reference/NLI similarity and GPTjudgments are not human understanding or appropriate reliance.
- API-only model-agnostic claim must be reconciled with score requirements for logits/calibrated probabilities and section3.1saliency mention.
- The publicREADME previously inspected is minimal, so availability of complete reproducible implementation remains unresolved.

**Claim preservation overlap:**
Already repeatedly evaluates and refines final generated explanations with target-model queries, and separately evaluates opposite-hint semantics and reference-explanation similarity. Thus cannot claim first post-generation behavioral check. In the inspected full text/appendices no explicit novice/expert audience adaptation experiment, structured per-claim evidence preservation across audience rewrites, release abstention/coverage objective or cost-controlled claim-release policy was identified. Its stopping condition may end without a flip and case study reportsfailure; not a validity guarantee.

**Novelty implication:**
High-priority nearest comparator for fixed-target explanation optimization. Candidate distinction is preservation of supported decision evidence under audience transformations with independent claim diagnostics; a contrary-hint loop or model-based rewriting alone is already prior art. Any comparison must state conditional meaning of its metric rather than treating it as ground truth.

**Baseline feasibility:**
Conceptual black-box comparator possible if target returns usable output scores; needs opposite-hint generator and up-to20explanation iterations plus prompt optimization50–100rounds. For small prototype, fixed-budget adapted reproduction should be clearly labelled. Resolve contradictory schedule/sample statements and minimal code release before claiming exact reproduction.

**Locators:**
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

**Corrections to interim:**
- Full text confirms fixed target predictor and iterative post-generation scoring; do not position target-query checking alone as new.
- Theoretical validity is conditional; do not repeat as an unqualified causal guarantee.
- Truthfulness primarily automated similarity/semantic consistency against reference rationales, not direct human outcomes.
- Prompt optimization budget/sample inconsistencies require resolution; exact reproduction not yet established.

## [L36] Faithfulness Serum: Mitigating the Faithfulness Gap in Textual Explanations of LLM Decisions via Attribution Guidance

**Full text reviewed:**
True

**Method:**
**Target:**
Fixed prior answer from an unmodified target LLM; explaining generation is steered after prediction. Compute PE-LRP relevance for first generated answer token, aggregate relevance over question input (excluding system/generated tokens), add alpha*relevance to post-softmax attention at selected layers throughout explanation decoding.

**Intervention:**
Main local models Llama3.1-8B-Instruct and Qwen2.5-7B-Instruct. Layers17–19 selected by logit-lens study. Staticalpha=.06Llama/.1Qwen from MMLU auxiliary-training lexical-diversity sweep.

**Adaptive:**
TTalpha regenerates explanation while adjustingalpha to seek distinct-1 ratio35–45%, max15iterations. This controls a lexical-diversity proxy, not verified support/claim risk; generation is not simply one extra pass in this adaptive variant.

**Evaluation setup:**
Inject four misleading hint types; retain instances where the same target model changes its answer to the hint-provided answer; ask post-hoc explanation with general or protocol-specific prompts (and intermediate grounding prompts).


**Evaluation:**
**Metrics:**
Two final-output evaluations: Qwen2.5-14B-Instruct judge requires explicit hint mention PLUS substantive reliance; CT keyword test accepts distinctive words per hint category. Neither checks every factual/model-evidence claim. Human validation of judge96sampledexplanations×3independentreviewers, average93.4%agreement with judge and reportedkappa.84.

**Data denominators:**
MainMMLU1000successfullyhint-flippedexamples per hint category for each open model; counts of searched inputs are reported (Llama1182–3378; Qwen1896–3232 dependinghint). Closedmodel evaluation50successfullyflippedexamples per hint/model (GPT4o,Gemini2.0Flash). Additional ARC-C,OpenBookQA,CommonsenseQA,SciQ report full dataset and selectedflip counts in Table8. Open-ended MMLU extension also used.

**Baselines:**
Unsteered explanation with same prompts; four promptingstrategies; attentionrollout/layer-to-layer relevance alternatives; firsttoken-only/firstsentence/full-decoding intervention; firstanswer-token vs explicitlabeltoken PE-LRP target.

**Reported result example:**
Table1 LlamaMMLU general metadata hint1000selectedflips: judge acknowledgment3.0→10.0%; CT2.9→6.9%. Sycophancy judge36.1→47.7%; CT47→65%. These specific conditional outcomes must not become universal validity/faithfulness improvements.

**Adaptive reporting caution:**
Table4 caption says1000examples, but §5 describes100benchmarksamples perhint across3seeds; preserve unresolved denominator mismatch if quoting TTalpha exact results. Main prose reports7.2generationsaverage. Credit-bias paragraph/Table6 also differ100vs1000sample wording; avoid those exact counts without clarification.


**Limitations:**
- Predict-and-explain only and attention mechanism only are explicit author limitations; residual/feed-forward/normalization effects not handled.
- Evaluation focuses on acknowledgment/dependence for synthetic hint-induced answer changes. This is a narrow known-influence test, not exhaustive truth, causal completeness or robustness to all real inputs.
- CT keyword matches can accept superficial references; complementary judge has human agreement but is still not universal ground truth.
- Paper qualitative guided examples can acknowledge a hint while retaining incorrect arithmetic or factual claims (AppendixC,PDFpp18–19). Thus hint attribution and globally correct supported claims differ.
- Static method adds one PE-LRP backward pass plus explanation attention modifications; no empiricalwallclockcosttable supplied. TTalpha multiple generations adds further cost. Experimental infrastructure NVIDIAH10080GB, individualrunmax24h.
- PDF title is Faithfulness Serum whereas inspected ACL XML/title metadata says Faithful Serum: flag version/title discrepancy rather than silently assume identical title metadata.

**Claim preservation overlap:**
**Exists:**
Finalgeneratedexplanations are semantically assessed for hint dependence by judge, with keyword complement and limited human judge validation. It is incorrect to say this predecessor never evaluates final text or has no semantic checking. It also compares explicitgrounding prompts and generationfluency.

**Not found in inspected text:**
No audience-specific rewriting stage, fixed-evidence claim schema with preservation tests across novice/expert variants, or release/abstention criterion based on independent general claim support. TTalpha is fluency-adaptive, not evidencesupport gating.

**Scope caution:**
Conditional hintcounter yields are reported; do not claim authors hide all selection denominators. Coverage of successfulhint construction is different from an explanationreleasecoverage protocol.


**Novelty implication:**
Attribution-grounded generation plus counterfactual influence testing and semantically judged final explanations is direct2026priorart. A candidate preservation study must target a distinguishable property such as semantic content across audience transformations, not just final-output checking.

**Baseline feasibility:**
Faithful attentionsteering requireslocalopenweight model and PE-LRP/backward/attentionhooks; potentially expensive for studentcompute. Treat as nearestmethod priority but only reproduce ifinternals/hardwareavailable. Promptgrounding baselines are easier but not reproduction of Serum. Do not claim wholemethod matched using only attributionwordsinprompt.

**Locators:**
- PDFp1: actual inspected title Faithfulness Serum; proceedingspp6622–6645,ACLJuly2026.
- PDFpp3–4, §3: hint-inducedflip setup, conditionalselection,LLMjudge and CT,openendedextension.
- PDFp5, §4Eq1: PE-LRPfirstanswertoken,question-tokenattention, layers17–19.
- PDFp6, §4/§5: staticstrength,distinct-1 threshold,TTalpha max15;MMLUsearchcounts.
- PDFp7, Tables1–4: mainmetrics,closedmodeldenominators,TTalphacaptionvsprose mismatch.
- PDFpp8–9, §5.1/Limitations: otherdatasets/ablations and paradigm/attentionlimits.
- PDFpp13–14, AppendixB: exactjudgeprompt,96×3humanvalidation,keywordsets.
- PDFpp18–19, AppendixC.3: guidedexplanations acknowledgehint but contain unsupportedcontradictoryarithmetic.
- PDFp22, AppendicesD/F/G: staticaddedbackwardpass,H10080GB,max24h,otherdatasetcounts.
- PDFpp23–24, AppendixH/I: decoding/targetablations andpseudocode.

**Corrections to interim:**
- Use actual PDF title Faithfulness Serum, with note officialmetadata used Faithful Serum.
- State it already evaluates final explanations with substantivehint-reliance judge and humanvalidation; noaudiencerewritingcontractfound is a narrower claim.
- Hardware/resources known after fulltext: H10080GB; do not describe low-cost on arbitrary localmachines from trainingfree claim.
- Distinguish staticextraPE-LRPbackwardpass from TTalpha repeatedlygenerated outputs; do not transfer minimal-cost claim toadaptivevariant.
- Avoid TTalpha andcreditbias denominator claims until internalcaption/prose inconsistencies are resolved.
