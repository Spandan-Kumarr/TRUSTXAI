# Step 2 — Literature Review and Research-Gap Assessment

**Project:** A Trustworthy & Explainable AI Framework for Large Language Model-Based Decision Support Systems  
**Student:** Spandan Kumar Gope · 22MIP10039 · Supervisor: Dr. Rajit Nair  
**Search date:** 26 October 2026  
**Version:** Interim 1.0 — priority full-text verification remains open  
**Purpose:** Research planning for Review 2; not a submitted paper or a claim of established novelty.

## 1. Main finding and completion status

There is a credible research problem here, but the broad integration presented at Review 1 occupies a well-developed research area. Model-grounded explanations, natural-language translation, explanation critique, counterfactual reclassification, iterative refinement and audience tailoring all have substantial predecessors. A new application integrating those components would be a useful engineering deliverable, but integration alone is insufficient evidence of an original research method.

The most promising direction to investigate next is **preservation of supported target-model claims through audience adaptation**, with explicit testing of checker errors, output coverage and computational cost. This is a candidate question, not a finding that no prior work addresses it. It must be tested against the nearest papers in full before committing to novelty.

This interim review contains **38 curated source records**, of which **28 have official ACL Anthology proceedings metadata attached**. Two supplied base papers were available in full. Other evidence comprises official abstracts, primary author/organization READMEs and selected implementation files. No published experimental result has been independently reproduced.

Direct requests to scholarly websites returned proxy-policy 403 errors. A network-access draft was saved, but it has not been applied or published. The accessible official ACL metadata repository and author repositories enabled substantial screening and synthesis. Full-text scrutiny of the closest competitors remains blocked, so **Step 2 is not yet fully closed**. This document distinguishes source claims, inspected code behavior and our research recommendations.

## 2. Search design and its limits

The search combined the two supervisor-selected base papers, a title-keyword screen over specified official ACL collections, citation tracing, and targeted searches for actual author repositories. Thirty XML collections were retrieved across 2019–2026. Their 38,613 paper records yielded 754 title matches using the documented regex. Forty collection-URL requests were made: ten initially used incorrect Findings filenames, returned 404 and were corrected. These failures are URL errors, not excluded papers.

The 38 curated records combine relevant screen hits and citation/repository tracing. They are not the result of full-text assessment of all 754 matches. The selected collections omit some years, venues and workshops; title matching misses papers whose terminology differs. The search is therefore a **bounded, traceable literature review**, not a comprehensive systematic review or a PRISMA selection claim. See SEARCH_PROTOCOL.md and evidence/acl_fetch_log.json for exact coverage and requests.

Inclusion prioritized explanations of model decisions, LLM explanation reliability, relevant text counterfactual methods, natural-language XAI interfaces, audience tailoring and evaluation design. Generic RAG factuality, image explanation and agent-planning papers were not treated as direct classifier-explanation baselines. A few related records were retained to clarify boundaries, such as VERDICT's solver-driven decisions and judge manipulation in agent evaluation.

Official abstracts establish what authors report; they do not allow independent inspection of full protocols, significance tests, ablations or limitations. A README establishes the documented release, not reproduction. A venue named only in an author repository remains author-reported. Bibliographic fields unavailable from inspected sources were left unresolved rather than guessed. In particular, the canonical publication year/issue metadata of the first base paper still needs publisher verification.

## 3. The research area, clarified

### 3.1 Different questions are often called faithfulness

An explanation can be readable, factually supported by an evidence record and useful to a user while still failing to reveal a model's internal decision process. Conversely, a faithful account of a model error need not recommend the correct real-world decision. These are different evaluation targets.

Jacovi and Goldberg argue for explicit assumptions and graded faithfulness [L06]. CC-SHAP distinguishes output-level self-consistency from faithfulness to inner workings, and compares the contributions of input to prediction and explanation [L21]. Madsen et al. use self-consistency checks for counterfactual, attribution and redaction explanations, finding task/model dependence in the reported experiments [L18]. Randl et al. deliberately call their perturbation measure dependability rather than proof of internal faithfulness [L02].

The thesis should separately report task correctness, consistency with supplied evidence, behavioral dependability, counterfactual validity, adaptation preservation and human outcomes. It should not compress them into an unvalidated trust score. Agreement with one attribution method is not ground truth about every aspect of the target model.

### 3.2 The decision model must remain the object explained

The Review 1 scope puts an LLM in the decision path. Explanations and interventions therefore need to refer to that target LLM under recorded prompts, revision and inference settings. TalkToModel and XAIstories demonstrate valuable interfaces and translation methods, but their documented tabular or predict_proba targets are not automatically equivalent to an instruction-tuned generative LLM [L13, L22].

