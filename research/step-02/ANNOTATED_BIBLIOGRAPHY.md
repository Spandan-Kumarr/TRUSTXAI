# Annotated Literature Library — updated27October2026

43records; access depth is record-specific. Full-text audit does not mean experimental reproduction.

## [L01] A Three-level Framework for LLM-enhanced Explainable AI: From Technical Explanations to Natural Language

**Authors:** Marilyn Bello; Rafael Bello; María-Matilde García; Ann Nowé; Iván Sevillano-García; Francisco Herrera
**Year / venue:** 2025 / Information Systems Frontiers
**Access:** Full supplied paper, sections 3–5 especially pp. 8–18
**Metadata:** Year2025 verified in Crossref; volume/issue not supplied

**Contribution:** Three levels: algorithmic/domain evidence, human-centered interaction, societal transparency; LLM interprets existing XAI evidence for audiences.

**Limits:** Authors explicitly acknowledge conceptual foundation requiring further empirical validation (p.18); loan illustrations are not a controlled user study or measured faithfulness guarantee.

**Thesis implication:** Primary audience-aware framework motivation; broad integration is already proposed.

**Comparison:** Conceptual architecture comparator; operationalize evidence preservation rather than claiming invention of three-level XAI.

**Source:** https://doi.org/10.1007/s10796-025-10668-1

## [L02] Mind the gap: from plausible to valid self-explanations in large language models

**Authors:** Korbinian Randl; John Pavlopoulos; Aron Henriksson; Tony Lindgren
**Year / venue:** 2025 / Machine Learning 114, article 220
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** Previously reviewed base paper uses target generativeLLM classification and samples counterfactual candidates by alternative class; reclassifies candidates,retainsvalidones,selects by similarity×target probability,and stops underboundedclasswisebudget.

**Limits:** Classification/decoder-only;noactionability;prompt-sensitivitylimited;finite retriesmayfail;validCFdoesnotproveinternalfaithfulness.

**Thesis implication:** Generation/reclassification/retry and empirical validity testing alreadypriorart.

**Comparison:** Reproduce smallopenmodel prompting-basedcandidatebaselineandexplicitlydistinguish observedlabeltargetsuccessfromsurfaceplausibility;respectGPLv3codeif reused.

**Source:** https://doi.org/10.1007/s10994-025-06838-6

## [L03] Beyond Accuracy: Behavioral Testing of NLP Models with CheckList

**Authors:** Marco Tulio Ribeiro; Tongshuang Wu; Carlos Guestrin; Sameer Singh
**Year / venue:** 2020 / Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics
**Access:** Official abstract/metadata plus detailed README; full paper not retrieved
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Behavioral test methodology over linguistic capabilities and test types, with tools for minimum functionality, invariance and directional-expectation testing.

**Limits:** Tests target model behavior and task-specific expectations; not a certificate of narrative faithfulness or fairness. Test labels must match intended semantics of edits.

**Thesis implication:** Separates perturbations that should preserve labels from those that should change them.

**Comparison:** Use framework to design targeted robustness/negative-control probes rather than claiming all perturbations should keep predictions unchanged.

**Source:** https://aclanthology.org/2020.acl-main.442/

## [L04] ERASER: A Benchmark to Evaluate Rationalized NLP Models

**Authors:** Jay DeYoung; Sarthak Jain; Nazneen Fatema Rajani; Eric Lehman; Caiming Xiong; Richard Socher; Byron C. Wallace
**Year / venue:** 2020 / Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics
**Access:** Official abstract/metadata plus README and metric implementation; full paper not retrieved
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Benchmark with human rationale annotations and distinct plausibility/faithfulness-oriented measurements. Source implements rationale alignment, classification, comprehensiveness, sufficiency and AOPC metrics.

**Limits:** Human rationale overlap measures agreement, not causal internal faithfulness; removal/retention metrics depend on model score access and perturbation distribution. Dataset source licences must be checked individually.

**Thesis implication:** Provides evaluation protocol and potentially annotated movie-review data consistent with base paper2.

**Comparison:** Candidate evaluation backbone. Label probability must be meaningfully defined for generative labels; no fabricated probability for API-only access.

**Source:** https://aclanthology.org/2020.acl-main.408/

## [L05] NILE : Natural Language Inference with Faithful Natural Language Explanations

**Authors:** Sawan Kumar; Partha Talukdar
**Year / venue:** 2020 / Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics
**Access:** Official abstract and metadata only; full paper not accessed
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** NILE generates label-specific explanations used in the prediction path and tests explanation sensitivity.

**Limits:** By-construction explanation-to-prediction differs from post-hoc explanations of an unchanged LLM.

**Thesis implication:** Reason-then-predict architectures are existing alternatives; do not silently change scope.

**Comparison:** Architecture comparator, not same-target post-hoc baseline.

**Source:** https://aclanthology.org/2020.acl-main.771/

## [L06] Towards Faithfully Interpretable NLP Systems: How Should We Define and Evaluate Faithfulness?

**Authors:** Alon Jacovi; Yoav Goldberg
**Year / venue:** 2020 / Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics
**Access:** Official abstract and metadata only; full paper not accessed
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Foundational clarification of graded faithfulness and explicit evaluation assumptions.

**Limits:** Conceptual guidance; this is an opinion/evaluation paper, not a deployable validator.

**Thesis implication:** Define what the thesis means by faithfulness and what its tests cannot establish.

**Comparison:** Framework for evaluation, not algorithm baseline.

**Source:** https://aclanthology.org/2020.acl-main.386/

## [L07] Explaining NLP Models via Minimal Contrastive Editing (MiCE)

**Authors:** Alexis Ross; Ana Marasović; Matthew Peters
**Year / venue:** 2021 / Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021
**Access:** Official abstract + Official metadata plus README and selected search implementation; full paper not retrieved
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Uses a trained editor and search over masking amounts to find minimal contrastive edits; source re-scores candidates with the target predictor, records successful target-label edits and uses a bounded beam/search procedure.

**Limits:** Original toolkit uses task-specific predictor/editor training and legacy AllenNLP/Python3.7 setup; not a drop-in modern instruction-LLM experiment. No benchmark results were rerun.

**Thesis implication:** Minimality search plus classifier validation existed before LLM self-CF work.

**Comparison:** Relevant algorithmic comparator if adapted fairly to same target model; adaptation must be disclosed.

**Source:** https://aclanthology.org/2021.findings-acl.336/

## [L08] Polyjuice: Generating Counterfactuals for Explaining, Evaluating, and Improving Models

**Authors:** Tongshuang Wu; Marco Tulio Ribeiro; Jeffrey Heer; Daniel Weld
**Year / venue:** 2021 / Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers)
**Access:** Official abstract/metadata plus README; full paper not retrieved
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** A GPT-2-based general-purpose perturbation generator with controls over edit type and location; supports counterfactual error analysis and augmentation of explanation techniques.

**Limits:** Generator is distinct from validity certification for a specified classifier; sampled perturbations need target-specific label checks. Older generator/tool dependencies and text licences need consideration.

**Thesis implication:** Controlled lexical/semantic edit generation is established prior art.

**Comparison:** Candidate perturbation-generation comparator or robustness suite component; do not equate every perturbation with a valid counterfactual.

**Source:** https://aclanthology.org/2021.acl-long.523/

## [L09] Reframing Human-AI Collaboration for Generating Free-Text Explanations

