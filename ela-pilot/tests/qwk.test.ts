import { describe, it, expect } from 'vitest';
import { quadraticWeightedKappa } from '../src/lib/qwk';

/**
 * Reference values cross-checked against an independent implementation of
 * `sklearn.metrics.cohen_kappa_score(a, b, weights='quadratic', labels=range(min, max+1))`.
 */
describe('quadraticWeightedKappa — reference fixtures', () => {
  it("matches the brief's acceptance fixture (check C)", () => {
    expect(quadraticWeightedKappa([1, 2, 3, 3], [1, 2, 3, 2], 1, 3)).toBeCloseTo(0.8, 10);
  });

  it('returns 1 for perfect agreement with spread', () => {
    expect(quadraticWeightedKappa([1, 2, 3, 4], [1, 2, 3, 4], 1, 4)).toBeCloseTo(1, 10);
  });

  it('is negative when disagreement is worse than chance', () => {
    expect(quadraticWeightedKappa([1, 1, 4, 4], [4, 4, 1, 1], 1, 4)).toBeCloseTo(-1, 10);
  });

  it('penalises a far disagreement more than a near one', () => {
    const near = quadraticWeightedKappa([1, 2, 3, 4], [1, 2, 3, 3], 1, 4);
    const far = quadraticWeightedKappa([1, 2, 3, 4], [1, 2, 3, 1], 1, 4);
    expect(near).toBeGreaterThan(far);
  });

  it('is symmetric in its two rating vectors', () => {
    const a = [1, 2, 2, 3, 4, 4];
    const b = [1, 3, 2, 3, 3, 4];
    expect(quadraticWeightedKappa(a, b, 1, 4)).toBeCloseTo(
      quadraticWeightedKappa(b, a, 1, 4),
      10,
    );
  });

  it('is invariant to widening the declared scale', () => {
    // The (k-1)^2 weight normaliser cancels between numerator and denominator,
    // so padding the scale with unused rating levels must not move the metric.
    const narrow = quadraticWeightedKappa([1, 2, 2, 3], [1, 2, 3, 3], 1, 3);
    const wide = quadraticWeightedKappa([1, 2, 2, 3], [1, 2, 3, 3], 1, 6);
    expect(narrow).toBeCloseTo(0.8, 10);
    expect(wide).toBeCloseTo(narrow, 10);
  });

  it('returns 0 when both raters are constant but disagree', () => {
    expect(quadraticWeightedKappa([1, 1, 1], [3, 3, 3], 1, 4)).toBeCloseTo(0, 10);
  });
});

/**
 * The degenerate marginal.
 *
 * When both raters used one rating for every item and it was the same rating,
 * expected disagreement is 0 and kappa is 0/0. This implementation resolves
 * that to 1.
 *
 * Consequence for the pilot: QWK feeds a kill criterion (`qwk < 0.50`). A
 * reviewer who accepts every draft on a set of responses the model scored
 * identically produces exactly this case — so QWK reads 1.00 and the criterion
 * cannot trip on the very pattern it exists to catch. `computeMetrics` flags
 * the condition as `qwkDegenerate` and the dashboard labels it, so the number
 * is not read as evidence.
 */
describe('quadraticWeightedKappa — degenerate marginal', () => {
  it('returns 1 when both raters are constant and equal', () => {
    expect(quadraticWeightedKappa([3, 3, 3], [3, 3, 3], 1, 4)).toBe(1);
  });

  it('returns 1 for a single item that both raters agreed on', () => {
    expect(quadraticWeightedKappa([2], [2], 1, 4)).toBe(1);
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
