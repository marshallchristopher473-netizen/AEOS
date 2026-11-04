import { getDb } from '@db/client';
import { handle } from '@/lib/http';
import { currentReviewer } from '@/lib/reviewer';
import { appendAudit } from '@/lib/audit';
import { verifyAuditChain } from '@/lib/audit';
import { computeMetrics } from '@/lib/metrics';
import {
  listResponses,
  listDecisions,
  listScoringRuns,
  listRubrics,
  listAllCalibrations,
  listAudit,
} from '@/lib/repo';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * GET /api/export
 *
 * The pilot's evidence package: rubric, de-identified responses, every scoring
 * run with its pinned versions, every decision, the full audit chain, and the
 * chain's verification result.
 *
 * `pseudonym` and `subgroup` are de-identified cohort metadata, never
 * identifiers (brief, golden rule 4). Student response text is included because
 * a score is not auditable without the text it was given for; the pilot is
 * seeded with synthetic responses for exactly this reason.
 *
 * The export itself is appended to the audit log, so who exported what is
 * part of the record.
 */
export async function GET() {
  return handle(() => {
    const db = getDb();
    const actor = currentReviewer() ?? 'anonymous';

    const responses = listResponses(db);
    const decisions = listDecisions(db);
    const runs = listScoringRuns(db);
    const metrics = computeMetrics(db);

    appendAudit(db, actor, 'export', {
      responses: responses.length,
      decisions: decisions.length,
      scoringRuns: runs.length,
    });

    // Re-read and verify AFTER the export event so the chain in the package
    // includes the export entry itself and verifies as a whole.
    const auditChain = listAudit(db);
    const verification = verifyAuditChain(db);

    return {
      exportedAt: new Date().toISOString(),
      exportedBy: actor,
      schemaVersion: 1,
      note:
        'Synthetic pilot data. `pseudonym` and `subgroup` are de-identified cohort labels, not identifiers.',
      rubrics: listRubrics(db).map((r) => ({
        id: r.id,
        name: r.name,
        definition: JSON.parse(r.definition_json) as unknown,
        createdAt: r.created_at,
      })),
      responses: responses.map((r) => ({
        id: r.id,
        pseudonym: r.pseudonym,
        subgroup: r.subgroup,
        prompt: r.prompt,
        text: r.text,
        createdAt: r.created_at,
      })),
      scoringRuns: runs.map((run) => ({
        id: run.id,
        responseId: run.response_id,
        rubricId: run.rubric_id,
        modelVersion: run.model_version,
        promptVersion: run.prompt_version,
        drafts: JSON.parse(run.output_json) as unknown,
        createdAt: run.created_at,
      })),
      decisions: decisions.map((d) => ({
        id: d.id,
        responseId: d.response_id,
        scoringRunId: d.scoring_run_id,
        criterionId: d.criterion_id,
        aiScore: d.ai_score,
        finalScore: d.final_score,
        action: d.action,
        reviewer: d.reviewer,
        startedAt: d.started_at,
        decidedAt: d.decided_at,
        reviewSeconds: (Date.parse(d.decided_at) - Date.parse(d.started_at)) / 1000,
        note: d.note,
      })),
      calibrations: listAllCalibrations(db).map((c) => ({
        id: c.id,
        reviewer: c.reviewer,
        responseId: c.response_id,
        manualScore: c.manual_score,
        aiScore: c.ai_score,
        revealedAt: c.revealed_at,
        createdAt: c.created_at,
      })),
      metrics,
      auditChain,
      auditVerification: verification,
    };
  });
}
