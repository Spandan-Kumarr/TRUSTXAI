# Step 1 — Research Scope and Review 2 Readiness Brief

**Thesis:** A Trustworthy & Explainable AI Framework for Large Language Model-Based Decision Support Systems  
**Student:** Spandan Kumar Gope · 22MIP10039  
**Programme:** Integrated M.Tech CSE (Computational & Data Science), VIT Bhopal University  
**Supervisor:** Dr. Rajit Nair  
**Reviewers:** Dr. Vinesh Kumar; Ms. Neha Rathore  
**Prepared:** 26 October 2026 · Step 1, version 1.0  
**Document purpose:** Internal research planning and scope clarification; not a completed thesis, experimental report or submission manuscript.

## 1. Executive finding

This thesis concerns the reliability of explanations attached to decisions made by a large language model (LLM). The application will make the research method usable and inspectable. Its scientific contribution must come from a well-defined method and supporting experiments, rather than from combining familiar tools behind a new interface.

The strongest scope consistent with the Review 1 presentation is to investigate whether model-grounded evidence, explicit explanation checks and counterfactual testing can support audience-adapted explanations without introducing unsupported claims. This is a working research direction, not a verified novelty claim or a finding that the proposed method works.

The two base papers support complementary motivations: audience-aware communication and empirical scrutiny of self-explanations. They do not establish that combining these components is new. A broader, documented literature search is the next step.

For Review 2, the practical target is a bounded, reproducible research prototype, actual comparative evidence, a supervisor-reviewable IEEE manuscript and a Phase I report. This target is our preparation recommendation. The supplied university documents do not specify an implementation percentage, fixed experiment count or minimum accuracy.

## 2. Sources and strength of evidence

This brief uses the seven supplied files and the student's messages. It does not include a new online literature search. Page references below are physical PDF pages; slide references use the presentation's slide order.

| ID | Source | What it establishes |
| --- | --- | --- |
| S1 | DSN5098 syllabus, 7 pages | Course aims, individual project methodology, evaluation weights and report/publication requirements; especially pp. 2–3 and Review II form p. 5. |
| S2 | Guidelines for DSN5098 Master Thesis / Internship, 2 pages | Supervision, individual project work, report, review, attendance, plagiarism-report and publication provisions. |
| S3 | MT Final Review Assessment Form, academic year 2026–2027, 3 pages | Current Review 2 and Review 3 criteria, p. 2; final review criteria, p. 3. |
| S4 | Review 1 Master Thesis presentation, 22 slides | Presented title, proposal, planned modules, provisional evaluation and reported progress. Slide 22 contains no substantive extracted text. |
| S5 | Bello et al., A Three-level Framework for LLM-enhanced Explainable AI, 22 pages | Conceptual framework, audience roles, illustrative cases and acknowledged empirical limitations. |
| S6 | Randl et al., Mind the gap, 38 pages | Empirical self-explanation analysis, counterfactual validation, evaluation methods and limitations. |
| S7 | conference-template-a4 (3).docx | Supervisor-supplied IEEE A4 conference-paper layout and writing examples; not a university thesis-report template. |
| U1 | Student's messages in this conversation | Review dates, completed Review 1, reported reviewer feedback, supervisor instruction and minimalist application preference. |

S4 records what was presented, rather than independently proving that implementation or experiments exist. U1 is the source for the dated schedule and reported feedback; signed review comments and marks have not been supplied. S7 contains example author details and references that are not confirmed metadata for this project.

## 3. What the title means operationally

**Trustworthy:** Evaluate specific reliability properties and limitations. A fluent explanation or a verification badge cannot certify a system as safe, fair or legally compliant.

**Explainable:** Provide inspectable evidence related to the target model's decision, state what the evidence measures, and test relevant explanation claims. A generated rationale is not automatically a faithful account of internal computation.

**AI framework:** Define a modular, reproducible procedure that connects evidence extraction, checking, communication and evaluation. The scientific method must be distinguishable from the application interface.

**LLM-based decision support:** The Review 1 proposal puts an LLM in the decision path (S4, slides 12, 16–17, 19). A person remains responsible for consequential decisions. A research benchmark can simulate a bounded support task without becoming a deployed professional advisory service.

**Working scope statement:** Design and empirically evaluate a framework for a bounded LLM classification-based decision-support task, measuring how explanation verification and audience adaptation affect evidence consistency, behavioral reliability, counterfactual validity, cost and, where supported by an actual study, human understanding and appropriate reliance.

