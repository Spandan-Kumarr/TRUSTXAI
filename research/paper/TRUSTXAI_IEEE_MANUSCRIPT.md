# TRUSTXAI: An Evidence-Bound Framework for Auditable Local LLM Diagnostic Decision Support

**Authors:** Spandan Kumar Gope; [Supervisor Name]; [Reviewer 1 Name]; [Reviewer 2 Name]

**Affiliations:** [Integrated M.Tech CSE (Computational and Data Science), School/Department, Institution, City, Country]; [Supervisor affiliation]; [Reviewer 1 affiliation]; [Reviewer 2 affiliation]

**Correspondence:** [Author e-mail addresses and ORCID identifiers to be supplied]

## Abstract

Large language models can produce fluent clinical suggestions and explanations, but readable prose does not establish that an explanation preserves the behavior of the model that made the decision. This paper presents TRUSTXAI, a local research prototype for four-option diagnostic decision support that binds a frozen model decision to exact case spans, fresh one-span omission queries, a repeated selected-omission query, typed explanation claims, and an exportable audit record. A separate local language model renders simple and technical views from the same canonical facts. Structural checks and a pinned natural-language-inference checker gate release; a failed generation is replaced by a labelled evidence template rather than silently presented as a verified explanation. The framework was frozen before evaluation on a prespecified 60-case diagnosis-only subset of a pinned public MedQA mirror. The fixed Qwen3-4B target returned valid labels for all cases and selected the correct option in 47 of 60 cases (78.33%; Wilson 95% confidence interval, 66.38%--86.88%; macro-F1, 0.7865). Across 407 valid one-span omission queries, 54 changed the model answer, and 32 of 60 cases contained at least one answer-changing omission; all 60 selected-input rechecks agreed. The semantic gate exposed a material negative result: both the typed-plus-entailment and entailment-only configurations rejected all 240 intended-supported and all 480 intended-faulty held-out controls. Consequently, every production-condition natural narrative used the evidence-template fallback. The study establishes computational and engineering feasibility, audit coverage, and a reproducible verifier failure mode. It does not establish clinical utility, mechanistic faithfulness, or independently validated explanation quality.

**Keywords:** clinical decision support, explainable artificial intelligence, large language models, input omission, evidence grounding, computational feasibility

## I. Introduction

Large language models (LLMs) are increasingly considered as interfaces for clinical decision support because they can combine a diagnostic suggestion with natural-language communication. That combination creates two different evaluation problems. The first is whether a model selects the expected answer for a defined task. The second is whether its explanation accurately reports the evidence and observed behavior associated with that selection. A fluent answer can satisfy the first problem while failing the second. In a clinical context, this distinction matters because plausible wording may be mistaken for validated reasoning.

Audience-aware explainability frameworks motivate translating technical records into language suitable for different stakeholders [1]. However, an LLM used as a translator remains a generative model, and the resulting narrative can add, omit, or distort facts. Randl *et al.* distinguish plausible counterfactual explanations from counterfactuals that actually change the target model output [2]. More broadly, faithfulness research separates human plausibility from a specified behavioral or mechanistic relation to a model [3], [4]. These findings motivate a design in which the diagnostic target is not asked to retrospectively invent its own rationale. Instead, the system first records an intervention-based behavior trace and only then permits a separate model to communicate that trace.

TRUSTXAI addresses the following engineering question: can a resource-bounded local clinical decision-support system preserve an auditable link from a fixed diagnostic option to observed input-span sensitivity while refusing to silently release unsupported audience-facing prose? The scope is deliberately narrow. The task is a most-likely-diagnosis question with four supplied options. The intervention is deterministic removal of one contiguous input span at a time. The observation is whether the same pinned target changes its answer. This observation characterizes input sensitivity; it is not a causal clinical explanation or direct access to internal reasoning.

The study is organized around four research questions:

**RQ1 (diagnostic feasibility):** What accuracy, valid-output rate, option-position balance, and resource profile does the fixed local target exhibit on a prespecified held-out diagnosis subset?

