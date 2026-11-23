# Acceptance cases — Client Intake v0.1

Submit each case through the live form URL. Use a real inbox you control for
`Work email` so you can confirm the acknowledgment actually arrives.

Re-run all five after any change to the workflow, the templates or the rules.

## Before you submit anything: run the rule check

```bash
node agent-studio/workflows/client-intake/test/verify-rules.js
```

It reads the Code-node JavaScript straight out of the two workflow JSON files and
runs D1, D2 and D3 against these cases offline — no n8n, no Google account, no
credentials. It catches a broken rule or malformed workflow JSON in two seconds,
which the live cases below would take twenty minutes to surface. It does **not**
test the form, the sheet write, or any email; only the five cases below do that.

---

## AC-1 — P1, budget holder, immediate

| Field | Value |
|-------|-------|
| Full name | Dana Reyes |
| Work email | *(your test inbox)* |
| Phone | 555-0101 |
| Organization | Riverbend School District |
| Role | District Administrator |
| Students served | 2,000+ |
| Problem | Our special-education team spends most of Friday writing progress notes by hand. |
| Timeline | Immediately |
| Budget authority | I control the budget |

**Expect**

- One new row, `priority` = `P1`, `sla_due_at` ≈ submission time + 24h, `status` = `New`.
- Acknowledgment email to the test inbox quoting the submission reference.
- Operator email with `URGENT (P1)` in the subject.
- Exactly one operator email — not both the urgent and the standard one.

---

## AC-2 — P2, no budget authority, immediate

Same as AC-1, but **Budget authority** = `I do not control the budget`.

**Expect** `priority` = `P2`, `sla_due_at` ≈ +72h, operator subject begins
`New intake (P2)`. Acknowledgment still sent.

---

## AC-3 — P2, budget holder, distant timeline

Same as AC-1, but **Timeline** = `Just exploring`.

**Expect** `priority` = `P2`. This is the case that proves D1 needs *both*
conditions, not either one.

---

## AC-4 — Optional field empty

Same as AC-1, but leave **Phone** blank.

**Expect** the row is written with an empty `phone` cell and nothing errors. The
operator email shows an empty `Phone:` line.

---

## AC-5 — Follow-up sweep fires

1. In the `Intake` sheet, take the AC-2 row and set `sla_due_at` to yesterday.
   Leave `status` as `New`.
2. Set the AC-1 row's `status` to `Qualified` and its `sla_due_at` to yesterday
   as well.
3. Execute the Follow-Up Sweep workflow manually.

**Expect**

- Digest email lists the AC-2 row only. The AC-1 row is excluded because
  `Qualified` is not an open status.
- `overdue_count` in the subject is `1`.
- No row in the sheet is modified by the sweep.
- Running the sweep again with every open row inside its deadline sends **no**
  email at all.

---

## Pass condition

All five behave as described, and after the run the only writes in the sheet are
the four appended rows plus the status edits you made by hand in AC-5.
