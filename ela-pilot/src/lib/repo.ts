import type Database from 'better-sqlite3';
import type { Rubric } from './rubric';
import { parseRubric } from './rubric-schema';
import type { ScoreDraft } from './scoring';

/**
 * Typed row accessors. Everything that reads the pilot database goes through
 * here so the `unknown` returned by better-sqlite3 is narrowed in exactly one
 * place rather than cast ad hoc in every route.
 */

export type ResponseRow = {
  id: string;
  pseudonym: string;
  subgroup: string | null;
  prompt: string;
  text: string;
  created_at: string;
};

export type ScoringRunRow = {
  id: string;
  response_id: string;
  rubric_id: string;
  model_version: string;
  prompt_version: string;
  output_json: string;
  created_at: string;
};

export type DecisionRow = {
  id: string;
  response_id: string;
  scoring_run_id: string;
  criterion_id: string;
  ai_score: number;
  final_score: number;
  action: 'accept' | 'revise' | 'reject' | 'flag';
  reviewer: string;
  started_at: string;
  decided_at: string;
  note: string | null;
};

export type RubricRow = {
  id: string;
  name: string;
  definition_json: string;
  created_at: string;
};

export type CalibrationRow = {
  id: string;
  reviewer: string;
  response_id: string;
  manual_score: number;
  ai_score: number | null;
  revealed_at: string | null;
  created_at: string;
};

export function listResponses(db: Database.Database): ResponseRow[] {
  return db
    .prepare('SELECT * FROM responses ORDER BY pseudonym ASC')
    .all() as ResponseRow[];
}

export function getResponse(db: Database.Database, id: string): ResponseRow | undefined {
  return db.prepare('SELECT * FROM responses WHERE id = ?').get(id) as ResponseRow | undefined;
}

export function listScoringRuns(db: Database.Database): ScoringRunRow[] {
  return db.prepare('SELECT * FROM scoring_runs ORDER BY created_at ASC').all() as ScoringRunRow[];
}

/** Most recent scoring run for a response, or undefined if it has never been scored. */
export function latestScoringRun(
  db: Database.Database,
  responseId: string,
): ScoringRunRow | undefined {
  return db
    .prepare(
      'SELECT * FROM scoring_runs WHERE response_id = ? ORDER BY created_at DESC, rowid DESC LIMIT 1',
    )
    .get(responseId) as ScoringRunRow | undefined;
}

export function getScoringRun(db: Database.Database, id: string): ScoringRunRow | undefined {
  return db.prepare('SELECT * FROM scoring_runs WHERE id = ?').get(id) as ScoringRunRow | undefined;
}

export function listDecisions(db: Database.Database): DecisionRow[] {
  return db.prepare('SELECT * FROM decisions ORDER BY decided_at ASC').all() as DecisionRow[];
}

export function listDecisionsForResponse(
  db: Database.Database,
  responseId: string,
  reviewer: string,
): DecisionRow[] {
  return db
    .prepare('SELECT * FROM decisions WHERE response_id = ? AND reviewer = ?')
    .all(responseId, reviewer) as DecisionRow[];
}

export function getRubric(db: Database.Database, id: string): RubricRow | undefined {
  return db.prepare('SELECT * FROM rubrics WHERE id = ?').get(id) as RubricRow | undefined;
}

export function listRubrics(db: Database.Database): RubricRow[] {
  return db.prepare('SELECT * FROM rubrics ORDER BY created_at ASC').all() as RubricRow[];
}

/** The pilot runs a single rubric; this is the one the review flow uses. */
export function defaultRubric(db: Database.Database): { row: RubricRow; rubric: Rubric } {
  const row = db
    .prepare('SELECT * FROM rubrics ORDER BY created_at ASC LIMIT 1')
    .get() as RubricRow | undefined;
  if (!row) throw new Error('no rubric found — run `npm run seed` first');
  return { row, rubric: parseRubric(row.definition_json) };
}

export function parseDrafts(run: ScoringRunRow): ScoreDraft[] {
  const parsed: unknown = JSON.parse(run.output_json);
  if (!Array.isArray(parsed)) {
    throw new Error(`scoring_run ${run.id} output_json is not an array`);
  }
  return parsed as ScoreDraft[];
}

export function findDraft(drafts: ScoreDraft[], criterionId: string): ScoreDraft | undefined {
  return drafts.find((d) => d.criterionId === criterionId);
}

export function listCalibrations(db: Database.Database, reviewer: string): CalibrationRow[] {
  return db
    .prepare('SELECT * FROM calibration_sessions WHERE reviewer = ? ORDER BY created_at ASC')
    .all(reviewer) as CalibrationRow[];
}

export function listAllCalibrations(db: Database.Database): CalibrationRow[] {
  return db
    .prepare('SELECT * FROM calibration_sessions ORDER BY created_at ASC')
    .all() as CalibrationRow[];
}

export type AuditRow = {
  id: number;
  ts: string;
  actor: string;
  action: string;
  payload: string;
  prev_hash: string;
  hash: string;
};

export function listAudit(db: Database.Database): AuditRow[] {
  return db.prepare('SELECT * FROM audit_log ORDER BY id ASC').all() as AuditRow[];
}

export function listAuditByAction(db: Database.Database, action: string): AuditRow[] {
  return db
    .prepare('SELECT * FROM audit_log WHERE action = ? ORDER BY id ASC')
    .all(action) as AuditRow[];
}
