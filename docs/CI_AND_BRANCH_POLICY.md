# CI and branch policy

What each check gates, what it does not, and which gaps are structural.

Written after a sequence of CI changes (#68, #69, #70) that began as "fix a red
check" and turned out to be about a repeating pattern: **a check that runs and
cannot affect the outcome.** Four instances are catalogued below. The pattern is
worth naming because each instance looked different and each one was invisible
until something forced it into view.

---

## The pipeline

`.github/workflows/p0-backend-tests.yml`, workflow name **P0 Security
Candidate**. Three jobs run on every pull request into `main`:

| Job | What it proves |
| --- | --- |
| `backend-tests` | Backend imports, schemas and the FastAPI test suite |
| `rls-enforcement` | Applies the Supabase migrations to a real PostgreSQL instance and proves cross-tenant denial, then runs the M01–M18 mutation suite to prove the security tests can actually fail |
| `frontend-validation` | `npm ci` → dependency tree → lint → type-check → build → dependency audit |

`rls-enforcement` is the check with the most teeth: it breaks each tenant
control in a throwaway copy and asserts the suite notices, which catches a
policy that keeps its name while losing its effect.

### `frontend-validation` step order

```
install → verify tree → lint → type-check → build → audit
```

The audit runs **last**, deliberately. Fail-fast normally puts cheap checks
first, but that logic inverts here: `npm audit` is cheap and advisory while the
build is expensive and load-bearing. A failing step aborts the job, so an audit
in front of the build hides the checks that catch real regressions. See
instance 1 below.

### `npm audit` thresholds

`npm audit --audit-level=X` affects **only the exit code**. Every advisory at
every severity is printed regardless; the threshold decides which ones fail the
job, not which ones you see.

The gate is:

```yaml
- name: Audit dependencies (fails on high+, prints all advisories)
  run: npm audit --audit-level=high
```

Two decisions are embedded there:

- **Full tree, not `--omit=dev`.** Excluding dev dependencies would encode a
  "what ships to users" threat model. The risk being gated is execution in the
  CI runner: a compromised lint or build dependency runs with whatever tokens
  the job holds, and install and build hooks are a known attack surface. "Does
  not ship" and "cannot hurt you" are not the same claim.
- **`high`, not `low`.** A moderate advisory in lint tooling is worth knowing
  about — it is still printed — but is not worth blocking a merge on. A gate
  that is red for reasons nobody intends to act on trains people to ignore red,
  which costs more than it protects.

If you are tempted to add a separate "report" step, ask what it reports that
the gate does not. In this repo the answer is nothing. See instance 3.

---

## Branch protection

**Status: not applied.** `main` currently has no protection
(`GET /repos/:owner/:repo/branches/main` → `"protected": false`).

This must be set in **Settings → Branches** by a human with admin rights. The
GitHub App used for automation here has repository `admin: true` on the account
but is refused the branch-protection endpoints with
`"Resource not accessible by integration"` — the App installation lacks the
Administration scope. No PR or API call from automation can apply it.

### Checklist

- [ ] Require status checks to pass before merging, and require branches to be
      up to date:
  - [ ] `frontend-validation`
  - [ ] `backend-tests`
  - [ ] `rls-enforcement`
- [ ] **Do not allow bypassing the above settings** — without this, admins keep
      the hole open by design, which is the state this checklist exists to fix.
- [ ] Restrict force pushes.
- [ ] Restrict branch deletion.
- [ ] **Do not require approvals.** With a sole maintainer this deadlocks the
      repository: GitHub does not permit approving your own pull request, so
      every PR would need an admin bypass to merge — reintroducing the bypass
      the checklist is trying to remove. Revisit when there is a second
      maintainer.

All three checks are green today and the workflow has no `paths:` filter, so
every PR into `main` reports all three. There is no risk of a required check
sitting permanently at "Expected — waiting for status to be reported."

A merge queue is a separate question. It serialises merges behind required
checks; it does **not** address instance 4, because the review in question
publishes no check run for a queue to wait on. Confirm availability for this
repository's plan before relying on it.

---

## The pattern: a check that runs and cannot affect the outcome

### 1. Correctness checks masked by the audit

`npm audit --audit-level=low` ran immediately after `npm ci`. It had been red
since at least Nov 1, and because a failing step aborts the job, the dependency
tree, lint, type-check and build steps were **skipped on every run**. For days
there was no signal on whether the frontend built.

*Closed by #68* (audit moved last). The first run afterwards confirmed all four
steps passing — the first evidence in days that the frontend was healthy.

### 2. A gate on an unprotected branch

`frontend-validation` was treated as a gate through several rounds of work. It
never blocked anything: `main` has no protection, so #67 and #68 both merged
while it was red, with no override and no bypass prompt.

*Open — closed by the branch-protection checklist above.*

### 3. A report step that reported nothing new

#70 originally added `npm audit || true` before the gate, to surface moderates
the gate was assumed to suppress. The first CI run disproved the premise:
`--audit-level` sets the exit code, not the verbosity, so both steps emitted
byte-identical output three seconds apart.

The fallback rationale — a green-marked copy of the output for when the gate
goes red — does not survive contact with how a failed run is read. You click
the red step. A green step with the same text is harder to notice, not easier,
because green signals that nothing there needs attention.

*Closed by removing the step rather than rewriting its comment.*

### 4. A review that cannot gate a merge — structural

Codex review is configured on this repository and triggers on "draft marked
ready". It **publishes no check run**: on #67's head the only check runs were
`frontend-validation`, `rls-enforcement`, `backend-tests`, and the Vercel and
Supabase integrations. Its output is issue comments and reactions.

Consequences:

- It cannot be made a required status check, because there is no status to
  require.
- A merge queue would not wait for it, for the same reason.
- Required approvals would force a human pause long enough for it to land, but
  that option deadlocks a sole-maintainer repository (see the checklist).

On #67 and #69 the reviews completed clean *before* the merge — timing, not
design. On #70 the review **failed to complete** ("We couldn't complete this
review") five seconds after the PR was marked ready, and the PR merged seven
seconds after that. A diff of 30 lines merged with its review in a failed
state.

**This gap is structural: it cannot be closed by repository settings.** It is a
property of how quickly "mark ready" is followed by "merge". The mitigation is
procedural — check the review state before merging, and re-trigger with
`@codex review` if it reports `failed` rather than reading the absence of
findings as the absence of problems.

### Related: the workflow never runs on `main`

`main` is absent from the `push:` trigger list, and
`list_workflow_runs(branch: main)` returns zero runs, ever. This pipeline
validates PR heads only, so `main` could break from a direct push or a
dependency drift and nothing would report it.

Not the same pattern — this is a check that does not run where you would assume
it does — but it has the same consequence, and it limits what branch protection
buys: protection gates PRs into `main`, so if `main` itself is never validated,
the side door stays open.

*Open.*

---

## Change log

| PR | Change |
| --- | --- |
| [#68](https://github.com/marshallchristopher473-netizen/AEOS/pull/68) | Audit moved after lint/type-check/build, unmasking four checks |
| [#69](https://github.com/marshallchristopher473-netizen/AEOS/pull/69) | Non-breaking `npm audit fix`: 13 advisories → 8, clearing the `next/og` RCE and four highs |
| [#70](https://github.com/marshallchristopher473-netizen/AEOS/pull/70) | Audit gate moved from `low` to `high` on the full tree |
