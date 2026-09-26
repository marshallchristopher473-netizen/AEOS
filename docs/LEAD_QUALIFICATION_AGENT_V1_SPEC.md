# Lead Qualification + Enrollment Agent v1 — Specification

**Status:** v1 scope frozen
**Owner:** AEOS
**Last updated:** 2026-09-17
**Related documents:** `LEAD_AGENT_BENCHMARK_REPORT.md`, `LEAD_AGENT_FAILURE_LOG.md`, `TUTORING_PILOT_OFFER.md`

---

## 1. What this is

A decision agent that reads a single inbound parent inquiry to a tutoring business and
returns a structured recommendation about what to do with it.

It does **not** contact anyone. It reads one message and produces one decision record.

**Commercial framing:** tutoring businesses lose revenue because inquiries are answered
late, answered inconsistently, or not answered at all. This agent reads every inquiry
the moment it arrives and tells the business which ones are urgent, which are qualified,
what information is missing, and what to do next.

**AEOS framing:** the same engine is the prototype for a future AEOS *Enrollment /
Family Intake* module. Building it as a commercial tutoring product first generates
revenue and real-world validation without expanding AEOS's current technical scope.

---

## 2. Frozen v1 scope

### In scope

| Capability | Description |
| --- | --- |
| Intent classification | What kind of message is this? |
| Qualification | Is this a lead the business can serve? |
| Priority | How fast does a human need to touch it? |
| Missing-information detection | What does the business still need to know? |
| Recommended next action | What should happen to this inquiry? |
| Ready-to-send response draft | Suggested reply text, for human review before sending |
| Reasoning trace | Which rules fired, so a human can audit the decision |

### Explicitly out of scope for v1

