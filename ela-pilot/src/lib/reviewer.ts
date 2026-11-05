import { cookies } from 'next/headers';
import { ApiError } from './http';

/**
 * Pilot "auth": a single `reviewer` cookie naming who is reviewing.
 *
 * This is deliberately not authentication — the brief scopes the pilot to a
 * trusted local machine with synthetic data. It exists so decisions and audit
 * entries are attributable to a named reviewer, which the metrics require.
 * It must not be carried into anything handling real student data.
 */
export const REVIEWER_COOKIE = 'reviewer';

const MAX_REVIEWER_LEN = 64;
/** Conservative allowlist: the value lands in the audit chain and in exports. */
const REVIEWER_PATTERN = /^[A-Za-z0-9._@-]{1,64}$/;

export function normalizeReviewer(raw: string): string {
  const trimmed = raw.trim();
  if (!REVIEWER_PATTERN.test(trimmed)) {
    throw new ApiError(
      400,
      `reviewer must match ${REVIEWER_PATTERN.source} (max ${MAX_REVIEWER_LEN} chars)`,
    );
  }
  return trimmed;
}

/** The current reviewer, or null when the cookie is absent or malformed. */
export function currentReviewer(): string | null {
  const raw = cookies().get(REVIEWER_COOKIE)?.value;
  if (!raw) return null;
  try {
    return normalizeReviewer(raw);
  } catch {
    return null;
  }
}

/** The current reviewer, or a 401 for API routes. */
export function requireReviewer(): string {
  const reviewer = currentReviewer();
  if (!reviewer) {
    throw new ApiError(401, 'no reviewer selected — set a reviewer on the dashboard first');
  }
  return reviewer;
}
