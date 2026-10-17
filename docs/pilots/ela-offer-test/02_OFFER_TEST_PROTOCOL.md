# ELA Offer Test — Protocol

**Status:** review-only draft. This protocol does not authorize outreach, charges, or a live checkout. Each of those
is a separate Decision Owner (DO) action taken only after the gates below pass.

## 1. Purpose and non-claims

The test measures one thing: **whether individual teachers pay for the bounded offer in
[01_BOUNDED_SCOPE_ONE_PAGER.md](01_BOUNDED_SCOPE_ONE_PAGER.md) at the pre-registered price, and whether delivery and
refunds work.**

It cannot support claims about learning, time saved, AI quality, or implementation. A positive result is a
demand signal for this one offer at this one price, and nothing more.

## 2. Pre-registration (fill before the first contact)

Fill and commit this table before any prospect is contacted. A later change is a logged deviation, not an edit.

| Field | Value |
| --- | --- |
| Hypothesis (one sentence) | |
| Price tested (must match the scope sheet) | |
| Prospect source and channel | |
| Number of prospects to contact (N) | |
| Test window (start date, end date) | |
| **ADVANCE threshold:** paid sales (S6) of N contacted | |
| **STOP threshold:** paid sales (S6) at or below which the offer is dropped | |
| **Safety threshold:** refunds or delivery failures that force STOP regardless of sales | |
| Frozen by / date / commit SHA | |

Report counts (for example "2 of 15"), not percentages, while N is under 30.

## 3. Test-mode checkout and refund gate

No prospect may be sent a payment link until every row passes. Store evidence such as screenshots and test
transaction IDs in the private store, never in GitHub. Do not record card numbers anywhere.

| # | Check | Pass (Y/N) | Evidence location | Date |
| --- | --- | --- | --- | --- |
| 3.1 | Checkout created in the payment provider's **test mode** at the scope-sheet price | | | |
| 3.2 | Test purchase completes and the receipt shows the correct price, seller name, and terms link | | | |
| 3.3 | Test refund completes and the provider shows the payment reversed | | | |
| 3.4 | Processing fee for the test transaction read from the provider (not estimated) | | | |
| 3.5 | Test transaction logged in the offer-test log with `payment_mode = test` and excluded from all counts | | | |
| 3.6 | Switching to live mode recorded as a separate DO decision, with date | | | |

## 4. Funnel stages

Each stage is counted only when the event is observed. Stages are never inferred from a later stage. A prospect who
pays without replying gets an S6 date and no S2 date.

| Stage | Event that counts | Does **not** count |
| --- | --- | --- |
| S1 Contacted | Outreach message sent | Prospect identified but not contacted |
| S2 Replied | Any reply from the prospect | Automatic out-of-office replies |
| S3 Scope viewed | Prospect received the one-pager or saw it on a call | Link sent but no confirmation it was seen |
| S4 Stated intent | Prospect says they want to buy | Positive feedback, "interesting", or "maybe later" |
| S5 Checkout started | Provider shows a started checkout (leave blank if the provider cannot show this) | Link clicked with no checkout session |
| S6 Paid | Live-mode payment confirmed by the provider | Test-mode payments, promises to pay, invoices sent |
| S7 Delivered | Files sent to the buyer | Files prepared but not sent |
| S8 Receipt confirmed | Buyer confirms they received the files | Silence |
| R1 / R2 Refund | Refund requested / refund completed by the provider | |

**Revenue is the sum of S6 amounts minus completed refunds.** Stated intent (S4) is never reported as demand or
revenue.

## 5. Log fields — [templates/offer_test_log.csv](templates/offer_test_log.csv)

One row per prospect. The filled log lives in the private store. The copy in GitHub stays blank.

| Column | Rule |
| --- | --- |
| `prospect_id` | P01, P02, … Never a name or email. The ID-to-contact key lives only in the private store. |
| `source_channel` | Where the prospect came from, such as a referral or a teacher community |
| `role` | Self-described role, such as classroom teacher. Leave blank if not offered. |
| `s1_contacted_date` … `s8_receipt_confirmed_date` | ISO date (YYYY-MM-DD) of the observed event, otherwise blank |
| `payment_mode` | `live` or `test`. Test rows are excluded from every count. |
| `amount_paid_usd` | From the provider, at S6 |
| `refund_requested_date`, `refunded_date`, `refund_amount_usd` | From the provider |
| `stop_condition` | The scope-sheet stop condition that fired, if any |
| `notes_no_pii` | Free text. No names, emails, or student information. |

## 6. Unit economics — [templates/unit_economics_ledger.csv](templates/unit_economics_ledger.csv)

One row per paid sale. **Every cost carries a status: `ACTUAL` or `NOT MEASURED`.** No cost is estimated, averaged,
or copied from another product.

| Cost | Source that makes it `ACTUAL` |
| --- | --- |
| Processing fee | The provider's transaction record |
| Delivery time | Minutes logged at the time of delivery, not recalled afterwards |
| Labor cost | Delivery minutes × the hourly rate the DO sets once, in the pre-registration commit |
| AI cost | The AI provider's usage record for that sale. `0` is `ACTUAL` only when the delivery record shows no AI request was made for that sale. |
| Other direct cost | An invoice or receipt |

**Contribution margin** = net revenue − (processing fee + labor cost + AI cost + other direct cost).
It is computed only when every cost in the row is `ACTUAL`. Otherwise the cell reads `UNCALCULATED`.

**Starting position:** no AI request occurred in the reviewed audit, and broader AEOS usage data was unavailable.
AI cost per delivery is therefore `NOT MEASURED` until the first sale's own record exists.

## 7. Decision at the end of the test window

Compare the log with the frozen thresholds in section 2. Choose exactly one:

| Decision | When |
| --- | --- |
| **STOP** | Paid sales at or below the STOP threshold, or the safety threshold was reached, or any scope-sheet stop condition fired |
| **REVISE** | Between the thresholds. Change one thing (price, deliverable, or channel), re-freeze section 2, and run again |
| **ADVANCE** | Paid sales at or above the ADVANCE threshold, the safety threshold was not reached, and every sale has a complete ledger row |

ADVANCE means "run a larger offer test or a paid pilot." It does not authorize marketing claims, platform work, or
student-data use.

## 8. Definition of done

The test is done when:

1. Section 2 was frozen before the first S1 date.
2. Every row in section 3 passed before the first payment link was sent.
3. N prospects were contacted, or the window closed, whichever came first.
4. Every S6 sale has a ledger row with each cost marked `ACTUAL` or `NOT MEASURED`.
5. The DO has recorded one decision from section 7, with date and reason.
