import { z } from 'zod';
import type { Rubric, Criterion } from './rubric';

/**
 * Rubric validation and lookup.
 *
 * Kept separate from `rubric.ts` so that file stays a pure domain model with no
 * dependencies.
 *
 * `rubrics.definition_json` is an untrusted TEXT blob: SQLite does not check its
 * shape, and everything downstream — score-range enforcement, QWK scale bounds,
 * the calibration scale — trusts it. A rubric with `scale: {min: 4, max: 1}`
 * would make every score "out of scale" and silently block all decisions; a
 * missing `criteria` array would crash mid-render. So the blob is parsed once,
 * at the boundary, and fails loudly.
 */

export const anchorSchema = z.object({
  score: z.number().int(),
  exemplar: z.string().min(1),
});

export const scaleSchema = z
  .object({
    min: z.number().int(),
    max: z.number().int(),
    labels: z.array(z.string().min(1)).optional(),
  })
  .refine((s) => s.max > s.min, {
    message: 'scale.max must be greater than scale.min',
  })
  .refine((s) => !s.labels || s.labels.length === s.max - s.min + 1, {
    message: 'scale.labels must have one entry per scale point',
    path: ['labels'],
  });

export const criterionSchema = z
  .object({
    id: z.string().min(1),
    label: z.string().min(1),
    weight: z.number().positive(),
    scale: scaleSchema,
    description: z.string().min(1),
    anchors: z.array(anchorSchema).optional(),
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
  .refine((r) => new Set(r.criteria.map((c) => c.id)).size === r.criteria.length, {
    message: 'criterion ids must be unique',
    path: ['criteria'],
  });

/** Parse a rubric from a JSON string (as stored in `rubrics.definition_json`). */
export function parseRubric(definitionJson: string): Rubric {
  let raw: unknown;
  try {
    raw = JSON.parse(definitionJson);
  } catch {
    throw new Error('rubric definition_json is not valid JSON');
  }
  return rubricSchema.parse(raw) as Rubric;
}

export function findCriterion(rubric: Rubric, criterionId: string): Criterion | undefined {
  return rubric.criteria.find((c) => c.id === criterionId);
}

/**
 * Validate a score against its criterion's scale. Used by the decisions API so
 * a reviewer cannot submit a final score outside the rubric — an out-of-range
 * score would corrupt QWK, the pilot's headline validation metric.
 */
export function isScoreInScale(criterion: Criterion, score: number): boolean {
  return Number.isInteger(score) && score >= criterion.scale.min && score <= criterion.scale.max;
}
