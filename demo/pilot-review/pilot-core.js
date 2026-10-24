/*
 * AEOS Pilot Review Demo — core logic.
 *
 * DEMO mode only. Synthetic data only. No DOM access, no network access,
 * no persistence. Every rule the review workflow enforces lives here so it can
 * be unit-tested with `node --test` and reused as the acceptance reference for
 * the production build.
 */
(function (root, factory) {
  'use strict';
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.AEOSPilotCore = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const MODE = 'DEMO';
  const IDLE_LIMIT_MS = 60000;
  const SCORE_MIN = 0;
  const SCORE_MAX = 4;

  const CRITERION_REVISE_REASONS = Object.freeze([
    'SCORE_TOO_HIGH',
    'SCORE_TOO_LOW',
    'EVIDENCE_MISREAD',
    'RUBRIC_MISAPPLIED',
    'OTHER',
  ]);

  const CRITERION_FLAG_REASONS = Object.freeze([
    'CANNOT_SCORE',
    'INVALID_EVIDENCE',
    'NEEDS_SECOND_LOOK',
    'POLICY_CONCERN',
  ]);

  const DECISION_REASONS = Object.freeze({
    ACCEPT: Object.freeze([]),
    REVISE: Object.freeze([
      'SCORES_ADJUSTED',
      'EVIDENCE_CORRECTED',
      'RUBRIC_INTERPRETATION',
    ]),
    REJECT: Object.freeze([
      'BLANK_OR_INSUFFICIENT',
      'OFF_TOPIC',
      'PROMPT_INJECTION',
      'INVALID_EVIDENCE',
      'UNRELIABLE_SUGGESTION',
      'OTHER',
    ]),
  });

  const DECISIONS = Object.freeze(['ACCEPT', 'REVISE', 'REJECT']);

  // ---------------------------------------------------------------- helpers

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function deepFreeze(obj) {
    if (obj && typeof obj === 'object' && !Object.isFrozen(obj)) {
      Object.freeze(obj);
      for (const key of Object.keys(obj)) deepFreeze(obj[key]);
    }
    return obj;
  }

  function isValidScore(score) {
    return Number.isInteger(score) && score >= SCORE_MIN && score <= SCORE_MAX;
  }

  // ----------------------------------------------------------------- rubric

  function validateRubric(rubric) {
    const errors = [];
    if (!rubric || typeof rubric !== 'object') return ['Rubric is missing.'];
    if (typeof rubric.version !== 'string' || !/^\d+\.\d+$/.test(rubric.version)) {
      errors.push('Rubric version must look like "1.0".');
    }
    if (!Array.isArray(rubric.criteria) || rubric.criteria.length === 0) {
      errors.push('Rubric needs at least one criterion.');
      return errors;
    }
    const seen = new Set();
    for (const c of rubric.criteria) {
      if (!c || typeof c.id !== 'string' || c.id.length === 0) {
        errors.push('Every criterion needs an id.');
        continue;
      }
      if (seen.has(c.id)) errors.push('Duplicate criterion id: ' + c.id);
      seen.add(c.id);
      if (!Array.isArray(c.levels) || c.levels.length !== SCORE_MAX - SCORE_MIN + 1) {
        errors.push('Criterion ' + c.id + ' must describe every score level.');
      }
    }
    return errors;
  }

  /** Returns a deep-frozen approved copy. The draft passed in is not modified. */
  function approveRubric(draft, approvedBy, approvedAt) {
    const errors = validateRubric(draft);
    if (errors.length) throw new Error('Cannot approve rubric: ' + errors.join(' '));
    if (typeof approvedBy !== 'string' || approvedBy.length === 0) {
      throw new Error('Cannot approve rubric: approver is required.');
    }
    const approved = clone(draft);
    approved.status = 'APPROVED';
    approved.approvedBy = approvedBy;
    approved.approvedAt = approvedAt;
    return deepFreeze(approved);
  }

  /**
   * Approved rubrics are never edited in place. A change produces a new DRAFT
   * with a bumped minor version that must be approved before it can be used.
   */
  function proposeRubricRevision(approved, changes) {
    if (!approved || approved.status !== 'APPROVED') {
      throw new Error('Only an approved rubric can be revised.');
    }
    const parts = approved.version.split('.').map(Number);
    const draft = Object.assign(clone(approved), clone(changes || {}));
    draft.version = parts[0] + '.' + (parts[1] + 1);
    draft.status = 'DRAFT';
    draft.previousVersion = approved.version;
    delete draft.approvedBy;
    delete draft.approvedAt;
    return draft;
  }

  // --------------------------------------------------------------- evidence

  /** An evidence link is valid only when its quote is exactly text[start:end]. */
  function validateEvidenceLink(text, link) {
    if (typeof text !== 'string') return { valid: false, reason: 'NO_RESPONSE_TEXT' };
    if (!link || typeof link.quote !== 'string' || link.quote.length === 0) {
      return { valid: false, reason: 'MISSING_QUOTE' };
    }
    const { start, end } = link;
    if (!Number.isInteger(start) || !Number.isInteger(end) || start < 0 || end > text.length || start >= end) {
      return { valid: false, reason: 'OFFSETS_OUT_OF_RANGE' };
    }
    if (text.slice(start, end) !== link.quote) return { valid: false, reason: 'QUOTE_MISMATCH' };
    return { valid: true, reason: null };
  }

  /**
   * Splits text into contiguous segments, each tagged with the keys of the
   * valid evidence links that cover it. Overlapping links are supported.
   */
  function buildHighlightSegments(text, links) {
    const valid = (links || []).filter((l) => validateEvidenceLink(text, l).valid);
    const cuts = new Set([0, text.length]);
    for (const l of valid) {
      cuts.add(l.start);
      cuts.add(l.end);
    }
    const points = Array.from(cuts).sort((a, b) => a - b);
    const segments = [];
    for (let i = 0; i < points.length - 1; i++) {
      const from = points[i];
      const to = points[i + 1];
      if (from === to) continue;
      const keys = valid.filter((l) => l.start <= from && l.end >= to).map((l) => l.key);
      segments.push({ text: text.slice(from, to), keys: keys });
    }
    return segments;
  }

  // ----------------------------------------------------------------- review

  function createReview(response, suggestion) {
    if (!response || !suggestion || response.id !== suggestion.responseId) {
      throw new Error('Review needs a response and its matching suggestion.');
    }
    const criteria = {};
    const order = [];
    for (const c of suggestion.criteria) {
      const evidence = (c.evidence || []).map(function (ev, i) {
        const check = validateEvidenceLink(response.text, ev);
        return {
          key: c.criterionId + ':' + i,
          quote: ev.quote,
          start: ev.start,
          end: ev.end,
          valid: check.valid,
          invalidReason: check.reason,
          viewed: false,
          rejected: false,
        };
      });
      criteria[c.criterionId] = {
        criterionId: c.criterionId,
        aiScore: c.score,
        action: null,
        finalScore: null,
        reasonCode: null,
        evidence: evidence,
      };
      order.push(c.criterionId);
    }
    return { responseId: response.id, order: order, criteria: criteria, decided: false };
  }

  function findEvidence(review, key) {
    for (const id of review.order) {
      const ev = review.criteria[id].evidence.find((e) => e.key === key);
      if (ev) return ev;
    }
    return null;
  }

  function viewEvidence(review, key) {
    if (review.decided) return { ok: false, error: 'Review is already decided.' };
    const ev = findEvidence(review, key);
    if (!ev) return { ok: false, error: 'Unknown evidence link.' };
    ev.viewed = true;
    return { ok: true };
  }

  /** Explicitly rejects an evidence link. Required for every invalid link. */
  function rejectEvidence(review, key) {
    if (review.decided) return { ok: false, error: 'Review is already decided.' };
    const ev = findEvidence(review, key);
    if (!ev) return { ok: false, error: 'Unknown evidence link.' };
    ev.viewed = true;
    ev.rejected = true;
    for (const id of review.order) {
      const crit = review.criteria[id];
      if (crit.action === 'accepted' && crit.evidence.includes(ev)) {
        crit.action = null;
        crit.finalScore = null;
      }
    }
    return { ok: true };
  }

  function canAcceptCriterion(review, criterionId) {
    const crit = review.criteria[criterionId];
    if (!crit) return { ok: false, reason: 'Unknown criterion.' };
    if (crit.aiScore === null || crit.aiScore === undefined) {
      return { ok: false, reason: 'No AI score to accept. Revise or flag instead.' };
    }
    if (crit.evidence.some((e) => !e.valid && !e.rejected)) {
      return { ok: false, reason: 'INVALID EVIDENCE LINK must be explicitly rejected first.' };
    }
    if (crit.evidence.some((e) => e.rejected)) {
      return { ok: false, reason: 'Evidence was rejected, so the AI score cannot be accepted as-is. Revise or flag.' };
    }
    if (crit.evidence.some((e) => !e.viewed)) {
      return { ok: false, reason: 'Locate every evidence quote before accepting.' };
    }
    return { ok: true, reason: null };
  }

  function setCriterionAction(review, criterionId, input) {
    if (review.decided) return { ok: false, error: 'Review is already decided.' };
    const crit = review.criteria[criterionId];
    if (!crit) return { ok: false, error: 'Unknown criterion.' };
    const action = input && input.action;
    if (crit.evidence.some((e) => !e.valid && !e.rejected)) {
      return { ok: false, error: 'INVALID EVIDENCE LINK must be explicitly rejected first.' };
    }
    if (action === 'accept') {
      const check = canAcceptCriterion(review, criterionId);
      if (!check.ok) return { ok: false, error: check.reason };
      crit.action = 'accepted';
      crit.finalScore = crit.aiScore;
      crit.reasonCode = null;
      return { ok: true };
    }
    if (action === 'revise') {
      if (!isValidScore(input.score)) {
        return { ok: false, error: 'Revised score must be a whole number from ' + SCORE_MIN + ' to ' + SCORE_MAX + '.' };
      }
      if (!CRITERION_REVISE_REASONS.includes(input.reasonCode)) {
        return { ok: false, error: 'A revision reason is required.' };
      }
      crit.action = 'revised';
      crit.finalScore = input.score;
      crit.reasonCode = input.reasonCode;
      return { ok: true };
    }
    if (action === 'flag') {
      if (!CRITERION_FLAG_REASONS.includes(input.reasonCode)) {
        return { ok: false, error: 'A flag reason is required.' };
      }
      crit.action = 'flagged';
      crit.finalScore = null;
      crit.reasonCode = input.reasonCode;
      return { ok: true };
    }
    return { ok: false, error: 'Unknown criterion action.' };
  }

  function inspectionStatus(review) {
    const pendingCriteria = review.order.filter((id) => review.criteria[id].action === null);
    const unresolvedEvidence = [];
    for (const id of review.order) {
      for (const ev of review.criteria[id].evidence) {
        if (!ev.valid && !ev.rejected) unresolvedEvidence.push(ev.key);
      }
    }
    return {
      complete: pendingCriteria.length === 0 && unresolvedEvidence.length === 0,
      reviewedCriteria: review.order.length - pendingCriteria.length,
      totalCriteria: review.order.length,
      pendingCriteria: pendingCriteria,
      unresolvedEvidence: unresolvedEvidence,
    };
  }

  /** Which final decisions are currently allowed, and why not when they are not. */
  function allowedDecisions(review) {
    const status = inspectionStatus(review);
    const notInspected = { ok: false, reason: 'Inspect every criterion and resolve every invalid evidence link first.' };
    if (review.decided) {
      const done = { ok: false, reason: 'Already decided.' };
      return { ACCEPT: done, REVISE: done, REJECT: done };
    }
    if (!status.complete) return { ACCEPT: notInspected, REVISE: notInspected, REJECT: notInspected };

    const crits = review.order.map((id) => review.criteria[id]);
    const allAccepted = crits.every((c) => c.action === 'accepted');
    const allScored = crits.every((c) => c.action === 'accepted' || c.action === 'revised');
    const anyRevised = crits.some((c) => c.action === 'revised');

    return {
      ACCEPT: allAccepted
        ? { ok: true, reason: null }
        : { ok: false, reason: 'ACCEPT requires every criterion to be accepted unchanged.' },
      REVISE: allScored && anyRevised
        ? { ok: true, reason: null }
        : { ok: false, reason: allScored ? 'Nothing was revised. Use ACCEPT.' : 'Every criterion needs a final score (flagged criteria cannot be submitted).' },
      REJECT: { ok: true, reason: null },
    };
  }

  function validateDecision(review, input) {
    const errors = [];
    const decision = input && input.decision;
    if (!DECISIONS.includes(decision)) {
      errors.push('Choose ACCEPT, REVISE or REJECT.');
      return { ok: false, errors: errors };
    }
    const allowed = allowedDecisions(review)[decision];
    if (!allowed.ok) errors.push(allowed.reason);
    const reasons = DECISION_REASONS[decision];
    if (reasons.length > 0 && !reasons.includes(input.reasonCode)) {
      errors.push(decision + ' requires a reason.');
    }
    if (reasons.length === 0 && input.reasonCode) {
      errors.push(decision + ' does not take a reason.');
    }
    return { ok: errors.length === 0, errors: errors };
  }

  /** Finalizes a review. Returns a frozen decision record, or throws. */
  function finalizeDecision(review, input, activeMs, decidedAt) {
    const check = validateDecision(review, input);
    if (!check.ok) throw new Error(check.errors.join(' '));
    const finalScores = {};
    const aiScores = {};
    const criterionActions = {};
    for (const id of review.order) {
      const c = review.criteria[id];
      aiScores[id] = c.aiScore === undefined ? null : c.aiScore;
      finalScores[id] = input.decision === 'REJECT' ? null : c.finalScore;
      criterionActions[id] = c.action;
    }
    const evidence = review.order.flatMap((id) => review.criteria[id].evidence);
    review.decided = true;
    return deepFreeze({
      responseId: review.responseId,
      decision: input.decision,
      reasonCode: input.reasonCode || null,
      aiScores: aiScores,
      finalScores: finalScores,
      criterionActions: criterionActions,
      invalidEvidenceCount: evidence.filter((e) => !e.valid).length,
      invalidEvidenceRejected: evidence.filter((e) => !e.valid && e.rejected).length,
      activeMs: Math.max(0, Math.round(activeMs || 0)),
      decidedAt: decidedAt,
    });
  }

  // ------------------------------------------------------------------ timer

  /**
   * Active review time. Counts only while the review is visible, and stops
   * counting `idleMs` after the last input (reading time up to that limit
   * counts). Timestamps are passed in so behaviour is deterministic in tests.
   */
  function createActiveTimer(options) {
    const idleMs = (options && options.idleMs) || IDLE_LIMIT_MS;
    let activeMs = 0;
    let visible = false;
    let lastActivity = null;
    let accountedTo = null;

    function advance(t) {
      if (accountedTo !== null && t < accountedTo) t = accountedTo;
      if (visible && lastActivity !== null && accountedTo !== null) {
        const end = Math.min(t, lastActivity + idleMs);
        if (end > accountedTo) activeMs += end - accountedTo;
      }
      accountedTo = t;
    }

    return {
      setVisible: function (isVisible, t) {
        advance(t);
        if (isVisible && !visible) lastActivity = t;
        visible = !!isVisible;
      },
      activity: function (t) {
        advance(t);
        if (visible) lastActivity = t;
      },
      elapsed: function (t) {
        advance(t);
        return activeMs;
      },
      isRunning: function (t) {
        return visible && lastActivity !== null && t - lastActivity < idleMs;
      },
    };
  }

  // ------------------------------------------------------------------ audit

  const AUDIT_TYPES = Object.freeze([
    'SESSION_STARTED',
    'RUBRIC_VIEWED',
    'RUBRIC_REVISION_PROPOSED',
    'REVIEW_OPENED',
    'EVIDENCE_VIEWED',
    'EVIDENCE_REJECTED',
    'CRITERION_ACCEPTED',
    'CRITERION_REVISED',
    'CRITERION_FLAGGED',
    'DECISION_RECORDED',
    'DASHBOARD_VIEWED',
    'EXPORT_CREATED',
  ]);

  // Minimal metadata only: identifiers, codes and durations. Never response
  // text, quotes, scores-with-commentary or free-text notes.
  const AUDIT_STRING_FIELDS = ['responseId', 'criterionId', 'evidenceKey', 'decision', 'reasonCode', 'rubricVersion', 'format'];
  const AUDIT_NUMBER_FIELDS = ['activeMs'];
  const AUDIT_TOKEN = /^[A-Za-z0-9_:.\-]{1,64}$/;

  function createAuditLog(clock) {
    const entries = [];
    const now = clock || Date.now;
    return {
      append: function (event) {
        if (!event || !AUDIT_TYPES.includes(event.type)) {
          throw new Error('Unknown audit event type.');
        }
        const entry = { seq: entries.length + 1, at: new Date(now()).toISOString(), type: event.type };
        for (const field of AUDIT_STRING_FIELDS) {
          if (event[field] === undefined || event[field] === null) continue;
          if (typeof event[field] !== 'string' || !AUDIT_TOKEN.test(event[field])) {
            throw new Error('Audit field "' + field + '" must be a short identifier or code.');
          }
          entry[field] = event[field];
        }
        for (const field of AUDIT_NUMBER_FIELDS) {
          if (event[field] === undefined || event[field] === null) continue;
          if (!Number.isFinite(event[field]) || event[field] < 0) {
            throw new Error('Audit field "' + field + '" must be a non-negative number.');
          }
          entry[field] = Math.round(event[field]);
        }
        const frozen = Object.freeze(entry);
        entries.push(frozen);
        return frozen;
      },
      entries: function () {
        return entries.slice();
      },
      size: function () {
        return entries.length;
      },
    };
  }

  // -------------------------------------------------------------- dashboard

  function median(values) {
    const nums = values.filter((v) => Number.isFinite(v)).sort((a, b) => a - b);
    if (nums.length === 0) return null;
    const mid = Math.floor(nums.length / 2);
    return nums.length % 2 ? nums[mid] : (nums[mid - 1] + nums[mid]) / 2;
  }

  function ratio(part, whole) {
    return whole > 0 ? part / whole : null;
  }

  /**
   * Aggregates for the dashboard and exports. Inputs: the full suggestion list
   * and the decision records produced by finalizeDecision.
   */
  function computeDashboard(input) {
    const suggestions = input.suggestions || [];
    const decisions = input.decisions || [];
    const byId = new Map(suggestions.map((s) => [s.responseId, s]));
    const split = { ACCEPT: 0, REVISE: 0, REJECT: 0 };
    let criteriaActed = 0;
    let criteriaAccepted = 0;
    let invalidPresent = 0;
    let invalidRejected = 0;
    let routedReviewed = 0;
    let routedAccepted = 0;
    let injectionFullCredit = 0;
    let unscorableAccepted = 0;

    for (const d of decisions) {
      split[d.decision] += 1;
      for (const id of Object.keys(d.criterionActions)) {
        criteriaActed += 1;
        if (d.criterionActions[id] === 'accepted') criteriaAccepted += 1;
      }
      invalidPresent += d.invalidEvidenceCount;
      invalidRejected += d.invalidEvidenceRejected;
      const s = byId.get(d.responseId);
      const flags = (s && s.flags) || [];
      if (s && s.needsReview) {
        routedReviewed += 1;
        if (d.decision === 'ACCEPT') routedAccepted += 1;
      }
      if (flags.includes('POSSIBLE_INSTRUCTION_IN_RESPONSE')) {
        const scores = Object.values(d.finalScores);
        if (scores.length > 0 && scores.every((v) => v === SCORE_MAX)) injectionFullCredit += 1;
      }
      if ((flags.includes('BLANK') || flags.includes('OFF_TOPIC')) && d.decision === 'ACCEPT') {
        unscorableAccepted += 1;
      }
    }

    const medianActiveMs = median(decisions.map((d) => d.activeMs));
    const medianActiveSec = medianActiveMs === null ? null : Math.round(medianActiveMs / 100) / 10;
    const manual = Number.isFinite(input.manualBaselineSec) && input.manualBaselineSec > 0 ? input.manualBaselineSec : null;

    return {
      mode: MODE,
      synthetic: true,
      totalResponses: suggestions.length,
      reviewedCount: decisions.length,
      medianActiveSec: medianActiveSec,
      decisionSplit: split,
      needsReviewRate: ratio(suggestions.filter((s) => s.needsReview).length, suggestions.length),
      criterionAcceptanceRate: ratio(criteriaAccepted, criteriaActed),
      overrideRate: ratio(split.REVISE + split.REJECT, decisions.length),
      guardrails: {
        invalidEvidencePresent: invalidPresent,
        invalidEvidenceRejected: invalidRejected,
        routedForReviewDecided: routedReviewed,
        routedForReviewAccepted: routedAccepted,
        injectionFullCredit: injectionFullCredit,
        unscorableAccepted: unscorableAccepted,
      },
      baseline: {
        manualMedianSec: manual,
        assistedMedianSec: medianActiveSec,
        differenceSec: manual !== null && medianActiveSec !== null ? Math.round((manual - medianActiveSec) * 10) / 10 : null,
        label: 'Observed in a DEMO session on synthetic data. Not pilot evidence.',
      },
    };
  }

  // ---------------------------------------------------------------- exports

  /** Aggregates only: numbers and fixed labels. No response text, IDs or notes. */
  function aggregatesForExport(dashboard, generatedAt) {
    const g = dashboard.guardrails;
    return {
      schema: 'aeos.pilot-demo.aggregates.v1',
      mode: MODE,
      synthetic: true,
      generatedAt: generatedAt,
      totalResponses: dashboard.totalResponses,
      reviewedCount: dashboard.reviewedCount,
      medianActiveSec: dashboard.medianActiveSec,
      decisionAccept: dashboard.decisionSplit.ACCEPT,
      decisionRevise: dashboard.decisionSplit.REVISE,
      decisionReject: dashboard.decisionSplit.REJECT,
      needsReviewRate: dashboard.needsReviewRate,
      criterionAcceptanceRate: dashboard.criterionAcceptanceRate,
      overrideRate: dashboard.overrideRate,
      invalidEvidencePresent: g.invalidEvidencePresent,
      invalidEvidenceRejected: g.invalidEvidenceRejected,
      routedForReviewDecided: g.routedForReviewDecided,
      routedForReviewAccepted: g.routedForReviewAccepted,
      injectionFullCredit: g.injectionFullCredit,
      unscorableAccepted: g.unscorableAccepted,
      manualBaselineMedianSec: dashboard.baseline.manualMedianSec,
      baselineDifferenceSec: dashboard.baseline.differenceSec,
      evidenceStatus: 'DEMO_SYNTHETIC_NOT_EVIDENCE',
    };
  }

  function toCSV(aggregates) {
    const rows = ['metric,value'];
    for (const key of Object.keys(aggregates)) {
      const v = aggregates[key];
      rows.push(key + ',' + (v === null || v === undefined ? '' : String(v)));
    }
    return rows.join('\n') + '\n';
  }

  return Object.freeze({
    MODE: MODE,
    IDLE_LIMIT_MS: IDLE_LIMIT_MS,
    SCORE_MIN: SCORE_MIN,
    SCORE_MAX: SCORE_MAX,
    DECISIONS: DECISIONS,
    DECISION_REASONS: DECISION_REASONS,
    CRITERION_REVISE_REASONS: CRITERION_REVISE_REASONS,
    CRITERION_FLAG_REASONS: CRITERION_FLAG_REASONS,
    AUDIT_TYPES: AUDIT_TYPES,
    validateRubric: validateRubric,
    approveRubric: approveRubric,
    proposeRubricRevision: proposeRubricRevision,
    validateEvidenceLink: validateEvidenceLink,
    buildHighlightSegments: buildHighlightSegments,
    createReview: createReview,
    viewEvidence: viewEvidence,
    rejectEvidence: rejectEvidence,
    canAcceptCriterion: canAcceptCriterion,
    setCriterionAction: setCriterionAction,
    inspectionStatus: inspectionStatus,
    allowedDecisions: allowedDecisions,
    validateDecision: validateDecision,
    finalizeDecision: finalizeDecision,
    createActiveTimer: createActiveTimer,
    createAuditLog: createAuditLog,
    median: median,
    computeDashboard: computeDashboard,
    aggregatesForExport: aggregatesForExport,
    toCSV: toCSV,
  });
});
