# Active Step4 — diagnostic clinical decision support

Read clinical-cdss/README.md, clinical-cdss/FEASIBILITY_REPORT.pdf and clinical-cdss/STEP_04_CLINICAL_PROTOCOL.pdf.

# Step 4 — diagnostic CDSS feasibility

Clinical 1.0, 27 October 2026. **Measured feasibility gates passed; application and thesis experiments not yet implemented.**

Primary task: most-likely-diagnosis selection from four supplied clinical options. Read FEASIBILITY_REPORT.pdf for actual observations and STEP_04_CLINICAL_PROTOCOL.pdf for the planned study. The primary fresh24case pool achieved16/24correct; this is feasibility, not final-test/clinical performance. All48earlier exploratory source IDs are excluded from the primary pools, and archived results remain visible.

The selected runtime is local-only: Qwen3-4B-Instruct-2507FP32target and official Qwen3-1.7BGGUFQ8_0communication, with separate phases. Dataset answer fields never enter model prompts. Raw exam text/generated outputs remain outside Git. The public pack contains source IDs/hashes, summaries, licences and scripts.

There are no development/test predictions, completed H1/H2/H3comparisons, independent semantic audits, GPT/Gemini results or clinical validation. Application/paper/slides are not yet complete. Step5is the actual application and full pipeline; design/UI_REQUIREMENTS.md records the user's ChatGPT/Codex-style preference. See REPRODUCE.md for selected commands. Older SMS/PubMedQA protocols/ZIPs are superseded for this primary clinical task.
