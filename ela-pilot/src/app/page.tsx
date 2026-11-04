import Link from 'next/link';
import { getDb } from '@db/client';
import { currentReviewer } from '@/lib/reviewer';
import { computeMetrics, qwkTrend } from '@/lib/metrics';
import { verifyAuditChain } from '@/lib/audit';
import { isKillAcknowledged } from '@/lib/killack';
import { listResponses, latestScoringRun, listDecisionsForResponse, defaultRubric } from '@/lib/repo';
import { setReviewerAction, clearReviewerAction, acknowledgeKillAction } from './actions';
import { QwkTrend } from '@/components/QwkTrend';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function pct(v: number | null): string {
  return v === null ? 'n/a' : `${(v * 100).toFixed(0)}%`;
}

function num(v: number | null, digits = 2): string {
  return v === null ? 'n/a' : v.toFixed(digits);
}

export default function Dashboard() {
  const db = getDb();
  const reviewer = currentReviewer();

  let seeded = true;
  try {
    defaultRubric(db);
  } catch {
    seeded = false;
  }

  if (!seeded) {
    return (
      <div className="card">
        <h1 className="text-lg font-semibold">No rubric found</h1>
        <p className="mt-2 text-sm text-slate-600">
          Run <code className="rounded bg-slate-100 px-1">npm run seed</code> to load the pilot
          rubric and three synthetic responses.
        </p>
      </div>
    );
  }

  const metrics = computeMetrics(db);
  const trend = qwkTrend(db);
  const audit = verifyAuditChain(db);
  const acknowledged = isKillAcknowledged(metrics.kill);
  const { rubric } = defaultRubric(db);

  const responses = listResponses(db).map((r) => {
    const run = latestScoringRun(db, r.id);
    const decisions = reviewer ? listDecisionsForResponse(db, r.id, reviewer) : [];
    return {
      ...r,
      hasRun: Boolean(run),
      decided: decisions.length,
      total: rubric.criteria.length,
    };
  });

  return (
    <div className="space-y-6">
      {/* Kill-criteria banner — brief, golden rule 6. */}
      {metrics.kill.paused ? (
        <div className="rounded-md border-2 border-red-700 bg-red-50 p-4" role="alert">
          <h2 className="font-semibold text-red-900">
            Kill criteria tripped — accepting AI scores is {acknowledged ? 'acknowledged' : 'blocked'}
          </h2>
          <ul className="mt-1 list-inside list-disc text-sm text-red-900">
            {metrics.kill.violations.map((v) => (
              <li key={v}>{v}</li>
            ))}
          </ul>
          <p className="mt-2 text-sm text-red-900">
            Thresholds: QWK ≥ {metrics.killCriteria.minQwk}, unverified accept rate ≤{' '}
            {(metrics.killCriteria.maxUnverifiedAcceptRate * 100).toFixed(0)}%. Reviewers can still
            Revise, Reject and Flag.
          </p>
          {!acknowledged ? (
            <form action={acknowledgeKillAction} className="mt-3">
              <button className="btn btn-reject" type="submit">
                Acknowledge and re-enable Accept
              </button>
            </form>
          ) : (
            <p className="mt-2 text-sm font-medium text-red-900">
              Acknowledged by {reviewer ?? 'reviewer'} — Accept re-enabled for these violations only.
            </p>
          )}
        </div>
      ) : (
        <div className="rounded-md border border-green-700/30 bg-green-50 p-3 text-sm text-green-900">
          Kill criteria clear — QWK ≥ {metrics.killCriteria.minQwk} and unverified accept rate ≤{' '}
          {(metrics.killCriteria.maxUnverifiedAcceptRate * 100).toFixed(0)}%.
        </div>
      )}

      {/* Reviewer selection (the pilot's whole "auth" surface). */}
      <section className="card">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Reviewer</h2>
        {reviewer ? (
          <div className="mt-2 flex items-center gap-3">
            <span className="text-sm">
              Signed in as <strong>{reviewer}</strong>
            </span>
            <form action={clearReviewerAction}>
              <button className="btn btn-neutral" type="submit">
                Switch reviewer
              </button>
            </form>
          </div>
        ) : (
          <form action={setReviewerAction} className="mt-2 flex flex-wrap items-center gap-2">
            <input
              name="reviewer"
              required
              placeholder="e.g. teacher-a"
              pattern="[A-Za-z0-9._@\-]{1,64}"
              className="rounded border border-slate-300 px-2 py-1 text-sm"
            />
            <button className="btn btn-neutral" type="submit">
              Set reviewer
            </button>
            <span className="text-xs text-slate-500">
              Letters, digits, dot, underscore, @ and hyphen. Used for attribution, not security.
            </span>
          </form>
        )}
      </section>

      {/* Metric cards. */}
      <section>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Pilot metrics
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Metric
            label="QWK (AI draft vs final)"
            value={num(metrics.qwk)}
            caption={
              metrics.qwkDegenerate
                ? `${metrics.counts.decisions} decisions · no score variance — not evidence`
                : `${metrics.counts.decisions} decisions`
            }
            tone={
              metrics.qwkDegenerate
                ? 'bad'
                : metrics.qwk !== null && metrics.qwk < metrics.killCriteria.minQwk
                  ? 'bad'
                  : 'ok'
            }
          />
          <Metric
            label="Unverified accept rate"
            value={pct(metrics.unverifiedAcceptRate)}
            caption="accepted on a quote not in the text"
            tone={
              metrics.unverifiedAcceptRate > metrics.killCriteria.maxUnverifiedAcceptRate
                ? 'bad'
                : 'ok'
            }
          />
          <Metric
            label="Evidence checked before accept"
            value={pct(metrics.evidenceVerificationRate)}
            caption={`${metrics.counts.accepted} accepted decisions`}
          />
          <Metric
            label="Audit completeness"
            value={pct(metrics.auditCompleteness)}
            caption="decisions with pinned versions"
          />
          <Metric label="Acceptance rate" value={pct(metrics.acceptanceRate)} />
          <Metric label="Revise rate" value={pct(metrics.reviseRate)} />
          <Metric label="Reject rate" value={pct(metrics.rejectRate)} />
          <Metric label="Flag rate" value={pct(metrics.flagRate)} />
          <Metric
            label="Median review time"
            value={
              metrics.medianReviewSecondsOverall === null
                ? 'n/a'
                : `${metrics.medianReviewSecondsOverall.toFixed(1)}s`
            }
            caption="per criterion decision"
          />
          <Metric
            label="Case-insensitive accepts"
            value={pct(metrics.caseInsensitiveAcceptRate)}
            caption="quote matched only ignoring case"
          />
          <Metric
            label="Responses scored"
            value={`${metrics.counts.scoredResponses}/${metrics.counts.responses}`}
          />
          <Metric
            label="Audit chain"
            value={audit.ok ? 'intact' : `broken @ ${audit.brokenAt}`}
            tone={audit.ok ? 'ok' : 'bad'}
            caption="hash-chained, append-only"
          />
        </div>
      </section>

      {/* QWK trend. */}
      <section className="card">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">QWK trend</h2>
        <p className="text-xs text-slate-500">
          Cumulative agreement after each decision. Needs several decisions before it means
          anything.
        </p>
        <div className="mt-3">
          <QwkTrend points={trend} threshold={metrics.killCriteria.minQwk} />
        </div>
      </section>

      {/* Per-criterion detail. */}
      <section className="card">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          By criterion
        </h2>
        <table className="mt-2 w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500">
              <th className="py-1">Criterion</th>
              <th className="py-1">QWK</th>
              <th className="py-1">Median review time</th>
            </tr>
          </thead>
          <tbody>
            {rubric.criteria.map((c) => (
              <tr key={c.id} className="border-t border-slate-100">
                <td className="py-1">{c.label}</td>
                <td className="py-1 tabular-nums">{num(metrics.qwkByCriterion[c.id] ?? null)}</td>
                <td className="py-1 tabular-nums">
                  {metrics.medianReviewSeconds[c.id] === undefined ||
                  metrics.medianReviewSeconds[c.id] === null
                    ? 'n/a'
                    : `${(metrics.medianReviewSeconds[c.id] as number).toFixed(1)}s`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* Worklist. */}
      <section className="card">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Responses
          </h2>
          <a className="btn btn-neutral" href="/api/export" download="ela-pilot-export.json">
            Export evidence package
          </a>
        </div>
        <ul className="mt-2 divide-y divide-slate-100">
          {responses.map((r) => (
            <li key={r.id} className="flex flex-wrap items-center gap-3 py-2">
              <Link href={`/review/${r.id}`} className="font-medium hover:underline">
                {r.pseudonym}
              </Link>
              {r.subgroup ? (
                <span className="badge bg-slate-200 text-slate-700">{r.subgroup}</span>
              ) : null}
              <span className="text-sm text-slate-500">
                {r.hasRun ? 'scored' : 'not scored'}
                {reviewer ? ` · ${r.decided}/${r.total} decided` : ''}
              </span>
              <Link href={`/review/${r.id}`} className="btn btn-neutral ml-auto">
                Review
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function Metric({
  label,
  value,
  caption,
  tone = 'neutral',
}: {
  label: string;
  value: string;
  caption?: string;
  tone?: 'ok' | 'bad' | 'neutral';
}) {
  const toneClass =
    tone === 'bad' ? 'text-red-700' : tone === 'ok' ? 'text-green-800' : 'text-slate-900';
  return (
    <div className="card">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className={`mt-1 text-2xl font-semibold tabular-nums ${toneClass}`}>{value}</div>
      {caption ? <div className="mt-0.5 text-xs text-slate-500">{caption}</div> : null}
    </div>
  );
}
