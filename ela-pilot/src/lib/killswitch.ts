export type KillCriteria = {
  minQwk: number;
  maxUnverifiedAcceptRate: number;
};

export const DEFAULT_KILL: KillCriteria = {
  minQwk: 0.5,
  maxUnverifiedAcceptRate: 0.2,
};

export type KillStatus = {
  paused: boolean;
  violations: string[];
};

export function evaluateKill(
  metrics: { qwk: number | null; unverifiedAcceptRate: number },
  criteria: KillCriteria = DEFAULT_KILL,
): KillStatus {
  const violations: string[] = [];
  if (metrics.qwk !== null && metrics.qwk < criteria.minQwk) {
    violations.push(`QWK ${metrics.qwk.toFixed(2)} < ${criteria.minQwk}`);
  }
  if (metrics.unverifiedAcceptRate > criteria.maxUnverifiedAcceptRate) {
    violations.push(
      `Unverified accept rate ${(metrics.unverifiedAcceptRate * 100).toFixed(1)}% > ${(criteria.maxUnverifiedAcceptRate * 100).toFixed(0)}%`,
    );
  }
  return { paused: violations.length > 0, violations };
}
