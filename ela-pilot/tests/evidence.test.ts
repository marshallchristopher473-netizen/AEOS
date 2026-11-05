// tests/evidence.test.ts
import { describe, it, expect } from 'vitest';
import { verifyQuote } from '../src/lib/evidence';

describe('verifyQuote', () => {
  const response = 'The author argues  that homework harms students. She cites studies.';
  it('finds an exact quote across flexible whitespace', () => {
    const r = verifyQuote(response, 'The author argues that homework');
    expect(r.status).toBe('verified');
  });
  it('falls back to case-insensitive', () => {
    const r = verifyQuote(response, 'the AUTHOR argues');
    expect(r.status).toBe('case-insensitive');
  });
  it('flags paraphrases', () => {
    const r = verifyQuote(response, 'homework is bad for kids');
    expect(r.status).toBe('not_found');
  });
});

/**
 * Additional coverage beyond the acceptance block above.
 *
 * `verifyQuote` is the pilot's one defence against a model that invents a
 * quote, so the offsets it returns (used to highlight the response pane) and
 * its handling of hostile input are worth pinning, not just the status.
 */
const RESPONSE =
  'The author argues that rivers shape cities. In paragraph 3, the text states that "trade followed the water." This claim is supported by the map on page 12.';

describe('verifyQuote — returned offsets', () => {
  it('returns offsets that slice the matched span out of the response', () => {
    const r = verifyQuote(RESPONSE, 'trade followed the water');
    expect(r.status).toBe('verified');
    if (r.status === 'verified') {
      expect(RESPONSE.slice(r.start, r.end)).toBe('trade followed the water');
    }
  });

  it('returns the matched text as it appears in the response, not as quoted', () => {
    const r = verifyQuote(RESPONSE, 'Trade Followed The Water');
    expect(r.status).toBe('case-insensitive');
    if (r.status === 'case-insensitive') {
      expect(r.matched).toBe('trade followed the water');
      expect(RESPONSE.slice(r.start, r.end)).toBe('trade followed the water');
    }
  });

  it('prefers a strict match over a case-insensitive one when both exist', () => {
    const text = 'alpha beta Alpha beta';
    const r = verifyQuote(text, 'Alpha beta');
    expect(r.status).toBe('verified');
    if (r.status === 'verified') expect(r.start).toBe(11);
  });

  it('collapses newlines and runs of whitespace in the claimed quote', () => {
    const r = verifyQuote(RESPONSE, 'rivers   shape\n  cities');
    expect(r.status).toBe('verified');
    if (r.status === 'verified') expect(r.matched).toBe('rivers shape cities');
  });

  it('ignores surrounding whitespace in the claimed quote', () => {
    expect(verifyQuote(RESPONSE, '  the map on page 12  ').status).toBe('verified');
  });
});

describe('verifyQuote — rejects what it cannot find', () => {
  it('rejects the seeded perturbation pattern', () => {
    // scoring.ts perturbs the evidence criterion by replacing a middle word.
    // Acceptance check B depends on this landing as not_found.
    expect(verifyQuote(RESPONSE, 'trade not-in-source the water').status).toBe('not_found');
  });

  it('rejects an empty or whitespace-only quote', () => {
    expect(verifyQuote(RESPONSE, '').status).toBe('not_found');
    expect(verifyQuote(RESPONSE, '   \n ').status).toBe('not_found');
  });

  it('treats regex metacharacters as literal text, not as a pattern', () => {
    // A hostile or sloppy model emitting ".*" must not match everything —
    // otherwise any quote could be made to "verify".
    expect(verifyQuote(RESPONSE, '.*').status).toBe('not_found');
    expect(verifyQuote(RESPONSE, 'rivers.*cities').status).toBe('not_found');
    expect(verifyQuote(RESPONSE, '(?:)').status).toBe('not_found');
  });

  it('matches metacharacters when they genuinely appear in the response', () => {
    const text = 'The cost (approximately $4.50) rose sharply.';
    expect(verifyQuote(text, '(approximately $4.50)').status).toBe('verified');
  });
});
