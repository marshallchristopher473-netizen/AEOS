# AEOS PBIP Section A — Evidence Readiness

A single-file, browser-local planning tool for Section A of a SPED 607 PBIP
(Positive Behavior Intervention Plan).

Its job is **not** to hold case data. Its job is to stop a student under
deadline pressure from believing they are further along than they are — so the
one thing it must never do is let a status read **Verified** when the thing that
status asserts is not actually backed by recorded state.

Same premise as [`ela-pilot/`](../ela-pilot): the software's role is to keep a
human honest, and every claim it displays has to be derived from evidence it
actually holds.

---

## Quick start

Open `index.html` in a browser. That is the whole install — no server, no build
step, no dependencies. It works from `file://`, from a USB stick, or emailed to
yourself.

```bash
node --test tests/logic.test.mjs   # 50 regression tests, no npm install needed
node tests/scenarios.mjs           # 61 end-to-end checks against a stubbed DOM
```

---

## What it will and will not do

| It does | It does not |
| --- | --- |
| Track six rubric criteria and their blocking conditions | Grade anything, or predict an instructor's score |
| Record permission gates as **your own notes** | Grant, prove, or stand in for any permission |
| Index abstract, non-identifying references to existing records | Store case data, raw FBA records, or anything identifying |
| Warn when text *looks* like it identifies someone | Guarantee that text is de-identified |
| Keep state in this browser only | Send anything anywhere — there are no network calls |

The banner boundary is load-bearing: **additional timed coursework observations
are blocked.** The app exists to help assemble a Section A from records the
school has already authorized, not to generate new observation data.

---

## The gate model

A criterion can only read **Verified** while every condition it rests on holds.

| Criterion | Conditions enforced in code |
| --- | --- |
| **A1** Observable target behavior | `action`, `onset`, `offset`, `exclusions` and `rule` all non-blank (`impact` is excluded — its own label says leave it blank until supported) |
| **A2** Justification | coursework-reuse permission; family pathway *if* a family-sourced reference is indexed |
| **A3** Baseline data | reuse + baseline-equivalence + instructor acceptance, and **two verified baseline references on two *different* days**, same context, 15–30 minutes each |
| **A4** Multiple-source synthesis | reuse, plus verified references of **at least two different kinds** |
| **A5** Functional hypothesis | reuse + baseline + instructor, and **A3 already verified** |
| **W** Professional writing | a non-blank draft reference |

Two rules make this hold up:

1. **Gates are continuous, not write-once.** Every change re-tests everything
   already marked verified. Revoke a permission, clear a definition field, or
   delete a reference, and whatever rested on it is demoted automatically and
   you are told what changed and why. `revalidate()` runs to a fixed point, so a
   demoted A3 also demotes the A5 that depended on it.
2. **One definition of each gate.** `gateFailure()` is the only place a gate is
   decided. The "set" path, the re-validation sweep and the next-action panel
   all call it, so they cannot drift apart.

Permissions chain too: coursework reuse cannot be marked verified until the
school-team row is, because you cannot hold authorization without being able to
name who gave it.

---

## Identifier screen

Free-text fields are screened for things that look like identifiers — a title
followed by a name, dates, emails, phone numbers, room numbers, long digit runs.

**It is advisory and it is not a guarantee.** It never blocks input, and it
cannot see what it was not taught to look for. Its only job is to make you look
again before a file leaves the device. The readable export states what the
screen found rather than asserting the file is clean.

---

## Your data

Everything lives in this browser under the localStorage key
`aeos_pbi_section_a`. Nothing is transmitted.

- **Export JSON** — a full backup, restorable.
- **Export readable summary** — the same content as text, carrying the screen's
  findings. It contains every section the JSON backup contains.
- **Delete all local data** — on *Sources & export*. Export first; it cannot be
  undone.

Restoring is atomic: a backup is only persisted once it has actually rendered.
If it cannot be drawn, your previous data is put back untouched. Values the app
does not recognise are dropped rather than carried through.

---

## Audit

The original prototype is preserved as the first commit of this directory so the
hardening is reviewable as a diff.