**RQ2 (behavioral auditability):** How often do one-span omissions change the frozen target decision, and does a repeated selected omission reproduce the recorded result?

**RQ3 (verifier behavior):** Does the frozen explanation gate retain intended-supported controls while rejecting intended-faulty controls and unsupported natural narratives?

**RQ4 (system feasibility):** Can a local application bind inputs, model identity, omissions, explanation claims, release checks, history, and export records while failing explicitly when required assets or checks are unavailable?

This work makes four contributions. First, it specifies a hash-bound evidence contract that retains exact span offsets, original and modified input digests, model identity, all one-span outcomes, and a selected-result recheck. Second, it renders novice and technical views from the same four canonical facts without allowing the communicator to revise the diagnostic decision. Third, it implements a fail-closed release path combining deterministic claim checks, semantic support scoring, one bounded repair, and a labelled evidence-template fallback. Fourth, it evaluates the complete workflow with frozen model and data revisions, post-prediction gold release, aggregate software tests, and explicit negative reporting when the semantic checker collapses to zero supported-output coverage.

## II. Related Work

### A. LLM Explanations and Behavioral Validity

Faithfulness is not a single property. Jacovi and Goldberg argue that an explanation study must define the relation it intends to test rather than equating interpretability with plausibility [3]. Madsen *et al.* evaluate LLM self-explanations across counterfactual, feature-attribution, and redaction settings and find that reliability depends on the test [4]. Parcalabescu and Frank compare signed contribution profiles for answers and explanations, while describing the resulting measure as self-consistency rather than direct recovery of internal reasoning [5]. Randl *et al.* show that generated counterfactuals may appear plausible yet fail to change the same model's prediction [2]. TRUSTXAI therefore uses restrained terminology: one-span removals produce behavioral observations for a fixed target, not mechanistic explanations.

Critic and refinement pipelines are established prior work. Self-critique and refinement can revise a natural-language explanation while holding the predicted answer fixed [6]. Cross-Refine separates generator and critic roles [7], and Explanation-Refiner combines semantic parsing with symbolic verification [8]. FaithLM and attribution-guided methods use intervention or attribution signals to improve selected faithfulness proxies [9], [10]. TRUSTXAI does not claim novelty for using a critic, entailment model, or repair pass. Its contribution is the integrated evidence and release contract, including complete preservation of failed generation and check records.

### B. Conversational and Audience-Aware XAI

Conversational explanation systems predate this work. TalkToModel supports natural-language interaction with interpretable tabular-model operations [11], while InterroLang combines dialogue with attribution, perturbation, counterfactual, and rationalization functions for natural-language-processing models [12]. Bello *et al.* organize explainability into technical, human-centered, and social levels and position LLMs as mediators between technical outputs and audiences [1]. These studies show that a chat interface or multiple language levels are not, by themselves, novel. In TRUSTXAI, the interface is a delivery layer for an inspectable evidence record, explicit release status, and model provenance.

### C. Medical QA and Explanation Evaluation

MedQA introduced large-scale medical-exam question answering [13]. The present work uses a pinned four-option public mirror and a diagnosis-only subset; the reported result is not a full MedQA leaderboard score. MedExQA adds multiple reference explanations to medical questions and evaluates explanation generation beyond answer accuracy [14]. MedHallu studies medical hallucination detection using context and entailment signals [15]. These resources demonstrate the need to assess medical language generation, but neither answer accuracy nor an automated entailment score establishes that an audience-facing explanation preserves a recorded target-model intervention.

Human evaluation remains necessary for claims about usefulness and appropriate reliance. Chaleshtori *et al.* emphasize application-grounded human--AI tasks rather than readability or preference alone [16]. The current study consequently reports computational feasibility, omission behavior, output coverage, and checker failure. Independent human annotation, clinician assessment, and prospective clinical evaluation are reserved for future work.

## III. Problem Formulation and Scope

