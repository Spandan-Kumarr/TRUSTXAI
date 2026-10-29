# Step 2 — Literature Review and Research-Gap Assessment

**Thesis:** A Trustworthy & Explainable AI Framework for Large Language Model-Based Decision Support Systems  
**Student:** Spandan Kumar Gope · 22MIP10039 · Supervisor: Dr. Rajit Nair  
**Version:** 2.0 · 27 October 2026  
**Coverage:** Initial search 26 October; primary-text continuation 26–27 October 2026  
**Status:** Bounded Step 2 review completed; candidate contribution remains to be specified in Step 3.

## 1. Outcome

The research area supports a serious thesis, but the broad combination of LLM decisions, XAI, critique, counterfactual checking and audience adaptation is established prior art. Neither a new interface nor a renamed integration establishes a new research contribution.

The updated evidence library contains **43 curated records**, with **19 full-text audits including the two supplied base papers**. Other records retain explicit abstract, repository or targeted-reading labels. Full-text audits inspect methods, evaluation, limitations and relevant appendices; they are not reproductions. Detailed study notes and physical-page locators accompany this report.

The strongest direction for Step 3 is to investigate **preservation of typed evidence claims about a fixed target-LLM decision across audience transformations**, with independent diagnostic tests, output coverage and cost. This is a candidate contribution space. The inspected closest protocols do not demonstrate this exact combined evaluation, but that bounded finding does not prove field-wide novelty. The mechanism and its difference from existing methods must be specified next.

## 2. Search coverage and source verification

The initial official-ACL metadata screen covered 30 selected collections containing 38,613 paper records and 754 title-keyword matches. Forty collection-URL attempts included 10 incorrect Findings filenames, subsequently corrected. The initial 38 curated records were selected through that screen plus primary-repository and citation tracing, not full-text assessment of every match. This is a traceable bounded review, not an exhaustive systematic review.

The continuation resolved the previous network blocker: ACL PDFs, arXiv and Crossref returned successful responses. Sixteen priority ACL PDFs were downloaded, followed by two versioned arXiv PDFs and three additional citation-traced papers. Downloading alone is not counted as reading. The library separately identifies substantive full-text audits and targeted/available-but-not-audited texts.

Direct Crossref discovery searches identified Explanation-Refiner [L41] and concept-explanation evaluation [L42]; an iFlip reference led to Truth or Twist [L43] in the official 2025 INLG collection. Two of four Crossref discovery requests failed with 429/500 and were not treated as successful searches. Google returned a JavaScript interstitial, which supplied no usable search results. No Scopus/Web of Science coverage or indexing verification is claimed.

Crossref resolves the first base paper's online publication to **22 December 2025**; the retrieved record supplies no volume/issue. The second base paper is *Machine Learning*, volume 114, issue 10, article 220, 2025. PDF/catalogue title differences are preserved for Faithful/Faithfulness Serum and iFlip's expanded title. These are version/cataloguing cautions, not extra studies or proof of defective research.

## 3. What the closest full texts actually establish

### 3.1 Explanation generation, checking and refinement

**SR-NLE [L30]** holds a generative LLM's predicted answer fixed and refines its explanation using natural-language or important-word feedback. Its primary unfaithfulness measure checks whether the explanation string mentions an inserted influential adjective/adverb, over cases where that edit changes the prediction. This is an influence-acknowledgment proxy, not semantic validation of every claim. Absolute attribution magnitudes are used; they do not supply signed support by themselves. Appendix F.6 already tests random-word feedback and reports performance close to attribution feedback on e-SNLI. Our future experiments need appropriate random/length controls if claiming attribution helps.

**Cross-Refine [L25]** uses generator/critic roles, but the paper says it is not inherently iterative and allows changes to both prediction and explanation. Its human perceived-faithfulness and text-quality outcomes are different from fidelity to a fixed original decision. A fixed-decision adaptation would need to be labelled as an adaptation.