NILE uses explanations as part of prediction [L05]; Faithful CoT uses a structured reasoning/execution approach according to its author repository [L14]; VERDICT derives decisions through SMT/MaxSMT constraints [L33]. These are relevant alternatives, but changing the primary decision process to fit them would change the question from explaining an unchanged LLM to designing a different decision system.

## 4. Synthesis of the main research streams

### 4.1 Grounded explanation generation and refinement

Paper 1 supplies the conceptual motivation for communicating technical explanations to different audiences, but acknowledges the need for empirical validation [L01]. XAIstories already implements SHAP-to-narrative generation [L22]. MExGen provides context-attribution methods for costly, long-input generative LLM tasks, extending the explanatory setting beyond ordinary classifier probability vectors [L28].

SR-NLE uses iterative explanation critique and refinement, including attribution-based feedback, without additional training in the reported method [L30]. Cross-Refine uses a generator/critic arrangement [L25], and the MADR repository describes debate-based refinement for fact-checking explanations [L19]. Faithful Serum, verified in ACL 2026 metadata, guides explanation generation with attribution-informed attention interventions [L36]. FaithLM, verified in EACL 2026 metadata, links contrary-hint intervention scores with iterative refinement [L35].

Consequently, an extra critic, a second LLM, attribution hints, or a repair loop is not by itself a new contribution. The remaining question must specify an actual mechanism, failure mode and evaluation beyond those predecessors. We have not established whether these papers already contain the precise final-claim and audience-transformation checks that a future method would propose; that requires full text.

### 4.2 Counterfactual generation and validation

MiCE searches for minimal contrastive edits against a target predictor, and Polyjuice generates controllable textual perturbations [L07–L08]. CREST combines rationalization with counterfactual generation [L10]. DISCO generates and filters counterfactual data with LLMs, with a data-augmentation emphasis [L12]. The 2024 survey offers a taxonomy and metric review for citation tracing [L17]. These methods address related problems, but augmentation success is not automatically a valid local explanation of the current target LLM.

Randl et al. already generate candidates, reclassify them and retry under a budget [L02]. FitCF explicitly combines attribution-guided generation with label-flip verification [L26]. The recent iFlip abstract describes iterative confidence, attribution and natural-language feedback, including early stopping [L38]. Therefore adding feature importance, flip checking or bounded feedback loops to counterfactual generation cannot support a first-ever claim.

Mayne et al. report a validity–minimality trade-off in self-generated counterfactuals; their repository describes tabular binary tasks, so those findings must not be presented as a free-text benchmark [L27]. The thesis needs both outcome testing and checks on edit extent, semantic adequacy and input constraints. A label-changing string that destroys the task's meaning is not necessarily a useful explanation.

### 4.3 Conversational and audience-adapted XAI

TalkToModel separates dialogue interpretation from executable explanation operations [L13]. InterroLang adapts this line to NLP with attribution, counterfactuals, rationalization and dataset exploration, and reports user simulatability studies [L15]. ConvXAI offers heterogeneous conversational explanations for scientific-writing support [L11]. These systems preclude novelty claims based on a conversational explanation dashboard alone.

The 2026 group-specific explanation paper investigates activation steering for target-group style and knowledge, with factuality and expert assessment [L34]. Audience tailoring plus factuality evaluation is therefore already a research topic. Its topic-explanation setting differs from preserving evidence about a fixed target-classifier decision. That difference is a useful comparison axis, not proof that the latter problem is untouched.

Reframing Human-AI Collaboration already generates explanations and filters them using human-acceptability judgments [L09]. Human acceptance, model simulatability, factual correctness and appropriate reliance remain distinct. Explanation Utility reviews meaningful human–AI teaming and reports task-specific evidence that providing explanations does not necessarily improve efficient decision-making [L20]. The thesis must measure the intended human outcome rather than assume that a preferred explanation improves decisions.

### 4.4 Evaluation and diagnosticity

ERASER supplies rationale-oriented evaluation foundations [L04], while CheckList motivates task-specific behavioral tests [L03]. Normalized AOPC warns that raw perturbation metrics can mislead across models because score ranges depend on the target [L29]. Activation-patching work and Causal Diagnosticity illustrate additional ways to probe or assess explanation metrics [L31, L23]. They require stronger assumptions or model access than a simple deletion test; their scores must not be treated as interchangeable.

PEX consistency explicitly measures whether explanations support or oppose the predicted answer [L24]. The existence of such methods means that merely naming a new consistency score is insufficient. Any score requires a defined construct, independent diagnostics and evidence that it identifies the intended failures.