CRM integration · payments · SMS/email sending · calendar or booking integration ·
autonomous outbound contact of any kind · paid LLM API calls · multi-turn conversation ·
follow-up sequencing (Agent #2) · no-show and dormant-lead recovery (Agent #3) ·
dashboard UI · multi-industry generalization.

### Why v1 is a deterministic rule engine, not an LLM call

This is a deliberate engineering decision, not a limitation to apologize for:

1. **Zero marginal cost.** 100 benchmark cases cost $0 to run, so the benchmark can be
   re-run on every commit as a regression gate.
2. **Deterministic.** The same input always produces the same output, which is what
   makes a benchmark number meaningful. An LLM benchmarked once at 94% is not
   guaranteed to be at 94% tomorrow.
3. **Auditable.** Every decision carries the list of rule IDs that produced it, so a
   failure can be traced to a specific rule and repaired.
4. **Honest about what it is.** The claim this produces is "a rule system scores X% on a
   100-case benchmark", which is verifiable, rather than "AI understands parents".

Where an LLM belongs later (post-validation, behind the same benchmark as a regression
gate): response-draft phrasing, and a fallback classifier for messages the rule engine
marks low-confidence. See §9.

---

## 3. Input contract

One inquiry record:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | string | yes | Stable case identifier |
| `channel` | enum | yes | `web_form`, `email`, `sms`, `voicemail_transcript`, `facebook_message`, `google_business_message` |
| `received_at` | ISO 8601 string | yes | Used only for record-keeping in v1; priority is derived from message content, not clock time |
| `sender_name` | string \| null | yes | May be null |
| `sender_email` | string \| null | yes | May be null |
| `sender_phone` | string \| null | yes | May be null |
| `message` | string | yes | Raw inquiry text |

**Privacy:** the benchmark dataset is 100% synthetic. No real parent, student, or
family data is stored in this repository, and none may be. Real inquiries are handled
only under a signed pilot agreement, anonymized before ingestion (see
`TUTORING_PILOT_OFFER.md` §Data handling).

---

## 4. Output contract

```json
{
  "id": "LQ-001",
  "intent": "tutoring_inquiry",
  "qualification": "qualified",
  "priority": "urgent",
  "missing_information": ["availability", "learning_goal"],
  "next_action": "escalate_to_human_now",
  "response_draft": "Hi Dana — ...",
  "confidence": "high",
  "rules_fired": ["INT-01", "URG-02", "QUAL-01", "ACT-04"]
}
```

`intent`, `qualification`, `priority`, `missing_information`, and `next_action` are the
five **deterministic scored fields**. `response_draft`, `confidence`, and `rules_fired`
are unscored support output.

---

## 5. Business profile assumed by v1

The rules encode one concrete tutoring business. A different business changes the
profile, not the engine.

| Attribute | Value |
| --- | --- |
| Grades served | K–12 |
| Subjects served | Math, reading/ELA, writing, science, study skills, SAT/ACT prep |
| Formats | Online and in-person (local metro) |
| Not served | Adult learners, college coursework, graduate/professional exams, non-academic instruction (music, sports, driving), homework-completion-for-hire |

---

## 6. Decision rubric

This rubric is the **ground truth definition**. The 100-case answer key was written
against this rubric before any code was executed. Where the engine and the rubric
disagree, the engine is wrong.

### 6.1 Intent (8 values)

| Value | Definition |
| --- | --- |
| `tutoring_inquiry` | Seeking tutoring for a K–12 student, in any degree of detail |
| `pricing_inquiry` | The message's dominant ask is cost, rates, packages, or insurance/funding coverage |
| `scheduling_request` | Asking to book, move, or cancel a specific appointment or consultation |
| `existing_customer` | Sender identifies as a current client (has a tutor, a session, an invoice, an account) |
| `job_application` | Someone wants to work as a tutor |
| `spam` | Unsolicited bulk marketing, SEO/lead-gen pitches, crypto, phishing |
| `unrelated` | A real human with a real message that has nothing to do with the business |
| `unclear` | A genuine message too thin to classify (a greeting, a fragment, "?") |

**Precedence when signals conflict:** `existing_customer` > `scheduling_request` >
`job_application` > `spam` > `unrelated` > `pricing_inquiry` > `tutoring_inquiry` >
`unclear`.

Rationale: an existing customer asking about price is a retention conversation, not a
new lead. A new parent asking to book a consultation is a `scheduling_request`. A new
parent whose message is *mostly* "how much?" is a `pricing_inquiry` even though
tutoring is implied — because the correct reply differs.

### 6.2 Qualification (4 values)

| Value | Definition |
| --- | --- |
| `qualified` | A real prospective or current customer, in scope, with all three blocking fields present |
| `needs_info` | A real prospective customer, in scope, but at least one blocking field is missing |
| `out_of_scope` | A real person with a real request the business does not serve (§5 "Not served") |
| `not_a_lead` | Spam, job application, or unrelated — no sales or service follow-up applies |

**Blocking fields** (all three required for `qualified`): `grade_level`, `subject`,
`contact_info`.

`existing_customer` and `scheduling_request` from a known client are `qualified` by
definition — the business already has their details; blocking fields do not apply.

`out_of_scope` outranks missing information. An adult asking for graduate-exam tutoring
is `out_of_scope` even if they gave a phone number and a subject.

### 6.3 Priority (4 values)

Evaluated top-down; the first matching rule wins.

| Value | Triggers |
| --- | --- |
| `urgent` | A **dated deadline or event 10 days out or sooner** (test, exam, finals, IEP/504 meeting, report card, retention or failing decision, application deadline); an existing customer signalling cancellation, a billing error, or a safety/conduct concern |
| `high` | A dated deadline **11–30 days** out; wants to *start* immediately, ASAP, or this week; explicit buying signal ("ready to enroll", "how do I sign up", "send me the contract"); a booking or reschedule request; a prospect signalling they are about to go elsewhere ("nobody called me back", "I called three places"); any other existing-customer issue |
| `medium` | Genuine in-scope tutoring interest with no stated urgency, including vague inquiries and those missing information |
| `low` | Price-shopping with no commitment; an explicit deferral of *starting* by a month or more ("next semester", "in January", "after the holidays"); out-of-scope requests; spam; job applications; unrelated messages |

**Urgency boundary rule.** Urgency comes from a *deadline*, not from eagerness.
"We'd like to start this week" is `high`; "his final is this week" is `urgent`. Ten days
is the cutoff because it is the point past which a business can still schedule a normal
consultation rather than dropping everything — a deadline 9 days out is `urgent`, one
14 days out is `high`. Severity does not override the clock: a retention decision three
weeks away is `high`, not `urgent`, because it is still schedulable.

**Deferral rule.** Only an explicit deferral of *starting* demotes to `low`. A family
whose child returns to school next month but who wants help arranged now is `medium`,
not `low` — they are buying now.

**Catastrophic routing errors** (tracked separately, must be zero):
predicting `low` for a true `urgent` case, or `urgent` for a true spam/`not_a_lead` case.

### 6.4 Missing information (6 detected fields)

| Field | Present when the message supplies… |
| --- | --- |
| `grade_level` | A grade, year, or age that maps to K–12 |
| `subject` | A subject, course, or test the business teaches |
| `contact_info` | An email or phone in the record or the body |
| `availability` | Days, times, or a window the family can meet |
| `start_timeline` | When they want to begin |
| `learning_goal` | A stated desired outcome ("get back to a B"), a **named skill gap** ("fractions", "word problems", "letter sounds"), or a **specific performance state** ("sitting at a 58", "failing math", "dropped from Bs to Ds"). Generic distress — "she's struggling", "it hasn't improved" — does **not** count |

The first three are **blocking** (§6.2). The last three are tracked but do not block
qualification — few parents volunteer them in a first message, and demanding them is
what makes businesses lose leads.

**Relevance rule.** `missing_information` is empty whenever there is nothing to collect:
qualification `not_a_lead` (spam, unrelated, job application — there is no lead),
qualification `out_of_scope` (the answer is no regardless of what else they tell us),
and intent `existing_customer` (the business already holds their record). For every
other case, all six fields are evaluated.

### 6.5 Next action (9 values)

| Value | When |
| --- | --- |
| `escalate_to_human_now` | Priority `urgent` — a person must see it before any templated reply goes out |
| `book_consultation` | `qualified`, in scope, not urgent — offer consultation times |
| `request_missing_info` | `needs_info` — ask for the blocking fields, warmly and in one message |
| `send_pricing_then_book` | `pricing_inquiry` from an in-scope prospect — answer the price question and offer a consultation |
| `route_to_support` | `existing_customer`, non-urgent |
| `route_to_hiring` | `job_application` |
| `nurture_followup` | In scope but not buying now ("maybe next semester", far-future start) |
| `decline_and_refer` | `out_of_scope` — decline politely, refer out where possible |
| `archive_no_action` | `spam` or `unrelated` |

**Precedence:**

1. `escalate_to_human_now` outranks everything else. A price question with a test in
   three days is escalated, not templated.
2. For a `pricing_inquiry`, `send_pricing_then_book` outranks `request_missing_info`
   even when blocking fields are missing. A parent who asked "how much?" and got back
   only "what grade is your child?" is a lost lead. Answer the question first, ask for
   the details in the same message.
3. `route_to_hiring`, `decline_and_refer`, and `archive_no_action` follow directly from
   qualification and are never overridden except by rule 1.

---

## 7. Validation gate for v1

The agent is **not** done when it runs. It is done when it clears this gate.

| Metric | Gate |
| --- | --- |
| Intent accuracy | ≥ 90% |
| Qualification accuracy | ≥ 90% |
| Priority accuracy | ≥ 90% |
| Missing-information exact-set match | ≥ 85% |
| Next-action accuracy | ≥ 90% |
| Catastrophic routing errors | **0** |

Missing-information carries a lower gate because it is scored as an exact match of a
six-element set — a single field disagreement fails the whole case. Per-field
precision and recall are reported alongside it.

The benchmark is split: **cases LQ-001…LQ-080 are the development set** (rules may be
tuned against them) and **cases LQ-081…LQ-100 are held out** (no rule was written or
adjusted in response to a holdout failure). The holdout score is the number worth
quoting, and the gap between dev and holdout is the overfitting measurement.

**Definition of done for v1:** all six gates pass on the development set, the holdout
score is reported honestly whatever it is, every failure is recorded in
`LEAD_AGENT_FAILURE_LOG.md` with a rule change and a regression test, and the benchmark
runs from a clean checkout with no third-party dependencies.

---

## 8. What this evidence does and does not support

| Supported claim | Not supported |
| --- | --- |
| "Scores X% across five decision fields on a 100-case standardized benchmark" | "Works on real inquiries" — requires a shadow pilot |
| "Zero catastrophic routing errors on the benchmark" | "Increases enrollment" — requires a live pilot with a baseline |
| "Decisions are auditable to a specific rule" | "Saves N hours per week" — requires measured staff time before and after |

The benchmark is synthetic and author-written. It controls for rule overfitting via the
holdout split; it does **not** control for authoring bias — the same person wrote the
cases and the rubric. Real-world distribution is only established by Milestone C
(20+ real historical inquiries, shadow mode).

---

## 9. Deliberately deferred

| Deferred item | Gate that unlocks it |
| --- | --- |
| Agent #2: follow-up + appointment booking | v1 clears §7 |
| Agent #3: no-show / dormant-lead recovery | Agent #2 clears its own benchmark |
| LLM response-draft phrasing | Shadow pilot shows template drafts are the weak link |
| LLM fallback for `unclear` / low-confidence intents | Rule engine's residual failures concentrate in ambiguous text |
| Per-business configuration (profile as data, not code) | Second pilot business signs |
| CRM / calendar / sending integrations | A business asks to run it live |
| AEOS Enrollment module extraction | Commercial version has paying customers |

---

## 10. File map

| Path | Purpose |
| --- | --- |
| `agents/lead_qualification/schema.py` | Enums and the decision record |
| `agents/lead_qualification/profile.py` | The business profile from §5 |
| `agents/lead_qualification/extract.py` | Field detection (§6.4) |
| `agents/lead_qualification/agent.py` | Rule engine implementing §6 |
| `agents/lead_qualification/responses.py` | Response draft templates |
| `agents/lead_qualification/benchmark/dataset.json` | 100 synthetic inquiries |
| `agents/lead_qualification/benchmark/answer_key.json` | Ground truth per §6 |
| `agents/lead_qualification/benchmark/run_benchmark.py` | Scorer and report generator |
| `agents/lead_qualification/tests/` | Unit and regression tests |