**Authors:** Sarah Wiegreffe; Jack Hessel; Swabha Swayamdipta; Mark Riedl; Yejin Choi
**Year / venue:** 2022 / NAACL 2022
**Access:** Official ACL abstract and metadata plus official README; full paper not accessed
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Few-shot GPT3 free-text explanation generation combined with a supervised filter using binary human acceptability judgments. Official abstract reports crowdworkers sometimes prefer generated explanations to dataset human explanations, with weaknesses including novel information and support for the label.

**Limits:** Human acceptability is partly correlated with fine-grained explanation attributes, not proof of mechanistic faithfulness. Preference and grammatical/factual sufficiency need not imply appropriate reliance; full study protocol and effect sizes not read.

**Thesis implication:** Prior art for human assessment/collaboration around generated explanations; warns against presenting human acceptance as mechanistic fidelity.

**Comparison:** Human acceptability annotation materials and methodological background; investigate before reusing datasets/prompts.

**Source:** https://aclanthology.org/2022.naacl-main.47/

## [L10] CREST: A Joint Framework for Rationalization and Counterfactual Text Generation

**Authors:** Marcos Treviso; Alexis Ross; Nuno M. Guerreiro; André Martins
**Year / venue:** 2023 / Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
**Access:** Official abstract/metadata plus detailed README; full paper not retrieved
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Joint selective rationalization and counterfactual text generation; trains masker/editor, classifies generated edits and uses counterfactuals to regularize rationales. Repository provides IMDB/SNLI edits and validity, fluency, diversity, plausibility and simulation evaluation instructions.

**Limits:** Training-oriented rationalizer/predictor architecture differs from post-hoc verification of a fixed instruction LLM; off-the-shelf validity checks in README must not be assumed same-model validation. Compiler/SparseMAP and legacy dependencies add reproduction cost.

**Thesis implication:** Direct prior art against novelty claims about combining rationales, evidence extraction and counterfactual generation.

**Comparison:** Possible strong method/data comparator with careful target alignment; at minimum compare conceptual differences explicitly.

**Source:** https://aclanthology.org/2023.acl-long.842/

## [L11] ConvXAI: Delivering Heterogeneous AI Explanations via Conversations to Support Human-AI Scientific Writing

**Authors:** Hua Shen; Chieh-Yang Huang; Tongshuang Wu; Ting-Hao 'Kenneth' Huang
**Year / venue:** 2023 / CSCW 2023 Demo (author-reported); arXiv:2305.09770
**Access:** Official README, system/model documentation and preprint citation; no full paper accessed
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Conversational system for heterogeneous explanations supporting scientific writing. Repository documents SciBERT writing-structure and GPT-based writing-style models, intent classification, example-based explanations and MiCE counterfactuals.

**Limits:** Scientific-writing support is a specific task; demo code and screenshots do not establish benefit on LLM classification or calibrated trust. README does not provide a full human-study protocol or paper-level results.

**Thesis implication:** Prior art for conversational selection and integration of heterogeneous explanation types, including counterfactuals.

**Comparison:** Interaction and explanation-menu comparator; distinguish task-specific model support from verification of final LLM-written claims.

**Source:** https://arxiv.org/abs/2305.09770

## [L12] DISCO: Distilling Counterfactuals with Large Language Models

**Authors:** Zeming Chen; Qiyue Gao; Antoine Bosselut; Ashish Sabharwal; Kyle Richardson
**Year / venue:** 2023 / Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
**Access:** Official abstract/metadata plus author README; full paper not retrieved
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Prompts a large language model for phrasal perturbations and filters generations with a task-specific teacher; counterfactual data trains more robust NLI student models.

**Limits:** Training-data augmentation objective, not explanation verification of the same decision LLM; teacher filtering is not automatically target-model validity. README and final ACL abstract report different effect sizes, so no numerical comparison quoted.

**Thesis implication:** Generate-and-filter text pipelines with LLMs are established.

**Comparison:** Useful prior art and generation/filtering control; cannot directly substitute teacher labels for target-model checks.

**Source:** https://aclanthology.org/2023.acl-long.302/

## [L13] Explaining machine learning models with interactive natural language conversations using TalkToModel

**Authors:** Dylan Slack; Satyapriya Krishna; Himabindu Lakkaraju; Sameer Singh
**Year / venue:** 2023 / Nature Machine Intelligence
**Access:** Official README including abstract and citation; no full paper accessed
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Adaptive dialogue engine interprets natural language, execution component constructs explanations, conversational interface presents them. Repository supports tabular models and includes diabetes, COMPAS, German credit demos.

**Limits:** README explicitly says current system supports tabular models, not BERT sentiment models. Reported 73% healthcare-worker preference and 85% ML-professional ease-of-use agreement are preference/usability outcomes, not proof of faithfulness or calibrated reliance. Full human-study protocol not inspected.

**Thesis implication:** Strong prior art for conversational XAI with executable technical evidence; natural-language UI over explanations is not new.

**Comparison:** Architecture/UI comparator rather than automatic apples-to-apples end-to-end baseline for LLM text classification.

**Source:** https://doi.org/10.1038/s42256-023-00692-8

## [L14] Faithful Chain-of-Thought Reasoning

**Authors:** Qing Lyu; Shreya Havaldar; Adam Stein; Li Zhang; Delip Rao; Eric Wong; Marianna Apidianaki; Chris Callison-Burch
**Year / venue:** 2023 / IJCNLP-AACL 2023
**Access:** Primary author-repository README; paper full text not accessed
**Metadata:** Provisional metadata: verify before manuscript

**Contribution:** Translator LM reasoning chains are executed by deterministic solvers to derive answers in structured tasks.

**Limits:** Faithfulness-by-execution constrains answer derivation but does not guarantee that translated premises correctly represent the input. Different from post-hoc classification explanation.

**Thesis implication:** Connecting language, symbolic representations and executable checks is established prior art.

**Comparison:** Conceptual comparator for verifiable-by-construction methods; not automatically a fair baseline for a fixed classifier.

**Source:** https://arxiv.org/abs/2301.13379

## [L15] InterroLang: Exploring NLP Models and Datasets through Dialogue-based Explanations

**Authors:** Nils Feldhus; Qianli Wang; Tatiana Anikina; Sahil Chopra; Cennet Oguz; Sebastian Möller
**Year / venue:** 2023 / Findings of the Association for Computational Linguistics: EMNLP 2023
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** A modular dialogue engine parses questions into executable operations. Its execution engine inserts results into mainly rule/template-based responses. The explained targets are BERT-type models for DailyDialog dialogue acts, BoolQ yes/no answers and OLID offensive/nonoffensive classification. It uses Captum Integrated Gradients, Polyjuice counterfactuals, OpenAttack PWWS adversarial edits and nlpaug augmentations. Rationales are separate prompted outputs conditioned on input and target prediction; ChatGPT demonstrations support Dolly few-shot rationalization. Clarification concerns intent/slots and history, rather than audience-profile rewriting.

**Limits:** Small in-house/expert samples, with four authors in Task B; BERT-type task-specific targets; no direct model comparison or automated model-improvement loop. Subjective correctness is not semantic claim verification. Polyjuice often failed to produce a label-flipping perturbation. Some explanations induced false trust. Simulatability does not establish human decision utility.

**Thesis implication:** Conversational attribution-plus-counterfactual-plus-rationale integration is not new. A fixed generative decision-LLM target differs from this paper, but that model change alone does not establish novelty. Its human evidence must not be described as a universal causal benefit of dialogue over one-off explanation.

**Comparison:** Useful architecture and operation taxonomy; not automatically an apples-to-apples numerical baseline for a different generative decision model. Integrated Gradients requires internal access. Any adapted pipeline needs clear target and method attribution.

