# Audience-adaptive and conversational explanation literature

Search date: 26 October 2026. This is a focused component of Step 2, not an independent systematic review. Structured records are in `human_adaptation.json`; source snapshots and SHA-256 provenance are in `../evidence/human-adaptation/`.

## Access and verification boundary

Academic websites are blocked by the running proxy policy. Read-only fetches of actual authors' GitHub repositories and the official ACL Anthology GitHub metadata repository work. No URL proxy services or access-control workarounds were used. Six older systems/studies, the supplied base paper, and one October 2026 adaptation paper were inspected at the depths stated below. Public repository availability is not evidence of peer review; official ACL records were used where available. No application or published experiment has been reproduced by this subtask.

- Full paper read: supplied Bello et al. base paper, especially sections 3–5.
- Official ACL abstract + metadata and official README: InterroLang, Explanation Utility, Reframing Human-AI Collaboration, Attribute-Based Activation Steering.
- Official README including abstract/citation: TalkToModel.
- Official README/citation only: XAIstories and ConvXAI.

A property not discussed in a README cannot be declared absent from the corresponding paper. A full-text follow-up remains necessary before making a definitive nearest-prior-art exclusion or inheriting any user-study protocol.

## Core studies and their implications

| ID | Study | Evidence and relevance |
| --- | --- | --- |
| H01 | Bello et al., Three-level Framework, Information Systems Frontiers, publication-year metadata pending | Supplied PDF explicitly acknowledges further empirical validation is needed. Audience-aware LLM-mediated communication on algorithmic evidence is already proposed. |
| H02 | Slack, Krishna, Lakkaraju and Singh, TalkToModel, Nature Machine Intelligence, 2023; DOI 10.1038/s42256-023-00692-8 | Official README describes dialogue interpretation, execution of technical explanations and a conversation UI. It explicitly limits the system to tabular target models. Reported preference/usability percentages must not be presented as calibrated-trust evidence. |
| H03 | Feldhus et al., InterroLang, Findings EMNLP 2023, pp. 5399–5421; DOI 10.18653/v1/2023.findings-emnlp.359 | Official abstract describes two user studies, including simulatability: users predict a hidden model label from explanations. Dialogue helped relative to one-off explanations in their study. Implementation already integrates NLP attributions, counterfactuals, rationalization and exploration. |
| H04 | Martens, Hinns, Dams, Vergouwen and Evgeniou, Tell Me a Story! Narrative-Driven XAI with Large Language Models, README preprint citation 2024; arXiv:2309.17057 | Official code generates SHAPstories for models exposing `predict_proba`. Narrative SHAP translation is established prior art. Peer-reviewed publication metadata and full paper not verified. |
| H05 | Shen, Huang, Wu and Huang, ConvXAI, CSCW 2023 Demo; arXiv:2305.09770 | Official research README documents conversation, heterogeneous XAI, examples and MiCE counterfactuals for scientific-writing support. Conversationally selecting several explanation methods is not novel. Do not mislabel a demo as a verified main-paper publication. |
| H06 | Hashemi Chaleshtori et al., On Evaluating Explanation Utility for Human-AI Decision Making in NLP, Findings EMNLP 2024, pp. 7456–7504; DOI 10.18653/v1/2024.findings-emnlp.439 | Official abstract reviews metrics and dataset selection; reports that only 4 of over 50 candidate datasets meet their application-grounded criteria. In their contract legal-claim task, AI predictions with or without explanations did not speed decisions without compromising performance. This is task-specific, not proof all explanations are useless. |
| H07 | Wiegreffe, Hessel, Swayamdipta, Riedl and Choi, Reframing Human-AI Collaboration for Generating Free-Text Explanations, NAACL 2022, pp. 632–658; DOI 10.18653/v1/2022.naacl-main.47 | Official abstract already combines GPT-3 generation with a supervised human-acceptability filter. A generic generate-then-filter procedure is not new. Human preference/acceptability does not establish faithfulness. |
| H08 | Fichtel, Prange and Wachsmuth, Attribute-Based Activation Steering of LLMs for Group-Specific Explanation Generation, EMNLP 2026, pp. 2929–2959 | Official October 2026 abstract and code identify group knowledge/style attributes, apply activation steering, assess specificity/factuality, and include human experts. Audience tailoring with factuality evaluation is current prior art. The target is explanatory topic content, not necessarily a classifier decision's model-grounded evidence. |

## Closest originality threats

