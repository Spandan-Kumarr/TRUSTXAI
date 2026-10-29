# Step 3 — Research Contribution and Method Specification

**Approved thesis title retained:** A Trustworthy & Explainable AI Framework for Large Language Model-Based Decision Support Systems  
**Student:** Spandan Kumar Gope · 22MIP10039 · Supervisor: Dr. Rajit Nair  
**Prepared:** 27 October 2026 · Version 1.0  
**Status:** Working research specification for Step 4; no implementation, results or verified first-ever claim.

## 1. Selected research direction

Investigate whether an explicit, evidence-backed claim plan and final-text checks improve preservation of model evidence when an explanation of a fixed LLM decision is rendered for novice and expert audiences.

The working method name is **TRUSTXAI: evidence-preserving audience adaptation**. TRUSTXAI is the existing project label, not a claim that this name or method is globally unique. A possible later manuscript title is “Preserving Model Evidence in Audience-Adaptive Explanations of LLM Decisions.” The approved thesis title remains unchanged.

**Unit of study:** one source input, one fixed target-model decision, one versioned evidence record and two explanations expressing a shared essential claim set in different styles. The central output is a tested preservation procedure, supported by a reproducible diagnostic evaluation and a minimalist research application.

**Problem statement:** Audience adaptation can change which facts an explanation expresses, their direction, scope or uncertainty. A fluent rewrite may omit a limitation, reverse a feature effect, or turn one observed counterfactual outcome into a universal promise. Behavioral tests of the underlying model do not automatically validate that final prose. The study will evaluate this transition rather than claim access to the model's complete internal reasoning.

The method is selected for development, subject to task/model feasibility and further novelty checks tied to its exact specification. It is a research proposal, not a supervisor-approved change or demonstrated improvement.

## 2. Basis for selection and alternatives rejected

Step 2 assembled 43 records and 19 full-text audits. Stable references L01–L43 refer to that library. The gap statement is bounded to those inspected sources.

| Direction considered | Assessment | Decision |
| --- | --- | --- |
| General XAI plus LLM dashboard | Existing conversational and narrative systems overlap [L13, L15, L22]. | Engineering output, not the main novelty claim. |
| Critic/refine explanation generation | SR-NLE, Cross-Refine and FaithLM already address refinement [L30, L25, L35]. | Include strong comparisons; do not rename a critic loop as new. |
| Iterative validated counterfactual generation | Randl, FITCF and iFlip already cover major components [L02, L26, L38]. | Supporting evidence component; no new search algorithm claimed. |
| Audience adaptation with fact checking | Group-specific steering already evaluates atomic facts against Wikipedia [L34]. | Generic postgeneration fact checking is insufficient novelty. |
| Typed preservation of fixed decision evidence across audience views | Distinguishes the evidence object, obligation set and evaluation target from those inspected protocols. | Selected candidate; specify and test its incremental contribution. |

The promising difference is the precise preservation task and its operational evaluation. Individual components—structured records, checks, templates, abstention, bounded repair and provenance—have prior art. Combining them does not by itself prove originality. Literature outside the bounded review can still contain a close method.

## 3. Intended contributions and permitted claims

**C1 — A preservation procedure.** Define an audience-independent essential claim plan derived from a fixed target decision and a versioned evidence record. Render audience variants, then check the final prose against the obligations. Do not change the decision to make an explanation easier to justify.

**C2 — A diagnostic protocol.** Evaluate both meaning-preserving variants and controlled meaning-changing faults in decision labels, attribution qualifiers, concrete counterfactual outcomes and limitations. Also evaluate naturally generated outputs separately. Establish what the checker detects and misses rather than treating its pass signal as truth.

**C3 — An empirical characterization.** Measure complete supported-output yield, checker errors, omission, cross-view drift, failure coverage and cost against strong baselines and ablations. Report mixed or null findings if observed.

**Engineering deliverable.** An application exposes the target decision, evidence, checked edited inputs, audience views and check limitations. This makes the method inspectable; it is not an independent novelty claim.

A future manuscript may state “we propose and evaluate” only once the method has been implemented and evaluated. At this stage the correct wording is “the study will test.” No guarantee of internal faithfulness, fairness, safety, publication acceptance or improved grades follows from this specification.

