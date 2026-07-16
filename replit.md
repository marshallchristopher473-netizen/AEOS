# AEOS — AI Education Operations System

## Overview

An AI-powered education operations platform covering teacher productivity, student learning outcomes, parent engagement, assessment intelligence, and special education workflows.

**Stack:**
- Backend: FastAPI (Python 3.12) served with Uvicorn
- Database: Supabase (PostgreSQL + pgvector)
- Frontend: React / Next.js (not yet built)
- AI: Claude API, RAG pipelines (planned)

## Running the app

The backend workflow is configured and runs automatically:

```
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API is available at port **8000** (console output type).

Key endpoints:
- `GET /health` — health check
- `POST /assessments` — create an assessment
- `GET /assessments/{id}` — retrieve an assessment
- `GET /students/{id}` — retrieve a student

## Required secrets

Set in Replit Secrets:
- `SUPABASE_URL` — Supabase project URL (env var, shared)
- `SUPABASE_ANON_KEY` — Supabase anon/public key
- `SUPABASE_SERVICE_ROLE_KEY` — Supabase service role key (admin access)

## Project structure

```
backend/       FastAPI app (entry: backend/app/main.py)
frontend/      React/Next.js (empty — not yet scaffolded)
agents/        AI agent workflows (empty — planned)
database/      Schema / migrations (empty — planned)
```

## User preferences

- Keep the existing project structure and stack.
