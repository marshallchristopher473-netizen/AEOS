---
mode: agent
description: Verify or advance AEOS P0 Security using only reproducible, in-repo evidence.
---

# P0 Security — ground truth first

You are working on AEOS P0 Security. Read `.github/copilot-instructions.md` and `.github/instructions/backend-security.instructions.md` (and `supabase.instructions.md`, `frontend.instructions.md` if touching those areas) before doing anything else.

## Rule zero

**Trust git history, file contents, and executed command output over any prior claim** — including commit messages, PR descriptions, prior audit documents, and anything in this prompt that could be stale. This repository has repeatedly contained confident-sounding claims (specific commit SHAs, "route protection," "comprehensive tests") that did not correspond to anything actually present when checked. Check first.

## Before writing or claiming anything

1. Run:
   ```
   git status --short --branch
   git rev-parse HEAD
   git rev-parse origin/main
   git fetch origin '+refs/heads/*:refs/remotes/origin/*' '+refs/pull/*/head:refs/remotes/origin/pr/*'
   ```
2. If a specific commit SHA is referenced (by you, a prior message, or a file), verify it exists with `git cat-file -t <sha>` and `git log --all --oneline | grep <sha>` before treating it as real.
3. If the working tree is dirty, identify every changed file. If any of them are unrelated to the task at hand, say so before proceeding — don't fold unrelated changes into your work silently.
4. Read the actual source for the area you're about to touch. Do not infer behavior from filenames, docstrings, comments, or test names — read the executable code.

## Doing the work

- Run `scripts/verify_backend.sh` (or the individual pytest/compile commands) and paste the actual output. Never state a test passed without having run it in this session.
- Follow `.github/instructions/backend-security.instructions.md` for any route/auth change: every business route needs `get_current_actor`, tenant-scoped queries, server-derived identity fields, and both a same-tenant and a cross-tenant test.
- If you touch `backend/supabase/**`, follow `supabase.instructions.md` — new migration file, not an edit to an already-applied one, and reconcile against the live project rather than assuming the versioned file is current.
- Run `scripts/verify_p0_security.sh` and report its PENDING list honestly — don't summarize it as "passing" if PENDING items remain.

## Evidence

Save command transcripts and the exact commit SHA you tested under `evidence/p0-security/<candidate-sha>/`. Evidence tied to a SHA that isn't reachable from a fetched remote ref is not evidence — don't create a directory for a commit you haven't actually pushed and verified.

## Reporting

State plainly, per control: VERIFIED (with the command/output that proves it), NOT YET IMPLEMENTED, or CONTRADICTED BY EVIDENCE (if a claim and the actual code disagree). Never round "some controls pass" up to "P0 is done." Stop and report rather than guessing when something is ambiguous, when the working tree has unrelated changes, or when a required test can't actually run in this environment.