## 4. Formal objects and model roles

Let f be the fixed target LLM, x the original input, c the complete task/inference configuration, and y = f(x; c) its recorded decision. Generated explanations do not replace y. A prediction can be wrong against the dataset label while an explanation accurately describes the recorded model behavior; report these separately.

Let E be the versioned evidence record and P(E) a selected essential claim plan. Let G(E, P, a) render an explanation for audience a, where a is novice or expert. Let V assess the rendered text against E and P. V is an imperfect checker to evaluate, not an oracle.

Keep these roles distinct: target predictor, evidence extractor, counterfactual generator, communication generator, claim extractor/checker and any semantic annotator/judge. Roles may share model weights for feasibility, but shared weights do not establish independent validation. An evaluation model different from the generator is also not automatically independent truth.

### 4.1 Required evidence bindings

E records input identity, target model/revision, task prompt, output-label definitions and inference settings. Each evidence item records its source, scope and status. An attribution additionally binds its method, target class, score function, reference/baseline, feature/span and units. A counterfactual binds the exact original and edited inputs, requested target, observed target-model output and test settings.

Use content identifiers or hashes to reject stale/mixed evidence: an attribution for a different input, model, class or score function cannot silently support the current narrative. Hash equality ensures identity, not scientific correctness. Random seeds, where supported, do not guarantee identical remote-model behavior.

Data licences, split identifiers and experiment provenance are required implementation records. No secret values belong in evidence logs.

### 4.2 Claim types and support rules

| Type | Permitted statement | Required support and boundary |
| --- | --- | --- |
| Decision | The target model returned label y for x under c. | Exact recorded prediction; do not equate y with verified real-world truth. |
| Attribution | A specified feature has the reported score/direction for the named output quantity. | Matching method/class/scale; unsigned magnitudes do not support positive/negative direction or causal language. |
| Counterfactual observation | The exact tested edit produced the recorded label under c. | Direct target-model calls, edited-input identity and observed result; any flip is not necessarily desired-target success. |
| Limits/status | No successful edit was found in the stated attempts, or a property was not assessed. | Actual attempt counts/status; “not found” must not become “does not exist.” |
| Input observation | A quoted phrase or input value is present. | Exact span/value; mere presence does not establish decision influence. |

Runtime and technical metadata can be shown in evidence panels without crowding novice prose. Probabilities, logits and attribution values must be labelled as their actual quantities. None may be relabelled as calibrated confidence without justification.

## 5. The proposed preservation procedure

### Stage A — Freeze decision and build the evidence record

Run the target predictor and bind E to that run. Extract supported evidence using methods compatible with actual access. If signed attribution is unavailable, use appropriately qualified magnitude evidence or omit directional claims. Record invalid outputs and failed evidence extraction; do not manufacture scores.

Generate/test concrete counterfactual candidates under a bounded, logged budget. Independently classify edited inputs with the same target task definition. Report both desired-target success and any flip. A semantic-quality check is distinct from the target's output; successful label change does not establish actionability or logical feasibility.

### Stage B — Set the common claim plan before audience rendering

Choose P from E before generating either audience version. For the initial study, both versions must express the same essential facts: the decision, the selected supported evidence, an available tested outcome or explicit search-failure status, and the required uncertainty/limitation statements. The exact evidence-selection policy and claim count are fixed in Step 4 using development data.

Missing evidence generates an explicit status obligation rather than an invented explanation. Step 4 must specify a nontrivial minimum evidence requirement before testing; an empty or status-only record cannot count as a successful informative narrative merely because its boilerplate is correct. Keep such requests in the coverage denominator and report evidence-availability strata. If attribution is optional in a feasibility variant, report that variant separately; do not imply all evidence types were evaluated.

For the paired comparison, expert-only new factual claims are excluded from the narrative. Technical expansion can occur in separately labelled evidence panels. This keeps content differences from being mistaken for style effects. A later richer expert narrative would require a separate evaluation.

### Stage C — Render audience variants

