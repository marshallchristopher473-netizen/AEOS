'use strict';

// Run with: node --test demo/pilot-review/tests/
const test = require('node:test');
const assert = require('node:assert/strict');

const Core = require('../pilot-core.js');
const Fx = require('../fixtures.js');

function responseOf(id) {
  return Fx.responses.find((r) => r.id === id);
}

function suggestionOf(id) {
  return Fx.suggestions.find((s) => s.responseId === id);
}

function newReview(id) {
  return Core.createReview(responseOf(id), suggestionOf(id));
}

function viewAll(review) {
  for (const cid of review.order) {
    for (const ev of review.criteria[cid].evidence) {
      if (ev.valid) Core.viewEvidence(review, ev.key);
    }
  }
}

function acceptAll(review) {
  viewAll(review);
  for (const cid of review.order) {
    const r = Core.setCriterionAction(review, cid, { action: 'accept' });
    assert.ok(r.ok, r.error);
  }
}

// ------------------------------------------------------------------ fixtures

test('fixtures: 12 synthetic responses, each with one matching suggestion', () => {
  assert.equal(Fx.responses.length, 12);
  assert.equal(Fx.suggestions.length, 12);
  for (const r of Fx.responses) {
    assert.match(r.id, /^R-\d{3}$/);
    assert.match(r.pseudonym, /^Student \d{2}$/);
    assert.ok(suggestionOf(r.id), 'missing suggestion for ' + r.id);
  }
});

test('fixtures: every suggestion scores every rubric criterion in range', () => {
  const ids = Fx.rubricDraft.criteria.map((c) => c.id);
  for (const s of Fx.suggestions) {
    assert.deepEqual(s.criteria.map((c) => c.criterionId), ids, s.responseId);
    for (const c of s.criteria) {
      assert.ok(c.score === null || (Number.isInteger(c.score) && c.score >= 0 && c.score <= 4), s.responseId + ' ' + c.criterionId);
    }
  }
});

test('fixtures: required hostile cases are present', () => {
  const flags = Fx.suggestions.flatMap((s) => s.flags);
  for (const f of ['BLANK', 'INSUFFICIENT', 'OFF_TOPIC', 'POSSIBLE_INSTRUCTION_IN_RESPONSE', 'WEAK_EVIDENCE', 'CONFLICTING_EVIDENCE', 'HIGH_UNCERTAINTY']) {
    assert.ok(flags.includes(f), 'missing ' + f);
  }
  const levels = new Set(Fx.suggestions.map((s) => s.uncertainty));
  assert.deepEqual([...levels].sort(), ['high', 'low', 'medium']);
});

test('fixtures: R-010 is the only response with an invalid evidence link', () => {
  for (const s of Fx.suggestions) {
    const text = responseOf(s.responseId).text;
    const invalid = s.criteria.flatMap((c) => c.evidence).filter((e) => !Core.validateEvidenceLink(text, e).valid);
    assert.equal(invalid.length, s.responseId === 'R-010' ? 1 : 0, s.responseId);
  }
});

test('fixtures: the injection response is not given full credit by the mock evaluator', () => {
  const s = suggestionOf('R-007');
  assert.ok(s.needsReview);
  assert.ok(s.criteria.some((c) => c.score < Core.SCORE_MAX));
});

// -------------------------------------------------------------------- rubric

test('rubric: approval deep-freezes and leaves the draft editable', () => {
  const approved = Core.approveRubric(Fx.rubricDraft, 'Demo Teacher', Fx.RUBRIC_APPROVED_AT);
  assert.equal(approved.status, 'APPROVED');
  assert.ok(Object.isFrozen(approved));
  assert.ok(Object.isFrozen(approved.criteria[0].levels));
  assert.throws(() => { approved.criteria[0].name = 'Changed'; }, TypeError);
  assert.equal(Fx.rubricDraft.status, undefined);
  assert.ok(!Object.isFrozen(Fx.rubricDraft));
});