Six lenses audited it — state lifecycle, HTML injection, gate fidelity,
privacy/data-minimization, UI integrity, accessibility — each finding then
handed to an adversarial verifier told to refute it. **The verification pass was
cut short by a usage limit**: state, injection and gate findings were fully
verified, privacy was verified 1 of 5, and the integrity and accessibility
lenses were not verified at all. The tables below say which is which, because a
finding nobody tried to refute is weaker evidence than one that survived.

Severities are the verifier's, where one ran.

### Confirmed by adversarial verification

| Severity | Defect | Fix |
| --- | --- | --- |
| Critical | **A status could outlive its own precondition.** Gates were tested only at the instant a status was written; the fields and permissions they rested on stayed freely editable afterwards, and nothing re-checked | `revalidate()` runs after every mutation and re-tests everything currently verified, to a fixed point |
| Critical | **Downgrading a permission left every criterion that depended on it reading "verified"**, and the dashboard kept counting them | Same sweep, with a visible notice naming what was demoted and why |
| Critical | **A3 ignored the day label it collected.** Two references both marked `Day 1` — or both with no day — satisfied "two separate days" | The gate counts *distinct*, known days |
| Critical | **Stored HTML injection.** `badge()` interpolated state into `class="tag ${s}"` unescaped; a space-free payload (`<img/src=x/onerror=…>`) defeated the incidental `.replace(' ','-')`. The resulting script could rewrite every status to "verified" and persist it, subverting the one guarantee the tool exists to make | Enum-checked at the boundary and again in `badge()`; nothing unrecognised reaches markup |
| Critical | **The export asserted de-identification it never checked.** `exportText()` hard-coded `'Student A; no raw data'` above a verbatim dump of unscreened free text | The line is gone; the summary reports what the screen found and states that a screen is not a guarantee |
| High | **An imported backup wrote criterion statuses straight to "verified"**, bypassing every gate in `setCriterion()` | Imported state is normalized and then re-validated like any other change |
| High | **Import skipped the per-key normalization the load path applied.** A partial backup left nested keys undefined, so the dashboard threw on next navigation | One `normalize()` serves both paths |
| High | **A4 and A5 checked permission flags only** — both could be verified with an empty evidence index and A3 still blocked | A4 requires two distinct verified reference kinds; A5 requires A3 verified |
| Medium | **Unknown status rendered as "Verified".** With no matching `<option>` the browser shows the first one, which was `verified` | `sel()` coerces unrecognised values to `unresolved` |
| Medium | **`instructor` gated `next()` but not `setCriterion()`**, so A3 could be verified while the app recorded the instructor had not accepted the case | One dependency table drives both |
| Medium | **Arrays (`evidence`, `decisions`, `closeouts`) were normalized on neither path**, so a malformed array broke a page on every future load with no in-app repair | `normalize()` coerces them element by element |
| Medium | **The readable export hard-coded its attestation** (see the Critical row) while **`closeouts` were dropped from it entirely** | The summary carries every section the JSON backup carries |
| Low | **A1 validated one of its five stated clauses** — any non-blank `action` verified it | All of `action`, `onset`, `offset`, `exclusions`, `rule` required |

### Found, but not adversarially verified

The integrity and accessibility lenses finished; their findings were never
refutation-tested. Listed separately for that reason. Where a claim was
independently checkable I checked it myself, and said so.

| Severity | Defect | Status |
| --- | --- | --- |
| Reported critical | A persisted `permissions.reuse: null` made `badge()` call `null.replace`, so `render()` threw *before* `view.innerHTML` was written — a blank page on every later load, unrecoverable from the UI | **Reproduced by execution.** Note a *missing* key is repaired by the load path; an explicit `null` is not |
| Reported medium | A re-render — including one caused by a *refused* edit — discarded text typed into inputs not backed by state | **Reproduced by execution** |
| Reported medium | No code path could delete stored data; typing saved on every keystroke | **Verified by inspection** — the file contains no `removeItem` |
| Reported medium | The next-action panel never read criteria, writing or submission state and had no terminal branch | **Verified by inspection** |
| Reported medium | Selects had no accessible name; the current tab was indicated by colour alone; `.muted` failed WCAG AA | **Contrast re-measured independently**: `#708379` is 4.03:1 on white. The replacement is 4.92:1 on the page background |
| Reported low | Destructive removal had no confirmation and no undo | **Verified by inspection** |

