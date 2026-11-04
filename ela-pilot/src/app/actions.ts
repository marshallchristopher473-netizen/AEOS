'use server';

import { cookies } from 'next/headers';
import { revalidatePath } from 'next/cache';
import { getDb } from '@db/client';
import { REVIEWER_COOKIE, normalizeReviewer, currentReviewer } from '@/lib/reviewer';
import { KILL_ACK_COOKIE, violationSignature } from '@/lib/killack';
import { computeMetrics } from '@/lib/metrics';

const COOKIE_BASE = {
  httpOnly: true,
  sameSite: 'strict',
  path: '/',
  // The pilot runs on localhost over http; `secure` would make the cookie
  // unsettable there. Must be revisited before any hosted deployment.
  secure: process.env.NODE_ENV === 'production',
} as const;

/** Set the `reviewer` cookie from the dashboard form. */
export async function setReviewerAction(formData: FormData): Promise<void> {
  const raw = formData.get('reviewer');
  if (typeof raw !== 'string') return;
  const reviewer = normalizeReviewer(raw);
  cookies().set(REVIEWER_COOKIE, reviewer, { ...COOKIE_BASE, maxAge: 60 * 60 * 12 });
  revalidatePath('/', 'layout');
}

export async function clearReviewerAction(): Promise<void> {
  cookies().delete(REVIEWER_COOKIE);
  revalidatePath('/', 'layout');
}

/**
 * Acknowledge the currently-tripped kill criteria, re-enabling Accept.
 * The signature is recomputed server-side from live metrics, so a client
 * cannot acknowledge violations that are not actually in force.
 */
export async function acknowledgeKillAction(): Promise<void> {
  const metrics = computeMetrics(getDb());
  if (!metrics.kill.paused) return;
  cookies().set(KILL_ACK_COOKIE, violationSignature(metrics.kill.violations), {
    ...COOKIE_BASE,
    maxAge: 60 * 60 * 4,
  });
  revalidatePath('/', 'layout');
}

export async function clearKillAckAction(): Promise<void> {
  cookies().delete(KILL_ACK_COOKIE);
  revalidatePath('/', 'layout');
}

/** Used by the review page to know who is acting without re-reading cookies. */
export async function whoAmI(): Promise<string | null> {
  return currentReviewer();
}
