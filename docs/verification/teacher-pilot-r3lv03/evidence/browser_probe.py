"""Independent keyboard/persistence/failure/overflow probe of the PR #35 built
frontend against the candidate's loopback fixture API. Synthetic data only.

The fixture API keeps state in memory, so "persistence" here means the API
returns the saved record to a reloaded page and to a fresh browser context.
It is not evidence of durable hosted-database storage.
"""
import json
import sys

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:3000"
ASSESSMENT = "55555555-5555-4555-8555-555555555555"
URL = f"{BASE}/assessments/{ASSESSMENT}"
TOKEN = "synthetic-teacher"
results = {}


def record(name, ok, detail=""):
    results[name] = {"pass": bool(ok), "detail": detail}
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


def tab_to(page, predicate_js, limit=80):
    """Press Tab until document.activeElement satisfies predicate_js."""
    for _ in range(limit):
        page.keyboard.press("Tab")
        if page.evaluate(f"(() => {{ const el = document.activeElement; return !!el && ({predicate_js}); }})()"):
            return True
    return False


def new_page(browser, viewport=None):
    ctx = browser.new_context(viewport=viewport or {"width": 1280, "height": 900})
    ctx.add_init_script(f"localStorage.setItem('aeos_access_token', '{TOKEN}')")
    page = ctx.new_page()
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    return ctx, page, errors


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    ctx, page, console_errors = new_page(browser)
    decision_keys = []
    page.on("request", lambda r: decision_keys.append(r.headers.get("idempotency-key"))
            if r.method == "POST" and "/decisions" in r.url else None)

    page.goto(URL)
    page.wait_for_selector("#ai-response")
    record("ai_label_visible", page.get_by_text("It does not score, diagnose, or decide anything").count() == 1)

    # --- keyboard-only draft request --------------------------------------
    ok = tab_to(page, "el.id === 'ai-response'")
    page.keyboard.type("The plant grew taller because it received more sunlight each day, as shown in the table.")
    ok &= tab_to(page, "el.type === 'checkbox' && el.closest('form')")
    page.keyboard.press("Space")
    ok &= tab_to(page, "el.tagName === 'BUTTON' && el.type === 'submit'")
    page.keyboard.press("Enter")
    page.wait_for_selector("li.ai-draft textarea", timeout=15000)
    draft_label = page.locator("li.ai-draft p strong").first.inner_text()
    record("keyboard_request_draft", ok, f"draft status label={draft_label!r}")

    # --- save failure retains teacher text, then retry reuses key ---------
    revised = "Teacher revision: name the data table row that shows the height change."
    ok = tab_to(page, "el.id && el.id.startsWith('approved-')")
    page.keyboard.press("Control+A")
    page.keyboard.type(revised)
    page.route("**/decisions", lambda route: route.abort())
    ack = page.locator("li.ai-draft input[type=checkbox]")
    if ack.count():
        ok &= tab_to(page, "el.type === 'checkbox' && !!el.closest('li.ai-draft')")
        page.keyboard.press("Space")
    ok &= tab_to(page, "el.tagName === 'BUTTON' && el.textContent.includes('Save my revision')")
    page.keyboard.press("Enter")
    page.wait_for_selector("li.ai-draft [role=alert]", timeout=10000)
    kept = page.locator("li.ai-draft textarea").input_value()
    record("save_failure_shows_error", True, page.locator("li.ai-draft [role=alert]").inner_text()[:80])
    record("save_failure_retains_text", kept == revised)
    page.unroute("**/decisions")
    ok &= tab_to(page, "el.tagName === 'BUTTON' && el.textContent.includes('Save my revision')")
    page.keyboard.press("Enter")
    page.wait_for_selector("li.ai-draft [role=status]:has-text('revised')", timeout=10000)
    record("keyboard_save_revision", ok)
    real_keys = [k for k in decision_keys if k]
    record("retry_reuses_idempotency_key", len(real_keys) >= 2 and len(set(real_keys)) == 1,
           f"keys_sent={len(real_keys)} distinct={len(set(real_keys))}")

    # --- hard reload + fresh session --------------------------------------
    page.reload(wait_until="networkidle")
    page.wait_for_selector("li.ai-draft")
    after_reload = page.locator("li.ai-draft [role=status]").first.inner_text()
    record("persists_after_hard_reload", "revised" in after_reload, after_reload)
    ctx2, page2, _ = new_page(browser)
    page2.goto(URL)
    page2.wait_for_selector("li.ai-draft")
    fresh = page2.locator("li.ai-draft [role=status]").first.inner_text()
    record("persists_in_fresh_session", "revised" in fresh, fresh)
    record("no_console_errors_except_forced_abort",
           all("Failed to fetch" in e or "net::ERR_FAILED" in e for e in console_errors), str(console_errors)[:200])
    html = page.content()
    record("no_secret_in_page", "synthetic-fixture-key" not in html and "service_role" not in html.lower())

    # --- tenant separation through the UI ---------------------------------
    ctx3 = browser.new_context()
    ctx3.add_init_script("localStorage.setItem('aeos_access_token', 'synthetic-other-tenant')")
    page3 = ctx3.new_page()
    page3.goto(URL)
    page3.wait_for_timeout(2500)
    record("other_tenant_sees_no_draft", page3.locator("li.ai-draft").count() == 0,
           page3.locator("main").inner_text()[:120].replace("\n", " "))

    # --- mobile overflow at 375px -----------------------------------------
    for path in [f"/assessments/{ASSESSMENT}", "/assessments", "/assessments/new", "/students", "/students/new"]:
        mctx, mpage, _ = new_page(browser, {"width": 375, "height": 812})
        mpage.goto(BASE + path, wait_until="networkidle")
        mpage.wait_for_timeout(800)
        sw, iw = mpage.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
        record(f"mobile_no_overflow {path}", sw <= iw, f"scrollWidth={sw} innerWidth={iw}")
        if path == f"/assessments/{ASSESSMENT}":
            mpage.screenshot(path=sys.argv[1] + "/mobile-assessment-375.png", full_page=True)
        mctx.close()

    browser.close()

json.dump(results, open(sys.argv[1] + "/browser_probe_result.json", "w"), indent=2)
print("failed:", [k for k, v in results.items() if not v["pass"]])
