# Annotated Evidence Library

Search date: 26 October 2026. Source-backed summaries; most new records are abstract/README-level, not full-paper reviews. Full-text limitations are explicit. No experiment has been reproduced.

## [L01] A Three-level Framework for LLM-enhanced Explainable AI: From Technical Explanations to Natural Language

**Authors:** Marilyn Bello; Rafael Bello; María-Matilde García; Ann Nowé; Iván Sevillano-García; Francisco Herrera
**Year / venue:** 2025/2026 metadata unresolved / Information Systems Frontiers
**Publication evidence:** Journal article; supplied PDF accepted 19 November 2025, modified publication 2026; canonical year pending publisher verification
**Access:** Full supplied paper, sections 3–5 especially pp. 8–18

**Contribution reported by source:** Three levels: algorithmic/domain evidence, human-centered interaction, societal transparency; LLM interprets existing XAI evidence for audiences.

**Limits / unresolved details:** Authors explicitly acknowledge conceptual foundation requiring further empirical validation (p.18); loan illustrations are not a controlled user study or measured faithfulness guarantee.

**Thesis implication:** Primary audience-aware framework motivation; broad integration is already proposed.

**Comparison use:** Conceptual architecture comparator; operationalize evidence preservation rather than claiming invention of three-level XAI.

**Record:** https://doi.org/10.1007/s10796-025-10668-1

**Evidence inspected:**
- User-supplied PAPER 1.pdf

## [L02] Mind the gap: from plausible to valid self-explanations in large language models

**Authors:** Korbinian Randl; John Pavlopoulos; Aron Henriksson; Tony Lindgren
**Year / venue:** 2025 / Machine Learning 114, article 220
**Publication evidence:** Published journal article; supplied full PDF
**Access:** Full supplied paper plus README and selected implementation source

**Contribution reported by source:** Analyses extractive/counterfactual self-explanations of LLM classifiers; samples edited inputs and explicitly reclassifies them; estimates retries and evaluates validity, similarity, dependability and runtime.

**Limits / unresolved details:** Classification-only; decoder-only; gradient tests up to 9B; no actionability assessment; prompt sensitivity not systematically evaluated; finite retry budget can fail; similarity/validity do not establish internal reasoning.

**Thesis implication:** Direct base paper and mandatory methodological reference.

**Comparison use:** Reproduce target-model reclassification baseline and bounded rejection sampling before claiming a better validator. Report candidate attempts and failures.

**Record:** https://doi.org/10.1007/s10994-025-06838-6

**Evidence inspected:**
- Supplied PAPER 2.pdf, sections 3–6 and Appendix H
- https://raw.githubusercontent.com/k-randl/self-explaining_llms/main/README.md
- https://raw.githubusercontent.com/k-randl/self-explaining_llms/main/self-counterfactuals-movies.py

## [L03] Beyond Accuracy: Behavioral Testing of NLP Models with CheckList

**Authors:** Marco Tulio Ribeiro; Tongshuang Wu; Carlos Guestrin; Sameer Singh
**Year / venue:** 2020 / Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract/metadata plus detailed README; full paper not retrieved

**Contribution reported by source:** Behavioral test methodology over linguistic capabilities and test types, with tools for minimum functionality, invariance and directional-expectation testing.

**Limits / unresolved details:** Tests target model behavior and task-specific expectations; not a certificate of narrative faithfulness or fairness. Test labels must match intended semantics of edits.

**Thesis implication:** Separates perturbations that should preserve labels from those that should change them.

**Comparison use:** Use framework to design targeted robustness/negative-control probes rather than claiming all perturbations should keep predictions unchanged.

**Record:** https://aclanthology.org/2020.acl-main.442/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2020.acl.xml
- https://raw.githubusercontent.com/marcotcr/checklist/master/README.md

## [L04] ERASER: A Benchmark to Evaluate Rationalized NLP Models

**Authors:** Jay DeYoung; Sarthak Jain; Nazneen Fatema Rajani; Eric Lehman; Caiming Xiong; Richard Socher; Byron C. Wallace
**Year / venue:** 2020 / Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract/metadata plus README and metric implementation; full paper not retrieved

**Contribution reported by source:** Benchmark with human rationale annotations and distinct plausibility/faithfulness-oriented measurements. Source implements rationale alignment, classification, comprehensiveness, sufficiency and AOPC metrics.

**Limits / unresolved details:** Human rationale overlap measures agreement, not causal internal faithfulness; removal/retention metrics depend on model score access and perturbation distribution. Dataset source licences must be checked individually.

**Thesis implication:** Provides evaluation protocol and potentially annotated movie-review data consistent with base paper2.

**Comparison use:** Candidate evaluation backbone. Label probability must be meaningfully defined for generative labels; no fabricated probability for API-only access.

**Record:** https://aclanthology.org/2020.acl-main.408/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2020.acl.xml
- https://raw.githubusercontent.com/jayded/eraserbenchmark/master/README.md
- https://raw.githubusercontent.com/jayded/eraserbenchmark/master/rationale_benchmark/metrics.py

## [L05] NILE : Natural Language Inference with Faithful Natural Language Explanations

**Authors:** Sawan Kumar; Partha Talukdar
**Year / venue:** 2020 / Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract and metadata only; full paper not accessed

**Contribution reported by source:** NILE generates label-specific explanations used in the prediction path and tests explanation sensitivity.