Let a diagnostic input be x = (q, S, O), where q is the question, S = (s₁, ..., sₘ) is an ordered set of two to eight contiguous case spans, and O = (oA, oB, oC, oD) contains four distinct candidate diagnoses. A pinned target f returns a label y₀ ∈ {A, B, C, D}. For every span sᵢ, the system constructs x₋ᵢ by removing only that span and freshly queries the same target to obtain yᵢ = f(x₋ᵢ). An omission is answer-changing when yᵢ ≠ y₀.

The system chooses a single result for concise communication. If one or more valid omissions change the label, it selects the shortest changed span, breaking ties by source order. Otherwise, it selects the shortest valid unchanged span. It then queries the selected modified input again to obtain a recheck yᵢ′. Evidence is informative only when the original decision, selected result, and recheck are valid and yᵢ′ = yᵢ. All omissions remain in the audit even though only one is highlighted in the explanation.

Four typed claims define the communication boundary. C1 binds the selected option to its supplied diagnosis name. C2 describes the selected omission and the observed label transition. C3 reports available, tested, valid, and changed counts together with recheck status. C4 states that omissions measure model sensitivity rather than clinical causation or diagnostic confidence. Novice and technical views must express the same facts. The framework makes no claim that these facts reveal complete internal reasoning.

The prototype excludes treatment selection, test recommendation, electronic-health-record integration, autonomous care, and patient-facing deployment. It is evaluated with public exam-style cases. No participant or clinician study is reported, and no institutional ethics determination is inferred.

## IV. TRUSTXAI Framework

### A. Local System Architecture

TRUSTXAI uses four local layers, shown in Fig. 1. A React and TypeScript interface collects the case, question, and options. A FastAPI service validates the task boundary, stores versioned conversations in SQLite, and sends work to a serialized inference worker. The worker separates three model roles: Qwen3-4B-Instruct-2507 records the diagnostic and omission labels; Qwen3-1.7B-GGUF renders the audience views; and nli-deberta-v3-base scores sentence support. The diagnostic target is released before communication and checking to bound memory. The tested research profile performs no remote model inference and makes no GPT or Gemini API call.

<!-- FIGURE_1 -->

The worker processes jobs serially and bounds the queue. Editing a submitted case creates a new immutable case version. The database stores the original input, messages, progress, result snapshot, exact-token checker cache, and export record. Missing assets, invalid model labels, context overflow, queue rejection, and runtime errors remain visible failures. The service does not fabricate a replacement diagnosis.

### B. Evidence Construction

Input validation accepts only a most-likely-diagnosis question and four nonempty, distinct options. Segmentation preserves each span's exact character offsets. A SHA-256 digest binds the question, ordered spans, and options. Dataset answer fields are projected out before model inference.

The target first returns a strict A--D label with greedy decoding. No probability fallback or decision repair is allowed. The system then runs the all-span omission procedure defined in Section III. Each record contains the original and modified input digests, the model signature, returned label and supplied diagnosis name, removed-character count, timing, selected result, and recheck. This creates an auditable behavioral trace while retaining the distinction between a model observation and a clinical explanation.

### C. Dual-Audience Communication and Release

The communicator receives the canonical C1--C4 facts and renders a simple and a technical view. Both views are generated as one structured pair so that audience adaptation cannot silently change the underlying record. Before release, structural checks verify case identity, span offsets, target revision, query digests, option/name consistency, omission counts, selected-result identity, and recheck consistency. Claim-level rules detect changed diagnoses, unsupported counts, added treatment or certainty language, and scope violations.

Every generated sentence is also paired with its supporting canonical fact and scored by the pinned natural-language-inference model. Checker inputs are not truncated; pairs beyond its 512-token limit are unresolved and fail release. One complete-pair repair is permitted, followed by a complete recheck. If either view remains invalid, the interface presents a labelled deterministic evidence template and preserves the unsuccessful narrative and checker report. The fallback demonstrates fail-closed availability behavior, not successful explanation generation.

### D. Interface and Source-Bound Follow-Up

