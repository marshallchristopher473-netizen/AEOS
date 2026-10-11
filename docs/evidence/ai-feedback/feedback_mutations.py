"""Ad-hoc mutation check for the AI feedback slice (docs/evidence/ai-feedback).

Each mutant must make the named tests fail; a passing suite means the mutant
SURVIVED. Usage from the repository root, with a disposable PostgreSQL:

    AEOS_TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres \
        python docs/evidence/ai-feedback/feedback_mutations.py . "$(command -v python)"
"""
import json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

REPO = Path(sys.argv[1])
PY = sys.argv[2]
DB = os.environ.get("AEOS_TEST_DATABASE_URL")
APP = ["tests/test_ai_feedback.py", "tests/test_ai_feedback_provider.py"]
DBT = ["tests/test_ai_feedback_rls.py"]
S = "backend/app/services/ai_feedback/"
M = "backend/supabase/migrations/006_ai_feedback_drafts.sql"
MUTANTS = [
 ("evidence verification disabled", S+"validation.py", "    if start < 0:\n        return None", "    if start < 0:\n        start = 0", APP),
 ("prohibited-inference scan disabled", S+"validation.py", "if text and find_prohibited_language(text):", "if False:", APP),
 ("untrusted block escaping removed", S+"prompt.py", 'return value.replace("&", "\\\\u0026").replace("<", "\\\\u003c").replace(">", "\\\\u003e")', "return value", APP),
 ("criterion coverage check removed", S+"validation.py", '        raise OutputRejected("criteria_mismatch")', "        pass", APP),
 ("org allowlist check removed", S+"service.py", "if actor.organization_id not in self.settings.organization_allowlist:", "if False:", APP),
 ("accept-text equality check removed", S+"service.py", "if payload.approved_text != draft_text:", "if False:", APP),
 ("flag acknowledgement check removed", S+"service.py", "and not payload.review_flags_acknowledged", "and False", APP),
 ("idempotent replay removed", S+"service.py", "        existing = self._existing_request(actor, request_key)\n        if existing is not None:", "        existing = self._existing_request(actor, request_key)\n        if False:", APP),
 ("budget outcome ignored", S+"service.py", "            raise api_error(status.HTTP_429_TOO_MANY_REQUESTS, outcome)", "            outcome = 'reserved'", APP),
 ("assessment not tenant-scoped", S+"service.py", 'self.client, "assessments", payload.assessment_id, actor.organization_id, "Assessment not found"', 'self.client, "assessments", payload.assessment_id, (self.client.table("assessments").select("*").eq("id", payload.assessment_id).execute().data or [{}])[0].get("organization_id", ""), "Assessment not found"', APP),
 ("adapter base_url not pinned", S+"provider.py", "                base_url=settings.base_url,\n", "", APP),
 ("adapter leaks provider message", S+"provider.py", "        return ProviderError()\n", "        return ProviderError(str(exc))\n", APP),
 ("drafts append-only trigger removed", M, "CREATE TRIGGER ai_feedback_drafts_append_only\nBEFORE UPDATE ON public.ai_feedback_drafts\nFOR EACH ROW\nEXECUTE FUNCTION public.aeos_reject_ai_feedback_update();", "", DBT),
 ("drafts select policy permissive", M, "USING (public.aeos_has_org_access(ai_feedback_drafts.organization_id));", "USING (true);", DBT),
 ("reservation advisory lock removed", M, "    PERFORM pg_advisory_xact_lock(\n        hashtextextended('aeos_ai_feedback:' || new_request.organization_id::text, 0)\n    );", "", DBT),
 ("draft audit trigger removed", M, "CREATE TRIGGER ai_feedback_drafts_audit\nAFTER INSERT ON public.ai_feedback_drafts\nFOR EACH ROW\nEXECUTE FUNCTION public.aeos_audit_ai_feedback_draft();", "", DBT),
 ("request integrity trigger removed", M, "CREATE TRIGGER ai_feedback_requests_integrity\nBEFORE INSERT ON public.ai_feedback_requests\nFOR EACH ROW\nEXECUTE FUNCTION public.aeos_ai_feedback_request_integrity();", "", DBT),
]
results = []
for name, path, old, new, suite in MUTANTS:
    work = Path(tempfile.mkdtemp(prefix="fbmut_"))
    shutil.copytree(REPO / "backend", work / "backend", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(REPO / "frontend" / "src", work / "frontend" / "src")
    target = work / path
    text = target.read_text()
    if text.count(old) != 1:
        results.append({"mutant": name, "result": "INVALID (anchor count %d)" % text.count(old)}); continue
    target.write_text(text.replace(old, new))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    if suite is DBT:
        env["AEOS_REQUIRE_RLS_TESTS"] = "1"
    t = time.time()
    p = subprocess.run([PY, "-m", "pytest", *suite, "-q", "-p", "no:cacheprovider", "-W", "ignore::DeprecationWarning", "--tb=no"],
                       cwd=work / "backend", env=env, capture_output=True, text=True, timeout=600)
    tail = (p.stdout.strip().splitlines() or [""])[-1]
    results.append({"mutant": name, "exit": p.returncode, "summary": tail,
                    "result": "KILLED" if p.returncode == 1 and " failed" in tail else "SURVIVED" if p.returncode == 0 else "INVALID",
                    "seconds": round(time.time() - t, 1)})
    shutil.rmtree(work)
print(json.dumps(results, indent=1))
print("killed", sum(r["result"] == "KILLED" for r in results), "of", len(results))
