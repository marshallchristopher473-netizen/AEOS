# AEOS — repository-wide agent instructions

AEOS is one unified platform (not a collection of separate products). Priority order for all work: **Completion → Validation → Monetization → Scaling**.

## Current gate: P0 Security is NOT complete

Do not build product features (GradeFreed AI, literacy, SPED/dyslexia/dyscalculia modules, parent tools, UI redesign, billing, analytics, new AI models) until P0 Security passes. If you are unsure whether a task falls under P0 Security, treat it as frozen and ask.

**Verify P0 status yourself before trusting any prior claim in an issue, PR description, or commit message** — including this file, if it hasn't been kept current. Run `scripts/verify_p0_security.sh` and read its PENDING items; do not infer completion from filenames, comments, SQL text, mocks, or unexecuted tests. This repository's history contains multiple instances of confidently-worded commit messages and audit claims that did not correspond to anything actually in the repository — always check `git log`, `git cat-file`, and the actual source, not the claim.

## Architecture

- **Backend**: FastAPI, `backend/app/` — `api/` (routers), `core/` (auth, config, dependencies), `models/` (Pydantic schemas), `services/` (Supabase client wrappers).
- **Frontend**: Next.js 14 / React 18 / TypeScript, `frontend/src/app/`.
- **Database**: Supabase/Postgres, versioned migrations in `backend/supabase/migrations/`. The live Supabase project (`AEOS-MVP`) is the actual authority for what's deployed — it can and has drifted from the versioned migration file. Reconcile, don't assume either side is current.

## Build, test, validate

Prefer the scripts over improvising commands — they encode what's actually been verified to work in this repo:

- `scripts/verify_environment.sh` — one-time/idempotent setup (backend venv + pinned deps, frontend `npm ci`). Runs automatically on Codespace creation via `.devcontainer/devcontainer.json`.
- `scripts/verify_backend.sh` — compile checks, import checks, full `pytest` run. Mirrors `.github/workflows/backend.yml`.
- `scripts/verify_frontend.sh` — `npm ci` + `npm run build`. Does **not** run `npm run lint` — see the note in that script for why (no committed ESLint config; `next lint` requires interactive setup).
- `scripts/verify_p0_security.sh` — the P0 gate. Prints an honest PASS/PENDING matrix; do not treat "the script exited 0" as "P0 is done" — read the PENDING lines.

Never claim a test passed without having run it in this session and captured the output. Never claim a commit exists, was pushed, or is part of history without confirming its SHA against `git log --all` / a fetched remote ref.

## Path-specific instructions

See `.github/instructions/` for scoped guidance:
- `backend-security.instructions.md` — applies to `backend/app/**`
- `supabase.instructions.md` — applies to `backend/supabase/**`
- `frontend.instructions.md` — applies to `frontend/**`

## Evidence

P0 security work should land its verification evidence (command output, test counts, exact SHAs) under `evidence/p0-security/<candidate-sha>/` — see `evidence/p0-security/README.md`. Evidence tied to a SHA that doesn't exist on a fetched remote ref is not evidence.

## Non-destructive defaults

Do not force-push, rewrite history, delete branches, or run destructive git operations without explicit human approval in the current request. Do not commit or push without being asked to. Do not weaken a test or a security control to make a check pass.
