# Full-text Review Notes — Step 2 continuation

Updated27 October2026. Physical PDF pages and sections are supplied in thematic notes. These are source audits, not reproduced experiments.

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
Appendix F.6 Table12 e-SNLI: random-word feedback29.28% mean, IWF-Pmt30.10%, IWF-Attn27.69%, IWF-IG28.39%. Random trials use3seeds; result shows selected-word quality need not explain most improvement. Table13 acknowledgment-in-topN rates also compare to random.


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
ECQA first500instances due API cost; TriviaQA-LongBench300triples; BalancedCOPA500 questions. Appendix G addsMedMCQA and closed-model targets; exact additional subset size not stated in cited table.

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
- PDFpp15–17 Appendix G: additionaldomain/model results and scope
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
Table1 LlamaMMLU general metadata hint1000 selectedflips: judge acknowledgment3.0→10.0%; CT2.9→6.9%. Sycophancy judge36.1→47.7%; CT47→65%. These specific conditional outcomes must not become universal validity/faithfulness improvements.

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



# Counterfactual full-text audit — Step 2 continuation

Read date:26 October2026. FitCF,iFlip and TruthorTwist full texts inspected,including methods,experiments,limitations and relevant appendices; Randl base-paper analysis retained. No code executed or results reproduced. Locators use physical PDF pages.

## [L26] FITCF: A Framework for Automatic Feature Importance-guided Counterfactual Example Generation

### Method

- **Decision And Generator Roles:** ZEROCF obtains y_pred and feature attributions from a BERT classifier fine-tuned on the target dataset. An LLM generates edited text from original input, BERT prediction and attributed words. FITCF clusters SBERT embeddings with k-means, selects near-centroid examples, generates ZEROCF edits, and uses the same BERT to remove non-flipping demonstration pairs. More near-centroid examples are selected until the required demonstration count is obtained. The resulting demonstrations plus feature words condition a final few-shot LLM generation.
- **Attribution:** Gradient, Integrated Gradients, LIME and SHAP via FERRET; special-token words are replaced and subwords merged. The study uses attribution for BERT, not the generative LLM itself.
- **Validation:** BERT label verification applies to constructed demonstration pairs. The paper does not specify that every final generated counterfactual must be rejected until it passes the same BERT checker.
- **Budget And Stopping:** Demonstration count l=2k:10 for AG News,8 for SST2. If too few generated demonstration edits flip BERT, additional near-centroid instances are iteratively selected. No general finite retry guarantee is stated in the method.
- **Models:** Generation: Llama3-8B, Qwen2.5-32B and Qwen2.5-72B; attribution/demonstration verification: fine-tuned BERT. Qwen versions are GPTQ Int4; experiments use single RTX A6000/A100/H100 depending model.

### Evaluation

- **Datasets:** AG News four-class topic and SST2 binary sentiment. Main experimental N is not clearly supplied in inspected main text; do not infer it from percentages.
- **Baselines:** Polyjuice, BAE, FIZLE; compare ZEROCF and FITCF variants across four attribution methods.
- **Validity Metric:** Soft Label Flip Rate (SLFR), any predicted-label change. Section5.1 states same LLM for generation and classification. Appendix G.2 actually prompts the LLM with original+edited input together and asks yes/no whether their predicted categories differ. This paired judgment is not equivalent by definition to independent target-model label calls.
- **Quality Metrics:** GPT2 perplexity and normalized word-level Levenshtein distance TS (lower is more similar). This TS is lexical edit distance, not semantic similarity. Feature-attribution faithfulness is evaluated through comprehensiveness, sufficiency and Kendall tau with leave-one-out.
- **Ablation:** Remove important words; reduce demonstration count from2k to k; remove BERT flip verification. More demonstrations generally help SLFR; metric trade-offs vary by task/model.
- **Interpretation Caution:** Do not repeat a universal outperforming claim: Table1 contains metric/setting exceptions. For example Llama3-8B AGNews SHAP ZEROCF SLFR98.0% versus FITCF94.0%; the table does not show every FITCF variant improving every quantity.
- **Human Evaluation:** No human plausibility study; explicitly deferred because it requires annotations.

### Limitations

- English-only two-classification-task evaluation; no cross-domain decision-support deployment evidence.
- Only BERT predictions used for the attribution/demonstration-verifier role; contribution of other model architectures to those roles is explicitly unexplored.
- LLM used for final paired flip judgment differs from BERT used for grounding and demonstration checks. Appendix G.1 assumes similar classifier accuracies imply consistent SLFR tendencies, which is not a proof of per-example agreement.
- Fluency and edit distance are not semantic adequacy or real-world actionability.
- No study of human trust, audience-adaptation preservation or final natural-language claims.