**Source:** https://aclanthology.org/2023.findings-emnlp.359/

## [L16] Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting

**Authors:** Miles Turpin; Julian Michael; Ethan Perez; Samuel R. Bowman
**Year / venue:** 2023 / Archival venue not independently verified here
**Access:** Primary author-repository README; paper full text not accessed
**Metadata:** Provisional metadata: verify before manuscript

**Contribution:** Biasing features can alter predictions while CoT omits their influence; repository includes BBH/BBQ prompts, samples and analysis.

**Limits:** Specific task/model/input-bias experiments do not establish all explanations are unfaithful. Paper full text was not accessed.

**Thesis implication:** Motivates targeted tests for omitted decision influences and separates persuasive rationales from tested influence.

**Comparison:** Controlled bias/hint influence stress test; not a universal metric.

**Source:** https://arxiv.org/abs/2305.04388

## [L17] A Survey on Natural Language Counterfactual Generation

**Authors:** Yongjie Wang; Xiaoqi Qiu; Yu Yue; Xu Guo; Zhiwei Zeng; Yuhong Feng; Zhiqi Shen
**Year / venue:** 2024 / Findings of the Association for Computational Linguistics: EMNLP 2024
**Access:** Official abstract and metadata only; full paper not accessed
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Survey categorizes textual counterfactual generation methods and reviews evaluation metrics.

**Limits:** Survey abstract only; taxonomy details need full text before reuse.

**Thesis implication:** Use as structured citation-tracing source for minimality, validity and semantic quality.

**Comparison:** Related-work taxonomy rather than algorithm baseline.

**Source:** https://aclanthology.org/2024.findings-emnlp.276/

## [L18] Are self-explanations from Large Language Models faithful?

**Authors:** Andreas Madsen; Sarath Chandar; Siva Reddy
**Year / venue:** 2024 / Findings of the Association for Computational Linguistics: ACL 2024
**Access:** Official archival metadata and abstract plus primary author-repository README; full paper not accessed
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Applies self-consistency checks to counterfactual, feature-attribution and redaction explanations; reported reliability depends on explanation type, model and task.

**Limits:** Self-consistency is behavioral evidence and does not expose inaccessible internal ground truth; claims cannot be generalized across models/tasks.

**Thesis implication:** Directly relevant baseline and prior art for target-model counterfactual/redaction tests; undermines treating simple reclassification as novel.

**Comparison:** Reproduce an access-compatible self-consistency or redaction test, with precise operational terminology.

**Source:** https://aclanthology.org/2024.findings-acl.19/

## [L19] Can LLMs Produce Faithful Explanations For Fact-checking? Towards Faithful Explainable Fact-Checking via Multi-Agent Debate

**Authors:** Kyungha Kim; Sangyun Lee; Kung-Hsiang Huang; Hou Pong Chan; Manling Li; Heng Ji
**Year / venue:** 2024 / Archival venue not independently verified here
**Access:** Primary author-repository README; paper full text not accessed
**Metadata:** Provisional metadata: verify before manuscript

**Contribution:** MADR generates explanations, uses debater critiques and a judge, then refines against evidence; defines source-related error types and uses PolitiHop.

**Limits:** Evidence faithfulness is distinct from causal faithfulness to a classifier. LLM critics may share errors and add cost; no audience-preservation claim verified in accessed text.

**Thesis implication:** Very close prior art for generation→critique/checking→refinement; integration alone is not new.

**Comparison:** Consider a budget-matched critique/refinement comparator; isolate adaptation-specific checks.

**Source:** https://arxiv.org/abs/2402.07401

## [L20] On Evaluating Explanation Utility for Human-AI Decision Making in NLP

**Authors:** Fateme Hashemi Chaleshtori; Atreya Ghosal; Alexander Gill; Purbid Bambroo; Ana Marasovic
**Year / venue:** 2024 / Findings of the Association for Computational Linguistics: EMNLP 2024
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** A framework for application-grounded human–AI evaluation and dataset choice, followed by ContractNLI/NDAs case studies using task-finetuned Flan-T5-3B. Criteria cover realistic application and inputs, meaningful effort/difficulty, nonbenign risk and suitable model performance. Seventeen of 53 datasets pass reliance/complementary-performance suitability; six of those have nonbenign hazards and two are removed for quality, leaving four prioritized datasets. Studies compare prediction/confidence, abstention/role/record framing, outcome feedback, Input×Gradient highlights and EK-FAC influential examples.

**Limits:** Limited tasks, participants, examples and explanation types; length is an imperfect effort proxy and risk judgments are subjective. Better contemporary models can change task suitability. Gold-label quality matters. Simulatability, perceived helpfulness and real human–AI utility are distinct. Do not infer a unique participant count by dividing annotations.

**Thesis implication:** Does not settle the narrow supported-claim-preservation candidate. It strongly constrains human-benefit claims: brief sentiment/rationale benchmarks are not automatically validated real-world decision-support studies.

**Comparison:** Use the full protocol as an evaluation-design reference, not as an algorithm baseline. A legal user study needs realistic expertise, consent, qualification checks and adequate time. Reassess the selected contemporary LLM rather than inheriting their Flan-T5 task suitability.

**Source:** https://aclanthology.org/2024.findings-emnlp.439/

## [L21] On Measuring Faithfulness or Self-consistency of Natural Language Explanations

**Authors:** Letitia Parcalabescu; Anette Frank
**Year / venue:** 2024 / Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** CC-SHAP compares input-token contribution vectors for the answer and the generated explanation. SHAP contribution ratios are signed and normalized by the absolute-sum of input contributions for each generated token; ratios are averaged across output tokens. Final CC-SHAP is one minus cosine distance, i.e. cosine similarity, between the resulting prediction and explanation vectors. This avoids specially crafted editing-test inputs but SHAP itself still evaluates masked coalitions. The authors explicitly call the construct self-consistency, not established internal faithfulness.

**Limits:** A graded output/input-contribution consistency score is not mechanistic ground truth. Results depend on SHAP masking, Monte Carlo approximation, aggregation and normalization. Very small contributions in long outputs require special handling (Appendix A.3). Requires repeated inference and next-token logits/probabilities, but not gradients or activation access. Authors report about four minutes/example for CC-SHAP and six–36 hours per model/task for the full test suite; these are paper-specific runtimes. English-only autoregressive experiments; model-size relationship not established. Human judgment cannot establish unknown internal reasoning, although humans can judge other defined evidence-consistency properties.

**Thesis implication:** A consistency benchmark, contribution-profile comparison and comparison of multiple faithfulness tests are established prior art. Any G1/G2 proposal should distinguish semantic supported-claim preservation from attribution-profile similarity. Do not claim that a checker score establishes complete internal faithfulness.

**Comparison:** Suitable as an optional per-instance consistency diagnostic when target-model probabilities and enough repeated inference are available. Expensive to run across every candidate and audience variant. Black-box text-only APIs without probability access cannot directly support the released metric. A simplified alternative must be labelled an adaptation.

**Source:** https://aclanthology.org/2024.acl-long.329/

## [L22] Tell Me a Story! Narrative-Driven XAI with Large Language Models

**Authors:** David Martens; James Hinns; Camille Dams; Mark Vergouwen; Theodoros Evgeniou
**Year / venue:** 2024 / arXiv:2309.17057 (version/publication metadata pending)
**Access:** Official README and citation; no full paper accessed
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Provides SHAPstories narrative generation with LLMs; example notebook and code accept models exposing predict_proba.

