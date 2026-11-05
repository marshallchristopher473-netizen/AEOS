import { describe, it, expect } from 'vitest';
import { normalizeWeights, weightedTotal, type Rubric } from '../src/lib/rubric';
import {
  parseRubric,
  findCriterion,
  isScoreInScale,
  rubricSchema,
} from '../src/lib/rubric-schema';

const rubric: Rubric = {
  id: 'rubric_arg_g8',
  name: 'Grade 8 — Argumentative Essay',
  criteria: [
    { id: 'claim', label: 'Clear claim', weight: 1, scale: { min: 1, max: 4 }, description: 'd' },
    { id: 'evidence', label: 'Use of evidence', weight: 2, scale: { min: 1, max: 4 }, description: 'd' },
    { id: 'reasoning', label: 'Reasoning', weight: 2, scale: { min: 1, max: 4 }, description: 'd' },
    { id: 'structure', label: 'Organization', weight: 1, scale: { min: 1, max: 4 }, description: 'd' },
  ],
};

describe('normalizeWeights', () => {
  it('rescales weights to sum to 1', () => {
    const sum = normalizeWeights(rubric.criteria).reduce((s, c) => s + c.weight, 0);
    expect(sum).toBeCloseTo(1, 10);
  });

  it('preserves relative proportions', () => {
    const norm = normalizeWeights(rubric.criteria);
    const claim = norm.find((c) => c.id === 'claim')!;
    const evidence = norm.find((c) => c.id === 'evidence')!;
    expect(evidence.weight / claim.weight).toBeCloseTo(2, 10);
    expect(claim.weight).toBeCloseTo(1 / 6, 10);
  });

  it('does not mutate the input criteria', () => {
    const before = rubric.criteria.map((c) => c.weight);
    normalizeWeights(rubric.criteria);
    expect(rubric.criteria.map((c) => c.weight)).toEqual(before);
  });

  it('falls back to a divisor of 1 when weights sum to zero', () => {
    const zeroed = rubric.criteria.map((c) => ({ ...c, weight: 0 }));
    expect(normalizeWeights(zeroed).every((c) => c.weight === 0)).toBe(true);
  });
});

describe('weightedTotal', () => {
  it('returns a weighted mean on the raw score scale', () => {
    // (4*1 + 3*2 + 2*2 + 1*1) / 6 = 15/6
    const total = weightedTotal(rubric, { claim: 4, evidence: 3, reasoning: 2, structure: 1 });
    expect(total).toBeCloseTo(2.5, 10);
  });

  it('equals the top of the scale when every criterion is maxed', () => {
    expect(
      weightedTotal(rubric, { claim: 4, evidence: 4, reasoning: 4, structure: 4 }),
    ).toBeCloseTo(4, 10);
  });

  it('reduces to a simple mean when weights are equal', () => {
    const flat: Rubric = {
      ...rubric,
      criteria: rubric.criteria.map((c) => ({ ...c, weight: 1 })),
    };
    expect(weightedTotal(flat, { claim: 1, evidence: 2, reasoning: 3, structure: 4 })).toBeCloseTo(
      2.5,
      10,
    );
  });

  /**
   * Documented trap: a criterion absent from `scores` contributes 0, which on a
   * 1-4 rubric is BELOW the worst achievable score. A partially-reviewed
   * response therefore reports a total lower than any real performance, and the
   * number looks plausible rather than obviously broken.
   *
   * This is why `holisticAiScore` in calibration.ts re-normalises over the
   * criteria actually present instead of calling `weightedTotal`. Only pass a
   * fully-populated score map here.
   */
  it('counts a missing criterion as 0, not as absent', () => {
    const partial = weightedTotal(rubric, { claim: 4, evidence: 3, reasoning: 2 });
    expect(partial).toBeCloseTo(14 / 6, 10); // 2.333…

    // What the weighted mean of the scored criteria actually is:
    const scoredOnly = (4 * 1 + 3 * 2 + 2 * 2) / 5;
    expect(scoredOnly).toBeCloseTo(2.8, 10);
    expect(partial).toBeLessThan(scoredOnly);
  });

  it('returns 0 for an empty score map rather than signalling absence', () => {
    expect(weightedTotal(rubric, {})).toBe(0);
  });
});

describe('parseRubric', () => {
  it('parses the seeded rubric shape', () => {
    const parsed = parseRubric(JSON.stringify(rubric));
    expect(parsed.criteria.map((c) => c.id)).toEqual([
      'claim',
      'evidence',
      'reasoning',
      'structure',
    ]);
  });

  it('accepts optional scale labels with one entry per scale point', () => {
    const withLabels = {
      ...rubric,
      criteria: [
        {
          ...rubric.criteria[0]!,
          scale: { min: 1, max: 4, labels: ['beginning', 'developing', 'proficient', 'advanced'] },
        },
      ],
    };
    expect(parseRubric(JSON.stringify(withLabels)).criteria[0]!.scale.labels).toHaveLength(4);
  });

  it('rejects labels that do not line up with the scale', () => {
    const bad = {
      ...rubric,
      criteria: [{ ...rubric.criteria[0]!, scale: { min: 1, max: 4, labels: ['a', 'b'] } }],
    };
    expect(() => parseRubric(JSON.stringify(bad))).toThrow();
  });

  it('rejects malformed JSON', () => {
    expect(() => parseRubric('{not json')).toThrow(/not valid JSON/);
  });

  it('rejects an inverted scale', () => {
    // Would make every score "out of scale" and silently block all decisions.
    const bad = { ...rubric, criteria: [{ ...rubric.criteria[0]!, scale: { min: 4, max: 1 } }] };
    expect(() => parseRubric(JSON.stringify(bad))).toThrow();
  });

  it('rejects duplicate criterion ids', () => {
    const bad = { ...rubric, criteria: [rubric.criteria[0]!, rubric.criteria[0]!] };
    expect(() => parseRubric(JSON.stringify(bad))).toThrow();
  });

  it('rejects an anchor outside the criterion scale', () => {
    const bad = {
      ...rubric,
      criteria: [{ ...rubric.criteria[0]!, anchors: [{ score: 9, exemplar: 'x' }] }],
    };
    expect(() => parseRubric(JSON.stringify(bad))).toThrow();
  });

  it('rejects an empty criteria list', () => {
    expect(() => parseRubric(JSON.stringify({ ...rubric, criteria: [] }))).toThrow();
  });

  it('rejects a non-positive weight', () => {
    const bad = { ...rubric, criteria: [{ ...rubric.criteria[0]!, weight: 0 }] };
    expect(() => rubricSchema.parse(bad)).toThrow();
  });
});

describe('findCriterion / isScoreInScale', () => {
  it('finds a criterion by id', () => {
    expect(findCriterion(rubric, 'evidence')?.label).toBe('Use of evidence');
    expect(findCriterion(rubric, 'nope')).toBeUndefined();
  });

  it('accepts integers within the scale', () => {
    const c = findCriterion(rubric, 'claim')!;
    expect(isScoreInScale(c, 1)).toBe(true);
    expect(isScoreInScale(c, 4)).toBe(true);
  });

  it('rejects out-of-range and non-integer scores', () => {
    const c = findCriterion(rubric, 'claim')!;
    expect(isScoreInScale(c, 0)).toBe(false);
    expect(isScoreInScale(c, 5)).toBe(false);
    expect(isScoreInScale(c, 2.5)).toBe(false);
  });
});
