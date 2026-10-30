# AEOS Revenue Validation Module

This module holds the commercial assets for the first paid AEOS experiment. It contains
no platform code and no student data. It exists to answer one question with evidence:

> Can AEOS collect money from a real buyer for a bounded deliverable, at an effective
> hourly rate worth repeating?

## Primary objective

Collect **$650 from one bounded project** while holding total weekly effort to roughly
**four hours**, and record every hour so the effective rate is measurable rather than
assumed.

## The single offer

**AEOS Education Deck Sprint — $650.** One offer, one client at a time. Full terms in
[`offer/deck-sprint-offer.md`](offer/deck-sprint-offer.md).

Adding a second package, a second concurrent client, or a new service before the first
project is paid and measured is scope creep. See [`PARKING_LOT.md`](PARKING_LOT.md).

## Sequence

```
Sample finished → 5 contacts → 1 paid project → measured rate → decide to repeat
```

Each stage gates the next. Do not run them in parallel.

## What is here

| Path | What it is | When you use it |
| --- | --- | --- |
| `offer/deck-sprint-offer.md` | Client-facing one-pager for the $650 offer | Send to a prospect |
| `offer/scope-and-terms.md` | Inclusions, exclusions, deposit, revisions, change orders | Before you agree to anything |
| `offer/intake-form.md` | The questions that start the 7-day clock | After deposit clears |
| `offer/proposal-template.md` | Fill-in proposal / simple SOW | To confirm a verbal yes in writing |
| `outreach/outreach-templates.md` | First-contact and follow-up emails, by contact type | Contacting the 5 |
| `outreach/coverage-pay-inquiry.md` | Draft to close the open coverage-pay question | One focused block |
| `quality/deck-quality-checklist.md` | Production standard every deck must pass | Before any deck ships |
| `portfolio/parent-night-reading-sample.json` | The six-slide sample, source of truth | Building the sample |
| `evidence/experiments.md` | The four income experiments, with pass/fail thresholds | Deciding what to keep |
| `evidence/time-and-income-log.csv` | Every hour and every dollar | Daily, 30 seconds |
| `PARKING_LOT.md` | Everything deliberately not being built yet | When a new idea arrives |

Runnable tools live in [`../../tools/revenue/`](../../tools/revenue/).

## Commands

One-time setup (only needed for `.pptx` output):

```bash
pip install -r tools/revenue/requirements.txt
```

Build the sample deck (writes an editable `.pptx` with speaker notes, plus a Markdown
review copy):

```bash
python3 tools/revenue/build_deck.py docs/revenue/portfolio/parent-night-reading-sample.json --outdir build/decks
```

Check whether the work is actually paying:

```bash
python3 tools/revenue/rate_report.py docs/revenue/evidence/time-and-income-log.csv
```

Run the tests for both tools:

```bash
python3 tools/revenue/test_revenue_tools.py
```

## Immediate next step

Finish the portfolio sample. One two-hour block, using
[`quality/deck-quality-checklist.md`](quality/deck-quality-checklist.md) as the gate.

**Definition of done:** `build_deck.py` produces a `.pptx` whose every content slide has
body content and speaker notes, every further-reading entry resolves to a page you have
opened yourself, and the checklist passes with no unchecked blocking item.

## Short-term roadmap

1. Sample finished and checklist-passed.
2. One AI-evaluation application submitted (one block; income counts only when paid work arrives).
3. Sample shown to five relevant contacts; replies logged.
4. One project sold, delivered, accepted, and fully logged.
5. `rate_report.py` run on the completed project; repeat-or-stop decision recorded in `evidence/experiments.md`.

## Long-term vision

The deck sprint is not the company. It is the cheapest honest test of whether AEOS can
convert subject-matter expertise into money that someone chooses to pay. A validated,
repeatable production process — intake, scope control, quality gate, measured delivery —
is the same machinery a paid pilot of an AEOS software module will need. The service
funds the platform and proves the demand signal; it does not replace either.

## Potential risks

| Risk | Why it matters | Mitigation in this module |
| --- | --- | --- |
| No buyer with budget and urgency | The whole experiment stalls at step 3 | Five contacts before any further build; stop gate below |
| Scope creep inside a fixed price | $650 over 25 hours is $26/hour, not $65 | `scope-and-terms.md` exclusions + written change orders |
| Unverified rate claims drive the plan | Platform rates are advertised, not earned | Every external rate marked unverified in `experiments.md` |
| Sample uses sources you have not opened | One bad citation ends a sales conversation | Checklist blocks shipping on unverified sources |
| Shared coursework presented as solo work | Authorship misrepresentation | Attribution rule in the checklist |
| Hours go unrecorded | The rate becomes a guess, so the decision is a guess | 30-second daily log; `rate_report.py` warns on missing hours |

## Success metrics

- One invoice paid in full.
- Deliverable accepted by the client without a second revision round.
- Every hour from first contact to final acceptance recorded in the log.
- Effective rate computed from real data, not estimated.
- A written repeat-or-stop decision.

## Stop gates

**BLOCKED until the sample passes the quality checklist:** do not contact prospects.
A sample that shows headings without content argues against you.

**BLOCKED until one project is paid and measured:** do not add a second package, a
second concurrent client, a storefront, a course, or a new module.

**BLOCKED for any work touching real student information:** this module handles
marketing and sample material only. Client source material must be approved, non-
confidential content the client has the right to share. No student records, no IEP
content, no identifiable student work. If a prospect offers any of it, stop and
re-scope before accepting.
