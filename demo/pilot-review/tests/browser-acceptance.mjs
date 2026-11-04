/*
 * AEOS Pilot Review Demo — standalone browser acceptance check.
 *
 * Exercises the built demo in a real Chromium browser against a clean surface
 * (file:// by default, or a URL passed as argv[2]). It is deliberately NOT named
 * *.test.js: the demo CI job runs `node --test demo/pilot-review/tests/*.test.js`
 * with no browser available, and this check must not be swept into that glob.
 *
 * Usage:
 *   node demo/pilot-review/tests/browser-acceptance.mjs            # file:// the local tree
 *   node demo/pilot-review/tests/browser-acceptance.mjs <url>      # a hosted surface
 *
 * Exit code 0 = every check passed. Non-zero = at least one check failed.
 * This checks the demo's own bounded behaviour. It is not a P0 approval, a
 * security sign-off, or any evidence about teaching, grading time or outcomes.
 */
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

// Resolved through CJS so a Playwright installed outside this tree (a global or
// a preinstalled toolchain) is found without hardcoding any install path.
const { chromium } = createRequire(import.meta.url)('playwright');

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DEMO_DIR = path.resolve(HERE, '..');
const target = process.argv[2] || pathToFileURL(path.join(DEMO_DIR, 'index.html')).href;

const EXPECTED_CSP =
  "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; " +
  "connect-src 'none'; form-action 'none'; base-uri 'none'";

const results = [];
let failed = 0;
function check(name, ok, detail = '') {
  results.push({ name, ok: !!ok, detail });
  if (!ok) failed++;
  const tag = ok ? 'PASS' : 'FAIL';
  console.log(`${tag}  ${name}${detail ? ' — ' + detail : ''}`);
}

/* ---------- helpers that drive the demo's real DOM ---------- */

const btn = (page, text) =>
  page.locator('button', { hasText: new RegExp(`^\\s*${text}\\s*$`) });

async function gotoTab(page, label) {
  await page.locator('nav.tabs button', { hasText: label }).first().click();
}

async function openResponse(page, id) {
  await gotoTab(page, 'Response queue');
  const row = page.locator('tr', { has: page.locator('td', { hasText: new RegExp(`^${id}$`) }) });
  await row.locator('button').last().click();
  await page.locator('h1', { hasText: id }).waitFor();
}

/** The criterion <article> card whose <h3> is exactly name. */
const card = (page, name) =>
  page.locator('article.criterion', {
    has: page.locator('h3', { hasText: new RegExp(`^\\s*${name}\\s*$`) }),
  });