**Limits / unresolved details:** By-construction explanation-to-prediction differs from post-hoc explanations of an unchanged LLM.

**Thesis implication:** Reason-then-predict architectures are existing alternatives; do not silently change scope.

**Comparison use:** Architecture comparator, not same-target post-hoc baseline.

**Record:** https://aclanthology.org/2020.acl-main.771/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2020.acl.xml

## [L06] Towards Faithfully Interpretable NLP Systems: How Should We Define and Evaluate Faithfulness?

**Authors:** Alon Jacovi; Yoav Goldberg
**Year / venue:** 2020 / Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract and metadata only; full paper not accessed

**Contribution reported by source:** Foundational clarification of graded faithfulness and explicit evaluation assumptions.

**Limits / unresolved details:** Conceptual guidance; this is an opinion/evaluation paper, not a deployable validator.

**Thesis implication:** Define what the thesis means by faithfulness and what its tests cannot establish.

**Comparison use:** Framework for evaluation, not algorithm baseline.

**Record:** https://aclanthology.org/2020.acl-main.386/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2020.acl.xml

## [L07] Explaining NLP Models via Minimal Contrastive Editing (MiCE)

**Authors:** Alexis Ross; Ana Marasović; Matthew Peters
**Year / venue:** 2021 / Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract + Official metadata plus README and selected search implementation; full paper not retrieved

**Contribution reported by source:** Uses a trained editor and search over masking amounts to find minimal contrastive edits; source re-scores candidates with the target predictor, records successful target-label edits and uses a bounded beam/search procedure.

**Limits / unresolved details:** Original toolkit uses task-specific predictor/editor training and legacy AllenNLP/Python3.7 setup; not a drop-in modern instruction-LLM experiment. No benchmark results were rerun.

**Thesis implication:** Minimality search plus classifier validation existed before LLM self-CF work.

**Comparison use:** Relevant algorithmic comparator if adapted fairly to same target model; adaptation must be disclosed.

**Record:** https://aclanthology.org/2021.findings-acl.336/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2021.findings.xml
- https://raw.githubusercontent.com/allenai/mice/master/README.md
- https://raw.githubusercontent.com/allenai/mice/master/src/edit_finder.py

## [L08] Polyjuice: Generating Counterfactuals for Explaining, Evaluating, and Improving Models

**Authors:** Tongshuang Wu; Marco Tulio Ribeiro; Jeffrey Heer; Daniel Weld
**Year / venue:** 2021 / Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics and the 11th International Joint Conference on Natural Language Processing (Volume 1: Long Papers)
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract/metadata plus README; full paper not retrieved

**Contribution reported by source:** A GPT-2-based general-purpose perturbation generator with controls over edit type and location; supports counterfactual error analysis and augmentation of explanation techniques.

**Limits / unresolved details:** Generator is distinct from validity certification for a specified classifier; sampled perturbations need target-specific label checks. Older generator/tool dependencies and text licences need consideration.

**Thesis implication:** Controlled lexical/semantic edit generation is established prior art.

**Comparison use:** Candidate perturbation-generation comparator or robustness suite component; do not equate every perturbation with a valid counterfactual.

**Record:** https://aclanthology.org/2021.acl-long.523/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2021.acl.xml
- https://raw.githubusercontent.com/tongshuangwu/polyjuice/main/README.md

## [L09] Reframing Human-AI Collaboration for Generating Free-Text Explanations

**Authors:** Sarah Wiegreffe; Jack Hessel; Swabha Swayamdipta; Mark Riedl; Yejin Choi
**Year / venue:** 2022 / NAACL 2022
**Publication evidence:** Published proceedings metadata verified in official ACL Anthology record
**Access:** Official ACL abstract and metadata plus official README; full paper not accessed

**Contribution reported by source:** Few-shot GPT3 free-text explanation generation combined with a supervised filter using binary human acceptability judgments. Official abstract reports crowdworkers sometimes prefer generated explanations to dataset human explanations, with weaknesses including novel information and support for the label.

**Limits / unresolved details:** Human acceptability is partly correlated with fine-grained explanation attributes, not proof of mechanistic faithfulness. Preference and grammatical/factual sufficiency need not imply appropriate reliance; full study protocol and effect sizes not read.

**Thesis implication:** Prior art for human assessment/collaboration around generated explanations; warns against presenting human acceptance as mechanistic fidelity.

**Comparison use:** Human acceptability annotation materials and methodological background; investigate before reusing datasets/prompts.

**Record:** https://aclanthology.org/2022.naacl-main.47/

**Evidence inspected:**
- https://raw.githubusercontent.com/allenai/few_shot_explanations/main/README.md

## [L10] CREST: A Joint Framework for Rationalization and Counterfactual Text Generation

**Authors:** Marcos Treviso; Alexis Ross; Nuno M. Guerreiro; André Martins
**Year / venue:** 2023 / Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract/metadata plus detailed README; full paper not retrieved

**Contribution reported by source:** Joint selective rationalization and counterfactual text generation; trains masker/editor, classifies generated edits and uses counterfactuals to regularize rationales. Repository provides IMDB/SNLI edits and validity, fluency, diversity, plausibility and simulation evaluation instructions.

