import { describe, it, expect } from 'vitest';
import { runScoring } from '../src/lib/scoring';
import { verifyQuote } from '../src/lib/evidence';
import { rubricSchema, type Rubric } from '../src/lib/rubric';

const rubric: Rubric = rubricSchema.parse({
  id: 'rubric_arg_g8',
  name: 'Grade 8 — Argumentative Essay',
  criteria: [
    { id: 'claim', label: 'Clear claim', weight: 1, scale: { min: 1, max: 4 }, description: 'States a defensible position.' },
    { id: 'evidence', label: 'Use of evidence', weight: 2, scale: { min: 1, max: 4 }, description: 'Quotes or cites textual evidence accurately.' },
    { id: 'reasoning', label: 'Reasoning', weight: 2, scale: { min: 1, max: 4 }, description: 'Explains how evidence supports the claim.' },
    { id: 'structure', label: 'Organization', weight: 1, scale: { min: 1, max: 4 }, description: 'Logical paragraphs and transitions.' },
  ],
});

const SEEDED_TEXT =
  'The author argues that homework harms students. She cites studies showing sleep loss. This evidence shows the claim is strong because sleep affects learning. In conclusion, schools should limit homework.';

/** A spread of texts, including ones whose hash prefix sets the sign bit. */
function sampleTexts(n: number): string[] {
  const out: string[] = [SEEDED_TEXT];
  for (let i = 0; i < n; i++) {
    out.push(
      `Student ${i} wrote this. The author claims point ${i}. Evidence supports it. Therefore the conclusion holds.`,
    );
  }
  return out;
}

describe('mock scoring provider', () => {
  it('never emits a score outside the criterion scale', async () => {
    // Regression: a signed `>>` on a 32-bit hash seed produced negative scores
    // (e.g. -2 on a 1-4 scale) whenever the seed's top bit was set.
    for (const text of sampleTexts(150)) {
      const run = await runScoring(text, rubric);
      for (const draft of run.drafts) {
        const criterion = rubric.criteria.find((c) => c.id === draft.criterionId);
        expect(criterion, `unknown criterion ${draft.criterionId}`).toBeDefined();
        expect(Number.isInteger(draft.score)).toBe(true);
        expect(draft.score).toBeGreaterThanOrEqual(criterion!.scale.min);
        expect(draft.score).toBeLessThanOrEqual(criterion!.scale.max);
      }
    }
  });

  it('always emits a valid confidence level', async () => {
    for (const text of sampleTexts(150)) {
      const run = await runScoring(text, rubric);
      for (const draft of run.drafts) {
        expect(['low', 'medium', 'high']).toContain(draft.confidence);
      }
    }
  });

  it('emits one draft per criterion', async () => {
    const run = await runScoring(SEEDED_TEXT, rubric);
    expect(run.drafts.map((d) => d.criterionId).sort()).toEqual(
      rubric.criteria.map((c) => c.id).sort(),
    );
  });

  it('is deterministic for the same text', async () => {
    const a = await runScoring(SEEDED_TEXT, rubric);
    const b = await runScoring(SEEDED_TEXT, rubric);
    expect(b.drafts).toEqual(a.drafts);
  });

  it('pins a model and prompt version on every run', async () => {
    const run = await runScoring(SEEDED_TEXT, rubric);
    expect(run.modelVersion).toBeTruthy();
    expect(run.promptVersion).toBeTruthy();
  });

  it('deliberately perturbs the `evidence` quote so the safety net is exercised', async () => {
    // Acceptance check B depends on this: the seeded demo must show one red
    // "not verified" badge and green on the others.
    const run = await runScoring(SEEDED_TEXT, rubric);
    const statuses = new Map(
      run.drafts.map((d) => [d.criterionId, verifyQuote(SEEDED_TEXT, d.evidence).status]),
    );
    expect(statuses.get('evidence')).toBe('not_found');
    for (const id of ['claim', 'reasoning', 'structure']) {
      expect(statuses.get(id), `${id} should quote verbatim`).toBe('verified');
    }
  });
});