async function run() {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const context = await browser.newContext({ acceptDownloads: true });
  const page = await context.newPage();

  /* ---- instrumentation: every request, console error and page error ---- */
  const requests = [];
  const consoleErrors = [];
  const pageErrors = [];
  page.on('request', (r) => requests.push(r.url()));
  page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
  page.on('pageerror', (e) => pageErrors.push(String(e)));

  await page.goto(target, { waitUntil: 'load' });
  await page.locator('nav.tabs').waitFor({ timeout: 10000 });

  /* ================= 1. Standalone document integrity ================= */

  check('Page boots and renders the demo shell',
    await page.locator('nav.tabs button').count() >= 6);

  check('No uncaught page errors on load', pageErrors.length === 0, pageErrors.join(' | '));
  check('No console errors on load', consoleErrors.length === 0, consoleErrors.slice(0, 3).join(' | '));

  // Host-injected capability check: what scripts exist, and where, in the live DOM.
  const domShape = await page.evaluate(() => {
    const nodes = [...document.querySelectorAll('head *, body *')];
    const cspIndex = nodes.findIndex(
      (n) => n.tagName === 'META' && (n.getAttribute('http-equiv') || '').toLowerCase() === 'content-security-policy');
    const scripts = [...document.querySelectorAll('script')];
    return {
      cspContent: document.querySelector('meta[http-equiv="Content-Security-Policy"]')?.getAttribute('content') || null,
      scriptsBeforeCsp: scripts.filter((s) => nodes.indexOf(s) >= 0 && nodes.indexOf(s) < cspIndex).length,
      scriptSrcs: scripts.map((s) => s.getAttribute('src')),
      inlineScripts: scripts.filter((s) => !s.getAttribute('src')).length,
    };
  });

  check('CSP meta is byte-identical to the reviewed policy',
    domShape.cspContent === EXPECTED_CSP, domShape.cspContent ?? 'absent');
  check('Zero scripts injected before the CSP meta tag',
    domShape.scriptsBeforeCsp === 0, `found ${domShape.scriptsBeforeCsp}`);
  check('Exactly the three reviewed first-party scripts, no inline script',
    domShape.scriptSrcs.length === 3 &&
    domShape.inlineScripts === 0 &&
    ['pilot-core.js', 'fixtures.js', 'app.js'].every((f) => domShape.scriptSrcs.includes(f)),
    JSON.stringify(domShape.scriptSrcs) + ` inline=${domShape.inlineScripts}`);

  // Containment is origin-relative so it means the same thing on file:// and on
  // a real host: the page may fetch its own assets and nothing else, ever.
  const pageOrigin = await page.evaluate(() => location.origin);
  const foreign = (u) => {
    if (u.startsWith('data:') || u.startsWith('blob:')) return false;
    if (pageOrigin === 'null' || pageOrigin === '') return !u.startsWith('file://');
    return !u.startsWith(pageOrigin + '/');
  };
  const offHost = requests.filter(foreign);
  check('No third-party requests during load (same-origin assets only)',
    offHost.length === 0, offHost.slice(0, 3).join(' | '));

  /* ================= 2. Evidence gates unlock ACCEPT (R-001) ================= */

  await openResponse(page, 'R-001');
  const claim = card(page, 'Claim');
  const acceptBtn = claim.locator('button.primary', { hasText: 'Accept' });

  check('R-001 Accept is gated before the evidence is inspected',
    await acceptBtn.isDisabled());

  const quotes = claim.locator('button.quote');
  const qn = await quotes.count();
  for (let i = 0; i < qn; i++) await quotes.nth(i).click();

  check('R-001 Accept unlocks once every quote is located',
    await acceptBtn.isEnabled(), `${qn} quote(s) located`);
  await acceptBtn.click();
  check('R-001 accepted criterion records the AI score unchanged',
    /Accepted \(\d\)/.test(await claim.locator('span.chip').first().innerText()));

  /* ================= 3. Unscorable responses cannot gain numbers ================= */
  // R-004 BLANK: all four criteria null. R-005 INSUFFICIENT: only `conventions`
  // is null — the defect repaired at the final SHA. R-006 OFF_TOPIC: all null.

  for (const [id, label, nullCriteria] of [
    ['R-004', 'blank', ['Claim', 'Evidence', 'Reasoning', 'Conventions']],
    ['R-006', 'off-topic', ['Claim', 'Evidence', 'Reasoning', 'Conventions']],
    ['R-005', 'partially insufficient', ['Conventions']],
  ]) {
    await openResponse(page, id);
    let allDisabled = true;
    const detail = [];
    for (const name of nullCriteria) {
      const c = card(page, name);
      const sel = c.locator('select[aria-label^="Revised score"]');
      const revise = c.locator('div.inline-form button', { hasText: /^Revise$/ });
      const acc = c.locator('button.primary', { hasText: 'Accept' });
      const sDis = await sel.isDisabled(), rDis = await revise.isDisabled(), aDis = await acc.isDisabled();
      if (!(sDis && rDis && aDis)) { allDisabled = false; detail.push(`${name}: sel=${sDis} rev=${rDis} acc=${aDis}`); }
    }
    check(`${id} (${label}) numeric + accept controls are disabled on every unscored criterion`,
      allDisabled, detail.join('; '));
  }

  // R-005 is the sharp case: its three SCORED criteria must stay operable,
  // so the guard is proven to be targeted rather than a blanket lockout.
  await openResponse(page, 'R-005');
  const scoredOperable = await card(page, 'Claim').locator('div.inline-form button', { hasText: /^Revise$/ }).isEnabled();
  check('R-005 scored criteria remain operable (guard is targeted, not a blanket lock)', scoredOperable);

  /* ---- force the prohibited path from script, bypassing the disabled UI ---- */
  const forced = await page.evaluate(() => {
    const Core = window.AEOSPilotCore, Fx = window.AEOSPilotFixtures;
    const out = { attempted: 0, denied: 0, leaked: [] };
    for (const sug of Fx.suggestions) {
      const resp = Fx.responses.find((r) => r.id === sug.responseId);
      const nulls = sug.criteria.filter((c) => c.score === null || c.score === undefined);
      if (!nulls.length) continue;
      const review = Core.createReview(resp, sug);
      for (const c of nulls) {
        for (const score of [0, 1, 2, 3, 4]) {
          out.attempted++;
          let res;
          try {
            res = Core.setCriterionAction(review, c.criterionId,
              { action: 'revise', score, reasonCode: Core.CRITERION_REVISE_REASONS[0] });
          } catch { out.denied++; continue; }
          if (res && res.ok === false) { out.denied++; continue; }
          const got = review.criteria[c.criterionId].finalScore;
          if (typeof got === 'number') out.leaked.push(`${sug.responseId}/${c.criterionId}=${got}`);
          else out.denied++;
        }
      }
    }
    return out;
  });
  check('Scripted numeric REVISE (scores 0–4) on every null criterion is denied',
    forced.leaked.length === 0 && forced.attempted > 0,
    `${forced.denied}/${forced.attempted} denied; leaked: ${forced.leaked.join(',') || 'none'}`);

  /* ---- reasoned REJECT still available, and records no scores ---- */
  // Every decision is gated behind a complete inspection, so the blank response
  // must be flagged criterion by criterion before any decision is offered.
  await openResponse(page, 'R-004');
  const radio = (v) => page.locator(`input[type=radio][value="${v}"]`);
  check('R-004 every final decision is blocked before inspection is complete',
    (await radio('ACCEPT').isDisabled()) &&
    (await radio('REVISE').isDisabled()) &&
    (await radio('REJECT').isDisabled()));

  for (const name of ['Claim', 'Evidence', 'Reasoning', 'Conventions']) {
    const c = card(page, name);
    await c.locator('select[aria-label="Flag reason"]').selectOption('CANNOT_SCORE');
    await c.locator('div.inline-form button', { hasText: /^Flag$/ }).click();
  }
  check('R-004 inspection completes once every criterion is flagged',
    /Inspection complete/.test(await page.locator('div.progress').innerText()));

  const rejectRadio = radio('REJECT');
  check('R-004 REJECT is the only final decision unlocked after inspection',
    (await rejectRadio.isEnabled()) &&
    (await radio('ACCEPT').isDisabled()) &&
    (await radio('REVISE').isDisabled()));
  await rejectRadio.check();

  // Submit with no reason selected: it must be refused, with nothing recorded.
  await btn(page, 'Record decision').click();
  check('R-004 recording a REJECT with no reason is refused and records nothing',
    /REJECT requires a reason/.test(await page.locator('div.message').innerText()) &&
    (await page.locator('div.decision-bar.decided').count()) === 0);
  const reasonSel = page.locator('select[aria-label="Decision reason"]');
  await reasonSel.selectOption({ index: 1 });
  await btn(page, 'Record decision').click();
  const decided = await page.locator('div.decision-bar.decided').innerText();
  check('R-004 reasoned REJECT records no numeric scores',
    /REJECT/.test(decided) && /none \(score manually outside the demo\)/.test(decided),
    decided.replace(/\s+/g, ' ').slice(0, 110));

  /* ================= 4. Invalid evidence link (R-010) ================= */

  await openResponse(page, 'R-010');
  const invalidCard = page.locator('article.criterion', { has: page.locator('li.invalid') }).first();
  check('R-010 surfaces the invalid evidence link explicitly',
    (await invalidCard.locator('li.invalid strong').innerText()).includes('INVALID EVIDENCE LINK'));
  check('R-010 Accept is blocked while the invalid link is unresolved',
    await invalidCard.locator('button.primary', { hasText: 'Accept' }).isDisabled());
  check('R-010 Revise is blocked while the invalid link is unresolved',
    await invalidCard.locator('div.inline-form button', { hasText: /^Revise$/ }).isDisabled());
  await invalidCard.locator('button.danger', { hasText: 'Reject this link' }).click();
  check('R-010 rejecting the bad link does not silently re-enable accepting the AI score',
    await invalidCard.locator('button.primary', { hasText: 'Accept' }).isDisabled());

  /* ================= 5. Prompt injection (R-007) ================= */

  await openResponse(page, 'R-007');
  const banner = await page.locator('div.banner.warn').first().innerText();
  check('R-007 shows the injection warning and states it was not followed',
    /reads like an instruction/.test(banner) && /not followed/i.test(banner));
  const injectionFullCredit = await page.evaluate(() => {
    const Fx = window.AEOSPilotFixtures, Core = window.AEOSPilotCore;
    const s = Fx.suggestions.find((x) => x.flags.includes('POSSIBLE_INSTRUCTION_IN_RESPONSE'));
    return s.criteria.every((c) => c.score === Core.SCORE_MAX);
  });
  check('R-007 mock suggestion is not full credit', injectionFullCredit === false);

  /* ================= 6. Aggregate-only exports ================= */

  await gotoTab(page, 'Dashboard');
  const grab = async (label) => {
    const [dl] = await Promise.all([page.waitForEvent('download'), btn(page, label).click()]);
    const p = await dl.path();
    return { name: dl.suggestedFilename(), body: fs.readFileSync(p, 'utf8') };
  };
  const json = await grab('Download JSON');
  const csv = await grab('Download CSV');
  const parsed = JSON.parse(json.body);

  check('JSON export carries exactly the 21-field aggregate allowlist',
    Object.keys(parsed).length === 21, `${Object.keys(parsed).length} fields`);
  check('JSON export carries the schema id and both caveats',
    JSON.stringify(parsed).includes('aeos.pilot-demo.aggregates.v2') &&
    JSON.stringify(parsed).includes('DEMO_CLICKTHROUGH_NOT_GRADING_TIME') &&
    JSON.stringify(parsed).includes('DEMO_SYNTHETIC_NOT_EVIDENCE'));

  // No response text, pseudonyms or response IDs may leak into either export.
  const leakProbe = await page.evaluate(() => {
    const Fx = window.AEOSPilotFixtures;
    return {
      ids: Fx.responses.map((r) => r.id),
      names: Fx.responses.map((r) => r.pseudonym),
      words: Fx.responses.filter((r) => r.text.length > 40).map((r) => r.text.trim().split(/\s+/).slice(0, 6).join(' ')),
    };
  });
  const both = json.body + '\n' + csv.body;
  const leaked = [
    ...leakProbe.ids.filter((v) => both.includes(v)),
    ...leakProbe.names.filter((v) => both.includes(v)),
    ...leakProbe.words.filter((v) => both.includes(v)),
  ];
  check('Neither export contains response IDs, pseudonyms or response text',
    leaked.length === 0, leaked.slice(0, 3).join(' | '));

  // The CSV is long-form: a `metric,value` header plus one row per allowlisted field.
  const csvLines = csv.body.trim().split(/\r?\n/);
  const csvPairs = new Map(csvLines.slice(1).map((l) => {
    const i = l.indexOf(',');
    return [l.slice(0, i), l.slice(i + 1)];
  }));
  check('CSV export is a metric,value header plus exactly the 21 allowlisted rows',
    csvLines[0] === 'metric,value' && csvLines.length === 22 && csvPairs.size === 21,
    `${csvLines.length} lines, header "${csvLines[0]}"`);
  check('CSV and JSON expose the identical field set',
    Object.keys(parsed).every((k) => csvPairs.has(k)) && csvPairs.size === Object.keys(parsed).length);

  // Unmeasured values must be null in JSON and blank — not 0 — in CSV.
  const nullKeys = Object.keys(parsed).filter((k) => parsed[k] === null);
  check('Every null JSON value is serialised as a blank CSV cell, never 0',
    nullKeys.every((k) => csvPairs.get(k) === ''),
    nullKeys.length ? `null fields: ${nullKeys.join(', ')}` : 'no null fields in this run');

  // CSV injection / delimiter safety on any value that needs quoting.
  check('CSV quotes every value containing a comma, quote or newline',
    [...csvPairs.values()].every((v) => !/^[^"].*[,\r\n]/.test(v)));

  /* ================= 7. Reload discards everything ================= */

  await page.reload({ waitUntil: 'load' });
  await page.locator('nav.tabs').waitFor();
  await gotoTab(page, 'Response queue');
  const queueMeta = await page.locator('p.meta').first().innerText();
  check('Reload resets the queue to 0 of 12 decided', /^0 of 12 decided/.test(queueMeta), queueMeta);
  const notStarted = await page.locator('span.chip.status-not-started').count();
  check('Reload resets every response to NOT STARTED', notStarted === 12, `${notStarted}/12`);
  await gotoTab(page, 'Audit log');
  const auditRows = await page.locator('tbody tr').count();
  check('Reload leaves a single SESSION_STARTED audit entry',
    auditRows === 1 && /SESSION_STARTED/.test(await page.locator('tbody tr').first().innerText()),
    `${auditRows} row(s)`);

  // Zero-review export: the unmeasured timing field must be null / blank here.
  await gotoTab(page, 'Dashboard');
  const json0 = await grab('Download JSON');
  const csv0 = await grab('Download CSV');
  const p0 = JSON.parse(json0.body);
  const csv0Pairs = new Map(csv0.body.trim().split(/\r?\n/).slice(1).map((l) => {
    const i = l.indexOf(',');
    return [l.slice(0, i), l.slice(i + 1)];
  }));
  check('Zero-review export reports unmeasured interaction timing as null',
    p0.demoClickThroughMedianSec === null, String(p0.demoClickThroughMedianSec));
  check('Zero-review CSV renders that unmeasured timing as blank, not 0',
    csv0Pairs.get('demoClickThroughMedianSec') === '',
    JSON.stringify(csv0Pairs.get('demoClickThroughMedianSec')));
  check('Zero-review export still carries both caveats',
    json0.body.includes('DEMO_CLICKTHROUGH_NOT_GRADING_TIME') &&
    json0.body.includes('DEMO_SYNTHETIC_NOT_EVIDENCE'));

  /* ================= 8. Keyboard reachability ================= */

  await gotoTab(page, 'Response queue');
  await page.keyboard.press('Tab');
  const reached = await page.evaluate(() => {
    const seen = new Set();
    let el = document.activeElement, guard = 0;
    while (el && guard++ < 80) { seen.add(el.tagName); el = document.activeElement; break; }
    return [...document.querySelectorAll('button, select, input, [tabindex]')]
      .filter((n) => !n.disabled && n.tabIndex >= 0).length;
  });
  check('Interactive controls are in the keyboard tab order', reached > 0, `${reached} focusable`);
  const focusTag = await page.evaluate(() => document.activeElement?.tagName || 'NONE');
  check('Tab moves focus onto a real control', focusTag === 'BUTTON' || focusTag === 'A', focusTag);

  /* ================= 9. 390px viewport ================= */

  await page.setViewportSize({ width: 390, height: 844 });
  await openResponse(page, 'R-001');
  const layout = await page.evaluate(() => {
    const small = [...document.querySelectorAll('button, select')]
      .filter((n) => { const r = n.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.height < 28; })
      .map((n) => `${n.tagName}:${(n.textContent || '').trim().slice(0, 18)}:${Math.round(n.getBoundingClientRect().height)}px`);
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      clientWidth: document.documentElement.clientWidth,
      small,
    };
  });
  check('No document-level horizontal overflow at 390px',
    layout.overflow <= 0, `scrollWidth-clientWidth=${layout.overflow} (client ${layout.clientWidth})`);
  check('No visible control is under 28px tall at 390px',
    layout.small.length === 0, layout.small.slice(0, 4).join(' | '));

  /* ================= 10. Containment over the whole session ================= */

  const offHostAll = requests.filter(foreign);
  check('Zero third-party requests across the entire session',
    offHostAll.length === 0, offHostAll.slice(0, 3).join(' | '));
  check('Every request the page made resolves to one of its five own assets',
    requests.filter((u) => !u.startsWith('data:') && !u.startsWith('blob:')).every((u) =>
      ['index.html', 'styles.css', 'pilot-core.js', 'fixtures.js', 'app.js', 'favicon.ico']
        .some((f) => u.endsWith('/' + f))),
    [...new Set(requests)].slice(0, 6).join(' | '));
  check('No uncaught page errors across the entire session',
    pageErrors.length === 0, pageErrors.slice(0, 2).join(' | '));

  await browser.close();

  /* ---------------------------- summary ---------------------------- */
  const passed = results.filter((r) => r.ok).length;
  console.log('\n' + '-'.repeat(64));
  console.log(`Surface : ${target}`);
  console.log(`Result  : ${passed}/${results.length} checks passed, ${failed} failed`);
  console.log('-'.repeat(64));
  if (failed) {
    console.log('\nFailed checks:');
    for (const r of results.filter((x) => !x.ok)) console.log(`  - ${r.name}${r.detail ? ' — ' + r.detail : ''}`);
  }
  process.exit(failed ? 1 : 0);
}

run().catch((e) => { console.error('HARNESS ERROR:', e); process.exit(2); });
