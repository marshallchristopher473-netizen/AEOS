"""Chromium walk-through of the AI feedback panel against the synthetic fixture
server (deterministic provider). Records each check; no AI quality claim.

Prerequisites: `npm run build` in frontend/, then
  (cd backend && AEOS_SYNTHETIC_AI_FEEDBACK=1 python -m tests.ai_feedback_fixture_server) &
  (cd frontend && AEOS_API_URL=http://127.0.0.1:8000 npx next start -H 127.0.0.1 -p 3000) &
  python docs/evidence/ai-feedback/browser_ai_feedback.py /tmp/ai-feedback-panel.png
Requires the `playwright` Python package and a local Chromium (path below).
"""
import json, sys
from playwright.sync_api import sync_playwright, expect

BASE = "http://127.0.0.1:3000"
ASSESSMENT = "55555555-5555-4555-8555-555555555555"
fx = json.load(open("/home/user/AEOS/backend/tests/fixtures/ai_feedback/synthetic_ela.json"))
R01, R03, R05 = (fx["responses"][k]["text"] for k in ("R01", "R03", "R05"))
results = []

def check(name, fn):
    try:
        fn(); results.append((name, "PASS"))
    except Exception as exc:  # noqa: BLE001
        results.append((name, f"FAIL: {str(exc).splitlines()[0][:160]}"))

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args=["--no-sandbox"])
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(BASE + "/assessments")
    page.evaluate("localStorage.setItem('aeos_access_token', 'synthetic-teacher')")
    page.goto(f"{BASE}/assessments/{ASSESSMENT}")
    panel = page.locator("section[aria-labelledby='ai-feedback-heading']")

    check("panel renders with synthetic-only notice and empty state", lambda: (
        expect(panel.get_by_role("heading")).to_have_text("AI feedback draft (synthetic responses only)"),
        expect(panel.get_by_text("No AI drafts for this assessment yet.")).to_be_visible()))

    def unconfirmed():
        panel.get_by_label("Synthetic short response").fill(R01)
        panel.get_by_role("button", name="Draft feedback").click()
        expect(panel.get_by_role("alert")).to_contain_text("Confirm that this is a synthetic response")
    check("draft refused until synthetic data is confirmed", unconfirmed)

    def draft():
        panel.get_by_label("This is a synthetic response").check()
        panel.get_by_role("button", name="Draft feedback").click()
        for text in ("Draft ready for review", "Strength: You open with a clear statement.",
                     "Evidence from the response:", "Removed: the AI cited text that is not in the response.",
                     "Feedback that cited text not found in the response was removed.", "No teacher decision yet.",
                     "Rubric RUB-CER3 v0.1 · prompt aeos-ela-feedback-draft-v1 · model deterministic-fixture"):
            try:
                expect(panel.locator("p, ul.ai-flags > li", has_text=text).first).to_be_visible()
            except Exception as exc:
                raise AssertionError(f"{text!r}: {str(exc).splitlines()[0]}")
    check("draft shows criterion feedback, verified evidence, removed invented evidence, flags, versions", draft)

    item = panel.locator("li.ai-draft").first
    def accept_needs_ack():
        item.get_by_role("button", name="Accept draft as written").click()
        expect(item.get_by_role("alert")).to_contain_text("Confirm that you reviewed the flags")
    check("accept blocked until flags are acknowledged", accept_needs_ack)

    def accept():
        item.get_by_label("I reviewed the flags above.").check()
        item.get_by_role("button", name="Accept draft as written").click()
        expect(item.get_by_text("Teacher-approved feedback saved.")).to_be_visible()
        expect(item.get_by_text("Current teacher decision: accepted")).to_be_visible()
    check("explicit accept saves teacher-approved feedback", accept)

    def revise():
        box = item.get_by_label("Feedback text (edit to revise)")
        box.fill(box.input_value() + "\nTeacher note: add a second detail.")
        expect(item.get_by_role("button", name="Accept draft as written")).to_be_disabled()
        item.get_by_role("button", name="Save my revision").click()
        expect(item.get_by_text("Current teacher decision: revised")).to_be_visible()
    check("edited text can only be saved as a revision; latest decision is current", revise)

    def reload_persists():
        page.reload()
        expect(panel.locator("li.ai-draft").first.get_by_text("Current teacher decision: revised")).to_be_visible()
    check("draft and decision persist across reload", reload_persists)

    def injection():
        panel.get_by_label("Synthetic short response").fill(R05)
        panel.get_by_label("This is a synthetic response").check()
        panel.get_by_role("button", name="Draft feedback").click()
        expect(panel.get_by_text("looks like instructions to the AI").first).to_be_visible()
    check("embedded-instruction response is flagged to the teacher", injection)

    def abstained():
        panel.get_by_label("Synthetic short response").fill(R03)
        panel.get_by_role("button", name="Draft feedback").click()
        first = panel.locator("li.ai-draft").first
        expect(first.get_by_text("AI abstained")).to_be_visible()
        expect(first.get_by_role("button", name="Accept draft as written")).to_be_disabled()
    check("very short response yields an abstention that cannot be accepted", abstained)

    def support_denied():
        page.evaluate("localStorage.setItem('aeos_access_token', 'synthetic-support')")
        page.reload()
        first = panel.locator("li.ai-draft").first
        expect(first).to_be_visible()
        first.get_by_role("button", name="Reject draft").click()
        expect(first.get_by_role("alert")).to_contain_text("teacher or admin")
    check("support role can read but not decide", support_denied)

    def other_tenant():
        page.evaluate("localStorage.setItem('aeos_access_token', 'synthetic-other-tenant')")
        page.goto(f"{BASE}/assessments/{ASSESSMENT}")
        expect(page.locator("main [role=alert]")).to_contain_text("Assessment not found")
    check("other tenant cannot open the assessment or its drafts", other_tenant)

    page.evaluate("localStorage.setItem('aeos_access_token', 'synthetic-teacher')")
    page.goto(f"{BASE}/assessments/{ASSESSMENT}")
    panel.locator("li.ai-draft").first.wait_for()
    page.screenshot(path=sys.argv[1], full_page=True)
    results.append(("no uncaught page errors", "PASS" if not errors else f"FAIL: {errors[:2]}"))
    browser.close()

for name, outcome in results:
    print(f"{outcome[:4]}  {name}" + ("" if outcome == "PASS" else f"  -> {outcome}"))
print(f"{sum(o == 'PASS' for _, o in results)}/{len(results)} passed")