The communication LLM receives E, P and an audience instruction. It returns sentences with claim-ID links. Novice text uses plain language; expert text can name the method and output quantity. Both preserve essential content and qualifiers. Style instructions must not authorize stronger causal, confidence or real-world outcome claims.

Generated links are hints, not trusted evidence. A sentence citing a valid claim ID can still contain a contradiction or extra unsupported clause. Inspect the whole final narrative, including unlinked clauses. An explanation that merely repeats a keyword fails if it changes the claim's meaning.

### Stage D — Check final text against obligations

Use structural checks for identities, labels, units, numeric values and evidence availability. Use a semantic extraction/checking component for paraphrases, negation, scope, asserted relationships and omitted limitations. Evaluate that component on development diagnostics before fixing it; no particular parser, judge or entailment model is selected here.

For each final claim, retain a status: supported, contradicted, unsupported or unresolved. “Unsupported” means E does not justify the claim, not necessarily that it is false in the world. Unresolved extraction/checking must not be counted as verified. Detect missing mandatory claims separately from added claims.

The pass condition requires all essential obligations to be expressed and no detected unsupported/contradicted/unresolved assertion in the narrative. This is a checker decision with measurable false acceptance/rejection. The application label should say “passed specified evidence checks,” not “proved faithful.”

### Stage E — Bounded repair and release

Allow at most **one joint repair round** for a failed pair, using failed claim IDs and diagnostic reasons. Reparse and check the entire repaired output, not only the changed sentence. Repair may change explanations but not E, P or the target decision. Count every generation, extraction and checking call.

In the paired research condition, release the pair only if both views satisfy the checks. Otherwise record a failure and offer a clearly labelled deterministic evidence summary. This fallback keeps the application useful, but does not count as successful LLM-rendered output. Report fallback coverage and narrative coverage separately.

One repair round is the proposed bounded method setting, not an empirically optimal choice. Step 4 will document its resource implications and comparator budgets before test runs.

### Why there is no extra “consistency guarantee” module

If both explanations perfectly express the same complete semantic obligations, consistency on those obligations already follows. A separate pairwise checker adds no new logical guarantee. Cross-view metrics are diagnostic of imperfect rendering/checking; do not market a redundant check as an additional novel mechanism. Hashes and structured plans likewise cannot guarantee correctness of arbitrary natural-language extraction.

## 6. Worked example — synthetic, not a result

Assume an invented diagnostic fixture records decision A. An exact edited input was tested and also produced A, while the requested target was B. A separate attribution item contains only an unsigned importance magnitude.

Supported: “The model returned A. The record gives an unsigned attribution value for this phrase under the selected method. The tested edit did not reach B.”

Contradicted: “The tested edit produced B.” Unsupported: “This phrase increased the probability of A,” because unsigned magnitude does not establish direction. Unsupported: “No possible edit can produce B,” because one failed test cannot establish impossibility.

A novice rewrite can simplify vocabulary, but must preserve these distinctions. A fluent sentence containing the correct phrase name is insufficient if it reverses the observed outcome. These examples illustrate the proposed contract; they are not model outputs, dataset cases or evidence of checker performance.

## 7. Research questions and hypotheses

| ID | Question / hypothesis | Main comparison and outcome |
| --- | --- | --- |
| RQ1 / H1, primary | Does the full procedure improve complete supported pair yield over grounded audience prompting without final checks? H1 predicts a positive paired difference. | Same source inputs/decisions/evidence/obligations; independent evaluation of both final texts; abstentions and fallbacks count as failures of narrative yield. |
| RQ2 / H2, secondary | Does typed evidence checking accept fewer controlled unsupported/contradictory variants than a general evidence-aware LLM critic? H2 predicts lower false acceptance at a development-fixed acceptance target for supported variants. | Held-out diagnostic cases, including valid paraphrases and changed negation/scope/units/target labels; report both error types and acceptance coverage. |
| RQ3 / H3, secondary | Does one repair round improve supported pair yield relative to the same procedure without repair? H3 predicts positive yield gain, with additional measured cost. | Paired cases and initial outputs; failures retained; latency/calls and raw/final output quality reported. |
| RQ4, conditional human study | Do audience variants improve actual understanding or appropriate use relative to evidence templates? | Actual participant outcomes under an applicable approved protocol. No direction or superiority claim assumed; unavailable studies remain pending. |

