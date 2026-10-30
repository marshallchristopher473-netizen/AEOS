# Income Experiments Register

Four income experiments, each with a hypothesis and a pass/fail threshold set **before**
the result is known. An experiment without a threshold set in advance is a story you
tell yourself afterward.

## Verification status of external rates

Every rate below came from prior research recorded in the planning notes. **None was
independently verified when this file was written.** Advertised platform rates are what
a platform advertises — not what an applicant is accepted at, assigned, or paid.

Treat every figure here as a hypothesis to be replaced by a measured number from
[`time-and-income-log.csv`](time-and-income-log.csv) as soon as one real dollar arrives.

| Claim | Source | Status |
| --- | --- | --- |
| DataAnnotation advertises $25–50/hr for general projects | Prior research | Unverified; advertised, not earned |
| A curriculum-review listing advertised $13–38/hr | Prior research | Unverified; single listing, ~10 hrs/week expected |
| Upwork historical presentation-design rates $35–60/hr | Prior research | Unverified; historical platform average |
| Wyzant platform fee of 25% | Prior research | Unverified; confirm current terms before relying |

---

## Experiment 1 — Deck Sprint (primary)

**Experiment key:** `deck_sprint`

| Field | Value |
| --- | --- |
| Hypothesis | A bounded $650 presentation service can be sold to one education buyer and delivered in about 10 total hours. |
| Why it ranks first | Highest income per sale; work fits scheduled blocks rather than recurring appointments. |
| Baseline | No paying clients to date. |
| Method | Finish sample → contact 5 → sell 1 → deliver → measure. |
| Dataset | Every hour and dollar in `time-and-income-log.csv`. |
| Success threshold | One project paid in full **and** effective rate ≥ $50/hour across all acquisition, delivery, and admin hours. |
| Safety threshold | No confidential educational information handled at any point. A breach fails the experiment regardless of revenue. |
| Fail condition | Five contacts exhausted with no sale, **or** effective rate below $35/hour on the first completed project. |
| Decision if pass | Run a second project; only then consider offer #2 from the parking lot. |
| Decision if fail | Stop selling this offer. Reassess whether the failure was the offer, the price, or the contact list. |
| Status | Not started |
| Measured result | — |

**Note on the threshold:** $650 over 10 hours is $65/hour. The $50 threshold allows
real-world overrun. Below $35, the fallback options are better uses of the same evening.

---

## Experiment 2 — AI response evaluation

**Experiment key:** `ai_eval`

| Field | Value |
| --- | --- |
| Hypothesis | Evaluating AI responses produces usable income with near-zero client-acquisition overhead. |
| Why it ranks second | Lowest administration — no selling, no revisions, no invoicing. |
| Baseline | No application submitted. |
| Method | One focused block: complete one application. Assessment reportedly takes about an hour. |
| Success threshold | Accepted **and** paid work received within 30 days of applying. |
| Fail condition | No acceptance, or acceptance with no assigned work, within 30 days. |
| Known uncertainty | Acceptance and work availability are both outside your control. Flexible scheduling does not mean low mental effort — this is sustained-concentration work. |
| Accounting rule | **Income counts only when paid work actually arrives.** An accepted application is not revenue. Log application time as `admin` under this key; it reduces the effective rate honestly if income never comes. |
| Status | Not started |
| Measured result | — |

---

## Experiment 3 — Curriculum and assessment review

**Experiment key:** `curriculum_review`

| Field | Value |
| --- | --- |
| Hypothesis | Reviewing lessons, assessments, and rubrics — flagging factual errors, grade-level mismatches, and quality problems — matches existing auditing and classroom skill closely enough to pay. |
| Why it ranks third | The most overlooked fit. Closest to work already done well. |
| Baseline | No applications submitted. |
| Method | Apply selectively; accept only assignments that fit the four-hour weekly capacity. |
| Success threshold | One paid review assignment completed at ≥ $25/hour effective. |
| Fail condition | Minimum weekly commitment cannot be met inside the capacity limit. |
| Known constraint | The listing reviewed expected roughly ten hours weekly — **above** the capacity this experiment allows. Demand is demonstrated; this specific listing may not fit. |
| Status | Not started |
| Measured result | — |

---

## Experiment 4 — Tutoring (fallback)

**Experiment key:** `tutoring`

| Field | Value |
| --- | --- |
| Hypothesis | Middle-school reading, study-skills, or homework-system tutoring produces reliable income at $50–60/hour posted. |
| Why it ranks last | Familiar and reliable, but recurring appointments and preparation consume evenings — the scarcest resource. |
| Baseline | Prior classroom experience; no current clients. |
| Method | Direct rate if possible; platform only if direct fails. |
| Success threshold | ≥ $45/hour **net** including preparation, travel, and platform fees. |
| Fail condition | Net below $40/hour, or evening load exceeds the capacity limit. |
| Fee note | A platform fee reported at 25% would leave about $45 of a $60 posted rate before taxes and preparation. Preparation time is the part most often forgotten — log it. |
| Status | Not started |
| Measured result | — |

---

## Also tracked

**`coverage_pay`** — not an income experiment, but logged the same way. It may recover
pay for work already completed. Whether a correction is owed is unverified. See
[`../outreach/coverage-pay-inquiry.md`](../outreach/coverage-pay-inquiry.md).

---

## Capacity limit

**Roughly four hours per week across all experiments combined.** This is a proposed
limit, not another obligation — but if the log shows a sustained eight hours a week, the
experiment has quietly become a second job, and that is worth noticing deliberately
rather than discovering while exhausted.

Run `python3 tools/revenue/rate_report.py docs/revenue/evidence/time-and-income-log.csv`
to see the weekly load alongside the rate.

## Rules for this file

1. Thresholds are set **before** results. Never edited afterward to match an outcome.
2. "Measured result" is filled from the log, not from memory.
3. An experiment that fails its threshold is stopped, not quietly extended.
4. Distinguish honestly: hypothesis → internal test → pilot result → validated evidence.
   One paid project is a pilot result. It is not proof the business works.