The conversational interface provides history, editable case composition, simple/technical toggles, an evidence drawer, omission outcomes, model provenance, cancellation, versioning, and JSON export. It labels the output as a model suggestion rather than a verified diagnosis. Follow-up chat retrieves from a finite local registry of curated research notes and active-case evidence using TF--IDF. Generated factual sentences require recognized citations and passage support; otherwise, the system returns labelled source passages. This retrieval feature is an engineering component and was not evaluated as a comprehensive clinical-information system.

## V. Experimental Protocol

### A. Data Provenance and Splits

Records came from the public `GBaker/MedQA-USMLE-4-options` mirror at pinned revision `0fb93dd23a7339b6dcd27e241cb9b5eca62d4d18` [17]. The mirror contained 10,178 training and 1,273 test records. Rule-based eligibility restricted the task to diagnosis questions that could be represented by two to eight spans and four candidates, yielding 877 eligible training and 117 eligible test cases.

Three nonoverlapping pools were selected with seed 20261027: 24 feasibility cases from training, 40 development cases from training, and 60 held-out cases from the published test partition. Each pool was balanced by correct answer position, with 6, 10, and 15 cases per A--D position, respectively. This is an option-position control, not disease-class balancing. Exact and near-duplicate grouping found no selected repeated component and no cross-pool component overlap. Raw answer fields were removed from inference inputs, and held-out gold labels were released only after prediction artifacts were frozen.

### B. Models and Frozen Profiles

Table I summarizes the principal models. The diagnostic target ran on Linux x86-64 CPU in FP32 with four threads, thinking disabled, greedy decoding, and at most eight generated tokens. Only an exact normalized A--D response was valid. The communication model used deterministic GGUF inference. The checker used FP32, a 512-token maximum without truncation, and a development threshold grid of 0.60, 0.70, 0.80, 0.90, and 0.95. Model files and revisions were publisher-digest verified. A later Apple FP16/MPS portability profile is not part of any result in this paper.

**TABLE I. FROZEN MODEL ROLES**

| Role | Artifact and revision | Frozen profile |
|---|---|---|
| Diagnostic target | Qwen3-4B-Instruct-2507, `cdbee75f...` [18] | CPU FP32; 4 threads; greedy A--D |
| Communicator | Qwen3-1.7B-GGUF Q8_0, `90862c4b...` [19] | `llama-cpp-python` 0.3.16; deterministic |
| Support checker | nli-deberta-v3-base, `6c749ce3...` [20] | CPU FP32; 512 tokens; no truncation |

### C. Explanation Conditions and Checker Calibration

The frozen matrix contained a decision-only condition, shared-initial dual-view generation, omission-feedback rewrite, critic-plus-single-repair, deterministic evidence templates, and the production typed-plus-checker path. Conditions that required a comparable first draft shared the identical physical generation. A deterministic fallback counted as system output but not as successful narrative generation.

Development diagnostics included 160 intended-supported and 320 intended-faulty controlled slots. No threshold in the prespecified grid accepted any intended-supported slot. Before held-out access, the protocol recorded this failure and selected the least restrictive grid value, 0.60, solely as a frozen fallback operating point. Held-out controls contained 240 intended-supported and 480 intended-faulty slots. Construction intent is used only as a diagnostic proxy; it is not independent semantic ground truth.

### D. Outcomes and Analysis

RQ1 uses accuracy, balanced accuracy, option-position macro-F1, valid-output fraction, confusion matrix, and resource summaries. A two-sided Wilson interval [23] provides a descriptive 95% confidence interval for held-out accuracy. RQ2 uses valid omission count, answer-changing count, cases with any change, and selected-input recheck agreement. RQ3 reports accepted and rejected controls separately for intended-supported and intended-faulty groups and reports natural-output release coverage. The frozen comparative plan used exact paired tests and 5,000 source-cluster bootstrap replicates; formal human-dependent explanation hypotheses are outside the revised computational scope. RQ4 uses manifest integrity, end-to-end integration observations, and software contract tests.

The immutable held-out freeze has SHA-256 `10beddd73bf032819310d9bf2924dbfbffde580b835f6509f205b2c651120518`. Predictions, omissions, prompts, revisions, checker configuration, and per-call costs were checkpointed before gold release.