**Limits:** README does not establish claim-level verification, audience preservation, controlled human effects or explanation faithfulness. Those are unknown from this access, not confirmed absent from the paper. Models with predict_proba requirement differs from arbitrary black-box generative APIs.

**Thesis implication:** Direct prior art for translating SHAP attributions into LLM narratives; SHAP-plus-LLM cannot itself be novelty.

**Comparison:** Potential translation-only implementation comparator after code/paper review and adaptation to same target-model interface.

**Source:** https://arxiv.org/abs/2309.17057

## [L23] A Causal Lens for Evaluating Faithfulness Metrics

**Authors:** Kerem Zaman; Shashank Srivastava
**Year / venue:** 2025 / Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** Causal Diagnosticity evaluates whether a metric ranks a faithful explanation above an unfaithful one for the same target answer. Controlled pairs are constructed using knowledge edits: primarily in-context editing (ICE), with MEMIT weight-editing ablations. Two edited knowledge settings preserve the answer while changing the intended reason. Pairwise correct ordering scores 1, ties0.5 and incorrect ordering0, averaged over examples. The main benchmark uses synthetic explanations to enforce the intended edit relationship.

**Limits:** Faithful/unfaithful pair validity depends on edits actually taking effect and generalizing. Edit-success is assessed using whether the intended explanation has lower perplexity; this is explicitly an indicative proxy, not a complete portability/compositionality validation. Section5.3 states ICE Analogy edit reliability is below 50% and its diagnosticity findings are unreliable. The benchmark requires externally supplied explanations and per-instance scores, excluding tests that regenerate explanations (such as Counterfactual Edits) or depend on corpus-level scoring. Synthetic explanations reduce realism; differences from model-generated conditions and model-specific corruption sensitivity remain. CC-SHAP scaling experiments were excluded for cost.

**Thesis implication:** Independent diagnosticity evaluation is established. G2 requires a distinct, justified target, such as final claim support under a frozen evidence record, and must acknowledge the relationship and limitations of synthetic construction. Do not represent the paper as providing unqualified ground truth about latent reasoning.

**Comparison:** Useful protocol inspiration and optional metric sanity tests. ICE-based controlled contexts are cheaper than weight editing, but require verifying edit adherence and preserving the target/evidence definition. MEMIT and large-model ablations increase compute. It is a metric-evaluation framework, not a directly interchangeable explanation-generation baseline.

**Source:** https://aclanthology.org/2025.emnlp-main.1496/

## [L24] A Necessary Step toward Faithfulness: Measuring and Improving Consistency in Free-Text Explanations

**Authors:** Lingjun Zhao; Hal Daumé III
**Year / venue:** 2025 / Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** PEX consistency measures how an explanation favors a prediction over its negation. Although the original definition is a sequence-likelihood ratio, experiments use adjusted PEX (Eq4): posterior label log-odds with explanation appended minus prior label log-odds without it. Models are first supervised-fine-tuned for binary opinion-spam classification; sampled explanations are ranked by PEX to construct preference pairs, then DPO trains the explanation model. Evaluation trains student models to simulate teacher predictions, using teacher explanations during student training but not at test time.

**Limits:** Requires output probabilities; cannot directly score completely black-box text-only models. PEX is a contrastive support/consistency construct, not semantic proof that all prose claims are supported by the original input or that latent reasoning is accurately exposed. Experiments are binary classification; multiclass extension is future work. The simulation endpoint is system-level, not an individual explanation verification certificate, and assumes simulation is a useful proxy. SFT/DPO and student training impose substantial compute. Authors report SFT/DPO on one RTX A6000 for roughly 24 h per described training configuration; student training 1–2 h. Qualitative examples and average PEX do not establish all outputs are consistent.

**Thesis implication:** A proposal cannot claim novelty merely for a prediction-explanation consistency score or optimizing explanations against such a score. G1 should state which evidence-supported claim types, transformations and independent checks go beyond this probability-based contrastive consistency.

**Comparison:** A scoring-only adapted PEX condition may be feasible if the same target model exposes label probabilities and a binary task is selected. Reproducing the original DPO method requires task SFT, sampled preferences, model training and simulator training; it is not a cheap training-free baseline. Scope/budget exclusions must be explicit.

**Source:** https://aclanthology.org/2025.emnlp-main.797/

## [L25] Cross-Refine: Improving Natural Language Explanation Generation by Learning in Tandem

**Authors:** Qianli Wang; Tatiana Anikina; Nils Feldhus; Simon Ostermann; Sebastian Möller; Vera Schmitt
**Year / venue:** 2025 / Proceedings of the 31st International Conference on Computational Linguistics
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** Two LLM roles: generator produces a CoT NLE using FEB-style few-shot examples; critic assesses need for improvement, generates feedback and a suggested explanation; generator cross-references both to produce a refinement. It is not inherently iterative (Limitations), although authors propose adaptive extension. Section3.1 explicitly permits correcting BOTH prediction and explanation, so it is not a fixed-decision explanation-only procedure. Same weights may play both roles in self Cross-Refine. FiXer contains60 demonstrations constructed with Llama3-8B, ChatGPT feedback/suggestions, manual review and postprocessing; in-context prompts use limited examples.

**Limits:** ["Authors acknowledge context limits, small in-context demonstration collections and English/German evaluation.", "Human study small and filtered; paper does not report retention coverage of generation filters, so perceived ratings cannot be treated as unconditional coverage.", "Subjective perceived faithfulness is not same-target behavioral or internal causal fidelity.", "Section6.2 describes binary perceived faithfulness but later IAA explanation inconsistently calls perceived faithfulness5-point; preserve actual stated protocol and flag reproduction detail.", "General-purpose critics may introduce hallucinations on unfamiliar medical content."]

**Thesis implication:** Critic/generator separation, extra feedback+suggestions, correction and conversational NLE refinement cannot themselves support novelty. A fixed-decision audience-preservation protocol is distinguishable, but requires comparison with other prior work; changing predictions must be controlled in any adapted baseline.

**Comparison:** Potential useful7B role-prompting comparator, but faithful reproduction needsFiXer and exact prompt stages; must control multiple model calls and whether original decision is frozen. Original70B/MoE combinations add cost; adapting Qwen/model/prompt is an adaptation, not exact reproduction.

**Source:** https://aclanthology.org/2025.coling-main.77/

## [L26] FitCF: A Framework for Automatic Feature Importance-guided Counterfactual Example Generation

**Authors:** Qianli Wang; Nils Feldhus; Simon Ostermann; Luis Felipe Villa-Arenas; Sebastian Möller; Vera Schmitt
**Year / venue:** 2025 / Findings of the Association for Computational Linguistics: ACL 2025
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** {"decision_and_generator_roles": "ZEROCF obtains y_pred and feature attributions from a BERT classifier fine-tuned on the target dataset. An LLM generates edited text from original input, BERT prediction and attributed words. FITCF clusters SBERT embeddings with k-means, selects near-centroid examples, generates ZEROCF edits, and uses the same BERT to remove non-flipping demonstration pairs. More near-centroid examples are selected until the required demonstration count is obtained. The resulting demonstrations plus feature words condition a final few-shot LLM generation.", "attribution": "Gradient, Integrated Gradients, LIME and SHAP via FERRET; special-token words are replaced and subwords merged. The study uses attribution for BERT, not the generative LLM itself.", "validation": "BERT label verification applies to constructed demonstration pairs. The paper does not specify that every final generated counterfactual must be rejected until it passes the same BERT checker.", "budget_and_stopping": "Demonstration count l=2k:10 for AG News,8 for SST2. If too few generated demonstration edits flip BERT, additional near-centroid instances are iteratively selected. No general finite retry guarantee is stated in the method.", "models": "Generation: Llama3-8B, Qwen2.5-32B and Qwen2.5-72B; attribution/demonstration verification: fine-tuned BERT. Qwen versions are GPTQ Int4; experiments use single RTX A6000/A100/H100 depending model."}

