import { describe, it, expect } from 'vitest';
import { verifyQuote } from '../src/lib/evidence';

const RESPONSE =
  'The author argues that rivers shape cities. In paragraph 3, the text states that "trade followed the water." This claim is supported by the map on page 12.';

describe('verifyQuote — verified', () => {
  it('matches an exact substring', () => {
    const r = verifyQuote(RESPONSE, 'trade followed the water');
    expect(r.status).toBe('verified');
    if (r.status === 'verified') {
      expect(RESPONSE.slice(r.start, r.end)).toBe('trade followed the water');
    }
  });

  it('is whitespace-flexible (collapsed newlines still verify)', () => {
    const r = verifyQuote(RESPONSE, 'rivers   shape\n  cities');
    expect(r.status).toBe('verified');
    if (r.status === 'verified') expect(r.matched).toBe('rivers shape cities');
  });

  it('ignores surrounding whitespace in the claimed quote', () => {
    expect(verifyQuote(RESPONSE, '  the map on page 12  ').status).toBe('verified');
  });
});

describe('verifyQuote — case-insensitive', () => {
  it('flags a quote that only matches when case is ignored', () => {
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
});

describe('verifyQuote — not_found', () => {
  it('rejects a paraphrase', () => {
    expect(verifyQuote(RESPONSE, 'commerce moved along the river').status).toBe('not_found');
  });

  it('rejects the seeded perturbation pattern', () => {
    // scoring.ts perturbs the evidence criterion by replacing a middle word.
    expect(verifyQuote(RESPONSE, 'trade not-in-source the water').status).toBe('not_found');
  });

  it('rejects an empty or whitespace-only quote', () => {
    expect(verifyQuote(RESPONSE, '').status).toBe('not_found');
    expect(verifyQuote(RESPONSE, '   \n ').status).toBe('not_found');
  });

  it('treats regex metacharacters as literal text, not as a pattern', () => {
    // A hostile or sloppy model emitting ".*" must not match everything.
    expect(verifyQuote(RESPONSE, '.*').status).toBe('not_found');
    expect(verifyQuote(RESPONSE, 'rivers.*cities').status).toBe('not_found');
  });

  it('matches metacharacters when they genuinely appear in the response', () => {
    const text = 'The cost (approximately $4.50) rose sharply.';
    expect(verifyQuote(text, '(approximately $4.50)').status).toBe('verified');
  });
});
