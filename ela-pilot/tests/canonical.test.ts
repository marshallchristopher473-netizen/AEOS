import { describe, it, expect } from 'vitest';
import { canonicalJson } from '../src/lib/canonical';

/**
 * `canonicalJson` is what the audit chain hashes, so what matters most is that
 * the same logical payload always serializes to the same string.
 */
describe('canonicalJson — determinism', () => {
  it('sorts object keys', () => {
    expect(canonicalJson({ b: 1, a: 2 })).toBe('{"a":2,"b":1}');
  });

  it('sorts nested object keys', () => {
    expect(canonicalJson({ z: { d: 1, c: 2 }, a: 3 })).toBe('{"a":3,"z":{"c":2,"d":1}}');
  });

  it('produces identical output for logically identical payloads', () => {
    const a = { responseId: 'res_1', action: 'accept', scores: { final: 3, ai: 2 } };
    const b = { scores: { ai: 2, final: 3 }, action: 'accept', responseId: 'res_1' };
    expect(canonicalJson(a)).toBe(canonicalJson(b));
  });

  it('sorts keys inside objects nested in arrays', () => {
    expect(canonicalJson({ xs: [{ b: 1, a: 2 }] })).toBe('{"xs":[{"a":2,"b":1}]}');
  });

  it('preserves array order', () => {
    expect(canonicalJson({ xs: [3, 1, 2] })).toBe('{"xs":[3,1,2]}');
  });

  it('round-trips the payload shapes the audit log actually writes', () => {
    const payload = {
      decisionId: 'dec_1',
      action: 'accept',
      aiScore: 2,
      finalScore: 2,
      reviewSeconds: 1.863,
      hasNote: false,
      note: null,
      criterionIds: ['claim', 'evidence'],
    };
    expect(JSON.parse(canonicalJson(payload))).toEqual(payload);
  });
});

describe('canonicalJson — undefined handling', () => {
  it('drops undefined object values but keeps null', () => {
    expect(canonicalJson({ a: undefined, b: null, c: 1 })).toBe('{"b":null,"c":1}');
  });

  it('serializes undefined array entries as null', () => {
    expect(canonicalJson({ xs: [1, undefined, 2] })).toBe('{"xs":[1,null,2]}');
  });
});

/**
 * Documented coercions, pinned so they are discovered here rather than in an
 * immutable audit record.
 *
 * None of these break the hash chain — output stays deterministic, and
 * `verifyAuditChain` rehashes the stored payload string. They are data-fidelity
 * traps: the entry verifies perfectly while saying less than the caller meant.
 *
 * Rule for callers: put only strings, finite numbers, booleans, null, arrays
 * and plain objects into an audit payload. Convert dates with `.toISOString()`
 * BEFORE handing them to `appendAudit`.
 */
describe('canonicalJson — documented coercions (audit payload hazards)', () => {
  it('flattens a Date to an empty object — pass ISO strings instead', () => {
    // `sortKeys` rebuilds the Date as a plain object (a Date has no own
    // enumerable keys), so JSON.stringify never gets to call its toJSON.
    expect(canonicalJson({ at: new Date('2026-01-01T00:00:00.000Z') })).toBe('{"at":{}}');
    // The safe form:
    expect(canonicalJson({ at: new Date('2026-01-01T00:00:00.000Z').toISOString() })).toBe(
      '{"at":"2026-01-01T00:00:00.000Z"}',
    );
  });

  it('coerces non-finite numbers to null', () => {
    expect(canonicalJson({ score: NaN })).toBe('{"score":null}');
    expect(canonicalJson({ score: Infinity })).toBe('{"score":null}');
  });

  it('drops function values', () => {
    expect(canonicalJson({ fn: () => 1 })).toBe('{}');
  });

  it('throws on bigint rather than coercing it', () => {
    expect(() => canonicalJson({ big: 1n })).toThrow(/BigInt/i);
  });
});
