# Healthcare method amendment to Step3

27October2026. User authorised healthcare scope and local-only execution after confirming no API access/budget. The approved broad thesis title and evidence-preserving audience-transformation research question remain. The SMS task, its classifier, splits and feasibility scores are superseded for the active study.

## Task and decision

Use PubMedQA PQA-L question plus provided abstract context to predict yes/no/maybe. The application supports offline biomedical literature auditing. It does not diagnose a person or propose treatment. A source case is a PMID/article, not an individual patient. Dataset answer labels measure agreement with benchmark annotations; they are not an independent clinical safety assessment.

Inference inputs are projected explicitly to QUESTION and CONTEXTS. Omit LONG_ANSWER, final_decision, both stored model-prediction fields, metadata and source heading labels. The gold label is available only to sampling/evaluation code. A leakage sentinel check verifies the projection. Original context text is preserved without truncation, within the declared token/section budgets.

## Evidence contract

For API portability, primary behavior evidence consists of categorical same-target responses to controlled input omissions. It does not depend on access to hidden states or token log probabilities. Each CONTEXTS entry has a stable S1,S2,... identifier. Omit each entry separately, keep the question, other entries, IDs, model and prompt fixed, and classify the modified input. Preserve invalid outputs and all attempted tests.

An answer-changing omission is a bounded input counterfactual in the operational classifier sense. It is not a realistic change to a patient, a clinical intervention, a meaning-preserving rewrite or an internal causal explanation. The supplied entries are abstract context units, often sections; do not call them individual sentences or SHAP features.

Among valid answer-changing omissions select the shortest removed entry by characters, with earliest original index as tie-break. If no answer changes, choose the shortest valid nonchanging omission with the same tie-break. Independently repeat the selected target query uncached. Record all-label transition counts, any-label flip count and invalid-output counts. No unique opposite class exists in this three-class task. Do not import the binary SMS desired-label metric unchanged.

Minimum informative evidence requires a valid original answer, at least one valid omission result and an agreeing selected-result recheck. Other cases stay in the all-requested-source denominator. No-flip evidence remains informative, but it does not prove global robustness. No synthetic medical edit is generated in this primary experiment.

## Common four-claim plan

C1: exact frozen target answer, bound to the displayed question/input hash, with its model-status qualification.

C2: exact selected omitted-unit ID and observed original/omitted answers, including whether the answer changed. If unavailable, give explicit unresolved status.

C3: bounded search coverage: attempted omissions, valid outputs, answer changes and selected-result recheck status. Do not generalize to untested edits.

C4: input-omission evidence does not establish clinical causation, every possible outcome or complete internal reasoning.

Both novice and technical-reviewer views express all four facts; style is the audience transformation. Question and original context are displayed separately so generated prose need not restate clinical claims. This deliberately studies preservation of recorded behavioral audit evidence. It does not, by itself, establish that the model's biomedical answer or underlying clinical reasoning is correct.

The Step3 typed provenance, shared plan, complete final-text checks, one repair, labelled deterministic fallback and independent complete-supported-pair endpoint remain. Claim links are not proof. NLI is a fallible checker; the existing four synthetic smoke examples do not validate biomedical inference or audience-equivalence accuracy. Changed diagnostic faults must target labels, section identity, observed transitions, search counts, scope, unsupported clauses and omitted limitations.

The earlier attribution-word refinement baseline is replaced with an explicitly adapted omission-unit feedback baseline. It is not a faithful SR-NLE reproduction. Before claiming a contribution over biomedical explanation methods, extend the bounded literature review and audit the closest methods. The healthcare setting and context omission are established ideas, not a novelty claim.

## Model comparison

The authorised run is local-only. The first available candidate is pinned Qwen3-1.7B; healthcare suitability must be measured independently. The primary framework comparison pairs the same fixed backbone with a grounded blind-second-draft baseline and with TRUSTXAI. Other declared baselines and templates are secondary controls. Task accuracy is a backbone metric; a framework that explains a frozen answer does not change that answer.

GPT/Gemini remain a future conditional extension, with actual API availability, exact versions, common decoding protocol, cost and repeated-query behavior verified before inclusion. There are currently no GPT/Gemini outputs or results. A local-only pilot cannot establish cross-provider generalization.