**Limits / unresolved details:** Training-oriented rationalizer/predictor architecture differs from post-hoc verification of a fixed instruction LLM; off-the-shelf validity checks in README must not be assumed same-model validation. Compiler/SparseMAP and legacy dependencies add reproduction cost.

**Thesis implication:** Direct prior art against novelty claims about combining rationales, evidence extraction and counterfactual generation.

**Comparison use:** Possible strong method/data comparator with careful target alignment; at minimum compare conceptual differences explicitly.

**Record:** https://aclanthology.org/2023.acl-long.842/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2023.acl.xml
- https://raw.githubusercontent.com/deep-spin/crest/main/README.md

## [L11] ConvXAI: Delivering Heterogeneous AI Explanations via Conversations to Support Human-AI Scientific Writing

**Authors:** Hua Shen; Chieh-Yang Huang; Tongshuang Wu; Ting-Hao 'Kenneth' Huang
**Year / venue:** 2023 / CSCW 2023 Demo (author-reported); arXiv:2305.09770
**Publication evidence:** Demo acceptance stated in official README; separate main research-paper publication not verified
**Access:** Official README, system/model documentation and preprint citation; no full paper accessed

**Contribution reported by source:** Conversational system for heterogeneous explanations supporting scientific writing. Repository documents SciBERT writing-structure and GPT-based writing-style models, intent classification, example-based explanations and MiCE counterfactuals.

**Limits / unresolved details:** Scientific-writing support is a specific task; demo code and screenshots do not establish benefit on LLM classification or calibrated trust. README does not provide a full human-study protocol or paper-level results.

**Thesis implication:** Prior art for conversational selection and integration of heterogeneous explanation types, including counterfactuals.

**Comparison use:** Interaction and explanation-menu comparator; distinguish task-specific model support from verification of final LLM-written claims.

**Record:** https://arxiv.org/abs/2305.09770

**Evidence inspected:**
- https://raw.githubusercontent.com/huashen218/convxai/main/README.md

## [L12] DISCO: Distilling Counterfactuals with Large Language Models

**Authors:** Zeming Chen; Qiyue Gao; Antoine Bosselut; Ashish Sabharwal; Kyle Richardson
**Year / venue:** 2023 / Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract/metadata plus author README; full paper not retrieved

**Contribution reported by source:** Prompts a large language model for phrasal perturbations and filters generations with a task-specific teacher; counterfactual data trains more robust NLI student models.

**Limits / unresolved details:** Training-data augmentation objective, not explanation verification of the same decision LLM; teacher filtering is not automatically target-model validity. README and final ACL abstract report different effect sizes, so no numerical comparison quoted.

**Thesis implication:** Generate-and-filter text pipelines with LLMs are established.

**Comparison use:** Useful prior art and generation/filtering control; cannot directly substitute teacher labels for target-model checks.

**Record:** https://aclanthology.org/2023.acl-long.302/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2023.acl.xml
- https://raw.githubusercontent.com/eric11eca/disco/main/README.md

## [L13] Explaining machine learning models with interactive natural language conversations using TalkToModel

**Authors:** Dylan Slack; Satyapriya Krishna; Himabindu Lakkaraju; Sameer Singh
**Year / venue:** 2023 / Nature Machine Intelligence
**Publication evidence:** Published journal article per author repository citation; DOI verified in README, publisher page inaccessible
**Access:** Official README including abstract and citation; no full paper accessed

**Contribution reported by source:** Adaptive dialogue engine interprets natural language, execution component constructs explanations, conversational interface presents them. Repository supports tabular models and includes diabetes, COMPAS, German credit demos.

**Limits / unresolved details:** README explicitly says current system supports tabular models, not BERT sentiment models. Reported 73% healthcare-worker preference and 85% ML-professional ease-of-use agreement are preference/usability outcomes, not proof of faithfulness or calibrated reliance. Full human-study protocol not inspected.

**Thesis implication:** Strong prior art for conversational XAI with executable technical evidence; natural-language UI over explanations is not new.

**Comparison use:** Architecture/UI comparator rather than automatic apples-to-apples end-to-end baseline for LLM text classification.

**Record:** https://doi.org/10.1038/s42256-023-00692-8

**Evidence inspected:**
- https://raw.githubusercontent.com/dylan-slack/TalkToModel/main/README.md

## [L14] Faithful Chain-of-Thought Reasoning

**Authors:** Qing Lyu; Shreya Havaldar; Adam Stein; Li Zhang; Delip Rao; Eric Wong; Marianna Apidianaki; Chris Callison-Burch
**Year / venue:** 2023 / IJCNLP-AACL 2023
**Publication evidence:** Author-repository acceptance report; independently verify proceedings
**Access:** Primary author-repository README; paper full text not accessed

**Contribution reported by source:** Translator LM reasoning chains are executed by deterministic solvers to derive answers in structured tasks.

**Limits / unresolved details:** Faithfulness-by-execution constrains answer derivation but does not guarantee that translated premises correctly represent the input. Different from post-hoc classification explanation.

**Thesis implication:** Connecting language, symbolic representations and executable checks is established prior art.

**Comparison use:** Conceptual comparator for verifiable-by-construction methods; not automatically a fair baseline for a fixed classifier.

**Record:** https://arxiv.org/abs/2301.13379

**Evidence inspected:**
- https://raw.githubusercontent.com/veronica320/Faithful-COT/main/README.md

## [L15] InterroLang: Exploring NLP Models and Datasets through Dialogue-based Explanations

