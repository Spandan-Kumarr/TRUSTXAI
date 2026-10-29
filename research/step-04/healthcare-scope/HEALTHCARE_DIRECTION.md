# Healthcare direction — scope recommendation, not a completed protocol

27 October 2026. User requested a healthcare dataset and asked whether GPT versus Gemini versus TRUSTXAI is an easier comparison. The running SMS feasibility pilot was stopped immediately; completed numeric results and private traces are preserved. No healthcare dataset or model benchmark has been run. No development/test SMS prediction was made. Do not execute the prepared SMS finalization script or describe SMS Step4as complete.

## Recommended task

Use PubMedQA expert-labelled PQA-L as the first healthcare feasibility candidate: answer a biomedical research question with yes/no/maybe using its supplied abstract context. This is offline biomedical research question answering. It does not establish suitability for diagnosing patients or clinical deployment. The approved broad thesis title can remain; the task specification, evidence interventions, three-class classifier, resource gates, split protocol and application labels must be revised explicitly.

The original paper describes1,000expert-annotated instances,61,200unlabelled and211,300artificial instances. Those are paper-described counts, not independently parsed downloads. Each instance contains a question, abstract context without the conclusion, long answer/conclusion, and a yes/no/maybe answer. Only question and allowed context are inference inputs. Keep long_answer, final_decision, reviewer labels and any equivalent answer-containing fields out of model prompts and evidence premises. They are evaluation targets, not evidence available to the system.

The official repository supplies an MIT LICENSE. Preserve it and dataset/paper attribution, and verify the downloaded release and terms for underlying PubMed abstract text before redistribution. Repository licensing alone is not a finding that every underlying article's text is unrestricted. Prefer retrieval instructions and source IDs/hashes in the public project.

## Fair model/framework comparison

TRUSTXAI is a framework, whereas GPT/Gemini are underlying model families. Primary framework comparisons pair each fixed model with a grounded-prompt baseline and with TRUSTXAI using the same model version, task inputs and recorded decision. A local open-weight model can be another backbone if healthcare-specific feasibility passes. Record actual API model IDs, dates, supported settings, cost and failures; no GPT/Gemini API access or inference is currently verified.

Evaluate task accuracy/macro-F1 across backbones separately from evidence support, complete supported explanation yield, unsupported claims, abstention/fallback coverage and cost. With a frozen decision the explanation framework does not itself change task accuracy. Do not use a model's self-judgment as independent semantic ground truth. Clinical correctness and causal/medical validity of edited abstracts require separate treatment; successful model-label flips do not establish realistic medical interventions.

Public benchmark contamination remains possible; established healthcare data and a leaderboard comparison do not by themselves establish a novel contribution. The research question remains whether explicit typed evidence and checking/repair preserve supported content across audience explanations better than matched grounded prompting and other declared baselines.

## Next Step4revision

Verify primary release/revision/terms and actual fields/counts; exclude answer leakage; establish a source/article-level development/test split using the official split where suitable; choose context-length and evidence intervention budgets before outcome inspection; test only a separate healthcare feasibility pool; verify API availability or use local models first; amend compute projections and freeze the final protocol after development. Existing SMS feasibility scores do not transfer to healthcare and do not prove healthcare readiness. Independent semantic annotation and the optional understanding study remain unperformed.

## Sources checked

- Original PubMedQA paper, EMNLP-IJCNLP2019: https://aclanthology.org/D19-1259/ (abstract retrieved).
- Official code/data repository: https://github.com/pubmedqa/pubmedqa (README and MIT LICENSE retrieved).
- MedQA official repository: https://github.com/jind11/MedQA (README retrieved; exam-style alternative, not selected).
- MedMCQA publisher dataset card: https://huggingface.co/datasets/openlifescienceai/medmcqa (card retrieved, declares Apache2.0; exam-style alternative, not selected).

The PubMedQA project homepage route returned proxy403. The paper and official GitHub sources were accessible; no additional permission is needed for this recommendation. Do not treat the blocked homepage as evidence that dataset files are inaccessible. No leaderboard submission, email or other external message has been sent.
