"""Browser review smoke test via Chrome DevTools; synthetic backend required.

Uses websockets already supplied by the backend's uvicorn[standard] dependency.
Signs in through /login against the loopback Supabase Auth fixture that the
synthetic backend starts (backend/tests/supabase_auth_fixture.py). No hosted
Supabase, AI quality, or pilot-readiness claim is made.
"""
import asyncio
import json
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

import websockets

BASE = "http://127.0.0.1:3000"
DEBUG = "http://127.0.0.1:9222"
AUTH = "http://127.0.0.1:9999"
# Synthetic logins defined by backend/tests/supabase_auth_fixture.py.
TEACHER = "teacher@synthetic.aeos.test"
SUPPORT = "support@synthetic.aeos.test"
PASSWORD = "synthetic-password"
STUDENT = "33333333-3333-4333-8333-333333333333"
OTHER_ASSESSMENT = "66666666-6666-4666-8666-666666666666"


def wait_for_services():
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        try:
            with urlopen(Request("http://127.0.0.1:8000/assessments", headers={"Authorization": "Bearer synthetic-teacher"}), timeout=2) as response:
                assert response.status == 200
            with urlopen(AUTH + "/auth/v1/.well-known/jwks.json", timeout=2) as response:
                assert response.status == 200
            with urlopen(BASE + "/login", timeout=2) as response:
                assert response.status == 200
            with urlopen(DEBUG + "/json/list", timeout=2) as response:
                pages = json.load(response)
            return next(page["webSocketDebuggerUrl"] for page in pages if page["type"] == "page")
        except (OSError, AssertionError, StopIteration):
            time.sleep(0.5)
    raise AssertionError("Synthetic backend, Auth fixture, built frontend, or Chrome failed to start")


class Browser:
    def __init__(self, socket):
        self.socket = socket
        self.sequence = 0
        self.errors = []

    async def call(self, method, **params):
        self.sequence += 1
        call_id = self.sequence
        await self.socket.send(json.dumps({"id": call_id, "method": method, "params": params}))
        while True:
            message = json.loads(await asyncio.wait_for(self.socket.recv(), timeout=15))
            if message.get("method") == "Runtime.exceptionThrown":
                self.errors.append(message["params"])
            if message.get("id") == call_id:
                assert "error" not in message, message
                return message.get("result", {})

    async def evaluate(self, expression):
        result = await self.call("Runtime.evaluate", expression=expression, returnByValue=True, awaitPromise=True)
        assert "exceptionDetails" not in result, result
        return result.get("result", {}).get("value")

    async def wait(self, expression, description):
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if await self.evaluate(expression):
                return
            await asyncio.sleep(0.1)
        body = await self.evaluate("document.body.innerText")
        raise AssertionError(f"Timed out waiting for {description}: {body}")

    async def navigate(self, path):
        await self.evaluate("window.__aeosNavigationMark = true")
        await self.call("Page.navigate", url=BASE + path)
        await self.wait("window.__aeosNavigationMark !== true && location.pathname === " + json.dumps(path), "fresh navigation")

    async def goto(self, path):
        """Navigate and wait for the new document, wherever redirects land."""
        await self.evaluate("window.__aeosNavigationMark = true")
        await self.call("Page.navigate", url=BASE + path)
        await self.wait("window.__aeosNavigationMark !== true && document.readyState === 'complete'", "fresh navigation")

    async def sign_in(self, email, password, next_path):
        await self.goto("/login?next=" + quote(next_path, safe=""))
        # The form renders client-side; React props on it mean handlers are live,
        # so submitting cannot fall back to a native GET that leaks the password.
        await self.wait("location.pathname === '/login' && Object.keys(document.querySelector('form') || {}).some(k => k.startsWith('__reactProps'))", "hydrated sign-in form")
        await self.fill("#email", email)
        await self.fill("#password", password)
        await self.submit()

    async def sign_out(self):
        await self.evaluate("Array.from(document.querySelectorAll('button')).find(b => b.textContent === 'Sign out').click()")
        await self.wait("location.pathname === '/login'", "signed-out redirect to /login")

    async def reload(self):
        await self.evaluate("window.__aeosReloadMark = true")
        await self.call("Page.reload")
        await self.wait("window.__aeosReloadMark !== true", "fresh reload")

    async def fill(self, selector, value):
        # Native setter plus bubbled events updates React's controlled inputs.
        await self.evaluate("""(() => {
          const element = document.querySelector(%s);
          if (!element) throw new Error('Missing form field');
          const setter = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(element), 'value').set;
          setter.call(element, %s);
          element.dispatchEvent(new Event('input', { bubbles: true }));
          element.dispatchEvent(new Event('change', { bubbles: true }));
        })()""" % (json.dumps(selector), json.dumps(value)))

    async def submit(self):
        await self.evaluate("document.querySelector('form').requestSubmit()")


