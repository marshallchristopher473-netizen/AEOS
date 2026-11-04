import { createHash } from 'node:crypto';
import { cookies } from 'next/headers';
import type { KillStatus } from './killswitch';

/**
 * Kill-criteria acknowledgement.
 *
 * When a kill criterion trips, Accept is disabled until a reviewer explicitly
 * acknowledges it (brief, golden rule 6). The acknowledgement is stored as a
 * cookie holding a signature of the exact violations that were shown, so:
 *
 *  - acknowledging one problem does not silently cover a different one that
 *    trips later — the signature changes and the acknowledgement lapses;
 *  - no schema change or new audit action is needed, keeping `audit.ts` and
 *    `schema.sql` exactly as specified.
 *
 * This is informed consent, not an access control. It is client-held and a
 * determined reviewer could forge it; for a single-reviewer local pilot that is
 * the intended trade-off, and it must not be relied on beyond this pilot.
 */
export const KILL_ACK_COOKIE = 'kill_ack';

export function violationSignature(violations: string[]): string {
  return createHash('sha256').update(JSON.stringify([...violations].sort())).digest('hex').slice(0, 32);
}

/** True when the reviewer has acknowledged exactly these violations. */
export function isKillAcknowledged(kill: KillStatus): boolean {
  if (!kill.paused) return true;
  const ack = cookies().get(KILL_ACK_COOKIE)?.value;
  return ack === violationSignature(kill.violations);
}

/** Accept is permitted when nothing is tripped, or the trip was acknowledged. */
export function acceptAllowed(kill: KillStatus): boolean {
  return !kill.paused || isKillAcknowledged(kill);
}