**Limits:** ["English-only two-classification-task evaluation; no cross-domain decision-support deployment evidence.", "Only BERT predictions used for the attribution/demonstration-verifier role; contribution of other model architectures to those roles is explicitly unexplored.", "LLM used for final paired flip judgment differs from BERT used for grounding and demonstration checks. AppendixG.1 assumes similar classifier accuracies imply consistent SLFR tendencies, which is not a proof of per-example agreement.", "Fluency and edit distance are not semantic adequacy or real-world actionability.", "No study of human trust, audience-adaptation preservation or final natural-language claims."]

**Thesis implication:** Attribution-guided counterfactual generation, BERT label-flip filtering, verified few-shot demonstrations and component ablations are established prior art. A thesis keeping the decision LLM fixed must explicitly change attribution/checker access rather than silently adopt cross-model evidence.

**Comparison:** Useful algorithmic predecessor. Faithful reproduction needs BERT checkpoint, attribution toolchain, SBERT/k-means demonstration construction and original generator/paired-evaluation prompts. Replacing BERT with the target LLM or replacing paired judgment with independent label calls is an adaptation and must be labelled. Heavy32B/72B variants are optional resource-heavy comparisons;8B still requires GPU resources.

**Source:** https://aclanthology.org/2025.findings-acl.64/

## [L27] LLMs Don’t Know Their Own Decision Boundaries: The Unreliability of Self-Generated Counterfactual Explanations

**Authors:** Harry Mayne; Ryan Othniel Kearns; Yushi Yang; Andrew M. Bean; Eoin D. Delaney; Chris Russell; Adam Mahdi
**Year / venue:** 2025 / Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
**Access:** Official abstract/metadata plus author README; full paper not retrieved
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Studies self-generated counterfactual explanations against empirically elicited LLM decision boundaries; observes a validity–minimality trade-off when prompting for counterfactuals versus minimal counterfactuals.

**Limits:** README identifies tabular binary-classification setting; do not present these results as text-CF evidence or infer complete paper limitations from abstract alone. No numerical effect size asserted here.

**Thesis implication:** Strong near prior art: obtaining valid edits is insufficient; minimality and genuine boundary correspondence need evaluation.

**Comparison:** Prompt-only counterfactual and minimal-counterfactual conditions are valuable controls; tabular exhaustive-boundary metric does not transfer unchanged to free text.

**Source:** https://aclanthology.org/2025.emnlp-main.1231/

## [L28] Multi-Level Explanations for Generative Language Models

**Authors:** Lucas Monteiro Paes; Dennis Wei; Hyo Jin Do; Hendrik Strobelt; Ronny Luss; Amit Dhurandhar; Manish Nagireddy; Karthikeyan Natesan Ramamurthy; Prasanna Sattigeri; Werner Geyer; Soumya Ghosh
**Year / venue:** 2025 / Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
**Access:** Official abstract + author repository README (not full text)
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** MExGen extends perturbation-based attribution such as LIME/SHAP to costly, long-context text generation; scores context parts for influence on outputs and reports automated plus human evaluation.

**Limits:** Official abstract/README only. Context attribution is not proof of internal causal reasoning and is not itself audience-adapted claim validation. Method targets context-grounded generation rather than the same bounded classification task by default.

**Thesis implication:** Prior art for model-grounded explanations of LLM outputs and reusable in-context XAI tooling; the application or extending SHAP to text generation alone cannot be new.

**Comparison:** Relevant evidence-extraction comparator or reusable toolkit; ICX360 includes MExGen, CELL contrastive prompts and token highlighter. README states Apache2.0, not independently licence-audited here.

**Source:** https://aclanthology.org/2025.acl-long.1553/

## [L29] Normalized AOPC: Fixing Misleading Faithfulness Metrics for Feature Attributions Explainability

**Authors:** Joakim Edin; Andreas Geert Motzfeldt; Casper L. Christensen; Tuukka Ruotsalo; Lars Maaløe; Maria Maistro
**Year / venue:** 2025 / Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
**Access:** Official abstract/metadata + author README; full paper not accessed
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Normalized AOPC addresses misleading cross-model comparisons and interprets scores relative to model-specific bounds.

**Limits:** Inspect full-text normalization assumptions and compute costs before adapting to generative LLM labels.

**Thesis implication:** Raw perturbation scores cannot be compared naively across different target models.

**Comparison:** Metric-design source; primary repository also inspected.

**Source:** https://aclanthology.org/2025.acl-long.86/

## [L30] Self-Critique and Refinement for Faithful Natural Language Explanations

**Authors:** Yingming Wang; Pepa Atanasova
**Year / venue:** 2025 / Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** {"target": "A single instruction-tuned generative LLM predicts answer y; y is held fixed while the same LLM generates and refines its post-hoc explanation.", "pipeline": "Generate answer, generate initial explanation, then K feedback/refinement rounds. Natural-language feedback is regenerated from each current explanation; important-word feedback (IWF) is computed once and reused across rounds (Algorithm1). IWF variants are prompt ranking, final-layer mean-attention and Integrated Gradients.", "attribution": "Sequentially attribute each answer-span token to preceding input/output context; use absolute values, sum across answer tokens, then aggregate subword scores to words from task input excluding prompt tokens. Top5 words guide explanations; this is unsigned magnitude evidence, not signed contribution claims.", "checks": "Method refines from supplied feedback; the CT faithfulness test is an evaluation on label-changing inserted-word interventions. It does not apply a semantic claim verifier/release gate to every final explanation. Prompts request retaining correct content, but no mechanically enforced supported-claim contract is supplied."}

**Limits:** ["Authors: post-hoc explanations only; sole CT metric, no plausibility/completeness/reference alignment; underlying attention/IG reliability and baseline dependence; models only7–8B.", "IG uses EOS-embedding baseline. Selected500integrationsteps for Falcon/Llama/Mistral and1000forQwen make exact IG variant expensive; no actual compute configuration/runtime table is supplied in the inspected paper.", "Conditioning on label-changing interventions and lexical string matching limits construct validity. Length increases with refinement (Fig6); related surface overlap/length effects need independent controls.", "Paper itself acknowledges close-to-random important-word selection. Do not characterize random-feedback weakness as an undisclosed flaw or claim this paper proves causally faithful internal explanations."]

**Thesis implication:** Attribution-guided post-hoc explanation refinement with fixed target answer is established. Any contribution should exceed this with a concrete preservation mechanism and independent diagnostics; include random-word feedback and length controls before asserting attribution superiority.

**Comparison:** Prompt-based IWF is the most feasible lightweight direct comparator: one model, once-computed top5word ranking, K3refinements. Attention needs local internals; exact IG variant is substantially costlier. Clearly label prompt-IWF as prompted evidence, not grounded numerical attribution. Reproduce CT separately from any new claim-consistency metric.

**Source:** https://aclanthology.org/2025.emnlp-main.427/

## [L31] Towards Faithful Natural Language Explanations: A Study Using Activation Patching in Large Language Models

