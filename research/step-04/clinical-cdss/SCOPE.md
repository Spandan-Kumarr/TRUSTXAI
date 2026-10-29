# Active scope — Healthcare Clinical Decision Support System

27 October 2026. User explicitly confirmed the intended application is a Healthcare Clinical Decision Support System (CDSS). The approved broad thesis title remains unchanged.

Primary workflow under verification: a clinical vignette with clinical decision options, a fixed local LLM recommendation, observed evidence-omission audit, novice/technical explanations and provenance/uncertainty/fallback status. The user confirmed diagnostic decision support from clinical cases. This is a benchmark-based research prototype, not a clinically validated diagnostic service.

MedQA clinical vignettes are the primary benchmark candidate being verified. PubMedQA work is preserved as an auxiliary biomedical evidence-QA feasibility task. Its accuracy and partial rendering pilot must not be presented as clinical decision-support performance. All MedQA model evaluations remain unrun.

User confirmed no GPT/Gemini API access or budget: local models only. Existing Qwen3 weights are available, but their suitability must be measured on the actual clinical task. No benchmark accuracy or medical benefit is assumed.

Primary dataset selection needs verified release/source, content terms, field allowlist excluding gold answers, official split boundaries and a label-blind clinical-task eligibility rule. Model and explanation feasibility must then be measured without inspecting final-test predictions. Keep diagnosis/classification correctness separate from faithful reporting of model-behavior evidence. No real patient data, live clinical integration or external submission is part of the current work.
