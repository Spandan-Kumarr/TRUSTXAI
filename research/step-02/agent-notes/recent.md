# Recent nearest-method and novelty audit

Search date: 26 October 2026. Six close 2025–2026 studies verified using official ACL Anthology XML metadata/abstracts and author/organization repository READMEs. **No full paper text was retrieved for these six studies.** Numerical claims in abstracts/READMEs are author reports, not reproduced evidence. Network restrictions prevented direct ACL/arXiv full-text retrieval.

## Main conclusion

A new interface combining LLM decisions, XAI evidence, an explanation critic, iterative refinement and a counterfactual checker is insufficient for a novelty claim. At least SR-NLE, Cross-Refine, Faithful Serum and FaithLM are direct method-level predecessors. A viable contribution must define a narrower, independently testable mechanism and compare to the nearest methods rather than only an unverified self-explanation baseline.

## 1. Self-Critique and Refinement for Faithful Natural Language Explanations

- Authors: Yingming Wang, Pepa Atanasova.
- Publication metadata: Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing (2025); DOI 10.18653/v1/2025.emnlp-main.427.
- Sources: https://aclanthology.org/2025.emnlp-main.427/ and https://github.com/ymwangv/SR-NLE; raw evidence https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2025.emnlp.xml and https://raw.githubusercontent.com/ymwangv/SR-NLE/master/README.md.
- Access depth: Official abstract + author repository README (not full text).
- Contribution: SR-NLE iteratively critiques and refines post-hoc natural-language explanations, including feedback derived from feature attribution; no additional training is required in the reported method.
- Limits/cautions: Only official abstract and author README inspected. Self-feedback is not independent ground truth. Exact tested attribution-feedback procedures, intervention assumptions and reported results need full-text scrutiny; no audience-preservation protocol established by these inspected sources.
- Thesis implication: Direct prior art against claiming iterative explanation verification/refinement or attribution-guided correction as novel.
- Comparison use: Strong candidate baseline for attribution-feedback refinement; source pipeline includes answer, explanation, feedback and refinement runners.

## 2. Cross-Refine: Improving Natural Language Explanation Generation by Learning in Tandem

- Authors: Qianli Wang, Tatiana Anikina, Nils Feldhus, Simon Ostermann, Sebastian Möller, Vera Schmitt.
- Publication metadata: Proceedings of the 31st International Conference on Computational Linguistics (2025); DOI not supplied in XML record.
- Sources: https://aclanthology.org/2025.coling-main.77/ and https://github.com/qiaw99/Cross-Refine; raw evidence https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2025.coling.xml and https://raw.githubusercontent.com/qiaw99/Cross-Refine/main/README.md.
- Access depth: Official abstract + author repository README (not full text).
- Contribution: Uses two LLM roles, generator and critic, to assess, give feedback/suggested explanation and refine an initial NLE without supervised training.
- Limits/cautions: Abstract/README access only. LLM critique and human preference do not certify target-model faithfulness. Exact evaluation constructs and leakage controls require full text.
- Thesis implication: Direct prior art against novelty of a separate explanation critic or two-model generation-and-checking architecture.
- Comparison use: Candidate explanation-refinement baseline; compare fairly against its Self-Refine comparator and control call budget.

## 3. Multi-Level Explanations for Generative Language Models

- Authors: Lucas Monteiro Paes, Dennis Wei, Hyo Jin Do, Hendrik Strobelt, Ronny Luss, Amit Dhurandhar, Manish Nagireddy, Karthikeyan Natesan Ramamurthy, Prasanna Sattigeri, Werner Geyer, Soumya Ghosh.
- Publication metadata: Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers) (2025); DOI 10.18653/v1/2025.acl-long.1553.
- Sources: https://aclanthology.org/2025.acl-long.1553/ and https://github.com/IBM/ICX360; raw evidence https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2025.acl.xml and https://raw.githubusercontent.com/IBM/ICX360/main/README.md.
- Access depth: Official abstract + author repository README (not full text).
- Contribution: MExGen extends perturbation-based attribution such as LIME/SHAP to costly, long-context text generation; scores context parts for influence on outputs and reports automated plus human evaluation.
- Limits/cautions: Official abstract/README only. Context attribution is not proof of internal causal reasoning and is not itself audience-adapted claim validation. Method targets context-grounded generation rather than the same bounded classification task by default.
- Thesis implication: Prior art for model-grounded explanations of LLM outputs and reusable in-context XAI tooling; the application or extending SHAP to text generation alone cannot be new.
- Comparison use: Relevant evidence-extraction comparator or reusable toolkit; ICX360 includes MExGen, CELL contrastive prompts and token highlighter. README states Apache2.0, not independently licence-audited here.

## 4. Faithful Serum: Mitigating the Faithfulness Gap in Textual Explanations of LLM Decisions via Attribution Guidance