## VI. Results

### A. Diagnostic Feasibility

Table II reports the three sequential pools. The held-out target returned 60 valid decisions and 47 correct options, giving 78.33% accuracy (Wilson 95% confidence interval, 66.38%--86.88%), 0.7833 balanced accuracy, and 0.7865 macro-F1. Recalls by correct answer position A, B, C, and D were 0.8667, 0.8667, 0.6667, and 0.7333. These values describe the selected diagnosis-only subset and are not comparable to full MedQA leaderboard scores.

**TABLE II. DIAGNOSTIC OPTION PERFORMANCE**

| Pool | Correct/n | Accuracy | Balanced accuracy | Macro-F1 | Valid |
|---|---:|---:|---:|---:|---:|
| Feasibility | 16/24 | 66.67% | 0.6667 | 0.6702 | 24/24 |
| Development | 29/40 | 72.50% | 0.7250 | 0.7171 | 40/40 |
| Held-out | 47/60 | 78.33% | 0.7833 | 0.7865 | 60/60 |

The held-out confusion matrix, with rows denoting the correct option and columns the predicted option, was: A = [13, 1, 1, 0], B = [0, 13, 2, 0], C = [4, 1, 10, 0], and D = [1, 0, 3, 11]. No invalid prediction occurred. The apparent progression across pools is descriptive; the pools differ and are not competing model baselines.

<!-- FIGURE_2 -->

### B. Omission Behavior and Rechecks

All held-out cases produced informative evidence under the operational definition. The system executed 407 valid one-span omission queries. Fifty-four omissions changed the selected option (13.27% of queries), and 32 of 60 cases (53.33%) contained at least one answer-changing omission. Every selected modified input was queried again, and all 60 rechecks reproduced the selected result. Development showed a similar descriptive pattern: 35 changes among 286 valid omissions, 19 of 40 cases with at least one change, and 40 of 40 agreeing rechecks.

These findings answer RQ2 at the behavioral level. They show that all-span auditing and selected-result replication were operational and that answer changes were not rare. They do not identify clinical causal features. Conversely, a non-changing omission should not be interpreted as general robustness because only one bounded text intervention was tested at a time.

### C. Verifier Collapse and Fail-Closed Output

The held-out checker result was unambiguous. Typed-plus-entailment and entailment-only configurations each rejected all 240 intended-supported controls and all 480 intended-faulty controls. Thus, rejection of faulty controls was accompanied by 100% false rejection under construction intent, zero supported acceptance, and no discrimination between the two groups. The same zero-coverage behavior had already appeared in development at every threshold from 0.60 through 0.95.

**TABLE III. HELD-OUT CONTROL CHECKER OUTCOMES**

| Method | Intended-supported accepted | Intended-faulty accepted | Supported false rejection |
|---|---:|---:|---:|
| Entailment only | 0/240 | 0/480 | 100% |
| Typed plus entailment | 0/240 | 0/480 | 100% |

The natural-output proxy likewise accepted 0 of 60 blind-rewrite pairs and 0 of 60 production-condition pairs. The production path therefore released the labelled deterministic evidence template for all 60 cases. This is not evidence that the generated explanations were inferior or that the faulty controls were independently adjudicated. It establishes a severe coverage failure: the chosen entailment component made natural-language release unusably conservative under the frozen protocol. At the same time, the application failed closed rather than describing rejected prose as verified.

### D. Compute and Software Feasibility

Across development and held-out execution, the matrix and diagnostics consumed approximately 22.19 aggregate process CPU-hours, below the allocated 24 hours. The held-out physical matrix contained 407 generation or critic calls. Median wall time was 25.46 s per call and median process CPU time was 64.31 s. Feasibility target inference had a 12.12 s median response time and 18.91 GiB peak resident memory.

The frozen repository state passed 195 backend and research tests, a production frontend build, and four Chromium interface tests. Tests covered input constraints, span offsets, hashes, model signatures, omission/recheck identity, schema and count checks, queue rollback, cancellation, case versioning, citations, export, manifests, and statistical routines. Protocol fakes tested control flow and are not clinical evidence. A separate real-model browser run completed the diagnostic-to-fallback path in 160.08 s wall time with 18.93 GiB peak memory, establishing integration rather than diagnostic correctness because the synthetic case had no gold label.

