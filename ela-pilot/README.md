# AEOS ELA AI Pilot

An auditable, teacher-in-the-loop rubric scoring tool. Its purpose is to
**generate evidence** about whether AI-assisted ELA scoring is trustworthy —
not to grade students.

Every AI suggestion is evidence-linked, quote-verified, version-pinned, and
written to a tamper-evident audit chain. The teacher decides; the AI drafts.

The build brief, the implementation decisions and the deviations from it are in
[`CLAUDE.md`](./CLAUDE.md).

---

## Quick start

```bash
cd ela-pilot
npm install
npm run seed     # creates ./pilot.db with 1 rubric, 3 synthetic responses, 3 scoring runs
npm run dev      # http://localhost:3000
```

Then on the dashboard, set a reviewer name (e.g. `teacher-a`) before reviewing —
decisions and audit entries are attributed to it.

To start over: `rm -f pilot.db pilot.db-wal pilot.db-shm && npm run seed`.
(The seed inserts a fixed rubric id, so it must be run against a fresh file.)

| Script | What it does |
| --- | --- |
| `npm run seed` | Create and populate `./pilot.db` |
| `npm run dev` | Dev server on :3000 |
| `npm run build` / `npm start` | Production build / serve |
| `npm test` | Vitest unit suite |
| `npm run typecheck` | `tsc --noEmit` |

## The review loop

```
response + rubric
      ↓
scoring run  ──pins model_version + prompt_version──┐
      ↓                                             │
ScoreDraft per criterion                            │
      ↓                                             │
verifyQuote()  →  verified / case-insensitive / not_found
      ↓                                             │
teacher reviews: Accept · Revise · Reject · Flag    │
      ↓                                             │
decision row (one per criterion)  ──────────────────┘
      ↓
append-only, hash-chained audit_log
      ↓
live metrics + kill criteria
```

## Pages

| Route | Purpose |
| --- | --- |
| `/` | Metric cards, QWK trend, kill-criteria banner, export |
| `/review/[id]` | The heart: response pane with evidence highlighting, criterion cards, decisions |
| `/calibration` | Three anchor papers; score blind, then reveal AI + peers |
| `/rubrics` | Read-only rubric view (editing is v2) |