test('rubric: a change produces a new draft version, never an edit', () => {
  const approved = Core.approveRubric(Fx.rubricDraft, 'Demo Teacher', Fx.RUBRIC_APPROVED_AT);
  const draft = Core.proposeRubricRevision(approved, { title: 'New title' });
  assert.equal(draft.version, '1.1');
  assert.equal(draft.status, 'DRAFT');
  assert.equal(draft.previousVersion, '1.0');
  assert.equal(draft.approvedBy, undefined);
  assert.equal(approved.title, Fx.rubricDraft.title);
});

test('rubric: approval rejects invalid rubrics and missing approver', () => {
  assert.throws(() => Core.approveRubric({ version: '1.0', criteria: [] }, 'X', 'now'), /at least one criterion/);
  assert.throws(() => Core.approveRubric(Fx.rubricDraft, '', 'now'), /approver/);
  const dup = JSON.parse(JSON.stringify(Fx.rubricDraft));
  dup.criteria[1].id = dup.criteria[0].id;
  assert.throws(() => Core.approveRubric(dup, 'X', 'now'), /Duplicate/);
});

// ------------------------------------------------------------------ evidence

test('evidence: validation requires the quote to match the exact offsets', () => {
  const text = 'abc def ghi';
  assert.deepEqual(Core.validateEvidenceLink(text, { quote: 'def', start: 4, end: 7 }), { valid: true, reason: null });
  assert.equal(Core.validateEvidenceLink(text, { quote: 'def', start: 3, end: 6 }).reason, 'QUOTE_MISMATCH');
  assert.equal(Core.validateEvidenceLink(text, { quote: 'def', start: 9, end: 40 }).reason, 'OFFSETS_OUT_OF_RANGE');
  assert.equal(Core.validateEvidenceLink(text, { quote: '', start: 0, end: 1 }).reason, 'MISSING_QUOTE');
  assert.equal(Core.validateEvidenceLink(text, { quote: 'a', start: 1.5, end: 2 }).reason, 'OFFSETS_OUT_OF_RANGE');
});

test('evidence: highlight segments reassemble the text and support overlaps', () => {
  const text = 'one two three four';
  const links = [
    { key: 'a', quote: 'two three', start: 4, end: 13 },
    { key: 'b', quote: 'three four', start: 8, end: 18 },
    { key: 'bad', quote: 'nope', start: 0, end: 4 },
  ];
  const segs = Core.buildHighlightSegments(text, links);
  assert.equal(segs.map((s) => s.text).join(''), text);
  assert.deepEqual(segs.find((s) => s.text === 'three').keys, ['a', 'b']);
  assert.ok(segs.every((s) => !s.keys.includes('bad')));
});

// -------------------------------------------------------------------- review

test('review: a criterion cannot be accepted until its evidence is located', () => {
  const review = newReview('R-001');
  const first = Core.setCriterionAction(review, 'evidence', { action: 'accept' });
  assert.equal(first.ok, false);
  assert.match(first.error, /Locate every evidence quote/);
  viewAll(review);
  assert.ok(Core.setCriterionAction(review, 'evidence', { action: 'accept' }).ok);
});

test('review: decisions are blocked until every criterion is inspected', () => {
  const review = newReview('R-001');
  const before = Core.allowedDecisions(review);
  assert.equal(before.ACCEPT.ok, false);
  assert.equal(before.REJECT.ok, false);
  acceptAll(review);
  const after = Core.allowedDecisions(review);
  assert.ok(after.ACCEPT.ok);
  assert.equal(after.REVISE.ok, false);
  assert.ok(after.REJECT.ok);
});

test('review: ACCEPT records the AI scores unchanged and needs no reason', () => {
  const review = newReview('R-011');
  acceptAll(review);
  const rec = Core.finalizeDecision(review, { decision: 'ACCEPT' }, 42000, 'T');
  assert.deepEqual(rec.finalScores, { claim: 4, evidence: 4, reasoning: 4, conventions: 4 });
  assert.equal(rec.activeMs, 42000);
  assert.ok(Object.isFrozen(rec));
  assert.ok(review.decided);
  assert.equal(Core.setCriterionAction(review, 'claim', { action: 'flag', reasonCode: 'CANNOT_SCORE' }).ok, false);
});