### Claim Preservation Overlap

The paper covers attribution-guided counterfactual construction and verified demonstrations, not a multi-audience final explanation renderer. I found no protocol for preserving target-decision claims across novice/expert rewrites or independent auditing of such rendered claims in the inspected method/results/appendices. This is a bounded paper-level observation, not a global novelty claim.

### Novelty Implication

Attribution-guided counterfactual generation, BERT label-flip filtering, verified few-shot demonstrations and component ablations are established prior art. A thesis keeping the decision LLM fixed must explicitly change attribution/checker access rather than silently adopt cross-model evidence.

### Baseline Feasibility

Useful algorithmic predecessor. Faithful reproduction needs BERT checkpoint, attribution toolchain, SBERT/k-means demonstration construction and original generator/paired-evaluation prompts. Replacing BERT with the target LLM or replacing paired judgment with independent label calls is an adaptation and must be labelled. Heavy32B/72B variants are optional resource-heavy comparisons;8B still requires GPU resources.

### Locators

- PDF pp3–4 / printed1178–1179: §§3.1–3.3 methodology, BERT roles and demo verification
- PDF p5 / printed1180: §5.1 metrics and footnote11 targetLLM evaluation
- PDF pp6–8 / printed1181–1183: Table1, ablations and results
- PDF p9 / printed1184: limitations
- PDF pp13–14 / printed1188–1189: AppendixB/F, BERT models and hardware
- PDF pp15–16 / printed1190–1191: Appendix G paired yes/no evaluation prompt and similarity-of-accuracies assumption

### Corrections To Interim

- Distinguish BERT attribution/demonstration filtering from finalLLM flip judgment.
- Do not describe FITCF as validating every final CF against an unchanged generative decisionLLM.
- Describe TS as normalized word edit distance, not semantic similarity.
- Check reported outcomes rather than adopting universal author outperformance wording.

## [L38] iFlip: Iterative Feedback-driven Counterfactual Example Refinement

### Method

- **Roles:** Separate counterfactual generator G and explained classifier M. Initial y=M(x), choose desired y_tilde !=y. Generate x_cf0. If M(x_cf)=y_tilde stop; otherwise iteratively refine with feedback and recheck.
- **Models:** Generators OLMo2-7B, Qwen3-32B, Llama3.3-70B. Main explained classifiers are task-specific BERT. Additional experiments use RoBERTa. AppendixC.2 tests BERT-to-RoBERTa transfer of candidate edits or feedback, not generativeLLM decision targets.
- **Feedback:** Explained-model predicted-label maximum softmax confidence; SHAP,AttnLRP,Gradient×Input,LIME important words; LLM natural-language feedback; or combined confidence+SHAP+NL.
- **Budget:** Formal method allows initial candidate plus up toK refinement steps; experiment setting lists5iterations (with studies up to15). Generation temperature0.9,top-p0.95,top-k50,max-new-tokens4096. Top important words max(10,floor(0.1*original_words)). Explained-model majority voting over512-token windows/stride256.
- **Stopping:** Early stop after desired target-class success; otherwise stop at maxiterations. No unconditional100%success guarantee. They compare with nofeedback, randomfeedback, least-attributedfeedback and noearlystop.

### Evaluation

- **Datasets:** IMDb, AGNews and SNLI with premise/hypothesis edits separately. Dataset sources given; main per-condition sampleN not clearly established in inspected description, so no per-input rate uncertainty reconstructed.
- **Baselines:** CGG, FIZLEnaive, Causal What-Ifs. Main Table1 compares generators with BERT as explained model; AppendixC.1 compares RoBERTa.
- **Validity Metric:** LFR equation counts any label change M(x)!=M(x_cf). This is weaker than formal early-stopping target success M(x_cf)=y_tilde in multiclass tasks. AppendixJ.1 explicitly illustrates undesired NEUTRAL→ENTAILMENT when CONTRADICTION was intended. Report target-success and any-flip separately in thesis.
- **Quality Metrics:** Sentence embedding cosine similarity using all-MiniLM-L6-v2 is used as minimality proxy; GPT2 perplexity for fluency. Embedding similarity is not a literal minimum-edit or semantic-validity proof.
- **Headline Numbers:** FullPDF intro/§6.1 reports78.8%relative validity gain with4.95%lower similarity averaged across selected baselines/settings; this differs from officialXML abstract57.8%and is NOT a reproduced result. Prefer table-specific contextual comparisons if citing.
- **User Study:** 3 English-proficient participants evaluate10randomAGNews source examples under3methods (CGG,FIZLE,iFlip-NL) with6pointLikert completeness,overall satisfaction,feasibility. Reported human means e.g overall satisfaction2.67,2.93,5.13 respectively; tiny complementary study, not general evidence of appropriate reliance.
- **Judge Study:** Gemma3-27B,GPT-OSS-120B,DeepSeek-R1 rate same subjective dimensions; LLM-judge alignment is not independent task correctness.
- **Cost:** Table6 hardware: OLMo2-7B1×V10032GB;Qwen3-32B1×H10080GB;Llama3.3-70B2×H10080GB. Table7 AGNews OLMo2 confidence7.30h vsNL17.90h for reported run; sample denominator is not established here, so do not derive per-case latency.
- **Additional Tests:** CDA training and ID/OOD/human-CF tests; no general consistency guarantee, with some NLI outcomes worse than baseline. Early stopping prevents later candidate flip-backs. Trade-offs and random/least-attributed controls already in paper.

