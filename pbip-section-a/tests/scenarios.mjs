// Re-runs the exact scenarios that broke the original prototype, against the
// hardened build. Each must now behave correctly.
import { readFileSync } from 'node:fs'
import vm from 'node:vm'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

// Defaults to the sibling index.html. Pass a path to run the same scenarios
// against another build — e.g. the original prototype at this directory's first
// commit, which must still FAIL, or the suite has stopped detecting anything:
//   git show <baseline-sha>:pbip-section-a/index.html > /tmp/original.html
//   node pbip-section-a/tests/scenarios.mjs /tmp/original.html
const HERE = dirname(fileURLToPath(import.meta.url))
const FILE = process.argv[2] || join(HERE, '..', 'index.html')
const HTML = readFileSync(FILE, 'utf8')
const blocks = [...HTML.matchAll(/<script(?: id="[^"]*")?>([\s\S]*?)<\/script>/g)].map(m => m[1])
// Expose the live state object for assertions; `S` is a var inside the script.
const SRC = blocks.join('\n;\n') + '\n;globalThis.__S=function(){return S};'

function boot(stored, defer) {
  const els = new Map(), store = new Map(), alerts = [], confirms = [], handlers = {}, timers = []
  if (stored !== undefined) store.set('aeos_pbi_section_a', stored)
  // A real browser DESTROYS and recreates children when innerHTML is assigned.
  // The stub must too: otherwise a stale element keeps its old value and a test
  // can pass while the behaviour it names is broken.
  const STABLE = new Set(['tabs', 'view', 'announce'])
  const mk = (id) => {
    const el = { value: '', textContent: '', files: [], focus() {} }
    let html = ''
    Object.defineProperty(el, 'innerHTML', {
      get: () => html,
      set: (v) => {
        html = v
        if (id === 'view') for (const k of [...els.keys()]) if (!STABLE.has(k)) els.delete(k)
      },
    })
    return el
  }
  const ctx = {
    structuredClone, JSON, Object, Array, String, Number, Math, isFinite, parseInt, RegExp, Date, Promise,
    console, URL: { createObjectURL: () => 'blob:x', revokeObjectURL() {} },
    Blob: class { constructor(p) { ctx.__lastBlob = String(p[0]) } },
    // defer=true queues timers instead of running them, so the debounce
    // genuinely stays pending and the page-exit flush can be tested.
    setTimeout: (f) => { if (defer) { timers.push(f); return timers.length } f(); return 0 },
    clearTimeout: (id) => { if (defer && id) timers[id - 1] = null },
    alert: m => alerts.push(m), confirm: m => { confirms.push(m); return true },
    localStorage: {
      getItem: k => (store.has(k) ? store.get(k) : null),
      setItem: (k, v) => store.set(k, v),
      removeItem: k => store.delete(k),
    },
    window: {
      scrollTo() {},
      addEventListener(ev, fn) { (handlers[ev] = handlers[ev] || []).push(fn) },
    },
    document: {
      getElementById(id) { if (!els.has(id)) els.set(id, mk(id)); return els.get(id) },
      visibilityState: 'visible',
      querySelector: () => null,
      createElement: () => ({ click() {}, set href(_) {}, set download(_) {} }),
    },
  }
  ctx.globalThis = ctx
  vm.createContext(ctx)
  const err = (() => { try { vm.runInContext(SRC, ctx); return null } catch (e) { return e } })()
  const fire = (ev) => (handlers[ev] || []).forEach(f => f())
  const runTimers = () => { const t = timers.filter(Boolean); timers.length = 0; t.forEach(f => f()) }
  return { ctx, els, store, alerts, confirms, handlers, fire, timers, runTimers, bootError: err }
}

let pass = 0, fail = 0
const check = (name, ok, detail = '') => {
  if (ok) { pass++; console.log('  PASS  ' + name) }
  else { fail++; console.log('  FAIL  ' + name + (detail ? '  -> ' + detail : '')) }
}
const view = els => (els.get('view') || { innerHTML: '' }).innerHTML
async function section(label, fn) { console.log('\n' + label); try { await fn() } catch (e) { check(label + ' (threw)', false, e.message) } }

await section('1. corrupt persisted state must not brick the app', async () => {
  const bad = JSON.stringify({ permissions: { reuse: null }, criteria: {}, definition: {}, evidence: null })
  const { els, bootError } = boot(bad)
  check('boots without throwing', bootError === null, bootError && bootError.message)
  check('view is rendered, not blank', view(els).length > 100, 'len=' + view(els).length)
})

await section('2. a backup that cannot be drawn must not destroy saved work', async () => {
  const good = JSON.stringify({ permissions: { reuse: 'verified', team: 'verified' }, criteria: { A1: 'verified' }, definition: { action: 'a', onset: 'b', offset: 'c', exclusions: 'd', rule: 'e' } })
  const { ctx, store } = boot(good)
  const before = store.get('aeos_pbi_section_a')
  await ctx.importData({ text: async () => 'not json at all' })
  check('invalid JSON leaves storage untouched', store.get('aeos_pbi_section_a') === before)
  await ctx.importData({ text: async () => JSON.stringify([1, 2, 3]) })
  check('non-object backup leaves storage untouched', store.get('aeos_pbi_section_a') === before)
})

await section('3. injected markup must never reach the DOM', async () => {
  const evil = '"><img/src=x/onerror=STEAL()>'
  const { ctx, els } = boot(undefined)
  await ctx.importData({ text: async () => JSON.stringify({ permissions: { reuse: evil }, criteria: { A1: evil }, definition: { setting: evil }, closeouts: [evil] }) })
  ctx.go('dashboard')
  const d = view(els)
  check('no live element from payload on dashboard', !d.includes('<img/src=x'), d.slice(Math.max(0, d.indexOf('STEAL') - 60), 40))
  ctx.go('completion')
  check('payload escaped in closeout text', !view(els).includes('<img/src=x'))
  check('no onerror handler anywhere', !d.includes('onerror=STEAL'))
})

await section('4. A3 must require two DIFFERENT days', async () => {
  const { ctx, els } = boot(undefined)
  ctx.setPerm('team', 'verified'); ctx.setPerm('reuse', 'verified')
  ctx.setPerm('baseline', 'verified'); ctx.setPerm('instructor', 'verified')
  ctx.go('evidence')
  const add = (code, day) => {
    for (const [id, v] of [['kind', 'Existing school FBA baseline'], ['code', code], ['day', day], ['mins', '20'], ['context', 'yes'], ['evstatus', 'verified']]) ctx.document.getElementById(id).value = v
    ctx.addEvidence()
  }
  add('I-1', 'Day 1'); add('I-2', 'Day 1')
  ctx.setCriterion('A3', 'verified')
  check('two same-day refs do NOT verify A3', ctx.__S().criteria.A3 !== 'verified', 'A3=' + ctx.__S().criteria.A3)
  add('I-3', 'Day 2')
  ctx.setCriterion('A3', 'verified')
  check('adding a second distinct day verifies A3', ctx.__S().criteria.A3 === 'verified', 'A3=' + ctx.__S().criteria.A3)
})

await section('5. revoking a permission must demote what rested on it', async () => {
  const { ctx, els } = boot(undefined)
  ctx.setPerm('team', 'verified'); ctx.setPerm('reuse', 'verified')
  ctx.setCriterion('A2', 'verified')
  check('A2 verified while permission holds', ctx.__S().criteria.A2 === 'verified')
  ctx.setPerm('reuse', 'unresolved')
  check('A2 demoted when permission revoked', ctx.__S().criteria.A2 !== 'verified', 'A2=' + ctx.__S().criteria.A2)
  ctx.go('dashboard')
  check('dashboard counter reflects the demotion', /Criteria verified<strong>0\/6</.test(view(els)), view(els).match(/Criteria verified<strong>[^<]*</)?.[0])
})

await section('6. a partially shaped backup must not throw later', async () => {
  const { ctx } = boot(undefined)
  await ctx.importData({ text: async () => JSON.stringify({ permissions: {}, criteria: {}, definition: {}, writing: { status: 'unresolved' } }) })
  let threw = null
  try { ctx.setNested('writing', 'status', 'verified') } catch (e) { threw = e }
  check('setNested does not throw', threw === null, threw && threw.message)
})

await section('7. the readable export must be complete and must not over-claim', async () => {
  const { ctx } = boot(undefined)
  ctx.go('completion')
  ctx.document.getElementById('closeout').value = 'Completed the definition; next verify reuse'
  ctx.addCloseout()
  ctx.exportText()
  const t = ctx.__lastBlob
  check('closeouts appear in the readable summary', t.includes('Completed the definition'))
  check('no unconditional "no raw data" claim', !t.includes('no raw data'))
  check('states that a screen is not a guarantee', /not a guarantee/i.test(t))
})

await section('8. a render failure must show recovery, never a blank page', async () => {
  const { ctx, els } = boot(undefined)
  ctx.nextAction = () => { throw new Error('simulated draw failure') }
  ctx.go('dashboard')
  check('view is not blank after a throw', view(els).length > 50, 'len=' + view(els).length)
  check('recovery offers an export', view(els).includes('exportRaw'))
  check('saved data reported as unchanged', /has not been changed/.test(view(els)))
})

await section('9. local data can be deleted from inside the app', async () => {
  const { ctx, store } = boot(JSON.stringify({ permissions: { reuse: 'verified' }, criteria: {}, definition: {} }))
  ctx.resetAll()
  check('storage key removed', !store.has('aeos_pbi_section_a'))
})


await section('10. a redraw must not discard text typed into unsaved inputs', async () => {
  const { ctx, els } = boot(undefined)
  ctx.go('coordination')
  ctx.document.getElementById('question').value = 'May I reference the existing FBA?'
  ctx.document.getElementById('decisionnext').value = 'Ask the FBA lead on Thursday'
  // An unrelated action elsewhere on the page forces a full re-render.
  ctx.setPerm('team', 'verified')
  check('typed question survives the redraw', ctx.document.getElementById('question').value === 'May I reference the existing FBA?', 'got=' + JSON.stringify(ctx.document.getElementById('question').value))
  check('typed next-step survives the redraw', ctx.document.getElementById('decisionnext').value === 'Ask the FBA lead on Thursday')
})

await section('11. clearing a gating field must retract the status it gated', async () => {
  const { ctx } = boot(undefined)
  ctx.go('completion')
  ctx.setNested('writing', 'reference', 'PBIP_A_draft_v1')
  ctx.setNested('writing', 'status', 'verified')
  check('writing status verified with a reference', ctx.__S().writing.status === 'verified')
  ctx.setNested('writing', 'reference', '')
  check('status retracted when the reference is cleared', ctx.__S().writing.status !== 'verified', 'status=' + ctx.__S().writing.status)
})

await section('12. destructive removal is confirmed', async () => {
  const { ctx, els, confirms } = boot(undefined)
  ctx.setPerm('team', 'verified'); ctx.setPerm('reuse', 'verified'); ctx.setPerm('baseline', 'verified')
  ctx.go('evidence')
  for (const [id, v] of [['kind', 'Existing school FBA baseline'], ['code', 'I-9'], ['day', 'Day 1'], ['mins', '20'], ['context', 'yes'], ['evstatus', 'verified']]) ctx.document.getElementById(id).value = v
  ctx.addEvidence()
  check('reference added', ctx.__S().evidence.length === 1)
  check('add form cleared after a successful add', ctx.document.getElementById('code').value === '')
  ctx.removeEvidence(0)
  check('removal asked for confirmation', confirms.length === 1, 'confirms=' + confirms.length)
  check('reference removed after confirming', ctx.__S().evidence.length === 0)
})


await section('13. a cleared Type select must not become baseline evidence', async () => {
  const { ctx } = boot(undefined)
  for (const k of ['team', 'reuse', 'baseline', 'instructor']) ctx.setPerm(k, 'verified')
  ctx.go('evidence')
  const set = (id, v) => { ctx.document.getElementById(id).value = v }
  set('kind', 'Existing record review'); set('code', 'R-1')
  ctx.addEvidence()
  check('first reference added', ctx.__S().evidence.length === 1)
  // The user fills the next two WITHOUT reselecting Type, as the form just reset itself.
  set('code', 'R-2'); set('day', 'Day 1'); set('mins', '20'); set('context', 'yes'); set('evstatus', 'verified')
  ctx.addEvidence()
  set('code', 'R-3'); set('day', 'Day 2'); set('mins', '20'); set('context', 'yes'); set('evstatus', 'verified')
  ctx.addEvidence()
  const invented = ctx.__S().evidence.filter(e => e.kind === 'Existing school FBA baseline')
  check('no baseline evidence was invented', invented.length === 0, 'kinds=' + JSON.stringify(ctx.__S().evidence.map(e => e.kind)))
  ctx.setCriterion('A3', 'verified')
  check('A3 stays blocked', ctx.__S().criteria.A3 !== 'verified', 'A3=' + ctx.__S().criteria.A3)
})

await section('14. an unrelated JSON file must not replace saved work', async () => {
  const { ctx, store } = boot(undefined)
  ctx.go('completion')
  ctx.document.getElementById('closeout').value = 'Completed the definition; next verify reuse'
  ctx.addCloseout()
  check('closeout saved', ctx.__S().closeouts.length === 1)
  ctx.go('sources')
  await ctx.importData({ text: async () => JSON.stringify({ name: 'unrelated-package', version: '1.0.0' }) })
  check('work survives a wrong-file import', ctx.__S().closeouts.length === 1, 'closeouts=' + ctx.__S().closeouts.length)
  check('storage untouched', String(store.get('aeos_pbi_section_a')).includes('Completed the definition'))
  const said = ctx.document.getElementById('announce').textContent || ''
  check('user is told it was NOT restored', /not restored/i.test(said), 'said=' + said.slice(0, 70))
})

await section('15. a real backup still restores', async () => {
  const { ctx } = boot(undefined)
  ctx.go('sources')
  await ctx.importData({ text: async () => JSON.stringify({ app: 'aeos-pbip-section-a', v: 1, permissions: { team: 'verified' }, criteria: {}, definition: {}, closeouts: ['restored entry'] }) })
  check('marked backup is accepted', ctx.__S().closeouts.includes('restored entry'))
  check('its permissions came through', ctx.__S().permissions.team === 'verified')
})

await section('16. collection caps are enforced where entries are added', async () => {
  const { ctx, store } = boot(undefined)
  ctx.go('completion')
  for (let i = 1; i <= 205; i++) { ctx.document.getElementById('closeout').value = 'closeout ' + i; ctx.addCloseout() }
  const n = ctx.__S().closeouts.length
  check('add refuses past the cap', n === 200, 'in memory=' + n)
  const saved = JSON.parse(store.get('aeos_pbi_section_a'))
  check('storage matches memory', saved.closeouts.length === n, 'in storage=' + saved.closeouts.length)
  const { ctx: ctx2 } = boot(store.get('aeos_pbi_section_a'))
  check('nothing is lost on reload', ctx2.__S().closeouts.length === n, 'after reload=' + ctx2.__S().closeouts.length)
  const said = ctx.document.getElementById('announce').textContent || ''
  check('the refusal is explained', /maximum/i.test(said), 'said=' + said.slice(0, 70))
})


await section('17. the next action for W must lead to a control that sets W', async () => {
  const { ctx } = boot(undefined)
  for (const k of ['team', 'reuse', 'baseline', 'instructor']) ctx.setPerm(k, 'verified')
  for (const k of ['action', 'onset', 'offset', 'exclusions', 'rule']) ctx.setDef(k, 'x')
  ctx.setNested('writing', 'reference', 'PBIP_A_draft_v1')
  const S = ctx.__S()
  S.evidence = [
    { kind: 'Existing school FBA baseline', code: 'A', day: 'Day 1', mins: '20', context: 'yes', status: 'verified' },
    { kind: 'Existing school FBA baseline', code: 'B', day: 'Day 2', mins: '20', context: 'yes', status: 'verified' },
    { kind: 'Existing record review', code: 'C', day: '', mins: '', context: 'unresolved', status: 'verified' },
  ]
  for (const k of ['A1', 'A2', 'A3', 'A4', 'A5']) ctx.setCriterion(k, 'verified')
  const a = ctx.nextAction(ctx.__S())
  check('the open criterion is W', /Resolve W/.test(a[0]), a[0])
  check('it routes to a page that can set W', a[2] === 'criteria', 'routes to ' + a[2])
  ctx.go(a[2])
  check('that page offers the W control', /setCriterion\('W'/.test(ctx.document.getElementById('view').innerHTML))
  ctx.setCriterion('W', 'verified')
  check('following the advice actually resolves W', ctx.__S().criteria.W === 'verified')
  check('and the app reaches its terminal state', /All six criteria/.test(ctx.nextAction(ctx.__S())[0]))
})

await section('18. with no draft reference yet, W routes to where you enter one', async () => {
  const { ctx } = boot(undefined)
  for (const k of ['team', 'reuse', 'baseline', 'instructor']) ctx.setPerm(k, 'verified')
  for (const k of ['action', 'onset', 'offset', 'exclusions', 'rule']) ctx.setDef(k, 'x')
  check('W routes to completion while its reference is blank', ctx.actionPage(ctx.__S(), 'W') === 'completion')
  ctx.setNested('writing', 'reference', 'PBIP_A_draft_v1')
  check('and to criteria once it exists', ctx.actionPage(ctx.__S(), 'W') === 'criteria')
})

await section('19. a pending edit is flushed when the page goes away', async () => {
  const { ctx, store, fire } = boot(undefined, true)
  for (const k of ['action', 'onset', 'offset', 'exclusions', 'rule']) ctx.setDef(k, 'original text')
  fire('pagehide')
  check('the first edit is on disk', JSON.parse(store.get('aeos_pbi_section_a')).definition.action === 'original text')
  ctx.setDef('action', 'REPLACEMENT the user typed')
  check('still pending, not yet saved', JSON.parse(store.get('aeos_pbi_section_a')).definition.action === 'original text')
  fire('pagehide')   // the tab closes
  const onDisk = JSON.parse(store.get('aeos_pbi_section_a')).definition.action
  check('the edit survives the tab closing', onDisk === 'REPLACEMENT the user typed', 'on disk: ' + JSON.stringify(onDisk))
})

await section('20. clearing a gating field survives the tab closing too', async () => {
  const { ctx, store, fire } = boot(undefined, true)
  for (const k of ['team', 'reuse', 'baseline', 'instructor']) ctx.setPerm(k, 'verified')
  for (const k of ['action', 'onset', 'offset', 'exclusions', 'rule']) ctx.setDef(k, 'x')
  fire('pagehide')
  ctx.setCriterion('A1', 'verified')
  check('A1 verified', ctx.__S().criteria.A1 === 'verified')
  ctx.setDef('onset', '')        // user clears a field A1 rests on, then closes the tab
  fire('pagehide')
  const saved = JSON.parse(store.get('aeos_pbi_section_a'))
  check('the cleared field is persisted', saved.definition.onset === '')
  check('and A1 did not survive on disk', saved.criteria.A1 !== 'verified', 'A1 on disk: ' + saved.criteria.A1)
})

console.log(`\n${pass} passed, ${fail} failed`)
process.exit(fail ? 1 : 0)