**Authors:** Nils Feldhus; Qianli Wang; Tatiana Anikina; Sahil Chopra; Cennet Oguz; Sebastian Möller
**Year / venue:** 2023 / Findings of the Association for Computational Linguistics: EMNLP 2023
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official ACL metadata abstract plus official README; full paper not accessed

**Contribution reported by source:** Adapts TalkToModel to NLP; integrates feature attribution, counterfactuals/perturbations, free-text rationalization and dataset exploration. Official abstract reports two studies: perceived correctness/helpfulness and simulatability; dialogue explanations helped users predict hidden model labels more reliably than one-off explanations.

**Limits / unresolved details:** Perceived helpfulness and model simulatability are distinct from decision correctness and calibrated reliance. Results concern the studied models/tasks; detailed study protocol and effect sizes have not been read. Documented target models are BERT-family task classifiers, not evidence of verified explanations for instruction-tuned generative decision LLMs.

**Thesis implication:** Very close system-level prior art: combining conversation, NLP attribution, counterfactuals and rationalization is not a new contribution by itself.

**Comparison use:** Source of operation taxonomy and NLP UX; compare verified final claims and explicit failure reporting if method differences warrant. No licence confirmed from root LICENSE URL (404).

**Record:** https://aclanthology.org/2023.findings-emnlp.359/

**Evidence inspected:**
- https://raw.githubusercontent.com/DFKI-NLP/InterroLang/main/README.md
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2023.findings.xml

## [L16] Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting

**Authors:** Miles Turpin; Julian Michael; Ethan Perez; Samuel R. Bowman
**Year / venue:** 2023 / Archival venue not independently verified here
**Publication evidence:** Author repository supplies arXiv2023 citation
**Access:** Primary author-repository README; paper full text not accessed

**Contribution reported by source:** Biasing features can alter predictions while CoT omits their influence; repository includes BBH/BBQ prompts, samples and analysis.

**Limits / unresolved details:** Specific task/model/input-bias experiments do not establish all explanations are unfaithful. Paper full text was not accessed.

**Thesis implication:** Motivates targeted tests for omitted decision influences and separates persuasive rationales from tested influence.

**Comparison use:** Controlled bias/hint influence stress test; not a universal metric.

**Record:** https://arxiv.org/abs/2305.04388

**Evidence inspected:**
- https://raw.githubusercontent.com/milesaturpin/cot-unfaithfulness/main/README.md

## [L17] A Survey on Natural Language Counterfactual Generation

**Authors:** Yongjie Wang; Xiaoqi Qiu; Yu Yue; Xu Guo; Zhiwei Zeng; Yuhong Feng; Zhiqi Shen
**Year / venue:** 2024 / Findings of the Association for Computational Linguistics: EMNLP 2024
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract and metadata only; full paper not accessed

**Contribution reported by source:** Survey categorizes textual counterfactual generation methods and reviews evaluation metrics.

**Limits / unresolved details:** Survey abstract only; taxonomy details need full text before reuse.

**Thesis implication:** Use as structured citation-tracing source for minimality, validity and semantic quality.

**Comparison use:** Related-work taxonomy rather than algorithm baseline.

**Record:** https://aclanthology.org/2024.findings-emnlp.276/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2024.findings.xml

## [L18] Are self-explanations from Large Language Models faithful?

**Authors:** Andreas Madsen; Sarath Chandar; Siva Reddy
**Year / venue:** 2024 / Findings of the Association for Computational Linguistics: ACL 2024
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official archival metadata and abstract plus primary author-repository README; full paper not accessed

**Contribution reported by source:** Applies self-consistency checks to counterfactual, feature-attribution and redaction explanations; reported reliability depends on explanation type, model and task.

**Limits / unresolved details:** Self-consistency is behavioral evidence and does not expose inaccessible internal ground truth; claims cannot be generalized across models/tasks.

**Thesis implication:** Directly relevant baseline and prior art for target-model counterfactual/redaction tests; undermines treating simple reclassification as novel.

**Comparison use:** Reproduce an access-compatible self-consistency or redaction test, with precise operational terminology.

**Record:** https://aclanthology.org/2024.findings-acl.19/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2024.findings.xml

## [L19] Can LLMs Produce Faithful Explanations For Fact-checking? Towards Faithful Explainable Fact-Checking via Multi-Agent Debate

**Authors:** Kyungha Kim; Sangyun Lee; Kung-Hsiang Huang; Hou Pong Chan; Manling Li; Heng Ji
**Year / venue:** 2024 / Archival venue not independently verified here
**Publication evidence:** Author repository supplies arXiv2024 citation
**Access:** Primary author-repository README; paper full text not accessed

**Contribution reported by source:** MADR generates explanations, uses debater critiques and a judge, then refines against evidence; defines source-related error types and uses PolitiHop.

**Limits / unresolved details:** Evidence faithfulness is distinct from causal faithfulness to a classifier. LLM critics may share errors and add cost; no audience-preservation claim verified in accessed text.

**Thesis implication:** Very close prior art for generation→critique/checking→refinement; integration alone is not new.

**Comparison use:** Consider a budget-matched critique/refinement comparator; isolate adaptation-specific checks.

**Record:** https://arxiv.org/abs/2402.07401

