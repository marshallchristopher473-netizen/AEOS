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
returns `{ok:false, brokenAt:<id>}`. Covered by `tests/audit.test.ts`.

Note: a tamper test only means something once the log has rows. A fresh seed
writes none, so open a review first (or run the test suite, which seeds its own).

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
- **Audit payloads accept only JSON-primitive values.** `canonicalJson` flattens
  a `Date` to `{}` and coerces `NaN`/`Infinity` to `null`. The hash chain still
  verifies — it is a fidelity trap, not an integrity one — but `audit_log` is
  append-only, so a degraded entry cannot be corrected. Convert dates with
  `.toISOString()` before calling `appendAudit`. See CLAUDE.md, "Audit payload
  hazards".
- **Metrics are meaningless at small n.** With a handful of decisions, QWK swings
  wildly — the trend chart says so, and nothing here should be quoted as a result.

## What would make this a real validation

Not in scope for this build, but this is the gap between "it runs" and "it is evidence":

1. A second human rater, so teacher-vs-teacher agreement gives QWK a baseline to beat.
2. A pre-registered hypothesis, success threshold and minimum sample size, set before data collection.
3. A real model behind `SCORING_PROVIDER=openai`, with the prompt version pinned per run.
4. Consent, data handling and a privacy review before any non-synthetic response.
