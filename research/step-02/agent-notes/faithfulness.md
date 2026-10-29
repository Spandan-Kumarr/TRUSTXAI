# Step 2 workstream: faithful explanations, grounding and checking

Prepared 26 October 2026. Eight selected studies are recorded in `faithfulness.json`. This is a targeted research workstream, not an exhaustive systematic review. Academic PDF hosts were unavailable under the current runtime policy. Evidence was gathered from actual primary author repositories and, for two papers, official ACL Anthology XML supplied by the parent research pass. **No full paper PDF was read in this workstream.** The supplied two base papers remain separately available to the parent.

## Main findings for the thesis

1. Generation followed by critique, checking and refinement is established prior art. MADR is a particularly close example for evidence-grounded explanations in fact checking.
2. SHAP-to-narrative translation is established prior art (XAIstories); it normally explains a classifier distinct from the explaining LLM. Reusing it does not establish an explanation of an LLM decision.
3. Checking redactions or counterfactuals against the same LLM is established prior art (Madsen et al.; also the supplied Randl paper). These are valuable baseline tests, not novel by themselves.
4. **CC-SHAP explicitly argues that many “faithfulness” tests establish output self-consistency, not faithfulness to inaccessible internal reasoning.** This directly constrains terminology and novelty claims.
5. Attribution-guided explanation generation is a close 2026 competitor: Faithfulness Serum injects PE-LRP attribution guidance into attention. Its author repository reports ACL Main 2026 acceptance; independent venue verification remains necessary.
6. Avoid a one-sided claim that all LLM self-explanations are useless. A Positive Case for Faithfulness studies how explanations help predictor models simulate target-model behavior. Its author repository cites ICML2026, pending independent proceedings verification.
7. A promising question remains how to test **supported-claim preservation through audience adaptation**, with explicit unsupported/contradictory/omitted-claim analysis, measured verifier error and coverage/cost. The sources inspected here do not prove this is an unaddressed gap. Root's broader literature pass and Step 3 must test it against the nearest methods.

## Selected studies and actual access

### F01 — Turpin et al. (2023)

**Title:** Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting.

**Authors verified:** Miles Turpin, Julian Michael, Ethan Perez, Samuel R. Bowman.

**Primary evidence:** https://raw.githubusercontent.com/milesaturpin/cot-unfaithfulness/main/README.md

**Paper link from authors:** https://arxiv.org/abs/2305.04388

**Access:** Author README, including abstract and experiment/code overview; no full paper. The README's citation is an arXiv entry. Its archival venue was not independently verified in this workstream.

**Verified substance:** Input biasing can affect the selected answer without being acknowledged in a generated chain of thought. Repository provides prompts, samples and analysis for BBH and BBQ.

**Exact source snippet:** “CoT explanations can be plausible yet misleading”.

**Use:** Motivate targeted influence tests. Do not infer universal unfaithfulness, or quote a maximum observed result as the expected degradation for this thesis.

### F02 — Lyu et al. (2023)

**Title:** Faithful Chain-of-Thought Reasoning.

**Authors verified:** Qing Lyu, Shreya Havaldar, Adam Stein, Li Zhang, Delip Rao, Eric Wong, Marianna Apidianaki, Chris Callison-Burch.

**Primary evidence:** https://raw.githubusercontent.com/veronica320/Faithful-COT/main/README.md

**Paper:** https://arxiv.org/abs/2301.13379

**Access:** Author README with architecture, solver descriptions, usage and citation. Repository reports IJCNLP-AACL2023 acceptance; official proceedings metadata not yet inspected here.

**Verified substance:** A Translator LM produces reasoning representations that deterministic solvers execute to derive answers. Repository covers several structured reasoning datasets.

**Exact source snippet:** “the deterministic solvers for each dataset”.

**Use:** Prior art for executable checking and language-to-symbolic reasoning. Correct execution does not by itself guarantee that the input was correctly translated. It is not a drop-in baseline for explaining a fixed classifier after prediction.

### F03 — Parcalabescu and Frank (2024)

**Title:** On Measuring Faithfulness or Self-consistency of Natural Language Explanations.

**Official publication:** ACL2024, Volume 1 Long Papers, pp.6048–6089. DOI https://doi.org/10.18653/v1/2024.acl-long.329.

