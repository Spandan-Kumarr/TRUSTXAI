# Counterfactual and evaluation literature audit

Search date: 26 October 2026. Read-only research; no implementation or experiments were run.

## Access and source limits

The supplied Randl paper was available in full. For the other nine included records, evidence was official ACL Anthology XML (abstract/metadata where present), author-maintained README files, and selected code. These access depths are recorded per paper. Full papers have not been retrieved for these nine, so claims about exhaustive limitations, performance or applicability require later full-text verification. Academic hosts are blocked by the current proxy; official GitHub records were read directly, not via proxy-bypass services. GitHub search returned429 and was not repeatedly retried. Author-site PDF guesses returned404 and do not establish paper unavailability elsewhere.

## Strongest implications

1. **Generation → target-model reclassification → bounded retries is already in Randl et al.** Its movie-CF source explicitly records prediction, target probability, similarity and time for candidates and stops after bounded attempts. Simply adding that loop is not novelty.
2. **Minimality search with target prediction checks predates instruction LLMs.** MiCE (Findings ACL2021) provides candidate generation, target-predictor scoring, beam search and successful contrast edits. Polyjuice (ACL2021) provides controlled perturbations.
3. **Joint rationale + counterfactual modeling is established.** CREST (ACL2023) jointly trains selective rationalization and counterfactual generation, with rationale plausibility and counterfactual/simulation evaluation. The thesis must explain how fixed-target LLM checking differs from these training-oriented systems.
4. **LLM generate-and-filter pipelines are established.** DISCO (ACL2023) uses LLM perturbations and teacher filtering for NLI data augmentation. Teacher agreement does not establish validity for a different target model.
5. **A close 2025 paper exposes the validity–minimality trade-off.** Mayne et al., EMNLP2025, 'LLMs Don’t Know Their Own Decision Boundaries' evaluates SCEs. The README specifically describes tabular binary tasks, not unrestricted text. Text trials should still measure both valid label change and edit magnitude; high validity alone is inadequate.
6. **Evaluation must distinguish rationale agreement from behavioral evidence.** ERASER provides human annotations and comprehensiveness/sufficiency metrics. CheckList provides minimum functionality, invariance and directional tests; perturbations are not all supposed to preserve predictions.

## Reporting requirements implied by the prior art

- Keep every input and failed attempt in denominators: total coverage, candidate acceptance rate, success per example, attempts/model calls and latency. A validity filter trivially makes accepted examples valid under its own check; evaluate at dataset level and use independent/repeated checks where relevant.
- Report edit magnitude/minimality proxies separately from semantic adequacy, fluency, validity and actionability. Token similarity is not a proof that all non-target information was preserved.
- Reclassify with the actual decision model. Explain any different generator, editor, judge or teacher; do not silently replace the target classifier.
- Record prompt/model/settings and evaluate validity under repeated classification or prompt variation if stability is claimed. Finite retry formulas rely on assumptions and cannot promise unconditional100% validity.
- For generative classifiers, define label probability/tokenization carefully; do not call arbitrary output score a calibrated probability.
- Distinguish benchmark-label correctness from validity relative to an erroneous model decision. A valid edit can merely expose an undesirable model shortcut.
- Reusing benchmark rationales or counterfactual data requires checking provenance, splits and licences. Repository code licences do not automatically license all included source texts.

## Candidate opportunity, not a novelty conclusion

A carefully specified post-generation claim-preservation check across audience views, with explicit abstention/coverage and stable target-model counterfactual tests, could be investigated. It is not established as unique by this thematic audit, and its nearest audience-grounding/verification literature must be checked by the other tracks. Contribution would require a precise algorithm or measurable evaluation advance rather than integration alone.

## Additional screened item

Tailor: Generating and Perturbing Text with Semantic Controls (Ross, Wu, Peng, Peters, Gardner; ACL2022, DOI10.18653/v1/2022.acl-long.228) was verified from ACL XML and https://github.com/allenai/tailor README. It offers semantically controlled perturbations, useful as a robustness generator, but was left outside the initial main eight to keep focus. It is not the different ACL2023 paper also called Tailor.

The ACL2026 record2026.emnlp-main.645, 'Cited but Not Causal: A Counterfactual Audit of Refusal Explanations in Aligned Language Models', describes necessity/sufficiency interventions on cited refusal features. Metadata says October2026 and has no DOI; full text, authoritative publication timing and release have not been checked. Treat as a current candidate needing verification rather than established full-text evidence.

## Reproducibility

Machine-readable per-paper records: counterfactuals.json. Fetched evidence snapshots are in ../evidence/counterfactuals/. Metadata uses official XML from /workspace/thesis-reference/literature-cache; Polyjuice/MiCE exact records were also checked against directly fetched2021.acl.xml and2021.findings.xml. All snapshots have SHA256 entries in the evidence manifest. READMEs can be incomplete or differ from final papers; exact paper versions must be reconciled before manuscript citation.

## Added nearest competitors from Findings collections

**FitCF: A Framework for Automatic Feature Importance-guided Counterfactual Example Generation** (Wang et al., Findings ACL2025, DOI10.18653/v1/2025.findings-acl.64, pp.1176–1191) is especially important. The official abstract explicitly describes ZeroCF attribution-important-word guidance, label-flip verification and using verified counterfactuals as few-shot demonstrations. This rules out calling attribution-guided generation plus label flipping a new contribution. Full paper/code were not retrieved; the record is abstract-only.

**iFlip: Iterative Feedback-driven Counterfactual Example** (Wang, Wang, Feldhus, official record labelled Findings EMNLP2026, October, pp.749–779; no DOI in accessed metadata) describes iterative refinement using model confidence, attribution and natural-language feedback, plus early stopping. It is a direct candidate competitor to feedback-guided counterfactual repair. Full text, exact release/publication timing, code and licence need verification; reported abstract performance numbers are not adopted as checked experimental evidence here.

There are now ten main machine-readable records, with exact official author/venue/page metadata filled where available. These last two records are abstract-only; all other depths remain as stated.
