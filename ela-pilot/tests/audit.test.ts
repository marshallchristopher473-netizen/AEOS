import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { createHash } from 'node:crypto';
import type Database from 'better-sqlite3';
import { openDb } from '../db/client';
import { appendAudit, verifyAuditChain } from '../src/lib/audit';
import { canonicalJson } from '../src/lib/canonical';

const GENESIS = '0'.repeat(64);

let db: Database.Database;

beforeEach(() => {
  db = openDb(':memory:');
});

afterEach(() => {
  db.close();
});

describe('appendAudit', () => {
  it('chains the first entry to the genesis hash', () => {
    const { hash } = appendAudit(db, 'reviewer@example.org', 'review_started', { responseId: 'res_1' });
    const row = db.prepare('SELECT * FROM audit_log').get() as { prev_hash: string; hash: string };
    expect(row.prev_hash).toBe(GENESIS);
    expect(row.hash).toBe(hash);
  });

  it('links each entry to its predecessor', () => {
    const a = appendAudit(db, 'r1', 'review_started', { n: 1 });
    const b = appendAudit(db, 'r1', 'evidence_viewed', { n: 2 });
    const rows = db
      .prepare('SELECT prev_hash, hash FROM audit_log ORDER BY id')
      .all() as Array<{ prev_hash: string; hash: string }>;

    expect(rows[0].hash).toBe(a.hash);
    expect(rows[1].prev_hash).toBe(a.hash);
    expect(rows[1].hash).toBe(b.hash);
  });

  it('stores the payload canonically so key order cannot change the hash', () => {
    appendAudit(db, 'r1', 'decision', { b: 2, a: 1 });
    const row = db.prepare('SELECT payload FROM audit_log').get() as { payload: string };
    expect(row.payload).toBe(canonicalJson({ a: 1, b: 2 }));
    expect(row.payload).toBe('{"a":1,"b":2}');
  });
});

describe('verifyAuditChain', () => {
  it('returns ok on an empty log', () => {
    expect(verifyAuditChain(db)).toEqual({ ok: true });
  });

  it('returns ok on a clean chain (acceptance check A)', () => {
    appendAudit(db, 'r1', 'response_loaded', { responseId: 'res_1' });
    appendAudit(db, 'r1', 'evidence_viewed', { responseId: 'res_1', criterionId: 'evidence' });
    appendAudit(db, 'r1', 'decision', { responseId: 'res_1', action: 'accept' });
    expect(verifyAuditChain(db)).toEqual({ ok: true });
  });

  it('detects a forged row whose hash does not match its content', () => {
    appendAudit(db, 'r1', 'response_loaded', { responseId: 'res_1' });
    // INSERT is permitted by the schema; the hash chain is what catches it.
    db.prepare(
      'INSERT INTO audit_log (ts, actor, action, payload, prev_hash, hash) VALUES (?,?,?,?,?,?)',
    ).run('2026-01-01T00:00:00.000Z', 'attacker', 'decision', '{"action":"accept"}', GENESIS, 'deadbeef');

    const result = verifyAuditChain(db);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.brokenAt).toBe(2);
  });

  it('detects a spliced row that is internally consistent but breaks the link', () => {
    appendAudit(db, 'r1', 'response_loaded', { responseId: 'res_1' });
    appendAudit(db, 'r1', 'decision', { responseId: 'res_1' });

    // Forge a row that hashes correctly over its own fields but claims GENESIS
    // as its predecessor, i.e. an attempt to rewrite history mid-chain.
    const ts = '2026-01-01T00:00:00.000Z';
    const payload = canonicalJson({ action: 'accept', forged: true });
    const hash = createHash('sha256')
      .update([GENESIS, ts, 'attacker', 'decision', payload].join('|'))
      .digest('hex');
    db.prepare(
      'INSERT INTO audit_log (ts, actor, action, payload, prev_hash, hash) VALUES (?,?,?,?,?,?)',
    ).run(ts, 'attacker', 'decision', payload, GENESIS, hash);

    const result = verifyAuditChain(db);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.brokenAt).toBe(3);
  });
});

/**
 * The boundary of the guarantee.
 *
 * A hash chain with no external anchor detects modification and naive
 * insertion. It cannot detect a well-formed append at the tail, because the
 * forged row IS the new tail and there is nothing outside the DB to disagree
 * with it. Pinned here so the limitation is visible in the suite, not only in
 * the README: "tamper-evident" must never be stated to a security reviewer
 * without this caveat.
 */
describe('verifyAuditChain — known gap: unanchored tail append', () => {
  it('cannot detect a forged row appended at the tail with a recomputed hash', () => {
    appendAudit(db, 'teacher-a', 'response_loaded', { responseId: 'res_1' });
    appendAudit(db, 'teacher-a', 'decision', { responseId: 'res_1', action: 'reject' });

    // An attacker with DB write access reads the current tail and chains onto it.
    const tail = db.prepare('SELECT hash FROM audit_log ORDER BY id DESC LIMIT 1').get() as {
      hash: string;
    };
    const ts = new Date().toISOString();
    const payload = canonicalJson({ responseId: 'res_1', action: 'accept', forged: true });
    const hash = createHash('sha256')
      .update([tail.hash, ts, 'teacher-a', 'decision', payload].join('|'))
      .digest('hex');
    db.prepare(
      'INSERT INTO audit_log (ts, actor, action, payload, prev_hash, hash) VALUES (?,?,?,?,?,?)',
    ).run(ts, 'teacher-a', 'decision', payload, tail.hash, hash);

    // Verifies cleanly. This is the documented limit, not a passing security test.
    expect(verifyAuditChain(db)).toEqual({ ok: true });
  });
});

describe('append-only enforcement (acceptance check A)', () => {
  it('rejects UPDATE on audit_log', () => {
    appendAudit(db, 'r1', 'response_loaded', { responseId: 'res_1' });
    expect(() => db.prepare("UPDATE audit_log SET payload='{}' WHERE id=1").run()).toThrow(
      /audit_log is append-only/,
    );
  });

  it('rejects DELETE on audit_log', () => {
    appendAudit(db, 'r1', 'response_loaded', { responseId: 'res_1' });
    expect(() => db.prepare('DELETE FROM audit_log WHERE id=1').run()).toThrow(
      /audit_log is append-only/,
    );
  });

  it('leaves the chain verifiable after a blocked tamper attempt', () => {
    appendAudit(db, 'r1', 'response_loaded', { responseId: 'res_1' });
    try {
      db.prepare("UPDATE audit_log SET payload='{}' WHERE id=1").run();
    } catch {
      /* expected */
    }
    expect(verifyAuditChain(db)).toEqual({ ok: true });
  });
});
