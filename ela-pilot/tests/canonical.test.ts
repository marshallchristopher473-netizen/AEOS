import { describe, it, expect } from 'vitest';
import { canonicalJson, assertJsonValue, type JsonValue } from '../src/lib/canonical';

/**
 * `canonicalJson` is what the audit chain hashes, so two properties matter:
 * the same logical payload must always serialize to the same string, and
 * anything it cannot represent faithfully must throw rather than coerce.
 *
 * `audit_log` is append-only. A coerced entry would be valid, permanent and
 * wrong, with no backfill available — so refusing the write is the only
 * correction mechanism there is.
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

  it('accepts null, booleans and nested records', () => {
    expect(canonicalJson({ n: null, t: true, nested: { k: [1, 'a', false] } })).toBe(
      '{"n":null,"nested":{"k":[1,"a",false]},"t":true}',
    );
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

/**
 * Runtime rejections.
 *
 * The `JsonValue` type blocks each of these at compile time — that is the
 * primary defense, verified by the fact that these cases need a cast to even
 * reach the serializer. These tests cover the last line: a JS caller, an `as`
 * cast, or a value crossing an `unknown` boundary.
 */
const bypass = (v: unknown): JsonValue => v as JsonValue;

describe('canonicalJson — rejects non-representable values', () => {
  it('rejects a Date instead of flattening it to {}', () => {
    // The specific trap this guards: a Date has no own enumerable keys, so a
    // rebuild-as-plain-object serializer silently emits `{}` and loses the
    // value entirely, into a record that can never be corrected.
    expect(() => canonicalJson(bypass({ at: new Date('2026-01-01T00:00:00.000Z') }))).toThrow(
      /non-plain object \(Date\)/,
    );
    // The supported form:
    expect(canonicalJson({ at: new Date('2026-01-01T00:00:00.000Z').toISOString() })).toBe(
      '{"at":"2026-01-01T00:00:00.000Z"}',
    );
  });

  it('rejects other non-plain objects', () => {
    expect(() => canonicalJson(bypass({ m: new Map([['a', 1]]) }))).toThrow(/non-plain object \(Map\)/);
    expect(() => canonicalJson(bypass({ s: new Set([1]) }))).toThrow(/non-plain object \(Set\)/);
    class Decision {
      constructor(public score = 1) {}
    }
    expect(() => canonicalJson(bypass({ d: new Decision() }))).toThrow(
      /non-plain object \(Decision\)/,
    );
  });

  it('accepts a null-prototype record', () => {
    const bare = Object.create(null) as Record<string, JsonValue>;
    bare.b = 1;
    bare.a = 2;
    expect(canonicalJson(bare)).toBe('{"a":2,"b":1}');
  });

  it('rejects non-finite numbers instead of coercing them to null', () => {
    expect(() => canonicalJson(bypass({ score: NaN }))).toThrow(/non-finite number/);
    expect(() => canonicalJson(bypass({ score: Infinity }))).toThrow(/non-finite number/);
    expect(() => canonicalJson(bypass({ score: -Infinity }))).toThrow(/non-finite number/);
  });

  it('rejects undefined instead of dropping it — write an explicit null', () => {
    expect(() => canonicalJson(bypass({ a: undefined, c: 1 }))).toThrow(
      /undefined is not JSON-representable/,
    );
    expect(() => canonicalJson(bypass({ xs: [1, undefined, 2] }))).toThrow(
      /undefined is not JSON-representable/,
    );
    expect(canonicalJson({ a: null, c: 1 })).toBe('{"a":null,"c":1}');
  });

  it('rejects functions instead of dropping them', () => {
    expect(() => canonicalJson(bypass({ fn: () => 1 }))).toThrow(
      /function is not JSON-representable/,
    );
  });

  it('rejects bigint', () => {
    expect(() => canonicalJson(bypass({ big: 1n }))).toThrow(/bigint is not JSON-representable/);
  });

  it('rejects a non-representable value nested deep in the payload', () => {
    expect(() =>
      canonicalJson(bypass({ a: { b: { c: [{ d: new Date() }] } } })),
    ).toThrow(/non-plain object \(Date\)/);
  });
});

describe('assertJsonValue', () => {
  it('passes representable values through', () => {
    const v: unknown = { a: 1, b: [null, 'x', true] };
    expect(() => assertJsonValue(v)).not.toThrow();
  });

  it('throws on anything the audit log could not faithfully record', () => {
    expect(() => assertJsonValue({ at: new Date() })).toThrow(/non-plain object/);
    expect(() => assertJsonValue({ n: NaN })).toThrow(/non-finite/);
  });
});
