import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { stripTypeScriptTypes } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';

// Transport-contract tests for the AI feedback client. They execute the real
// TypeScript modules against synthetic fetch responses; no provider exists here.
async function client({ reply } = {}) {
  const requests = [];
  const context = vm.createContext({
    process: { env: {} },
    window: {},
    localStorage: { getItem: (key) => key === 'aeos_access_token' ? 'synthetic-session' : null },
    crypto: { randomUUID: () => '00000000-0000-4000-8000-00000000abcd' },
    fetch: async (url, options) => {
      requests.push({ url, options });
      return reply ? reply(url, options) : Response.json({ id: 'synthetic-draft' }, { status: 201 });
    },
  });
  const modules = new Map();
  for (const name of ['api', 'aiFeedback']) {
    const source = await readFile(new URL(`../src/lib/${name}.ts`, import.meta.url), 'utf8');
    modules.set(name, new vm.SourceTextModule(stripTypeScriptTypes(source), { context }));
  }
  await modules.get('aiFeedback').link((specifier) => {
    assert.equal(specifier, './api');
    return modules.get('api');
  });
  await modules.get('aiFeedback').evaluate();
  return { api: modules.get('api').namespace, feedback: modules.get('aiFeedback').namespace, requests };
}

test('draft request sends only synthetic input, the pinned rubric and an idempotency key', async () => {
  const { feedback, requests } = await client();
  await feedback.requestFeedbackDraft(
    { assessment_id: 'assessment-a', response_text: 'Synthetic response.', source_text: 'Synthetic passage.' },
    'key-1',
  );
  const [{ url, options }] = requests;
  assert.equal(url, '/api/ai-feedback/drafts');
  assert.equal(options.method, 'POST');
  assert.equal(options.headers['Idempotency-Key'], 'key-1');
  assert.equal(options.headers.Authorization, 'Bearer synthetic-session');
  assert.deepEqual(JSON.parse(options.body), {
    assessment_id: 'assessment-a',
    rubric_id: 'RUB-CER3',
    rubric_version: '0.1',
    response_text: 'Synthetic response.',
    source_text: 'Synthetic passage.',
    data_classification: 'synthetic',
  });
});

test('no provider, model, prompt or authority field can be sent from the browser', async () => {
  const { feedback, requests } = await client();
  await feedback.requestFeedbackDraft({ assessment_id: 'a', response_text: 'r', source_text: null }, 'k');
  const body = JSON.parse(requests[0].options.body);
  for (const field of ['model', 'model_id', 'system', 'prompt', 'organization_id', 'created_by', 'student_id', 'source_text']) {
    assert.ok(!(field in body), field);
  }
});

test('decisions always carry the explicit teacher confirmation and encode the draft id', async () => {
  const { feedback, requests } = await client();
  await feedback.recordFeedbackDecision('draft/1?x', { decision: 'revised', approved_text: 'Teacher text', review_flags_acknowledged: true }, 'k1');
  await feedback.recordFeedbackDecision('draft-2', { decision: 'rejected', approved_text: 'ignored', review_flags_acknowledged: false }, 'k2');

  assert.equal(requests[0].url, '/api/ai-feedback/drafts/draft%2F1%3Fx/decisions');
  assert.deepEqual(JSON.parse(requests[0].options.body), {
    decision: 'revised', approved_text: 'Teacher text', review_flags_acknowledged: true, teacher_confirmed: true,
  });
  assert.deepEqual(JSON.parse(requests[1].options.body), {
    decision: 'rejected', review_flags_acknowledged: false, teacher_confirmed: true,
  });
  assert.equal(requests[1].options.headers['Idempotency-Key'], 'k2');
});

test('list encodes the assessment id', async () => {
  const { feedback, requests } = await client({ reply: () => Response.json([]) });
  assert.deepEqual(await feedback.listFeedbackDrafts('a&assessment_id=other'), []);
  assert.equal(requests[0].url, '/api/ai-feedback/drafts?assessment_id=a%26assessment_id%3Dother');
});

test('sanitized server errors keep their code and fixed message, including 5xx', async () => {
  for (const [status, code, message] of [
    [503, 'feature_disabled', 'AI feedback drafting is not enabled.'],
    [503, 'provider_unavailable', 'The AI provider is unavailable. Try again later.'],
    [429, 'org_budget_exceeded', 'Your organization has reached its daily spending limit for AI drafts.'],
    [502, 'invalid_model_output', 'The AI output failed safety validation and was discarded.'],
    [409, 'idempotency_key_reused', 'This Idempotency-Key was already used for a different request.'],
  ]) {
    const { feedback, api } = await client({ reply: () => Response.json({ detail: { code, message, draft_id: 'd' } }, { status }) });
    await assert.rejects(
      feedback.requestFeedbackDraft({ assessment_id: 'a', response_text: 'r', source_text: null }, 'k'),
      (error) => error instanceof api.ApiError && error.code === code && error.status === status && error.message === message,
    );
  }
});

test('a new idempotency key comes from the platform UUID generator', async () => {
  const { feedback } = await client();
  assert.equal(feedback.newIdempotencyKey(), '00000000-0000-4000-8000-00000000abcd');
});
