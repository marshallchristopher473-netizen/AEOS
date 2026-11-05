// tests/qwk.test.ts
import { describe, it, expect } from 'vitest';
import { quadraticWeightedKappa } from '../src/lib/qwk';

describe('qwk', () => {
  it('matches the sklearn reference value', () => {
    // sklearn.metrics.cohen_kappa_score([1,2,3,3],[1,2,3,2], weights='quadratic') ≈ 0.8
    const k = quadraticWeightedKappa([1, 2, 3, 3], [1, 2, 3, 2], 1, 3);
    expect(k).toBeCloseTo(0.8, 2);
  });
  it('returns 1 on perfect agreement', () => {
    expect(quadraticWeightedKappa([1, 2, 3], [1, 2, 3], 1, 3)).toBe(1);
  });
});

/**
 * Additional coverage beyond the acceptance fixture above.
 *
 * Reference values cross-checked against an independent implementation of
 * `cohen_kappa_score(a, b, weights='quadratic', labels=range(min, max+1))`.
 */
describe('quadraticWeightedKappa — reference fixtures', () => {
  it('hits the acceptance fixture exactly, not merely to 2dp', () => {
    expect(quadraticWeightedKappa([1, 2, 3, 3], [1, 2, 3, 2], 1, 3)!).toBeCloseTo(0.8, 10);
  });

  it('is negative when disagreement is worse than chance', () => {
    expect(quadraticWeightedKappa([1, 1, 4, 4], [4, 4, 1, 1], 1, 4)!).toBeCloseTo(-1, 10);
  });

  it('penalises a far disagreement more than a near one', () => {
    const near = quadraticWeightedKappa([1, 2, 3, 4], [1, 2, 3, 3], 1, 4)!;
    const far = quadraticWeightedKappa([1, 2, 3, 4], [1, 2, 3, 1], 1, 4)!;
    expect(near).toBeGreaterThan(far);
  });

  it('is symmetric in its two rating vectors', () => {
    const a = [1, 2, 2, 3, 4, 4];
    const b = [1, 3, 2, 3, 3, 4];
    expect(quadraticWeightedKappa(a, b, 1, 4)!).toBeCloseTo(
      quadraticWeightedKappa(b, a, 1, 4)!,
      10,
    );
  });

  it('is invariant to widening the declared scale', () => {
    // The (k-1)^2 weight normaliser cancels between numerator and denominator,
    // so padding the scale with unused rating levels must not move the metric.
    const narrow = quadraticWeightedKappa([1, 2, 2, 3], [1, 2, 3, 3], 1, 3)!;
    const wide = quadraticWeightedKappa([1, 2, 2, 3], [1, 2, 3, 3], 1, 6)!;
    expect(narrow).toBeCloseTo(0.8, 10);
    expect(wide).toBeCloseTo(narrow, 10);
  });

  it('returns 0 when both raters are constant but disagree', () => {
    expect(quadraticWeightedKappa([1, 1, 1], [3, 3, 3], 1, 4)!).toBeCloseTo(0, 10);
  });

  it('returns exactly 0 for one disagreement against an otherwise constant rater', () => {
    // The realistic pilot path out of the degenerate case: accept three, revise
    // one. Kappa is defined again and reports the real signal.
    expect(quadraticWeightedKappa([1, 1, 1, 1], [1, 1, 1, 2], 1, 4)!).toBeCloseTo(0, 10);
  });
});

/**
 * The degenerate marginal returns null — kappa is undefined, not 1.
 *
 * A flat sample carries no agreement information. Reporting 1 would read as
 * "perfect agreement" and let it clear a `qwk < threshold` kill criterion,
 * which is exactly the case accept-everything on uniformly-scored responses
 * produces. `evaluateKill` then separates "too early to measure" from "flat at
 * a sample size where that is itself a finding".
 *
 * Note the contrast with "returns 1 on perfect agreement" above: that case has
 * rating variance and genuinely agrees, so 1 is the honest answer. Agreement
 * without variance is not the same thing and must not share its value.
 */
describe('quadraticWeightedKappa — degenerate marginal', () => {
  it('returns null when both raters are constant and equal', () => {
    expect(quadraticWeightedKappa([3, 3, 3], [3, 3, 3], 1, 4)).toBeNull();
  });

  it('returns null for a single item that both raters agreed on', () => {
    expect(quadraticWeightedKappa([2], [2], 1, 4)).toBeNull();
  });

  it('is defined again as soon as one rating differs', () => {
    expect(quadraticWeightedKappa([3, 3, 3], [3, 3, 2], 1, 4)).not.toBeNull();
  });
});

describe('quadraticWeightedKappa — input validation', () => {
  it('throws on empty input', () => {
    expect(() => quadraticWeightedKappa([], [], 1, 4)).toThrow(/empty input/);
  });

  it('throws on mismatched lengths', () => {
    expect(() => quadraticWeightedKappa([1, 2], [1], 1, 4)).toThrow(/length mismatch/);
  });

  it('throws on ratings outside the declared scale', () => {
    expect(() => quadraticWeightedKappa([1, 5], [1, 2], 1, 4)).toThrow(/out of range/);
    expect(() => quadraticWeightedKappa([1, 2], [0, 2], 1, 4)).toThrow(/out of range/);
  });

  it('throws on a non-integer rating', () => {
    // Not a guarded path: a fractional index misses the matrix row entirely.
    // Pinned so the failure stays loud rather than becoming a silent miscount.
    expect(() => quadraticWeightedKappa([1.5], [1], 1, 4)).toThrow();
  });
});
