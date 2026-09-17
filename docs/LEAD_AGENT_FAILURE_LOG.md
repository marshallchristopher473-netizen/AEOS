# Lead Qualification Agent v1 — Failure Log

Every benchmark failure, its root cause, the rule that changed, and the test
that now locks the fix in place.

Format: **Case → error → why it failed → rule change → regression test.**

Two categories are kept separate on purpose:

- **R-nn — rule changes.** The engine was wrong. The rule was repaired.
- **K-nn — key corrections.** The *answer key* was wrong or internally
  inconsistent. Changing ground truth to match an engine is how benchmarks get
  laundered, so each of these carries the reasoning that justifies it
  independently of what the engine produced.

Baseline before any repair (first run, 2026-09-17): intent 95% / qualification
98% / priority 92% / missing-info 85% / action 96% on the development split;
78% of cases fully correct; zero catastrophic routing errors.

---

## R-01 — Substring matching turned ordinary inquiries into existing customers

| | |
| --- | --- |
| **Cases** | LQ-053, LQ-059 (dev); LQ-055 (dev); LQ-083, LQ-099 (holdout) |
| **Error** | `intent: expected 'tutoring_inquiry' got 'existing_customer'`; on LQ-083 a spam message was classified as a current client and routed to support |
| **Why** | Marker matching used plain `in`. `"one of your tutors"` contains the substring `"our tutor"`. `"how your sessions are structured"` contains `"our session"`. Separately, `"dual-enrollment"` contains `"enroll"`, firing a buying signal on LQ-055 |
| **Rule change** | `agent._contains_any` now anchors every marker at both ends with `(?<![a-z0-9])…(?![a-z0-9])` |
| **Regression test** | `TestR01BoundaryMatching` — five tests, including that a genuine `"our tutor"` and a genuine `"ready to enroll"` still fire |

The highest-value fix in the set: one bug, five cases, and the worst single
outcome in the whole run (spam routed to a human as a paying client).

---

## R-02 — A bare mention of an excluded subject disqualified a real lead

| | |
| --- | --- |
| **Cases** | LQ-020 (dev) |
| **Error** | `qualification: expected 'qualified' got 'out_of_scope'`, and with it the priority, missing-information and action all fell over — a four-field failure on one case |
| **Why** | `"A friend of mine from my son's soccer team mentioned your name"` contains `soccer`, which is on the excluded-subject list. Scope was being decided by whether a word appeared, not by what the sender was asking for |
| **Rule change** | `extract.detect_excluded_subject` now only counts an excluded keyword when it sits in a sentence that also contains an ask (`do you`, `offer`, `teach`, `lessons`, `looking for`, `need`, `want`, `learn`, …) |
| **Regression test** | `TestR02ExcludedSubjectNeedsAsk` — the soccer mention stays qualified; `"Do you teach piano?"` stays out of scope |

---

## R-03 — A bare price question was unclassifiable

| | |
| --- | --- |
| **Cases** | LQ-004, LQ-039 (dev); LQ-082 (holdout) |
| **Error** | `intent: expected 'pricing_inquiry' got 'unclear'`, action `request_missing_info` instead of `send_pricing_then_book`. On LQ-082 the message was classified `unrelated` and archived — a real lead thrown away |
| **Why** | `classify_intent` checked for a tutoring signal (a child reference, a grade, the word "tutor") *before* checking for a price question. `"how much do u charge per hour"` has none of those, so it fell through to the catch-all before the pricing branch was ever reached |
| **Rule change** | The price-ask check moved above the tutoring-signal gate. A price question put to a tutoring business is a pricing inquiry whether or not a child is mentioned |
| **Regression test** | `TestR03PriceAskOrdering` — the bare price question classifies correctly, a *declarative* cost mention (LQ-040, "cost matters") still does not, and a genuinely off-topic message is still `unrelated` |

---

## R-04 — A named exam did not count as a learning goal

