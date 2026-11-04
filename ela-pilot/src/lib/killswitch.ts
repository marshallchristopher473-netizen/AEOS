export type KillCriteria = {
  minQwk: number;
  maxUnverifiedAcceptRate: number;
  /**
   * Decisions required before an undefined QWK counts as a finding rather than
   * "not enough data yet". Pre-registered alongside `minQwk` — do not tune it
   * to match the data a run happens to produce.
   */
  minQwkSampleSize: number;
};

export const DEFAULT_KILL: KillCriteria = {
  minQwk: 0.5,
  maxUnverifiedAcceptRate: 0.2,
  minQwkSampleSize: 10,
};

export type KillStatus = {
  paused: boolean;
  violations: string[];
  /** Criteria that could not be evaluated yet. Reported, never pausing. */
  unmeasured: string[];
};

/**
 * A null `qwk` has two very different meanings, and collapsing them is what
 * makes a kill switch either useless or untrusted:
 *
 *  - below `minQwkSampleSize`: a handful of decisions that happened to agree is
 *    what small samples look like. Pausing here is a false positive, and false
 *    positives are what teach teams to switch kill criteria off.
 *  - at or above it: every AI score and every final score identical across a
 *    real sample means the rubric, the model's range, or the reviewers need
 *    investigating. That is worth pausing for.
 *
 * Note this is not the rubber-stamping detector. A reviewer who accepts 100%
 * having verified 100% of evidence is fine; one who accepts 90% having verified
 * 10% is the failure — and `evidenceVerificationRate` is what separates those.
 * Two instruments, two failure modes.
 */
export function evaluateKill(
  metrics: { qwk: number | null; qwkN: number; unverifiedAcceptRate: number },
  criteria: KillCriteria = DEFAULT_KILL,
): KillStatus {
  const violations: string[] = [];
  const unmeasured: string[] = [];

  if (metrics.qwk === null) {
    if (metrics.qwkN >= criteria.minQwkSampleSize) {
      violations.push(`QWK undefined at n=${metrics.qwkN} (no rating variance — investigate)`);
    } else {
      unmeasured.push(`QWK (n=${metrics.qwkN} < ${criteria.minQwkSampleSize})`);
    }
  } else if (metrics.qwk < criteria.minQwk) {
    violations.push(`QWK ${metrics.qwk.toFixed(2)} < ${criteria.minQwk}`);
  }

  if (metrics.unverifiedAcceptRate > criteria.maxUnverifiedAcceptRate) {
    violations.push(
      `Unverified accept rate ${(metrics.unverifiedAcceptRate * 100).toFixed(1)}% > ${(criteria.maxUnverifiedAcceptRate * 100).toFixed(0)}%`,
    );
  }

  return { paused: violations.length > 0, violations, unmeasured };
}
