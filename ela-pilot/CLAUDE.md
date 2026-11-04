# ELA AI Pilot — Build Brief

## Goal
Turn the existing static ELA teacher demo into a **pilot-grade, auditable,
teacher-in-the-loop scoring tool**. The pilot's job is to generate evidence, not
to impress. Every AI suggestion must be evidence-linked, verifiable, version-pinned,
and logged in a tamper-evident audit chain.

## Non-goals
- No student-facing UI.
- No real LLM calls by default (use the `mock` provider; `openai` is opt-in via env).
- No auth beyond a simple `reviewer` cookie. This is a pilot, not production.
- No multi-tenant. Single SQLite file.

## Stack (do not substitute)
- Next.js 14 App Router, TypeScript strict
- better-sqlite3 (synchronous, one file: `./pilot.db`)
- Tailwind CSS
- Zod for all API input validation
- Vitest for unit tests
- Node 20+

## Golden rules
1. **Never mutate `audit_log`.** Schema enforces it with triggers. App code only INSERTs.
2. **Never trust the LLM's evidence quote.** Always run it through `verifyQuote()`
   before display; show `verified` / `case-insensitive` / `not_found` badge.
3. **Pin model + prompt versions per scoring run.** Columns `model_version` and
   `prompt_version` on `scoring_runs` are NOT NULL and immutable after insert.
4. **Synthetic data only** in the seeded demo. `responses.subgroup` is de-identified
   cohort metadata (e.g. `"EL"`, `"IEP"`, `"gen-ed"`) — never an identifier.
5. **One decision per criterion per review.** Store in `decisions`, one row per
   criterion. Time-on-task is `decided_at - started_at` per criterion row.
6. **Kill criteria are computed live** on the dashboard. If tripped, show a red banner
   and disable the Accept button until a reviewer acknowledges.

## Domain model

Rubric = { id, name, criteria: Criterion[] }
Criterion = { id, label, weight, scale: {min,max}, description, anchors?: {score, exemplar}[] }

ScoreDraft (from LLM) = {
  criterionId, score, rationale, evidence (verbatim quote),
  confidence: 'low'|'medium'|'high'
}

Decision = {
  response_id, scoring_run_id, criterion_id,
  ai_score, final_score,
  action: 'accept'|'revise'|'reject'|'flag',
  reviewer, started_at, decided_at, note?
}

## Metrics (all computed in /api/metrics)
- qwk: quadratic weighted kappa, AI draft vs. final, criterion-level, over all decisions
- acceptanceRate: accept / all decisions
- reviseRate, rejectRate, flagRate
- medianReviewSeconds: per criterion, from started_at → decided_at
- evidenceVerificationRate: accepted decisions where an `evidence_viewed` audit
  event for the same response exists BEFORE the decision ts, / accepted decisions
- unverifiedAcceptRate: accepted decisions whose draft evidence was NOT verified, / accepted
- auditCompleteness: decisions that have a matching scoring_run with both versions
  set / all decisions

## Kill criteria (default; surfaced in UI)
- qwk < 0.50
- unverifiedAcceptRate > 0.20
If either trips, banner is red and Accept is disabled.

## Acceptance checks (must all pass before "done")
A. Tamper test: manually `UPDATE audit_log SET payload='{}' WHERE id=1` fails with
   `audit_log is append-only`. `verifyAuditChain()` returns `{ok:true}` on a clean DB.
B. Evidence test: the seeded mock for criterion `evidence` deliberately returns a
   perturbed quote, so `/review` shows a red "not verified" badge on that one card
   and green on the others. `unverifiedAcceptRate` metric reflects it.
C. QWK test: `quadraticWeightedKappa([1,2,3,3],[1,2,3,2], 1, 3)` ≈ 0.8. Verify
   against the fixture in `tests/qwk.test.ts`.

---

# Implementation decisions

Where the brief left a judgement call, this is what was decided and why.

| Question | Decision |
| --- | --- |
| "NOT verified" for `unverifiedAcceptRate` | Counts only `not_found` (the quote is absent from the response). `case-insensitive` is a real match, so folding it in would inflate a kill criterion with non-issues — it is reported separately as `caseInsensitiveAcceptRate`. A decision whose draft can no longer be reconstructed also counts as unverified, so the safety metric fails closed. |
| `started_at` for time-on-task | Derived **server-side**, never sent by the client. The clock for a criterion starts at whichever is later: the reviewer opening the response (`review_started` in the audit chain) or their previous decision on it. Time-on-task is evidence, so it must not be client-settable. |
| Kill acknowledgement storage | A `kill_ack` cookie holding a hash of the exact violations shown. Acknowledging one violation does not cover a different one that trips later. Chosen so `schema.sql` and `audit.ts` stay exactly as specified. It is informed consent, not an access control. |
| QWK when undefined | Returns `null`, never 0 or 1. If a rater used one rating throughout, expected disagreement is 0 and kappa is 0/0. The dashboard shows "n/a" so a reader cannot mistake it for a measurement. |
| Calibration score granularity | `calibration_sessions.manual_score` is one integer, so calibration is holistic. The AI's holistic score is the weight-weighted mean of its per-criterion drafts mapped onto the rubric's overall scale. |
| Rate denominators | Any rate with a zero denominator is `null`, not 0 — "nothing reviewed yet" and "nothing went wrong" must not look the same. |
| Audit payload value types | Only strings, finite numbers, booleans, `null`, arrays and plain objects. See "Audit payload hazards" below — `canonicalJson` silently coerces anything else. |

## Audit payload hazards

`canonicalJson` rebuilds every object as a plain object before `JSON.stringify`
runs. That is what makes it deterministic, and it has three consequences worth
knowing, all pinned in `tests/canonical.test.ts`:

| Input | Serializes as | Why |
| --- | --- | --- |
| `new Date(...)` | `{}` | A Date has no own enumerable keys, so it is rebuilt as an empty plain object and its `toJSON` is never called. **Total loss of the value.** |
| `NaN` / `Infinity` | `null` | Standard `JSON.stringify` behaviour. |
| a function | dropped | Standard `JSON.stringify` behaviour. |
| `1n` (bigint) | throws | Standard `JSON.stringify` behaviour. |

None of these break the hash chain: output stays deterministic, and
`verifyAuditChain` rehashes the *stored payload string*, so entries written this
way still verify. They are data-fidelity traps — the entry verifies perfectly
while recording less than the caller meant, and `audit_log` is append-only so it
cannot be corrected afterwards.

**Rule: convert dates with `.toISOString()` before calling `appendAudit`.** Every
current call site already passes ISO strings (via `nowIso()`) or numbers.

## Deviations from the brief

- **`src/lib/scoring.ts` — two operators changed.** The mock provider used the
  signed shift `>>` on a 32-bit hash seed. When the seed's top bit is set (which
  it is for the first seeded response) this yields negative values, producing an
  out-of-scale score of `-2` on a 1–4 scale and `confidence: undefined`. That
  made the review flow unusable: a `-2` draft cannot be scored against the
  rubric. Changed to the unsigned `>>>` in the two shift sites; nothing else was
  touched. `tests/scoring.test.ts` locks the invariant.
- **`next@14.2.35`.** The brief pins Next 14. Every Next 14 release carries an
  open advisory whose only fix is Next 16, which would be substituting a major
  version. Staying on the newest 14.x and documenting it — see "Known risks".