## API

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/responses` | Worklist with scoring + decision state |
| `POST` | `/api/score` | `{ responseId }` → new scoring run, audit entry |
| `POST` | `/api/decisions` | Record one criterion decision, audit entry |
| `POST` | `/api/audit/evidence-viewed` | `{ responseId, criterionId }` → audit entry |
| `GET` | `/api/metrics` | Live metrics + kill status |
| `GET` | `/api/audit/verify` | Recompute the hash chain end to end |
| `GET` | `/api/export` | Full evidence package (self-verifying) |
| `POST` | `/api/calibration` | Blind holistic score |
| `POST` | `/api/calibration/reveal` | Reveal AI + peer scores |

## Metrics, and what they do and do not claim

These are **pilot instrumentation**, not validated outcome claims. Nothing here
supports a statement like "saves teachers time" or "improves accuracy" until a
pilot has actually run with real reviewers and enough decisions to be meaningful.

| Metric | Definition |
| --- | --- |
| `qwk` | Quadratic weighted kappa, AI draft vs. teacher final, pooled over all decisions. `null` when undefined. |
| `qwkByCriterion` | The same, within each criterion. |
| `acceptanceRate` / `reviseRate` / `rejectRate` / `flagRate` | Share of decisions by action. |
| `medianReviewSeconds` | Median `decided_at − started_at`, per criterion. Derived server-side. |
| `evidenceVerificationRate` | Accepted decisions preceded by an `evidence_viewed` event on the same response. |
| `unverifiedAcceptRate` | Accepted decisions whose quote was `not_found` in the response. **Feeds a kill criterion.** |
| `caseInsensitiveAcceptRate` | Accepted decisions whose quote matched only ignoring case. Reported separately. |
| `auditCompleteness` | Decisions whose scoring run carries both a model and a prompt version. |

A rate with a zero denominator is `null`, never `0`.

### Kill criteria

| Threshold | Default |
| --- | --- |
| `qwk` below | `0.50` |
| `unverifiedAcceptRate` above | `0.20` |

When either trips, the dashboard and review page show a red banner and **Accept
is disabled server-side** (HTTP 423) until a reviewer acknowledges that specific
set of violations. Revise, Reject and Flag stay available — the point is to stop
rubber-stamping, not to stop reviewing.

## Acceptance checks

All three pass on a freshly seeded database.

**A — Audit log is append-only and tamper-evident**

```bash
curl -s localhost:3000/api/audit/verify          # {"ok":true,...}
sqlite3 pilot.db "UPDATE audit_log SET payload='{}' WHERE id=1"
#   Runtime error: audit_log is append-only
```
`DELETE` is blocked the same way. Because `INSERT` is permitted by design,
`verifyAuditChain()` is what catches a forged row — it recomputes every hash and
returns `{ok:false, brokenAt:<id>}`. Covered by `tests/audit.test.ts`, including
a row that hashes correctly over its own fields but is spliced mid-chain.

Note: a tamper test only means something once the log has rows. A fresh seed
writes none, so open a review first (or run the test suite, which seeds its own).

**What "tamper-evident" does and does not mean here** — state it this precisely
to a security reviewer:

- ✅ Catches **modification** of any existing entry (triggers block it; the chain
  would also detect it).
- ✅ Catches **naive insertion** — a row with a `prev_hash` that doesn't match
  its predecessor breaks the chain.
- ❌ Does **not** catch a **tail append** by someone with direct DB write access.
  A forger who recomputes the hash against the current tail produces a chain
  that verifies cleanly. There is no external anchor for `verifyAuditChain` to
  disagree with, so by construction it cannot detect this.

That is acceptable for this pilot's threat model — the goal is "a reviewer
cannot quietly rewrite yesterday's decision", and that holds. It is **not**
acceptable for a deployment where the DB writer is not trusted. The fix is
external anchoring: publish the tail hash on a cadence to somewhere the DB
writer does not control (a district-controlled log, a signed timestamp, a second
store). That is a **prerequisite**, listed below — not a later feature.

**B — Unverified evidence is caught and surfaced**

The mock provider deliberately perturbs the quote for the `evidence` criterion.
On `/review/[id]` that card shows a red **✕ not verified** badge with a "do not
accept this score" warning; the other three show green **✓ verified**. Accepting
the unverified one moves `unverifiedAcceptRate` to 25%, which trips the kill
criterion and disables Accept.

**C — QWK matches the reference**

`quadraticWeightedKappa([1,2,3,3],[1,2,3,2], 1, 3) === 0.8` exactly.
Covered by `tests/qwk.test.ts`, cross-checked against an independent
implementation of `sklearn.metrics.cohen_kappa_score(..., weights='quadratic')`.

```bash
npm test     # 47 tests
```

## Known risks and limitations

Read this before putting the pilot in front of anyone.

- **Next.js 14 carries an open security advisory.** The brief pins Next 14 and
  the only published fix is Next 16 — a major-version substitution the brief
  rules out. This build uses the newest 14.x (`14.2.35`) and every other
  dependency is patched (`npm audit`: 9 vulnerabilities → 1). **Run it on
  localhost only.** Do not expose it to a network. Revisit the pin before any
  hosted deployment.
- **The `reviewer` cookie is attribution, not authentication.** Anyone who can
  reach the server can set it to any name. Acceptable for a single trusted
  machine; not acceptable anywhere else.
- **Kill acknowledgement is a client-held cookie.** A reviewer could forge it.
  It exists to force an informed choice, not to prevent a determined one.
- **Synthetic data only.** No real student work should be loaded into this
  pilot. There is no tenant isolation, no encryption at rest, no FERPA/COPPA
  handling, and no consent flow. Those are prerequisites for real data, not
  follow-ups.
- **`evidenceVerificationRate` is response-scoped**, per the brief: it counts an
  `evidence_viewed` event on the same *response* before the decision, not
  necessarily on the same *criterion*. It is a floor, not proof of attention.
- **Every review-page load appends two audit entries** (`response_loaded`,
  `review_started`). The chain is intentionally noisy; a reload re-starts the
  per-criterion clock.
- **The audit chain has no external anchor.** A tail append by someone with
  direct DB write access verifies cleanly — see acceptance check A above. This
  is a **prerequisite** for any deployment where the DB writer is not trusted,
  ranked with tenant isolation and the Next 14 advisory, not a follow-up.
- **Audit payloads are restricted to JSON-representable values**, enforced by
  the `JsonValue` type on `appendAudit` and again by `canonicalJson`, which
  throws rather than coerces. Convert dates with `.toISOString()` and write
  explicit `null` rather than `undefined`. See CLAUDE.md, "Audit payloads: two
  layers of defense".
- **QWK reads 1.00 when there is no score variance.** If every AI score and
  every final score are the same value, kappa is 0/0 and resolves to 1 — which
  is what accept-everything on uniformly-scored responses produces, the very
  pattern the QWK kill criterion should catch. The dashboard labels this case
  ("no score variance — not evidence") via the `qwkDegenerate` flag, but the
  threshold itself does not account for it. Do not quote a QWK of 1.00 without
  checking that flag.
- **Metrics are meaningless at small n.** With a handful of decisions, QWK swings
  wildly — the trend chart says so, and nothing here should be quoted as a result.

## What would make this a real validation

Not in scope for this build, but this is the gap between "it runs" and "it is evidence":

1. A second human rater, so teacher-vs-teacher agreement gives QWK a baseline to beat.
2. A pre-registered hypothesis, success threshold and minimum sample size, set before data collection.
3. A real model behind `SCORING_PROVIDER=openai`, with the prompt version pinned per run.
4. Consent, data handling and a privacy review before any non-synthetic response.

### Prerequisites before real data or an untrusted writer

These gate deployment; none is a follow-up:

| Gate | Why |
| --- | --- |
| External anchoring of the audit tail hash | Without it, "tamper-evident" does not cover a tail append by whoever can write to the DB |
| Tenant isolation, encryption at rest, FERPA/COPPA handling, consent | No student work can be loaded until these exist |
| Resolve the Next 14 advisory | Only published fix is Next 16; until then, localhost only |
| Real authentication | The `reviewer` cookie is attribution, not authentication |