### Limitations

- English-only; limited attribution-method set; expensive iterative generation, especially NL feedback.
- 3-person10-case user study is explicitly limited; satisfaction/feasibility ratings do not measure human decision correctness or calibrated trust.
- Main targets are BERT/RoBERTa rather than instruction-tuned generativeLLM decisions, despite LLM generators.
- Any-flip reporting and desired-target stopping are distinct success definitions.
- Cosine similarity and PPL do not establish complete semantic adequacy or real-world actionability.
- Isolated appendix consistency issues: Table33 labels originalbusiness/counterfactualbusiness but isFlipYes; another row business→sport but isFlipNo. AppendixL introductory dimension names differ from its detailed scoring definitions. These are reporting/protocol-document inconsistencies to check before reuse, not proof that whole experiments are invalid.

### Claim Preservation Overlap

The paper validates edited inputs and rates their explanatory quality; it does not implement/test an audience-adapted natural-language explanation layer preserving claims from a fixed decision-evidence record. I found no novice/expert rewrite comparison or final-claim preservation audit. However, confidence/attribution/NLfeedback, target-class checks,earlystop,randomfeedback controls, budgets and failure examples already overlap prospective supporting components.

### Novelty Implication

A bounded feedback+earlystopping CF loop, sensitivity to important words, validity/similarity/cost trade-off, and transfer tests cannot be claimed new. The main decision-model boundary should be explicit; applying to generativeLLM targets requires an actual justified adaptation and evidence.

### Baseline Feasibility

Confidence-only and NLfeedback versions are implementable candidates but currently trained-classifier-target baselines. Whitebox attribution needs gradient/attention access.8B/7B generator variants still GPUheavy;32B/70B models are not essential to a bounded thesis pilot. Budget-matched comparisons must account for initial generation, feedback and retries. No code executed.

### Locators

- PDF pp1–3 / printed749–751: full title, formal generation/check/refine, feedback and model roles
- PDF p4 / printed752: LFR,embedding/PPL and3participant10case user study;footnote4BERT/RoBERTa
- PDF p5 / printed753: Table1 main results and ablation definitions
- PDF pp6–9 / printed754–757: results,trade-off,earlystopping,limitations and ethics
- PDF pp13–17 / printed761–765: AppendixB/C hardware,parameters,model table and BERT/RoBERTa transfer setting
- PDF p22 / printed770: AppendixJ undesired flip and failure cases
- PDF p28 / printed776: AppendixL annotation instructions
- PDF pp29–31 / printed777–779: judge prompt andper-rater/error tables,includingTable33

### Corrections To Interim

- Update fullPDF title to include Example Refinement; XML title differs.
- Do not reuse XML57.8%result: currentPDF abstractremovedit andintroreports78.8%relative gainunderits aggregation.
- Main explained models BERT/RoBERTa, not generatorLLMs.
- Separate desired-target validity from reported any-flip LFR.
- Early stopping,budget/quality trade-off and failure controls already are explicit prior art.

## [L02] Mind the gap: from plausible to valid self-explanations in large language models

### Method

Previously reviewed base paper uses target generativeLLM classification and samples counterfactual candidates by alternative class; reclassifies candidates,retainsvalidones,selects by similarity×target probability,and stops underboundedclasswisebudget.

### Evaluation

3classificationtasks,200 selectedtexts each;dependabilityperturbation,similarityandvalidity. Gradientmethods up to9B;prompt-only experiments larger.

### Limitations

Classification/decoder-only;noactionability;prompt-sensitivitylimited;finite retriesmayfail;validCFdoesnotproveinternalfaithfulness.

