# Checklist Sign-off — Parent Night Reading Sample

Two passes run against
[`../portfolio/parent-night-reading-sample.json`](../portfolio/parent-night-reading-sample.json),
on separate days, per
[`deck-quality-checklist.md`](deck-quality-checklist.md).

## Verdict

**DOES NOT SHIP YET.** One blocking item is unmet: the four sources on the final
slide have not been opened. Everything else passes.

| Field | Entry |
| --- | --- |
| Deck | Supporting Your Middle Schooler's Reading at Home |
| Client / purpose | Portfolio sample for the AEOS Education Deck Sprint |
| First pass completed | 2026-10-28 (build and render) |
| Second pass completed | 2026-10-30 (fresh eyes, two days later) |
| Blocking items all passed | **No** — section C outstanding |
| Known limitations disclosed | Sources confirmed by search only, not opened |

## What each pass caught

### Pass 1 — 2026-10-28

| Finding | Section | Resolution |
| --- | --- | --- |
| The classroom example was labeled composite only in the speaker notes, not on the slide | H (privacy) | Added a `footnote` field to the deck schema; the label now renders on the slide |

### Pass 2 — 2026-10-30

| Finding | Section | Resolution |
| --- | --- | --- |
| **Reading Rockets is focused on PreK–grade 3.** Citing it first in a grades 6–8 parent deck sends the audience to the wrong place | C, E | Replaced with **AdLit** (adlit.org), WETA's grades 4–12 sister site. Speaker notes now say explicitly why Reading Rockets is not on the list |
| The National Center on Improving Literacy was listed as a general family resource, but most of its family material targets ages 0–5 | C | Kept, but narrowed to the one thing it genuinely offers this audience: the state dyslexia-law lookup, which supports the previous slide |
| The IES citation pointed at the WWC homepage rather than the relevant guide | C | Now cites *Providing Reading Interventions for Students in Grades 4–9* directly (`ies.ed.gov/ncee/wwc/practiceguide/29`) |
| "Colorin Colorado" was missing its accent | G (proper nouns) | Corrected to **Colorín Colorado** |
| Slide 6's fourth bullet wrapped to a second line with an unindented orphan, and mixed signals with the action | B (hierarchy) | The three questions moved to a closing line; the slide now makes one point |

## Section results

| Section | Result | Note |
| --- | --- | --- |
| A — Completeness | **Pass** | 6 content slides, all with body text; speaker notes on all 7 slides (83–251 words each); no placeholders. Enforced by `build_deck.py` |
| B — Density and hierarchy | **Pass** | Worst slide now 28 words against a 40-word limit; sources appear once; nothing pasted verbatim from a source |
| C — Sources and claims | **FAIL — blocking** | See below |
| D — Attribution | **Pass** | Original work, stated in `meta.attribution`; not adapted from coursework or client material |
| E — Audience fit | **Pass** | Grades 6–8 parents named in `meta.audience`; jargon avoided; one specific action stated |
| F — Visual consistency | **Pass** | One font pairing, one color set, fixed heading position; body 22pt, captions 16pt; verified by rendering all 7 slides |
| G — Mechanics | **Pass** | Proper nouns checked by eye; opens in LibreOffice and PowerPoint; editable `.pptx`, not a PDF |
| H — Privacy | **Pass** | No student names, records, or identifiable work. The one example is composite and labeled as such on the slide |

## Why section C fails

The checklist requires: *"Every source listed has been opened by you. Not recalled,
not assumed from the title, not produced by an AI tool and trusted. Opened."*

That has not happened. The cloud session's network policy blocked direct access to
`readingrockets.org` and `improvingliteracy.org`, so no page was fetched.

What *was* done on 2026-10-30: each of the four organizations was checked through web
search. All four exist, with the publishers and scope claimed on the slide —

| Source | Confirmed | Evidence standard |
| --- | --- | --- |
| AdLit (adlit.org) | WETA project, grades 4–12, parent tips, Spanish resources | Search results only |
| Colorín Colorado (colorincolorado.org) | WETA, bilingual, for families of English learners | Search results only |
| Improving Literacy (improvingliteracy.org) | US Dept. of Education funded, Boston University–led; state dyslexia-law tool | Search results only |
| IES practice guide 29 | *Providing Reading Interventions for Students in Grades 4–9*, WWC 2022007, March 2022, panel chaired by Sharon Vaughn | Search results only |

Search results are secondary evidence. They establish that these organizations exist and
broadly cover what the slide says; they do not establish that each page loads today and
reads as described. The checklist asks for the stronger standard, and the stronger
standard has not been met.

## To clear it

Open these four and confirm each loads and still covers what the slide claims:

- [ ] https://www.adlit.org/
- [ ] https://www.colorincolorado.org/
- [ ] https://improvingliteracy.org/
- [ ] https://ies.ed.gov/ncee/wwc/practiceguide/29

Then tick section C, change the verdict above to SHIP, and log the time in
[`../evidence/time-and-income-log.csv`](../evidence/time-and-income-log.csv).

Alternatively, allowing those domains in the environment's network settings would let the
pages be fetched and checked directly in a later session.