test('review: REVISE requires a revised criterion and a reason', () => {
  const review = newReview('R-012');
  acceptAll(review);
  const bad = Core.setCriterionAction(review, 'conventions', { action: 'revise', score: 2 });
  assert.equal(bad.ok, false);
  assert.match(bad.error, /reason/);
  assert.equal(Core.setCriterionAction(review, 'conventions', { action: 'revise', score: 7, reasonCode: 'SCORE_TOO_LOW' }).ok, false);
  assert.ok(Core.setCriterionAction(review, 'conventions', { action: 'revise', score: 2, reasonCode: 'SCORE_TOO_LOW' }).ok);
  assert.equal(Core.allowedDecisions(review).ACCEPT.ok, false);
  assert.equal(Core.validateDecision(review, { decision: 'REVISE' }).ok, false);
  assert.equal(Core.validateDecision(review, { decision: 'REVISE', reasonCode: 'OFF_TOPIC' }).ok, false);
  const rec = Core.finalizeDecision(review, { decision: 'REVISE', reasonCode: 'SCORES_ADJUSTED' }, 1000, 'T');
  assert.equal(rec.finalScores.conventions, 2);
  assert.equal(rec.aiScores.conventions, 1);
});

test('review: REJECT requires a reason and records no final scores', () => {
  const review = newReview('R-001');
  acceptAll(review);
  assert.throws(() => Core.finalizeDecision(review, { decision: 'REJECT' }, 0, 'T'), /requires a reason/);
  const rec = Core.finalizeDecision(review, { decision: 'REJECT', reasonCode: 'UNRELIABLE_SUGGESTION' }, 0, 'T');
  assert.ok(Object.values(rec.finalScores).every((v) => v === null));
});

test('review: blank responses cannot be accepted, only flagged and rejected', () => {
  const review = newReview('R-004');
  const r = Core.setCriterionAction(review, 'claim', { action: 'accept' });
  assert.equal(r.ok, false);
  assert.match(r.error, /No AI score/);
  for (const cid of review.order) {
    assert.ok(Core.setCriterionAction(review, cid, { action: 'flag', reasonCode: 'CANNOT_SCORE' }).ok);
  }
  const allowed = Core.allowedDecisions(review);
  assert.equal(allowed.ACCEPT.ok, false);
  assert.equal(allowed.REVISE.ok, false);
  assert.ok(allowed.REJECT.ok);
});

test('review: R-010 invalid evidence link blocks the criterion until explicitly rejected', () => {
  const review = newReview('R-010');
  const bad = review.criteria.evidence.evidence.find((e) => !e.valid);
  assert.equal(bad.invalidReason, 'QUOTE_MISMATCH');
  viewAll(review);

  for (const action of [{ action: 'accept' }, { action: 'revise', score: 2, reasonCode: 'EVIDENCE_MISREAD' }, { action: 'flag', reasonCode: 'INVALID_EVIDENCE' }]) {
    const r = Core.setCriterionAction(review, 'evidence', action);
    assert.equal(r.ok, false, action.action);
    assert.match(r.error, /INVALID EVIDENCE LINK/);
  }
  for (const cid of ['claim', 'reasoning', 'conventions']) Core.setCriterionAction(review, cid, { action: 'accept' });
  assert.deepEqual(Core.inspectionStatus(review).unresolvedEvidence, [bad.key]);
  assert.equal(Core.allowedDecisions(review).REJECT.ok, false);

  assert.ok(Core.rejectEvidence(review, bad.key).ok);
  const stillNoAccept = Core.setCriterionAction(review, 'evidence', { action: 'accept' });
  assert.equal(stillNoAccept.ok, false);
  assert.match(stillNoAccept.error, /rejected/);
  assert.ok(Core.setCriterionAction(review, 'evidence', { action: 'revise', score: 2, reasonCode: 'EVIDENCE_MISREAD' }).ok);
  assert.equal(Core.allowedDecisions(review).ACCEPT.ok, false);
  const rec = Core.finalizeDecision(review, { decision: 'REVISE', reasonCode: 'EVIDENCE_CORRECTED' }, 5000, 'T');
  assert.equal(rec.invalidEvidenceCount, 1);
  assert.equal(rec.invalidEvidenceRejected, 1);
});

