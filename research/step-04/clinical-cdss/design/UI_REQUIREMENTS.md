# TRUSTXAI clinical CDSS interface

User preference confirmed 27 October 2026: a ChatGPT/Codex-inspired interface. This refines the earlier request for minimalist, professional graphics. This file specifies the application to build in Step 5; it is not a completed interface.

The desktop layout has a narrow left sidebar for new cases, case history and settings; a spacious central conversation; and a rounded composer anchored at the bottom. An expandable right-side evidence panel provides the technical audit. Keep generous whitespace, restrained borders, readable typography and small icons. Use TRUSTXAI branding and a simple mark. Support light/dark themes; follow system preference initially.

The central welcome asks the user to select a research case or enter a clinical vignette, its diagnostic question and four candidate diagnoses. The validated benchmark task selects among supplied options; the interface must make that scope clear. Keep candidate entry in a compact expandable composer section. Do not imply unrestricted differential-diagnosis generation has been evaluated.

Assistant messages present the model-selected option and source option name, followed by the simple explanation. A per-message toggle opens the technical explanation. Follow-up actions expose recorded evidence: explain simply, show the audit, inspect an omitted case span. These actions remain bound to the same frozen case/model decision. Editing clinical input creates a new case version.

The evidence panel shows case findings with stable source references, actual omission outcomes, tested versus available spans, recheck status, model provenance and explanation-check/fallback status. Display model output as a suggestion requiring review. Show uncertainty through actual unresolved/unstable statuses; do not invent probability confidence, medical sources, citations or clinical validation.

Keep implementation details such as claim IDs, hashes, quantization and runtime seeds inside the technical audit where they help research verification. The ordinary conversation should remain clear and concise. No accounts, cloud-provider selection or paid API screens are required for the authorised local-only version.

On narrow screens collapse the sidebar and show evidence in a drawer. Provide keyboard navigation, visible focus, adequate contrast, labelled controls, accessible textarea resizing and reduced motion. Avoid decorative medical stock images, animated dashboards and excessive charts. Any clinical example in a public screenshot must be appropriately sourced or clearly synthetic, with predictions actually computed for that exact input.

Suggested dimensions: 250px sidebar, 820px maximum conversation width, optional 340px evidence pane. Suggested palette: light main #ffffff/sidebar #f9f9f9/text #252525/border #e5e5e5; dark main #212121/sidebar #171717/text #ececec/border #383838. Use system sans-serif fonts and restrained status accents.
