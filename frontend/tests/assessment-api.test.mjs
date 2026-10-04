import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { stripTypeScriptTypes } from 'node:module';
import test from 'node:test';
import vm from 'node:vm';

// Execute the production TypeScript request modules without a test dependency.
// These are transport-contract tests; they do not render React or test live auth.
async function client({ base, token = 'synthetic-session', reply, browser = true } = {}) {
  const requests = [];
  const context = vm.createContext({
    process: { env: { NEXT_PUBLIC_API_URL: base } },
    ...(browser ? { window: {}, localStorage: { getItem: (key) => key === 'aeos_access_token' ? token : null } } : {}),
    fetch: async (url, options) => {
      requests.push({ url, options });
      return reply ? reply(url, options) : Response.json({ id: 'synthetic-result' }, { status: 201 });
    },
  });
  const modules = new Map();
  for (const name of ['api', 'assessments']) {
    const source = await readFile(new URL(`../src/lib/${name}.ts`, import.meta.url), 'utf8');
    modules.set(name, new vm.SourceTextModule(stripTypeScriptTypes(source), { context }));
  }
  await modules.get('assessments').link((specifier) => {
    assert.equal(specifier, './api');
    return modules.get('api');
  });
  await modules.get('assessments').evaluate();
  return { api: modules.get('api').namespace, assessments: modules.get('assessments').namespace, requests };
}

test('save sends a zero score and only review fields through the shared bearer client', async () => {
  const { assessments, requests } = await client();
  await assessments.saveAssessmentReview('assessment-a', {
    score: 0, max_score: 10, summary: 'Synthetic teacher findings', status: 'complete',
  });
  assert.equal(requests.length, 1);
  assert.equal(requests[0].url, '/api/assessment-results');
  assert.equal(requests[0].options.method, 'POST');
  assert.equal(requests[0].options.headers.Authorization, 'Bearer synthetic-session');
  assert.equal(requests[0].options.headers['Content-Type'], 'application/json');
  assert.deepEqual(JSON.parse(requests[0].options.body), {
    assessment_id: 'assessment-a', score: 0, max_score: 10,
    summary: 'Synthetic teacher findings', status: 'complete',
  });
});

test('intake and reads share the configured API base; assessment IDs are encoded', async () => {
  const { assessments, requests } = await client({ base: 'https://synthetic.example/api/' });
  await assessments.listAssessments();
  await assessments.getAssessment('id/with?reserved');
  await assessments.listAssessmentResults('id&other=tenant');
  await assessments.createAssessment({
    student_id: 'student-a', title: 'Synthetic assessment', assessment_type: 'reading', status: 'draft', notes: null,
  });
  assert.deepEqual(requests.map(({ url }) => url), [
    'https://synthetic.example/api/assessments',
    'https://synthetic.example/api/assessments/id%2Fwith%3Freserved',
    'https://synthetic.example/api/assessment-results?assessment_id=id%26other%3Dtenant',
    'https://synthetic.example/api/assessments',
  ]);
  assert.equal(JSON.parse(requests[3].options.body).student_id, 'student-a');
  assert.ok(!('organization_id' in JSON.parse(requests[3].options.body)));
  assert.ok(!('created_by' in JSON.parse(requests[3].options.body)));
});

test('no browser session never substitutes a credential and server-side token lookup is safe', async () => {
  for (const settings of [{ token: null }, { browser: false }]) {
    const { api, requests } = await client(settings);
    assert.equal(api.getAccessToken(), null);
    await api.apiFetch('/assessments');
    assert.ok(!('Authorization' in requests[0].options.headers));
  }
});

test('authorization, validation, and unavailable-service errors have usable messages', async () => {
  for (const [status, detail, message] of [
    [401, 'expired', 'Please sign in again to continue.'],
    [403, 'This action requires teacher or admin authorization', 'This action requires teacher or admin authorization'],
    [404, 'Assessment not found', 'Assessment not found'],
    [422, [{ msg: 'invalid input' }], 'Please check the values and try again.'],
    [500, 'internal stack trace', 'Request failed with status 500. Please try again.'],
  ]) {
    const { assessments } = await client({ reply: () => Response.json({ detail }, { status }) });
    await assert.rejects(assessments.listAssessmentResults('a'), (error) => error.message === message);
  }
  const { api } = await client({ reply: () => new Response('<html>proxy unavailable</html>', { status: 502 }) });
  await assert.rejects(api.apiFetch('/assessments'), (error) => error.message === 'Request failed with status 502. Please try again.');
});

test('request cancellation is forwarded and connection failures are not reported as saves', async () => {
  const controller = new AbortController();
  const failure = new TypeError('Synthetic connection failure');
  const { assessments, requests } = await client({ reply: () => { throw failure; } });
  await assert.rejects(assessments.saveAssessmentReview('a', {
    score: null, max_score: null, summary: 'Synthetic draft', status: 'draft',
  }, controller.signal), (error) => error === failure);
  assert.equal(requests[0].options.signal, controller.signal);
  assert.equal(JSON.parse(requests[0].options.body).score, null);
});

test('a successful read returns saved data and 204 returns no value', async () => {
  const reviews = [{ id: 'r', assessment_id: 'a', score: 0, summary: 'Synthetic persisted response', status: 'draft' }];
  const { assessments } = await client({ reply: () => Response.json(reviews) });
  assert.deepEqual(await assessments.listAssessmentResults('a'), reviews);
  const { api } = await client({ reply: () => new Response(null, { status: 204 }) });
  assert.equal(await api.apiFetch('/empty'), undefined);
});