### Claim Preservation Overlap

Noaudience-adaptationclaimpreservationprotocol;itisthecloser same-generativeLLM baseline for reclassification than BERT-targetmethods.

### Novelty Implication

Generation/reclassification/retry and empirical validity testing alreadypriorart.

### Baseline Feasibility

Reproduce smallopenmodel prompting-basedcandidatebaselineandexplicitlydistinguish observedlabeltargetsuccessfromsurfaceplausibility;respectGPLv3codeif reused.

### Locators

- PDFpp8,10–11,16–20,35

### Corrections To Interim

- Preserve distinction between dependability and fullinternalfaithfulness.

## [L43] Truth or Twist? Optimal Model Selection for Reliable Label Flipping Evaluation in LLM-based Counterfactuals

### Method

- **Scope:** Studies semantic/ground-truth label validity for counterfactual data augmentation (CDA), explicitly distinguished from explaining a particular model by changing its prediction (p1footnote2).
- **Generator Judge Roles:** Counterfactuals generated by FIZLE or FLARE with Llama3-{8B,70B}/Qwen2.5-{14B,32B}. Judges grouped as same model, same family, independent with/without target-data fine-tuning, or distillation-related;15judges including trainedBERT/RoBERTa and multiple off-the-shelfLLMs, plus majority ensemble.
- **Evaluator Protocol:** Judge assigns a class to the edited input using a direct category-only task prompt (AppendixD/Fig10). LFR compares edited-input predicted label against ORIGINAL DATASET label. It is not the paired original+edited yes/no meta-judgment shown in FitCF Appendix G.
- **Human Alignment:** Human-label edited inputs define semantic reference labels; compare automatic and human aggregate LFR via absolute closeness/rank, most-to-least alignment ratio and Pearson correlation. This evaluates semantic label agreement, not access to model-internal reasoning.

### Evaluation

- **Datasets:** AGNews,SST2,SNLI. User study90nativeEnglishannotators;45sourceindices sampled/dataset;eachsubset evaluated by2annotators,authorsadjudicateties;15counterfactuals/annotator described. Reported Cohen kappa0.55 (moderateagreement). Do not reconstruct a unique totalannotation count fromthese summaries.
- **Main Result:** Authors report independent non-fine-tuned judges align best on average with humanLFR, but substantial discrepancy remains; ordinary downstream taskperformance does not guarantee label-flipjudge alignment. Their aggregate best relationship ranking4.15/Pearson0.47 are experiment-specific, not guarantee of anyindependentjudge.
- **Augmentation:** CDA uses500originaltraininginstances plus generatedcounterfactuals, classifiertrainedforCDA distinct fromfine-tunedjudgecheckpoint. Evaluates originaltestsets andhumanlabelledCFset, excludesselectedCFs/originals fromtraining. AppendixH reports moderateSpearmancorrelation0.41forAGNews betweenrelationshipranking andCFtestperformance;weak onotherdatasets.
- **Important Boundary:** A semantic judge can disagree with the targetmodel while being morehuman-aligned. Its independentjudgment cannot replace reclassification with the fixed targetLLM when testing behavioralCF validity.

### Limitations

- English-only;generatorfamiliesQwen/Llama and selectedjudges limitgeneralization.
- Observed model-relationship associations do not isolate a causal effect of independence, finetuning or contamination; models differ in capability and training.
- Human labels for ambiguous editedtext have onlymoderateagreement and adjudication;call them annotatedreference labelsratherthanunquestionabletruth.
- Paper concentratesonlabel-flipvalidity/CDA,notcomprehensiveCF quality,fairness,actionabilityoraudience-adaptedclaimpreservation.
- The claim of fully automatedCDA inadequacy is limited to studiedsystems/settings. No theorem that all automationis impossible.

### Claim Preservation Overlap

Supplies strong prior art for evaluating the evaluator and distinguishing humansemantic validCFs fromtargetmodelbehavior. It doesnot provide an audience rewriting layer or claim-level preservation protocol. It narrows any purported novel independent-verifier argument.

### Novelty Implication

Judge-selection effects, weak human/model alignment and the distinction semantic-validity vsbehavioralflip are existing research insights. Thesis should retain BOTH constructs if relevant ratherthaninventingthisdistinction or equatingindependentjudgeagreementwithfaithfulness.

### Baseline Feasibility

Use as evaluation-design foundation; reproducingall4generators×15judges isresourceheavyandunnecessaryforpilot. A limited clearlylabelled independentsemanticcheck mayaugment same-targetreclassification, withhumanannotationonfeasiblesubset. No authors codeexecuted.

### Locators

