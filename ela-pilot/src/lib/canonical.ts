/**
 * Deterministic JSON serialization.
 *
 * The audit chain hashes `canonicalJson(payload)`. If the same logical payload
 * could serialize two different ways (key order, `undefined` handling), the
 * chain would be unverifiable across processes. So: object keys are sorted
 * recursively, `undefined` object values are dropped, and `undefined` inside
 * arrays becomes `null` (matching JSON.stringify's array behaviour).
 *
 * Non-finite numbers are rejected rather than silently serialized as `null`,
 * because a NaN score quietly becoming `null` in the audit record would hide a
 * real bug.
 */
export function canonicalJson(value: unknown): string {
  return JSON.stringify(canonicalize(value));
}

function canonicalize(value: unknown): unknown {
  if (value === null) return null;

  if (typeof value === 'number') {
    if (!Number.isFinite(value)) {
      throw new TypeError(`canonicalJson: non-finite number (${String(value)}) cannot be serialized`);
    }
    return value;
  }

  if (typeof value === 'bigint') {
    throw new TypeError('canonicalJson: bigint cannot be serialized');
  }

  if (typeof value === 'string' || typeof value === 'boolean') return value;

  if (typeof value === 'undefined') return undefined;

  if (value instanceof Date) return value.toISOString();

  if (Array.isArray(value)) {
    return value.map((item) => {
      const c = canonicalize(item);
      return typeof c === 'undefined' ? null : c;
    });
  }

  if (typeof value === 'object') {
    const source = value as Record<string, unknown>;
    const out: Record<string, unknown> = {};
    for (const key of Object.keys(source).sort()) {
      const c = canonicalize(source[key]);
      if (typeof c !== 'undefined') out[key] = c;
    }
    return out;
  }

  // functions, symbols
  throw new TypeError(`canonicalJson: unsupported value of type ${typeof value}`);
}