Classification is a recommended starting scope because decisions and counterfactual outcomes can be tested more clearly than unrestricted recommendations. The exact task, dataset and model remain open until literature and feasibility assessment. The approved thesis title is retained unchanged.

## 4. What has and has not been completed

| Item | Evidence-based status at Step 1 |
| --- | --- |
| Title and research area | Presented in S4, slides 1–2; retained as the working thesis scope. |
| Base papers | Selected with the supervisor according to U1; reviewed for this brief. |
| Literature synthesis and gap identification | S4, slide 13, reports completion at Review 1. No broader search log or full literature matrix has been supplied, so novelty remains unverified. |
| Architecture and modules | Proposed in S4, slides 12, 17 and 19; not yet experimentally validated. |
| Domain, task and dataset | Explicitly not finalized in S4, slide 6. |
| Model, XAI method and compute | Candidate tools only, S4, slide 14; selection remains open. |
| Application and experiment code | No code supplied. Current TRUSTXAI checkout contains no project files or commits before this Step 1 documentation. |
| Results and baseline comparisons | Not provided. S4, slide 18, explicitly does not claim experimental results. |
| Human evaluation | Planned; no participants, consent procedure or study outcomes provided. |
| Manuscript | Supervisor requested preparation in IEEE format; no completed manuscript supplied. |
| Publication status | No submission, acceptance or publication evidence supplied. |

Step 1 completes a scope audit. It does not retroactively convert proposed modules into completed work.

## 5. What the base papers contribute

### 5.1 Paper 1: audience-aware explanation framework

Bello et al. propose three levels: algorithmic/domain-informed explanation; human-centered interaction; and societal transparency. The explaining LLM translates existing technical explanations into accessible dialogue. The decision model need not itself be an LLM (S5, section 3, pp. 8–13).

The loan-approval illustrations combine SHAP, decision trees or example-based reasoning with natural-language explanations. The GPT-4.5 examples are explicitly illustrative (S5, section 4, pp. 14–18, especially p. 15). The authors acknowledge that the framework requires further empirical validation (p. 18). These examples are not evidence of measured gains in human understanding, calibrated trust or freedom from hallucination.

**Relevance:** Provides the audience and communication perspective. It motivates empirically checking whether technical evidence survives translation and adaptation.

### 5.2 Paper 2: plausibility, dependability and counterfactual validity

Randl et al. study LLMs that classify inputs and then generate extractive or counterfactual self-explanations. They evaluate food-hazard, movie-review sentiment and toxic-span classification using 200 selected inputs per task (S6, sections 3–4.1, pp. 6–8).

They find that plausible self-explanations need not track internal model behavior. Their counterfactual procedure generates candidates, reclassifies them with the target model, and keeps candidates meeting its validity condition. Finite retry budgets can fail (S6, section 4.4, pp. 16–18; Appendix H, p. 35).

The paper calls its perturbation test **dependability**, because the test does not cleanly separate plausibility from faithfulness (section 4.3, pp. 10–11). Counterfactual validity is narrower than full faithfulness. Limitations include classification-only tasks, decoder-only models, limited prompt analysis, no actionability evaluation, gradient experiments limited to models up to 9B parameters, and SHAP used as a runtime comparison rather than a strong counterfactual baseline (sections 5–6, pp. 18–20).

**Relevance:** Provides empirical methods and cautions for verifying explanations about an actual LLM decision model. Its reported average speed advantage over SHAP is specific to its experiments and must not be transferred to this thesis as an expected result.

### 5.3 What their combination does not establish

Neither the two papers nor the Review 1 presentation establish a first-ever framework, a new verification algorithm, improved accuracy, elimination of hallucination, or generalizable human trust benefits. Each prospective contribution must survive the broader Step 2 literature search and Step 3 novelty assessment.

## 6. Distinguishing the properties we will evaluate

