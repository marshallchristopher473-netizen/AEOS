import { describe, it, expect } from 'vitest';
import { quadraticWeightedKappa } from '../src/lib/qwk';

/**
 * Reference values cross-checked against
 * `sklearn.metrics.cohen_kappa_score(a, b, weights='quadratic', labels=range(min, max+1))`.
 */
describe('quadraticWeightedKappa — reference fixtures', () => {
  it('matches the brief\'s acceptance fixture (check C)', () => {
    expect(quadraticWeightedKappa([1, 2, 3, 3], [1, 2, 3, 2], 1, 3)).toBeCloseTo(0.8, 10);
  });

  it('returns 1 for perfect agreement with spread', () => {
    expect(quadraticWeightedKappa([1, 2, 3, 4], [1, 2, 3, 4], 1, 4)).toBeCloseTo(1, 10);
  });

  it('is negative when disagreement is worse than chance', () => {
    const k = quadraticWeightedKappa([1, 1, 4, 4], [4, 4, 1, 1], 1, 4);
    expect(k).not.toBeNull();
    expect(k as number).toBeLessThan(0);
    expect(k as number).toBeCloseTo(-1, 10);
  });

  it('penalises a far disagreement more than a near one', () => {
    const near = quadraticWeightedKappa([1, 2, 3, 4], [1, 2, 3, 3], 1, 4) as number;
    const far = quadraticWeightedKappa([1, 2, 3, 4], [1, 2, 3, 1], 1, 4) as number;
    expect(near).toBeGreaterThan(far);
  });

  it('is symmetric in its two rating vectors', () => {
    const a = [1, 2, 2, 3, 4, 4];
    const b = [1, 3, 2, 3, 3, 4];
    expect(quadraticWeightedKappa(a, b, 1, 4)).toBeCloseTo(
      quadraticWeightedKappa(b, a, 1, 4) as number,
      10,
    );
  });

  it('is invariant to widening the declared scale', () => {
    // The (N-1)^2 weight normaliser cancels between numerator and denominator,
    // so padding the scale with unused rating levels must not move the metric.
    // Asserted explicitly because a reader could reasonably expect otherwise.
    const narrow = quadraticWeightedKappa([1, 2, 2, 3], [1, 2, 3, 3], 1, 3) as number;
    const wide = quadraticWeightedKappa([1, 2, 2, 3], [1, 2, 3, 3], 1, 6) as number;
    expect(narrow).toBeCloseTo(0.8, 10);
    expect(wide).toBeCloseTo(narrow, 10);
  });
});

describe('quadraticWeightedKappa — undefined cases return null', () => {
  it('returns null for empty input', () => {
    expect(quadraticWeightedKappa([], [], 1, 4)).toBeNull();
  });

  it('returns null when one rater used a single rating throughout', () => {
    // Expected disagreement is 0, so kappa is 0/0 — undefined, not 1.
    expect(quadraticWeightedKappa([3, 3, 3], [3, 3, 3], 1, 4)).toBeNull();
  });
});

describe('quadraticWeightedKappa — input validation', () => {
  it('rejects mismatched lengths', () => {
    expect(() => quadraticWeightedKappa([1, 2], [1], 1, 4)).toThrow(/length mismatch/);
  });

  it('rejects ratings outside the declared scale', () => {
    expect(() => quadraticWeightedKappa([1, 5], [1, 2], 1, 4)).toThrow(/outside/);
    expect(() => quadraticWeightedKappa([1, 2], [0, 2], 1, 4)).toThrow(/outside/);
  });

  it('rejects a non-increasing scale', () => {
    expect(() => quadraticWeightedKappa([1], [1], 3, 3)).toThrow(/must exceed/);
  });

  it('rejects non-integer ratings', () => {
    expect(() => quadraticWeightedKappa([1.5], [1], 1, 4)).toThrow(/outside/);
  });
});
