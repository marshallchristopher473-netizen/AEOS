/**
 * Regression suite for pbip-section-a/index.html.
 *
 * The app ships as ONE file so it can be emailed, copied to a USB stick or
 * opened straight from disk. To keep that property while still testing the
 * logic that decides whether something counts as "verified", this suite
 * extracts the <script id="aeos-logic"> block out of the HTML and runs it in a
 * node:vm context. No build step, no dependencies.
 *
 * Every test below corresponds to a defect confirmed in the audit of the
 * original prototype. If one fails, that defect is back.
 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const HERE = dirname(fileURLToPath(import.meta.url))
const HTML = readFileSync(join(HERE, '..', 'index.html'), 'utf8')

/**
 * Names the logic block is contracted to expose. Evaluating in the host realm
 * (rather than node:vm) keeps returned arrays and objects comparable with
 * assert.deepEqual — a vm realm has its own Array.prototype, so every
 * deepStrictEqual against a literal would fail for the wrong reason.
 * Listing the names here also makes their absence a test failure.
 */
const EXPORTS = [
  'STATUS', 'NAMES', 'LOCKED', 'PERM_KEYS', 'PERM_LABEL', 'DEF_KEYS', 'A1_REQUIRED',
  'MEASURES', 'EVIDENCE_KINDS', 'DAY_LABELS', 'CONTEXTS', 'CRITERIA', 'CRITERIA_IDS',
  'MIN_MINS', 'MAX_MINS', 'MIN_BASELINE_DAYS',
  'asString', 'oneOf', 'asMinutes', 'initialState', 'normalize',
  'qualifyingBaselineDays', 'verifiedKindCount', 'gateFailure', 'evidenceGateFailure',
  'permGateFailure', 'revalidate', 'nextAction', 'screenText', 'screenState',
  'verifiedCount', 'blockedCount', 'summaryText',
]

function logicSource() {
  const m = HTML.match(/<script id="aeos-logic">([\s\S]*?)<\/script>/)
  assert.ok(m, 'index.html must contain a <script id="aeos-logic"> block')
  return m[1]
}
const L = new Function(logicSource() + '\nreturn {' + EXPORTS.join(',') + '};')()

/** A state with the permissions needed to index and verify baseline evidence. */
function permitted(extra = {}) {
  const S = L.normalize({})
  S.permissions.team = 'verified'
  S.permissions.reuse = 'verified'
  S.permissions.baseline = 'verified'
  S.permissions.instructor = 'verified'
  Object.assign(S.permissions, extra)
  return S
}
const baselineRef = (code, day, mins = 20) => ({
  kind: 'Existing school FBA baseline', code, day, mins: String(mins),
  context: 'yes', status: 'verified',
})

