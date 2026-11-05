import { getDb } from '@db/client';
import { handle } from '@/lib/http';
import { verifyAuditChain } from '@/lib/audit';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/**
 * GET /api/audit/verify
 * Recomputes the audit hash chain end to end. `{ ok: true }` means every entry
 * still hashes to the value stored beside it; `brokenAt` names the first row
 * that does not.
 */
export async function GET() {
  return handle(() => {
    const db = getDb();
    const result = verifyAuditChain(db);
    const { n } = db.prepare('SELECT COUNT(*) AS n FROM audit_log').get() as { n: number };
    return { ...result, entries: n, checkedAt: new Date().toISOString() };
  });
}