**Authors:** Wei Jie Yeo; Ranjan Satapathy; Erik Cambria
**Year / venue:** 2025 / Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** Causal Faithfulness (CaF) replaces SHAP-style contribution profiles with activation-patching indirect effects. Clean, corrupted and patched forward passes create token×layer matrices for the answer and post-hoc explanation; effects are averaged across generated tokens. CaF is cosine similarity of the two matrices, with variants aggregating token or layer axes or patching windows. Symmetric Token Replacement (STR) uses manually constructed equal-token-length counterfactual spans rather than Gaussian embedding noise.

**Limits:** Requires internal hidden-state intervention and output probabilities; approximately T×L patching forward passes, in addition to clean/corrupted processing and output-token effects. Equal token-length replacements depend on tokenizer; manually edited gold-rationale spans and corrupted-span-onward visibility limit task coverage. Claims of lower OOD corruption risk are shown in selected controlled tasks, not a theorem that all STR inputs are in-distribution. Models are one family; different base/chat prompting and limited samples qualify generalization. GPT-4o plausibility is not participant understanding or appropriate reliance. Internal causal-attribution agreement remains a designed proxy; authors acknowledge full mechanistic faithfulness remains a larger challenge.

**Thesis implication:** Layer-aware attribution consistency is established prior art. Avoid claiming a completely new internal-faithfulness metric without comparison; do not equate a final prose evidence checker with CaF. G1 can distinguish its evidence-preservation target, while acknowledging that the underlying attribution record remains imperfect.

**Comparison:** Suitable optional white-box diagnostic if compute and manually aligned counterfactual spans are available. Poor default for text-only APIs or unrestricted task data because of hidden-state access, token alignment and cost. Cannot infer feasible runtime from model parameter count alone.

**Source:** https://aclanthology.org/2025.emnlp-main.529/

## [L32] A Positive Case for Faithfulness: LLM Self-Explanations Help Predict Model Behavior

**Authors:** Harry Mayne; Justin Singh Kang; Dewi Sid William Gould; Kannan Ramchandran; Adam Mahdi; Noah Y. Siegel
**Year / venue:** 2026 / ICML 2026
**Access:** Primary author-repository README; paper full text not accessed
**Metadata:** Provisional metadata: verify before manuscript

**Contribution:** Evaluates whether self-explanations help predictor models simulate target-model behavior on counterfactual inputs; includes reference/predictor pipelines and simulatability analysis.

**Limits:** README/code description alone does not establish general fidelity. Simulatability depends on task, target, predictor and prompts.

**Thesis implication:** Counterweight to assuming all self-explanations are useless; investigate when they predict behavior.

**Comparison:** Complementary explanation-assisted simulatability evaluation if feasible; not direct access to hidden computation.

**Source:** https://arxiv.org/abs/2602.02639

## [L33] Accountable AI with Grounded, Faithful, Consistent, Actionable Rationales: A Case Study in Clinical Trial Matching with VERDICT

**Authors:** Zikai Zhou; Yufei Jin; Yilin Xu; Yu-Chiang Wang; Chieh-Ju Chao; Monica Lam
**Year / venue:** 2026 / Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing
**Access:** Official abstract + author repository README (not full text)
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** VERDICT converts constraints/policies into SMT/MaxSMT and derives eligibility decisions from a solver, exposing assumptions and pivotal conditions that would change outcomes; combines accountable rationale artifacts with a working clinical trial application.

**Limits:** Official abstract and extensive author README only. Solver-based decisions differ from explanations of an unchanged LLM classifier. Clinical resources and data licensing impose scope costs. README-reported benchmark numbers have not been reproduced; no clinical deployment endorsement.

**Thesis implication:** Strong prior art for evidence-grounded decision support, audit trails, pivotal/counterfactual conditions and explicit undecided states. Changing the thesis to solver decisions would change Review1 scope.

**Comparison:** Architecture/limitation comparator, not automatically a fair same-task numerical baseline. Abstract metadata lists EMNLP2026; collection ingested 2026-10-21 and month October.

**Source:** https://aclanthology.org/2026.emnlp-main.2598/

## [L34] Attribute-Based Activation Steering of LLMs for Group-Specific Explanation Generation

**Authors:** Leandra Fichtel; Janek Prange; Henning Wachsmuth
**Year / venue:** 2026 / Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** Extracts style/knowledge attributes from Stack Exchange answers for 11 groups using Qwen models and embedding clustering, retaining 1,250 attributes. For each group it selects top style and knowledge attributes, constructs positive-minus-negated attribute activation vectors, weights/sums them and injects steering into selected three-layer windows. It compares group-only/group-plus-attribute prompts, standard Konen steering and proposed attribute steering. The outputs are topical educational explanations, not explanations of a fixed classifier decision.

**Limits:** Group averages may stereotype and miss individual knowledge; Stack Exchange forum participation need not represent professions. English and fixed groups only. LLM-derived attributes and factuality judgments inherit errors; authors interpret factuality relatively, not as absolute truth. Greater specificity can reduce factuality or drift away from answering the question. Human groups were selected among the best-performing groups, sample size is small and agreement low. Human comparison bundles attributes and activation versus group-only baselines, so it is not an isolated activation-effect estimate.

**Thesis implication:** The candidate must specify same-target decision evidence and a distinct preservation mechanism or diagnostic protocol. Audience adaptation, atomic decomposition, factuality checking and trade-off measurement each already exist. Helpful human effects cannot be inferred from steering success.

**Comparison:** Prompt-based group-only and group-plus-attributes conditions are feasible adaptation comparators. The full activation pipeline needs internal access and substantial data/model infrastructure. Control prompt information and evaluate the same target-decision/evidence setting; do not directly compare its encyclopedia factuality scores with classifier-evidence preservation scores.

**Source:** https://aclanthology.org/2026.emnlp-main.127/

## [L35] FaithLM: Towards Faithful Explanations for Large Language Models

**Authors:** Yu-Neng Chuang; Guanchu Wang; Chia-Yuan Chang; Ruixiang Tang; Shaochen Zhong; Fan Yang; Andrew Wen; Mengnan Du; Xuanting Cai; Vladimir Braverman; Xia Hu
**Year / venue:** 2026 / Proceedings of the 19th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers)
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** Separates unchanged target predictor f from explanation generator g_E, includingAPI targets in stated formulation. For explanationE, a strong LLM produces an opposite-semantics contrary hint notE; target is queried with hint plus original input. Score is target prediction sensitivity f(X)-f(X|notE), described as output logits/calibrated probabilities; section3.1 also mentions scoring nonzero-attribution tokens. Algorithm1 repeatedly generates explanations informed by trajectory of explanations/scores until fixed budget or decision flip. Algorithm2 optimizes an elicitation prompt by average score over held-out training examples. A theorem connects contrary-hint sensitivity to causal faithfulness under explicit equivalence-of-hint-to-do-intervention and irrelevant-text invariance assumptions.

**Limits:** ["Theorem is conditional on semantic hint implementing a causal do-intervention and target invariance to irrelevant text. These assumptions are not automatically satisfied by realLLM prompting; sensitivity may also reflect suggestion compliance. It is not unconditional certification of internal causal reasoning.", "Optimization/evaluation share contrary-hint score; independent diagnostic checks are needed before universalfaithfulness claims.", "Generation and opposite-hint quality matter; AppendixK.3 explicitly shows a purported contrary hint that reaffirms the original rationale and fails to flip prediction.", "Authors emphasize increased compute/carbon cost due iteration; main empirical focusMCQ tasks, future workopen-ended/multilingual.", "Reference/NLI similarity and GPTjudgments are not human understanding or appropriate reliance.", "API-only model-agnostic claim must be reconciled with score requirements for logits/calibrated probabilities and section3.1saliency mention.", "The publicREADME previously inspected is minimal, so availability of complete reproducible implementation remains unresolved."]

