import { describe, it, expect } from 'vitest';
import { evaluateKill, DEFAULT_KILL, type KillCriteria } from '../src/lib/killswitch';

const ok = { qwk: 0.9, qwkN: 20, unverifiedAcceptRate: 0 };

describe('evaluateKill — measured QWK', () => {
  it('does not pause when both criteria are satisfied', () => {
    const s = evaluateKill(ok);
    expect(s.paused).toBe(false);
    expect(s.violations).toEqual([]);
    expect(s.unmeasured).toEqual([]);
  });

  it('pauses when QWK is below the threshold', () => {
    const s = evaluateKill({ ...ok, qwk: 0.17 });
    expect(s.paused).toBe(true);
    expect(s.violations).toEqual(['QWK 0.17 < 0.5']);
  });

  it('treats the threshold as inclusive — exactly minQwk does not trip', () => {
    expect(evaluateKill({ ...ok, qwk: DEFAULT_KILL.minQwk }).paused).toBe(false);
  });

  it('pauses when the unverified accept rate is above the threshold', () => {
    const s = evaluateKill({ ...ok, unverifiedAcceptRate: 0.25 });
    expect(s.paused).toBe(true);
    expect(s.violations).toEqual(['Unverified accept rate 25.0% > 20%']);
  });

  it('reports both violations together', () => {
    const s = evaluateKill({ qwk: 0.04, qwkN: 12, unverifiedAcceptRate: 0.25 });
    expect(s.violations).toHaveLength(2);
    expect(s.paused).toBe(true);
  });
});

/**
 * The two meanings of a null QWK. Collapsing them is what makes a kill switch
 * either useless (never trips on a flat run) or untrusted (pauses a healthy
 * n=4 pilot, teaching the team to switch it off).
 */
describe('evaluateKill — undefined QWK', () => {
  it('does not pause below the sample-size floor, but reports it as unmeasured', () => {
    // The seeded path: accepting S-019's four all-1 drafts.
    const s = evaluateKill({ qwk: null, qwkN: 4, unverifiedAcceptRate: 0 });
    expect(s.paused).toBe(false);
    expect(s.violations).toEqual([]);
    expect(s.unmeasured).toEqual(['QWK (n=4 < 10)']);
  });

  it('does not pause on an empty pilot', () => {
    const s = evaluateKill({ qwk: null, qwkN: 0, unverifiedAcceptRate: 0 });
    expect(s.paused).toBe(false);
    expect(s.unmeasured).toEqual(['QWK (n=0 < 10)']);
  });

  it('pauses once a flat sample reaches the floor — flatness is then a finding', () => {
    const s = evaluateKill({ qwk: null, qwkN: 10, unverifiedAcceptRate: 0 });
    expect(s.paused).toBe(true);
    expect(s.violations).toEqual(['QWK undefined at n=10 (no rating variance — investigate)']);
    expect(s.unmeasured).toEqual([]);
  });

  it('never reports a criterion as both violated and unmeasured', () => {
    for (const qwkN of [0, 1, 9, 10, 11, 50]) {
      const s = evaluateKill({ qwk: null, qwkN, unverifiedAcceptRate: 0 });
      expect(s.violations.length + s.unmeasured.length).toBe(1);
    }
  });

  it('still catches the evidence criterion while QWK is unmeasured', () => {
    // The failure modes are independent: a tiny sample must not mask an
    // unverified-accept problem.
    const s = evaluateKill({ qwk: null, qwkN: 4, unverifiedAcceptRate: 0.25 });
    expect(s.paused).toBe(true);
    expect(s.violations).toEqual(['Unverified accept rate 25.0% > 20%']);
    expect(s.unmeasured).toEqual(['QWK (n=4 < 10)']);
  });
});

describe('evaluateKill — custom criteria', () => {
  it('honours a pre-registered sample-size floor', () => {
    const strict: KillCriteria = { ...DEFAULT_KILL, minQwkSampleSize: 3 };
    expect(evaluateKill({ qwk: null, qwkN: 4, unverifiedAcceptRate: 0 }, strict).paused).toBe(true);
  });

  it('defaults minQwkSampleSize to 10', () => {
    expect(DEFAULT_KILL.minQwkSampleSize).toBe(10);
  });
});