| Property | Meaning in this project | What it does not prove |
| --- | --- | --- |
| Task correctness | Predicted label agrees with independently supplied reference labels. | A correct explanation, safety or a correct decision in every real setting. |
| Evidence consistency / grounding | Explanation claims match the supplied attribution, input, prediction and validation records. | That the evidence fully reveals the model's internal reasoning. |
| Behavioral evidence / dependability | Specified interventions test whether highlighted evidence tracks target-model behavior. | Full internal faithfulness or complete causal access to latent reasoning; results depend on intervention assumptions. |
| Counterfactual validity | The concrete edited input produces the claimed outcome from the same target model under stated inference settings. | Real-world actionability, causal feasibility, fairness or factual truth. |
| Plausibility | People judge an explanation to be sensible. | Faithfulness or validity. |
| Audience preservation | Adaptation changes presentation while retaining supported factual content and limitations. | Improved human understanding without measuring it. |
| Appropriate reliance | People accept useful correct advice and appropriately question or reject incorrect advice. | Merely higher confidence, satisfaction or preference. |
| Robustness / consistency | Behavior is evaluated under specified, justified changes. | Identical outputs for every perturbation; some changes should change the answer. |

Agreement with SHAP, another explainer, an LLM judge or a human annotation is a comparison signal, not privileged ground truth about internal reasoning. Counterfactuals are interventions on the model input; they are not automatically causal claims about the world.

## 7. Roles and conceptual verification boundary

### 7.1 Decision LLM and communication LLM

The **decision LLM** produces the classification to be explained. Evidence and behavioral tests must refer to that same target model, with the same task definition and recorded inference configuration.

The **communication LLM** renders evidence for a user and may answer bounded follow-up questions. It may use the same underlying model weights with a separate prompt, or a different model; this is not decided in Step 1. Its explanatory role must be distinguished from the target decision process.

A conventional classifier can be a clearly labelled comparator or auxiliary model. Explaining it does not establish an explanation of the LLM's decision. A silently substituted classifier would change the presented scope.

### 7.2 Conceptual flow

1. Record the input, target-model decision and inference configuration.
2. Extract candidate evidence compatible with the target model's actual access conditions.
3. Test relevant evidence and concrete counterfactual candidates; retain both successful and failed checks.
4. Construct an evidence record with explicit support, uncertainty and limits.
5. Generate an audience-adapted candidate explanation using that record.
6. Check the final rendered claims against the record. Where a supported check fails, repair with a bounded procedure or report insufficient support rather than inventing a justification.
7. Display the decision, explanation, supporting evidence and the scope of checks; retain an audit record.

This flow clarifies the Review 1 design, not a finalized architecture or novel algorithm. Checking only before communication is insufficient: generation and audience rewriting can introduce new claims. Any follow-up response making additional claims needs the same discipline. A checker passing means only that its defined checks passed.

### 7.3 Access and experiment constraints

Black-box API access does not automatically provide gradients, attention matrices or calibrated label probabilities. Local open-weight models may enable additional methods but require suitable compute and licences. Method selection must match actual access. Behavioral probes and repeated generation add cost and can be sensitive to prompts and inference variability.

Record prompts, model revisions, seeds where supported, generation settings, candidate budgets, data splits and failed outputs. Caching should avoid repeated calls without mixing conditions or leaking evaluation data. Log-probabilities and attribution values must be labelled with their actual units; they are not automatically percentages or confidence scores.

## 8. Bounded scope for Review 2

### 8.1 Recommended core

- One clearly defined primary classification-based support task with identifiable intended users and licensed benchmark data.
- A feasible target LLM and evidence-extraction approach matched to its access conditions.
- A testable verification contribution selected after literature assessment.
- Counterfactual reclassification with explicit failure reporting and a fixed budget.
- Limited, clearly defined audience views that preserve supported content.
- Reproducible baseline comparisons, targeted ablations, cost measurement and error analysis.
- A minimalist application that exposes evidence and limitations, plus report and manuscript documentation.

These are research planning recommendations, not university-mandated counts or proof that each component is novel. Multiple models or datasets should be added only when feasible and necessary to support the intended claims. A one-task pilot must be described as such and cannot support broad cross-domain claims.

### 8.2 Baselines already proposed at Review 1

Retain the four proposed conditions as candidates: unverified LLM self-explanation; standalone technical XAI output; XAI-to-LLM translation without verification; and the integrated approach (S4, slide 18). Step 4 must make them comparable by controlling the target decision model, examples, generation budgets and evaluation conditions where applicable.

Standalone XAI is not a natural-language system, so comparisons must respect output format. A separate verification-only versus verification-plus-adaptation comparison may help isolate adaptation effects; it is a candidate ablation, not a finalized experiment.

### 8.3 Outside the initial scope

