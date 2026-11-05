import { getDb } from '@db/client';
import { handle } from '@/lib/http';
import { computeMetrics } from '@/lib/metrics';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * GET /api/metrics
 * Live pilot metrics plus kill-criteria status. Computed on every request —
 * nothing is cached, because a stale kill status would let a reviewer keep
 * accepting after a threshold has been crossed.
 */
export async function GET() {
  return handle(() => computeMetrics(getDb()));
}