**FaithLM [L35]** already tests generated explanations through contrary-hint interventions and optimizes prompts/explanations. Its theoretical claims depend on stated assumptions; score improvement is not an unconditional certificate of internal faithfulness. It is a close verification predecessor, not merely an explanation generator.

**Faithfulness Serum [L36]** uses attribution-guided attention interventions and assesses final explanations' acknowledgment of influential hints. It includes LLM judging, keyword checks and human validation of that judging. Therefore final-output checking itself is not novel. Hint acknowledgment still does not validate every factual or numerical claim in an explanation. The study requires model internals and substantial hardware; static guidance and adaptive regeneration have different cost profiles.

**Explanation-Refiner [L41]** formally checks and refines NLI explanations using Isabelle/HOL, event semantics and proof-failure feedback. Its proof concerns a formalized theory under its assumptions. It does not demonstrate that an explanation reveals the computation of an unchanged LLM classifier. Formal claim representations and external checking already have prior art, and translation fidelity remains a separate issue.

### 3.2 Counterfactuals: distinguish target, generator and evaluator

**Randl et al. [L02]**, the second base paper, is especially aligned with the thesis's LLM-decision scope: the target generative LLM classifies inputs, proposes counterfactuals and is queried to test edited inputs. Generation, reclassification and bounded retry are established components. Validity and dependability do not establish complete internal faithfulness.

**FITCF [L26]** uses fine-tuned BERT for attribution and filtering demonstration pairs. An LLM then generates final few-shot counterfactuals. The reported flip evaluator is not uniformly that same BERT: Appendix G presents the LLM with original and edited text together and asks a yes/no question about changed classifications. That paired judgment must not be silently equated with independent calls to a fixed target classifier. Demonstration filtering also does not establish that every final generated edit passed the same checker.

**iFlip [L38]** separates generatorG from explained classifierM. The inspected main/transfer experiments use BERT/RoBERTa targets, despite using LLM generators. Its early stopping requires the desired target label, while its reported label-flip rate counts any changed label. In multiclass settings, those are different outcomes. Embedding similarity is a minimality proxy, not proof of a minimum edit. The small human study—three participants and 10 source cases—measures subjective qualities, not appropriate reliance. Feedback, early stopping, random controls and budget trade-offs are already explicit prior art.

**Truth or Twist [L43]** studies semantic label validity for counterfactual data augmentation, expressly distinguished from changing a particular target model's prediction. Its judges directly label edited inputs and are compared with human annotations. A more human-aligned independent judge cannot replace the target LLM when assessing behavioral counterfactual validity. Semantic adequacy and target-model behavior should be reported separately. Judge-choice effects and evaluating the evaluator are already research topics.

### 3.3 Audience adaptation and human outcomes

**Group-specific activation steering [L34]** already evaluates atomic facts in audience-tailored explanations with FActScore against Wikipedia for its science-question setting. Generic audience adaptation plus postgeneration claim checking is therefore not an adequate novelty claim. Its goal is topic factuality and group specificity, rather than preserving a fixed classifier's decision, attribution and validated counterfactual evidence.

Its nine-expert study on 50 questions has mixed outcomes: the prompting baseline scores higher on helpfulness and plausibility, while the proposed method scores higher on steering and slightly on the harmonic aggregate. Do not turn that trade-off into a claim of universally better user benefit. No human decision-accuracy or appropriate-reliance improvement is established there.

**InterroLang [L15]** already integrates dialogue, NLP attribution, perturbations/counterfactuals and rationalization. Its explained targets are BERT-type task models; much response rendering is rule/template based. The simulatability study has six participants including four authors and a sequential explanation design; it is not a clean randomized dialogue-versus-one-off trial. It remains close system prior art, but not a general causal demonstration of improved decision-making.

**Explanation Utility [L20]** refines the task-selection issue:17of53 datasets meet its reliance/complementarity criteria; four are prioritized after further filters. Its projected perfect-deferral performance is hypothetical, not measured team performance. Its empirical legal-task results caution against assuming that showing explanations improves efficient decisions. Human readability, preference, model simulatability and appropriate reliance need separate endpoints.

