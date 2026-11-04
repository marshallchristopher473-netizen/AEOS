/**
 * Quadratic weighted kappa (QWK).
 *
 * This is the pilot's headline agreement metric: how closely the AI draft score
 * agrees with the teacher's final score, penalising large disagreements
 * quadratically more than small ones. It is the same statistic as
 * `sklearn.metrics.cohen_kappa_score(a, b, weights='quadratic')` over a fixed
 * rating range.
 *
 *   kappa = 1 - sum(w * O) / sum(w * E)
 *
 * where O is the observed confusion matrix, E is the expected matrix under
 * independence (rescaled to O's total), and w[i][j] = (i-j)^2 / (N-1)^2.
 *
 * Returns `null` when kappa is undefined — i.e. sum(w * E) is 0, which happens
 * when at least one rater used a single rating for every item. Reporting 0 or 1
 * there would be a fabricated number, and the dashboard must show "n/a" rather
 * than a value a reader could mistake for evidence.
 */
export function quadraticWeightedKappa(
  a: readonly number[],
  b: readonly number[],
  min: number,
  max: number,
): number | null {
  if (a.length !== b.length) {
    throw new Error(`quadraticWeightedKappa: length mismatch (${a.length} vs ${b.length})`);
  }
  if (!Number.isInteger(min) || !Number.isInteger(max)) {
    throw new Error('quadraticWeightedKappa: min and max must be integers');
  }
  if (max <= min) {
    throw new Error(`quadraticWeightedKappa: max (${max}) must exceed min (${min})`);
  }
  if (a.length === 0) return null;

  const n = max - min + 1;
  const observed: number[][] = Array.from({ length: n }, () => new Array<number>(n).fill(0));
  const histA = new Array<number>(n).fill(0);
  const histB = new Array<number>(n).fill(0);

  for (let k = 0; k < a.length; k++) {
    const ra = a[k] as number;
    const rb = b[k] as number;
    if (!Number.isInteger(ra) || ra < min || ra > max) {
      throw new Error(`quadraticWeightedKappa: rating ${ra} outside [${min}, ${max}]`);
    }
    if (!Number.isInteger(rb) || rb < min || rb > max) {
      throw new Error(`quadraticWeightedKappa: rating ${rb} outside [${min}, ${max}]`);
    }
    const i = ra - min;
    const j = rb - min;
    (observed[i] as number[])[j] = ((observed[i] as number[])[j] as number) + 1;
    histA[i] = (histA[i] as number) + 1;
    histB[j] = (histB[j] as number) + 1;
  }

  const total = a.length;
  const denomWeight = (n - 1) * (n - 1);

  let numerator = 0;
  let denominator = 0;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const w = ((i - j) * (i - j)) / denomWeight;
      const o = ((observed[i] as number[])[j] as number);
      // Expected counts rescaled so that sum(E) === sum(O) === total.
      const e = ((histA[i] as number) * (histB[j] as number)) / total;
      numerator += w * o;
      denominator += w * e;
    }
  }

  if (denominator === 0) return null;
  return 1 - numerator / denominator;
}
