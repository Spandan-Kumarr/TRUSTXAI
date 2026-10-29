# Counterfactual full-text audit — Step 2 continuation

Read date:26October2026. FitCF,iFlip and TruthorTwist full texts inspected,including methods,experiments,limitations and relevant appendices; Randl base-paper analysis retained. No code executed or results reproduced. Locators use physical PDF pages.

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
- **Validity Metric:** Soft Label Flip Rate (SLFR), any predicted-label change. Section5.1 states same LLM for generation and classification. AppendixG.2 actually prompts the LLM with original+edited input together and asks yes/no whether their predicted categories differ. This paired judgment is not equivalent by definition to independent target-model label calls.
- **Quality Metrics:** GPT2 perplexity and normalized word-level Levenshtein distance TS (lower is more similar). This TS is lexical edit distance, not semantic similarity. Feature-attribution faithfulness is evaluated through comprehensiveness, sufficiency and Kendall tau with leave-one-out.
- **Ablation:** Remove important words; reduce demonstration count from2k to k; remove BERT flip verification. More demonstrations generally help SLFR; metric trade-offs vary by task/model.
- **Interpretation Caution:** Do not repeat a universal outperforming claim: Table1 contains metric/setting exceptions. For example Llama3-8B AGNews SHAP ZEROCF SLFR98.0% versus FITCF94.0%; the table does not show every FITCF variant improving every quantity.
- **Human Evaluation:** No human plausibility study; explicitly deferred because it requires annotations.

### Limitations

- English-only two-classification-task evaluation; no cross-domain decision-support deployment evidence.
- Only BERT predictions used for the attribution/demonstration-verifier role; contribution of other model architectures to those roles is explicitly unexplored.
- LLM used for final paired flip judgment differs from BERT used for grounding and demonstration checks. AppendixG.1 assumes similar classifier accuracies imply consistent SLFR tendencies, which is not a proof of per-example agreement.
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
- PDF pp15–16 / printed1190–1191: AppendixG paired yes/no evaluation prompt and similarity-of-accuracies assumption

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

3classificationtasks,200selectedtexts each;dependabilityperturbation,similarityandvalidity. Gradientmethods up to9B;prompt-only experiments larger.

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
- **Evaluator Protocol:** Judge assigns a class to the edited input using a direct category-only task prompt (AppendixD/Fig10). LFR compares edited-input predicted label against ORIGINAL DATASET label. It is not the paired original+edited yes/no meta-judgment shown in FitCF AppendixG.
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