The 2026 judge-manipulation record shows a related risk when style or fabricated reasoning changes evaluations without changes to observable agent actions [L37]. Its setting is different, but it motivates checking observable evidence rather than relying solely on an LLM's assessment of another LLM's prose. A Positive Case for Faithfulness provides a counterbalancing, author-reported explanation-assisted model-behavior prediction study; its ICML venue claim remains unverified against proceedings [L32]. The field does not support a blanket conclusion that all explanations are always useful or always unfaithful.

## 5. Closest predecessors and fair comparison roles

| Method | Established overlap | Important boundary | Role to consider |
| --- | --- | --- | --- |
| SR-NLE [L30] | Attribution feedback, critique and iterative NLE refinement. | Exact evaluation assumptions require full text. | High-priority same-task refinement comparator. |
| Faithful Serum [L36] | Attribution-guided generation with counterfactual faithfulness tests. | Requires internal model access for attention interventions. | Close methodological comparator if access permits; otherwise explicit scope comparison. |
| FaithLM [L35] | Intervention-based explanation testing and optimization. | Contrary-hint semantics differ from deletion; inspected README is minimal. | Read full method before implementing its score. |
| Cross-Refine [L25] | Separate critic and generator refine explanations. | Critique does not itself establish independent fidelity. | Candidate critic-loop baseline with matched budget. |
| FitCF / iFlip [L26, L38] | Attribution-guided edits, flip checking and iterative feedback. | Full search procedures and release details require scrutiny. | Strong CF baselines, not optional novelty footnotes. |
| XAIstories [L22] | LLM narratives from attribution evidence. | Documented predict_proba interface; not generic LLM access. | Translation-only comparator after justified adaptation. |
| InterroLang [L15] | NLP dialogue, attribution, counterfactuals and rationalization. | Documented task models and user endpoints differ. | System and interaction comparison; not automatic numerical baseline. |
| Group-specific steering [L34] | Audience tailoring with factuality assessment. | Topic explanations differ from target-decision evidence. | Adaptation comparator or design reference. |
| MExGen [L28] | Attribution of context-grounded generated outputs. | Generation/task/cost assumptions differ. | Evidence-extraction alternative when appropriate. |
| VERDICT [L33] | Accountable DSS, assumptions and pivotal conditions. | Solver-derived decisions rather than unchanged LLM decisions. | Architecture/claim-boundary comparison. |

Not every related system needs to be reimplemented. After full-text review, select the nearest feasible methods and state exclusions transparently. If an implementation changes prompts, attribution access or stopping criteria, label it an adaptation rather than a faithful reproduction. Do not call an original method outperformed when only a weakened surrogate was compared.

## 6. A focused implementation-source audit

Two SR-NLE evaluation scripts were fetched and read without execution. In the inspected faithfulness.py snapshot, is_word_in_expl tests whether a lowercased edit_word is a substring of the generated explanation. The script uses this as a faithful/unfaithful indicator and excludes missing outputs; a refined condition also filters on available feedback. The companion counter.py checks changed predictions and tracks valid outputs. Source URLs and SHA-256 hashes are retained in evidence/code-inspection/fetch_log.json.

This is a concrete observation about released scripts, not a finding that the whole paper is wrong. It shows why metric operationalization matters: mentioning an influential word is narrower than supporting every claim in an explanation. Mention may be embedded in a denial, a contradictory sentence or an unrelated statement. Those are logical diagnostic cases suggested by the implementation, not experiments performed here.

The thesis should distinguish influential-evidence acknowledgment from semantic claim support. It should also report the denominator and missing-output coverage when comparing conditions. Optimizing a method against a surface proxy and evaluating only that proxy could make improvements appear stronger than they are.

## 7. What can and cannot support originality

| Proposed claim | Literature finding | Appropriate treatment |
| --- | --- | --- |
| First SHAP-to-LLM explanation application | XAIstories already implements narratives [L22]. | Exclude this novelty claim. |
| First conversational attribution/CF/rationale system | InterroLang and related systems overlap [L15, L11, L13]. | Treat interface integration as engineering. |
| First critique/refine verifier for NLE | SR-NLE, Cross-Refine and MADR overlap [L30, L25, L19]. | Specify a narrower method difference. |
| First attribution-guided validated counterfactuals | FitCF and iFlip overlap [L26, L38]; Randl already reclassifies candidates [L02]. | Use these as prior art and baselines. |
| First audience-tailored explanations with factuality | Group-specific steering directly overlaps [L34]. | Distinguish task and preservation target. |
| Our checker guarantees internal faithfulness | Consistency/faithfulness literature does not justify that inference [L06, L18, L21]. | State the exact tested property and uncertainty. |
| Complete supported-claim preservation under audience transformations is an open gap | Inspected sources do not settle whether nearest full papers already address it. | Candidate only; priority full-text search required. |