Training a foundation model from scratch, unrestricted agents, many unrelated domains, clinical or financial deployment, a large decorative dashboard and unsupported claims of universal trustworthiness are outside the recommended initial scope. Retrieval augmentation or fine-tuning should be added only if the eventual research question requires them.

Human evaluation remains part of the presented ambition. Its claims require an appropriate protocol, applicable institutional permission and actual participants. If those are unavailable by Review 2, report the technical pilot and human-study plan honestly; do not substitute simulated responses or LLM ratings for participant evidence.

## 9. Candidate research questions for later refinement

**RQ1 — Evidence preservation:** Does the proposed checking method reduce unsupported or contradictory explanation claims relative to unverified and translation-only baselines on the same target-model decisions?

**RQ2 — Behavioral evidence:** Under a specified intervention protocol, how do the proposed explanations compare on behavioral dependability, and how do those results differ from narrative evidence consistency?

**RQ3 — Counterfactual checking:** What validity, semantic-change and failure-rate trade-offs arise when generated counterfactuals are reclassified under a bounded budget?

**RQ4 — Audience adaptation:** Does adaptation preserve verified factual content across defined audience views, and, if an actual user study is feasible, improve understanding without increasing inappropriate reliance?

**RQ5 — Practical cost:** What latency, model-call, compute and coverage costs accompany any observed reliability improvements?

These questions are provisional. Step 3 should select a small primary set, state falsifiable hypotheses and distinguish the principal contribution from supporting evaluations. No improvement is assumed in advance.

## 10. Review 2 assessment and evidence to prepare

Review 2 is assessed out of 50, contributing 25% to final grading (S1, p. 3; S2, p. 2). The table uses the current 2026–2027 assessment wording (S3, p. 2). Suggested evidence is our interpretation for preparation.

| Assessment criterion | Marks | Evidence to prepare |
| --- | --- | --- |
| Application of engineering principles and concepts | 10 | Defined task, justified algorithms, model/explainer access assumptions and measured quantities. |
| Problem-solving approach / methodology used | 10 | Literature-supported problem, research questions, reproducible method, fair comparisons and preliminary analysis. |
| Modern tool usage | 5 | Working research pipeline, suitable libraries, useful application and reproducible execution. |
| Ethics / social relevance / environmental consideration | 10 | Intended users, privacy and licence handling, misleading-explanation risks, human-study safeguards where applicable and measured compute/cost limits. |
| Phase 1 documentation / article submission in journals or conferences etc. | 10 | Phase I report and IEEE manuscript with truthful draft/submission status. Confirm any additional school-specific submission expectation. |
| Communication and presentation skills | 5 | Clear PPT, understandable demonstration, explanation of findings, failures and next steps. |

The report is needed at Review 2 even though the separate submission date is later. Paper preparation does not replace the Phase I report. The current form mentions article submission within one criterion; it does not expressly require acceptance by Review 2. Review 3 mentions acceptance and the final form mentions publication; the overall guidelines also require a publication outcome. Confirm the acceptable route with the supervisor before selecting a venue.

## 11. Dates, document formats and academic presentation

| Milestone | Student-supplied schedule | Consequence for preparation |
| --- | --- | --- |
| Review 2 | 18–20 November 2026, online | Prepare report, PPT, demonstrable work and backup evidence before the assigned slot. |
| Phase I report submission | Before 25 November 2026, online | Have the review version ready earlier; incorporate review feedback before submission. |
| Review 3 | 20–22 January 2027, online | Plan extended experiments, analysis and feedback incorporation. |
| Final review | 1–3 March 2027, offline | Final demonstration, thesis and publication-outcome evidence as required. |
| Final Phase II report | Before 8 March 2027, offline | Final university-format submission. |

These dates come from U1, not the undated review schedule in the PDFs. The generic documents require hardcopies, while U1 gives online Phase I logistics; confirm the current delivery instructions without delaying independent research.

The reported supervisor instruction is: **“Prepare a research paper in IEEE format.”** S7 is an A4 conference template with a two-column main body and example author blocks. Preserve relevant formatting when drafting, replace all sample content, and establish real authorship before submission. IEEE formatting alone does not identify a venue, prove IEEE publication, or set a page limit. The Phase I university report format has not been supplied.

The application should present a concise input/output workflow, evidence view, checked counterfactuals and labelled results tables or plots. Use restrained colour, legible typography and explicit check statuses. A single uncalibrated “trust score” would obscure distinct properties and is not currently justified. Research quality comes from the method and evidence, not visual complexity.