| | |
| --- | --- |
| **Cases** | LQ-007, LQ-011, LQ-061 (dev); LQ-092, LQ-096 (holdout) |
| **Error** | `missing_information` included `learning_goal` on cases the key marks complete |
| **Why** | `has_learning_goal` looked for a target grade, a named skill gap or a performance state. A parent who says "his SAT is in 9 days and he needs the math section" has stated the goal as precisely as anyone can, but named none of those three |
| **Rule change** | A dated academic event now satisfies `learning_goal`. Implemented by passing the existing deadline detection into `has_learning_goal` rather than adding new keywords |
| **Regression test** | `TestR04DeadlineImpliesGoal` — a named exam supplies the goal; an inquiry with no deadline still reports it missing |
| **Checked against** | Every key entry that marks `learning_goal` missing was re-checked for a detectable deadline. None has one, so the rule adds no false positives on the benchmark |

---

## R-05 — A stated working level was not recognised as a performance state

| | |
| --- | --- |
| **Cases** | LQ-062 (dev) |
| **Error** | `missing_information` included `learning_goal` for "ready for high school level math" |
| **Why** | `_PERFORMANCE_STATE` handled letter grades, numeric grades and "two years ahead" but not the level phrasing homeschooling parents use |
| **Rule change** | Added `_LEVEL_STATEMENT`, covering "ready for / working at / reading at / below / above … level" |
| **Regression test** | `TestR05LevelStatement` — the level statement counts; generic distress ("she's really struggling") still does not, which is the distinction the rubric turns on |

---

## R-06 — Week-scale phrases fired on past tense and on deadlines

| | |
| --- | --- |
| **Cases** | LQ-018, LQ-025, LQ-035, LQ-065 (dev) |
| **Error** | `start_timeline` reported present on four cases where the family never said when they wanted to begin |
| **Why** | Three separate over-matches: `"I called three places **this week**"` (past tense), `"if his math does not come up **by the end of** the quarter"` (a deadline, not a start), and `"cannot **get started** on anything"` (the child's executive function, not the parent's timeline) |
| **Rule change** | `"by the end of"` removed from the start-timeline pattern; `get (him\|her\|them) started` now requires the pronoun; and `this week / next week / this weekend` only count alongside a forward-looking verb in the same sentence |
| **Regression test** | `TestR06StartTimelineFalsePositives` — four tests, one per over-match, plus the positive case ("we want to start this week") |

---

## R-07 — "Cannot get started" read as buying urgency

| | |
| --- | --- |
| **Cases** | LQ-018 (dev) |
| **Error** | `priority: expected 'medium' got 'high'` |
| **Why** | `"He is bright but cannot get started on anything"` describes an ADHD symptom. `"get started"` was on the start-now signal list, so a description of the child's difficulty was read as the parent wanting to begin immediately |
| **Rule change** | Bare `"get started"` removed from `START_NOW_SIGNALS`; replaced with the forms that actually carry intent (`want to get started`, `ready to get started`, `get him/her/them started`) |
| **Regression test** | `TestR07GetStartedNotABuyingSignal` — the child's difficulty is medium; the parent's intent is high |

This one matters beyond the benchmark: the false signal appeared on a
special-education inquiry, which is exactly the population where a
mis-prioritized response does the most damage.

---

## R-08 — Families drop the word "grade"

| | |
| --- | --- |
| **Cases** | LQ-052 (dev) |
| **Error** | `qualification: expected 'qualified' got 'needs_info'` — a parent with a chemistry midterm *the next morning* was told to send more information |
| **Why** | `"shes in 11th"` matched no grade pattern, so `grade_level` was blocking |
| **Rule change** | Added `\bin\s+(\d{1,2})(?:st\|nd\|rd\|th)\b` |
| **Regression test** | `TestR08GradeWithoutTheWordGrade` — `"shes in 11th"` resolves to grade 11, and `"the meeting is on the 24th"` still resolves to no grade |

---

## R-09 — Offered meeting windows were missed

| | |
| --- | --- |
| **Cases** | LQ-011, LQ-050, LQ-052 (dev) |
| **Error** | `availability` reported missing where the family had named a window |
| **Why** | Availability was only recognised through a narrow set of framing words. `"could do a session tonight"` and `"move tomorrow's consult to Friday same time"` are both offers, and neither used one |
| **Rule change** | Added `could do`, `would work`, `see`, `meet`, `move`, `reschedule`, `switch`, `book`, `set up` to the availability context |
| **Regression test** | `TestR09AvailabilityContext` — four tests. Two confirm the new offers are caught; two confirm the original discrimination survives, so `"his final is on Friday"` and `"her annual review meeting is next Wednesday"` are still *not* availability |

The last two tests are the point of the entry. Widening availability detection
risks reintroducing the deadline/availability confusion the detector exists to
avoid, so the fix is pinned from both sides.