A defensible contribution could be a new method, a well-justified diagnostic benchmark or an empirical finding with practical importance. It does not need to claim that all its components were invented. Conversely, renaming existing components or giving them a new interface does not establish a new method.

## 8. Candidate gaps for Step 3

### G1. Evidence preservation through audience transformations

**Question:** When a decision explanation is simplified for a novice or expanded for an expert, can a defined mechanism preserve its supported decision, feature-direction, counterfactual and uncertainty claims?

**Potential distinction:** Evaluate preservation of evidence about the same fixed target decision, rather than general factuality or audience preference. Compare generation-only, attribution-feedback refinement, adaptation without final checks and adaptation with the proposed mechanism.

**Tests needed:** Define claim types and their evidence requirements; assess final text with independently annotated or deliberately controlled cases; compare preservation, false acceptance, useful coverage and cost. Include variations that preserve meaning and ones that change negation, qualifiers, feature direction or counterfactual scope.

**Novelty status:** Unverified. SR-NLE, Faithful Serum, FaithLM, group-specific steering and claim-verification literature must be inspected in full. A claim–evidence schema, postcheck or rejection label alone is not necessarily new.

### G2. Diagnostic testing of explanation checkers

**Question:** Do checkers accept fluent explanations containing unsupported or contradicted model-evidence claims, and do they reject correct paraphrases?

**Potential contribution:** A controlled diagnostic protocol paired with target-model tests could reveal a useful failure mode beyond keyword inclusion. Separate injected-evidence errors from naturally generated errors; neither alone represents the full deployment distribution.

**Novelty status:** Unverified. CheckList, Causal Diagnosticity, CC-SHAP and judge-robustness work are existing foundations. This is most promising as an evaluation contribution supporting G1, rather than an unrelated second project.

### G3. Budget-aware counterfactual trade-offs

**Question:** What validity, minimality, semantic adequacy and coverage can be achieved under a fixed call budget?

**Assessment:** Useful supporting evaluation, but a weaker primary novelty candidate because Randl, MiCE, FitCF and iFlip already cover substantial generation/search/verification territory. A new scheduler would require a clearly differentiated algorithm and comparison; merely choosing a retry count is insufficient.

**Recommendation:** Investigate G1 as the potential main contribution and G2 as its diagnostic evaluation. Treat G3 and the application as supporting components unless Step 3 identifies stronger contrary evidence. Do not finalize this recommendation as a novel method until the reading blockers are resolved.

## 9. Experimental implications already supported by this review

### 9.1 Keep the evaluation layers separate

- **Task performance:** Evaluate target-model correctness against independently supplied labels. Explanation quality cannot repair an incorrect prediction by declaration.
- **Evidence consistency:** Define exactly which claims are supported, contradicted or not testable from the record. Check final text after adaptation, not only the original evidence object.
- **Behavioral dependence:** Use justified interventions and controls. Deletion can change grammar or create out-of-distribution inputs. Attribute evidence to a specified output class and quantity.
- **Counterfactual outcomes:** Distinguish any label flip from the claimed target label; use the same target model and recorded settings. Record instability if repeated inference can change outcomes.
- **Human outcomes:** Separate readability, preference, model simulatability, understanding and appropriate reliance. Measure actual judgments if human benefits are claimed.

### 9.2 Avoid selection-based improvements

If only candidates that change the model's label are retained, validity among accepted candidates can be high by construction. Report the fraction of all original inputs for which the system produced a useful valid output, how many attempts were needed, and which cases failed. A system that releases one easy case and rejects everything else cannot be compared to a fully responding baseline using accepted-case validity alone.

For explanations, report independent estimated error among released outputs together with coverage over all requested inputs. For counterfactuals, report validity, edit magnitude, semantic adequacy, failures, model calls and latency. This is a reporting recommendation, not a new risk-control theorem. No rejection threshold is chosen in Step 2.

### 9.3 Independent diagnostics and fair budgets

Separate development cases used to tune checks from held-out evaluation cases. Include supported paraphrases as well as unsupported claims so a trivial always-reject checker does not appear successful. If feasible, obtain blinded human labels for a defined subset and agreement/adjudication records. An LLM judge alone is not independent truth.

Compare conditions on the same decisions/examples, account for total generation and checking cost, and record retries and model revisions. Do not use a single successful demo as evidence of general improvement. Select statistical procedures and uncertainty estimates in Step 4 after the data structure and hypotheses are specified; no p-values or effect sizes are invented here.