## VII. Discussion

### A. What the Study Establishes

The fixed local target demonstrated computational feasibility on the selected task: all held-out outputs were valid, and 47 of 60 options matched the released gold labels. More than half of held-out cases had at least one span whose removal changed the target's answer. Because every selected omission was repeated, the highlighted result is distinguishable from a one-off cached observation. These properties support an auditable application workflow in which a reviewer can inspect the exact input, model identity, intervention, and output transition.

The strongest result is not that the explanation checker succeeded. It did not. Deterministic binding made case identities, transitions, counts, and scope mechanically checkable, whereas the general semantic gate rejected every intended-supported control. This distinction matters for trustworthy-system engineering: a fail-closed component can prevent unchecked prose from being released, but excessive rejection can eliminate useful narrative coverage. Safety-oriented refusal behavior and validated explanation quality are different claims.

The evidence template preserved availability of the audit facts without presenting failed prose as a successful explanation. Nevertheless, a template does not prove that clinicians or patients understand the record, and repeated rechecks do not prove that omission behavior reflects clinically meaningful reasoning. Human evaluation is therefore a validation requirement for future claims about usefulness, semantic preservation, and appropriate reliance rather than a result inferred from the current system.

### B. Relation to Prior Work

The observed all-span changes complement counterfactual validity studies [2], [21] by retaining every bounded deletion and repeating the selected modified input. Unlike free-form counterfactual generation, the intervention cannot invent a replacement clinical fact. The tradeoff is that contiguous spans are linguistic units rather than validated medical concepts. Relative to critic and refinement work [6]--[10], the framework contributes full failure accounting and a deterministic fallback but does not show that repair improved semantic quality. Relative to conversational XAI [11], [12], its differentiating object is the evidence contract exposed through the interface, not the conversational layout itself.

### C. Practical Implications

For developers, the results argue for reporting coverage alongside rejection performance. A verifier that rejects every faulty example can appear successful unless supported examples are measured at the same time. Typed invariants should be separated from probabilistic semantic checks so that the source of a failure is visible. For researchers, immutable prediction freezes and post-prediction gold release reduce opportunities for unrecorded test tuning. For users, the interface should display whether a generated explanation, repaired explanation, or deterministic evidence template was released.

## VIII. Threats to Validity, Ethics, and Reproducibility

**Construct validity:** One-span omission is an input-removal test, not a measure of complete internal reasoning, clinical causation, or calibrated confidence. Intended-supported and intended-faulty controls were produced from construction rules and lack independent semantic labels. Consequently, checker findings describe construction-intent behavior and coverage, not clinical sensitivity or specificity.

**Internal validity:** Development preceded held-out access, and gold answers were released after prediction freeze. Exact and near-duplicate controls found no selected cross-pool component. However, source cases may have appeared in model pretraining, which cannot be ruled out. The post hoc Wilson interval is descriptive. Human-dependent H1--H3 comparisons were not used in this revised study.

**External validity:** The 60 cases form a diagnosis-only, option-position-balanced subset of one public mirror. The target, communicator, checker, and CPU configuration are single fixed choices. Results do not generalize to the full MedQA benchmark, other datasets, open-ended diagnosis, clinical notes, other LLMs, or deployed care. There is no GPT/Gemini comparison, clinician evaluation, or prospective validation.

**Software validity:** Contract and browser tests support implementation correctness but cannot validate diagnostic quality or explanation meaning. The source-grounded chat was integration-tested, not evaluated as a clinical retrieval system. The application has no authentication, authorization, encryption at rest, or secure deletion. It should not receive identifiable patient information or be publicly deployed.

**Ethics:** The evaluation used public exam-style records and synthetic interface cases; no participant was recruited and no patient intervention occurred. Output is labelled as a model suggestion for review. The system provides no treatment recommendation and is not a medical device. Local inference limits inference-time data egress but does not establish privacy, regulatory compliance, or security.

