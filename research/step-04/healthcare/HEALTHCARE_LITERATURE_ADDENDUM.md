# Healthcare literature addendum

27 October 2026. This is a focused extension to the existing bounded Step 2 review, prompted by the healthcare scope change. It is not a systematic search or evidence that the proposed combination has never been attempted. Three healthcare-specific papers were checked from primary full texts; existing nearby records remain relevant. No published experiment was reproduced.

## PubMedQA — the task source

Jin et al. (2019), *PubMedQA: A Dataset for Biomedical Research Question Answering*, EMNLP-IJCNLP, DOI 10.18653/v1/D19-1259. Original paper: https://aclanthology.org/D19-1259/ . Full-text task/data/split descriptions were inspected; official data/code were downloaded separately at an immutable revision.

The task uses a research question and corresponding abstract without its conclusion. The long answer/conclusion and categorical answer are targets, not permissible inference evidence. PQA-L has 1,000 expert-labelled cases; the extra unlabeled/artificial sets are distinct. Existing published accuracy numbers use a different evaluation setup from our 60-case balanced subset. Our data retrieval verified 552 yes, 338 no, 110 maybe and reproduced the upstream 500/500 split. Public benchmark memorization remains possible.

## MedHallu — close prior for medical verification and diagnostics

Pandit et al. (2025), *MedHallu: A Comprehensive Benchmark for Detecting Medical Hallucinations in Large Language Models*, arXiv:2502.14302. Primary full text: https://arxiv.org/abs/2502.14302 . Dataset card: https://huggingface.co/datasets/UTAustin-AIHealth/MedHallu . Methods, implementation, evaluation setting and limitations were inspected in the retrieved 18-page PDF. Final publication status beyond the verified preprint record was not established here.

The benchmark derives 1,000 cases from labelled PubMedQA and 9,000 from artificial PubMedQA. Its four fault categories include question misinterpretation, incomplete information, mechanism/pathway misattribution and fabricated methods/evidence. Candidate hallucinations are produced with a Qwen2.5-14B generator, assessed using multiple LLM discriminators, checked with bidirectional NLI and iteratively improved with GPT-4o-mini-backed TextGrad. The feedback loop aims to generate convincing hard negatives; it is not the same objective as repairing a narrative to preserve supported facts.

Detection is evaluated with and without relevant context. An extra “not sure” response and knowledge provision affect results. Semantic similarity to reference answers, medical hallucination detection, NLI-based checks, feedback loops and explicit uncertainty therefore cannot be claimed as new contributions of TRUSTXAI. Nor is using PubMedQA for a medical error benchmark new.

The generated hallucinations are primarily automatically constructed/filtered. The original PQA-L expert annotation must not be described as expert validation of every new hallucinated answer. The paper's prose and implementation details differ on majority-versus-at-least-one discriminator acceptance, and mention different NLI model families; verify released code before claiming exact reproduction. Its reported hard-category F1 and knowledge gains are not our results.

The proposed distinction to test is preservation of *recorded fixed-target omission evidence* in two audience views, evaluated over all requested cases, with a matched grounded baseline and independent outcome audit. This distinction is a testable scope, not proof of novelty or superiority. MedHallu-like faults can inform diagnostics, but a small custom fixture set does not reproduce the full MedHallu benchmark.

## MedExQA — close prior for multiple medical explanations

Kim, Wu, Abdulle and Wu (2024), *MedExQA: Medical Question Answering Benchmark with Multiple Explanations*, BioNLP 2024, pages 167–181, DOI 10.18653/v1/2024.bionlp-1.14. Publisher metadata: https://aclanthology.org/2024.bionlp-1.14/ . Retrieved full text: https://arxiv.org/abs/2406.06331 . Dataset card: https://huggingface.co/datasets/bluesky333/MedExQA . Preparation, methods, explanation evaluation, human study and limitations were inspected in the retrieved 15-page PDF; no benchmark run was reproduced.

It contains 965 multiple-choice questions across five specialties, with two reference explanations per question and human validation of distinct writing styles. There are five development questions per specialty and 940 test questions. Medical explanation pairs and stylistic diversity are established prior work; they are not new merely because our interface has two views. The pairs are reference explanations, rather than necessarily explicit lay/expert transformations of an unchanged target's behavioral audit.

The paper distinguishes next-token/logit classification from generated chat-answer parsing; GPT was excluded from its logit evaluation. This directly supports using an explicit comparable categorical-output protocol rather than assuming every API exposes equivalent logits. Explanation metrics include BLEU, ROUGE, METEOR and SciBERT-based BERTScore, with incorrect answers receiving zero in its combined evaluation. Human assessment used three health-related MSc annotators on only 25 development examples; limitations identify author involvement and small scale. Its reported correlation increase from 0.9347 to 0.9385 with multiple references is small and does not prove internal model faithfulness, clinical usefulness or our method's benefit.

Its dataset is CC BY-NC-SA 4.0 according to the paper/card; it is not silently substituted into the current MIT-repository PubMedQA study. A future medical semantic-correctness study would require suitable domain evaluation; our present behavioral evidence audit makes a narrower claim.

## Previously reviewed nearby methods

L25 Cross-Refine already uses generator/critic/refinement and evaluates HealthFC. It can alter both answer and explanation; our adaptation freezes the target answer and must control call opportunity. Health-domain critic gains are not uniform and the original selected human ratings are not unrestricted evidence-preservation yield.

L13 TalkToModel already provides conversational explanations for tabular models, including a diabetes example. A professional healthcare XAI interface is not a new contribution by itself. Its target-model scope differs from our LLM classifier.

L33 VERDICT already presents accountable rationales in clinical trial matching through an SMT/MaxSMT decision architecture. The earlier review checked abstract/author README, not full text; solver-derived decisions differ from auditing a frozen LLM decision. Retain that evidence-access limitation.

## Consequence for the claim

The defensible working contribution is an implemented and independently evaluated protocol for preserving fixed-target behavioral evidence across audience narratives, including numeric/binding/scope faults, one bounded repair and explicit fallback coverage. It requires measured comparisons against grounded blind rewrite, generic critic/refinement and deterministic templates. A healthcare setting, multiple explanations, an entailment checker or a repair loop alone is insufficient. Current feasibility checks establish none of the proposed semantic effects; the test matrix and independent annotation are still unrun.