- PDFp1/printed80: scope distinction andfootnote2
- PDFpp2–3/printed81–82: metric,generator/judgerelationships,methods,datasets
- PDFp4/printed83:90annotators,45indices,2raters,adjudication,kappa0.55 andalignmentmetrics
- PDFpp5–6/printed84–85:results,limitations,ethics
- PDFpp9–10/printed88–89:modeltables,humanannotation setup
- PDFp13/printed92:Figure10directcategory-onlyprompts
- PDFp14/printed93:annotationguidelines
- PDFpp16–18/printed95–97:CDA500instances,CFholdoutandtable-specificresults

### Corrections To Interim

- Newprimaryfulltextreference;notpreviouslyinthe38recordlibrary.
- Independentjudge recommendation concerns human-ground-truthCDA validity;do nottransferitunqualifiedtosame-targetbehavioralfaithfulness.
- Ordinaryclassificationaccuracydoesnotestablishsemanticjudgeaccuracyonsyntheticambiguousedits.

## Candidate-gap conclusion

The papers motivate a strict boundary between target prediction, generator, explanatory evidence, semantic judge and user-facing claims. The exact novice/expert final-claim preservation protocol under consideration is not presented in these three papers; this bounded comparison does not prove global novelty. Independentsemanticjudges and fixedtargetbehavioralchecksanswerdifferentquestions.


# Full-text audit: human-facing explanation research

Reviewed 26 October 2026. Locators use physical PDF pages. Main methods, experiments, limitations and relevant appendices were inspected. No experiments were reproduced.

## L15 — InterroLang: Exploring NLP Models and Datasets through Dialogue-based Explanations

**Method:** A modular dialogue engine parses questions into executable operations. Its execution engine inserts results into mainly rule/template-based responses. The explained targets are BERT-type models for DailyDialog dialogue acts, BoolQ yes/no answers and OLID offensive/nonoffensive classification. It uses Captum Integrated Gradients, Polyjuice counterfactuals, OpenAttack PWWS adversarial edits and nlpaug augmentations. Rationales are separate prompted outputs conditioned on input and target prediction; ChatGPT demonstrations support Dolly few-shot rationalization. Clarification concerns intent/slots and history, rather than audience-profile rewriting.

**Evaluation:** Task A recruits 10 in-house computational-linguistics/computer-science students to rate turns and dialogues. Task B recruits six participants: four paper authors and two Task A students. Each receives nine instances across three datasets and a randomized itinerary of explanation operations, stopping when ready to guess the target-model output. It measures simulatability, including possibly incorrect model outputs, not real task correctness or appropriate reliance. No separate randomized single-turn control arm is described. Appendix F.2 instructs participants to disregard wrong parses and retry until the intended operation is returned.

**Details:**
- participants: Task A: 10 students. Task B: six participants, including four authors and two Task A students. These are not disjoint samples.
- reported_Table_5: Operation-associated Sim(all): free-text rationale 94.74%, local attribution 91.43%, counterfactual 85.00%; average conversational turns 3.70, 3.85 and 4.14 respectively. These overlapping conversational endpoints are not isolated randomized method effects.
- collected_data: 1,449 Task A dialogue turns and 188 Task B dialogue turns.

**Limitations:** Small in-house/expert samples, with four authors in Task B; BERT-type task-specific targets; no direct model comparison or automated model-improvement loop. Subjective correctness is not semantic claim verification. Polyjuice often failed to produce a label-flipping perturbation. Some explanations induced false trust. Simulatability does not establish human decision utility.

**Overlap:** Close system prior art for executable evidence, dialogue, attribution, counterfactuals and natural-language rationales. Most responses are template-filled; generated rationales are separate prompted outputs. Inspected methods, studies and appendices do not describe checking an audience-rewritten final explanation for supported/contradicted/unsupported decision, attribution and counterfactual claims, nor testing preservation across audience transformations with release gating. This is a bounded observation about the described methods, not proof about every possible code extension.

**Novelty implication:** Conversational attribution-plus-counterfactual-plus-rationale integration is not new. A fixed generative decision-LLM target differs from this paper, but that model change alone does not establish novelty. Its human evidence must not be described as a universal causal benefit of dialogue over one-off explanation.

**Feasibility:** Useful architecture and operation taxonomy; not automatically an apples-to-apples numerical baseline for a different generative decision model. Integrated Gradients requires internal access. Any adapted pipeline needs clear target and method attribution.

