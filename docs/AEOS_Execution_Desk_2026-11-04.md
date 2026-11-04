# AEOS ELA pilot execution desk

Christopher Marshall · November 4, 2026 · supersedes the November 2 desk. Status recorded after independent source review, PR #64 repair, and a completed browser acceptance pass at the final SHA.

## Decision and actual progress

**Source checks pass. Browser acceptance now passes at the final SHA on a clean surface. The demonstration is ACCEPTED for offline adult tester use. Public hosted availability remains BLOCKED on one decision that is yours. Demand remains UNVALIDATED and no study is approved.**

The single change since November 2: the browser gate is closed. Everything in sections 2–5 below is unchanged, because all of it waits on inputs only you can supply.

| Requested work | Actual state | Next dependency |
|---|---|---|
| Independent re-verification of PR #64 | Complete. Five syntax checks and 37 tests pass; no unresolved source blocker | None. Done. |
| One usable demonstration | **Complete for offline use.** 46/46 browser checks pass at `e6f2de5` on `file://` and on a local same-origin host. Exact-source ZIP verified byte-for-byte | Hosted public link still needs your audience choice |
| Five ELA teacher interviews | Script, seven-slot register and one unaddressed Gmail draft prepared; **0 completed** | Confirm people and contact addresses, then schedule actual conversations |
| Two literacy coach interviews | One current coach identified as a proposed contact; **0 completed** | Identify/confirm both coaches |
| 3–5-teacher feasibility study | Canonical P-TER-01 v0.3 read; readiness and measurement forms prepared; **0 enrolled, 0 sessions** | Approved packet, independent reference reviewers, operating details |
| Strongest-substitute comparison | Separate prospective amendment drafted; **0 comparisons** | Select from actual interview workflows, then approve the amendment |
| Paid continuation | Conditional offer and transaction ledger drafted; **0 offers sent, 0 purchases** | Operational workflow, buyer authority, approved offer, payment evidence |

No invitation, interview response, consent, session result, provider purchase, sale, merge, AEOS P0 approval or P-TER-01 approval was invented or recorded as completed. No live-model evaluation was introduced. The Gmail draft is not an interview or a sent invitation.

## 1. Demonstration: verification complete

### What changed on November 4

The November 2 desk recorded overall acceptance as BLOCKED with one named cause: the final source had never been loaded by a browser. Source checks cannot see the difference that got the earlier AppDeploy host rejected — three platform scripts injected ahead of the CSP meta tag. That gap needed a browser.

A repeatable browser check now exists and passes.

