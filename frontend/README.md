# TRUSTXAI clinical workspace

React, TypeScript and Vite interface for the local FastAPI service. The UI submits real API requests; it contains no fabricated diagnostic results.

```sh
npm ci
npm run dev
```

Development requests under `/api` proxy to `http://127.0.0.1:8000`. `npm run build` produces `dist/`, which the backend serves in production.

The diagnostic composer requires a vignette, a question and four candidate diagnoses. Editing a completed case creates a new case with `parent_id`; the original input and decision remain in history. Ask-with-sources and case follow-ups display the answer's recorded source passages and grounding status. Evidence, runtime provenance and explanation-check details are available in the audit drawer. The theme follows the system initially and stores only the theme preference in browser storage.

Browser checks:

```sh
npx playwright install chromium
npm run test:e2e
# If Chromium is already installed on the system:
PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium npm run test:e2e
```

The four browser tests use explicitly labelled API fixtures to verify diagnostic submission/polling, evidence inspection, follow-ups and citations, immutable revisions, mobile navigation and theme, JSON import, cancellation/deletion, and validation. They do not measure real inference or clinical accuracy. Fixture screenshots are generated under `test-results/screenshots/`. Backend inference validation is separate.

The Playwright configuration and tests use CommonJS because Playwright 1.52's ESM TypeScript loader hangs with the environment's Node 24 runtime. Application source remains TypeScript.