test('review: rejecting evidence after accepting undoes the acceptance', () => {
  const review = newReview('R-001');
  acceptAll(review);
  const key = review.criteria.evidence.evidence[0].key;
  Core.rejectEvidence(review, key);
  assert.equal(review.criteria.evidence.action, null);
  assert.equal(Core.inspectionStatus(review).complete, false);
});

// --------------------------------------------------------------------- timer

test('timer: counts only visible time and pauses 60 s after the last input', () => {
  const t = Core.createActiveTimer({ idleMs: 60000 });
  t.setVisible(true, 0);
  t.activity(30000);
  assert.equal(t.elapsed(30000), 30000);
  assert.equal(t.elapsed(200000), 90000, 'stops 60 s after the last input');
  t.activity(210000);
  assert.equal(t.elapsed(220000), 100000, 'idle gap is not counted');
  t.setVisible(false, 225000);
  assert.equal(t.elapsed(900000), 105000, 'hidden time is not counted');
  t.setVisible(true, 1000000);
  assert.equal(t.elapsed(1010000), 115000);
});

test('timer: never runs before it is made visible and ignores clock going backwards', () => {
  const t = Core.createActiveTimer();
  t.activity(1000);
  assert.equal(t.elapsed(50000), 0);
  t.setVisible(true, 50000);
  assert.equal(t.elapsed(40000), 0);
  assert.equal(t.elapsed(55000), 5000);
});

// --------------------------------------------------------------------- audit

test('audit: append-only, frozen, sequenced entries', () => {
  let clock = 0;
  const log = Core.createAuditLog(() => (clock += 1000));
  log.append({ type: 'SESSION_STARTED', rubricVersion: '1.0' });
  const e = log.append({ type: 'DECISION_RECORDED', responseId: 'R-001', decision: 'ACCEPT', activeMs: 1234.4 });
  assert.equal(e.seq, 2);
  assert.equal(e.activeMs, 1234);
  assert.ok(Object.isFrozen(e));
  assert.throws(() => { e.decision = 'REJECT'; }, TypeError);
  const copy = log.entries();
  copy.pop();
  assert.equal(log.size(), 2);
  assert.equal(typeof log.remove, 'undefined');
  assert.equal(typeof log.update, 'undefined');
});

test('audit: drops unknown fields and refuses free text', () => {
  const log = Core.createAuditLog(() => 0);
  const e = log.append({ type: 'REVIEW_OPENED', responseId: 'R-002', text: 'student writing', pseudonym: 'Student 02' });
  assert.equal(e.text, undefined);
  assert.equal(e.pseudonym, undefined);
  assert.throws(() => log.append({ type: 'DECISION_RECORDED', reasonCode: 'the student wrote about a turtle' }), /identifier or code/);
  assert.throws(() => log.append({ type: 'NOT_A_TYPE' }), /Unknown audit event type/);
  assert.throws(() => log.append({ type: 'DECISION_RECORDED', activeMs: -5 }), /non-negative/);
});

// ----------------------------------------------------------------- dashboard