| Item | Value |
|---|---|
| Source | `e6f2de5c3329c47f34face0732e714817cde3af1` (PR #64, draft) |
| Tree | `1cdae845a24d34146a4b636bb350010ea47655b8` |
| Baseline | `b9c68aa3e6fe35f676da04c10683bfdda12a9eed` |
| Runner | Chromium via Playwright, Node v22.23.4 |
| Surfaces | Offline `file://`, and a local same-origin HTTP host |
| **Result** | **46/46 checks passed on each surface, 0 failed** |
| Harness | `demo/pilot-review/tests/browser-acceptance.mjs` (PR #66, draft, stacked on #64) |
| Record | `demo/pilot-review/BROWSER_ACCEPTANCE.md` |

The five runtime files were hash-matched to the commit before the run; all five SHA-256 values match the independent verifier's table exactly. The 37 unit tests also pass on Node 22.23.4 — a third Node major, after the builder's and verifier's 24.22.1 and CI's 20.

### What the browser check covers

- **Standalone document integrity.** CSP meta byte-identical to the reviewed policy; zero scripts before the CSP meta tag; exactly three first-party scripts; no inline script. This is the precise condition AppDeploy failed, so it is asserted rather than assumed.
- **Containment.** Every request compared against the page's own origin: its own five assets and nothing else, on either surface.
- **Unscored criteria stay unscored.** The repair at this SHA is checked twice — through the disabled controls on R-004, R-005 and R-006, and again by bypassing the UI entirely to drive `setCriterionAction` with every score 0–4 against every null criterion in the fixture set. 45 of 45 attempts denied, nothing reaching `finalScore`. R-005's three *scored* criteria stay operable, so the guard is demonstrably targeted rather than a blanket lockout.
- **Decision gates.** All three decisions blocked before inspection completes; after flagging, REJECT alone unlocks on the blank response; submitting with no reason is refused and records nothing; reasoned REJECT records no numeric scores.
- **Evidence, injection, exports, reload, keyboard, 390px.** R-001's accept gate; R-010's invalid link blocking accept and revise until explicitly rejected, and not silently re-enabling acceptance afterwards; R-007's injection warning; the 21-field aggregate allowlist with both caveats and no response text, IDs or pseudonyms; unmeasured timing as `null` in JSON and blank — not `0` — in CSV; reload resetting to 0/12 with one SESSION_STARTED entry; no horizontal overflow and no control under 28px at 390px.

Two checks failed on first run. Both were the harness being wrong, not the demo: REJECT is correctly gated behind a complete inspection, and the CSV is correctly long-form `metric,value`. Both assertions were corrected to match the real contract rather than relaxed to pass.

### What this still does not establish

- **Nothing about any other hosted surface.** The check validates the surface it is pointed at. The owner-private Sites preview still reaches a sign-in wall; its served bytes remain unverified. Do not advertise that link as anonymously available.
- **Containment is observational.** No request was made; that is not proof none could be. Active exfiltration probing and CSP violation reporting were not performed.
- **Chromium only.** No screen-reader, Firefox, WebKit or real mobile-hardware pass.
- **Not approval of anything else.** Not AEOS P0 verification, not hosted security sign-off, not P-TER-01 approval, not demand validation. The demo stays synthetic, memory-only, mock-evaluated, with no model call, no backend and no persistence. It cannot establish grading time or workload savings.

### Offline package — ready to use now

`AEOS_ELA_Demo_e6f2de5.zip` contains the exact five runtime files, source manifest, SHA-256 list and instructions. Extract the whole folder and open `index.html`. This is now the **recommended** route for adult testers: it avoids any hosting overlay, needs no sign-in, and is the surface the browser check passes on. The November 2 caveat that it "does not count as fresh file:// browser acceptance" is **resolved** — that pass has now been performed.

### CI status at the final head

Unchanged from November 2. Backend, RLS and the static demo check succeed. Frontend validation fails at `npm audit --audit-level=low` with 21 vulnerabilities (16 moderate, 4 high, 1 critical); dependency-tree validation, lint, type-check and build are skipped after that failure, so no frontend build pass is claimed. Those dependency files are inherited and sit outside both PRs. **No gate was weakened and no merge occurred.** PR #66 does not touch them.

### Open pull requests

| PR | State | Contents |
|---|---|---|
| [#64](https://github.com/marshallchristopher473-netizen/AEOS/pull/64) | draft, unmerged | The demo: 10 added files under `demo/pilot-review/**` and `.github/workflows/pilot-demo.yml` |
| [#66](https://github.com/marshallchristopher473-netizen/AEOS/pull/66) | draft, unmerged | Browser acceptance harness + record. Based on #64's branch; 2 added files |

Keep both draft until #64's merge requirements are satisfied.

## 2. Seven discovery interviews

Unchanged from November 2. **0 completed.**

**Do discovery before showing the positioning statement.** Ask about a real recent task rather than whether someone likes an AI idea. Do not request or copy student work. Take minimal coded notes with permission; no audio/video recording by default. Do not publish quotations without separate permission.

Proposed people are a shortlist, not an authorized recipient set or a completed sample. Current school directories support the roles below; recent direct-email addresses sometimes differ from directory addresses. Do not guess aliases or send to every available teacher.

| Slot | Proposed person / eligibility | State |
|---|---|---|
| T01 | Kimberly R. Carter, MVMS Language & Literature content specialist; confirm recent classroom ELA feedback responsibility | Unconfirmed |
| T02 | Cesar M. Fortuna, MVMS Language & Literature teacher | Unconfirmed |
| T03 | Danica Lee, MVMS Language & Literature teacher | Unconfirmed |
| T04 | Stephen M. Smith, MVMS Language & Literature teacher | Unconfirmed |
| T05 | Cynthia J. Vance, MVMS Language & Literature teacher | Unconfirmed |
| C01 | Dr. Jenise B. Leach, Briggs Chaney MS literacy coach | Unconfirmed |
| C02 | Not identified. A current ELA content specialist is not automatically a literacy coach | Open |

Sources checked: [MVMS staff directory](https://www.montgomeryschoolsmd.org/schools/mvms/staff/directory/), [Briggs Chaney directory](https://www.montgomeryschoolsmd.org/schools/briggschaneyms/staff/directory/). Directory presence does not establish willingness, purchasing authority or your intended contacts. You may replace the entire shortlist.

### Neutral 15-minute guide

1. "Think about the most recent ELA response or writing task you gave feedback on. When was it, what did students need to do, and what feedback did you need to produce?" Ask for a verbal account, not a student artifact.
2. "Walk me through what you actually did, from opening the task to returning the feedback." Probe batch size, setup, rubric, reading, drafting, editing, saving/returning and reopening after a failure. Separate remembered estimates from measured time.
3. "Which tools did you use at each step? Which were school-provided, paid personally, free, or manual?" Ask which tool they would use tomorrow if AEOS did not exist.
4. "Describe the most difficult correction you made during that task. What was wrong, how did you notice, and how did you decide the final feedback?" Ask about unsupported evidence, mismatched rubric judgments, missed nuance, dialect and score corrections without implying that any occurred.
5. "What did you double-check or redo? What happened if you disagreed with a suggestion or something failed?" Probe recovery and work outside the main interface.
6. "When was the last time you adopted or paid for a feedback tool? What triggered it, who approved it and which budget paid?" Ask whether they can personally authorize a purchase, recommend one, approve a department budget, or only refer to another role. Do not infer school authority from title.
7. "What would have to improve for you to switch from your current procedure? What would make switching a poor trade?" Ask for a concrete next-task criterion, including a reason to keep the incumbent.

Only then test the supplied statement: **"AEOS helps middle-school ELA teams inspect the evidence behind draft feedback, correct unsupported judgments and retain clear human decisions."** Ask them to paraphrase it, identify the relevant step in their recent task, say what sounds unnecessary, and describe the evidence they would need. Record it as a positioning hypothesis, not a proven benefit.

For coaches, also ask about the most recent feedback calibration/support task they personally handled, differences across teachers and the actual procurement path. Keep their answers separate from the five classroom-teacher interviews.

### One form per actual conversation

`Interview code | role/eligibility | date | permission for notes | most recent task/date | actual sequence | tool at each step | hardest correction and detection | setup/edit/recovery burden (reported vs measured) | incumbent tomorrow | last adoption/payment example | personal/department purchasing role | switching condition | rejection/negative evidence | statement paraphrase | next step | source-note reference`

Leave fields blank or "not reported"; never fill from assumptions. Summarize teacher and coach counts separately. Seven interviews are qualitative discovery, not population demand validation.

One **unaddressed, unsent** Gmail draft exists: "Optional 15-minute conversation about teacher feedback workflows," draft `r-2693725268775707139`. It states independent-project status, no MCPS endorsement, optional participation, no student data, no recording and no purchase obligation. Resolve recipients before addressing or sending it.

## 3. Feasibility study: controlling packet and run gate

Unchanged from November 2. **0 enrolled, 0 sessions. BLOCKED.**

The recovered P-TER-01 v0.3 packet explicitly says **proposed review candidate; human approval, instrumentation and participant-run gates OPEN**. No newer signed approval was established. "Run the approved study" cannot be recorded as authorization evidence for a missing approved version.

Preserve that packet. Its smallest route is a controlled fixture-assisted experiment: target four consenting adult teachers (permitted 3–5, fixed before invitations), eight distinct experimental responses per teacher, four manual and four frozen-fixture reviews, the attendance interpretation task, and three separate 0/1/2 criteria without a total. Blank/off-task is NA. Short on-task answers remain scorable under that rubric. **The four-criterion 0–4 Rivergate demonstration is not this study implementation** — and the browser acceptance pass in section 1 does not change that. A passing demo is not an approved study instrument.

Before study invitations, complete and retain:

- The actual approved packet/version and hashes, or all required documented approvals for v0.3; missing registry reconciliation or an independent scope ruling.
- Two qualified independent ELA reference reviewers, independent of draft authors and blind to drafts/timing; a third independent adjudicator; resolved references, A/B matching, rubric, training and planted-check approvals. Key-exposed adults cannot be comparative participants.
- Exactly versioned study materials and original frozen drafts, declared handcrafted/provider origin, no live calls by default; approved study adapter/measurement forms and a complete preflight.
- Named study/incident owner, restricted storage and access roster, consent/withdrawal contact, exact withdrawal/deletion dates and method, compensation/staff budget and any provider budget. The proposed $25 provider cap is not spending authorization.
- Authoritative original/final artifacts and terminal receipts; reload/recovery, duplicate decisions, evidence gates, unknown versions, keyboard/access and no unauthorized finalization checked on the exact study build.

Use the four counterbalanced sequences in v0.3 and record the random seed/draw and actual within-block order. Each teacher sees a response once. Training uses new nonexperimental material. Do not show reference answers between blocks or add enrollment after inspecting results. Do not pool manual/fixture/live conditions or count task attempts as independent teachers.

### Full workload and quality records

Use the packet's forms and decision thresholds unchanged unless prospectively amended. Record common setup, condition setup, training and repeats, all task work, editing, wait, technical/facilitator recovery, external breaks and debrief. Time from response availability to confirmed terminal receipt; failed saves keep running. **The demo idle/click timer cannot replace this record.**

Mutually exclusive states: `REVIEW`, `EDIT`, `WAIT`, `RECOVERY`, `EXTERNAL_PAUSE`. Service time = elapsed minus documented external pause; active teacher work = review + edit + recovery. Product failures are recovery, not excludable interruptions. Report staff time separately. Show all one-time preparation and all draft attempts, generation/validation/repair time and actual charge evidence; allocate only according to the frozen exposure rule, without double-counting overlapping work/latency. Missing timing boundaries make the affected comparison unavailable.

Keep original draft and teacher final separately. Independent reviewers adjudicate final quality, criterion agreement, unsupported propositions, evidence validity and severity. Teacher edits are correction observations, not automatically model errors. Count cosmetic/substantive changes, rejection, abandonment, assistance and incidents, including unfavorable results. Do not make a time benefit claim if final quality worsens or denominators/matching are unresolved.

Blank event header:

`event_id | run_id | teacher_code | protocol_hash | build/tree | condition | block/order | task/hash | UTC | monotonic_seconds | state/event | actor | original_artifact_ref | final_artifact_ref | receipt_ref | reason/incident_ref | supersedes_event_id`

Blank task/quality header:

`run/task | attempted/completed/abandoned | original draft ref | final ref | three final criteria/NA | evidence refs | disposition/reason | cosmetic/substantive changes | start/stop/receipt | REVIEW | EDIT | WAIT | RECOVERY | EXTERNAL_PAUSE | setup/training refs | help/deviation | rater1 | rater2 | adjudication | uncertainty/severity`

Current observation cells are empty. The existing packet contains the full consent and collection forms; this desk does not approve or overwrite them.

## 4. Separate prospective substitute amendment — DRAFT, not approved

Unchanged from November 2. **0 comparisons.**

Local working label **CMP-ELA-01 draft 0.1** is newly proposed, not an existing registry identifier. It must not change, unlock or append a competitor condition to the base study silently.

**Question:** Does the evidence-inspection/correction workflow produce a specific useful advantage over the strongest tool teachers already use, at acceptable final quality and complete workload?

Select the incumbent after interviews based on actual recent use, suitability for the same task and access. Manual Google Docs feedback may be the real incumbent. **Brisk is provisional**, because current official documentation describes rubric-based feedback, Google Docs comments and teacher review before comments are saved. Its October 2026 batch instructions also require direct viewing before approval. Human review by itself is therefore not an established unique AEOS feature. These are vendor-documented capabilities, not a hands-on competitor test or proof that Brisk lacks evidence inspection. Sources: [Give Feedback](https://help.briskteaching.com/hc/en-us/articles/39310182411412-How-To-Give-Feedback), [Batch Feedback](https://help.briskteaching.com/hc/en-us/articles/40848467709716-How-can-I-give-feedback-to-multiple-students-at-once), checked November 2, 2026.

Before collecting a competitor result, sign and date a separate plan specifying the chosen product/plan/version, current price, permission/data terms, workflow configuration, model/settings where disclosed, all prompts and retry rules, training, outcomes, analysis and rejection criteria. Use a separate cohort and newly authored, independently matched materials; protect existing A/B forms and reference keys. Freeze a new allocation/order before recruitment. If comparing live Brisk with frozen AEOS fixtures, explicitly label the unequal generation conditions and keep end-to-end live and review-only findings distinct; do not call the result a fair live-product comparison by default.

Use the same final-artifact requirements and independent adjudication in both arms, with source attribution blinded where possible. Count installation, account/setup, rubric loading, reading, editing, transfer/export, wait, rejection, retries and recovery. Retain first outputs and all attempts; no best-of-N cherry-picking. Log interface constraints and unavailable functions as outcomes, rather than silently repairing one product more than the other. Keep costs, teacher/staff burden, failures and qualitative preference separate. Do not pool these observations into the base feasibility result. No comparative result exists yet.

## 5. Paid continuation — conditional offer and purchase record

Unchanged from November 2. **0 offers sent, 0 purchases.**

Offer only after the workflow actually operates, required evidence/data gates pass and a teacher or authorized buyer wants continued use. Keep any offer after outcome collection and debrief to avoid influencing study responses. Confirm the payer and procurement authority; a teacher's personal interest is not school authorization.

**Draft price hypothesis for review:** one teacher, 30 days of the operational synthetic-only workflow, $10 one-time, no automatic renewal. Specify exact access dates, supported scope, support, data handling, cancellation/refund terms and payment method before sending. Do not promise live grading, student-data use, savings or school integration that has not been verified. This amount is a proposed experiment, not an approved invoice or a claim of market price.

Draft wording: "You have now used the operational synthetic workflow. If it solves a task you want to keep doing, the proposed continuation is [exact scope and dates] for [approved fee], paid once with no automatic renewal. Participation in the study does not require purchase. Please decline if your current tools work better. A school purchase requires your normal authorization process."

Ledger header:

`buyer_code | authority/payer | operational version | stated interest/date/exact wording | approved offer/terms/date | accepted offer/date | invoice/order reference | payment status | actual amount/currency | receipt/settlement reference/date | refund/chargeback | access delivered/dates | actual use | later renewal/payment`

Use separate statuses: interest → offer → accepted → payment pending → paid → delivered → renewed/refunded. Count **paid** only from actual payment/settlement evidence; accepted terms, a draft invoice or "I would pay" is not a purchase. Report gross receipts and refunds separately. No payment request was sent and no buyer was charged.

## 6. Copy-paste AI prompts for the remaining work

Use one builder plus one independent verifier for bounded changes. Base44 credits are not required to rebuild this static demonstration. Do not open parallel implementations on Base44, AppDeploy and Vercel.

**Prompt H from the November 2 desk is retired.** Its job — verify a clean tester URL — is now done for the offline and same-origin cases by `demo/pilot-review/tests/browser-acceptance.mjs`, which is repeatable and takes a URL argument. Point the harness at any future host instead of re-running a manual audit:

```bash
node demo/pilot-review/tests/browser-acceptance.mjs https://your-host/index.html
```

It exits non-zero on any failure and prints each failed check. A pass certifies that surface at that moment and nothing else.

### H′ — Publish one clean tester URL, after you choose the audience

```text
Continue the existing AEOS Teacher ELA Synthetic Demo Sites project appgprj_6ae8afbafcf481918cbee9d03a1d1f42; do not create another project or rebuild the UI. The approved candidate is AEOS PR64 e6f2de5c3329c47f34face0732e714817cde3af1, tree 1cdae845a24d34146a4b636bb350010ea47655b8. Read the actual current Sites state and preserve its identity. Apply only my explicit audience choice. Never guess viewer emails, weaken CSP or use an overlay-instrumented host. After publishing, run demo/pilot-review/tests/browser-acceptance.mjs against the live URL and paste the full output. Confirm the served assets match the five source SHA-256 values. Distinguish source inspection from active network testing and disclose unperformed probes. Recheck PR head and deployment version at the end. Return READY or BLOCKED with exact evidence; this is not P0 or P-TER-01 approval. Do not send invitations as part of verification.
```

### I — Recruit and synthesize discovery, once contacts are resolved

```text
Use the confirmed five ELA teacher and two literacy coach identities supplied in this session. Reuse the existing unaddressed Gmail discovery draft r-2693725268775707139; do not send duplicate invitations or guess addresses. Offer an optional 15-minute discovery interview using the execution desk's neutral recent-task guide. Keep interviews separate from the feasibility study. Do not request student work or imply school endorsement. Collect actual answers with notes permission; keep unanswered fields missing. Ask recent task, current tools, hardest correction/detection, full setup/edit/recovery burden, last adoption/payment and actual purchasing role before showing the positioning statement. Summarize seven coded cases and negative evidence, teachers and coaches separately. Label remembered time estimates and hypothetical prices explicitly. No fabricated quotations, completed interviews or demand claims.
```

### S — Make the approved study operational, then administer actual sessions

```text
Read canonical P-TER-01 v0.3 and the actual signed approval/version I provide. Resolve differences prospectively; never infer approval from a passing build or a passing browser check. Preserve the attendance task, three separate 0/1/2 criteria, four M/four F distinct responses per teacher, frozen drafts, independent references/adjudication, counterbalancing, clocks, receipts and missing-data rules. Do not relabel the four-criterion Rivergate demo. Complete consent/storage/access/deletion/withdrawal/budget fields and all independent material approvals before study invitations. Build only a bounded controlled offline/replay route and append-only measurement forms needed for that exact approved packet. Use synthetic mechanical preflight events in a separate namespace; no fake participant rows. Independently verify original/final artifacts, terminal receipts, recovery/reload, duplicate decisions, full workload clocks, invalid evidence, unknown versions, access and human control. Once gates and real consents exist, schedule 3–5 actual adults, fixed N before invitations, administer without answer coaching, retain all attempts and record full setup/training/edit/wait/recovery and actual costs. Report descriptive quality/adjudication and per-teacher full workload, adverse/missing results and limits. Do not add competitor/live conditions or claim general savings/market validation.
```

### C — Finalize the separate substitute protocol before comparison

```text
Use actual discovery evidence to select the strongest current substitute; Brisk is provisional, not automatically the winner. Turn CMP-ELA-01 draft 0.1 in the execution desk into a separately reviewed prospective protocol. Keep the base P-TER-01 packet, cohort, materials and analysis unchanged. Use a new cohort and fresh independently matched forms, record product/plan/version/date/settings/prompts/retries and price, equalize final-output requirements and training opportunity, blind independent quality adjudication where feasible, and count complete workload and actual costs. Explicitly distinguish live generation from frozen fixture review. Freeze eligibility, assignment, outcomes, decision rules and data handling before collection. Return a reviewable amendment with unresolved fields; do not manufacture approval or comparative results.
```

### P — Seek paid continuation only after operation

```text
Check operational acceptance and the completed-study/debrief boundary before a commercial approach. Identify the actual payer and purchasing authority from interviews; keep school and personal purchase separate. Prepare a concrete 30-day one-time continuation offer using my approved price/scope/dates/refund/access terms, with no automatic renewal or unverified capability promise. Ask only the resolved authorized recipient after the offer is approved. Record stated interest, offer, acceptance, payment pending, actual settlement/receipt, refunds, delivery/use and renewal as separate events. Do not charge, enable billing, send an invoice or count revenue without the required authorization/evidence. Produce counts and actual receipts, never turn hypothetical willingness into a sale.
```

## Inputs required to continue

The demo blocker is cleared. Three inputs remain, all of them yours:

1. **Demo audience.** Public URL for adult testers, or named access with confirmed addresses. The Sites preview remains owner-private. **You do not need to resolve this to start testing** — the verified offline ZIP works now and needs no sign-in.
2. **The seven intended interview contacts**, or confirmation/replacements for the six-person shortlist plus a second current literacy coach. Resolve the differing address formats before sending.
3. **The actual approved P-TER-01 version/approval record**, qualified independent reference reviewers and adjudicator, and completed storage/access/withdrawal/deletion/budget fields. If no approved packet exists, obtain those reviews rather than calling v0.3 approved.

## Highest-leverage next action

Interviews are now the constraint. The demo is testable, and every other track waits on evidence that only real conversations produce. Nothing further should be built until a teacher has described a real recent feedback task.

**Action** → Confirm or replace the seven interview contacts and their working email addresses.
**Where** → Your own contacts, then the existing unaddressed Gmail draft `r-2693725268775707139`.
**Produce** → Seven named people with confirmed addresses, each marked teacher or coach.
**Definition of done** → The draft is addressed and sent to confirmed recipients, with zero guessed aliases, and a dated register row exists per recipient showing invitation sent and no response yet.

The narrow next product question is whether teachers experience a specific advantage over the workflow they already use. The browser pass closes a verification gap; it is not evidence that anyone wants this. No additional AEOS module is justified by this preparation alone.
