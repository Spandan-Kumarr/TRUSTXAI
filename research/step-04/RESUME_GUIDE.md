> SUPERSEDED SMS DOCUMENT —27October2026: user requested healthcare. Earlier network blocker is resolved. Read healthcare-scope/HEALTHCARE_DIRECTION.md and current VALIDATION_AND_STATUS.json. This historical text is not the healthcare protocol.

# Remaining Step 4 work

Official metadata, licences, dataset bytes, source splits and tokenizer-only preflight now pass. Full target/NLI weights and model inference do not.

The exact observed weight-delivery redirect is **us.aws.cdn.hf.co**. Its proxy403 is separate from working huggingface.co metadata. The new host was saved additively to the draft; runtime activation/publication has not been confirmed. Review/save the change in environment settings and publish, then continue.

After a meaningful network update, run the prepared interpreter with feasibility/download_models.py. It checks the public HTTPS route, uses pinned revisions, resumes with supported standard HTTP, and compares safetensors SHA-256 against the publisher's recorded LFS digests. No TLS or checksum check is disabled. The new download helper is syntax-checked; a successful full transfer has not yet been tested.

Then load the verified target weights, score only the20feasibility messages, check accuracy/timing/memory, generate the prespecified ten two-view JSON cases, and smoke-check the NLI model. Record failures and revise only using feasibility data. Do not inspect final-test inference or change sample membership based on outcomes. Prompt/checker development and final test lock remain later stages.

Raw messages and original source captures stay in /workspace/thesis-runtime. SPLIT_MANIFEST.csv contains source IDs/hashes. Source grouping is verified; it does not establish absence of model-pretraining contamination.
