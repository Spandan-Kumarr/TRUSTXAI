# Step4 — experiment design and runtime preparation

Prepared27October2026. Start with STEP_04_EXPERIMENT_PROTOCOL.pdf or .docx. EXPERIMENT_CONFIG.json contains selected candidates, planned counts, gates and null revision/hash fields. This is not a locked, runnable final study until primary access, licences, model weights and feasibility are verified.

Selected task: offline SMS spam triage. Main CPU candidate: Qwen2.5-1.5B-Instruct; smaller fallback selected only through feasibility checks. Semantic checker candidate: nli-deberta-v3-base. No paid API/GPU assumed. User's MacBook AirM5 is an optional uninspected local environment.

Verified: CPU resource observations, pinned runtime imports and compatible package installation. Not run: model inference, data preparation, pilot, semantic checker or research experiments. Public model/dataset hosts currently return403; network additions are saved, not applied/published. Complete unaffected protocol work while access is pending.

Use INSTALL_CPU_RUNTIME.sh only in this Linux /workspace environment. It is not a macOS installer. No application code, commits, push or external submission was performed.