**Evidence inspected:**
- https://raw.githubusercontent.com/SangyunLee1027/Code-for-Towards-Faithful-Explainable-Fact-Checking-via-Multi-Agent-Debate/main/README.md

## [L20] On Evaluating Explanation Utility for Human-AI Decision Making in NLP

**Authors:** Fateme Hashemi Chaleshtori; Atreya Ghosal; Alexander Gill; Purbid Bambroo; Ana Marasovic
**Year / venue:** 2024 / Findings of the Association for Computational Linguistics: EMNLP 2024
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official ACL metadata abstract plus official README and study-template index; full paper not accessed

**Contribution reported by source:** Reviews application-grounded explanation evaluation metrics and dataset-selection criteria; abstract reports only 4 of more than 50 considered explainability datasets satisfy their criteria. On legal-claim verification given contracts, AI predictions with or without explanations did not speed decision-makers without compromising performance. Argues for revisiting team design and deferral.

**Limits / unresolved details:** Task-specific negative result cannot be generalized to every explanation or application. The abstract does not show that explanations are always useless; full protocol/effect sizes remain uninspected. Highlights need for tasks where human-AI teams are meaningful, independent outcome measurement and appropriate deferral.

**Thesis implication:** Direct evaluation-design prior art for thesis human study and suitable decision-support domains; should be read in full before selecting protocol.

**Comparison use:** Protocol and human-study design source rather than explanation-generation algorithm baseline.

**Record:** https://aclanthology.org/2024.findings-emnlp.439/

**Evidence inspected:**
- https://raw.githubusercontent.com/utahnlp/nlp-explanation-utility-guideline/main/README.md
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2024.findings.xml

## [L21] On Measuring Faithfulness or Self-consistency of Natural Language Explanations

**Authors:** Letitia Parcalabescu; Anette Frank
**Year / venue:** 2024 / Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official archival metadata and abstract plus primary author-repository README; full paper not accessed

**Contribution reported by source:** CC-SHAP compares Shapley input contributions toward the answer with contributions toward its explanation; code also implements earlier counterfactual, input-from-explanation, biasing and CoT corruption tests.

**Limits / unresolved details:** Attribution-pattern agreement establishes self-consistency, not guaranteed causal internal faithfulness. Masking assumptions and call/probability requirements matter.

**Thesis implication:** Directly challenges using consistency or an explainer comparison as a faithfulness certificate.

**Comparison use:** Relevant self-consistency comparator where target-model access/compute permit.

**Record:** https://aclanthology.org/2024.acl-long.329/

**Evidence inspected:**
- https://raw.githubusercontent.com/Heidelberg-NLP/CC-SHAP/main/README.md
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2024.acl.xml

## [L22] Tell Me a Story! Narrative-Driven XAI with Large Language Models

**Authors:** David Martens; James Hinns; Camille Dams; Mark Vergouwen; Theodoros Evgeniou
**Year / venue:** 2024 / arXiv:2309.17057 (version/publication metadata pending)
**Publication evidence:** Preprint citation supplied in official README; peer-reviewed venue not verified
**Access:** Official README and citation; no full paper accessed

**Contribution reported by source:** Provides SHAPstories narrative generation with LLMs; example notebook and code accept models exposing predict_proba.

**Limits / unresolved details:** README does not establish claim-level verification, audience preservation, controlled human effects or explanation faithfulness. Those are unknown from this access, not confirmed absent from the paper. Models with predict_proba requirement differs from arbitrary black-box generative APIs.

**Thesis implication:** Direct prior art for translating SHAP attributions into LLM narratives; SHAP-plus-LLM cannot itself be novelty.

**Comparison use:** Potential translation-only implementation comparator after code/paper review and adaptation to same target-model interface.

**Record:** https://arxiv.org/abs/2309.17057

**Evidence inspected:**
- https://raw.githubusercontent.com/ADMAntwerp/XAIstories/main/README.md

## [L23] A Causal Lens for Evaluating Faithfulness Metrics

**Authors:** Kerem Zaman; Shashank Srivastava
**Year / venue:** 2025 / Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract and metadata only; full paper not accessed

**Contribution reported by source:** Causal Diagnosticity uses model editing to create faithful/unfaithful explanation pairs and compare faithfulness metrics.

**Limits / unresolved details:** Official abstract only; exact model-edit validity and construction require full-text review.

**Thesis implication:** Tests need independent diagnostic checks; optimizing a verifier score is not enough.

**Comparison use:** High-priority evaluation reference.

**Record:** https://aclanthology.org/2025.emnlp-main.1496/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2025.emnlp.xml

## [L24] A Necessary Step toward Faithfulness: Measuring and Improving Consistency in Free-Text Explanations

**Authors:** Lingjun Zhao; Hal Daumé III
**Year / venue:** 2025 / Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract and metadata only; full paper not accessed

**Contribution reported by source:** PEX consistency extends weight of evidence to quantify support/opposition of free-text explanations; uses preference optimization.

**Limits / unresolved details:** Prediction-explanation consistency is one aspect of faithfulness, not full internal equivalence; abstract only.

**Thesis implication:** Explicit prediction-explanation consistency metrics and optimization already exist.

**Comparison use:** Relevant metric/optimization comparator if compatible.

**Record:** https://aclanthology.org/2025.emnlp-main.797/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2025.emnlp.xml

## [L25] Cross-Refine: Improving Natural Language Explanation Generation by Learning in Tandem

