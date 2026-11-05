// tests/audit.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import Database from 'better-sqlite3';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { appendAudit, verifyAuditChain } from '../src/lib/audit';
import { canonicalJson } from '../src/lib/canonical';

const GENESIS = '0'.repeat(64);

let db: Database.Database;
beforeEach(() => {
  db = new Database(':memory:');
  db.exec(readFileSync(new URL('../db/schema.sql', import.meta.url), 'utf8'));
});

afterEach(() => {
  db.close();
});

describe('audit', () => {
  it('chains entries', () => {
    appendAudit(db, 't1', 'review_started', { responseId: 'r1' });
    appendAudit(db, 't1', 'decision', { responseId: 'r1', criterionId: 'claim', final: 3 });
    expect(verifyAuditChain(db)).toEqual({ ok: true });
  });

  it('detects tampering', () => {
    appendAudit(db, 't1', 'decision', { x: 1 });
    appendAudit(db, 't1', 'decision', { x: 2 });
    // Forge a row. INSERT is permitted by the schema; DELETE is NOT — the
    // append-only trigger blocks it (see "rejects DELETE at the DB level"), so
    // an attacker cannot truncate first. The hash chain is what catches the
    // insert: prev_hash '0' does not match the real predecessor's hash.
    db.prepare(
      "INSERT INTO audit_log (ts, actor, action, payload, prev_hash, hash) VALUES ('x','t1','decision','{}','0','0')",
    ).run();
    const r = verifyAuditChain(db);
    expect(r.ok).toBe(false);
  });

  it('rejects UPDATE at the DB level', () => {
    appendAudit(db, 't1', 'decision', { x: 1 });
    expect(() => db.prepare("UPDATE audit_log SET payload='{}' WHERE id=1").run()).toThrow(
      /append-only/,
    );
  });

  it('rejects DELETE at the DB level', () => {
    appendAudit(db, 't1', 'decision', { x: 1 });
    expect(() => db.exec('DELETE FROM audit_log WHERE id = 1')).toThrow(/append-only/);
    expect(() => db.exec('DELETE FROM audit_log')).toThrow(/append-only/);
  });
});

describe('appendAudit', () => {
  it('chains the first entry to the genesis hash', () => {
    const { hash } = appendAudit(db, 'teacher-a', 'review_started', { responseId: 'res_1' });
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

    expect(rows[0]!.hash).toBe(a.hash);
    expect(rows[1]!.prev_hash).toBe(a.hash);
    expect(rows[1]!.hash).toBe(b.hash);
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

  it('names the first broken row', () => {
    appendAudit(db, 'r1', 'response_loaded', { responseId: 'res_1' });
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

    // Hashes correctly over its own fields, but claims GENESIS as its
    // predecessor — an attempt to rewrite history mid-chain.
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

/**
 * The boundary of the guarantee.
 *
 * A hash chain with no external anchor detects modification and naive
 * insertion. It cannot detect a well-formed append at the tail, because the
 * forged row IS the new tail and there is nothing outside the DB to disagree
 * with it. Pinned here so the limitation is visible in the suite, not only in
 * the README: "tamper-evident" must never be stated to a security reviewer
 * without this caveat.
 *
 * This test asserts `ok === true`. Adding tail anchoring would flip it, which
 * forces whoever does that to update this assertion and the README table in
 * the same commit — the gap cannot quietly close or quietly persist.
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