**Thesis implication:** High-priority nearest comparator for fixed-target explanation optimization. Candidate distinction is preservation of supported decision evidence under audience transformations with independent claim diagnostics; a contrary-hint loop or model-based rewriting alone is already prior art. Any comparison must state conditional meaning of its metric rather than treating it as ground truth.

**Comparison:** Conceptual black-box comparator possible if target returns usable output scores; needs opposite-hint generator and up-to20explanation iterations plus prompt optimization50–100rounds. For small prototype, fixed-budget adapted reproduction should be clearly labelled. Resolve contradictory schedule/sample statements and minimal code release before claiming exact reproduction.

**Source:** https://aclanthology.org/2026.eacl-long.177/

## [L36] Faithfulness Serum: Mitigating the Faithfulness Gap in Textual Explanations of LLM Decisions via Attribution Guidance

**Authors:** Bar Alon; Itamar Zimerman; Lior Wolf
**Year / venue:** 2026 / Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** PDF title differs from catalogue; both variants retained; verify final citation title before submission

**Contribution:** {"target": "Fixed prior answer from an unmodified target LLM; explaining generation is steered after prediction. Compute PE-LRP relevance for first generated answer token, aggregate relevance over question input (excluding system/generated tokens), add alpha*relevance to post-softmax attention at selected layers throughout explanation decoding.", "intervention": "Main local models Llama3.1-8B-Instruct and Qwen2.5-7B-Instruct. Layers17–19 selected by logit-lens study. Staticalpha=.06Llama/.1Qwen from MMLU auxiliary-training lexical-diversity sweep.", "adaptive": "TTalpha regenerates explanation while adjustingalpha to seek distinct-1 ratio35–45%, max15iterations. This controls a lexical-diversity proxy, not verified support/claim risk; generation is not simply one extra pass in this adaptive variant.", "evaluation_setup": "Inject four misleading hint types; retain instances where the same target model changes its answer to the hint-provided answer; ask post-hoc explanation with general or protocol-specific prompts (and intermediate grounding prompts)."}

**Limits:** ["Predict-and-explain only and attention mechanism only are explicit author limitations; residual/feed-forward/normalization effects not handled.", "Evaluation focuses on acknowledgment/dependence for synthetic hint-induced answer changes. This is a narrow known-influence test, not exhaustive truth, causal completeness or robustness to all real inputs.", "CT keyword matches can accept superficial references; complementary judge has human agreement but is still not universal ground truth.", "Paper qualitative guided examples can acknowledge a hint while retaining incorrect arithmetic or factual claims (AppendixC,PDFpp18–19). Thus hint attribution and globally correct supported claims differ.", "Static method adds one PE-LRP backward pass plus explanation attention modifications; no empiricalwallclockcosttable supplied. TTalpha multiple generations adds further cost. Experimental infrastructure NVIDIAH10080GB, individualrunmax24h.", "PDF title is Faithfulness Serum whereas inspected ACL XML/title metadata says Faithful Serum: flag version/title discrepancy rather than silently assume identical title metadata."]

**Thesis implication:** Attribution-grounded generation plus counterfactual influence testing and semantically judged final explanations is direct2026priorart. A candidate preservation study must target a distinguishable property such as semantic content across audience transformations, not just final-output checking.

**Comparison:** Faithful attentionsteering requireslocalopenweight model and PE-LRP/backward/attentionhooks; potentially expensive for studentcompute. Treat as nearestmethod priority but only reproduce ifinternals/hardwareavailable. Promptgrounding baselines are easier but not reproduction of Serum. Do not claim wholemethod matched using only attributionwordsinprompt.

**Source:** https://aclanthology.org/2026.acl-long.300/

## [L37] Gaming the Judge: How Unfaithful Chain-of-Thought Can Undermine Agent Evaluation

**Authors:** Muhammad Khalifa; Lajanugen Logeswaran; Jaekyeom Kim; Sungryull Sohn; Yunxiang Zhang; Moontae Lee; Hao Peng; Lu Wang; Honglak Lee
**Year / venue:** 2026 / Findings of the Association for Computational Linguistics: EMNLP 2026
**Access:** Official abstract and metadata only; full paper not accessed
**Metadata:** Source-backed metadata; verify final venue style before manuscript

**Contribution:** Studies manipulation of judges by rewriting agent reasoning while holding actions/observations fixed.

**Limits:** Agent evaluation setting differs from classification explanations; abstract-only and no reproduced results.

**Thesis implication:** Independent evidence checks should supplement style-sensitive LLM judgments.

**Comparison:** Adversarial evaluation motivation, not a direct explanation-generator baseline.

**Source:** https://aclanthology.org/2026.findings-emnlp.1636/

## [L38] iFlip: Iterative Feedback-driven Counterfactual Example Refinement

**Authors:** Yilong Wang; Qianli Wang; Nils Feldhus
**Year / venue:** 2026 / Findings of the Association for Computational Linguistics: EMNLP 2026
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** PDF title differs from catalogue; both variants retained; verify final citation title before submission

**Contribution:** {"roles": "Separate counterfactual generator G and explained classifier M. Initial y=M(x), choose desired y_tilde !=y. Generate x_cf0. If M(x_cf)=y_tilde stop; otherwise iteratively refine with feedback and recheck.", "models": "Generators OLMo2-7B, Qwen3-32B, Llama3.3-70B. Main explained classifiers are task-specific BERT. Additional experiments use RoBERTa. AppendixC.2 tests BERT-to-RoBERTa transfer of candidate edits or feedback, not generativeLLM decision targets.", "feedback": "Explained-model predicted-label maximum softmax confidence; SHAP,AttnLRP,Gradient×Input,LIME important words; LLM natural-language feedback; or combined confidence+SHAP+NL.", "budget": "Formal method allows initial candidate plus up toK refinement steps; experiment setting lists5iterations (with studies up to15). Generation temperature0.9,top-p0.95,top-k50,max-new-tokens4096. Top important words max(10,floor(0.1*original_words)). Explained-model majority voting over512-token windows/stride256.", "stopping": "Early stop after desired target-class success; otherwise stop at maxiterations. No unconditional100%success guarantee. They compare with nofeedback, randomfeedback, least-attributedfeedback and noearlystop."}

**Limits:** ["English-only; limited attribution-method set; expensive iterative generation, especially NL feedback.", "3-person10-case user study is explicitly limited; satisfaction/feasibility ratings do not measure human decision correctness or calibrated trust.", "Main targets are BERT/RoBERTa rather than instruction-tuned generativeLLM decisions, despite LLM generators.", "Any-flip reporting and desired-target stopping are distinct success definitions.", "Cosine similarity and PPL do not establish complete semantic adequacy or real-world actionability.", "Isolated appendix consistency issues: Table33 labels originalbusiness/counterfactualbusiness but isFlipYes; another row business→sport but isFlipNo. AppendixL introductory dimension names differ from its detailed scoring definitions. These are reporting/protocol-document inconsistencies to check before reuse, not proof that whole experiments are invalid."]

**Thesis implication:** A bounded feedback+earlystopping CF loop, sensitivity to important words, validity/similarity/cost trade-off, and transfer tests cannot be claimed new. The main decision-model boundary should be explicit; applying to generativeLLM targets requires an actual justified adaptation and evidence.