**Authors:** Qianli Wang; Tatiana Anikina; Nils Feldhus; Simon Ostermann; Sebastian Möller; Vera Schmitt
**Year / venue:** 2025 / Proceedings of the 31st International Conference on Computational Linguistics
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract + author repository README (not full text)

**Contribution reported by source:** Uses two LLM roles, generator and critic, to assess, give feedback/suggested explanation and refine an initial NLE without supervised training.

**Limits / unresolved details:** Abstract/README access only. LLM critique and human preference do not certify target-model faithfulness. Exact evaluation constructs and leakage controls require full text.

**Thesis implication:** Direct prior art against novelty of a separate explanation critic or two-model generation-and-checking architecture.

**Comparison use:** Candidate explanation-refinement baseline; compare fairly against its Self-Refine comparator and control call budget.

**Record:** https://aclanthology.org/2025.coling-main.77/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2025.coling.xml
- https://raw.githubusercontent.com/qiaw99/Cross-Refine/main/README.md

## [L26] FitCF: A Framework for Automatic Feature Importance-guided Counterfactual Example Generation

**Authors:** Qianli Wang; Nils Feldhus; Simon Ostermann; Luis Felipe Villa-Arenas; Sebastian Möller; Vera Schmitt
**Year / venue:** 2025 / Findings of the Association for Computational Linguistics: ACL 2025
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract and bibliographic metadata only; full text and code not retrieved

**Contribution reported by source:** Introduces ZeroCF, attribution-important-word guidance for zero-shot counterfactual generation, and FitCF, which label-flip-verifies these candidates and inserts them as few-shot demonstrations; abstract discusses LIME/Integrated Gradients and ablations.

**Limits / unresolved details:** Only official abstract/metadata read; full protocol, target/generator identity, statistical results, prompt details and licensing not verified. Do not equate author use of faithful with established internal-faithfulness proof.

**Thesis implication:** Very close prior art: attribution-guided generation plus label-flip verification is already expressly proposed.

**Comparison use:** Mandatory near-method comparison for any attribution-guided counterfactual proposal; inspect full text/code before finalizing protocol.

**Record:** https://aclanthology.org/2025.findings-acl.64/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2025.findings.xml

## [L27] LLMs Don’t Know Their Own Decision Boundaries: The Unreliability of Self-Generated Counterfactual Explanations

**Authors:** Harry Mayne; Ryan Othniel Kearns; Yushi Yang; Andrew M. Bean; Eoin D. Delaney; Chris Russell; Adam Mahdi
**Year / venue:** 2025 / Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract/metadata plus author README; full paper not retrieved

**Contribution reported by source:** Studies self-generated counterfactual explanations against empirically elicited LLM decision boundaries; observes a validity–minimality trade-off when prompting for counterfactuals versus minimal counterfactuals.

**Limits / unresolved details:** README identifies tabular binary-classification setting; do not present these results as text-CF evidence or infer complete paper limitations from abstract alone. No numerical effect size asserted here.

**Thesis implication:** Strong near prior art: obtaining valid edits is insufficient; minimality and genuine boundary correspondence need evaluation.

**Comparison use:** Prompt-only counterfactual and minimal-counterfactual conditions are valuable controls; tabular exhaustive-boundary metric does not transfer unchanged to free text.

**Record:** https://aclanthology.org/2025.emnlp-main.1231/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2025.emnlp.xml
- https://raw.githubusercontent.com/HarryMayne/SCEs/main/README.md

## [L28] Multi-Level Explanations for Generative Language Models

**Authors:** Lucas Monteiro Paes; Dennis Wei; Hyo Jin Do; Hendrik Strobelt; Ronny Luss; Amit Dhurandhar; Manish Nagireddy; Karthikeyan Natesan Ramamurthy; Prasanna Sattigeri; Werner Geyer; Soumya Ghosh
**Year / venue:** 2025 / Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract + author repository README (not full text)

**Contribution reported by source:** MExGen extends perturbation-based attribution such as LIME/SHAP to costly, long-context text generation; scores context parts for influence on outputs and reports automated plus human evaluation.

**Limits / unresolved details:** Official abstract/README only. Context attribution is not proof of internal causal reasoning and is not itself audience-adapted claim validation. Method targets context-grounded generation rather than the same bounded classification task by default.

**Thesis implication:** Prior art for model-grounded explanations of LLM outputs and reusable in-context XAI tooling; the application or extending SHAP to text generation alone cannot be new.

**Comparison use:** Relevant evidence-extraction comparator or reusable toolkit; ICX360 includes MExGen, CELL contrastive prompts and token highlighter. README states Apache2.0, not independently licence-audited here.

**Record:** https://aclanthology.org/2025.acl-long.1553/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2025.acl.xml
- https://raw.githubusercontent.com/IBM/ICX360/main/README.md

## [L29] Normalized AOPC: Fixing Misleading Faithfulness Metrics for Feature Attributions Explainability

**Authors:** Joakim Edin; Andreas Geert Motzfeldt; Casper L. Christensen; Tuukka Ruotsalo; Lars Maaløe; Maria Maistro
**Year / venue:** 2025 / Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract/metadata + author README; full paper not accessed

**Contribution reported by source:** Normalized AOPC addresses misleading cross-model comparisons and interprets scores relative to model-specific bounds.

**Limits / unresolved details:** Inspect full-text normalization assumptions and compute costs before adapting to generative LLM labels.