**Reproducibility:** The public artifact repository records split identities, source revisions, prompt hashes, model revisions, publisher digests, package versions, native-build provenance, checkpoint manifests, aggregate results, and tests [22]. Raw exam text, private generation traces, SQLite history, and model weights are excluded. Retrieval instructions and hashes permit reconstruction subject to source licensing and availability. The primary results use Linux CPU FP32 only.

## IX. Conclusion and Future Work

TRUSTXAI demonstrates a complete local workflow for binding a four-option diagnostic suggestion to exact case spans, fresh all-span omissions, a repeated selected intervention, typed explanation facts, and an exportable application audit. On the prespecified 60-case subset, the fixed target achieved 78.33% accuracy with 100% valid labels. The omission audit completed 407 valid interventions, found answer changes in 32 cases, and reproduced every selected result. The explanation checker, however, rejected every intended-supported control and every natural production pair. This negative result prevents claims of validated explanation quality while exposing an important engineering failure mode: fail-closed release can preserve audit integrity yet collapse narrative coverage.

Future work will obtain two independent semantic annotations, record inter-rater agreement and adjudication, and evaluate whether novice and technical views preserve the same evidence. Clinician studies should measure comprehension, appropriate reliance, and workflow value rather than preference alone. External datasets, open-ended tasks, stronger local and commercial baselines, calibration, subgroup analysis, retrieval evaluation, adversarial testing, and prospective clinical governance are also required. The semantic gate should be redesigned and recalibrated on independently labelled clinical claims before any generated narrative is considered for practical use.

## References

[1] M. Bello, R. Bello, M.-M. García, A. Nowé, I. Sevillano-García, and F. Herrera, “A three-level framework for LLM-enhanced explainable AI: From technical explanations to natural language,” *Information Systems Frontiers*, 2025, doi: 10.1007/s10796-025-10668-1.

[2] K. Randl, J. Pavlopoulos, A. Henriksson, and T. Lindgren, “Mind the gap: From plausible to valid self-explanations in large language models,” *Machine Learning*, vol. 114, Art. no. 220, 2025, doi: 10.1007/s10994-025-06838-6.

[3] A. Jacovi and Y. Goldberg, “Towards faithfully interpretable NLP systems: How should we define and evaluate faithfulness?” in *Proc. 58th Annu. Meeting Assoc. Comput. Linguistics*, 2020, pp. 4198--4205, doi: 10.18653/v1/2020.acl-main.386.

[4] A. Madsen, S. Chandar, and S. Reddy, “Are self-explanations from large language models faithful?” in *Findings of ACL*, 2024, pp. 295--337, doi: 10.18653/v1/2024.findings-acl.19.

[5] L. Parcalabescu and A. Frank, “On measuring faithfulness or self-consistency of natural language explanations,” in *Proc. 62nd Annu. Meeting Assoc. Comput. Linguistics*, 2024, pp. 6048--6089, doi: 10.18653/v1/2024.acl-long.329.

[6] Y. Wang and P. Atanasova, “Self-critique and refinement for faithful natural language explanations,” in *Proc. EMNLP*, 2025, pp. 8481--8507, doi: 10.18653/v1/2025.emnlp-main.427.

[7] Q. Wang, T. Anikina, N. Feldhus, S. Ostermann, S. Möller, and V. Schmitt, “Cross-Refine: Improving natural language explanation generation by learning in tandem,” in *Proc. 31st Int. Conf. Computational Linguistics*, 2025, pp. 1150--1167.

[8] X. Quan, M. Valentino, L. A. Dennis, and A. Freitas, “Verification and refinement of natural language explanations through LLM-symbolic theorem proving,” in *Proc. EMNLP*, 2024, pp. 2933--2958, doi: 10.18653/v1/2024.emnlp-main.172.

[9] Y.-N. Chuang *et al.*, “FaithLM: Towards faithful explanations for large language models,” in *Proc. EACL*, 2026, pp. 3802--3824, doi: 10.18653/v1/2026.eacl-long.177.

