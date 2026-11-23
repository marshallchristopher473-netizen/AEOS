# Intake sheet — column contract

Google Sheet, one tab named exactly `Intake`. Row 1 holds the headers in
`intake-sheet.header.csv`, in that order, spelled exactly that way. The n8n nodes
map by column name, so renaming a column breaks the workflow.

| # | Column | Written by | Notes |
|---|--------|-----------|-------|
| A | `submission_id` | workflow | `AEOS-<execution id>-<n>`. Quoted in every email so a client reply can be matched to a row. |
| B | `submitted_at` | workflow | ISO 8601 UTC. |
| C | `full_name` | workflow | from the form |
| D | `work_email` | workflow | from the form |
| E | `phone` | workflow | may be empty |
| F | `organization` | workflow | from the form |
| G | `role` | workflow | from the form |
| H | `students_served` | workflow | band, not a count |
| I | `problem_statement` | workflow | free text |
| J | `timeline` | workflow | D1 input |
| K | `budget_authority` | workflow | D1 input |
| L | `priority` | workflow | `P1` or `P2` — output of D1 |
| M | `sla_due_at` | workflow | ISO 8601 UTC — output of D2 |
| N | `status` | **human** | `New` on write. Then `Contacted`, `Qualified`, `Disqualified`, `Won`, `Lost`. Only `New` and `Contacted` are swept by D3. |
| O | `owner` | **human** | who is working the lead |
| P | `first_contact_at` | **human** | when a human actually replied — the SLA measurement |
| Q | `outcome` | **human** | free text or one of the closing statuses |
| R | `notes` | **human** | free text |

Columns N–R are blank when the row is written. They are the human record. The
follow-up sweep reads `status` and `sla_due_at`; nothing in either workflow ever
writes to a row after it is appended.

## Privacy boundary

This sheet holds adult business-contact data only: names, work emails, phone
numbers and organizations of people who chose to contact AEOS. It must not hold
student names, student identifiers, grades, scores, IEP content or any other
student record. The form warns submitters twice. If a submitter pastes student
data into `problem_statement` anyway, delete it from the cell and note the
redaction in `notes` — do not leave it in the sheet and do not forward it.