**Thesis implication:** Raw perturbation scores cannot be compared naively across different target models.

**Comparison use:** Metric-design source; primary repository also inspected.

**Record:** https://aclanthology.org/2025.acl-long.86/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2025.acl.xml
- https://raw.githubusercontent.com/JoakimEdin/naopc/main/README.md

## [L30] Self-Critique and Refinement for Faithful Natural Language Explanations

**Authors:** Yingming Wang; Pepa Atanasova
**Year / venue:** 2025 / Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract + author repository README (not full text)

**Contribution reported by source:** SR-NLE iteratively critiques and refines post-hoc natural-language explanations, including feedback derived from feature attribution; no additional training is required in the reported method.

**Limits / unresolved details:** Only official abstract and author README inspected. Self-feedback is not independent ground truth. Exact tested attribution-feedback procedures, intervention assumptions and reported results need full-text scrutiny; no audience-preservation protocol established by these inspected sources.

**Thesis implication:** Direct prior art against claiming iterative explanation verification/refinement or attribution-guided correction as novel.

**Comparison use:** Strong candidate baseline for attribution-feedback refinement; source pipeline includes answer, explanation, feedback and refinement runners.

**Record:** https://aclanthology.org/2025.emnlp-main.427/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2025.emnlp.xml
- https://raw.githubusercontent.com/ymwangv/SR-NLE/master/README.md

## [L31] Towards Faithful Natural Language Explanations: A Study Using Activation Patching in Large Language Models

**Authors:** Wei Jie Yeo; Ranjan Satapathy; Erik Cambria
**Year / venue:** 2025 / Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract and metadata only; full paper not accessed

**Contribution reported by source:** Studies activation patching to compare causal attributions of explanation and answer, avoiding some out-of-distribution probes.

**Limits / unresolved details:** Requires internal access; author claims about comprehensive faithfulness are not independently verified here.

**Thesis implication:** Behavioral token masking and internal causal probes address different constructs.

**Comparison use:** Potential white-box diagnostic comparator after feasibility assessment.

**Record:** https://aclanthology.org/2025.emnlp-main.529/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2025.emnlp.xml

## [L32] A Positive Case for Faithfulness: LLM Self-Explanations Help Predict Model Behavior

**Authors:** Harry Mayne; Justin Singh Kang; Dewi Sid William Gould; Kannan Ramchandran; Adam Mahdi; Noah Y. Siegel
**Year / venue:** 2026 / ICML 2026
**Publication evidence:** Author-repository BibTeX cites ICML2026; proceedings not yet inspected
**Access:** Primary author-repository README; paper full text not accessed

**Contribution reported by source:** Evaluates whether self-explanations help predictor models simulate target-model behavior on counterfactual inputs; includes reference/predictor pipelines and simulatability analysis.

**Limits / unresolved details:** README/code description alone does not establish general fidelity. Simulatability depends on task, target, predictor and prompts.

**Thesis implication:** Counterweight to assuming all self-explanations are useless; investigate when they predict behavior.

**Comparison use:** Complementary explanation-assisted simulatability evaluation if feasible; not direct access to hidden computation.

**Record:** https://arxiv.org/abs/2602.02639

**Evidence inspected:**
- https://raw.githubusercontent.com/HarryMayne/faithfulness/main/README.md

## [L33] Accountable AI with Grounded, Faithful, Consistent, Actionable Rationales: A Case Study in Clinical Trial Matching with VERDICT

**Authors:** Zikai Zhou; Yufei Jin; Yilin Xu; Yu-Chiang Wang; Chieh-Ju Chao; Monica Lam
**Year / venue:** 2026 / Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract + author repository README (not full text)

**Contribution reported by source:** VERDICT converts constraints/policies into SMT/MaxSMT and derives eligibility decisions from a solver, exposing assumptions and pivotal conditions that would change outcomes; combines accountable rationale artifacts with a working clinical trial application.

**Limits / unresolved details:** Official abstract and extensive author README only. Solver-based decisions differ from explanations of an unchanged LLM classifier. Clinical resources and data licensing impose scope costs. README-reported benchmark numbers have not been reproduced; no clinical deployment endorsement.

**Thesis implication:** Strong prior art for evidence-grounded decision support, audit trails, pivotal/counterfactual conditions and explicit undecided states. Changing the thesis to solver decisions would change Review1 scope.

**Comparison use:** Architecture/limitation comparator, not automatically a fair same-task numerical baseline. Abstract metadata lists EMNLP2026; collection ingested 2026-10-21 and month October.

**Record:** https://aclanthology.org/2026.emnlp-main.2598/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2026.emnlp.xml
- https://raw.githubusercontent.com/stanford-oval/clinical-trial-matching/main/README.md

## [L34] Attribute-Based Activation Steering of LLMs for Group-Specific Explanation Generation

**Authors:** Leandra Fichtel; Janek Prange; Henning Wachsmuth
**Year / venue:** 2026 / Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official ACL metadata/abstract plus official research README; no full paper accessed

**Contribution reported by source:** Identifies target-group style/knowledge attributes, computes attribute-based activation steering vectors and adds them during LLM inference. Abstract reports evaluation of group specificity, factuality and human experts compared with prompting/steering baselines; claimed better specificity-factuality balance is author-reported abstract evidence.

