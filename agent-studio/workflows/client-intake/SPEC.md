# AI Client Intake & Follow-Up System — Workflow Specification v0.1

Status: **non-AI build**. No model is in this workflow. Every decision below is a
deterministic rule evaluated by n8n. AI is out of scope until v0.2.

---

## 1. Trigger

A prospective client submits the AEOS intake form.

One trigger, one path. v0.1 has no second entry point: leads that arrive by email,
DM, phone or referral are typed into the same form by the operator, so every lead
has exactly one origin and one shape.

---

## 2. Inputs

| # | Field | Type | Required | Allowed values |
|---|-------|------|----------|----------------|
| 1 | `full_name` | text | yes | free text |
| 2 | `work_email` | email | yes | validated as email by the form |
| 3 | `phone` | text | no | free text |
| 4 | `organization` | text | yes | free text |
| 5 | `role` | dropdown | yes | Teacher · Paraeducator · Special Educator · Instructional Coach · School Administrator · District Administrator · Parent · Other |
| 6 | `students_served` | dropdown | yes | 1–30 · 31–150 · 151–500 · 501–2,000 · 2,000+ |
| 7 | `problem_statement` | textarea | yes | free text |
| 8 | `timeline` | dropdown | yes | Immediately · This month · This quarter · This school year · Just exploring |
| 9 | `budget_authority` | dropdown | yes | I control the budget · I influence the budget · I do not control the budget · Not sure |

Derived at submission time, not collected: `submission_id`, `submitted_at`,
`priority`, `sla_due_at`, `status` (defaults to `New`).

No student data is collected. No field on this form may hold a student name,
student identifier, grade, score, IEP detail or any other student record.

---

## 3. Decisions

All three rules are deterministic. The same inputs always produce the same output.

**D1 — Priority tier**

```
priority = P1  IF  timeline        ∈ {Immediately, This month}
               AND budget_authority ∈ {I control the budget, I influence the budget}
priority = P2  otherwise
```

**D2 — Response deadline**

```
sla_due_at = submitted_at + 24 hours   IF priority = P1
sla_due_at = submitted_at + 72 hours   IF priority = P2
```

**D3 — Overdue follow-up**

```
overdue = TRUE  IF  status ∈ {New, Contacted}
                AND now > sla_due_at
```

`status` is set by a human (see §5). The sweep reads it; it never writes it.

---

## 4. Actions

| # | Action | Trigger | Target |
|---|--------|---------|--------|
| A1 | Append one row to the Intake sheet | every submission | Google Sheet `Intake` |
| A2 | Send acknowledgment email (fixed template) | every submission | the submitter |
| A3 | Send internal notification — `URGENT` subject prefix when D1 = P1 | every submission | the operator |
| A4 | Send overdue digest listing every row where D3 = TRUE | daily, 08:00 local | the operator |

A1 runs before A2 and A3. If the row fails to write, no email is sent.

---

## 5. Human approvals

| Gate | Who | What they decide |
|------|-----|------------------|
| G1 | Operator | Whether the lead is real and worth contacting. Nothing in the workflow qualifies or disqualifies a lead. |
| G2 | Operator | Every reply after the acknowledgment. The workflow sends no second message to a client, ever. |
| G3 | Operator | `status`, `owner`, `first_contact_at`, `outcome` and `notes` are typed into the sheet by hand. These columns are the record of whether a lead advanced. |
| G4 | Operator | Any change to the routing rules or email templates requires editing the workflow and re-running the acceptance cases in `test/acceptance-cases.md`. |

A2 is a fixed template that promises a reply window and nothing else. No price,
quote, proposal, scope, availability or commitment leaves this system without a
human writing and sending it.

---

## 6. Outputs

**Artifacts**

1. One row per submission in the `Intake` sheet — the single source of truth for leads.
2. One acknowledgment email per submission.
3. One internal notification per submission.
4. One overdue digest per day, sent only when at least one row is overdue.

**Measurements the outputs make possible**

| Metric | Read from |
|--------|-----------|
| Leads per week | count of rows by `submitted_at` |
| Time to first contact | `first_contact_at` − `submitted_at` |
| SLA hit rate | share of rows where `first_contact_at` ≤ `sla_due_at` |
| Overdue rate | rows where D3 = TRUE at digest time ÷ open rows |
| Conversion by tier | `outcome` grouped by `priority` |

These are counts of real events, not claims. No output of this workflow asserts
time saved, quality or any educational effect.
