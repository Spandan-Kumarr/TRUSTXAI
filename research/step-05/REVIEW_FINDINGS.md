# Backend correctness review

Reviewed on 27 October 2026. Scope: the new local diagnostic workspace, its evidence contract, generated-explanation release flow, source-grounded chat, SQLite history and HTTP boundary. The review used code inspection and scripted protocol fakes. It did not load model weights or independently judge clinical answers, prose support or reader understanding.

Final verification: **107 tests passed** in 0.51 seconds. All defects listed below are corrected in the exercised implementation. The only emitted warning is a dependency deprecation in Starlette's test client. The distinct novice/expert fallback wording retains the same recorded facts; accepted generic-critic baselines preserve their initial generated pair rather than replacing it with that fallback.

## Regressions found during implementation

The review identified these concrete defects and added regression tests while the implementation was corrected:

- The explanation checker zipped requested support/coverage checks against returned scores without requiring equal lengths. An empty score list could pass. The citation checker could similarly accept an incomplete nonempty score list. Both require exactly one result per requested pair.
- Initial binding checks covered the overall case digest but omitted the exact source spans, modified-input digests and per-query model signatures. Binding checks now reject mixed source offsets, model identities, query hashes, selected observations and omission metadata. An independent expected target signature can be supplied by the pipeline.
- The numeric checker counted the method phrase “one-span omission” as an extra quantity, so the canonical facts failed their own count check. Method wording is excluded from quantity extraction.
- B0/B1/B2/B3 initially ran the proposed NLI gate inline. That would change the declared baselines. These paths retain baseline outputs without the proposed gate. B3 uses its own generic critic decision and permits at most one repair.
- The chat option guard missed ordinary wording such as “The selected option is B” when the frozen original answer was A. This construction is now covered by an explicit regression using permissive mocked NLI.
- Queue-full rejection initially happened after saving a new conversation or follow-up message, leaving orphan queued cases or duplicated follow-ups on retry. HTTP regressions check that rejected requests leave no visible orphan conversation and preserve existing history.
- Public feasibility examples now bind their source identifier to the recorded question, candidates, original span plan and input digest. Modified clinical content cannot retain that attribution. Source-binding tests also caught a whitespace-equivalence edge: accepted display whitespace must be restored to the canonical source question before reusing its frozen input digest.
- A real-model chat integration check produced cited prose instead of the requested JSON. Chat now permits complete plain prose through the same citation and per-sentence support gate. It does not recover partial fields from malformed JSON or fenced payloads. Four added test cases exercise this behavior and the rejection boundaries; the diagnostic narrative-pair schema remains strict.

The tests also check one repair before a labelled deterministic fallback; invalid original decisions; disagreement on the selected omission recheck; cancellation before publication; malformed views; unsupported extra clauses; fabricated citation numbers; source-support failures; gold-label exclusion; unknown source rejection; case versioning; exported snapshots; strict target-label parsing; fresh full target queries; context overflow without truncation; and checker-cache invalidation on revision change.

## Interpretation boundaries

Passing these tests establishes the exercised software contracts under scripted inputs. Mock entailment scores are chosen test values, not measurements of the real entailment model. The tests cannot show that the NLI checker reliably rejects medical hallucinations, that accepted prose is independently supported, that an omission establishes causation, or that either audience view improves understanding.

The configured release and generic-critic thresholds remain provisional development choices. They are not calibrated clinical confidence scores. Final threshold selection, independent supported/unsupported annotations, the held-out diagnostic study and a human audience evaluation remain separate research work under the existing protocol.

Source-grounded chat uses the finite local registry plus the active case record. Public-source notes are curated summaries with recorded provenance; a provenance-file digest does not make a note a verbatim publisher passage. The application labels source content types and retains source snapshots in message history. Retrieval coverage and real-model answer support still require empirical evaluation.

The research runner must report ungated baseline prose separately from proposed-method release status and retain all requested sources in coverage-sensitive denominators. A deterministic evidence fallback is a system output; it does not count as a successful generated narrative pair. No test result here establishes diagnostic accuracy, novelty over existing refinement/verification methods, superiority over GPT/Gemini, or patient benefit.

## Reproduction

Run from the repository root:

```sh
PYTHONPATH=backend /workspace/thesis-runtime/venv/bin/python -m pytest -q
```

The suite uses temporary SQLite databases and protocol fakes; it performs no model download, weight loading or external inference.