- Authors: Bar Alon, Itamar Zimerman, Lior Wolf.
- Publication metadata: Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers) (2026); DOI 10.18653/v1/2026.acl-long.300.
- Sources: https://aclanthology.org/2026.acl-long.300/ and https://github.com/Bar-A-94/FaithfulnessSerum; raw evidence https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2026.acl.xml and https://raw.githubusercontent.com/Bar-A-94/FaithfulnessSerum/main/README.MD.
- Access depth: Official abstract + author repository README (not full text).
- Contribution: Faithful Serum evaluates omitted influential hints using counterfactuals and guides explanations using PE-LRP token-attribution heatmaps injected at attention level; training-free.
- Limits/cautions: Official abstract/README only, not full-text verification. Guidance requires open-model internals; author README notes a narrow intervention-strength range and instability/repetition when too high. Its strong claim of actual-evidence faithfulness must be interpreted within its tests.
- Thesis implication: Very close 2026 prior art for attribution-grounded explanation generation and intervention-based checks; prevents first-ever grounding-plus-verification claim.
- Comparison use: High-priority nearest-method comparator if model/access compatible; otherwise explicit related-work comparison and possibly a reproduced simpler condition.

## 5. FaithLM: Towards Faithful Explanations for Large Language Models

- Authors: Yu-Neng Chuang, Guanchu Wang, Chia-Yuan Chang, Ruixiang Tang, Shaochen Zhong, Fan Yang, Andrew Wen, Mengnan Du, Xuanting Cai, Vladimir Braverman, Xia Hu.
- Publication metadata: Proceedings of the 19th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers) (2026); DOI 10.18653/v1/2026.eacl-long.177.
- Sources: https://aclanthology.org/2026.eacl-long.177/ and https://github.com/ynchuang/FaithLM; raw evidence https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2026.eacl.xml and https://raw.githubusercontent.com/ynchuang/FaithLM/main/README.md.
- Access depth: Official abstract + author repository README (not full text).
- Contribution: FaithLM formalizes explanation faithfulness via prediction shifts when explanation content is contradicted; uses contrary-hint scoring and iteratively refines elicitation prompts and explanations.
- Limits/cautions: Official abstract plus minimal official README only. Theoretical soundness is an author claim in the abstract, not independently checked. Different intervention semantics from standard input deletion or counterfactual reclassification; cannot treat scores as equivalent.
- Thesis implication: Direct 2026 prior art for model-agnostic behavioral explanation assessment linked to iterative improvement.
- Comparison use: High-priority behavioral verification comparator; full text needed before implementing its contrary-hint score.

## 6. Accountable AI with Grounded, Faithful, Consistent, Actionable Rationales: A Case Study in Clinical Trial Matching with VERDICT

- Authors: Zikai Zhou, Yufei Jin, Yilin Xu, Yu-Chiang Wang, Chieh-Ju Chao, Monica Lam.
- Publication metadata: Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing (2026); DOI not supplied in XML record.
- Sources: https://aclanthology.org/2026.emnlp-main.2598/ and https://github.com/stanford-oval/clinical-trial-matching; raw evidence https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2026.emnlp.xml and https://raw.githubusercontent.com/stanford-oval/clinical-trial-matching/main/README.md.
- Access depth: Official abstract + author repository README (not full text).
- Contribution: VERDICT converts constraints/policies into SMT/MaxSMT and derives eligibility decisions from a solver, exposing assumptions and pivotal conditions that would change outcomes; combines accountable rationale artifacts with a working clinical trial application.
- Limits/cautions: Official abstract and extensive author README only. Solver-based decisions differ from explanations of an unchanged LLM classifier. Clinical resources and data licensing impose scope costs. README-reported benchmark numbers have not been reproduced; no clinical deployment endorsement.
- Thesis implication: Strong prior art for evidence-grounded decision support, audit trails, pivotal/counterfactual conditions and explicit undecided states. Changing the thesis to solver decisions would change Review1 scope.
- Comparison use: Architecture/limitation comparator, not automatically a fair same-task numerical baseline. Abstract metadata lists EMNLP2026; collection ingested 2026-10-21 and month October.

## Additional older direct prior art

**Tell Me a Story! Narrative-Driven XAI with Large Language Models** — David Martens, James Hinns, Camille Dams, Mark Vergouwen and Theodoros Evgeniou. Official repository ADMAntwerp/XAIstories: https://github.com/ADMAntwerp/XAIstories; raw README https://raw.githubusercontent.com/ADMAntwerp/XAIstories/main/README.md. README BibTeX year 2024, arXiv:2309.17057 (initial identifier 2023); exact publication/version metadata not independently resolved. The repository already implements SHAPstories and explicitly supports classifiers with predict_proba such as scikit-learn. Thus translating SHAP into narrative explanations is established prior art; it does not by itself explain an LLM decision model. Access depth: author README only, no full text.

## Date and interpretation notes

The official 2026 EMNLP XML volume reports month October and ingest-date 2026-10-21, so those records were present before the current task date. The repository's VERDICT preprint identifier is 2609.03366. Do not infer November scheduling merely from historical EMNLP dates.

A narrower candidate question worth later investigation is whether a claim-level evidence contract can survive audience transformations, with risk/coverage-aware rejection and independent adversarial tests. This is **not verified novel**: claim checking, attribution guidance, refinement, explicit undecided states and audit trails each have prior art. A full-text comparison is needed before selecting it.
