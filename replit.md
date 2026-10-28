# AEOS — AI Education Operations System

## Overview

An education operations prototype. The current slice lets teachers read
assessments and add teacher-entered reviews. AI generation, improved educational
outcomes, parent communication, and pilot readiness have not been demonstrated.
See `docs/TEACHER_ASSESSMENT_REVIEW.md` for the workflow and verification limits.

**Stack:**
- Backend: FastAPI (Python 3.12) served with Uvicorn
- Database: Supabase (PostgreSQL + pgvector)
- Frontend: React / Next.js; assessment and student pages exist
- AI: Claude API, RAG pipelines (planned)

## Running the app

The backend can be started with:

```
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API is available at port **8000** (console output type).

Key endpoints:
- `GET /health` — health check
- `POST /assessments` — create an assessment
- `GET /assessments/{id}` — retrieve an assessment
- `GET /students/{id}` — retrieve a student
- `GET /assessment-results?assessment_id={id}` — read reviews for an accessible assessment
- `POST /assessment-results` — save a teacher-entered review

Start the frontend separately with `cd frontend && npm ci && npm run dev`.
Open `/assessments`; Next.js proxies its `/api` requests to the backend using
`AEOS_API_URL` (default `http://127.0.0.1:8000`). A supported session and database
configuration are required; this slice has no sign-in page.

## Required secrets

Set in Replit Secrets:
- `SUPABASE_URL` — Supabase project URL (env var, shared)
- `SUPABASE_ANON_KEY` — Supabase anon/public key
- `SUPABASE_SERVICE_ROLE_KEY` — Supabase service role key (admin access)

## Project structure

```
backend/       FastAPI app (entry: backend/app/main.py)
frontend/      React/Next.js assessment and student pages
agents/        Empty placeholder on main; separate draft PRs contain agent work
database/      Empty placeholder; migrations live in backend/supabase/migrations/
```

## User preferences

- Keep the existing project structure and stack.
