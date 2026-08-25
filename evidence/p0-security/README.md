# P0 security evidence

Each subdirectory here is named for the exact 40-character commit SHA it verifies:

```
evidence/p0-security/<candidate-sha>/
```

Before creating one, confirm the SHA is real and reachable:

```bash
git cat-file -t <candidate-sha>
git log --all --oneline | grep <candidate-sha>
git branch --all --contains <candidate-sha>
```

An evidence directory for a SHA that isn't reachable from a fetched remote ref is not evidence of anything — don't create one preemptively for work that hasn't been committed and pushed yet.

## What belongs in a candidate's directory

- The exact commands run and their full output (not summarized), for at minimum:
  - `scripts/verify_backend.sh`
  - `scripts/verify_p0_security.sh`
  - any live-database checks performed (RLS state, cross-tenant attack tests), with the queries and results
- A short `SUMMARY.md` stating, per control, whether it's verified (with a pointer to the specific output proving it) or still pending — see `.github/instructions/backend-security.instructions.md` for the control list.
- No real student, IEP, 504, or other protected data, ever — synthetic/demo data only.
- No secrets (Supabase keys, JWTs from a real user, etc.) — redact before saving.

## What this directory is not

A place to record what a task *intended* to do, or to restate a prior claim. If you can't reproduce a result by running the command yourself right now, it doesn't go here.