### 3.4 Metrics and their assumptions

**CC-SHAP [L21]** compares signed, normalized input contributions to prediction and explanation via cosine similarity. It uses masked SHAP coalitions, repeated inference and output probabilities; it is not a perturbation-free or low-cost universal black-box score. The paper explicitly distinguishes self-consistency from internal faithfulness.

**Causal Diagnosticity [L23]** evaluates faithfulness metrics using model-edited explanation pairs. Its reference labels depend on successful edits; the paper warns that one in-context analogy-editing setting has low reliability. Synthetic construction is useful but cannot be treated as unqualified ground truth.

**PEX consistency [L24]** measures support for a prediction, with the experimental score based on changes in label log-odds after appending an explanation. It uses probability access and training/preference optimization. Reported student-simulation improvements are not universal percentages of internally faithful explanations or measured human gains.

**Causal Faithfulness [L31]** compares activation-patching indirect-effect patterns for answer and explanation. It requires hidden-state interventions and probabilities, and its replacement/span constraints limit applicability. Its plausibility ratings use an LLM judge, not a participant study.

**Agarwal et al. [L39]** is a conceptual review distinguishing plausibility and faithfulness, not a new controlled improvement experiment. **Lanham et al. [L40]** intervene on CoT with mistakes, early answering, filler tokens and paraphrases. Their results depend on task/model; §5 acknowledges the lack of independent internal-reasoning ground truth. Paraphrase robustness is already prior art and is different from preserving evidence through a user-facing rewrite after fixing a decision.

## 4. Consequences for the proposed thesis

| Question | Literature-grounded decision |
| --- | --- |
| What is being explained? | The same target LLM decision, recorded with its task prompt, model revision and inference settings. |
| Is the generator always the target? | No. Keep generator, target predictor, evidence extractor, semantic judge and renderer distinct. |
| Is final-output checking new? | No. FaithLM, Serum, FActScore-based audience evaluation and formal refinement provide different existing checks. |
| Does any flip establish the claimed counterfactual? | No. Report desired-target success separately from any-flip rate and semantic adequacy. |
| Does prose agreement establish internal faithfulness? | No. Identify the exact tested consistency/behavioral property. |
| Does a preferred explanation establish useful reliance? | No. Measure human judgments and correctness appropriate to the task. |
| Can the application alone establish research novelty? | No. It demonstrates a method whose contribution needs independent evidence. |

The interface can remain minimalist: input, fixed decision, inspectable evidence, checked counterfactuals, audience view and explicit limitations. Its quality should come from understandable evidence and reliable execution. No decorative dashboard or generic trust score is needed.

## 5. Candidate contribution for Step 3

**Candidate question:** Can a specified claim-preservation mechanism keep supported decision, directional-attribution, concrete counterfactual and uncertainty claims intact when an explanation of a fixed LLM decision is rewritten for novice and expert audiences?

**Potential contribution:** A method and diagnostic protocol for the transition from target-model evidence to final audience-facing claims. The contribution would have to go beyond generic schemas, critics, semantic entailment, factuality scoring or a repair loop, all of which have predecessors.

**Necessary contrasts:** Initial evidence consistency versus final text; meaning-preserving paraphrases versus meaning-changing edits; target-class success versus any flip; supported claims versus unsupported but fluent statements; correct rejection versus useful response coverage. Evaluate independently of the score used to generate/refine explanations.

**What has not been established:** That this mechanism is new, that it improves results, that it increases appropriate reliance, or that it generalizes beyond selected tasks/models. Step 3 must define the actual method and strongest competing interpretation. If it merely reproduces an existing method, revise the candidate rather than rename it.