## 10. Dataset and implementation reconnaissance

These are candidates for later feasibility assessment, not selections.

| Resource | Available evidence | Potential use | Important limit |
| --- | --- | --- | --- |
| ERASER movie-review task | Base paper plus official benchmark README and metrics source. | Comparable text classification and human rationale spans. | Human spans are not target-model reasoning; maintain official splits. |
| e-SNLI | Official dataset README inspected. | NLI decisions and human-written explanation material; used in related refinement research. | Human explanation support is not LLM faithfulness; training contamination and split design need assessment. |
| Food Recall Incidents | Supplied Randl paper and repository. | Bounded multi-class hazard task with relatively explicit evidence. | Specialized task and annotation availability; exact version/licence still needed. |
| Toxic Spans / HateXplain | Base-paper Toxic Spans description; separate HateXplain README inspected. | Harmful-language classification with human annotations. | Distinct datasets; do not interchange labels or splits. Subjectivity and identity-related cases need careful evaluation. |
| Contract/claim verification | Explanation Utility abstract and study repository. | Potentially meaningful support task with human judgments. | Domain expertise, documents, permissions and study burden may exceed the initial pilot scope. |

The dataset choice should jointly satisfy target-model access, meaningful decision support, available evidence, licence terms and feasible evaluation. Selecting a familiar dataset solely because a UI example exists would weaken the research justification. Check benchmark memorization and use held-out material where possible; prompted LLM evaluation is not automatically training-free from a contamination perspective.

Code availability is also not uniform. The FaithLM README inspected here is minimal and does not establish a runnable complete release. Some methods require gradients or activation access. Read the actual licence and dependencies before reuse; attribution scores and generative label probabilities require compatible implementations. Selected licences were checked in the thematic notes, but this is not a full dependency/legal audit. No baseline code was executed or installed during this literature stage.

## 11. Priorities and blockers before Step 2 can close

**Priority full texts:** SR-NLE [L30], Faithful Serum [L36], FaithLM [L35], FitCF [L26], iFlip [L38], group-specific steering [L34], CC-SHAP [L21], Explanation Utility [L20], and the closest causal/consistency evaluation papers [L23–L24, L31]. Inspect methods, assumptions, supplementary protocols, task/model access and ablations; revise the candidate gaps if they already cover the proposed mechanism.

**Citation tracing still open:** Agarwal, Tanneru and Lakkaraju's Faithfulness versus plausibility, arXiv:2402.04614, is cited by the second base paper but has not been read directly here. Lanham et al.'s Measuring Faithfulness in Chain-of-Thought Reasoning also remains a primary-source retrieval target. These are reading-queue entries, not reviewed records. Canonical metadata for the first base paper and several author-reported venue/version claims need verification.

**Access action:** The saved environment draft adds scholarly and search destinations while preserving the existing package-manager preset and other settings. The user needs to review/save those network changes in environment settings and publish the environment, as required by the configuration tool. Saving the draft did not change the running network. After a meaningful runtime update, retry actual article access and continue this review. These were proxy-policy denials, not evidence that the papers do not exist or that new credentials are required.

**What can continue without access:** The initial matrix, source snapshots, scope corrections, code-inspection notes and candidate-gap assessment are saved. Further definitive novelty assessment and accurate reproduction of the nearest methods depend on reading the blocked primary texts. Step 3 can discuss candidates, but must not treat this interim review as proof that a method is unprecedented.

## 12. Deliverables and research decisions

- STEP_02_LITERATURE_REVIEW.md, .docx and .pdf: this synthesis and its limits.
- LITERATURE_MATRIX.xlsx and .csv: 38 records with access depth, contribution, cautions and comparison role.
- LITERATURE_LIBRARY.json and ANNOTATED_BIBLIOGRAPHY.md: machine-readable and annotated evidence records.
- REFERENCES_WORKING.bib: provisional citation library; not submission-ready where metadata is flagged.
- SEARCH_PROTOCOL.md and evidence/: exact screening coverage, accessible source excerpts, hashes and limitations.
- GAP_AUDIT.csv and PRIORITY_READING.csv: candidate claims, nearest prior art and remaining verification tasks.

**Supported decisions:** Expand related work beyond the two base papers; avoid broad integration novelty; retain the decision-LLM scope; distinguish explanation properties; strengthen baselines; evaluate coverage and checker errors; keep the interface minimalist.

**Still open:** Final contribution, dataset/model choice, validated novelty, full-text comparison, human-study protocol and manuscript conclusions. No application, thesis results, human-study outcome, publication acceptance or grade claim is made in this stage.
