import { createHash } from 'node:crypto';
import { newId } from './ids';
import type { Rubric, Criterion } from './rubric';

export type ScoreDraft = {
  criterionId: string;
  score: number;
  rationale: string;
  evidence: string;
  confidence: 'low' | 'medium' | 'high';
};

export type ScoreRun = {
  id: string;
  modelVersion: string;
  promptVersion: string;
  drafts: ScoreDraft[];
};

export const MODEL_VERSION = process.env.SCORING_MODEL_VERSION ?? 'mock-1.0.0';
export const PROMPT_VERSION = process.env.SCORING_PROMPT_VERSION ?? 'rubric-v1';

export interface ScoringProvider {
  score(responseText: string, rubric: Rubric): Promise<ScoreDraft[]>;
}

// ---------- Mock provider (deterministic, default) ----------
class MockProvider implements ScoringProvider {
  async score(text: string, rubric: Rubric): Promise<ScoreDraft[]> {
    const sentences = text.match(/[^.!?]+[.!?]+/g) ?? [text];
    const seed = parseInt(createHash('sha256').update(text).digest('hex').slice(0, 8), 16);
    const pick = (i: number) => sentences[(seed + i) % sentences.length].trim();

    return rubric.criteria.map((c: Criterion, i) => {
      // `>>>` (unsigned), not `>>`: the seed is a 32-bit hash prefix whose top
      // bit is often set, and JS's signed shift would make it negative —
      // yielding out-of-scale scores and negative array indices.
      const score = c.scale.min + ((seed >>> i) % (c.scale.max - c.scale.min + 1));
      const realQuote = pick(i);
      // Deliberate perturbation on the "evidence" criterion so the review screen
      // exercises the not-verified safety net in the seeded demo.
      const evidence =
        c.id === 'evidence' ? perturb(realQuote) : realQuote;
      return {
        criterionId: c.id,
        score,
        rationale: `Mock rationale for "${c.label}": score ${score} based on ${realQuote.slice(0, 40)}…`,
        evidence,
        confidence: (['low', 'medium', 'high'] as const)[(seed >>> (i + 4)) % 3]!,
      };
    });
  }
}

function perturb(sentence: string): string {
  const words = sentence.split(/\s+/);
  if (words.length < 3) return sentence + ' (paraphrased)';
  words[Math.floor(words.length / 2)] = 'not-in-source';
  return words.join(' ');
}

// ---------- OpenAI provider (opt-in) ----------
class OpenAIProvider implements ScoringProvider {
  async score(text: string, rubric: Rubric): Promise<ScoreDraft[]> {
    const key = process.env.OPENAI_API_KEY;
    if (!key) throw new Error('OPENAI_API_KEY required for provider=openai');
    const rubricSummary = rubric.criteria
      .map((c) => `- ${c.id} (${c.label}, scale ${c.scale.min}-${c.scale.max}): ${c.description}`)
      .join('\n');
    const prompt = [
      'Score the following student response against the rubric.',
      'For EACH criterion, return JSON: {criterionId, score, rationale, evidence, confidence}.',
      'The `evidence` field MUST be a verbatim substring of the student response.',
      'Never paraphrase. If you cannot quote, use an empty string.',
      '',
      'RUBRIC:',
      rubricSummary,
      '',
      'RESPONSE:',
      text,
    ].join('\n');

    const res = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` },
      body: JSON.stringify({
        model: process.env.OPENAI_MODEL ?? 'gpt-4o-mini',
        response_format: { type: 'json_object' },
        messages: [
          { role: 'system', content: 'You are a rubric scorer. Reply with JSON {"drafts": [...]}.' },
          { role: 'user', content: prompt },
        ],
      }),
    });
    if (!res.ok) throw new Error(`openai ${res.status}: ${await res.text()}`);
    const json = (await res.json()) as { choices: { message: { content: string } }[] };
    const parsed = JSON.parse(json.choices[0].message.content) as { drafts: ScoreDraft[] };
    return parsed.drafts;
  }
}

export function getProvider(): ScoringProvider {
  const name = process.env.SCORING_PROVIDER ?? 'mock';
  return name === 'openai' ? new OpenAIProvider() : new MockProvider();
}

export async function runScoring(
  responseText: string,
  rubric: Rubric,
): Promise<ScoreRun> {
  const provider = getProvider();
  const drafts = await provider.score(responseText, rubric);
  return {
    id: newId('run'),
    modelVersion: MODEL_VERSION,
    promptVersion: PROMPT_VERSION,
    drafts,
  };
}
