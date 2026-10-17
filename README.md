# AEOS — AI Education Operations System

AEOS is an education operations prototype with a Next.js/React frontend, a
FastAPI backend, and versioned Supabase/PostgreSQL migrations.

The current teacher assessment review slice supports assessment intake, reading
an assessment and its saved results, and adding a teacher-entered review with an
optional score and a draft or complete status. Start at `/assessments`.
See [the workflow guide](docs/TEACHER_ASSESSMENT_REVIEW.md) for prerequisites,
reproduction commands, and the recorded verification limits.

The existing backend also exposes student and intervention-plan create/list/read
routes. Authenticated requests resolve the actor, role, and organization on the
server; teacher/admin writes use the shared tenant-scoped services. This is an
implementation description, not independent P0 security certification.

AI generation, diagnostic accuracy, rubric generation, standards alignment,
teacher analytics, parent communication, and improved educational outcomes are
not established by this slice. The repository does not demonstrate time savings,
learning gains, or pilot readiness. The
[MVP acceptance criteria](docs/MVP_ACCEPTANCE_CRITERIA.md) describe target behavior.

## Local development

Use Python 3.11+ and Node.js 22.13+ (the pinned Supabase frontend packages require
Node 22). Install the existing dependencies without changing the lockfile:

```bash
cd backend
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a separate terminal:

```bash
cd frontend
npm ci
npm run dev
```

Next.js proxies `/api` to `http://127.0.0.1:8000`. Set the server-side
`AEOS_API_URL` from `frontend/.env.example` if the backend lives elsewhere.
The assessment pages use the shared API client and this same-origin proxy.

Use `backend/.env.example` for backend configuration. Keep credentials in ignored
environment files or your environment's secret manager; service-role credentials
must stay server-side. A configured, migrated database and a supported Supabase
session are prerequisites for a real database run. This slice has no sign-in UI.
Follow the workflow guide for the existing session-token convention and the
separate synthetic-data verification path.
