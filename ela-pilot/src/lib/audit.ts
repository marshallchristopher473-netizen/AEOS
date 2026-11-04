import { createHash } from 'node:crypto';
import type Database from 'better-sqlite3';
import { canonicalJson, type JsonValue } from './canonical';

const GENESIS = '0'.repeat(64);

export type AuditAction =
  | 'response_loaded'
  | 'review_started'
  | 'evidence_viewed'
  | 'scoring_run'
  | 'decision'
  | 'calibration_scored'
  | 'calibration_revealed'
  | 'export';

export function appendAudit(
  db: Database.Database,
  actor: string,
  action: AuditAction,
  // Recursive, not a primitives-only union: audit payloads already nest.
  // `undefined` is deliberately absent — write an explicit `null`.
  payload: Record<string, JsonValue>,
): { ts: string; hash: string } {
  const ts = new Date().toISOString();
  const prevRow = db
    .prepare('SELECT hash FROM audit_log ORDER BY id DESC LIMIT 1')
    .get() as { hash: string } | undefined;
  const prevHash = prevRow?.hash ?? GENESIS;
  const payloadJson = canonicalJson(payload);
  const hash = createHash('sha256')
    .update([prevHash, ts, actor, action, payloadJson].join('|'))
    .digest('hex');

  db.prepare(
    'INSERT INTO audit_log (ts, actor, action, payload, prev_hash, hash) VALUES (?,?,?,?,?,?)',
  ).run(ts, actor, action, payloadJson, prevHash, hash);

  return { ts, hash };
}

export function verifyAuditChain(
  db: Database.Database,
): { ok: true } | { ok: false; brokenAt: number } {
  const rows = db
    .prepare('SELECT id, ts, actor, action, payload, prev_hash, hash FROM audit_log ORDER BY id ASC')
    .all() as Array<{
      id: number; ts: string; actor: string; action: string;
      payload: string; prev_hash: string; hash: string;
    }>;

  let prev = GENESIS;
  for (const r of rows) {
    const expected = createHash('sha256')
      .update([prev, r.ts, r.actor, r.action, r.payload].join('|'))
      .digest('hex');
    if (r.prev_hash !== prev || r.hash !== expected) {
      return { ok: false, brokenAt: r.id };
    }
    prev = r.hash;
  }
  return { ok: true };
}
