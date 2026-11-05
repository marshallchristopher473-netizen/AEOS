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
| QWK when undefined | Returns `null`, never 0 or 1. A flat sample has no rating variance to compute kappa against, so kappa is undefined — `sklearn.cohen_kappa_score` returns nan; the standard is not to invent a value. Returning `1` would read as perfect agreement and let a flat run clear the `qwk < 0.50` criterion. |
| Undefined QWK in the kill switch | Split by sample size, not treated as one case. Below `minQwkSampleSize` (10) it is reported as **unmeasured** — a handful of agreeing decisions is what small samples look like, and pausing there is a false positive that teaches teams to disable kill switches. At or above it, a flat sample is itself a finding (rubric, model range, or reviewer behaviour) and pauses. |
| Which metric catches rubber-stamping | `evidenceVerificationRate`, not QWK. A reviewer who accepts 100% having verified 100% of evidence is fine; one who accepts 90% having verified 10% is the failure, and QWK cannot tell those apart. The degenerate-QWK violation means "this run has nothing to say", which is a different failure. Two instruments, two failure modes — do not collapse them. |
| Calibration score granularity | `calibration_sessions.manual_score` is one integer, so calibration is holistic. The AI's holistic score is the weight-weighted mean of its per-criterion drafts mapped onto the rubric's overall scale. |
| Rate denominators | Any rate with a zero denominator is `null`, not 0 — "nothing reviewed yet" and "nothing went wrong" must not look the same. |
| Audit payload value types | Enforced twice: `appendAudit` takes `Record<string, JsonValue>`, and `canonicalJson` throws on anything non-representable. See "Audit payloads: two layers of defense". |
| Pre-registered thresholds | `minQwk` (0.50), `maxUnverifiedAcceptRate` (0.20) and `minQwkSampleSize` (10). The sample floor is a threshold like the others: fix it before data collection and do not tune it to match the n a run happens to produce. If a second reviewer would land 12 decisions total, that is just over the line — the conversation to have before they start, not after. |

## Audit payloads: two layers of defense

`audit_log` is append-only, so a payload written wrong cannot be backfilled or
corrected. The only correction mechanism available is refusing to write it.
A serializer that silently coerces is worse than one that throws, because the
entry it produces is valid, permanent and wrong.

**Layer 1 — the type (primary).** `appendAudit` takes
`payload: Record<string, JsonValue>`, where `JsonValue` is recursive (payloads
already nest). A `Date`, `NaN`, a function or an `undefined` fails to compile.
`undefined` is deliberately not in the union: write an explicit `null`.

**Layer 2 — the serializer (last line).** `canonicalJson` rejects, rather than
coerces, anything it cannot represent faithfully — catching a JS caller, an
`as` cast, or a value crossing an `unknown` boundary:

| Input | Result |
| --- | --- |
| `new Date(...)`, `Map`, `Set`, class instance | throws `non-plain object (X)` |
| `NaN` / `Infinity` | throws `non-finite number` |
| `undefined` | throws `undefined is not JSON-representable` |
| function, bigint | throws `… is not JSON-representable` |
| plain object, incl. null-prototype | serialized, keys sorted |

The `Object.getPrototypeOf` check is what makes layer 2 real. Without it, a
rebuild-as-plain-object serializer turns a `Date` into `{}` — no own enumerable
keys, so `toJSON` is never reached — losing the value entirely into a record
that can never be fixed.

For a value whose shape is not known statically (e.g. a Zod schema with
`z.unknown()` fields), narrow it at the boundary with `assertJsonValue(v)`
rather than loosening `appendAudit`. No current route needs it: every schema
parses to concrete types.

No migration was required. `verifyAuditChain` rehashes the *stored payload
string* rather than re-serializing objects, so entries written before the change
verify identically after it; and existing payloads (ISO strings, numbers) are
byte-identical under the strict serializer anyway. The change only governs
future writes, which is the point.

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