An evaluation-only contribution could also be defensible if it establishes a new, useful failure mode with an independent protocol. Controlled diagnostics themselves are not new; the specific construct, cases and findings must add evidence beyond CheckList, Causal Diagnosticity and existing consistency tests.

## 6. Recommended baseline and evaluation structure

| Condition | Purpose | Important control |
| --- | --- | --- |
| Unverified LLM self-explanation | Starting explanation condition. | Same fixed target decisions and test inputs. |
| Grounded translation without final check | Isolate grounding from final-text validation. | Same evidence and comparable generation budget. |
| Attribution-feedback refinement, informed by SR-NLE | Stronger existing refinement comparison. | Match decision policy; include random-word/length controls where relevant. |
| Audience adaptation without preservation mechanism | Measure effects of rewriting. | Same audience instructions and underlying evidence. |
| Proposed mechanism with adaptation | Test the actual Step 3 contribution. | Independent held-out diagnostics and labelled failures. |

This is a recommended design skeleton, not a frozen implementation protocol. FaithLM, Serum, formal refinement and other competitors need either justified direct comparisons or transparent exclusion/adaptation based on the chosen task and compute. A weakened surrogate must not be reported as an original method outperformed.

For counterfactual components, a same-target reclassification baseline based on Randl is closer to the presented decision-LLM scope than silently using BERT-derived evidence. If adapting FITCF or iFlip, state precisely what changed.

Report task performance; supported, contradicted and unverifiable final claims; behavioral diagnostics under explicit assumptions; target-success and any-flip rates; semantic/edit quality; failure rate; coverage over all inputs; model calls and latency. High validity among retained candidates alone can result from filtering. Uncertainty should be estimated from the actual sampling design in Step 4, not invented now.

If human evaluation is feasible, use actual participants and the applicable consent/permission process, clear tasks and independent outcomes. Do not substitute LLM ratings for participants or infer reliance from satisfaction. If it is infeasible before Review2, report the technical pilot and the pending human-study plan honestly.

## 7. Feasibility and source limitations

The full texts expose substantial resource differences: attention intervention, activation patching, probability-based scores, fine-tuned classifiers and repeated generation are not interchangeable API features. Some reported systems use large GPUs or costly searches. Step 4 must inspect available resources before selecting models and baselines; there is no need to reproduce every large-model experiment for a bounded M.Tech pilot.

Candidate datasets remain unselected. ERASER movie rationales, e-SNLI, Food Recall Incidents, harmful-language datasets and contract verification have different evidence, licensing, difficulty and human-study requirements. Human rationales are not automatic ground truth for target-model reasoning. Respect original splits and assess contamination.

The bibliography includes43 records with mixed reading depth. Source/version ambiguities and remaining metadata checks are flagged. Concept-based readability [L42], for example, concerns global hidden-space concepts; its targeted overview does not establish a direct novice/expert prose method. Several older repository-only venue claims still require verification before manuscript citation. They are not prerequisites for the current bounded gap assessment.

No paper's experiments have been reproduced here. No significant result, publication acceptance, plagiarism clearance, clinical utility or grade improvement is claimed. The review supports methodological planning, not deployment or an originality certificate.

## 8. Completion and next handoff

**Completed:** access revalidation; priority full-text reading; source-backed corrections; bibliography expansion; generator/target/evaluator separation; candidate-gap reassessment; baseline and evaluation implications; updated report, spreadsheet, notes and provenance.

**Step 3 deliverable:** choose and specify a narrow contribution, research questions, falsifiable hypotheses and a precise comparison with nearest methods. Keep the approved thesis title unless supervisor guidance changes it. Dataset/model selection and experimental thresholds follow in Step 4; application development remains a later step.

The source-level audit is in FULLTEXT_REVIEW_NOTES.md. Stable citation IDs L01–L43 resolve in LITERATURE_MATRIX.xlsx, ANNOTATED_BIBLIOGRAPHY.md and REFERENCES_WORKING.bib. Version1's blocked-access conclusions are preserved under archive/v1 and superseded by this report.