### Refuted

Three findings did not survive verification and were **not** treated as defects:

- **"The import reports *Invalid app backup* while having already saved it."**
  Refuted, and I had repeated this claim before checking it. The file input
  exists only on the Sources page, whose render path touches none of the missing
  keys — so the import completes, the alert never fires, and the failure is
  **silent**. The data loss is identical; the user just gets no signal at all.
  The dashboard then throws on navigation and shows stale markup from the
  previous page.
- Two further findings were refuted as unreachable or not defects. The evidence
  status being uneditable after creation was among them; it is nonetheless
  editable now, as an improvement rather than a fix.

### Defects introduced by the hardening itself

Automated review of the hardening commit found three, all reproduced by
execution before being fixed. They were one mistake wearing three hats — **a
fallback that failed open** — which is now golden rule 5 in `CLAUDE.md`.

| Severity | Defect | Fix |
| --- | --- | --- |
| P1 | `permGateFailure()` ran only when the permission dropdown changed, so revoking school-team coordination left `reuse` — and A2 above it — reading verified. The hardening commit reintroduced the exact write-once defect it existed to remove | Permissions are swept by `revalidate()` alongside criteria and evidence |
| P2 | `asMinutes()` used `parseInt`, so a `30.9`-minute observation truncated to `30` and entered the qualifying window; `1e3` became `1` | Whole minutes only, by pattern, never by truncation. A duration that cannot be read exactly is not a duration |
| P2 | An unrecognised evidence `kind` defaulted to `EVIDENCE_KINDS[0]` — the **baseline** kind — inventing baseline evidence from a row that never named a source | Rows whose kind cannot be read are dropped, as codeless and duplicate rows are |

The purity test was also tightened: it compared raw source text, so the word
"window" in a *comment* failed it. It now strips comments and matches whole
identifiers, and additionally forbids `fetch` and `XMLHttpRequest`.

A second review round found three more, two of them data loss:

| Severity | Defect | Fix |
| --- | --- | --- |
| P2 | **Baseline evidence could be filed without choosing a source type.** After a successful add the form resets, and the Type `<select>`'s first option is the *baseline* kind. A user filling the next reference without touching Type silently filed baseline evidence; two of those on different days verified A3 — through ordinary UI use, no crafted import | The control now opens on "Choose a source type…" with nothing preselected, and `addEvidence()` refuses a blank kind |
| P2 | **Any JSON object was accepted as a backup.** Selecting the wrong file — a `package.json`, say — normalized to an empty state, rendered cleanly, replaced the user's work and reported "Restored." | `looksLikeBackup()` requires the app's own marker or at least three recognisable top-level keys; exports now carry `app`/`v` |
| P2 | **The 200-row cap was enforced in `normalize()` but not where rows are added.** Entry 201 was accepted and saved, then silently dropped on the next load | The add handlers refuse at the same boundary and say why |

The first of those is worth dwelling on: the stub-DOM scenario test for it
**passed while the bug was still live**, because the stub reused element objects
instead of recreating them on `innerHTML` assignment, so the select read empty
rather than showing its real default. A real-browser check caught it. The stub
now destroys and recreates children the way a browser does.

A third round found two more:

| Severity | Defect | Fix |
| --- | --- | --- |
| P2 | **The next action for W led to a dead end.** It routed to *Completion & submission*, which sets `S.writing.status` and has no control for `S.criteria.W`. Following the advice left W unresolved, the dashboard stuck at 5/6, and the same next action on screen indefinitely | `actionPage()` routes each criterion to the page where its blocker can actually be fixed — W to completion while its draft reference is blank, to rubric gaps once it exists |
| P2 | **A debounced edit was lost if the tab closed within 400 ms.** Worse, clearing a gating field could revert on reload *together with* the verified status that rested on it | `flushSettle()` on `pagehide` and on `visibilitychange` → hidden, which revalidates and persists synchronously |