**Locators:**
- Sections 2 and Figure 2, PDF pp. 2–4 (printed 5400–5402): architecture and dialogue.
- Sections 3–4, PDF pp. 5–6 (printed 5403–5404): targets and methods.
- Section 5.3 and Tables 3–5, PDF pp. 6–8 (printed 5404–5406): human studies/results.
- Limitations, PDF p. 9 (printed 5407).
- Appendix F.2/Figure 8, PDF p. 20 (printed 5418): randomized itinerary and wrong-parse retry instruction.

**Corrections to interim:**
- Replace a broad superiority claim over one-off explanation with the actual small sequential simulatability study; there is no explicit randomized one-off control arm.
- Disclose four authors in the six-person simulatability sample.
- Keep simulation accuracy separate from task correctness and appropriate reliance.

## L20 — On Evaluating Explanation Utility for Human-AI Decision Making in NLP

**Method:** A framework for application-grounded human–AI evaluation and dataset choice, followed by ContractNLI/NDAs case studies using task-finetuned Flan-T5-3B. Criteria cover realistic application and inputs, meaningful effort/difficulty, nonbenign risk and suitable model performance. Seventeen of 53 datasets pass reliance/complementary-performance suitability; six of those have nonbenign hazards and two are removed for quality, leaving four prioritized datasets. Studies compare prediction/confidence, abstention/role/record framing, outcome feedback, Input×Gradient highlights and EK-FAC influential examples.

**Evaluation:** Study I asks humans to make all final decisions under five conditions. There are 35–40 responses per condition, up to six instances per participant and 1,108 annotations; the total unique participant count across conditions is not unambiguously stated. Recruitment requires legal-related education/work and English fluency, with qualification/attention checks and delayed AI reveal. Study II uses idealized deferral: all shown instances are predictor errors and users are warned. It has 23 participants in the highlights condition and 20 in the examples condition, with 73 completed instances.

**Details:**
- prioritized_datasets: ['EvidenceInference-v2 with retrieval', 'SciFact-Open', 'ContractNLI', 'ILDC']
- Study_I_conditions: ['P1: prediction and temperature-scaled confidence', 'P2: adds abstention, role and prior-record framing', 'P3: adds outcome feedback', 'P4: adds Input×Gradient highlights', 'P5: adds three EK-FAC influential training examples, themselves highlighted']
- Study_I_results: All human–AI conditions are at least 9.5 F1 points below the model alone. Table 3 model-minus-human gaps are 17.0, 18.5, 10.7, 9.6 and 10.0 respectively. Conditions also change framing/feedback, so differences cannot all be attributed to explanations.
- Study_II_results: Best tested deferral recall is 30%, motivating the idealized study assumption. Human micro-F1 is 34.2% on 73 model-error cases. Mean self-reported explanation impact is 2.56. The projected 92.6% team performance assumes perfect deferral and is not a measured deployed-system result.
- label_quality_caution: An author-reviewed subset of 29 cases changes 11 labels. The resulting score changes concern that subset, not a wholly cleaned benchmark.

**Limitations:** Limited tasks, participants, examples and explanation types; length is an imperfect effort proxy and risk judgments are subjective. Better contemporary models can change task suitability. Gold-label quality matters. Simulatability, perceived helpfulness and real human–AI utility are distinct. Do not infer a unique participant count by dividing annotations.

**Overlap:** The inspected methods/studies do not implement audience rewriting followed by claim-level checking of preserved decision, attribution or counterfactual facts. Role framing concerns participant context; explanations are confidence, highlights and influential examples. This is an evaluation-design source rather than a competing NLE-generation method.

**Novelty implication:** Does not settle the narrow supported-claim-preservation candidate. It strongly constrains human-benefit claims: brief sentiment/rationale benchmarks are not automatically validated real-world decision-support studies.

**Feasibility:** Use the full protocol as an evaluation-design reference, not as an algorithm baseline. A legal user study needs realistic expertise, consent, qualification checks and adequate time. Reassess the selected contemporary LLM rather than inheriting their Flan-T5 task suitability.

**Locators:**
- Section 2, PDF pp. 2–3: evaluation distinctions.
- Section 3, PDF pp. 3–6: dataset criteria and the 17/53 versus four-prioritized distinction.
- Section 4, Figure 1 and Table 3, PDF pp. 6–8: Study I.
- Section 5, PDF pp. 8–9: Study II and perfect-deferral assumption.
- Section 7, PDF p. 10: limitations.
- Appendix D.3–D.6, PDF pp. 22–24: recruitment, consent, payment and process.
- Table 20, PDF p. 31: perfect-deferral projection.

**Corrections to interim:**
- Refine “only four suitable datasets” to 17 suitable for reliance/complementary performance, with four prioritized after risk and quality filtering.
- Separate the idealized 92.6% projection from observed human performance.
- Keep negative results task-specific and distinguish explanation effects from framing/feedback differences.

