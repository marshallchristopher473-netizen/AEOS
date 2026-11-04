import Link from 'next/link';
import { notFound as nextNotFound } from 'next/navigation';
import { getDb } from '@db/client';
import { currentReviewer } from '@/lib/reviewer';
import { appendAudit } from '@/lib/audit';
import { verifyQuote } from '@/lib/evidence';
import { computeMetrics } from '@/lib/metrics';
import { acceptAllowed } from '@/lib/killack';
import {
  getResponse,
  latestScoringRun,
  parseDrafts,
  findDraft,
  listDecisionsForResponse,
  defaultRubric,
} from '@/lib/repo';
import { ReviewClient, type CriterionView } from './ReviewClient';
import { ScoreResponseButton } from './ScoreResponseButton';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export default function ReviewPage({ params }: { params: { id: string } }) {
  const db = getDb();
  const reviewer = currentReviewer();

  const response = getResponse(db, params.id);
  if (!response) nextNotFound();

  const { rubric } = defaultRubric(db);
  const run = latestScoringRun(db, params.id);

  if (!reviewer) {
    return (
      <div className="card">
        <h1 className="text-lg font-semibold">Select a reviewer first</h1>
        <p className="mt-2 text-sm text-slate-600">
          Decisions and audit entries are attributed to a named reviewer, so one must be set before
          reviewing.
        </p>
        <Link href="/" className="btn btn-neutral mt-4 inline-block">
          Go to dashboard
        </Link>
      </div>
    );
  }

  if (!run) {
    return (
      <div className="card">
        <h1 className="text-lg font-semibold">
          {response.pseudonym} has no scoring run yet
        </h1>
        <p className="mt-2 text-sm text-slate-600">
          Generate AI draft scores for this response before reviewing. The model and prompt versions
          are pinned to the run at creation time.
        </p>
        <div className="mt-4">
          <ScoreResponseButton responseId={response.id} />
        </div>
      </div>
    );
  }

  // Opening the review starts the clock. The timestamp is written server-side
  // into the audit chain; `started_at` on each decision is derived from it, so
  // time-on-task cannot be set by the client.
  appendAudit(db, reviewer, 'response_loaded', {
    responseId: response.id,
    scoringRunId: run.id,
  });
  appendAudit(db, reviewer, 'review_started', {
    responseId: response.id,
    scoringRunId: run.id,
    rubricId: rubric.id,
  });

  const drafts = parseDrafts(run);
  const decisions = listDecisionsForResponse(db, response.id, reviewer);
  const decisionByCriterion = new Map(decisions.map((d) => [d.criterion_id, d]));

  const criteria: CriterionView[] = rubric.criteria.map((c) => {
    const draft = findDraft(drafts, c.id);
    const decision = decisionByCriterion.get(c.id);
    return {
      id: c.id,
      label: c.label,
      description: c.description,
      weight: c.weight,
      scale: c.scale,
      draft: draft
        ? {
            score: draft.score,
            rationale: draft.rationale,
            evidence: draft.evidence,
            confidence: draft.confidence,
          }
        : null,
      // Golden rule 2: never trust the model's quote — verify it server-side
      // before it reaches the screen.
      verification: draft ? verifyQuote(response.text, draft.evidence) : { status: 'not_found' },
      decision: decision
        ? {
            action: decision.action,
            finalScore: decision.final_score,
            note: decision.note,
            decidedAt: decision.decided_at,
          }
        : null,
    };
  });

  const metrics = computeMetrics(db);
  const canAccept = acceptAllowed(metrics.kill);

  return (
    <ReviewClient
      responseId={response.id}
      pseudonym={response.pseudonym}
      subgroup={response.subgroup}
      prompt={response.prompt}
      text={response.text}
      modelVersion={run.model_version}
      promptVersion={run.prompt_version}
      scoringRunId={run.id}
      rubricName={rubric.name}
      criteria={criteria}
      killPaused={metrics.kill.paused}
      killViolations={metrics.kill.violations}
      acceptAllowed={canAccept}
    />
  );
}
