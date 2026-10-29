# Step 5 delivery: TRUSTXAI clinical workspace

**Recorded:** 27 October 2026  
**Thesis:** *A Trustworthy & Explainable AI Framework for Large Language Model-Based Decision Support Systems*  
**Task:** diagnostic decision support from a clinical vignette and four supplied candidate diagnoses  
**Status:** implemented local research prototype; clinical validation and comparative superiority are not established

## Delivered application

TRUSTXAI now has a working ChatGPT/Codex-style conversational interface backed by real, pinned local models. It provides:

- conversation history, search, immutable case versions, deletion, JSON export, themes and responsive desktop/mobile layouts;
- diagnostic case entry, four candidate diagnoses, synthetic examples and bound public MedQA feasibility examples;
- a frozen A–D target suggestion, fresh queries for every case-span omission and an independent selected-input recheck;
- simple and technical evidence views built from the same typed facts;
- exact spans, offsets, omission outcomes, recheck, model identity and explanation checks in an evidence drawer;
- one bounded explanation repair, complete recheck and labelled evidence-template fallback when checks fail;
- source-grounded chat over seven recorded public-research/protocol notes plus active-case evidence;
- citation identity and NLI support checks, showing labelled retrieved notes when generated text is withheld;
- local SQLite history, exact score caching, a serialized inference worker, bounded queue and cancellation.

The application has no GPT/Gemini API dependency and makes no remote model request. Missing local assets cause an explicit failure; no mock answer is substituted.

## Implemented evidence flow

1. Validate the diagnostic question and exactly four distinct, non-empty options.
2. Run pinned Qwen3-4B-Instruct-2507 in CPU FP32 with greedy A–D output and no decision retry.
3. Make fresh full queries for the original case, each of two to eight stable one-span omissions and the selected omission recheck.
4. Check input digests, offsets, option/name binding, model signature, modified-input digests, counts and recheck identity.
5. Use pinned Qwen3-1.7B GGUF Q8_0 to render simple and technical views with deterministic decoding.
6. Apply typed structural rules and pinned DeBERTa NLI to the complete pair at the provisional 0.90 threshold. Allow one joint repair.
7. If the repaired pair fails, publish a labelled deterministic evidence template. This is interface output, not a successful LLM narrative generation.

Application communication uses a 4,096-token context to accommodate source chat. Step 4 rendering feasibility used 2,048 tokens, so application-chat timing is a separate engineering observation.

## Components

| Role | Component | Frozen behavior |
| --- | --- | --- |
| Diagnostic target | Qwen3-4B-Instruct-2507, `cdbee75f17c01a7cc42f958dc650907174af0554` | CPU FP32, 4 threads, greedy A–D, 8-token cap, 1,536-token input limit |
| Communicator | Qwen3-1.7B-GGUF Q8_0, `90862c4b9d2787eaed51d12237eafdfe7c5f6077` | llama-cpp-python 0.3.16, CPU, deterministic, 384-token cap, 4,096-token context |
| Support checker | nli-deberta-v3-base, `6c749ce3425cd33b46d187e45b92bbf96ee12ec7` | CPU FP32, no truncation, unresolved beyond 512 tokens, provisional threshold 0.90 |
| API/storage | FastAPI and SQLite | loopback default, local storage, one inference worker |
| Interface | React 19, TypeScript and Vite | production assets served by FastAPI |

Exact model digests are in `research/step-04/evidence/MODEL_REVISIONS.json`; native library revisions and hashes are in `research/step-04/clinical-cdss/evidence/NATIVE_BUILD_PROVENANCE.json`; observed packages are in `APP_ENVIRONMENT.json`.

## Verification completed

- **107 backend tests passed** in 0.51 seconds.
- **4 Chromium interface tests passed** in 7.2 seconds after a production build.
- Production build transformed 1,581 modules; the JavaScript bundle was 236.08 kB before gzip.
- Browser fixtures are explicitly labelled. They verify UI behavior and do not count as clinical evidence.

The backend suite covers source/input binding, offsets, target identity, omission hashes, recheck binding, schemas, counts, scope rules, fail-closed scoring, citations, queue rollback, immutable versions, cancellation and export. Protocol fakes test control flow; they do not establish real NLI reliability or clinical correctness.

### Real-model diagnostic integration

A browser with no mocked routes submitted the labelled synthetic respiratory example:

| Observation | Result |
| --- | --- |
| Conversation ID | `81678ff5-9b0a-45ec-b91e-6b59827d901e` |
| Recorded option | A — Community-acquired pneumonia |
| Case spans tested | 4/4 |
| Recorded answer changes | 0 |
| Selected-input recheck | A; agreed |
| Generated-pair release | Failed provisional automated checks |
| Released presentation | Labelled evidence template with distinct simple/technical wording |
| Wall / CPU time | 160.08 / 450.22 seconds |
| Peak process RSS | 18.93 GiB |
| Browser errors / overflow | 0 / none at tested desktop and mobile viewports |

The synthetic case has no assigned clinical gold label. This run establishes integration and fail-closed publication behavior, not diagnostic accuracy.

### Real-model source-chat integration

The local communicator answered a MedQA dataset question from retrieved notes. Its cited draft did not meet the provisional 0.90 per-sentence entailment gate, so it was withheld. The interface displayed three labelled retrieved notes with preserved citation numbers and `Curated source summary` labels. This confirms the safe fallback path, not retrieval coverage or checker accuracy.

The machine-readable record is `LIVE_BROWSER_CHECK.json`. Raw histories and drafts remain in the runtime SQLite database outside Git.

## Review images

- `APP_PREVIEW_WELCOME.png` — new-conversation screen.
- `APP_PREVIEW_REAL_SYNTHETIC_AUDIT.png` — real suggestion, explanation and evidence drawer.
- `APP_PREVIEW_REAL_SYNTHETIC_MOBILE.png` — responsive real-case view.
- `APP_PREVIEW_REAL_SOURCE_CHAT.png` — real source-chat fallback and curated-source label.

Screenshots in `frontend/test-results` are UI fixtures and must not be presented as experimental evidence.

## Research boundaries

- The task selects among four supplied options. It is not unrestricted diagnosis, treatment advice, EHR integration or clinical deployment.
- Omission results describe model behavior; they do not prove clinical causation or complete internal reasoning.
- The NLI threshold is provisional and not independently calibrated for medical claims.
- Curated summaries retain URLs and provenance hashes but are not publisher quotations; chat does not search the whole web.
- The Step 4 result of 16/24 is separate from application integration and does not establish patient benefit.
- No GPT/Gemini experiment or comparative superiority result exists.
- B0–B4/P adapters exist as standalone paths. The shared-initial-generation comparison runner belongs to Step 6.
- MacBook M5/MPS and fresh-machine setup are not validated; the verified runtime is Linux CPU cloud.

## Completion decision

Step 5 is complete as an application implementation and integration milestone. The code, API, interface, real local models, evidence audit, fail-closed explanations, source-chat fallback, automated tests and real-model browser evidence are present.

The reviewable source bundle is `research/STEP_05_APPLICATION_PACK.zip`; its separately generated digest is in `research/STEP_05_APPLICATION_PACK.sha256`. It contains application source, tests, Step 5 records and the directly referenced protocol/provenance files; it excludes model weights, runtime databases, caches and raw datasets.

Step 6 must use only the 40 development sources for annotations, threshold calibration, prompt diagnostics and the shared comparison runner, then freeze all choices before unlocking the 60-case held-out test. Paper and Review 2 claims must come from those measured comparisons.
