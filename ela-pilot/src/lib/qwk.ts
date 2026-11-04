/**
 * Quadratic weighted kappa for ordinal rubric scores.
 *
 * Returns `null` when the marginal is degenerate (both raters constant and
 * equal). That case contains no rating variance to compute kappa against, so
 * kappa is undefined — not 1. Returning 1 would read as "perfect agreement" and
 * let a flat sample clear a `qwk < threshold` kill criterion while carrying no
 * agreement information at all. `sklearn.cohen_kappa_score` returns nan here;
 * the standard is not to invent a value.
 *
 * Callers distinguish "undefined because the sample is tiny" from "undefined at
 * a sample size where flatness is itself a finding" — see `evaluateKill`.
 */
export function quadraticWeightedKappa(
  a: number[],
  b: number[],
  minRating: number,
  maxRating: number,
): number | null {
  if (a.length !== b.length) throw new Error('qwk: length mismatch');
  if (a.length === 0) throw new Error('qwk: empty input');

  const k = maxRating - minRating + 1;
  const O: number[][] = Array.from({ length: k }, () => new Array(k).fill(0));
  for (let i = 0; i < a.length; i++) {
    const ri = a[i] - minRating;
    const ci = b[i] - minRating;
    if (ri < 0 || ri >= k || ci < 0 || ci >= k) throw new Error('qwk: rating out of range');
    O[ri][ci]++;
  }

  const n = a.length;
  const rowSums = O.map((r) => r.reduce((s, v) => s + v, 0));
  const colSums = Array.from({ length: k }, (_, j) => O.reduce((s, r) => s + r[j], 0));

  const W: number[][] = Array.from({ length: k }, (_, i) =>
    Array.from({ length: k }, (_, j) => ((i - j) ** 2) / ((k - 1) ** 2)),
  );

  let num = 0;
  let den = 0;
  for (let i = 0; i < k; i++) {
    for (let j = 0; j < k; j++) {
      const E = (rowSums[i] * colSums[j]) / n;
      num += W[i][j] * O[i][j];
      den += W[i][j] * E;
    }
  }
  if (den === 0) return null;
  return 1 - num / den;
}