H1 is the primary confirmatory target. H2/H3 are secondary; treatment of multiplicity and intervals belongs in Step 4. H2's acceptance target is chosen before test evaluation from development constraints, not adjusted until a preferred result appears. If a comparator cannot reach that target, report the trade-off rather than claiming a matched comparison.

No numerical improvement, sample size, significance threshold or human-study outcome is assumed. A failed hypothesis is a legitimate result and must not be rewritten as a success after seeing outcomes.

## 8. Evaluation definitions and denominators

**Complete supported pair yield:** number of requested source cases whose two released LLM narratives each express every mandatory claim with required scope, and contain no independently identified unsupported or contradictory assertion, divided by all requested source cases. Missing, rejected, unparsable and fallback cases remain in the denominator.

Support is judged against E. An input with an incorrect target prediction can still satisfy this preservation endpoint; report target task correctness and results stratified by correct/incorrect predictions separately. No claim of real-world correctness follows from a supported pair.

**Checker false acceptance:** proportion of independently labelled unsupported/contradictory diagnostic variants that the checker passes. **False rejection:** proportion of independently supported diagnostic variants it blocks. Mandatory-claim omission is recorded separately. Controlled faults have known construction labels only for the defined changes; they are not universal natural-error ground truth.

**Natural-output audit:** independently annotate or adjudicate a defined held-out subset, with annotators blinded to condition where feasible. Do not use the same checker as sole evaluator of its own success. An LLM judge, even a different model, is not enough to establish human understanding or unquestionable semantic truth. If human annotation cannot be obtained, label resulting natural-output measures as automated estimates and restrict claims.

**Cross-view drift:** disagreement, omission or strengthening of a shared claim across the two views, evaluated on all produced pairs as well as released pairs. Rejecting difficult outputs must not hide initial drift. Also report supported required-claim recall and added-claim error separately; raw verbosity should not make a method look better.

**Cost and coverage:** report generation, repair, extraction/checking and counterfactual calls; wall time and available resource measurements; narrative release rate; fallback rate; and coverage/error trade-offs. Do not present 100% validity after filtering as unconditional success.

Use source inputs as the main experimental units. Multiple audience views, candidate edits and mutations from one input are correlated. Split by source and derived variants before development/testing, aggregate within source or use clustered uncertainty estimates, and avoid treating each paraphrase as an independent sample. Exact estimators and sample counts follow in Step 4.

## 9. Baselines and ablations

| Condition | What it tests | Fairness / interpretation |
| --- | --- | --- |
| B0: unverified self-explanation | Initial explanation behavior. | Same target decisions; separately report absence of supplied evidence. |
| B1: grounded audience prompting | Effect beyond supplying E and P. | Same model, claim plan, audience prompts and content budget; no final gate. |
| B2: attribution-feedback refinement | Strong prior method family informed by SR-NLE. | Fixed-decision adaptation explicitly labelled; comparable repair/generation budget; random-word controls where relevant. |
| B3: general evidence-aware critic | Typed checking versus generic checking/repair. | Same evidence, obligations and allowed repair count; count all judging calls. |
| B4: deterministic audience templates | Whether LLM rewriting is needed at all. | Same facts/qualifiers; credible plain/expert templates; report minimal cost and actual human outcomes when available. |
| Proposed procedure | Joint preservation, final checking and bounded repair. | Independent evaluation; all requested cases retained. |

Templates are a necessary strong baseline. If they preserve facts and serve users as well at lower cost, prefer them operationally and report that result. The thesis's decision LLM can remain unchanged; an LLM renderer is not justified merely by its presence in the prototype.

Ablate final checks, shared mandatory-claim obligations, provenance/scope binding and repair. Give each ablation a defined intervention and reason; do not disable several components simultaneously and attribute the difference to one. Provenance mismatch can be tested through controlled stale/wrong-class records but must be reported separately from normal generation.