## L34 — Attribute-Based Activation Steering of LLMs for Group-Specific Explanation Generation

**Method:** Extracts style/knowledge attributes from Stack Exchange answers for 11 groups using Qwen models and embedding clustering, retaining 1,250 attributes. For each group it selects top style and knowledge attributes, constructs positive-minus-negated attribute activation vectors, weights/sums them and injects steering into selected three-layer windows. It compares group-only/group-plus-attribute prompts, standard Konen steering and proposed attribute steering. The outputs are topical educational explanations, not explanations of a fixed classifier decision.

**Evaluation:** Uses 600 ELI5 test questions and 97 science questions across 11 groups, with three roughly 7–8B model families plus a Qwen32B ablation. Tuning uses 100 ELI5 validation questions. Specificity is estimated by a learned group classifier. Factuality decomposes generated text into atomic facts and validates against Wikipedia using open FActScore; only the science questions receive factuality scores. The human study has nine Upwork experts: three each in biology, game development and philosophy. They rate 50 questions (25 science, 25 ELI5), each with three method outputs shuffled within question, on 1–5 steering, plausibility and helpfulness scales.

**Details:**
- Table_2: Prompting: steering 3.12, plausibility 4.56, helpfulness 4.03, harmonic mean 3.81. Proposed: 4.17, 3.87, 3.64, 3.88. Konen: 3.46, 2.75, 2.70, 2.93. Thus the proposed method improves steering but does not exceed prompting on helpfulness or plausibility.
- agreement_and_subsets: Krippendorff alpha ranges 0.178–0.489. Science-question helpfulness 4.01 (prompting) versus 3.90 (proposed) is not significantly different.
- factuality: OLMo-2-1124-7B-SFT extracts atomic facts; gemma-3-4b-it validates them against Wikipedia as of 1 April 2023. Failed extraction on nonsensical outputs is assigned score zero.
- compute: Appendix B.1 reports a shared cluster with 16 H200 and eight A100 GPUs, approximately 200 GPU hours total. A small prompting baseline does not necessarily require those resources.
- ablation_precision: The alternative-attribute-extractor robustness check compares steering-vector cosine similarity, rather than rerunning the entire generation/evaluation pipeline, due to compute cost.

**Limitations:** Group averages may stereotype and miss individual knowledge; Stack Exchange forum participation need not represent professions. English and fixed groups only. LLM-derived attributes and factuality judgments inherit errors; authors interpret factuality relatively, not as absolute truth. Greater specificity can reduce factuality or drift away from answering the question. Human groups were selected among the best-performing groups, sample size is small and agreement low. Human comparison bundles attributes and activation versus group-only baselines, so it is not an isolated activation-effect estimate.

**Overlap:** Direct overlap: the paper already performs atomic-fact checking on generated audience-tailored explanations against a source (Wikipedia). Thus generic audience adaptation plus postgeneration fact checking is prior art. However, inspected methods/evaluation do not preserve a previously fixed target-LLM decision, signed attribution evidence, validated counterfactual outcomes or uncertainty claims across paired rewrites. Factuality concerns topical encyclopedia facts, and scoring is evaluation rather than an output-release gate.

**Novelty implication:** The candidate must specify same-target decision evidence and a distinct preservation mechanism or diagnostic protocol. Audience adaptation, atomic decomposition, factuality checking and trade-off measurement each already exist. Helpful human effects cannot be inferred from steering success.

**Feasibility:** Prompt-based group-only and group-plus-attributes conditions are feasible adaptation comparators. The full activation pipeline needs internal access and substantial data/model infrastructure. Control prompt information and evaluate the same target-decision/evidence setting; do not directly compare its encyclopedia factuality scores with classifier-evidence preservation scores.

**Locators:**
- Section 3, PDF pp. 3–4 (printed 2931–2932): attributes, activation differences and steering.
- Sections 4–5, PDF pp. 4–6 (printed 2932–2934): data, models, tuning and metrics.
- Section 6/Table 1, PDF p. 7 (printed 2935): automatic trade-off.
- Section 6.3/Table 2, PDF pp. 8–9 (printed 2936–2937): human study and results.
- Sections 8–9, PDF p. 10 (printed 2938): limitations and ethics.
- Appendix A.4.4, PDF pp. 17–18 (printed 2945–2946): vector-only robustness check.
- Appendix B.1/B.3/B.4, PDF pp. 18–19 (printed 2946–2947): compute, specificity models and FActScore.
- Appendix B.9, PDF pp. 20–22 (printed 2948–2950): group selection, randomization and instructions.

