# Pilot Sign-In Setup and Live Isolation Check

How to connect the teacher portal (`frontend/`) to Supabase Auth and the AEOS
API (`backend/`), then prove tenant isolation against a real deployment.
**Use synthetic students only.** Real student data stays blocked until step 5
passes on the deployed system.

## 1. Supabase project settings

1. Authentication → Sign In / Providers → Email: enabled.
2. Authentication → Sign In / Providers: **turn off "Allow new users to sign up"**.
   Accounts are provisioned by an AEOS admin; a self-signed-up account has no
   AEOS user row and is refused by the API (403) anyway.
3. Apply `backend/supabase/migrations/001`–`004` in order.

## 2. Environment

| File | Variable | Value |
|---|---|---|
| `backend/.env` | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | from Supabase → Project Settings → API |
| `backend/.env` | `CORS_ALLOWED_ORIGINS` | exact portal origin(s), e.g. `https://portal.example.org` — no wildcards, no paths |
| `frontend/.env.local` | `NEXT_PUBLIC_API_URL` | the API base URL |
| `frontend/.env.local` | `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` | from Supabase → Project Settings → API |

The service-role key belongs **only** in the backend. The anon key is public by
design; tenant RLS (migration 002 onward) is what limits direct database access.

## 3. Provision two synthetic organizations

For each teacher: create the login in Authentication → Users → Add user, copy
its user UID, then link it to an AEOS organization in the SQL editor:

```sql
-- Organization A and B (synthetic)
insert into organizations (id, name, type) values
  (gen_random_uuid(), 'Pilot Org A (synthetic)', 'pilot'),
  (gen_random_uuid(), 'Pilot Org B (synthetic)', 'pilot');

-- One teacher per organization; auth_user_id = the Supabase user UID
insert into users (id, organization_id, auth_user_id, email, full_name, role)
select gen_random_uuid(), id, '<UID-of-teacher-A>', 'teacher-a@example.org', 'Teacher A', 'teacher'
from organizations where name = 'Pilot Org A (synthetic)';

insert into users (id, organization_id, auth_user_id, email, full_name, role)
select gen_random_uuid(), id, '<UID-of-teacher-B>', 'teacher-b@example.org', 'Teacher B', 'teacher'
from organizations where name = 'Pilot Org B (synthetic)';
```

## 4. Run locally

```bash
cd backend && uvicorn app.main:app --port 8000
cd frontend && npm run dev   # http://localhost:3000
```

## 5. Live check (definition of done)

| # | Action | Expected |
|---|---|---|
| 1 | Sign in as Teacher A, add a student "Alpha Synthetic" | Lands on `/students`; student appears |
| 2 | Sign out, sign in as Teacher B, open `/students` | **Zero** of Org A's students |
| 3 | As Teacher B, open `/students/<Alpha's id>` directly | Error (404), no data |
| 4 | Sign out, open `/students` | "Please sign in to view students." |
| 5 | Wrong password | "Sign-in failed. Check your email and password." |
| 6 | Set Org A `status = 'suspended'`, reload as Teacher A | Error (403); set back to `active` afterwards |

Record the date, deployment URL and result of each row before any real pilot data.