**Official metadata/abstract:** https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2024.acl.xml

**Author evidence:** https://raw.githubusercontent.com/Heidelberg-NLP/CC-SHAP/main/README.md

**Access:** Official archival metadata and abstract plus author README; no full paper.

**Verified substance:** CC-SHAP compares input contributions toward an answer with contributions toward an explanation. The official abstract characterizes earlier faithfulness tests as output-level self-consistency and describes a Comparative Consistency Bank. README documents counterfactual, input-from-explanation, biasing and CoT corruption implementations.

**Exact official-abstract snippet:** “these faithfulness tests do not measure faithfulness to the models’ inner workings”.

**Use:** Essential measurement reference. It should prevent presenting a checker pass or agreement with another explainer as privileged ground truth about internal reasoning. A comparator may require costly target-model probability evaluations and careful masking assumptions.

### F04 — Kim et al. (2024)

**Title:** Can LLMs Produce Faithful Explanations For Fact-checking? Towards Faithful Explainable Fact-Checking via Multi-Agent Debate.

**Authors verified:** Kyungha Kim, Sangyun Lee, Kung-Hsiang Huang, Hou Pong Chan, Manling Li, Heng Ji.

**Primary evidence:** https://raw.githubusercontent.com/SangyunLee1027/Code-for-Towards-Faithful-Explainable-Fact-Checking-via-Multi-Agent-Debate/main/README.md

**Paper:** https://arxiv.org/abs/2402.07401

**Access:** Author README including abstract, detailed method and error typology; archival venue not verified, no full paper.

**Verified substance:** Multi-Agent Debate Refinement (MADR) uses initial explanation generation, two debaters, feedback exchange, judge evaluation and refinement. README documents PolitiHop fact checking and intrinsic/extrinsic entity/event/noun-phrase errors, incoherence, overgeneralization and irrelevant evidence.

**Exact snippet:** “A final agent (Refiner) revises the explanation based on the combined feedback.”

**Use:** Strong nearest competing workflow. Evidence consistency is distinct from internal causal faithfulness; critics can share model errors and add cost. Budget-matched checking/refinement is a reasonable baseline candidate. The accessed README does not demonstrate preservation across audience transformations.

### F05 — Martens et al. (author citation year2024)

**Title:** Tell Me a Story! Narrative-Driven XAI with Large Language Models.

**Authors verified:** David Martens, James Hinns, Camille Dams, Mark Vergouwen, Theodoros Evgeniou.

**Primary evidence:** https://raw.githubusercontent.com/ADMAntwerp/XAIstories/main/README.md

**Paper:** https://arxiv.org/abs/2309.17057

**Access:** Author README; no full paper. The author citation says2024 while the arXiv identifier originated in2023. Final publication year/venue needs verification.

**Verified substance:** SHAPstories generates narratives for models exposing `predict_proba`, with example notebook and LLM integration.

**Exact snippet:** “Currently, only models that have a `predict_proba` function are supported”.

**Use:** Established SHAP-to-language prior art. No quantitative human-study or checker-efficacy claims were verified from the accessed source. Preserve the distinction between the model being explained and the LLM explaining it.

### F06 — Alon, Zimerman and Wolf (2026)

**Title:** Faithfulness Serum: Mitigating the Faithfulness Gap in Textual Explanations of LLM Decisions via Attribution Guidance.

**Primary evidence:** https://raw.githubusercontent.com/Bar-A-94/FaithfulnessSerum/main/README.MD

**Paper:** https://arxiv.org/abs/2604.14325

**Status:** Author repository says “Accepted to ACL 2026 (Main Conference)”. The repository's own citation remains an arXiv entry. Independently verify proceedings before describing it as a verified archival publication.

**Access:** Author README, method/configuration/usage details; no full paper.

**Verified substance:** Tests counterfactual hint influence; computes PE-LRP token attributions and injects them into attention during explanation generation. Open-weight interventions are distinguished from closed-model generation/evaluation scripts.

**Exact snippets:** “Injecting them into attention during explanation generation”; “Too high → unstable or repetitive outputs”.

