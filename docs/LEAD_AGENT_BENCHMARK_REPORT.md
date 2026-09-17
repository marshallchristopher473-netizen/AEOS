# Lead Qualification Agent v1 — Benchmark Report

**Date:** 2026-09-17
**Agent version:** 1.0.0 · **Dataset version:** 1.0.0 · **Answer key version:** 1.0.1
**Reproduce:** `python3 -m agents.lead_qualification.benchmark.run_benchmark --failures`

---

## Headline result

**Lead Qualification Agent v1 scores 98% across 100 standardized parent
inquiries, with zero catastrophic routing errors.**

"98%" means 98 of 100 cases were correct on **all five** decision fields
simultaneously — not an average across fields, which would read higher.

On the 20 held-out cases the agent had never been tuned against, it scores 95%.

---

## Scorecard

| Metric | Development (80) | Holdout (20) | All (100) | Gate | Result |
| --- | ---: | ---: | ---: | ---: | :---: |
| Intent classification | 100% | 100% | 100% | 90% | PASS |
| Qualification | 100% | 100% | 100% | 90% | PASS |
| Priority | 99% | 100% | 99% | 90% | PASS |
| Missing-information detection | 100% | 95% | 99% | 85% | PASS |
| Recommended-action | 100% | 100% | 100% | 90% | PASS |
| Catastrophic routing errors | 0 | 0 | 0 | 0 | PASS |
| **All five fields correct** | **99%** | **95%** | **98%** | — | — |

Gates are defined in `LEAD_QUALIFICATION_AGENT_V1_SPEC.md` §7 and were set
before the benchmark was run.

### Per-case format

Each case is scored on the five fields independently. Example, LQ-001:

| Test | Expected | Agent | Result |
| --- | --- | --- | :---: |
| Intent | tutoring_inquiry | tutoring_inquiry | PASS |
| Qualification | qualified | qualified | PASS |
| Priority | urgent | urgent | PASS |
| Missing data | availability | availability | PASS |
| Next action | escalate_to_human_now | escalate_to_human_now | PASS |

Any case's table: `run_benchmark --case LQ-001`.

---

## Catastrophic routing errors: 0 of 100

Two errors are tracked separately because they are the ones that cost a
business money or credibility rather than a little polish:

| Error | Count | Why it matters |
| --- | ---: | --- |
| A truly urgent inquiry ranked `low` | 0 | A parent with an exam in three days sits in a queue behind a price shopper |
| Spam or a non-lead escalated as `urgent` | 0 | Staff are paged for a phishing text, and stop trusting the system |

The second is actively probed. LQ-094 is a phishing SMS that opens with the
word **URGENT** and demands action "within 12 hours"; LQ-060 is form spam.
Both are correctly ranked `low`. The engine resolves qualification before
priority precisely so that no message classified as spam, unrelated, a job
application or out-of-scope can be escalated by urgency language it happens to
contain.

---

## Where the two failures are

| Case | Split | Field | Expected | Agent | Status |
| --- | --- | --- | --- | --- | --- |
| LQ-067 | dev | priority | `medium` | `low` | **Accepted.** A school counselor asking for rates so she can refer families has no home in the v1 taxonomy — neither `low` ("price-shopping with no commitment") nor `medium` ("genuine tutoring interest") is true of her. v2 adds a `referral_partner` intent |
| LQ-092 | holdout | missing_information | `[]` | `[start_timeline]` | **Known key inconsistency, deliberately uncorrected.** "Any evening this week works" is a meeting window; by the same reasoning applied to LQ-022 and LQ-065 the key should mark `start_timeline` missing. Correcting a holdout answer after seeing engine output would contaminate the split, so it stands and the agent is scored as failing it |

Full reasoning for both: `LEAD_AGENT_FAILURE_LOG.md`.

---

## Missing-information detection, per field

Exact-set match is a harsh metric — one field wrong fails the whole case — so
per-field precision and recall are reported alongside it. Scored over the 76
cases where the field list is not suppressed.

| Field | Precision | Recall | False positives | False negatives |
| --- | ---: | ---: | ---: | ---: |
| `grade_level` | 100% | 100% | 0 | 0 |
| `subject` | 100% | 100% | 0 | 0 |
| `contact_info` | 100% | 100% | 0 | 0 |
| `availability` | 100% | 100% | 0 | 0 |
| `start_timeline` | 97.9% | 100% | 1 | 0 |
| `learning_goal` | 100% | 100% | 0 | 0 |

The single false positive is LQ-092 above. Recall is 100% across all six
fields: the agent never tells a business a detail has been supplied when it has
not, which is the error direction that would cause a family to be contacted
with a confident, wrong assumption about their child.

---

## What the benchmark contains

100 synthetic inquiries across six channels (web form, email, SMS, voicemail
transcript, Facebook message, Google Business message).

| Category | n | Category | n |
| --- | ---: | --- | ---: |
| Urgent tutoring requests | 10 | Existing customers | 8 |
| Missing grade/subject information | 9 | Special circumstances (IEP, 504, ADHD, ELL, 2e, medical) | 8 |
| Price shopping | 9 | Vague inquiries | 8 |
| Spam | 8 | Immediate-start families | 7 |
| Out of scope | 6 | Scheduling requests | 5 |
| Unrelated | 5 | Job applications | 4 |
| Edge cases | 13 | | |

The edge cases are the ones worth naming, because they are where a keyword
matcher normally falls apart: a 400-word rambling email that buries the grade
and subject in the middle; text-speak with no punctuation; a hostile parent who
has already been ignored by three competitors; a non-native English speaker
writing "grade 8" instead of "8th grade"; a message asking for homework to be
completed for the student; a 10th grader enrolled in a course called *College
Algebra*; a kindergartener at the bottom edge of the served range; and a
two-child inquiry where one child is urgent and the other is not.