---

## K-01 — Key correction: a deadline is not a start date (LQ-022)

| | |
| --- | --- |
| **Case** | LQ-022 (development split) |
| **Original key** | `missing_information: ["availability"]` |
| **Corrected key** | `missing_information: ["availability", "start_timeline"]` |

**Why the key was wrong, independent of the engine.** LQ-022 says "the 11th
grader has a test next tuesday". LQ-024 says the application "is due October
1st". Neither parent says when they want to begin. The original key credited
LQ-022 with a start timeline and LQ-024 without one — the same construction
scored two different ways. The rubric defines `start_timeline` as "when they
want to begin", and neither message supplies it, so LQ-022 was corrected to
match LQ-024 rather than the reverse.

The engine was right and the key was wrong. Recorded here because a corrected
answer key is the one change that can quietly inflate a benchmark, and it
should never be invisible.

---

## K-02 — Key inconsistency deliberately left uncorrected (LQ-092)

| | |
| --- | --- |
| **Case** | LQ-092 (**holdout** split) |
| **Key** | `missing_information: []` — unchanged |
| **Status** | The agent is scored as **failing** this case |

LQ-092 says "Any evening this week works", which is a meeting window. Under the
same reasoning as K-01 — and consistent with LQ-065, whose "any afternoon next
week works" is keyed as *missing* a start timeline — `start_timeline` should be
marked missing here too.

It has not been corrected. LQ-092 is a holdout case, and editing a holdout
answer after seeing what the engine produced would contaminate the split and
destroy the only overfitting control the benchmark has. The inconsistency costs
one holdout case (missing-information holdout accuracy 95% rather than 100%),
which is a price worth paying for a number that means something.

**Planned:** correct in dataset v1.1, alongside a re-run and a fresh holdout.

---

## Accepted failure — LQ-067, a referral partner has no home in the taxonomy

| | |
| --- | --- |
| **Case** | LQ-067 (dev) |
| **Error** | `priority: expected 'medium' got 'low'` |
| **Status** | **Not fixed.** Accepted as a v1 limitation |

A school counselor asks for services, rates and sliding-scale information so
she can refer families. The rubric offers no good answer:

- `low` fits the letter of the rule — she asks about price and commits to
  nothing.
- `medium` fits the business reality — a counselor who refers families is worth
  more than any single lead in the benchmark.

The v1 taxonomy has eight intents and none of them is "referral partner", so
whichever value is chosen, something true is lost. The key keeps `medium` and
the agent returns `low`, and the case is carried as a failure rather than
papered over by bending either the rule or the key.

**v2 fix:** add a `referral_partner` intent with its own action
(`route_to_partnerships`). Counselors, pediatricians, school psychologists and
learning specialists are a distinct and valuable inbound channel that v1 cannot
represent.

---

## Two taxonomy gaps found but not yet acted on

| Gap | Case | What v1 does | What v2 should do |
| --- | --- | --- | --- |
| No distinct bucket for requests refused on academic-integrity grounds | LQ-053 (a parent asking for their son's homework to be completed for him) | `decline_and_refer`, the same bucket as "we don't teach piano" | A separate `decline_policy_violation` action. The response templates already diverge internally, because referring this request onward would be worse than useless — but the scored action cannot tell the two situations apart |
| Multi-child inquiries collapse to one record | LQ-022, LQ-100 | The most urgent child sets the record's priority | One decision record per student, linked to one family. Correct behaviour is already achieved for priority, but "grade 4 reading and grade 11 chemistry" cannot be represented as two distinct needs |

---

## Result after all repairs

| Metric | Before | After (dev) | After (holdout) |
| --- | ---: | ---: | ---: |
| Intent | 95% | 100% | 100% |
| Qualification | 98% | 100% | 100% |
| Priority | 92% | 99% | 100% |
| Missing information | 85% | 100% | 95% |
| Next action | 96% | 100% | 100% |
| All five fields correct | 78% | 99% | 95% |
| Catastrophic routing errors | 0 | 0 | 0 |

Nine rule changes, one key correction, one key inconsistency held open on
purpose, one accepted failure, and 52 tests. Every rule change was a repair to
a general detection rule — none added a keyword that only matches one benchmark
case, which is why the holdout tracks the development split instead of
collapsing.
