export type VerificationResult =
  | { status: 'verified'; start: number; end: number; matched: string }
  | { status: 'case-insensitive'; start: number; end: number; matched: string }
  | { status: 'not_found' };

function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function buildRegex(quote: string, caseInsensitive: boolean): RegExp {
  const parts = quote.trim().split(/\s+/).map(escapeRegex);
  return new RegExp(parts.join('\\s+'), caseInsensitive ? 'i' : '');
}

/**
 * Verify that a claimed quote actually appears in the student response.
 * Tries strict (case-sensitive, whitespace-flexible) first, then case-insensitive.
 * Anything else is `not_found` and must be shown as a red flag in the UI.
 */
export function verifyQuote(response: string, quote: string): VerificationResult {
  if (!quote.trim()) return { status: 'not_found' };

  const strict = buildRegex(quote, false).exec(response);
  if (strict) {
    return {
      status: 'verified',
      start: strict.index,
      end: strict.index + strict[0].length,
      matched: strict[0],
    };
  }
  const loose = buildRegex(quote, true).exec(response);
  if (loose) {
    return {
      status: 'case-insensitive',
      start: loose.index,
      end: loose.index + loose[0].length,
      matched: loose[0],
    };
  }
  return { status: 'not_found' };
}