function decideAll() {
  const decisions = [];
  for (const r of Fx.responses) {
    const review = newReview(r.id);
    const s = suggestionOf(r.id);
    viewAll(review);
    for (const ev of review.order.flatMap((cid) => review.criteria[cid].evidence)) {
      if (!ev.valid) Core.rejectEvidence(review, ev.key);
    }
    const scorable = s.criteria.every((c) => c.score !== null) && !s.criteria.some((c) => c.evidence.some((e) => !Core.validateEvidenceLink(r.text, e).valid));
    if (scorable && !s.needsReview) {
      for (const cid of review.order) Core.setCriterionAction(review, cid, { action: 'accept' });
      decisions.push(Core.finalizeDecision(review, { decision: 'ACCEPT' }, 30000, 'T'));
    } else {
      for (const cid of review.order) Core.setCriterionAction(review, cid, { action: 'flag', reasonCode: 'NEEDS_SECOND_LOOK' });
      decisions.push(Core.finalizeDecision(review, { decision: 'REJECT', reasonCode: 'UNRELIABLE_SUGGESTION' }, 60000, 'T'));
    }
  }
  return decisions;
}

test('dashboard: aggregates decisions, rates and guardrails', () => {
  const decisions = decideAll();
  const d = Core.computeDashboard({ suggestions: Fx.suggestions, decisions: decisions, manualBaselineSec: 90 });
  assert.equal(d.mode, 'DEMO');
  assert.equal(d.synthetic, true);
  assert.equal(d.reviewedCount, 12);
  assert.equal(d.decisionSplit.ACCEPT + d.decisionSplit.REVISE + d.decisionSplit.REJECT, 12);
  assert.equal(d.needsReviewRate, Fx.suggestions.filter((s) => s.needsReview).length / 12);
  assert.equal(d.guardrails.invalidEvidencePresent, 1);
  assert.equal(d.guardrails.invalidEvidenceRejected, 1);
  assert.equal(d.guardrails.injectionFullCredit, 0);
  assert.equal(d.guardrails.unscorableAccepted, 0);
  assert.equal(d.guardrails.routedForReviewAccepted, 0);
  assert.equal(d.baseline.manualMedianSec, 90);
  assert.ok(d.baseline.differenceSec !== null);
  assert.match(d.baseline.label, /Not pilot evidence/);
});

test('dashboard: handles no decisions and an invalid baseline', () => {
  const d = Core.computeDashboard({ suggestions: Fx.suggestions, decisions: [], manualBaselineSec: -3 });
  assert.equal(d.medianActiveSec, null);
  assert.equal(d.overrideRate, null);
  assert.equal(d.baseline.manualMedianSec, null);
  assert.equal(d.baseline.differenceSec, null);
});

test('median: odd, even and empty inputs', () => {
  assert.equal(Core.median([3, 1, 2]), 2);
  assert.equal(Core.median([4, 1, 2, 3]), 2.5);
  assert.equal(Core.median([]), null);
});

// ------------------------------------------------------------------- exports

test('exports: aggregates only, with no response text, quotes, pseudonyms or IDs', () => {
  const d = Core.computeDashboard({ suggestions: Fx.suggestions, decisions: decideAll(), manualBaselineSec: 75 });
  const agg = Core.aggregatesForExport(d, '2026-10-24T00:00:00.000Z');
  const json = JSON.stringify(agg);
  const csv = Core.toCSV(agg);
  assert.equal(agg.mode, 'DEMO');
  assert.equal(agg.evidenceStatus, 'DEMO_SYNTHETIC_NOT_EVIDENCE');
  for (const value of Object.values(agg)) {
    assert.ok(value === null || ['number', 'boolean', 'string'].includes(typeof value));
  }
  const forbidden = [];
  for (const r of Fx.responses) {
    forbidden.push(r.id, r.pseudonym);
    if (r.text.length > 20) forbidden.push(r.text.slice(0, 20));
  }
  for (const s of Fx.suggestions) {
    for (const c of s.criteria) for (const e of c.evidence) if (e.quote.length > 8) forbidden.push(e.quote);
  }
  for (const f of forbidden) {
    assert.ok(!json.includes(f), 'JSON export leaks: ' + f);
    assert.ok(!csv.includes(f), 'CSV export leaks: ' + f);
  }
  assert.ok(csv.startsWith('metric,value\n'));
  assert.equal(csv.trim().split('\n').length, Object.keys(agg).length + 1);
});