**Corrections to interim:**
- Strengthen the overlap: atomic-fact support of generated group-specific explanations is already evaluated. Generic postgeneration checks are not an unoccupied gap.
- Report the mixed human outcomes: prompting has higher helpfulness/plausibility, while the proposed method has higher steering and harmonic mean.
- Do not call vector-cosine robustness evidence a full generation rerun.
- Avoid a universal best-harmonic-mean claim: Table 1 Ministral group-plus-attributes Konen baseline has 0.274 versus proposed 0.260.



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

Behavioral self-consistency, prediction-support log odds, contribution-profile alignment and activation-patching alignment are distinct constructs. None of the four inspected full papers develops the exact fixed-decision audience-rewriting/typed-claim preservation pipeline proposed as a candidate in Step 2, but this bounded observation is not an exhaustive novelty proof. Diagnostic testing itself is established by Causal Diagnosticity and others. A practical thesis should use independent held-out support labels for its defined claim target, report valid paraphrases as well as injected errors, keep coverage/cost visible, and label latent-faithfulness claims conservatively.



## [L39] Faithfulness vs. Plausibility: On the (Un)Reliability of Explanations from Large Language Models

**Method:** Conceptual review distinguishing plausibility and model faithfulness, covering token importance, counterfactuals and CoT; application-specific transparency discussion.

**Evaluation:** Illustrative examples and synthesis of prior studies; not a new controlled benchmark or measured improvement.

**Limitations:** Conceptual definitions and recommendations do not certify a method; domain examples do not establish empirical deployment outcomes.

**Claim Preservation Overlap:** Already argues for meeting both user-facing and model-facing needs; no specified typed decision-evidence preservation experiment across audience rewrites in inspected text.

**Novelty Implication:** Motivation is established; do not claim invention of the plausibility-faithfulness distinction.

**Baseline Feasibility:** Conceptual foundation rather than executable baseline.

**Locators:** ['§§2–4, PDF pp2–5', '§§5–7, PDF pp5–9']

## [L40] Measuring Faithfulness in Chain-of-Thought Reasoning

**Method:** Intervenes on generated CoT by early answering, mistakes, filler tokens and paraphrasing; measures subsequent answers. Main experiments use a175B RLHF model; model-size experiments are separate.

**Evaluation:** Eight multiple-choice tasks;100 reasoning samples/problem, temperature0.8 and nucleus p0.95. Task-dependent effects; paraphrase experiment isolates phrasing by hiding the original question from the paraphraser and preserving a later continuation.

**Limitations:** §5 explicitly lacks independent access to true internal reasoning. No guarantee that behavioral robustness establishes complete faithfulness. Proprietary models and sampling cost limit direct reproduction.

**Claim Preservation Overlap:** Paraphrase intervention is existing prior art; not audience-specific rendering of a fixed decision/evidence record.

**Novelty Implication:** Do not claim novel paraphrase robustness or first behavioral intervention tests.

**Baseline Feasibility:** Use its controlled-intervention logic; repeating175B/100samples is not required for a bounded thesis pilot.

**Locators:** ['§2.1, PDF pp2–3', '§§2.3–2.6, PDF pp3–7', '§3 and §5, PDF pp7–9']

## [L41] Verification and Refinement of Natural Language Explanations through LLM-Symbolic Theorem Proving

**Method:** Explanation-Refiner converts NLI premises, hypotheses and explanatory facts into Isabelle/HOL theories using event semantics/FOL, corrects syntax, proposes proof steps, and refines explanations using failed proof feedback.

**Evaluation:** Evaluates formalized entailment and refinement on e-SNLI, QASC, WorldTree with open/closed LLMs; measures logical validity and autoformalization errors.

**Limitations:** Guarantees concern the formalized theory under its assumptions; natural-language-to-logic translation can lose semantics. Logical support is distinct from tracing an unchanged LLM decision. Authors caution that safety/correctness guarantees in critical applications require further investigation.

**Claim Preservation Overlap:** Formal external checks, sentence-level semantic preservation and refinement already exist. Not an inspected multi-audience preservation protocol tied to target-LLM attributions and behavioralCF outcomes.

**Novelty Implication:** Formalizing claims or adding an external checker alone is not new; this is important direct prior art.

**Baseline Feasibility:** Architecture comparator; full reproduction adds Isabelle, formalization prompts and iterative model calls.

**Locators:** ['§2 and §3, PDF pp2–5', '§4, PDF pp5–8', '§5.3, Conclusion and Limitations, PDF p9']