async def main():
    socket_url = wait_for_services()
    async with websockets.connect(socket_url, max_size=2**22) as socket:
        browser = Browser(socket)
        await browser.call("Page.enable")
        await browser.call("Runtime.enable")
        await browser.goto("/assessments")
        await browser.wait("location.pathname === '/login' && new URLSearchParams(location.search).get('next') === '/assessments'", "signed-out redirect to /login")
        api = await browser.evaluate("fetch('/api/assessments').then(r => ({ status: r.status, redirected: r.redirected }))")
        assert api == {"status": 401, "redirected": False}, api
        print("PASS: signed out, pages redirect to /login with the return path and the API answers 401")

        await browser.sign_in(TEACHER, "not-the-password", "/assessments")
        await browser.wait("document.querySelector('.error')?.innerText.includes('Incorrect email or password.')", "generic sign-in refusal")
        assert await browser.evaluate("location.pathname === '/login'")
        await browser.fill("#password", PASSWORD)
        await browser.submit()
        await browser.wait("location.pathname === '/assessments' && document.body.innerText.includes('A Reading Screen')", "assessment list after sign-in")
        assert await browser.evaluate("document.cookie.includes('-auth-token')")
        print("PASS: wrong password refused generically; sign-in returns to the requested page with a cookie session")

        await browser.navigate("/assessments/new")
        await browser.wait("document.querySelector('#student_id') !== null", "assessment intake")
        await browser.fill("#student_id", STUDENT)
        await browser.fill("#title", "Synthetic browser assessment")
        await browser.fill("#assessment_type", "reading")
        await browser.submit()
        await browser.wait("document.querySelector('#review-summary') !== null", "created assessment review")
        await browser.wait("document.body.innerText.includes('No reviews recorded for this assessment.')", "empty reviews")
        path = await browser.evaluate("location.pathname")
        assert path.startswith("/assessments/") and path != "/assessments/new", path

        findings = "Synthetic findings <script>window.__aeosInjected=true</script>"
        await browser.fill("#review-score", "0")
        await browser.fill("#review-max-score", "10")
        await browser.fill("#review-summary", findings)
        await browser.fill("#review-status", "complete")
        await browser.submit()
        await browser.wait("document.body.innerText.includes('Completed review saved.')", "confirmed complete save")
        await browser.wait("document.querySelectorAll('.review-list li').length === 1", "single saved review")
        assert await browser.evaluate("document.querySelector('.review-list').innerText.includes('0 / 10')")
        assert not await browser.evaluate("window.__aeosInjected === true")

        await browser.reload()
        await browser.wait("document.querySelector('.review-list')?.innerText.includes('Synthetic findings')", "review after reload")
        assert await browser.evaluate("document.querySelector('.review-list').innerText.includes('complete')")
        print("PASS: create → complete review → save → reload; zero score and literal summary")

        await browser.fill("#review-summary", "Synthetic draft without a score")
        await browser.submit()
        await browser.wait("document.body.innerText.includes('Draft review saved.')", "confirmed draft save")
        await browser.reload()
        await browser.wait("document.querySelectorAll('.review-list li').length === 2", "both saved reviews after reload")
        assert await browser.evaluate("document.querySelector('.review-list').innerText.includes('Not recorded')")
        print("PASS: optional-score draft persists separately from completed review")

        await browser.fill("#review-score", "11")
        await browser.fill("#review-max-score", "10")
        await browser.fill("#review-summary", "Invalid unsaved review")
        await browser.submit()
        await browser.wait("document.querySelector('[role=alert]')?.innerText.includes('cannot exceed')", "score-range validation")
        assert await browser.evaluate("document.querySelectorAll('.review-list li').length === 2")
        await browser.evaluate("Array.from(document.querySelectorAll('button')).find(b => b.textContent === 'Discard unsaved review').click()")
        assert await browser.evaluate("document.querySelector('#review-summary').value === ''")
        print("PASS: invalid score is not saved; discard clears unsaved fields")

        await browser.sign_out()
        await browser.sign_in(SUPPORT, PASSWORD, path)
        await browser.wait("location.pathname === %s && document.querySelector('#review-summary') !== null" % json.dumps(path), "support read access")
        await browser.fill("#review-summary", "Synthetic forbidden write")
        await browser.submit()
        await browser.wait("document.querySelector('[role=alert]')?.innerText.includes('teacher or admin')", "write-role denial")
        assert await browser.evaluate("document.querySelector('#review-summary').value === 'Synthetic forbidden write'")
        assert await browser.evaluate("document.querySelectorAll('.review-list li').length === 2")
        print("PASS: forbidden save preserves form; no false success or new review")

        await browser.sign_out()
        await browser.sign_in(TEACHER, PASSWORD, "/assessments/" + OTHER_ASSESSMENT)
        await browser.wait("document.querySelector('[role=alert]')?.innerText.includes('Assessment not found')", "cross-tenant read denial")
        assert await browser.evaluate("document.querySelector('#review-summary') === null")
        print("PASS: cross-tenant assessment shows no review form")

        await browser.sign_out()
        await browser.goto(path)
        await browser.wait("location.pathname === '/login' && new URLSearchParams(location.search).get('next') === %s" % json.dumps(path), "signed-out redirect")
        assert await browser.evaluate("document.querySelector('#review-summary') === null")
        assert not browser.errors, browser.errors
        print("PASS: after sign-out the review page redirects to /login; no browser runtime exceptions")


if __name__ == "__main__":
    asyncio.run(main())
