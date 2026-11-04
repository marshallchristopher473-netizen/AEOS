import { z } from 'zod';

/**
 * Rubric domain model.
 *
 * A rubric is stored in `rubrics.definition_json` as a JSON blob. Everything
 * that reads it goes through `parseRubric`, so a malformed rubric fails loudly
 * at the boundary instead of producing silent nonsense scores downstream.
 */

export const anchorSchema = z.object({
  score: z.number().int(),
  exemplar: z.string().min(1),
});

export const criterionSchema = z
  .object({
    id: z.string().min(1),
    label: z.string().min(1),
    weight: z.number().positive(),
    scale: z.object({
      min: z.number().int(),
      max: z.number().int(),
    }),
    description: z.string().min(1),
    anchors: z.array(anchorSchema).optional(),
  })
  .refine((c) => c.scale.max > c.scale.min, {
    message: 'scale.max must be greater than scale.min',
    path: ['scale'],
  })
  .refine(
    (c) => (c.anchors ?? []).every((a) => a.score >= c.scale.min && a.score <= c.scale.max),
    { message: 'anchor score outside criterion scale', path: ['anchors'] },
  );

export const rubricSchema = z
  .object({
    id: z.string().min(1),
    name: z.string().min(1),
    criteria: z.array(criterionSchema).min(1),
  })
  .refine(
    (r) => new Set(r.criteria.map((c) => c.id)).size === r.criteria.length,
    { message: 'criterion ids must be unique', path: ['criteria'] },
  );

export type Anchor = z.infer<typeof anchorSchema>;
export type Criterion = z.infer<typeof criterionSchema>;
export type Rubric = z.infer<typeof rubricSchema>;

/** Parse a rubric from a JSON string (as stored in `rubrics.definition_json`). */
export function parseRubric(definitionJson: string): Rubric {
  let raw: unknown;
  try {
    raw = JSON.parse(definitionJson);
  } catch {
    throw new Error('rubric definition_json is not valid JSON');
  }
  return rubricSchema.parse(raw);
}

export function findCriterion(rubric: Rubric, criterionId: string): Criterion | undefined {
  return rubric.criteria.find((c) => c.id === criterionId);
}

/**
 * Validate a score against its criterion's scale. Used by the decisions API so
 * a reviewer cannot submit a final score outside the rubric.
 */
export function isScoreInScale(criterion: Criterion, score: number): boolean {
  return Number.isInteger(score) && score >= criterion.scale.min && score <= criterion.scale.max;
}

/** Weighted total of final scores, normalised to 0..1. Reporting only. */
export function weightedTotal(
  rubric: Rubric,
  scoresByCriterion: Record<string, number>,
): number | null {
  let weightSum = 0;
  let achieved = 0;
  for (const c of rubric.criteria) {
    const score = scoresByCriterion[c.id];
    if (typeof score !== 'number') continue;
    const span = c.scale.max - c.scale.min;
    if (span <= 0) continue;
    achieved += c.weight * ((score - c.scale.min) / span);
    weightSum += c.weight;
  }
  if (weightSum === 0) return null;
  return achieved / weightSum;
}