Answer key distribution: 15 `urgent`, 21 `high`, 29 `medium`, 35 `low`;
17 `not_a_lead`, 7 `out_of_scope`, 76 live leads.

---

## Method

1. **The rubric was frozen first** (spec §6): eight intents, four qualification
   states, four priority levels, six detected fields, nine actions, with
   explicit precedence rules.
2. **100 cases were written**, then **the answer key was written manually
   against the rubric**, with a one-sentence rationale per case, before any
   engine code existed.
3. **The engine was implemented from the rubric**, not from the cases.
4. **First run:** 78% of cases fully correct, gates marginal, zero catastrophic
   errors.
5. **Every failure was traced to a root cause** and repaired at the rule level.
   Nine rule changes, each with a regression test. Two answer-key problems were
   found; one was corrected with published reasoning, one was left open on
   purpose to protect the holdout.
6. **Re-run:** 98% of cases fully correct.

### The overfitting control

Cases LQ-001–080 are the development split; rules were tuned against them.
Cases LQ-081–100 were held out and **no rule was written or adjusted in
response to a holdout failure**.

The holdout tracks the development split within four points (95% vs 99%
all-fields-correct). That gap is the evidence that the nine repairs were
genuine generalizations rather than case patches — a keyword bolted on per
failing case would have driven the development split to 100% while the holdout
stagnated near its 75% baseline. It did not.

Three holdout cases (LQ-083, LQ-092, LQ-099) were fixed as a side effect of
repairs driven entirely by development-split failures. That is the intended
behaviour of a root-cause fix and is noted rather than claimed as independent
evidence.

---

## What this evidence supports — and what it does not

| Supported | Not supported |
| --- | --- |
| "Scores 98% across five decision fields on a 100-case standardized benchmark" | "Works on real parent inquiries" |
| "Zero catastrophic routing errors, including against spam that impersonates urgency" | "Increases enrollment" or "recovers lost revenue" |
| "Every decision is traceable to the specific rules that produced it" | "Saves N hours per week" |
| "Deterministic: identical input always produces identical output, at zero marginal cost" | "Understands parents" |

### Limitations, stated plainly

1. **The cases are synthetic and author-written.** The holdout split controls
   for rule overfitting. It does **not** control for authoring bias: the same
   person wrote the rubric, the inquiries and the key, so the distribution is a
   model of real inbound mail, not a sample of it. Real messages will be
   messier, and some will fail.
2. **One business profile.** Grades, subjects and exclusions are hard-coded for
   one K–12 tutoring business (spec §5). A business that tutors adults or
   teaches music inverts several answers.
3. **Rules, not language understanding.** The engine matches patterns. It will
   miss phrasings absent from the benchmark, and a message written to evade it
   would succeed. This is the accepted cost of determinism and zero marginal
   cost at v1.
4. **Single-turn.** One message in, one decision out. No conversation, no
   follow-up, no memory of an earlier inquiry from the same family.
5. **The response drafts are templates and are not scored.** No claim is made
   about their quality.

**A 98% benchmark score is not a validated product.** It clears one gate on the
validation ladder. The next gate is the only one that tests the assumption this
report cannot: whether real inquiries look anything like these.

---

## Validation ladder

```
BUILD → BENCHMARK → SHADOW PILOT → LIVE PILOT → CASE STUDY → PAID DEPLOYMENT
```

| Milestone | Status |
| --- | --- |
| A — 100 synthetic cases tested | **Complete** |
| B — Benchmark report | **Complete** (this document) |
| C — 20+ real historical inquiries, shadow mode | **Next.** See `TUTORING_PILOT_OFFER.md` |
| D — First tutoring-business testimonial | Blocked on C |
| E — First paid pilot | Blocked on D |
| F — Follow-up module (Agent #2) | Blocked on C |
| G — Recovery module (Agent #3) | Blocked on F |

Agent #2 is deliberately not started. Building a follow-up engine on top of a
qualification engine that has never seen a real inquiry compounds an unvalidated
assumption instead of testing it.

### The measurement Milestone C produces

Shadow mode makes the comparison the benchmark cannot: for 20–50 anonymized
historical inquiries, what the business actually did versus what the agent
recommends. Three numbers come out of it —

1. **Agreement rate** with what staff did, where staff got it right.
2. **Catch rate**: inquiries the agent flags `urgent` or `qualified` that
   received a slow response or none at all. This is the number the offer is
   built on.
3. **False-alarm rate**: escalations a business owner judges unnecessary.

Only after that does a claim about lost inquiries become defensible.

---

## Reproducing this report

```bash
# Score all 100 cases, with every failure printed
python3 -m agents.lead_qualification.benchmark.run_benchmark --failures

# One case in the Test / Expected / Agent / Result format
python3 -m agents.lead_qualification.benchmark.run_benchmark --case LQ-052

# Regenerate the scorecard table, or dump full per-case results
python3 -m agents.lead_qualification.benchmark.run_benchmark --markdown table.md
python3 -m agents.lead_qualification.benchmark.run_benchmark --json results.json

# 52 regression and invariant tests
python3 -m unittest discover -s agents/lead_qualification/tests -t .
```

Standard library only — no dependencies, no API keys, no network, no cost. The
runner exits non-zero if any development-split gate fails, so it works as a CI
regression gate unchanged.

---

## Privacy

All 100 cases are synthetic. No real parent, student or family data appears in
this repository, and none may be added to it. Phone numbers use the reserved
555-01xx range; email addresses use `example.com`. Real inquiries are handled
only under a signed pilot agreement and anonymized before ingestion
(`TUTORING_PILOT_OFFER.md` § Data handling).