1. **A conversational XAI application is not itself a research gap.** TalkToModel and InterroLang already have natural-language interaction with executable explanations. InterroLang is particularly close to a text classification application because it combines attributions, perturbations/counterfactuals and free-text rationales.
2. **SHAP-to-LLM narratives are not a contribution by themselves.** XAIstories already provides code. The exact model interface and whether it can wrap a generative classifier must be assessed rather than replacing the target LLM with a different classifier for convenience.
3. **Generating candidate explanations and filtering them is established.** Reframing Human-AI Collaboration uses a human-acceptability-trained filter; novelty would need a precise difference in the claims checked, evidence used, guarantees claimed and empirical evaluation.
4. **Audience adaptation is more mature than the two base papers alone suggest.** The October 2026 activation-steering paper has target-group attributes, specificity/factuality measures, prompting/steering comparisons and expert evaluation. Merely adding novice/expert prompt labels will not establish originality.
5. **Human-centered usefulness must be measured, not asserted.** InterroLang's simulatability and Explanation Utility's task/team criteria are different evaluation constructs. Both are more informative than asking only whether users like a narrative.

## Promising narrower research question, not verified novelty

Investigate whether a defined, auditable model-evidence record can preserve decision-relevant factual claims and limitations across audience transformations, while separately measuring target-model behavioral probes, counterfactual validation and failure coverage. This differs conceptually from topic factuality, readability or preference, but the broader literature must still be searched for equivalent claim-preservation methods.

A useful experiment would compare the same target-model decision/evidence record across translation-only and audience-adapted conditions, check the final rendered claims, and report both accepted coverage and error rates. A system can appear accurate if it rejects most cases; reliability should therefore be assessed together with coverage, latency and remaining unsupported claims. This is a recommendation for later design, not an implemented method or an experimental finding.

## Human evaluation: constructs that should remain distinct

- **Preference/ease of use:** subjective experience; may increase even when the advice is wrong.
- **Model simulatability:** ability to predict what the model will output, including its mistakes; not necessarily better real task decisions.
- **Task performance:** correctness/time on the actual task with and without assistance; baseline and task suitability matter.
- **Appropriate reliance:** distinguish following correct advice from accepting incorrect advice and appropriately rejecting it. Confidence/satisfaction alone do not measure this.
- **Claim preservation:** whether adaptation retains supported numbers, signs, evidence scope and uncertainty; human clarity alone does not establish it.

The thesis should not infer that explanations improve decision-making just because participants say they are helpful, nor require every benchmark to support a meaningful human-AI team. A human-study pilot must use actual participants under applicable institutional requirements; synthetic respondents and LLM-judged preference do not count as a human study.

## Code and feasibility observations

- TalkToModel: MIT licence checked; older Python 3.9 and CUDA 11.3 setup, CPU path documented. Current target-model scope is tabular.
- InterroLang: code/model documentation is public; root `LICENSE` URL returned 404, so licence remains unverified. Use licence inspection before code reuse, not an assumption of permission from public visibility.
- XAIstories: MIT licence checked; `predict_proba` requirement and external LLM API keys documented.
- ConvXAI: MIT licence checked; Python 3.7, MongoDB, model checkpoints and dependencies make direct reproduction more involved than a small standalone prototype.
- Explanation Utility: MIT licence checked; repository includes task-model development, deferral materials and Qualtrics study-template links.
- Reframing Human-AI Collaboration: Apache 2.0 licence checked; released generation/acceptability data and Mechanical Turk templates.
- Group-specific steering: official code and sample outputs available. README says full generated SQLite database exceeds 100 GB and releases only a subset of Qwen 7B explanations for 600 ELI5 test questions and 97 science questions. This is a storage/reproduction warning from their setup, not a requirement for our proposed application. Licence not yet checked.

None of these applications is automatically a fair end-to-end baseline for an instruction-tuned LLM decision task. Reuse operation categories or evaluate individual methods only after matching the target model, inputs, budget and outcome definitions.

## Non-peer-reviewed software leads, excluded from the core study count

`gak92/LLM-XAI-Malware-Framework` has a README describing a thesis implementation combining XGBoost/LIME/SHAP/local LLMs and analyst/manager/user narratives. It is an accessible example of similar software composition, not a verified published research result. Author identity, date, publication status, quality and licence were not established; do not cite it as peer-reviewed evidence or copy its content. Its existence reinforces why a new UI and multi-audience prompts alone cannot support an unprecedented-system claim.

## Primary URLs

- https://github.com/dylan-slack/TalkToModel
- https://github.com/DFKI-NLP/InterroLang
- https://github.com/ADMAntwerp/XAIstories
- https://github.com/huashen218/convxai
- https://github.com/utahnlp/nlp-explanation-utility-guideline
- https://github.com/allenai/few_shot_explanations
- https://github.com/webis-de/emnlp26-group-specific-explanations
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2023.findings.xml
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2024.findings.xml
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2022.naacl.xml
- https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2026.emnlp.xml