FaithLM, Serum, Explanation-Refiner and group-specific steering remain nearest related methods. Exact reproduction is not promised. Step 4 will choose feasible direct comparators, document adaptations and explain task/access mismatches. Do not substitute a weakened implementation and claim to outperform the original published method.

## 10. Diagnostic case families

Use paired supported/changed variants where possible: decision-label substitution; negation reversal; wrong attribution class; unsupported signed direction; swapped score units; wrong edited-input identity; any-flip described as desired-target success; specific observed edit generalized to all edits; dropped uncertainty; incorrect input/model binding; unsupported extra clause despite correct claim links; and omitted mandatory facts.

Include positive controls: correct synonyms, sentence reordering, harmless simplification, valid numeric formatting and explicit failed-search statements. Avoid a benchmark containing only obviously bad text. Fault locations and surface styles should vary; otherwise a detector can learn formatting cues. Keep controlled faults and naturally generated errors as separate result groups.

Concrete case fixtures supplied with this step are invented examples for specification only. They are not evaluation data, measured results or a substitute for a held-out diagnostic benchmark.

## 11. Feasibility and Review 2 boundary

The core target is one well-defined classification-based support task, two audience styles, a feasible decision LLM, a bounded evidence pipeline and an inspectable prototype. Dataset, specific models, explainer, thresholds, participants and sample sizes are not selected in Step 3. Step 4 must inspect actual compute, access, licences and available time before committing.

Avoid training a foundation model, a many-domain product or multiple expensive mechanisms merely to enlarge the project. Attribution/score access must match the target; if unavailable, change the evidence method transparently instead of explaining a different model. Properly labelled partial evidence is better than a fabricated signed attribution.

For Review 2 on 18–20 November 2026, aim for a reproducible pilot, meaningful baseline comparisons, failure examples, methodology, IEEE manuscript draft and a Phase I report available at the review. Report statistical uncertainty and limited generalization. Larger validation, broader models and an incomplete human study can be Phase II work with explicit status. No fixed completion percentage is inferred from the rubric.

## 12. Decisions frozen for Step 4 and open choices

**Selected:** preservation of fixed-decision evidence across two audience views; a common essential claim plan; final prose checking; bounded single repair; coverage-sensitive evaluation; templates and a generic critic as strong controls; independent diagnostics; explicit separation from internal faithfulness and task correctness.

**Open:** task/domain and data; target and communication models; attribution method and output quantity; claim extractor and checker; evidence-selection policy; exact generation/candidate budgets; experimental size and uncertainty estimates; participant/annotation arrangements; and appropriate venue. These are substantive Step 4 choices, not hidden assumptions.

**Step 3 completion:** contribution candidate, mechanism, research questions/hypotheses, novelty comparison, failure criteria and scope are concrete enough to design experiments. Originality is a bounded working proposition, not established by naming the method. Step 4 should reject infeasible settings and refine the protocol before any final test results are collected.

## 13. Source locators for the main distinctions

- [L02] Randl et al.: PDF pp.10–11,16–20,35; dependability, counterfactual reclassification and bounded search.
- [L21] CC-SHAP: §§4.1,5.2 and Limitations; output consistency, probability access and computational cost.
- [L25] Cross-Refine: §§3.1–3.2,6; Limitations p.9; target correction and perceived faithfulness.
- [L30] SR-NLE: §§3.3,4.3; Appendix F.6/Table12; magnitude feedback, intervention-word proxy and random controls.
- [L34] Group-specific steering: §§4–6, Table2; Appendix B.4; atomic-fact checks and mixed human outcomes.
- [L35] FaithLM: §§3.1–3.3; Algorithms1–2; theorem assumptions and contrary-hint refinement.
- [L36] Faithfulness Serum: §3; Appendices B,C,F; final hint-reliance checks and resource assumptions.
- [L41] Explanation-Refiner: §§2–4 and Limitations; formal proof support versus target-model computation.
- [L43] Truth or Twist: §1 footnote2,§4.5,Appendix D/Figure10; semantic CDA validity versus fixed-model behavioral validity.

Exact titles and primary URLs are provided in NEAREST_METHOD_COMPARISON.csv, linked to the Step 2 library. No new literature search or experimental result is represented as completed in this step.
