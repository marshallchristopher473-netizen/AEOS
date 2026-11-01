/*
 * AEOS Pilot Review Demo — UI.
 *
 * DEMO mode only: synthetic fixtures, PREWRITTEN simulated suggestions,
 * in-memory state. No model is called, nothing is persisted, sent or published.
 * All rules come from pilot-core.js; this file only renders state and forwards
 * teacher actions. The DOM is built with createElement/textContent only,
 * never innerHTML.
 *
 * The flow this demo completes, one primary action per screen:
 *   Start demo -> assignment & rubric -> choose a response -> inspect evidence
 *   and the prewritten draft -> accept / revise / reject -> completion screen.
 */
(function () {
  'use strict';

  const Core = window.AEOSPilotCore;
  const Fx = window.AEOSPilotFixtures;
  const appRoot = document.getElementById('app');

  if (!Core || !Fx || !appRoot) {
    document.body.textContent = 'Demo failed to load: pilot-core.js or fixtures.js is missing.';
    return;
  }

  const now = () => Date.now();
  const rubric = Core.approveRubric(Fx.rubricDraft, 'Demo Teacher (synthetic)', Fx.RUBRIC_APPROVED_AT);
  const responsesById = new Map(Fx.responses.map((r) => [r.id, r]));
  const suggestionsById = new Map(Fx.suggestions.map((s) => [s.responseId, s]));
  const criterionNames = new Map(rubric.criteria.map((c) => [c.id, c.name]));

  // Wording used everywhere the simulated suggestions are described. The demo
  // must never read as though a model was called.
  const SIMULATION_NOTE = 'Prewritten simulated suggestions (' + Fx.EVALUATOR + '). No AI model runs in this demo.';
  const SESSION_ONLY = 'Recorded for this demo session only. Nothing is saved to a server, gradebook or file.';

  const STEPS = {
    home: ['Step 1 of 5', 'Start'],
    assignment: ['Step 2 of 5', 'Read the source material'],
    queue: ['Step 3 of 5', 'Choose one prepared response'],
    review: ['Step 4 of 5', 'Inspect the evidence and the prewritten draft'],
    complete: ['Step 5 of 5', 'Decision recorded for this demo session'],
    dashboard: ['Optional', 'Session totals'],
    audit: ['Optional', 'Session activity log'],
  };

  let audit = null;
  let state = null;

  function freshSession() {
    audit = Core.createAuditLog(now);
    state = {
      view: 'home',
      activeId: null,
      reviews: new Map(),
      timers: new Map(),
      decisions: new Map(),
      pendingDecision: {},
      criterionDraft: {},
      focusKey: null,
      focusHeading: false,
      message: null,
      proposedRevision: null,
      confirmReset: false,
    };
    audit.append({ type: 'SESSION_STARTED', rubricVersion: rubric.version });
  }

  freshSession();

  // ------------------------------------------------------------- DOM helper

  function h(tag, attrs) {
    const el = document.createElement(tag);
    if (attrs) {
      for (const key of Object.keys(attrs)) {
        const value = attrs[key];
        if (value === null || value === undefined || value === false) continue;
        if (key === 'class') el.className = value;
        else if (key === 'text') el.textContent = value;
        else if (key.startsWith('on') && typeof value === 'function') el.addEventListener(key.slice(2).toLowerCase(), value);
        else el.setAttribute(key, value === true ? '' : String(value));
      }
    }
    const children = Array.prototype.slice.call(arguments, 2).flat(Infinity);
    for (const child of children) {
      if (child === null || child === undefined || child === false) continue;
      el.appendChild(child instanceof Node ? child : document.createTextNode(String(child)));
    }
    return el;
  }

  function select(options, attrs) {
    return h('select', attrs, h('option', { value: '' }, 'Choose…'), options.map((o) => h('option', { value: o }, humanize(o))));
  }

  function humanize(code) {
    return String(code).toLowerCase().replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase());
  }

  function pct(value) {
    return value === null ? '—' : Math.round(value * 100) + '%';
  }

  function seconds(ms) {
    return (Math.round(ms / 100) / 10).toFixed(1) + ' s';
  }

  function heading(text) {
    const [step, label] = STEPS[state.view] || ['', ''];
    return h('div', { class: 'view-head' },
      h('p', { class: 'step' }, step + ' · ' + label),
      h('h1', { id: 'view-heading', tabindex: '-1' }, text));
  }

  // ------------------------------------------------------------ state flow

  function setMessage(text, kind) {
    state.message = text ? { text: text, kind: kind || 'error' } : null;
  }

  function go(view, responseId) {
    state.view = view;
    if (responseId) state.activeId = responseId;
    state.focusKey = null;
    state.confirmReset = false;
    state.focusHeading = true;
    setMessage(null);
    if (view === 'assignment') audit.append({ type: 'RUBRIC_VIEWED', rubricVersion: rubric.version });
    if (view === 'dashboard') audit.append({ type: 'DASHBOARD_VIEWED' });
    if (view === 'review' && responseId) openReview(responseId);
    syncTimers();
    render();
    window.scrollTo(0, 0);
  }

  function resetDemo() {
    freshSession();
    state.focusHeading = true;
    setMessage('Demo reset. Every decision from the previous demo session has been discarded.', 'ok');
    render();
    window.scrollTo(0, 0);
  }

  function openReview(id) {
    if (!state.reviews.has(id)) {
      state.reviews.set(id, Core.createReview(responsesById.get(id), suggestionsById.get(id)));
      state.timers.set(id, Core.createActiveTimer({ idleMs: Core.IDLE_LIMIT_MS }));
    }
    if (!state.criterionDraft[id]) state.criterionDraft[id] = {};
    if (!state.decisions.has(id)) audit.append({ type: 'REVIEW_OPENED', responseId: id });
  }

  function draftFor(responseId, criterionId) {
    const perResponse = state.criterionDraft[responseId] || (state.criterionDraft[responseId] = {});
    return perResponse[criterionId] || (perResponse[criterionId] = { score: '', reviseReason: '', flagReason: '' });
  }

  // Only the open, undecided review in a visible tab accrues active time.
  function syncTimers() {
    const t = now();
    const tabVisible = document.visibilityState === 'visible';
    for (const [id, timer] of state.timers) {
      const counting = tabVisible && state.view === 'review' && state.activeId === id && !state.decisions.has(id);
      timer.setVisible(counting, t);
    }
  }

  function act(result, auditEvent, focusKey) {
    if (result.ok) {
      audit.append(auditEvent);
      setMessage(null);
    } else {
      setMessage(result.error);
    }
    state.focusKey = focusKey || null;
    render();
  }

  function locateEvidence(review, ev) {
    const result = Core.viewEvidence(review, ev.key);
    act(result, { type: 'EVIDENCE_VIEWED', responseId: review.responseId, evidenceKey: ev.key }, ev.valid ? ev.key : null);
  }

  function rejectEvidence(review, ev) {
    const result = Core.rejectEvidence(review, ev.key);
    act(result, { type: 'EVIDENCE_REJECTED', responseId: review.responseId, evidenceKey: ev.key, reasonCode: ev.valid ? 'TEACHER_REJECTED' : ev.invalidReason });
  }

  function criterionAction(review, criterionId, input) {
    const result = Core.setCriterionAction(review, criterionId, input);
    const types = { accept: 'CRITERION_ACCEPTED', revise: 'CRITERION_REVISED', flag: 'CRITERION_FLAGGED' };
    act(result, { type: types[input.action], responseId: review.responseId, criterionId: criterionId, reasonCode: input.reasonCode || null });
  }

  function confirmDecision(review) {
    const pending = state.pendingDecision[review.responseId] || {};
    const input = { decision: pending.decision, reasonCode: pending.reasonCode || null };
    const check = Core.validateDecision(review, input);
    if (!check.ok) {
      setMessage(check.errors.join(' '));
      render();
      return;
    }
    const timer = state.timers.get(review.responseId);
    const activeMs = timer.elapsed(now());
    const record = Core.finalizeDecision(review, input, activeMs, new Date().toISOString());
    state.decisions.set(review.responseId, record);
    audit.append({ type: 'DECISION_RECORDED', responseId: record.responseId, decision: record.decision, reasonCode: record.reasonCode, activeMs: record.activeMs });
    syncTimers();
    go('complete', review.responseId);
  }

  function nextUndecided() {
    return Fx.responses.find((r) => !state.decisions.has(r.id));
  }

  function download(filename, mime, content) {
    const url = URL.createObjectURL(new Blob([content], { type: mime }));
    const a = h('a', { href: url, download: filename });
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  }

  function exportAggregates(format) {
    const agg = Core.aggregatesForExport(dashboardData(), new Date().toISOString());
    if (format === 'json') download('aeos-pilot-demo-aggregates.json', 'application/json', JSON.stringify(agg, null, 2) + '\n');
    else download('aeos-pilot-demo-aggregates.csv', 'text/csv', Core.toCSV(agg));
    audit.append({ type: 'EXPORT_CREATED', format: format.toUpperCase() });
    setMessage('Export built in this browser and offered as a download. Nothing was uploaded.', 'ok');
    render();
  }

  function dashboardData() {
    // No manual baseline is collected or shown: this demo makes no
    // time-saving, success-rate or effectiveness claim.
    return Core.computeDashboard({
      suggestions: Fx.suggestions,
      decisions: Array.from(state.decisions.values()),
    });
  }

  // ---------------------------------------------------------------- render

  function render() {
    const scrollY = window.scrollY;
    const active = document.activeElement;
    const restoreId = active && active.getAttribute ? active.getAttribute('data-fid') : null;

    appRoot.replaceChildren(...[renderNav(), renderMessage(), renderView()].filter(Boolean));
    window.scrollTo(0, scrollY);

    if (state.focusHeading) {
      state.focusHeading = false;
      const hd = appRoot.querySelector('#view-heading');
      if (hd) hd.focus();
    } else if (restoreId) {
      const again = appRoot.querySelector('[data-fid="' + CSS.escape(restoreId) + '"]');
      if (again && !again.disabled) again.focus();
    }

    if (state.focusKey) {
      const mark = appRoot.querySelector('mark[data-keys~="' + CSS.escape(state.focusKey) + '"]');
      if (mark) {
        mark.scrollIntoView({ block: 'center', behavior: 'smooth' });
        mark.classList.add('pulse');
      }
    }
  }

  function renderNav() {
    const tabs = [
      ['home', 'Pilot home'],
      ['assignment', 'Assignment & rubric'],
      ['queue', 'Response queue'],
      ['review', 'Review'],
      ['dashboard', 'Dashboard'],
      ['audit', 'Audit log'],
    ];
    return h('div', { class: 'nav-row' },
      h('nav', { class: 'tabs', 'aria-label': 'Demo sections' },
        tabs.map(([view, label]) => h('button', {
          type: 'button',
          'data-fid': 'tab:' + view,
          class: state.view === view ? 'tab active' : 'tab',
          'aria-current': state.view === view ? 'page' : null,
          disabled: view === 'review' && !state.activeId,
          onclick: () => go(view),
        }, label))),
      renderResetControl());
  }

  function renderResetControl() {
    if (!state.confirmReset) {
      return h('button', {
        type: 'button', class: 'reset', 'data-fid': 'reset',
        onclick: () => { state.confirmReset = true; render(); },
      }, '↺ Reset demo');
    }
    return h('div', { class: 'reset-confirm', role: 'group', 'aria-label': 'Confirm demo reset' },
      h('span', null, 'Discard this demo session?'),
      h('button', { type: 'button', class: 'danger', 'data-fid': 'reset-yes', onclick: resetDemo }, 'Yes, reset'),
      h('button', { type: 'button', 'data-fid': 'reset-no', onclick: () => { state.confirmReset = false; render(); } }, 'Cancel'));
  }

  function renderMessage() {
    if (!state.message) return null;
    return h('div', { class: 'message ' + state.message.kind, role: state.message.kind === 'error' ? 'alert' : 'status' }, state.message.text);
  }

  function renderView() {
    switch (state.view) {
      case 'assignment': return renderAssignment();
      case 'queue': return renderQueue();
      case 'review': return renderReview();
      case 'complete': return renderComplete();
      case 'dashboard': return renderDashboard();
      case 'audit': return renderAudit();
      default: return renderHome();
    }
  }

  function renderHome() {
    const notices = [
      ['Nothing is saved — refreshing clears everything',
        'This demonstration keeps all of its work in the browser tab’s memory. Refreshing or closing the page clears every decision you record, and there is no way to get it back. Use "Reset demo" at the top right to start over on purpose.'],
      ['Suggestions are prewritten simulations',
        'Each suggestion, score and rationale was written by hand in advance and stored in a fixture file. No AI model is called while you use this page.'],
      ['Synthetic data only',
        'Every response, name and score here is invented. Do not enter or discuss real student information.'],
      ['The teacher decides',
        'Suggestions are drafts. Nothing becomes a score until you accept, revise or reject it.'],
      ['Nothing leaves this page',
        'No gradebook, student, parent or server receives anything. Network requests are blocked by the page’s security policy.'],
      ['Not evidence',
        'This demo reports no time saving, success rate or effectiveness result. The only numbers shown are counts of what you did in this session.'],
    ];
    const steps = [
      'Read the assignment, the passage and the approved rubric',
      'Choose one prepared response from the queue',
      'Locate the evidence quote behind each prewritten suggestion',
      'Accept, revise or flag each criterion',
      'Record one decision: ACCEPT, REVISE or REJECT',
    ];
    return h('section', { class: 'view' },
      heading('Evidence-linked scoring review'),
      h('p', { class: 'lede' }, 'A bounded prototype of the GradeFreed teacher review workflow for one Grade 8 ELA assignment, ' +
        'running entirely in your browser on invented data.'),
      h('div', { class: 'banner warn' }, h('strong', null, 'Read before you start: '),
        'this demonstration stores your work in memory only. Refreshing the page clears it.'),
      h('div', { class: 'notices' }, notices.map(([title, body], i) =>
        h('div', { class: 'notice' }, h('span', { class: 'notice-num' }, String(i + 1)), h('div', null, h('strong', null, title), h('p', null, body))))),
      h('h2', null, 'What you will do'),
      h('ol', { class: 'steps' }, steps.map((s) => h('li', null, s))),
      h('button', { type: 'button', class: 'primary big', 'data-fid': 'start', onclick: () => go('assignment') }, 'Start demo'));
  }

  function renderAssignment() {
    const a = Fx.assignment;
    return h('section', { class: 'view' },
      heading(a.title),
      h('p', { class: 'meta' }, 'Grade ' + a.grade + ' · ' + a.subject + ' · ' + a.id + ' · synthetic'),
      h('div', { class: 'card' }, h('h2', null, 'Prompt'), h('p', null, a.prompt)),
      h('div', { class: 'card' }, h('h2', null, a.passageTitle), h('p', { class: 'passage' }, a.passage)),
      h('div', { class: 'card' },
        h('div', { class: 'row-between' },
          h('h2', null, rubric.title),
          h('span', { class: 'chip ok' }, 'APPROVED · v' + rubric.version + ' · locked')),
        h('p', { class: 'meta' }, 'Approved by ' + rubric.approvedBy + ' on ' + rubric.approvedAt.slice(0, 10) +
          '. Approved rubrics cannot be edited; a change creates a new draft version that must be approved before use.'),
        h('div', { class: 'table-wrap' },
          h('table', { class: 'rubric' },
            h('thead', null, h('tr', null, h('th', null, 'Criterion'), [0, 1, 2, 3, 4].map((n) => h('th', null, String(n))))),
            h('tbody', null, rubric.criteria.map((c) =>
              h('tr', null, h('th', { scope: 'row' }, c.name), c.levels.map((l) => h('td', null, l))))))),
        h('div', { class: 'row-between' },
          h('button', { type: 'button', 'data-fid': 'propose', onclick: () => {
            state.proposedRevision = Core.proposeRubricRevision(rubric, {});
            audit.append({ type: 'RUBRIC_REVISION_PROPOSED', rubricVersion: state.proposedRevision.version });
            render();
          } }, 'Propose a change'),
          state.proposedRevision
            ? h('p', { class: 'meta' }, 'Draft v' + state.proposedRevision.version + ' created (status ' + state.proposedRevision.status +
              ') for this demo session. The queue keeps using approved v' + rubric.version + '.')
            : null)),
      h('button', { type: 'button', class: 'primary big', 'data-fid': 'to-queue', onclick: () => go('queue') }, 'Choose a response'));
  }

  function statusFor(id) {
    if (state.decisions.has(id)) return state.decisions.get(id).decision;
    if (state.reviews.has(id)) return 'IN REVIEW';
    return 'NOT STARTED';
  }

  function renderQueue() {
    const decided = state.decisions.size;
    const next = nextUndecided();
    return h('section', { class: 'view' },
      heading('Response queue'),
      h('p', { class: 'meta' }, decided + ' of ' + Fx.responses.length + ' decided in this demo session · rubric v' + rubric.version),
      h('p', { class: 'meta' }, SIMULATION_NOTE),
      next
        ? h('button', { type: 'button', class: 'primary big', 'data-fid': 'open-next', onclick: () => go('review', next.id) },
          'Open ' + next.id + ' (' + next.pseudonym + ')')
        : h('button', { type: 'button', class: 'primary big', 'data-fid': 'to-dashboard', onclick: () => go('dashboard') },
          'All responses decided · view session totals'),
      h('div', { class: 'table-wrap' },
        h('table', { class: 'queue' },
          h('thead', null, h('tr', null, ['Response', 'Student (synthetic)', 'Simulated uncertainty', 'Flags', 'Status', ''].map((t) => h('th', null, t)))),
          h('tbody', null, Fx.responses.map((r) => {
            const s = suggestionsById.get(r.id);
            const status = statusFor(r.id);
            return h('tr', null,
              h('td', null, r.id),
              h('td', null, r.pseudonym),
              h('td', null, h('span', { class: 'chip u-' + s.uncertainty }, s.uncertainty)),
              h('td', null, s.flags.length ? s.flags.map((f) => h('span', { class: 'chip warn' }, humanize(f))) : '—',
                s.needsReview ? h('span', { class: 'chip warn' }, 'Needs review') : null),
              h('td', null, h('span', { class: 'chip status-' + status.replace(' ', '-').toLowerCase() }, status)),
              h('td', null, h('button', { type: 'button', 'data-fid': 'open:' + r.id, onclick: () => go('review', r.id) },
                state.decisions.has(r.id) ? 'View' : 'Open')));
          })))));
  }

  function renderReview() {
    const id = state.activeId;
    const response = responsesById.get(id);
    const suggestion = suggestionsById.get(id);
    const review = state.reviews.get(id);
    const record = state.decisions.get(id);
    const allEvidence = review.order.flatMap((cid) => review.criteria[cid].evidence);

    const banners = [];
    if (suggestion.flags.includes('POSSIBLE_INSTRUCTION_IN_RESPONSE')) {
      banners.push(h('div', { class: 'banner warn' }, 'This response contains text that reads like an instruction to the evaluator. ' +
        'It was treated as student writing and was not followed.'));
    }
    if (suggestion.flags.includes('BLANK')) banners.push(h('div', { class: 'banner warn' }, 'Blank response. The simulated evaluator did not score it, so no criterion can be accepted.'));
    if (suggestion.flags.includes('OFF_TOPIC')) banners.push(h('div', { class: 'banner warn' }, 'Off-topic response. The simulated evaluator did not score it.'));
    if (suggestion.flags.includes('CONFLICTING_EVIDENCE')) banners.push(h('div', { class: 'banner warn' }, 'The response uses evidence on both sides of its claim.'));

    const segments = Core.buildHighlightSegments(response.text, allEvidence);
    const responseBody = response.text.length === 0
      ? h('p', { class: 'empty' }, '(no text submitted — this response is blank)')
      : h('p', { class: 'response-text' }, segments.map((seg) => seg.keys.length
        ? h('mark', { 'data-keys': seg.keys.join(' '), class: seg.keys.includes(state.focusKey) ? 'focus' : null }, seg.text)
        : seg.text));

    const source = h('details', { class: 'card source' },
      h('summary', null, 'Source material: assignment prompt and passage'),
      h('p', null, h('strong', null, 'Prompt: '), Fx.assignment.prompt),
      h('p', { class: 'passage' }, h('strong', null, Fx.assignment.passageTitle + ': '), Fx.assignment.passage));

    return h('section', { class: 'view review' },
      heading(response.id + ' · ' + response.pseudonym),
      h('div', { class: 'row-between' },
        h('p', { class: 'meta' }, 'Rubric v' + rubric.version + ' · simulated uncertainty: ' + suggestion.uncertainty + ' · ' + SIMULATION_NOTE),
        h('span', { class: 'timer' }, 'Active time ', h('strong', { id: 'active-time' }, seconds(record ? record.activeMs : state.timers.get(id).elapsed(now()))))),
      record ? h('div', { class: 'banner info' }, 'This response was already decided in this demo session. It is read-only.') : null,
      banners,
      source,
      h('div', { class: 'review-grid' },
        h('div', { class: 'response-pane card' }, h('h2', null, 'Student response (synthetic)'), responseBody),
        h('div', { class: 'criteria-pane' }, review.order.map((cid) => renderCriterion(review, cid, suggestion, !!record)))),
      record ? renderDecidedBar(record) : renderDecisionBar(review));
  }

  function renderCriterion(review, cid, suggestion, locked) {
    const crit = review.criteria[cid];
    const ai = suggestion.criteria.find((c) => c.criterionId === cid);
    const accept = Core.canAcceptCriterion(review, cid);
    const hasInvalid = crit.evidence.some((e) => !e.valid && !e.rejected);
    const draft = draftFor(review.responseId, cid);
    const statusLabel = crit.action === null ? 'Pending'
      : crit.action === 'accepted' ? 'Accepted (' + crit.finalScore + ')'
      : crit.action === 'revised' ? 'Revised to ' + crit.finalScore + ' · ' + humanize(crit.reasonCode)
      : 'Flagged · ' + humanize(crit.reasonCode);

    const scoreSelect = h('select', {
      'aria-label': 'Revised score for ' + criterionNames.get(cid),
      'data-fid': 'score:' + cid,
      onchange: (e) => { draft.score = e.target.value; },
    }, h('option', { value: '' }, 'Score…'), [0, 1, 2, 3, 4].map((n) => h('option', { value: String(n) }, String(n))));
    scoreSelect.value = draft.score;

    const reviseReason = select(Core.CRITERION_REVISE_REASONS, {
      'aria-label': 'Revision reason for ' + criterionNames.get(cid),
      'data-fid': 'revise-reason:' + cid,
      onchange: (e) => { draft.reviseReason = e.target.value; },
    });
    reviseReason.value = draft.reviseReason;

    const flagReason = select(Core.CRITERION_FLAG_REASONS, {
      'aria-label': 'Flag reason for ' + criterionNames.get(cid),
      'data-fid': 'flag-reason:' + cid,
      onchange: (e) => { draft.flagReason = e.target.value; },
    });
    flagReason.value = draft.flagReason;

    return h('article', { class: 'card criterion ' + (crit.action ? 'done' : '') },
      h('div', { class: 'row-between' },
        h('h3', null, criterionNames.get(cid)),
        h('span', { class: 'chip ' + (crit.action ? 'ok' : '') }, statusLabel)),
      h('p', null, h('strong', null, 'Prewritten suggestion: '), crit.aiScore === null ? 'not scored' : crit.aiScore + ' / ' + Core.SCORE_MAX,
        ' · simulated uncertainty ', h('span', { class: 'chip u-' + ai.uncertainty }, ai.uncertainty)),
      h('p', { class: 'rationale' }, ai.rationale),
      crit.evidence.length === 0 ? h('p', { class: 'meta' }, 'No evidence quotes for this criterion.') :
        h('ul', { class: 'evidence' }, crit.evidence.map((ev) => {
          if (!ev.valid) {
            return h('li', { class: 'invalid' },
              h('strong', null, 'INVALID EVIDENCE LINK'),
              h('span', null, ' “' + ev.quote + '” is not at characters ' + ev.start + '–' + ev.end + ' (' + humanize(ev.invalidReason) + ').'),
              ev.rejected ? h('span', { class: 'chip' }, 'Rejected')
                : h('button', { type: 'button', class: 'danger', 'data-fid': 'rej:' + ev.key, disabled: locked, onclick: () => rejectEvidence(review, ev) }, 'Reject this link'));
          }
          return h('li', null,
            h('button', { type: 'button', class: 'quote' + (ev.viewed ? ' viewed' : ''), 'data-fid': 'loc:' + ev.key, disabled: locked, onclick: () => locateEvidence(review, ev) },
              '“' + ev.quote + '”'),
            ev.viewed ? h('span', { class: 'meta' }, ' located') : h('span', { class: 'meta' }, ' click to locate'),
            ev.rejected ? h('span', { class: 'chip' }, 'Rejected')
              : h('button', { type: 'button', class: 'link', 'data-fid': 'rej:' + ev.key, disabled: locked, onclick: () => rejectEvidence(review, ev) }, 'reject'));
        })),
      locked ? null : h('div', { class: 'actions' },
        h('button', { type: 'button', class: 'accept', 'data-fid': 'accept:' + cid, disabled: !accept.ok || hasInvalid, title: accept.reason || 'Accept the prewritten score',
          onclick: () => criterionAction(review, cid, { action: 'accept' }) }, 'Accept'),
        !accept.ok ? h('span', { class: 'hint' }, accept.reason) : null,
        h('div', { class: 'inline-form' },
          scoreSelect, reviseReason,
          h('button', { type: 'button', 'data-fid': 'revise:' + cid, disabled: hasInvalid, onclick: () => criterionAction(review, cid, {
            action: 'revise',
            score: draft.score === '' ? null : Number(draft.score),
            reasonCode: draft.reviseReason,
          }) }, 'Revise')),
        h('div', { class: 'inline-form' },
          flagReason,
          h('button', { type: 'button', 'data-fid': 'flag:' + cid, disabled: hasInvalid, onclick: () => criterionAction(review, cid, { action: 'flag', reasonCode: draft.flagReason }) }, 'Flag'))));
  }

  function renderDecisionBar(review) {
    const status = Core.inspectionStatus(review);
    const allowed = Core.allowedDecisions(review);
    const pending = state.pendingDecision[review.responseId] || {};
    const reasons = pending.decision ? Core.DECISION_REASONS[pending.decision] : [];

    const reasonSelect = reasons.length
      ? select(reasons, { 'aria-label': 'Reason for ' + pending.decision, 'data-fid': 'decision-reason', onchange: (e) => {
        pending.reasonCode = e.target.value;
        state.pendingDecision[review.responseId] = pending;
      } })
      : null;
    if (reasonSelect && pending.reasonCode) reasonSelect.value = pending.reasonCode;

    const progress = status.reviewedCriteria + '/' + status.totalCriteria + ' criteria reviewed' +
      (status.unresolvedEvidence.length ? ' · ' + status.unresolvedEvidence.length + ' invalid evidence link unresolved' : '');

    return h('div', { class: 'decision-bar', role: 'region', 'aria-label': 'Final decision' },
      h('div', { class: 'progress ' + (status.complete ? 'ok' : '') }, status.complete ? 'Inspection complete' : progress),
      h('div', { class: 'decision-options', role: 'group', 'aria-label': 'Decision' },
        Core.DECISIONS.map((d) => h('label', { class: 'decision-option' + (allowed[d].ok ? '' : ' disabled'), title: allowed[d].reason || '' },
          h('input', { type: 'radio', name: 'decision', value: d, 'data-fid': 'decision:' + d, checked: pending.decision === d, disabled: !allowed[d].ok,
            onchange: () => {
              state.pendingDecision[review.responseId] = { decision: d, reasonCode: '' };
              render();
            } }),
          ' ' + d))),
      reasonSelect,
      h('button', { type: 'button', class: 'primary', 'data-fid': 'record', disabled: !pending.decision, onclick: () => confirmDecision(review) }, 'Record decision'));
  }

  function renderDecidedBar(record) {
    return h('div', { class: 'decision-bar decided' },
      h('div', null, h('strong', null, record.decision), record.reasonCode ? ' · ' + humanize(record.reasonCode) : '', ' · ', SESSION_ONLY),
      h('button', { type: 'button', class: 'primary', 'data-fid': 'to-complete', onclick: () => go('complete', record.responseId) }, 'See the summary'));
  }

  function renderComplete() {
    const record = state.decisions.get(state.activeId);
    if (!record) return renderQueue();
    const response = responsesById.get(record.responseId);
    const next = nextUndecided();
    const scoreLine = record.decision === 'REJECT'
      ? 'No scores were recorded. A rejected suggestion is scored manually, outside this demo.'
      : Object.keys(record.finalScores).map((k) => criterionNames.get(k) + ' ' + record.finalScores[k]).join(' · ');

    const changed = Object.keys(record.criterionActions).filter((k) => record.criterionActions[k] !== 'accepted');

    return h('section', { class: 'view complete' },
      heading('Decision recorded for this demo session'),
      h('div', { class: 'banner ok' }, h('strong', null, record.decision + ' · ' + response.id + ' (' + response.pseudonym + '). '), SESSION_ONLY),
      h('div', { class: 'card' },
        h('h2', null, 'What you decided'),
        h('dl', { class: 'summary' },
          h('dt', null, 'Decision'), h('dd', null, record.decision + (record.reasonCode ? ' · ' + humanize(record.reasonCode) : '')),
          h('dt', null, 'Final scores'), h('dd', null, scoreLine),
          h('dt', null, 'Criteria you changed or flagged'), h('dd', null, changed.length ? changed.map((k) => criterionNames.get(k) + ' (' + record.criterionActions[k] + ')').join(' · ') : 'none — every criterion was accepted unchanged'),
          h('dt', null, 'Invalid evidence links'), h('dd', null, record.invalidEvidenceRejected + ' of ' + record.invalidEvidenceCount + ' rejected before deciding'),
          h('dt', null, 'Active time on this response'), h('dd', null, seconds(record.activeMs) + ' (measured in this session; not a time-saving claim)'))),
      h('div', { class: 'banner warn' },
        'This decision exists only in this browser tab. Refreshing the page clears it, and nothing was sent to a server, gradebook or student.'),
      next
        ? h('button', { type: 'button', class: 'primary big', 'data-fid': 'next-response', onclick: () => go('review', next.id) },
          'Review the next response (' + next.id + ')')
        : h('button', { type: 'button', class: 'primary big', 'data-fid': 'to-dashboard', onclick: () => go('dashboard') },
          'All responses decided · view session totals'),
      h('div', { class: 'secondary-actions' },
        h('button', { type: 'button', 'data-fid': 'back-queue', onclick: () => go('queue') }, 'Back to the queue'),
        h('button', { type: 'button', 'data-fid': 'see-totals', onclick: () => go('dashboard') }, 'Session totals'),
        h('button', { type: 'button', 'data-fid': 'see-audit', onclick: () => go('audit') }, 'Session activity log')));
  }

  function stat(label, value, sub) {
    return h('div', { class: 'stat card' }, h('span', { class: 'stat-label' }, label), h('span', { class: 'stat-value' }, value),
      sub ? h('span', { class: 'meta' }, sub) : null);
  }

  function renderDashboard() {
    const d = dashboardData();
    const g = d.guardrails;
    const split = d.decisionSplit;
    const next = nextUndecided();
    const bar = h('div', { class: 'split-bar', 'aria-hidden': 'true' });
    for (const k of Core.DECISIONS) {
      if (!split[k]) continue;
      const seg = h('span', { class: 'seg seg-' + k.toLowerCase() }, k + ' ' + split[k]);
      seg.style.flexGrow = String(split[k]);
      bar.appendChild(seg);
    }
    const guard = (label, good, detail) => h('li', { class: good ? 'ok' : 'warn' }, h('strong', null, good ? 'PASS ' : 'CHECK '), label, ' — ', detail);
    const info = (label, detail) => h('li', { class: 'info' }, h('strong', null, 'INFO '), label, ' — ', detail);

    return h('section', { class: 'view' },
      heading('Session totals'),
      h('p', { class: 'banner info' }, 'DEMO · synthetic data · ' + d.reviewedCount + ' of ' + d.totalResponses +
        ' responses decided in this demo session. These are counts of what you just did. They are not pilot evidence, ' +
        'and this demo reports no time saving, success rate or effectiveness result.'),
      h('div', { class: 'stats' },
        stat('Median active time', d.medianActiveSec === null ? '—' : d.medianActiveSec + ' s', 'per response decided here'),
        stat('Needs-review rate', pct(d.needsReviewRate), 'fixed property of the prewritten fixtures'),
        stat('Criteria accepted unchanged', pct(d.criterionAcceptanceRate), 'of criteria you acted on'),
        stat('Override rate', pct(d.overrideRate), 'your REVISE + REJECT decisions')),
      h('div', { class: 'card' }, h('h2', null, 'Decision split'),
        d.reviewedCount ? bar : h('p', { class: 'meta' }, 'No decisions yet in this demo session.'),
        h('p', { class: 'meta' }, Core.DECISIONS.map((k) => k + ' ' + split[k]).join(' · '))),
      h('div', { class: 'card' }, h('h2', null, 'Guardrails'),
        h('ul', { class: 'guardrails' },
          guard('Invalid evidence links rejected', g.invalidEvidenceRejected === g.invalidEvidencePresent, g.invalidEvidenceRejected + ' of ' + g.invalidEvidencePresent + ' in decided responses'),
          guard('Prompt-injection attempts given full credit', g.injectionFullCredit === 0, String(g.injectionFullCredit)),
          guard('Blank or off-topic responses accepted', g.unscorableAccepted === 0, String(g.unscorableAccepted)),
          info('Routed-for-review responses accepted unchanged', g.routedForReviewAccepted + ' of ' + g.routedForReviewDecided))),
      next
        ? h('button', { type: 'button', class: 'primary big', 'data-fid': 'open-next', onclick: () => go('review', next.id) },
          'Open the next response (' + next.id + ')')
        : h('button', { type: 'button', class: 'primary big', 'data-fid': 'back-queue', onclick: () => go('queue') }, 'Back to the queue'),
      h('div', { class: 'card' }, h('h2', null, 'Export session totals'),
        h('p', { class: 'meta' }, 'Built in your browser and offered as a download. Nothing is uploaded. Exports contain counts, ' +
          'rates and medians only: no response text, quotes, pseudonyms or response IDs. Every export is labelled DEMO_SYNTHETIC_NOT_EVIDENCE.'),
        h('div', { class: 'inline-form' },
          h('button', { type: 'button', 'data-fid': 'export-json', onclick: () => exportAggregates('json') }, 'Download JSON'),
          h('button', { type: 'button', 'data-fid': 'export-csv', onclick: () => exportAggregates('csv') }, 'Download CSV'))));
  }

  function renderAudit() {
    const entries = audit.entries();
    const cols = ['seq', 'at', 'type', 'responseId', 'criterionId', 'evidenceKey', 'decision', 'reasonCode', 'activeMs', 'rubricVersion', 'format'];
    return h('section', { class: 'view' },
      heading('Session activity log'),
      h('p', { class: 'meta' }, entries.length + ' entries · append-only · identifiers, codes and durations only · held in memory for this demo session'),
      h('div', { class: 'table-wrap' },
        h('table', { class: 'audit' },
          h('thead', null, h('tr', null, cols.map((c) => h('th', null, c)))),
          h('tbody', null, entries.slice().reverse().map((e) =>
            h('tr', null, cols.map((c) => h('td', null, e[c] === undefined ? '' : c === 'at' ? e[c].slice(11, 19) : String(e[c])))))))),
      h('button', { type: 'button', class: 'primary big', 'data-fid': 'back-queue', onclick: () => go('queue') }, 'Back to the queue'));
  }

  // ---------------------------------------------------------- live wiring

  let lastActivity = 0;
  function onActivity() {
    const t = now();
    if (t - lastActivity < 1000) return;
    lastActivity = t;
    if (state.view === 'review' && state.activeId) {
      const timer = state.timers.get(state.activeId);
      if (timer) timer.activity(t);
    }
  }
  for (const type of ['pointerdown', 'pointermove', 'keydown', 'wheel', 'scroll']) {
    window.addEventListener(type, onActivity, { passive: true });
  }
  document.addEventListener('visibilitychange', syncTimers);

  setInterval(() => {
    if (state.view !== 'review' || !state.activeId || state.decisions.has(state.activeId)) return;
    const el = document.getElementById('active-time');
    const timer = state.timers.get(state.activeId);
    if (el && timer) el.textContent = seconds(timer.elapsed(now()));
  }, 1000);

  render();
})();
