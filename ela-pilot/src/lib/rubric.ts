// src/lib/rubric.ts
export type Criterion = {
  id: string;
  label: string;
  weight: number;              // normalized at scoring time
  scale: { min: number; max: number; labels?: string[] };
  description: string;
  anchors?: { score: number; exemplar: string }[];
};

export type Rubric = {
  id: string;
  name: string;
  criteria: Criterion[];
};

export function normalizeWeights(criteria: Criterion[]): Criterion[] {
  const total = criteria.reduce((s, c) => s + c.weight, 0) || 1;
  return criteria.map((c) => ({ ...c, weight: c.weight / total }));
}

export function weightedTotal(
  rubric: Rubric,
  scores: Record<string, number>,
): number {
  const norm = normalizeWeights(rubric.criteria);
  return norm.reduce((s, c) => s + (scores[c.id] ?? 0) * c.weight, 0);
}
