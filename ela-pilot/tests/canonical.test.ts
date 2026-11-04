import { describe, it, expect } from 'vitest';
import { canonicalJson } from '../src/lib/canonical';

describe('canonicalJson', () => {
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

  it('preserves array order', () => {
    expect(canonicalJson({ xs: [3, 1, 2] })).toBe('{"xs":[3,1,2]}');
  });

  it('drops undefined object values but keeps null', () => {
    expect(canonicalJson({ a: undefined, b: null, c: 1 })).toBe('{"b":null,"c":1}');
  });

  it('serializes undefined array entries as null, like JSON.stringify', () => {
    expect(canonicalJson({ xs: [1, undefined, 2] })).toBe('{"xs":[1,null,2]}');
  });

  it('serializes dates as ISO strings', () => {
    expect(canonicalJson({ at: new Date('2026-01-01T00:00:00.000Z') })).toBe(
      '{"at":"2026-01-01T00:00:00.000Z"}',
    );
  });

  it('rejects non-finite numbers rather than silently writing null', () => {
    expect(() => canonicalJson({ score: NaN })).toThrow(/non-finite/);
    expect(() => canonicalJson({ score: Infinity })).toThrow(/non-finite/);
  });

  it('rejects values it cannot represent deterministically', () => {
    expect(() => canonicalJson({ fn: () => 1 })).toThrow(/unsupported value/);
    expect(() => canonicalJson({ big: 1n })).toThrow(/bigint/);
  });
});