**Limits / unresolved details:** Group-specific topic explanation and factuality are not the same as faithful explanation of a target classifier decision. No full-paper protocol/effect sizes inspected. Requires white-box activation access and more infrastructure than simple prompting; README says full generated database exceeds 100 GB with only an exemplary subset shared.

**Thesis implication:** Very direct, recent prior art: audience tailoring with factuality evaluation cannot be claimed first-ever. Promising narrower question: preservation of verified target-model evidence across audience adaptation, assessed separately from encyclopedic factuality.

**Comparison use:** Adaptation baseline or related method; compare prompting-based audience variants first if steering implementation is beyond available compute. Do not imply head-to-head reproduction already run.

**Record:** https://aclanthology.org/2026.emnlp-main.127/

**Evidence inspected:**
- https://raw.githubusercontent.com/webis-de/emnlp26-group-specific-explanations/main/README.md
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2026.emnlp.xml

## [L35] FaithLM: Towards Faithful Explanations for Large Language Models

**Authors:** Yu-Neng Chuang; Guanchu Wang; Chia-Yuan Chang; Ruixiang Tang; Shaochen Zhong; Fan Yang; Andrew Wen; Mengnan Du; Xuanting Cai; Vladimir Braverman; Xia Hu
**Year / venue:** 2026 / Proceedings of the 19th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers)
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract + author repository README (not full text)

**Contribution reported by source:** FaithLM formalizes explanation faithfulness via prediction shifts when explanation content is contradicted; uses contrary-hint scoring and iteratively refines elicitation prompts and explanations.

**Limits / unresolved details:** Official abstract plus minimal official README only. Theoretical soundness is an author claim in the abstract, not independently checked. Different intervention semantics from standard input deletion or counterfactual reclassification; cannot treat scores as equivalent.

**Thesis implication:** Direct 2026 prior art for model-agnostic behavioral explanation assessment linked to iterative improvement.

**Comparison use:** High-priority behavioral verification comparator; full text needed before implementing its contrary-hint score.

**Record:** https://aclanthology.org/2026.eacl-long.177/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2026.eacl.xml
- https://raw.githubusercontent.com/ynchuang/FaithLM/main/README.md

## [L36] Faithful Serum: Mitigating the Faithfulness Gap in Textual Explanations of LLM Decisions via Attribution Guidance

**Authors:** Bar Alon; Itamar Zimerman; Lior Wolf
**Year / venue:** 2026 / Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract + Primary author-repository README; paper full text not accessed

**Contribution reported by source:** Counterfactual hint-influence tests plus PE-LRP attribution guidance injected into attention during explanation generation; open/closed model scripts.

**Limits / unresolved details:** Interventions need suitable open-weight access. README notes narrow useful strength range, with unstable or repetitive outputs if too strong. No universal guarantee verified.

**Thesis implication:** Close recent prior art against novelty based only on attribution grounding or detecting hidden hints.

**Comparison use:** Strong access-matched comparator candidate; include among nearest work.

**Record:** https://aclanthology.org/2026.acl-long.300/

**Evidence inspected:**
- https://raw.githubusercontent.com/Bar-A-94/FaithfulnessSerum/main/README.MD
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2026.acl.xml

## [L37] Gaming the Judge: How Unfaithful Chain-of-Thought Can Undermine Agent Evaluation

**Authors:** Muhammad Khalifa; Lajanugen Logeswaran; Jaekyeom Kim; Sungryull Sohn; Yunxiang Zhang; Moontae Lee; Hao Peng; Lu Wang; Honglak Lee
**Year / venue:** 2026 / Findings of the Association for Computational Linguistics: EMNLP 2026
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract and metadata only; full paper not accessed

**Contribution reported by source:** Studies manipulation of judges by rewriting agent reasoning while holding actions/observations fixed.

**Limits / unresolved details:** Agent evaluation setting differs from classification explanations; abstract-only and no reproduced results.

**Thesis implication:** Independent evidence checks should supplement style-sensitive LLM judgments.

**Comparison use:** Adversarial evaluation motivation, not a direct explanation-generator baseline.

**Record:** https://aclanthology.org/2026.findings-emnlp.1636/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2026.findings.xml

## [L38] iFlip: Iterative Feedback-driven Counterfactual Example

**Authors:** Yilong Wang; Qianli Wang; Nils Feldhus
**Year / venue:** 2026 / Findings of the Association for Computational Linguistics: EMNLP 2026
**Publication evidence:** Official ACL proceedings metadata retrieved
**Access:** Official abstract and bibliographic metadata only; full text and code not retrieved

**Contribution reported by source:** Iterative counterfactual refinement using model-confidence, attribution and natural-language feedback, with number-of-iterations, highly attributed words and early stopping identified as important in the abstract.

**Limits / unresolved details:** October2026 anthology record only; no DOI assigned in accessed metadata. Exact publication/version timing, full protocol, effect-size denominators, human study and code/licence have not been verified. No numeric performance result adopted from abstract.

**Thesis implication:** Very close candidate prior art to attribution-guided iterative validation, feedback and bounded early stopping; novelty must be checked against it.

**Comparison use:** Inspect full text/code and establish release timing; include as nearest related method where reproducible rather than claim iterative feedback itself is new.

**Record:** https://aclanthology.org/2026.findings-emnlp.38/

**Evidence inspected:**
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2026.findings.xml
