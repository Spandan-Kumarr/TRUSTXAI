// Browser-only API fixtures. No real inference, clinical evidence or measured performance.
const import_test = require("@playwright/test");
const input = { kind: "diagnostic", case_text: "Synthetic UI test vignette. This is an interface fixture only.", question: "Which supplied test option is selected?", options: { A: "UI fixture option A", B: "UI fixture option B", C: "UI fixture option C", D: "UI fixture option D" } };
const source = { id: "ui-source", title: "UI test source \u2014 not clinical evidence", content: "This passage exists only to verify the source dialog.", url: "https://example.org/ui-test", category: "test_fixture" };
const now = "2026-10-27T09:00:00Z";
async function fixtures(page, options = {}) {
  let saved = null;
  let history = [];
  let lastSubmission = null;
  await page.route("**/api/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    let body;
    if (path === "/api/runtime") body = { ready: true, phase: "ready", device: "CPU", target: { model: "UI test fixture" }, communicator: { model: "UI test fixture" } };
    else if (path === "/api/examples") body = ["One", "Two", "Three"].map((name, index) => ({ ...input, id: `synthetic-${index}`, title: `Synthetic UI fixture ${name}`, synthetic: true }));
    else if (path === "/api/sources") body = [source];
    else if (path === "/api/cases" && request.method() === "GET") body = history;
    else if (path === "/api/cases" && request.method() === "POST") {
      lastSubmission = request.postDataJSON();
      saved = { id: `case-${history.length + 1}`, title: lastSubmission.title || "Synthetic UI fixture case", input: { ...lastSubmission, kind: "diagnostic" }, status: "queued", created_at: now, updated_at: now, result: null, progress: { stage: "queued", detail: "UI test fixture queued.", percent: 0 }, messages: [{ id: "u1", role: "user", kind: "case", payload: lastSubmission, created_at: now }] };
      history = [saved, ...history];
      body = saved;
    } else if (path === "/api/chats" && request.method() === "POST") {
      const text = request.postDataJSON().text;
      saved = { id: "chat-1", title: text, input: { kind: "chat", text }, status: "complete", created_at: now, updated_at: now, messages: [{ id: "u1", role: "user", kind: "question", payload: { text }, created_at: now }, { id: "a1", role: "assistant", kind: "answer", payload: { text: "UI test answer with a recorded source.", citations: [source], grounding_status: "source_passages" }, created_at: now }] };
      history = [saved];
      body = saved;
    } else if (path.endsWith("/cancel")) {
      saved = { ...saved, status: "cancelled" };
      history = [saved];
      body = saved;
    } else if (path.endsWith("/messages")) {
      const text = request.postDataJSON().text;
      saved = { ...saved, status: "complete", messages: [...saved.messages, { id: "u2", role: "user", kind: "question", payload: { text }, created_at: now }, { id: "a2", role: "assistant", kind: "answer", payload: { text: "A grounded UI fixture follow-up.", citations: [source], grounding_status: "source_checked" }, created_at: now }] };
      body = saved;
    } else if (path.startsWith("/api/cases/") && request.method() === "DELETE") {
      history = [];
      body = { deleted: true };
    } else if (path.startsWith("/api/cases/")) {
      if (!options.pending && saved && saved.status === "queued") {
        saved = { ...saved, status: "complete", result: { evidence: { decision: { label: "A", name: "UI fixture option A" }, spans: [{ id: "S1", text: input.case_text, start: 0, end: input.case_text.length }], omissions: [{ span_id: "S1", label: "B", changed: true, valid: true }], selected: { span_id: "S1", label: "B" }, recheck: { agrees: true }, target: { model: "UI test fixture" } }, views: { novice: { C1: "UI fixture suggestion only.", C2: "UI fixture omission outcome.", C3: "One UI fixture span tested.", C4: "This is not a clinical result." }, expert: { C1: "Technical UI fixture decision.", C2: "Technical omission fixture.", C3: "Technical coverage fixture.", C4: "Technical limitation fixture." } }, release_status: "evidence_template", automated_release_passed: false, checker: { operating_point: "provisional_development" } }, messages: [...saved.messages, { id: "a1", role: "assistant", kind: "analysis", payload: { text: "UI fixture analysis" }, created_at: now }] };
        history = [saved, ...history.filter((value) => value.id !== saved.id)];
      }
      body = saved;
    } else return route.fulfill({ status: 404, json: { detail: "Unknown UI fixture route." } });
    await route.fulfill({ json: body });
  });
  return { submission: () => lastSubmission };
}
(0, import_test.test)("diagnostic flow preserves the case, displays recorded evidence, and binds follow-ups", async ({ page }) => {
  const fixture = await fixtures(page);
  await page.goto("/");
  await page.getByRole("button", { name: /Synthetic UI fixture One/ }).click();
  await (0, import_test.expect)(page.getByRole("textbox", { name: "Clinical vignette" })).toHaveValue(input.case_text);
  await (0, import_test.expect)(page.getByRole("textbox", { name: "Candidate diagnosis D" })).toHaveValue(input.options.D);
  await page.getByRole("button", { name: "Analyze diagnostic case", exact: true }).click();
  await (0, import_test.expect)(page.getByRole("heading", { name: "UI fixture option A", exact: true })).toBeVisible({ timeout: 1e4 });
  await page.getByRole("button", { name: "Technical explanation", exact: true }).click();
  await (0, import_test.expect)(page.getByText("Technical UI fixture decision.", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "View evidence", exact: true }).click();
  await (0, import_test.expect)(page.getByRole("heading", { name: "Evidence audit" })).toBeVisible();
  await (0, import_test.expect)(page.getByText("Changed", { exact: true })).toBeVisible();
  await page.screenshot({ path: "test-results/screenshots/desktop-evidence-UI-FIXTURE.png", fullPage: true });
  await page.getByRole("complementary", { name: "Evidence audit" }).getByRole("button", { name: "Close evidence audit", exact: true }).click();
  await page.getByRole("textbox", { name: "Follow-up question" }).fill("Explain the source support.");
  await page.getByRole("button", { name: "Send follow-up question" }).click();
  await (0, import_test.expect)(page.getByText("A grounded UI fixture follow-up.")).toBeVisible();
  await page.getByRole("button", { name: /UI test source/ }).click();
  await (0, import_test.expect)(page.getByRole("dialog", { name: "Source passage" })).toBeVisible();
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Edit as a new case" }).click();
  await (0, import_test.expect)(page.getByText("New version \xB7 The previous case stays in history.")).toBeVisible();
  await page.getByRole("button", { name: "Analyze diagnostic case", exact: true }).click();
  await import_test.expect.poll(() => fixture.submission()?.parent_id).toBe("case-1");
});
(0, import_test.test)("ask mode opens sources and persists theme on mobile without horizontal overflow", async ({ page }) => {
  await fixtures(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("button", { name: "Dark theme", exact: true }).click();
  await page.getByRole("button", { name: "Close navigation" }).click();
  await page.getByRole("button", { name: "Ask with sources", exact: true }).click();
  await page.getByRole("textbox", { name: "Your question" }).fill("What sources support the system?");
  await page.getByRole("button", { name: "Send question", exact: true }).click();
  await (0, import_test.expect)(page.getByText("UI test answer with a recorded source.")).toBeVisible();
  await page.getByRole("button", { name: /UI test source/ }).click();
  await (0, import_test.expect)(page.getByRole("dialog")).toBeVisible();
  await page.keyboard.press("Escape");
  (0, import_test.expect)(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  await (0, import_test.expect)(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.screenshot({ path: "test-results/screenshots/mobile-chat-dark-UI-FIXTURE.png", fullPage: true });
  await page.getByRole("button", { name: "Open evidence audit", exact: true }).click();
  await (0, import_test.expect)(page.getByRole("dialog", { name: "Evidence audit" })).toHaveAttribute("aria-modal", "true");
  await (0, import_test.expect)(page.locator("main")).toHaveAttribute("inert", "");
  await page.keyboard.press("Tab");
  await (0, import_test.expect)(page.getByRole("dialog", { name: "Evidence audit" }).locator(":focus")).toHaveCount(1);
  await page.keyboard.press("Escape");
  await (0, import_test.expect)(page.locator("main")).not.toHaveAttribute("inert", "");
  await page.reload();
  await (0, import_test.expect)(page.locator("html")).toHaveAttribute("data-theme", "dark");
});
(0, import_test.test)("imports JSON, cancels a pending run, and deletes its history entry", async ({ page }) => {
  await fixtures(page, { pending: true });
  await page.goto("/");
  await page.locator("input[type=file]").setInputFiles({ name: "synthetic-ui-fixture.json", mimeType: "application/json", buffer: Buffer.from(JSON.stringify(input)) });
  await (0, import_test.expect)(page.getByRole("textbox", { name: "Clinical vignette" })).toHaveValue(input.case_text);
  await page.getByRole("button", { name: "Analyze diagnostic case", exact: true }).click();
  await (0, import_test.expect)(page.getByText("Waiting for the local runtime", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Stop processing", exact: true }).first().click();
  await (0, import_test.expect)(page.getByText("Processing was cancelled. Any completed evidence remains in this record.")).toBeVisible();
  await page.getByRole("button", { name: /Delete synthetic-ui-fixture/ }).click();
  await page.getByRole("button", { name: "Delete conversation", exact: true }).click();
  await (0, import_test.expect)(page.getByRole("heading", { name: /Reason through a case/ })).toBeVisible();
});
(0, import_test.test)("validates missing candidate diagnoses without sending a partial case", async ({ page }) => {
  const fixture = await fixtures(page);
  await page.goto("/");
  await page.getByRole("textbox", { name: "Clinical vignette" }).fill("Synthetic UI fixture vignette.");
  await page.getByRole("button", { name: "Analyze diagnostic case", exact: true }).click();
  await (0, import_test.expect)(page.getByRole("alert")).toContainText("all four candidate diagnoses");
  await (0, import_test.expect)(page.getByRole("textbox", { name: "Candidate diagnosis A" })).toBeVisible();
  (0, import_test.expect)(fixture.submission()).toBeNull();
});
