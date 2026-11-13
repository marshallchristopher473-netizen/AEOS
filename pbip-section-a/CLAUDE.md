# PBIP Section A — Build Brief

## Goal
A browser-local planning index that keeps a graduate student honest about what
Section A evidence they actually have. It generates **no** case data and holds
**no** student information.

## Non-goals
- No server, no build step, no dependencies, no network calls. Ever.
- No student data, no raw FBA records, no real dates, names or school details.
- No grading, and no prediction of an instructor's score.
- No support for conducting additional timed observations — they are blocked by
  the assignment's own permission boundary, and the app must never help plan one.

## Stack (do not substitute)
- One HTML file. Plain ES5-compatible JavaScript in two inline `<script>` blocks.
- `node --test` with `node:vm`-free host evaluation for the suite. No npm install.
- Node 20+ to run the tests. The app itself needs only a browser.

## Golden rules

1. **The logic block stays pure.** `<script id="aeos-logic">` must never
   reference `document`, `localStorage`, `window` or `alert`. A test enforces
   this. If it breaks, the suite can no longer load the logic and the critical
   behaviour silently stops being tested.

2. **One definition of every gate.** `gateFailure()` decides whether a criterion
   may read verified; `evidenceGateFailure()` and `permGateFailure()` do the same
   for references and permissions. The set path, the re-validation sweep and the
   next-action panel all call them. Never inline a gate condition at a call site
   — that is exactly how the original drifted into `next()` demanding instructor
   acceptance while `setCriterion()` did not.

3. **Gates are continuous, never write-once.** Every mutation goes through
   `commit()` (or `settle()` for debounced text), which runs `revalidate()`.
   Anything whose conditions stopped holding is demoted and the user is told what
   and why. A status may never outlive its own precondition.

4. **`normalize()` is the only trust boundary.** Both the load path and the
   import path go through it, and nothing else may construct state. Unrecognised
   values are dropped, not carried. The original had a per-key merge on load and
   a wholesale assign on import; that asymmetry was the root of three separate
   critical defects.

5. **Never assert what has not been checked.** No "no raw data", no "metadata
   only", no de-identification claim that code did not verify. Where the app
   reports a screen result, it also says a screen is not a guarantee. This rule
   outranks reassuring copy.

6. **Nothing unescaped reaches markup.** Text goes through `E()`; statuses go
   through the enum. Both `normalize()` and `badge()`/`sel()` coerce, because
   defence at the boundary alone was not enough — an unmatched `<option>` makes
   the browser display the first one, which is `verified`.

7. **Persist only what has drawn.** Import renders the candidate state before
   saving it, and restores the previous value and the previous storage entry if
   it cannot. `render()` never leaves the view blank: a throw shows the recovery
   panel so the user can export and reset.

8. **Destructive actions are confirmed and named.** Removal says which item, and
   warns that dependent criteria may be demoted.

## Domain model

```
Permissions  existing | additional | mentor   (locked, instructor-clarified)
             team → reuse → { instructor, baseline } → family (conditional)

Criteria     A1 definition-complete
             A2 reuse [+ family if a family reference is indexed]
             A3 reuse + baseline + instructor + 2 DISTINCT qualifying days
             A4 reuse + ≥2 distinct verified reference kinds
             A5 reuse + baseline + instructor + A3 verified
             W  non-blank draft reference

Evidence     { kind, code, day, mins, context, status }
             qualifying baseline = kind=baseline ∧ status=verified ∧ context=yes
                                   ∧ 15 ≤ mins ≤ 30 ∧ day ≠ unknown
```

`day` is an opaque ordinal (`Day 1`–`Day 3`), never a real date. It exists to
establish *distinctness* without recording anything identifying.

## When changing this file

1. Read the audit table in `README.md` first — every row is a defect that was
   reproduced by execution, and a change that reintroduces one will fail a test.
2. Add the gate to the logic block, not the handler.
3. Add a test to `tests/logic.test.mjs` that fails before your change.
4. Run `node --test tests/logic.test.mjs`.
5. If you touched render or storage, re-run the scenario harness against both
   this file and the original baseline commit — the harness must still report
   failures on the original, or it has stopped being able to detect anything.

## Definition of done

A student can open the file, see one next action with the specific reason it is
blocked, record permissions and non-identifying references, watch a status demote
itself when they revoke the permission under it, export a readable summary that
states what the identifier screen found, delete everything from inside the app,
and never once be told something is verified that is not.