// ---------------------------------------------------------------------------
// The logic block must stay pure, or this suite stops being able to load it.
// ---------------------------------------------------------------------------
test('logic block touches no DOM or storage API', () => {
  // Strip comments before checking: this is a check on CODE, not prose. A bare
  // substring match fires on an English word like "the 15-30 window" in a
  // comment, and a test that cries wolf is one someone eventually deletes.
  // Block comments only, plus whole-line // comments, so regex literals in the
  // identifier screen are left intact.
  const code = HTML.match(/<script id="aeos-logic">([\s\S]*?)<\/script>/)[1]
    .replace(/\/\*[\s\S]*?\*\//g, ' ')
    .replace(/^\s*\/\/.*$/gm, ' ')
  for (const forbidden of ['document', 'localStorage', 'window', 'alert', 'fetch', 'XMLHttpRequest']) {
    assert.ok(!new RegExp('\\b' + forbidden + '\\b').test(code),
      `logic block must not reference ${forbidden}`)
  }
})

// ---------------------------------------------------------------------------
// normalize() is the single trust boundary. The original had none: the load
// path merged per key and the import path did not, so a backup could install
// a state shape that crashed render() and bricked the app.
// ---------------------------------------------------------------------------
test('normalize survives garbage without throwing', () => {
  for (const bad of [null, undefined, 0, 'x', [], true, { criteria: 'nope' }]) {
    const S = L.normalize(bad)
    assert.equal(typeof S.permissions.reuse, 'string')
    assert.ok(Array.isArray(S.evidence))
    assert.ok(Array.isArray(S.decisions))
    assert.ok(Array.isArray(S.closeouts))
    assert.equal(typeof S.writing.reference, 'string')
    assert.equal(typeof S.submission.receipt, 'string')
  }
})

test('normalize backfills every key a partial backup omits', () => {
  // The exact shape that bricked the prototype: containers present, keys absent.
  const S = L.normalize({ permissions: { baseline: 'verified' }, criteria: {}, definition: { setting: 'gym' } })
  assert.equal(S.permissions.reuse, 'unresolved', 'missing permission must not be undefined')
  assert.equal(S.definition.action, '', 'missing definition field must not be undefined')
  assert.equal(S.criteria.A1, 'unresolved')
  assert.equal(S.writing.reference, '', 'setNested would throw on undefined here')
})

test('normalize rejects values outside the status enum', () => {
  const evil = '"><img/src=x/onerror=alert(1)>'
  const S = L.normalize({ permissions: { reuse: evil }, criteria: { A1: evil }, definition: {} })
  assert.equal(S.permissions.reuse, 'unresolved')
  assert.equal(S.criteria.A1, 'unresolved')
  assert.ok(!JSON.stringify(S).includes('onerror'), 'no injected markup may survive normalization')
})

test('normalize re-applies the locked permissions', () => {
  const S = L.normalize({ permissions: { existing: 'blocked', additional: 'verified', mentor: 'unresolved' }, criteria: {}, definition: {} })
  assert.equal(S.permissions.existing, 'verified')
  assert.equal(S.permissions.additional, 'blocked', 'additional observations must stay blocked')
  assert.equal(S.permissions.mentor, 'verified')
})

test('normalize coerces evidence rows and drops duplicate codes', () => {
  const S = L.normalize({
    permissions: {}, criteria: {}, definition: {},
    evidence: [
      { kind: 'Existing school FBA baseline', code: 'A-1', day: 'Day 9', mins: '999', context: 'maybe', status: 'excellent' },
      { kind: 'Existing record review', code: 'A-1' },
      null, 'nope', { code: '' },
    ],
  })
  assert.equal(S.evidence.length, 1, 'duplicate, null and empty-code rows are dropped')
  const e = S.evidence[0]
  assert.equal(e.kind, 'Existing school FBA baseline')
  assert.equal(e.day, '', 'unknown day label falls back to unknown')
  assert.equal(e.mins, '', 'out-of-range minutes are dropped')
  assert.equal(e.context, 'unresolved')
  assert.equal(e.status, 'unresolved')
})

test('asMinutes accepts only whole minutes, never by truncation', () => {
  for (const ok of [['20', '20'], ['15', '15'], [' 30 ', '30'], [30, '30'], ['120', '120'], ['1', '1']])
    assert.equal(L.asMinutes(ok[0]), ok[1], `should accept ${JSON.stringify(ok[0])}`)
  // parseInt() would turn these into 30, 14 and 1 respectively.
  for (const bad of ['30.9', 30.9, '14.2', '1e3', '-5', '0', '121', '', 'abc', null, undefined, {}])
    assert.equal(L.asMinutes(bad), '', `should reject ${JSON.stringify(bad)}`)
})

test('a 30.9-minute reference cannot be truncated into the A3 window', () => {
  const S = L.normalize({
    permissions: { team: 'verified', reuse: 'verified', baseline: 'verified', instructor: 'verified' },
    criteria: {}, definition: {},
    evidence: [
      { kind: 'Existing school FBA baseline', code: 'A', day: 'Day 1', mins: '30.9', context: 'yes', status: 'verified' },
      { kind: 'Existing school FBA baseline', code: 'B', day: 'Day 2', mins: '30.9', context: 'yes', status: 'verified' },
    ],
  })
  assert.deepEqual(S.evidence.map(e => e.mins), ['', ''], 'an unreadable duration is not a duration')
  assert.equal(L.qualifyingBaselineDays(S), 0)
  assert.match(L.gateFailure(S, 'A3'), /DIFFERENT days/)
})

test('an unrecognised evidence kind is dropped, never defaulted to the baseline kind', () => {
  assert.equal(L.EVIDENCE_KINDS[0], 'Existing school FBA baseline',
    'the first kind is the privileged one, which is why defaulting to it is unsafe')
  const S = L.normalize({
    permissions: { team: 'verified', reuse: 'verified', baseline: 'verified', instructor: 'verified' },
    criteria: {}, definition: {},
    evidence: [
      { kind: 'totally bogus', code: 'X', day: 'Day 1', mins: '20', context: 'yes', status: 'verified' },
      { code: 'Y', day: 'Day 2', mins: '20', context: 'yes', status: 'verified' },
      { kind: 'Existing record review', code: 'Z' },
    ],
  })
  assert.deepEqual(S.evidence.map(e => e.code), ['Z'], 'only the row naming a real source survives')
  assert.equal(L.qualifyingBaselineDays(S), 0)
  assert.match(L.gateFailure(S, 'A3'), /DIFFERENT days/)
})

test('revoking school-team coordination demotes reuse and everything under it', () => {
  const S = L.normalize({
    permissions: { team: 'verified', reuse: 'verified' }, criteria: { A2: 'verified' }, definition: {},
  })
  assert.deepEqual(L.revalidate(S), [], 'consistent while the whole chain holds')
  S.permissions.team = 'unresolved'
  const demoted = L.revalidate(S)
  assert.equal(S.permissions.reuse, 'unresolved', 'a permission may not outlive its own prerequisite')
  assert.equal(S.criteria.A2, 'unresolved', 'and the cascade must reach the criteria beneath it')
  assert.ok(demoted.some(d => d.what.includes('Permission')))
  assert.ok(demoted.some(d => d.what.includes('A2')))
})

test('a permission chain broken in an imported backup is repaired on load', () => {
  const S = L.normalize({
    permissions: { team: 'unresolved', reuse: 'verified', baseline: 'verified' },
    criteria: { A2: 'verified' }, definition: {},
    evidence: [{ kind: 'Existing school FBA baseline', code: 'A', day: 'Day 1', mins: '20', context: 'yes', status: 'verified' }],
  })
  L.revalidate(S)
  assert.equal(S.permissions.reuse, 'unresolved')
  assert.equal(S.criteria.A2, 'unresolved')
  assert.equal(S.evidence[0].status, 'unresolved', 'evidence authorized by the revoked chain goes too')
})

test('normalize maps the legacy "Other distinct day" label', () => {
  const S = L.normalize({
    permissions: {}, criteria: {}, definition: {},
    evidence: [{ kind: 'Existing school FBA baseline', code: 'X-1', day: 'Other distinct day' }],
  })
  assert.equal(S.evidence[0].day, 'Day 3')
})

test('normalize is idempotent', () => {
  const once = L.normalize({ permissions: { reuse: 'verified' }, criteria: {}, definition: {}, closeouts: ['a', '', 'b'] })
  assert.deepEqual(L.normalize(JSON.parse(JSON.stringify(once))), once)
})

// ---------------------------------------------------------------------------
// A3: "Two separate days, same context, 15-30 minutes each."
// The original counted rows and never read the day label it collected.
// ---------------------------------------------------------------------------
test('A3 rejects two references on the SAME day', () => {
  const S = permitted()
  S.evidence = [baselineRef('I-1', 'Day 1'), baselineRef('I-2', 'Day 1')]
  assert.equal(L.qualifyingBaselineDays(S), 1)
  assert.match(L.gateFailure(S, 'A3'), /DIFFERENT days/)
})

test('A3 accepts two references on different days', () => {
  const S = permitted()
  S.evidence = [baselineRef('I-1', 'Day 1'), baselineRef('I-2', 'Day 2')]
  assert.equal(L.qualifyingBaselineDays(S), 2)
  assert.equal(L.gateFailure(S, 'A3'), null)
})

test('A3 ignores references with an unknown day', () => {
  const S = permitted()
  S.evidence = [baselineRef('I-1', 'Day 1'), baselineRef('I-2', '')]
  assert.equal(L.qualifyingBaselineDays(S), 1, 'an unknown day cannot establish distinctness')
})

test('A3 enforces the duration window and the context clause', () => {
  const S = permitted()
  S.evidence = [baselineRef('I-1', 'Day 1', 14), baselineRef('I-2', 'Day 2', 31)]
  assert.equal(L.qualifyingBaselineDays(S), 0)
  S.evidence = [baselineRef('I-1', 'Day 1'), baselineRef('I-2', 'Day 2')]
  S.evidence[1].context = 'no'
  assert.equal(L.qualifyingBaselineDays(S), 1)
})

test('A3 requires instructor acceptance, matching what nextAction demands', () => {
  const S = permitted({ instructor: 'unresolved' })
  S.evidence = [baselineRef('I-1', 'Day 1'), baselineRef('I-2', 'Day 2')]
  assert.match(L.gateFailure(S, 'A3'), /Instructor case acceptance/)
})

// ---------------------------------------------------------------------------
// Gates must hold continuously. The original checked them only at the instant
// of the click, so revoking a permission left "verified" on screen.
// ---------------------------------------------------------------------------
test('revoking a permission demotes the criteria that rested on it', () => {
  const S = permitted()
  S.criteria.A2 = 'verified'
  assert.deepEqual(L.revalidate(S), [], 'nothing to demote while the permission holds')
  S.permissions.reuse = 'unresolved'
  const demoted = L.revalidate(S)
  assert.equal(S.criteria.A2, 'unresolved', 'A2 must not survive its permission being revoked')
  assert.ok(demoted.some(d => d.what.includes('A2')))
  assert.match(demoted[0].why, /not verified/)
})

test('revalidate reaches a fixed point through A3 to A5', () => {
  const S = permitted()
  S.evidence = [baselineRef('I-1', 'Day 1'), baselineRef('I-2', 'Day 2')]
  S.criteria.A3 = 'verified'
  S.criteria.A5 = 'verified'
  assert.deepEqual(L.revalidate(S), [])
  // Removing one day invalidates A3, which must cascade to A5 in one sweep.
  S.evidence.pop()
  const demoted = L.revalidate(S)
  assert.equal(S.criteria.A3, 'unresolved')
  assert.equal(S.criteria.A5, 'unresolved', 'A5 rests on A3 and must cascade')
  assert.equal(demoted.length, 2)
})

test('revoking a permission demotes verified evidence rows too', () => {
  const S = permitted()
  S.evidence = [baselineRef('I-1', 'Day 1')]
  S.permissions.baseline = 'unresolved'
  const demoted = L.revalidate(S)
  assert.equal(S.evidence[0].status, 'unresolved')
  assert.ok(demoted.some(d => d.what.includes('I-1')))
})

test('clearing the draft reference retracts the writing status', () => {
  const S = permitted()
  S.writing.reference = 'PBIP_A_draft_v1'
  S.writing.status = 'verified'
  assert.deepEqual(L.revalidate(S), [], 'holds while the reference is present')
  S.writing.reference = ''
  const demoted = L.revalidate(S)
  assert.equal(S.writing.status, 'unresolved', 'a status may not outlive the field it was gated on')
  assert.ok(demoted.some(d => d.what === 'Writing status'))
})

test('clearing the receipt retracts the submission status', () => {
  const S = permitted()
  S.submission.receipt = 'BB-2026-11-17'
  S.submission.status = 'verified'
  assert.deepEqual(L.revalidate(S), [])
  S.submission.receipt = '   '
  L.revalidate(S)
  assert.equal(S.submission.status, 'unresolved')
})

test('clearing a definition field retracts A1', () => {
  const S = permitted()
  for (const k of L.A1_REQUIRED) S.definition[k] = 'x'
  S.criteria.A1 = 'verified'
  assert.deepEqual(L.revalidate(S), [])
  S.definition.onset = ''
  L.revalidate(S)
  assert.equal(S.criteria.A1, 'unresolved')
})

test('revalidate leaves a consistent state alone', () => {
  const S = permitted()
  S.evidence = [baselineRef('I-1', 'Day 1'), baselineRef('I-2', 'Day 2')]
  S.criteria.A3 = 'verified'
  assert.deepEqual(L.revalidate(S), [])
  assert.equal(S.criteria.A3, 'verified')
})

// ---------------------------------------------------------------------------
// Each criterion must test what its own text claims.
// ---------------------------------------------------------------------------
test('A1 requires every clause of its definition, not just the action', () => {
  const S = L.normalize({})
  S.definition.action = 'leaves the assigned area'
  const why = L.gateFailure(S, 'A1')
  assert.match(why, /onset/)
  assert.match(why, /offset/)
  assert.match(why, /exclusions/)
  assert.match(why, /rule/)
  for (const k of ['onset', 'offset', 'exclusions', 'rule']) S.definition[k] = 'x'
  assert.equal(L.gateFailure(S, 'A1'), null)
  assert.equal(S.definition.impact, '', 'impact stays out of the gate by design')
})

test('A4 requires verified references of two different kinds', () => {
  const S = permitted()
  S.evidence = [baselineRef('I-1', 'Day 1'), baselineRef('I-2', 'Day 2')]
  assert.match(L.gateFailure(S, 'A4'), /different kinds/)
  S.evidence.push({ kind: 'Existing record review', code: 'R-1', day: '', mins: '', context: 'unresolved', status: 'verified' })
  assert.equal(L.gateFailure(S, 'A4'), null)
})

test('A5 requires A3 to be verified first', () => {
  const S = permitted()
  assert.match(L.gateFailure(S, 'A5'), /A3 must be verified/)
  S.evidence = [baselineRef('I-1', 'Day 1'), baselineRef('I-2', 'Day 2')]
  S.criteria.A3 = 'verified'
  assert.equal(L.gateFailure(S, 'A5'), null)
})

test('an indexed family reference makes the family pathway a gate', () => {
  const S = permitted()
  S.evidence = [{ kind: 'Family input via approved channel', code: 'F-1', day: '', mins: '', context: 'unresolved', status: 'unresolved' }]
  assert.match(L.gateFailure(S, 'A2'), /family/i)
  S.permissions.family = 'verified'
  assert.equal(L.gateFailure(S, 'A2'), null)
})

test('W requires a draft reference', () => {
  const S = permitted()
  assert.match(L.gateFailure(S, 'W'), /draft reference/)
  S.writing.reference = 'PBIP_A_draft_v1'
  assert.equal(L.gateFailure(S, 'W'), null)
})

test('coursework reuse cannot be verified before the school team is identified', () => {
  const S = L.normalize({})
  assert.match(L.permGateFailure(S, 'reuse', 'verified'), /School-team coordination/)
  S.permissions.team = 'verified'
  assert.equal(L.permGateFailure(S, 'reuse', 'verified'), null)
  assert.equal(L.permGateFailure(S, 'reuse', 'unresolved'), null, 'downgrades are always allowed')
})

test('evidence cannot be verified ahead of its authorizing permission', () => {
  const S = L.normalize({})
  const e = baselineRef('I-1', 'Day 1')
  assert.match(L.evidenceGateFailure(S, e), /coursework reuse/i)
  S.permissions.reuse = 'verified'
  assert.match(L.evidenceGateFailure(S, e), /baseline equivalence/i)
  S.permissions.baseline = 'verified'
  assert.equal(L.evidenceGateFailure(S, e), null)
})

// ---------------------------------------------------------------------------
// nextAction must stay truthful, including at the end.
// ---------------------------------------------------------------------------
test('nextAction walks the permission chain in order', () => {
  const S = L.normalize({})
  assert.match(L.nextAction(S)[0], /school FBA lead/i)
  S.permissions.team = 'verified'
  assert.match(L.nextAction(S)[0], /coursework-reuse/i)
  S.permissions.reuse = 'verified'
  assert.match(L.nextAction(S)[0], /baseline equivalence/i)
})

test('nextAction has a terminal state and does not claim it is a grade', () => {
  const S = permitted()
  // A consistent terminal state: the definition must be complete, or A1 could
  // not have been verified in the first place.
  for (const k of L.A1_REQUIRED) S.definition[k] = 'x'
  S.evidence = [baselineRef('I-1', 'Day 1'), baselineRef('I-2', 'Day 2'),
  { kind: 'Existing record review', code: 'R-1', day: '', mins: '', context: 'unresolved', status: 'verified' }]
  S.writing.reference = 'PBIP_A_draft_v1'
  for (const k of L.CRITERIA_IDS) S.criteria[k] = 'verified'
  assert.deepEqual(L.revalidate(S), [], 'the terminal state must be self-consistent')
  const [title, body] = L.nextAction(S)
  assert.match(title, /All six criteria/)
  assert.match(body, /not an instructor grade/)
})

test('nextAction explains why the criterion it names is blocked', () => {
  const S = permitted()
  for (const k of ['onset', 'offset', 'exclusions', 'rule', 'action']) S.definition[k] = 'x'
  S.criteria.A1 = 'verified'
  S.criteria.A2 = 'verified'
  const [, body] = L.nextAction(S)
  assert.ok(body.length > 0)
})

// ---------------------------------------------------------------------------
// The export must not assert de-identification it has not checked.
// ---------------------------------------------------------------------------
test('the readable summary never claims "no raw data" unconditionally', () => {
  const S = L.normalize({})
  assert.ok(!L.summaryText(S).includes('no raw data'))
  assert.ok(!HTML.includes('Student A; no raw data'), 'the hard-coded attestation must be gone')
})

test('a clean summary says the screen found nothing, not that the file is safe', () => {
  const text = L.summaryText(L.normalize({}))
  assert.match(text, /no flags raised/i)
  assert.match(text, /not a guarantee/i)
})

test('the summary reports what the identifier screen actually found', () => {
  const S = L.normalize({})
  S.definition.setting = 'meets with Ms. Carter on 03/14'
  const text = L.summaryText(S)
  assert.match(text, /FLAGGED/)
  assert.match(text, /Measurement · setting/)
})

test('the readable summary carries every section the JSON backup carries', () => {
  const S = L.normalize({})
  S.closeouts = ['Completed the definition; next verify reuse']
  const text = L.summaryText(S)
  assert.match(text, /CLOSEOUTS/, 'closeouts were silently dropped by the original')
  assert.ok(text.includes('Completed the definition'))
  for (const section of ['PERMISSIONS', 'CRITERIA', 'DEFINITION', 'EVIDENCE INDEX', 'DECISIONS', 'WRITING', 'SUBMISSION']) {
    assert.match(text, new RegExp(section))
  }
})

// ---------------------------------------------------------------------------
// The identifier screen is advisory. It must catch the obvious cases without
// firing on ordinary de-identified planning text.
// ---------------------------------------------------------------------------
test('the screen flags obvious identifiers', () => {
  assert.deepEqual(L.screenText('spoke with Ms. Carter'), ['a title followed by a name'])
  assert.ok(L.screenText('observed 03/14/2026').includes('a date'))
  assert.ok(L.screenText('on Nov 17 at lunch').includes('a date'))
  assert.ok(L.screenText('email parent@example.com').includes('an email address'))
  assert.ok(L.screenText('call 555-867-5309').includes('a phone number'))
  assert.ok(L.screenText('moved to Room 214').includes('a room number'))
  assert.ok(L.screenText('id 887312').includes('a run of four or more digits'))
})

test('the screen stays quiet on ordinary de-identified text', () => {
  for (const ok of [
    'leaves the assigned area without permission',
    'starts when the student crosses the taped boundary',
    'ends after 10 consecutive seconds in area',
    'frequency count per 15 minute block',
    '',
  ]) assert.deepEqual(L.screenText(ok), [], `should not flag: ${ok}`)
})

test('screenState reports where each flag came from', () => {
  const S = L.normalize({})
  S.closeouts = ['called 555-123-4567']
  const flags = L.screenState(S)
  // A phone number also trips the four-or-more-digits rule; overlapping
  // reasons are fine for an advisory screen, so assert on origin and content.
  assert.ok(flags.length >= 1)
  assert.ok(flags.every(f => f.where === 'Closeout 1'))
  assert.ok(flags.some(f => f.why === 'a phone number'))
})

// ---------------------------------------------------------------------------
// Counters feed the dashboard; they must not read reassuringly by accident.
// ---------------------------------------------------------------------------
test('verifiedCount and blockedCount track the real state', () => {
  const S = L.normalize({})
  assert.equal(L.verifiedCount(S), 0)
  assert.equal(L.blockedCount(S), 2, 'A3 and A5 start blocked')
  S.criteria.A1 = 'verified'
  assert.equal(L.verifiedCount(S), 1)
})