The stub gained deferred timers and lifecycle events so the debounce genuinely
stays pending in tests — with timers running synchronously, the flush could not
have been tested at all.

A fourth round found two more:

| Severity | Defect | Fix |
| --- | --- | --- |
| P2 | **`__proto__` as a reference code escaped deduplication.** On a plain `{}`, `seen['__proto__'] = 1` hits the inherited setter rather than creating an own property, so `hasOwnProperty` stayed false. Two copies of one reference survived and satisfied A3's two-distinct-days rule, where any ordinary duplicate code collapses to one | `Object.create(null)` for the dedup set, and for the day and kind tallies |
| P2 | **A1's next action was the same dead end as W.** `actionPage()` returned `definition` unconditionally, so once the definition was complete the advice pointed at Measurement, which edits the definition but cannot set `S.criteria.A1` | The gate is now checked **first** for every criterion — if nothing blocks it, the destination is the page holding the readiness controls |

The second is worth noting against the round before it: the W dead end and the
A1 dead end were the same defect, and the fix for W was written per-criterion
rather than as a rule. Fixing the instance instead of the class left its twin
in the very function written to fix it.

A fifth round then found a *third* instance, which finally identified the real
cause:

| Severity | Defect | Fix |
| --- | --- | --- |
| P2 | **The conditional family-pathway blocker routed to the evidence index**, which has no permission controls. That requirement lives in the gate function but not in `CRITERION_PERMS`, so anything re-deriving the destination missed it | `gateBlock()` returns `{ why, where }` — one walk producing both the reason and the page it can be acted on. `gateFailure()` and `actionPage()` are now thin views of that single answer and cannot drift |

Three dead ends reached review because the reason and the destination were
computed by two separate walks over the same conditions. Each individual fix was
correct and none of them addressed that. The structural fix is golden rule 2
applied to routing: one definition, one walk, one answer.

A sixth round found the debounce reaching the exports:

| Severity | Defect | Fix |
| --- | --- | --- |
| P2 | **An export inside the 400 ms debounce window serialized the new text with the old statuses.** Clearing a verified draft reference and exporting at once produced a summary reading `status=verified, reference=""` — and no later validation can correct a file already downloaded | `flushBeforeExport()` settles and re-validates before either export, and tells the user what was demoted. `exportRaw()` deliberately does not flush: it is the recovery panel's "give me exactly what is on disk" escape hatch |

Both this and the page-exit flush are the same hazard: a debounce is a window in
which recorded state and displayed state disagree, and anything that *leaves* the
app during that window carries the disagreement with it. The exports are the
worst case, because the file outlives the session.

### Does the suite actually fail?

A suite that passes against the broken original would prove nothing. The same
scenario harness, unchanged:

| Target | Result |
| --- | --- |
| Original prototype | **27 passed, 29 failed** |
| Current build | **61 passed, 0 failed** |
| `tests/logic.test.mjs` | **50 passed, 0 failed** |

---

## How it is built

The file is deliberately one file, and deliberately split into two scripts:

- `<script id="aeos-logic">` — pure. No DOM, no storage, no side effects. Every
  gate decision lives here.
- `<script id="aeos-ui">` — DOM and storage only. Makes no gate decisions.

The test suite extracts the logic block straight out of the HTML and evaluates
it, which is what lets the critical behaviour be tested without giving up the
single-file property or adding a build step. A test asserts the logic block
never references `document`, `localStorage`, `window` or `alert`, so the split
cannot quietly erode.

---

## Known limits

- Statuses are **self-reported notes**. The app cannot verify that a permission
  was really granted, and says so wherever it shows one.
- The day labels (`Day 1`–`Day 3`) are deliberately opaque. They establish
  *distinctness* without recording real dates, which would be identifying.
- The identifier screen is a heuristic. It will miss things.
- The rubric encoded here comes from the working Section A template. Confirm the
  current Blackboard rubric and submission channel before relying on any of it.
