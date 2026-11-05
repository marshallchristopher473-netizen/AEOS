import { randomUUID } from 'node:crypto';

/**
 * Prefixed, collision-resistant identifiers.
 *
 * Prefixes make IDs self-describing in the audit log and in exports, which
 * matters when a reviewer or an auditor is reading a CSV months later.
 */
export type IdPrefix = 'rub' | 'resp' | 'run' | 'dec' | 'cal';

export function newId(prefix: IdPrefix): string {
  return `${prefix}_${randomUUID()}`;
}

export const newRubricId = () => newId('rub');
export const newResponseId = () => newId('resp');
export const newScoringRunId = () => newId('run');
export const newDecisionId = () => newId('dec');
export const newCalibrationId = () => newId('cal');

/** ISO-8601 UTC timestamp — the only time format stored in the DB. */
export function nowIso(): string {
  return new Date().toISOString();
}
