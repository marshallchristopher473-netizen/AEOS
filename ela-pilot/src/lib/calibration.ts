import type { Rubric } from './rubric';
import type { ScoreDraft } from './scoring';

/**
 * Calibration uses a single holistic score per anchor paper, because
 * `calibration_sessions.manual_score` is one integer per reviewer per response.
 *
 * The holistic scale spans the rubric's criteria, and the AI's holistic score
 * is the weight-weighted mean of its per-criterion drafts mapped onto it. This
 * keeps "what the teacher scored blind" and "what the AI scored" on one
 * comparable axis.
 */
export function calibrationScale(rubric: Rubric): { min: number; max: number } {
  return {
    min: Math.min(...rubric.criteria.map((c) => c.scale.min)),
    max: Math.max(...rubric.criteria.map((c) => c.scale.max)),
  };
}

/** Weighted holistic AI score on the calibration scale, rounded to an integer. */
export function holisticAiScore(rubric: Rubric, drafts: ScoreDraft[]): number | null {
  const byId = new Map(drafts.map((d) => [d.criterionId, d.score]));

  let weightSum = 0;
  let achieved = 0;
  for (const c of rubric.criteria) {
    const score = byId.get(c.id);
    if (typeof score !== 'number') continue;
    const span = c.scale.max - c.scale.min;
    if (span <= 0) continue;
    achieved += c.weight * ((score - c.scale.min) / span);
    weightSum += c.weight;
  }
  if (weightSum === 0) return null;

  const fraction = achieved / weightSum;
  const scale = calibrationScale(rubric);
  return Math.round(scale.min + fraction * (scale.max - scale.min));
}
