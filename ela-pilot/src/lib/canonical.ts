/**
 * Stable JSON serialization for hashing. Keys sorted recursively.
 *
 * This is the primitive the audit chain hashes, and `audit_log` is append-only:
 * a payload written wrong cannot be backfilled or corrected. So this refuses to
 * serialize anything it cannot represent faithfully rather than coercing it.
 * A silently coerced entry is the worst outcome available here — valid,
 * permanent, and wrong.
 *
 * The prototype check is what makes that guarantee hold at runtime rather than
 * only at the type level: `Date`, `Map`, `Set` and class instances all have own
 * enumerable key sets that would rebuild into a misleading plain object (a Date
 * becomes `{}`), so they are rejected outright — even from a JS caller or an
 * `as` cast that slipped past the type.
 */
export type JsonValue =
  | string | number | boolean | null
  | JsonValue[]
  | { [key: string]: JsonValue };

export function canonicalJson(value: JsonValue): string {
  return JSON.stringify(sortKeys(value));
}

function sortKeys(v: JsonValue): JsonValue {
  if (Array.isArray(v)) return v.map(sortKeys);
  if (v !== null && typeof v === 'object') {
    const proto = Object.getPrototypeOf(v);
    if (proto !== Object.prototype && proto !== null) {
      throw new Error(
        `canonicalJson: non-plain object (${proto?.constructor?.name ?? 'null-proto'}) is not JSON-representable`,
      );
    }
    const out: Record<string, JsonValue> = {};
    for (const k of Object.keys(v).sort()) out[k] = sortKeys(v[k] as JsonValue);
    return out;
  }
  if (v === null || typeof v === 'string' || typeof v === 'boolean') return v;
  if (typeof v === 'number') {
    if (!Number.isFinite(v)) throw new Error(`canonicalJson: non-finite number (${v})`);
    return v;
  }
  throw new Error(`canonicalJson: ${typeof v} is not JSON-representable`);
}

/**
 * Narrow an `unknown` to `JsonValue` by attempting serialization.
 *
 * Use at a boundary where a value's shape is not known statically — e.g. a Zod
 * schema with `z.unknown()` fields — so the rest of the call graph stays
 * strongly typed instead of loosening `appendAudit`.
 */
export function assertJsonValue(v: unknown): asserts v is JsonValue {
  canonicalJson(v as JsonValue); // throws if not representable
}