**Use:** Strong recent prior art against claiming generic attribution-guided LLM explanations as new. The accessed text supports a restricted mechanism and its implementation, not universal fidelity. Model-access and intervention-strength requirements matter.

### F07 — Mayne et al. (2026)

**Title:** A Positive Case for Faithfulness: LLM Self-Explanations Help Predict Model Behavior.

**Authors verified:** Harry Mayne, Justin Singh Kang, Dewi Sid William Gould, Kannan Ramchandran, Adam Mahdi, Noah Y. Siegel.

**Primary evidence:** https://raw.githubusercontent.com/HarryMayne/faithfulness/main/README.md

**Paper:** https://arxiv.org/abs/2602.02639

**Status:** Author README cites ICML2026 and OpenReview `nkJIMejfaN`; independent proceedings not inspected.

**Access:** Author README, experimental workflow and citation; no full paper.

**Verified substance:** Generates counterfactual inputs, collects reference-model predictions, evaluates predictor-model outputs and analyses self-explanation-assisted simulatability.

**Exact snippet:** “Evaluating predictor models on their ability to simulate model behavior”.

**Use:** A complementary behavioral perspective and a necessary counterweight to universal negative claims. Simulatability remains conditioned on task, target, predictor and prompts; it is not direct access to hidden causal computation.

### F08 — Madsen, Chandar and Reddy (2024)

**Title:** Are self-explanations from Large Language Models faithful?

**Official publication:** Findings of ACL2024, pp.295–337. DOI https://doi.org/10.18653/v1/2024.findings-acl.19.

**Official metadata/abstract:** https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/2024.findings.xml

**Author evidence:** https://raw.githubusercontent.com/AndreasMadsen/llm-introspection/main/README.md

**Paper:** https://arxiv.org/abs/2401.07927

**Access:** Official archival metadata and abstract plus author README with task configurations; no full paper.

**Verified substance:** Self-consistency tests address counterfactual, feature-attribution and redaction explanations. Reliability varies by explanation type, model and task. Author code includes IMDB, RTE, bAbI-1 and MCTest and configurable prompt variations.

**Exact source snippet:** “the truthfulness is highly dependent on the model and the specific task”.

**Use:** A direct baseline source for model-matched self-consistency checks. Terms such as interpretability-faithfulness in author wording must not obscure the weaker operational evidence highlighted by F03.

## Unresolved discoveries and exclusions

- **Agarwal, Tanneru and Lakkaraju (2024), Faithfulness versus plausibility: On the (Un)reliability of explanations from large language models**, arXiv2402.04614: exact title/authors are cited in the supplied Randl base paper (references). Direct primary text was not obtained. Do not present it as a fully read study; this is a secondary-citation verification target.
- **Lanham et al. (2023), Measuring Faithfulness in Chain-of-Thought Reasoning:** discussed in CC-SHAP's method README; full bibliographic and paper evidence not obtained here. Retain as a citation-tracing target, not a substantively reviewed entry.
- **Faithful-LME:** exact repository searches produced no match; this does not establish non-existence. Keep as an unresolved named search target rather than inventing details.
- **cerai-iitm/LExT:** accessible repository combines plausibility/faithfulness submetrics, but no paper title, authorship or peer-reviewed publication metadata was verified. Treat as a repository-only implementation discovery; do not cite it as an established scholarly metric or adopt its aggregate score as validated.
- **safety-research/faithful-cot:** accessible repository describes structural RL/attention/gradient interventions and code/math tasks. GitHub description names Faithfulness as Information Flow, but the README inspected did not provide a stable paper bibliography. Retain for later primary-paper verification, outside the eight-study list.

## Search and coverage notes

Discovery used legitimate GitHub repository search and direct raw reads from actual source repositories. Representative queries: `Faithful Chain-of-Thought Reasoning`, `faithfulness plausibility`, `Measuring Faithfulness`, `Faithful LLM explanations`, `XAIstories`, and quoted titles with `in:readme`. Some searches returned429; unchanged requests were not repeatedly retried. Author links and exact metadata were checked where accessible. Root's official ACL collection screening supplies broader coverage.

The local README captures are under `/tmp/faithfulness-literature/`; per-source SHA256 values are in the JSON where recorded. Do not interpret absence in these constrained searches as absence in the literature. No contribution is certified novel by this workstream.
