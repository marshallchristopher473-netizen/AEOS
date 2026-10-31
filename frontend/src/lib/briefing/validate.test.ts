/**
 * Integrity-gate tests.
 *
 * Run with the Node runtime already required by this project — no test dependency is added:
 *
 *   npm test
 *
 * Imports here are extensionless and use the `@/` alias, matching the rest of the codebase
 * and keeping `npx tsc --noEmit` happy. `scripts/ts-resolve.mjs` teaches Node to resolve
 * both, since Node's own ESM resolver requires explicit extensions.
 *
 * These assert that the gate *rejects* malformed briefings. A validator nobody has watched
 * fail is indistinguishable from a validator that always passes, and this one is the only
 * thing standing between a deadline and a document that overclaims.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';

import type { Briefing, Claim, Source } from './types';
import { assertBriefingValid, validateBriefing } from './validate';

const META_SOURCE: Source = {
  id: 'meta',
  kind: 'meta-analysis',
  authors: 'Example & Example',
  year: 2020,
  title: 'A meta-analysis',
};

const BOOK_SOURCE: Source = {
  id: 'book',
  kind: 'book',
  authors: 'Author',
  year: 1999,
  title: 'A trade book',
};

function briefingWith(claim: Claim, sources: Source[] = [META_SOURCE]): Briefing {
  return {
    slug: 'fixture',
    title: 'Fixture',
    subtitle: 'Fixture',
    revised: '2026-10-28',
    scope: 'Fixture',
    sources,
    sections: [
      {
        slug: 'only',
        title: 'Only',
        summary: 'Only',
        tone: 'neutral',
        groups: [{ id: 'g', heading: 'G', claims: [claim] }],
      },
    ],
  };
}

function errorsFor(briefing: Briefing): string[] {
  return validateBriefing(briefing)
    .filter((issue) => issue.severity === 'error')
    .map((issue) => issue.message);
}

test('a well-formed claim passes', () => {
  const briefing = briefingWith({
    id: 'ok',
    text: 'Distributed practice outperforms massed practice for long-term retention.',
    tier: 'established',
    sources: ['meta'],
  });

  assert.deepEqual(errorsFor(briefing), []);
  assert.doesNotThrow(() => assertBriefingValid(briefing));
});

test('a sourced tier with no sources is rejected', () => {
  const errors = errorsFor(
    briefingWith({ id: 'c', text: 'Something is true.', tier: 'established', sources: [] }),
  );

  assert.equal(errors.length, 1);
  assert.match(errors[0], /requires at least one source/);
});

test('a citation to an unknown source id is rejected', () => {
  const errors = errorsFor(
    briefingWith({ id: 'c', text: 'Something is true.', tier: 'emerging', sources: ['ghost'] }),
  );

  assert.ok(errors.some((message) => /unknown source "ghost"/.test(message)));
});

test('"established" cannot rest on a trade book alone', () => {
  const errors = errorsFor(
    briefingWith(
      { id: 'c', text: 'Something is true.', tier: 'established', sources: ['book'] },
      [BOOK_SOURCE],
    ),
  );

  assert.ok(errors.some((message) => /needs a meta-analysis/.test(message)));
});

test('a bare number in claim text without a magnitude record is rejected', () => {
  // This is the exact failure mode of "raises Black student achievement (ES: 0.8)" —
  // a precise quantity with no metric and no population recorded anywhere.
  const errors = errorsFor(
    briefingWith({
      id: 'c',
      text: 'The programme raises achievement by 43%.',
      tier: 'established',
      sources: ['meta'],
    }),
  );

  assert.ok(errors.some((message) => /no `magnitude` record/.test(message)));
});

test('an effect-size notation without a magnitude record is rejected', () => {
  const errors = errorsFor(
    briefingWith({
      id: 'c',
      text: 'Culturally affirming instruction raises achievement (ES: 0.8).',
      tier: 'established',
      sources: ['meta'],
    }),
  );

  assert.ok(errors.some((message) => /no `magnitude` record/.test(message)));
});

test('the same claim with a magnitude record passes', () => {
  const briefing = briefingWith({
    id: 'c',
    text: 'The programme improved delayed retention.',
    tier: 'established',
    sources: ['meta'],
    magnitude: {
      value: '43%',
      metric: 'Delayed free recall, one week',
      population: 'US undergraduates',
    },
  });

  assert.deepEqual(errorsFor(briefing), []);
});

test('efficacy language is rejected below a marketable tier', () => {
  const errors = errorsFor(
    briefingWith({
      id: 'c',
      text: 'Our method is clinically validated for adolescent test anxiety.',
      tier: 'inference',
      sources: ['meta'],
    }),
  );

  assert.ok(errors.some((message) => /asserts proven benefit/.test(message)));
});

test('negated efficacy language is not mistaken for a claim', () => {
  // "a guarantee that cannot be met" is a disclaimer, not marketing. The negation guard
  // exists because the first version of this rule flagged exactly this sentence.
  const briefing = briefingWith({
    id: 'c',
    text: 'A sub-second detection guarantee on a statistical classifier cannot be met.',
    tier: 'inference',
    sources: ['meta'],
  });

  assert.deepEqual(errorsFor(briefing), []);
});

test('a hypothesis cannot carry a magnitude', () => {
  const errors = errorsFor(
    briefingWith({
      id: 'c',
      text: 'Family co-certification will help.',
      tier: 'hypothesis',
      sources: [],
      magnitude: { value: '20%', metric: 'invented', population: 'invented' },
    }),
  );

  assert.ok(errors.some((message) => /cannot carry a magnitude/.test(message)));
});

test('a retraction must record what was previously said', () => {
  const errors = errorsFor(
    briefingWith({
      id: 'c',
      text: 'Learning-styles matching does not improve learning.',
      tier: 'retracted',
      sources: ['meta'],
    }),
  );

  assert.ok(errors.some((message) => /must record what was previously asserted/.test(message)));
});

test('a retired claim cannot re-enter at a non-retracted tier', () => {
  // The failure mode this guards: someone copies an old slide into new content under a tier
  // that reads as endorsement. Every one of these was actually asserted in the original.
  for (const text of [
    'Culturally affirming instruction raises achievement (ES: 0.8).',
    'Students study 90% faster with our method.',
    'Spaced repetition powered by the Anki SM-18 engine.',
    'Scheduling built on the NASA BARS method.',
    'A PhD-Level certification for middle schoolers.',
    'We assess VARK modality preference at intake.',
    'We detect preferred cultural learning style from ancestry.',
    'We operate a 72-hour breach notification protocol.',
    'The programme is CEU-eligible.',
    'Certification confers paid peer tutoring eligibility.',
  ]) {
    const errors = errorsFor(
      briefingWith({
        id: 'c',
        text,
        // `inference` is the tier a well-meaning author would reach for.
        tier: 'inference',
        sources: ['meta'],
        magnitude: { value: 'n/a', metric: 'n/a', population: 'n/a' },
      }),
    );
    assert.ok(
      errors.some((message) => /revives a retired claim/.test(message)),
      `expected the blocklist to catch: ${text}`,
    );
  }
});

test('the same retired claims ARE allowed at tier "retracted"', () => {
  // The retracted tier exists to quote the bad claim so the correction stays legible.
  const briefing = briefingWith({
    id: 'c',
    text: 'Anki does not implement SM-18; it is SuperMemo’s proprietary algorithm.',
    tier: 'retracted',
    sources: ['meta'],
    note: 'The original described an "Anki SM-18 engine" in six places.',
  });

  assert.deepEqual(errorsFor(briefing), []);
});

test('duplicate claim ids are rejected', () => {
  const briefing = briefingWith({
    id: 'dupe',
    text: 'Something is true.',
    tier: 'emerging',
    sources: ['meta'],
  });
  briefing.sections[0].groups[0].claims.push({
    id: 'dupe',
    text: 'Something else is true.',
    tier: 'emerging',
    sources: ['meta'],
  });

  assert.ok(errorsFor(briefing).some((message) => /Duplicate claim id/.test(message)));
});

test('assertBriefingValid throws with every error listed', () => {
  const briefing = briefingWith({
    id: 'c',
    text: 'Our proven method improves scores by 90%.',
    tier: 'inference',
    sources: [],
  });

  assert.throws(
    () => assertBriefingValid(briefing),
    (error: Error) =>
      /integrity error/.test(error.message) &&
      /requires at least one source/.test(error.message) &&
      /asserts proven benefit/.test(error.message) &&
      /no `magnitude` record/.test(error.message),
  );
});

test('the shipped MindUnlock briefing passes the gate', async () => {
  const { MINDUNLOCK_BRIEFING } = await import('@/content/mindunlock');
  assert.doesNotThrow(() => assertBriefingValid(MINDUNLOCK_BRIEFING));
});