**Comparison:** Confidence-only and NLfeedback versions are implementable candidates but currently trained-classifier-target baselines. Whitebox attribution needs gradient/attention access.8B/7B generator variants still GPUheavy;32B/70B models are not essential to a bounded thesis pilot. Budget-matched comparisons must account for initial generation, feedback and retries. No code executed.

**Source:** https://aclanthology.org/2026.findings-emnlp.38/

## [L39] Faithfulness vs. Plausibility: On the (Un)Reliability of Explanations from Large Language Models

**Authors:** Agarwal, Chirag; Tanneru, Sree Harsha; Lakkaraju, Himabindu
**Year / venue:** 2024 / arXiv preprint
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** Conceptual review distinguishing plausibility and model faithfulness, covering token importance, counterfactuals and CoT; application-specific transparency discussion.

**Limits:** Conceptual definitions and recommendations do not certify a method; domain examples do not establish empirical deployment outcomes.

**Thesis implication:** Motivation is established; do not claim invention of the plausibility-faithfulness distinction.

**Comparison:** Conceptual foundation rather than executable baseline.

**Source:** https://arxiv.org/abs/2402.04614v3

## [L40] Measuring Faithfulness in Chain-of-Thought Reasoning

**Authors:** Lanham, Tamera; Chen, Anna; Radhakrishnan, Ansh; Steiner, Benoit; Denison, Carson; Hernandez, Danny; Li, Dustin; Durmus, Esin; Hubinger, Evan; Kernion, Jackson; Lukošiūtė, Kamilė; Nguyen, Karina; Cheng, Newton; Joseph, Nicholas; Schiefer, Nicholas; Rausch, Oliver; Larson, Robin; McCandlish, Sam; Kundu, Sandipan; Kadavath, Saurav; Yang, Shannon; Henighan, Thomas; Maxwell, Timothy; Telleen-Lawton, Timothy; Hume, Tristan; Hatfield-Dodds, Zac; Kaplan, Jared; Brauner, Jan; Bowman, Samuel R.; Perez, Ethan
**Year / venue:** 2023 / arXiv preprint
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** Intervenes on generated CoT by early answering, mistakes, filler tokens and paraphrasing; measures subsequent answers. Main experiments use a175B RLHF model; model-size experiments are separate.

**Limits:** §5 explicitly lacks independent access to true internal reasoning. No guarantee that behavioral robustness establishes complete faithfulness. Proprietary models and sampling cost limit direct reproduction.

**Thesis implication:** Do not claim novel paraphrase robustness or first behavioral intervention tests.

**Comparison:** Use its controlled-intervention logic; repeating175B/100samples is not required for a bounded thesis pilot.

**Source:** https://arxiv.org/abs/2307.13702v1

## [L41] Verification and Refinement of Natural Language Explanations through LLM-Symbolic Theorem Proving

**Authors:** Xin Quan; Marco Valentino; Louise A. Dennis; Andre Freitas
**Year / venue:** 2024 / Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** Explanation-Refiner converts NLI premises, hypotheses and explanatory facts into Isabelle/HOL theories using event semantics/FOL, corrects syntax, proposes proof steps, and refines explanations using failed proof feedback.

**Limits:** Guarantees concern the formalized theory under its assumptions; natural-language-to-logic translation can lose semantics. Logical support is distinct from tracing an unchanged LLM decision. Authors caution that safety/correctness guarantees in critical applications require further investigation.

**Thesis implication:** Formalizing claims or adding an external checker alone is not new; this is important direct prior art.

**Comparison:** Architecture comparator; full reproduction adds Isabelle, formalization prompts and iterative model calls.

**Source:** https://aclanthology.org/2024.emnlp-main.172/

## [L42] Evaluating Readability and Faithfulness of Concept-based Explanations

**Authors:** Meng Li; Haoran Jin; Ruixuan Huang; Zhihao Xu; Defu Lian; Zijia Lin; Di Zhang; Xiting Wang
**Year / venue:** 2024 / Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing
**Access:** Official metadata/abstract plus targeted PDF overview; not counted as full-text audit
**Metadata:** Primary metadata verified; detailed study not audited

**Contribution:** Formalizes concept-based explanations and evaluates readability/faithfulness and their measures.

**Limits:** Global hidden-concept evaluation differs from local audience-adapted prose. Targeted full-text overview only; detailed experiments not audited.

**Thesis implication:** Avoid conflating concept readability with reader comprehension of an explanation.

**Comparison:** Scope/evaluation background; not a direct local-classification baseline.

**Source:** https://aclanthology.org/2024.emnlp-main.36/

## [L43] Truth or Twist? Optimal Model Selection for Reliable Label Flipping Evaluation in LLM-based Counterfactuals

**Authors:** Qianli Wang; Van Bach Nguyen; Nils Feldhus; Luis Felipe Villa-Arenas; Christin Seifert; Sebastian Möller; Vera Schmitt
**Year / venue:** 2025 / Proceedings of the 18th International Natural Language Generation Conference
**Access:** Full-text methods, evaluation, limitations and relevant appendices inspected; no reproduction
**Metadata:** Primary source inspected; retain any stated title/version discrepancy

**Contribution:** {"scope": "Studies semantic/ground-truth label validity for counterfactual data augmentation (CDA), explicitly distinguished from explaining a particular model by changing its prediction (p1footnote2).", "generator_judge_roles": "Counterfactuals generated by FIZLE or FLARE with Llama3-{8B,70B}/Qwen2.5-{14B,32B}. Judges grouped as same model, same family, independent with/without target-data fine-tuning, or distillation-related;15judges including trainedBERT/RoBERTa and multiple off-the-shelfLLMs, plus majority ensemble.", "evaluator_protocol": "Judge assigns a class to the edited input using a direct category-only task prompt (AppendixD/Fig10). LFR compares edited-input predicted label against ORIGINAL DATASET label. It is not the paired original+edited yes/no meta-judgment shown in FitCF AppendixG.", "human_alignment": "Human-label edited inputs define semantic reference labels; compare automatic and human aggregate LFR via absolute closeness/rank, most-to-least alignment ratio and Pearson correlation. This evaluates semantic label agreement, not access to model-internal reasoning."}

**Limits:** ["English-only;generatorfamiliesQwen/Llama and selectedjudges limitgeneralization.", "Observed model-relationship associations do not isolate a causal effect of independence, finetuning or contamination; models differ in capability and training.", "Human labels for ambiguous editedtext have onlymoderateagreement and adjudication;call them annotatedreference labelsratherthanunquestionabletruth.", "Paper concentratesonlabel-flipvalidity/CDA,notcomprehensiveCF quality,fairness,actionabilityoraudience-adaptedclaimpreservation.", "The claim of fully automatedCDA inadequacy is limited to studiedsystems/settings. No theorem that all automationis impossible."]

**Thesis implication:** Judge-selection effects, weak human/model alignment and the distinction semantic-validity vsbehavioralflip are existing research insights. Thesis should retain BOTH constructs if relevant ratherthaninventingthisdistinction or equatingindependentjudgeagreementwithfaithfulness.

**Comparison:** Use as evaluation-design foundation; reproducingall4generators×15judges isresourceheavyandunnecessaryforpilot. A limited clearlylabelled independentsemanticcheck mayaugment same-targetreclassification, withhumanannotationonfeasiblesubset. No authors codeexecuted.

**Source:** https://aclanthology.org/2025.inlg-main.5/
