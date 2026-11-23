# Runbook — Client Intake v0.1 (non-AI)

One sitting, about 45–60 minutes. Do the steps in order; each one is verifiable
before you move on.

Prerequisites: an n8n instance that is reachable from the public internet
(self-hosted Community Edition is free; n8n Cloud works too), a Google account,
and the sending mailbox you want clients to see.

---

## Step 1 — Create the sheet

1. New Google Sheet named `AEOS Client Intake`.
2. Rename the first tab to exactly `Intake`.
3. Paste the contents of `spreadsheet/intake-sheet.header.csv` into row 1, one
   header per column, A through R.
4. Copy the sheet ID out of the URL:
   `https://docs.google.com/spreadsheets/d/`**`<THIS PART>`**`/edit`

**Verify:** row 1 reads `submission_id` in A1 and `notes` in R1.

---

## Step 2 — Connect credentials in n8n

Create two credentials:

- **Google Sheets OAuth2** — the account that owns the sheet.
- **Gmail OAuth2** — the mailbox that sends the acknowledgment and the operator
  notifications.

**Verify:** both credentials show a successful connection test in n8n.

---

## Step 3 — Import the workflows

Import both files (n8n → Workflows → Import from File):

- `n8n/01-client-intake.workflow.json`
- `n8n/02-followup-sweep.workflow.json`

Then in **each** workflow replace the placeholders:

| Placeholder | Replace with | Appears in |
|-------------|--------------|------------|
| `REPLACE_WITH_GOOGLE_SHEET_ID` | the sheet ID from Step 1 | both workflows, the Google Sheets node |
| `REPLACE_WITH_OPERATOR_EMAIL` | the address that should get internal alerts | 3 Gmail nodes total |

Select the Google Sheets credential on both Sheets nodes and the Gmail
credential on all four Gmail nodes. Imported workflows never carry credentials;
unselected credential slots are the most common reason the first test fails.

**Verify:** no node shows a red warning triangle in either workflow.

---

## Step 4 — Activate and get the form URL

1. Activate `AEOS — Client Intake v0.1`.
2. Open the **Intake Form** node and copy the **Production URL**. It ends in
   `/form/aeos-client-intake`.
3. Open that URL in a browser. The form renders with all nine fields.

**Verify:** the form loads for someone who is not logged into n8n — check it in
a private window or on your phone.

---

## Step 5 — Run the acceptance cases

Work through all five cases in `test/acceptance-cases.md`.

**Verify:** every expectation in that file holds. This is the gate. Do not move
to Step 6 or start any AI work until all five pass.

---

## Step 6 — Turn the sweep on

Activate `AEOS — Intake Follow-Up Sweep v0.1`. It runs daily at 08:00 in the
n8n instance's timezone (n8n → Settings → Timezone — set it before activating,
or the digest will arrive at the wrong hour).

**Verify:** one manual execution with nothing overdue finishes with zero items
after `Flag Overdue (D3)` and sends no email.

---

## Definition of done

All of the following are true at once:

- [ ] A person who is not you can open the form URL and submit it.
- [ ] Their submission appears as one row in `Intake` within 10 seconds.
- [ ] They receive an acknowledgment email quoting their `submission_id`.
- [ ] You receive one operator email, correctly marked urgent or standard.
- [ ] A row left open past `sla_due_at` shows up in the next daily digest.
- [ ] All five acceptance cases pass.
- [ ] No student data is in the sheet.

When those hold, the non-AI loop works and the gate is cleared.

---

## What is deliberately not here

These are known gaps in v0.1, not oversights. Add them when a real submission
proves one is needed, not before.

| Gap | Why it is acceptable in v0.1 |
|-----|------------------------------|
| No spam or bot filtering | The form is unlisted. If spam arrives, add a honeypot field before adding a captcha. |
| No deduplication | A person submitting twice creates two rows. The operator closes one. |
| No retry if Google Sheets is down | The run fails and n8n records the failed execution. Turn on n8n's error workflow or check the executions list weekly. |
| No CRM | The sheet *is* the CRM until the lead volume makes it painful. |
| No AI anywhere | That is the point of the gate. |

## Swapping components

- **Different form host** (Vercel page, Google Form, Tally): replace the Form
  Trigger with a **Webhook** node and map the incoming field names in
  `Apply Decision Rules`. Nothing downstream changes.
- **Different mail provider**: replace the Gmail nodes with **Send Email**
  (SMTP). The subject and body expressions copy across unchanged.
- **Slack instead of email for internal alerts**: replace the two operator Gmail
  nodes with a Slack node. Keep the acknowledgment on email.