The university documents call for individual project work, supervisor interaction, review attendance and a plagiarism-check report. No numerical similarity threshold or AI-assistance policy has been supplied. The student must understand and be able to reproduce and defend the work; preserve provenance and follow applicable disclosure and authorship rules. This brief is not an originality certificate or a plagiarism report.

## 12. Decisions, questions and next-step handoff

### 12.1 Established for planning

- Retain the presented title and LLM decision-support scope.
- Treat the primary decision model and explanatory communication as distinct roles.
- Keep grounding, behavioral evidence, counterfactual validity and human plausibility separate.
- Include checking after audience adaptation; do not equate a checker pass with universal correctness.
- Build a minimalist, evidence-inspectable prototype alongside a reproducible research pipeline.
- Keep manuscript, Phase I report and Review 2 PPT as separate deliverables.

These are scope conclusions and design recommendations, not newly approved supervisor instructions.

### 12.2 Open decisions, with when they matter

| Question | Current handling | Needed by |
| --- | --- | --- |
| Any supervisor constraint or correction after Review 1? | An optional question has been sent. Until answered, use S4 and the reported IEEE instruction; do not infer additional approvals. | Scope refinement; incorporate new guidance when supplied. |
| Which gap is insufficiently addressed in existing research? | Open; investigate nearest methods, not just the two base papers. | Steps 2–3. |
| Which task, data, target model and XAI method? | Open; compare alternatives rather than select for interface convenience. | Step 4. |
| Available local/cloud compute, approved API budget and model access? | Check actual capabilities and required credentials; request only remaining constraints. | Before experiment commitment in Step 4. |
| Human-study permission, participant access and consent process? | Not provided; do not claim human-study findings. | Before recruiting or collecting responses. |
| Phase I template, certificates, plagiarism-check process and current submission logistics? | University-format requirement known; specific template and thresholds not supplied. | Report preparation, with report available for Review 2. |
| Venue, author order and publication-route expectations? | Not specified by the IEEE-format instruction. | Manuscript submission planning. |

None of these open choices prevents beginning the Step 2 literature search. Decisions tied to credentials, participants or institutional requirements must be resolved before dependent work.

### 12.3 Step 2 search brief

Search for empirical work on LLM self-explanation reliability; model-grounded natural-language explanations; explanation claim checking; perturbation-based evaluation; validated text counterfactuals; audience-adaptive explanations; and human understanding/appropriate reliance. Include relevant foundational work and current work through the actual search date. Use citation tracing from both base papers and compare nearest competing methods and available code.

Record queries, sources, search dates, inclusion/exclusion reasons, peer-review/preprint status, datasets, model-access requirements, baselines and evaluation weaknesses. Verify publication metadata and distinguish author claims from demonstrated results. Step 2 should end with a traceable literature matrix and candidate gaps, not a preselected claim that the system is unprecedented.

## 13. Source references and Step 1 completion

**[S5]** M. Bello, R. Bello, M.-M. García, A. Nowé, I. Sevillano-García, and F. Herrera, “A Three-level Framework for LLM-enhanced Explainable AI: From Technical Explanations to Natural Language,” *Information Systems Frontiers*. DOI: https://doi.org/10.1007/s10796-025-10668-1. Supplied PDF: accepted 19 November 2025; copyright 2025, modified publication 2026. Canonical publication year, volume and pagination require publisher-metadata verification in Step 2.

**[S6]** K. Randl, J. Pavlopoulos, A. Henriksson, and T. Lindgren, “Mind the gap: from plausible to valid self-explanations in large language models,” *Machine Learning*, vol. 114, art. 220, 2025. DOI: https://doi.org/10.1007/s10994-025-06838-6. Published online 27 August 2025 in the supplied PDF. The paper reports code at https://github.com/k-randl/self-explaining_llms under GPLv3; repository contents have not yet been audited.

S4, slide 21, includes a generic “additional peer-reviewed literature” entry. It is not a usable citation and must be replaced with full, verified references in later deliverables.

**Completed:** source inspection; current-status audit; title interpretation; role clarification; property definitions; bounded scope; provisional questions; rubric mapping; unresolved-decision register; Step 2 handoff.

**Not completed in Step 1:** broad literature search, novelty validation, task/model selection, application implementation, experiments, human study, research manuscript, Phase I report or Review 2 presentation. No result, acceptance or publication claim has been made.
