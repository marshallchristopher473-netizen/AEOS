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
must stay server-side. A configured, migrated database and a Supabase project
are prerequisites for a real database run. The workflow guide also describes the
separate synthetic-data verification path.

## Running the teacher portal locally (sign-in)

Use synthetic data only. Do not create accounts or records for real students.
`<project-ref>` below is your Supabase project's reference ID.

Before you start, check both of these; either one blocks sign-in:

- **Asymmetric JWT signing keys** (Project Settings → JWT Keys shows an ES256
  or RS256 key). The backend refuses tokens signed with the legacy HS256
  secret, so sign-in would succeed but every API call would return 401.
- **Migrations 001–007 applied** (`backend/supabase/migrations/`). The Table
  Editor should list `organizations`, `users`, `students`, `assessments`, and
  `ai_feedback_drafts`.

1. Backend: `cp backend/.env.example backend/.env` and set:
   - `SUPABASE_URL=https://<project-ref>.supabase.co`
   - `SUPABASE_SERVICE_ROLE_KEY` (server-side only; never in the frontend,
     chat, or a commit)
   - `SUPABASE_JWKS_URL=https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json`
   - `SUPABASE_JWT_ISSUER=https://<project-ref>.supabase.co/auth/v1`

   The browser reaches the API through the same-origin `/api` proxy, so the
   backend needs no CORS configuration. Then:
   ```bash
   cd backend && pip install -r requirements.txt
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
2. Frontend: `cp frontend/.env.example frontend/.env.local` and set
   `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` (the public
   anon key, never the service-role key). Then:
   ```bash
   cd frontend && npm ci && npm run dev
   ```
3. Create a test teacher:
   - Supabase dashboard → Authentication → Users → Add user (email + password,
     auto-confirm). Copy the user's UID.
   - In the SQL editor, link that login to an AEOS organization. A login with
     no active `users` row, or an inactive organization, is refused by the API.
     ```sql
     INSERT INTO organizations (id, name, type)
     VALUES (gen_random_uuid(), 'Synthetic Pilot Org', 'pilot')
     RETURNING id;

     INSERT INTO users (id, organization_id, auth_user_id, email, full_name, role)
     VALUES (gen_random_uuid(), '<org id from above>', '<auth user UID>',
             'teacher@example.test', 'Test Teacher', 'teacher');
     ```
4. Open http://localhost:3000. Signed-out visitors are redirected to `/login`;
   after sign-in you land on Students. "Sign out" is in the header.
5. A new organization has no records, so walk the review flow end to end:
   create a synthetic student, create an assessment for that student, save a
   review, reload the page and confirm the review is still there, then sign
   out. Done when every step completes with no error message on the page and
   no red errors in the browser console.

If it fails:

| Symptom | Likely cause |
|---|---|
| Signed in, but pages say "Please sign in again to continue." | Legacy HS256 signing keys, or a wrong `SUPABASE_JWKS_URL` or `SUPABASE_JWT_ISSUER` |
| "Authenticated identity has no active AEOS user" | No active `users` row for the login, or its `auth_user_id` does not match the auth user's UID |
| "Sign-in is not configured" | `frontend/.env.local` is missing, or the dev server was not restarted after creating it |

Checks: `npm run lint`, `npx tsc --noEmit`, `npm test`, and `npm run build` in
`frontend/`; `python -m pytest tests/ -q` in `backend/`.