[10] B. Alon, I. Zimerman, and L. Wolf, “Faithfulness Serum: Mitigating the faithfulness gap in textual explanations of LLM decisions via attribution guidance,” in *Proc. 64th Annu. Meeting Assoc. Computational Linguistics*, 2026, pp. 6622--6645, doi: 10.18653/v1/2026.acl-long.300.

[11] D. Slack, S. Krishna, H. Lakkaraju, and S. Singh, “Explaining machine learning models with interactive natural language conversations using TalkToModel,” *Nature Machine Intelligence*, 2023, doi: 10.1038/s42256-023-00692-8.

[12] N. Feldhus, Q. Wang, T. Anikina, S. Chopra, C. Oguz, and S. Möller, “InterroLang: Exploring NLP models and datasets through dialogue-based explanations,” in *Findings of EMNLP*, 2023, pp. 5399--5421, doi: 10.18653/v1/2023.findings-emnlp.359.

[13] D. Jin, E. Pan, N. Oufattole, W.-H. Weng, H. Fang, and P. Szolovits, “What disease does this patient have? A large-scale open domain question answering dataset from medical exams,” *Applied Sciences*, vol. 11, no. 14, Art. no. 6421, 2021, doi: 10.3390/app11146421.

[14] Y. Kim, J. Wu, Y. Abdulle, and H. Wu, “MedExQA: Medical question answering benchmark with multiple explanations,” in *Proc. BioNLP*, 2024, pp. 167--181, doi: 10.18653/v1/2024.bionlp-1.14.

[15] S. Pandit, J. Xu, J. Hong, Z. Wang, T. Chen, K. Xu, and Y. Ding, “MedHallu: A comprehensive benchmark for detecting medical hallucinations in large language models,” *arXiv preprint arXiv:2502.14302*, 2025.

[16] F. Hashemi Chaleshtori, A. Ghosal, A. Gill, P. Bambroo, and A. Marasovic, “On evaluating explanation utility for human-AI decision making in NLP,” in *Findings of EMNLP*, 2024, pp. 7456--7504, doi: 10.18653/v1/2024.findings-emnlp.439.

[17] GBaker, “MedQA-USMLE-4-options,” Hugging Face dataset mirror, rev. `0fb93dd23a7339b6dcd27e241cb9b5eca62d4d18`. [Online]. Available: https://huggingface.co/datasets/GBaker/MedQA-USMLE-4-options

[18] Qwen Team, “Qwen3-4B-Instruct-2507,” Hugging Face model card, rev. `cdbee75f17c01a7cc42f958dc650907174af0554`. [Online]. Available: https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507

[19] Qwen Team, “Qwen3-1.7B-GGUF,” Hugging Face model card, rev. `90862c4b9d2787eaed51d12237eafdfe7c5f6077`. [Online]. Available: https://huggingface.co/Qwen/Qwen3-1.7B-GGUF

[20] Cross-Encoder Authors, “nli-deberta-v3-base,” Hugging Face model card, rev. `6c749ce3425cd33b46d187e45b92bbf96ee12ec7`. [Online]. Available: https://huggingface.co/cross-encoder/nli-deberta-v3-base

[21] Q. Wang, V. B. Nguyen, N. Feldhus, L. F. Villa-Arenas, C. Seifert, S. Möller, and V. Schmitt, “Truth or twist? Optimal model selection for reliable label flipping evaluation in LLM-based counterfactuals,” in *Proc. 18th Int. Natural Language Generation Conf.*, 2025, pp. 80--97.

[22] S. K. Gope, “TRUSTXAI: Research prototype and frozen computational artifacts,” GitHub repository, 2026. [Online]. Available: https://github.com/Spandan-Kumarr/TRUSTXAI

[23] E. B. Wilson, “Probable inference, the law of succession, and statistical inference,” *J. Amer. Stat. Assoc.*, vol. 22, no. 158, pp. 209--212, 1927, doi: 10.1080/01621459.1927.10502953.
