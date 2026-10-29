# Reproduction notes — measured clinical feasibility

This is the executed Linux cloud CPU profile, not a tested Mac installation. The M5 MacBook's RAM/MPS performance is unknown. Data/model downloads are public and ungated. No API keys or paid calls are required.

Use `/workspace/thesis-runtime/venv/bin/python`. The dependency freeze, selected model revisions/digests, compiler source revision, GGUF hash, native library hashes and current hardware preflight are in `evidence/`. The target uses PyTorch FP32, four threads; the communicator uses official Qwen3-1.7B GGUF Q8_0 via llama-cpp-python 0.3.16, two decode/four prefill threads. These are different roles, not an unspecified shared model.

Raw data and outputs live outside Git under `/workspace/thesis-runtime/clinical-cdss`. `TRUSTXAI_RUNTIME` can set the runtime root in the principal scripts. Public `EXPLORATORY_SOURCE_EXCLUSIONS.json` preserves the 48 source IDs excluded during scope QA. Do not resample cases based on outcomes.

The source files were fetched from the pinned GBaker mirror, explicitly identified in `evidence/SOURCE_PROVENANCE.json`; their counts and SHA256 were verified. The author repository supplies code and an external data link, not these versioned question files. Preserve author/mirror attribution and notices; avoid redistributing exam text or the unused textbook corpus.

Executed primary sequence, from the clinical-cdss directory:

```bash
/workspace/thesis-runtime/venv/bin/python scripts/fetch_clinical_data.py
/workspace/thesis-runtime/venv/bin/python scripts/prepare_clinical.py
/workspace/thesis-runtime/venv/bin/python scripts/run_clinical_pilot.py --phase classification --target-dtype float32 --suffix _DIAG_FP32
/workspace/thesis-runtime/venv/bin/python scripts/run_clinical_pilot.py --phase evidence --target-dtype float32 --suffix _DIAG_FP32
/workspace/thesis-runtime/venv/bin/python scripts/render_native_pilot.py
/workspace/thesis-runtime/venv/bin/python scripts/measure_nli_cost.py
/workspace/thesis-runtime/venv/bin/python scripts/project_compute.py
```

The inference programs refuse to overwrite completed results. Keep the recorded outputs. For a repeat use an isolated copy/new output workspace and record its run identity; do not delete failed attempts or mix them with the primary result. `evidence/EXECUTED_PILOT_SCRIPT.py` preserves the exact classifier/evidence harness used before its defaults were changed to the selected FP32 profile. Actual primary invocations already specified FP32 explicitly; prediction logic is unchanged.

The evidence phase saves eight records under `pilot_DIAG_FP32/*_evidence.json`. It tests only first/last spans, then freshly rechecks the selected result. The native phase consumes those exact records; raw narrative/critic traces stay private. The full all-span pipeline, complete checkers and one-repair experiment are Step 5 work.

Resource dependencies were installed and checked in this environment. The native binding was built from the official abetlen/llama-cpp-python tag v0.3.16 and its pinned llama.cpp submodule using GCC/G++, CMake, CPU-only settings and `GGML_NATIVE=ON`. Explicit compilers avoid the inherited unavailable `clang -pthread` setting. Diskcache 5.6.3 was installed from its publisher-hash-verified wheel. Native/HuggingFace token IDs matched on preflight and every measured generation.

Asset helpers: `scripts/download_target.py` retrieves pinned Qwen3-4B safetensors and verifies publisher LFS digests; `scripts/download_native_communication.py` retrieves the pinned official GGUF and verifies its complete SHA256. The native reference tokenizer is the pinned Qwen3-1.7B revision in `evidence/SELECTED_MODEL_ARTIFACTS.json`. The semantic checker is the pinned NLI repository in the same file. Their exact local paths are recorded in the sibling `evidence/MODEL_REVISIONS.json` supplied with the pack. Populate those assets before an isolated fresh run. The target downloader's large-transfer routine and original native downloader were executed; the small relocation of the target helper was syntax-checked, not independently redownloaded.

Current output artifacts validate actual source preparation, primary classification, eight-case evidence/format/runtime, native tokenizer plumbing and a measured cost projection. A complete fresh-machine bootstrap was not rerun. JSON validity, NLI smoke checks and cost fixtures are not semantic or clinical accuracy evaluations. Development/test inference and H1/H2/H3 remain unrun; do not change that by running a test cohort before the development protocol is frozen.

The data retrieval helper was syntax-checked; recorded source bytes were already retrieved and verified. FORMAT_PILOT_OUTPUTS_FOR_REVIEW.json provides actual unreviewed audience pairs and canonical audit facts without full clinical case text. These are not semantic benchmark labels.
