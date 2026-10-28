# Systems and cost engineering

> Unit economics, scope, architecture and evaluability, judged the way an infrastructure engineer judges them.

**Provenance.** Produced by an independent expert lens in a nine-lens audit of
`MindUnlock_Academy.jsx` (859 lines). The lens read the source in full and used live web search
to check statutes, regulations, effect sizes and product facts.
>
> **Verification status: adversarial verification was still running when this document was written. Findings are single-source and have **not** been independently checked. See `90-verification.md` once it lands.**
>
> Evidence tiers on each finding are the lens's own: `ESTABLISHED` (replicated meta-analytic
> evidence or primary legal text), `EMERGING`, `EXPERT-OPINION`, `INFERENCE` (the lens's
> reasoning), `SPECULATION`. Items the lens could not verify are marked UNVERIFIED in the
> evidence field — **those are leads to check, not facts**. Nothing here is legal advice.

---

## Executive summary

The single most important finding: **at the design described, gross margin on the $399/yr family plan is approximately zero before a dollar of infrastructure, content, or support — and the document contains no cost model at all.**

Modelling the artifact's own design (8 LangGraph agents with persistent memory, 5-agent daily chain, tutor chat, note feedback, anxiety coach, per-student ancestor generation, parent coach) yields roughly **262K input / 9K output tokens per family per day**, ~6.8M input tokens/month. At current frontier pricing (Claude Opus 5.5, $4/$20 per MTok, cached 2026-10-06) that is **$32.15/family/month against $33.25 of gross revenue**. A mid-tier model (Sonnet 5.5, $2/$10) lands at $16.09 — 48% of revenue. The design sits *exactly* on the break-even line, with no headroom: one engaged student doing 30 tutor turns instead of 12 is immediately loss-making. Separately, the stated production stack (ECS Fargate multi-AZ, RDS Multi-AZ, ElastiCache, CloudFront, Pinecone, NAT GW, a second Supabase project) runs ~$520/month fixed — $1.04/family at the Year-1 target of 500 families, but **$52/family during the 10-family pilot that the roadmap says lasts eight months.**

A re-architected version — deterministic core for everything deterministic, three narrow model call types instead of eight agents, prompt caching, Haiku-default routing with graded escalation, precomputed human-reviewed cultural content, batch for anything non-interactive — costs **~$1.80/family/month, an ~18x reduction**, and is also faster, testable, and operable by one person.

Three things make the current design unshippable regardless of cost. (1) **Scope**: ~45 engineering-months plus ≥25 person-months of content, against one founder with a full-time MCPS job, in 12 months — over-scoped 6-8x. (2) **Evaluability**: eight chained stochastic agents cannot be regression-tested, and the only stated quality control, "confidence scoring... human review if score < 0.85," is not a mechanism — LLMs do not emit calibrated confidence. (3) **Factual**: "Anki SM-18" is a category error (SM-18 is SuperMemo's proprietary algorithm; Anki uses SM-2/FSRS), and "AnkiConnect sync" is a desktop-only loopback add-on that cannot do what a mobile product implies.

The strongest asset is unused: AEOS already has a committed, mutation-tested, FORCE-RLS multi-tenant model over exactly the right entities (students, assessments, ai_recommendations, intervention_plans, audit_logs). Build MindUnlock as an AEOS module, not a parallel stack.

---

## Findings

### F01 — No cost model exists, and the design's unit economics are negative at the stated price point

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Business tab: 'Family Subscription — $49/mo | $399/yr ... Goal: 500 families Year 1'; Tech Stack: 'Claude 3.5 Sonnet / DeepSeek-V3 ... Primary: Claude'; AI Agents tab: 8 agents each with persistent 'Memory:' and chained workflows ('Daily Study Session: BARS Schedule Agent → Learning Path Agent → Tutor Agent → Cultural Identity Agent → [Test Anxiety Coach]').

**The problem**

The document costs nothing. Modelling its own design: each agent call carries ~2K system/persona + ~3K student profile + ~2K agent memory + ~2K retrieved content ≈ 9K input before the turn itself, and LangGraph chains accumulate prior agents' outputs downstream. Per family per day (ASSUMPTIONS, my estimates): daily 5-agent chain 45K in / 2.6K out; tutor chat 12 turns with full-history resend 163K in / 4.2K out; note feedback 2.6K/0.3K; anxiety coach 17K/0.5K; per-student ancestor generation 4K/0.5K; parent coach 31K/1.0K. Total ≈ 262K input / 9.1K output per family per day. Over 26 active days: 6.82M input / 237K output per month. PRICE ASSUMPTIONS (published rates, cached 2026-10-06, and prices move): Opus 5.5 $4.00/$20.00 per MTok; Sonnet 5.5 $2.00/$10.00; Haiku 5.5 $0.10/$0.50. Monthly inference per family: frontier $32.15; mid-tier $16.09; small $0.80. Gross revenue is $399/12 = $33.25/month. Frontier gross margin = $1.10 (3.3%) BEFORE infrastructure, Stripe (~$0.99/mo amortized), content, support or the founder's time — i.e. negative. Break-even on frontier is ~274K input tokens/family/day; the design is at 262K. There is no headroom: a student who does 30 tutor turns instead of 12 is loss-making on day one. Also note the artifact names 'Claude 3.5 Sonnet' as primary — a model that is several generations retired; pricing a 2026 product against it is pricing against nothing.

**Evidence**

Published model pricing as of 2026-10-06 (Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50 per MTok; cache reads $0.20 on Opus/Sonnet; Batch API 50% discount) — verified against current rate tables; mark as moving targets. Token volumes are my estimates from the artifact's own architecture, clearly labelled as assumptions.

**Recommendation**

Before writing another line of agent code, build the spreadsheet: tokens per surface per user per day x price per tier = COGS/family/month. Set a hard ceiling of $3.00/family/month (9% of gross) and enforce it in code with a per-family meter and circuit breaker. Then re-architect to hit it (see Addition A2/A5): prompt caching on the static prefix, Haiku-default with graded escalation, precomputed cultural content, batch for non-interactive work, rolling-window chat context instead of full-history resend. Target: ~$1.80/family/month, ~5.4% of revenue — an ~18x reduction, with real numbers shown in Addition A5.

### F02 — Scope is over-committed by roughly 6-8x on engineering alone, before any content

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> Roadmap: 4 phases, Months 1-12, culminating in '500 family subscriptions, 15 schools licensed, 2 grants submitted, Spanish beta: 50 families'. Inventory across tabs: 9 app surfaces, 8 agents, 4 certification tracks, 3 diagnostic instruments (52+38+24 = 114 domains), 6 note-taking methods, SRS engine, IEP parser, BARS scheduler, 100+ ancestor profiles across 40+ cultures, Google Classroom + Canvas LMS sync, district dashboard, Spanish version, GED-to-PhD 8-level pathway.

**The problem**

My engineering estimate for 'working, tested, accessible, FERPA-safe' (not demo) for one competent full-stack engineer: auth/tenancy/COPPA consent 2.5; student diagnostic + wizard + audio-assisted mode 2.0; parent+staff instruments 1.0; BARS scheduler 3.0; SRS engine 2.0; Study Lab 2.5; Anxiety Toolkit 2.0; 4 certification tracks incl. adaptive exam engine, 500-item bank tooling, video upload + rubric scoring, certificate gen 5.0; ancestor library software 1.0; Family Hub + moderated discussion 2.5; AI tutor + agents + eval + safety 4.0; IEP parser + accommodation engine + monthly reports 2.5; LMS integration (OAuth, roster sync, LTI) 3.0; district dashboard 2.0; mobile offline-first + two app stores + EAS/OTA 4.0; Spanish (audio + cultural content + Spanish-language safety classification, not just strings) 1.5; GED-to-PhD 2.0; infra/CI/observability/pen-test remediation 3.0. Subtotal ~45.5 engineering-months. Non-engineering, also on the founder: 240+ instructional hours of curriculum across four tracks (at even a conservative 10:1 development-to-finished-hour ratio that is ~15 person-months; industry rules of thumb for interactive e-learning run far higher), 100+ scholar-reviewed ancestor profiles ~4, a 500-item psychometric bank with validity evidence ~6, plus instrument validation with a licensed school psychologist. The artifact budgets that last item as 'Week 1-2'; real instrument validation (content validity, pilot, item analysis, reliability) is 9-18 months and is typically a dissertation. The founder has a full-time MCPS job and is also building AEOS.

**Evidence**

Estimates are mine (INFERENCE), calibrated to shipped-and-tested rather than demo. The e-learning development-ratio range is an industry rule of thumb (EXPERT-OPINION) — I have not verified a specific published figure and would check the Chapman Alliance surveys before quoting a number.

**Recommendation**

Collapse to one surface. Build the pre-test anxiety protocol with pre/post measurement, as a PWA, for 10 families, in 8 weeks — it is the artifact's own core thesis, needs 3 modules of content rather than 240 hours, can be measured in 8 weeks, and if the effect is absent nothing else in the product matters. Then, in order with explicit kill criteria: (2) deterministic BARS scheduler, no AI, 6 wks — kill if median weekly active days < 3 by week 4; (3) spaced repetition, 4 wks — kill if <40% of students reach a 5-day review streak by week 3; (4) tutor chat, 6 wks — kill if COGS/family/month > $3 or the eval gate cannot be held green; (5) parent coaching, 6 wks — kill if <30% of parents complete module 3. Certification, LMS, district dashboard, Spanish and GED-to-PhD do not start until there are 100 paying families. For the anxiety protocol itself, the gate at n=10 is engagement and direction, honestly stated — not a significance claim: kill if <60% complete 6 of 8 pre-test protocols.

### F03 — A parallel stack re-implements, unproven, the exact multi-tenant security model AEOS has already proved — for FERPA records and IEP contents

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Tech Stack tab proposes React Native/Expo, Pinecone, Redis (Upstash), Celery, AWS ECS Fargate, RDS Multi-AZ, ElastiCache, CloudFront, and a 'Supabase cloud (separate project)'. The founder's own stated principle is 'shared AEOS infrastructure over per-module duplication' and 'security over feature velocity'.

**The problem**

AEOS already contains, committed: backend/supabase/migrations/001_initial_schema.sql with organizations, schools, users, students, assessments, ai_recommendations, intervention_plans, intervention_actions, progress_events, audit_logs; 002_tenant_rls.sql with ENABLE plus FORCE ROW LEVEL SECURITY on all ten tables and per-operation policies; 003_fk_relationship_hardening.sql and 004_org_lifecycle_and_write_authority.sql; backend/app/services/tenant_scope.py, backend/app/core/auth.py and dependencies.py; and backend/tests/ containing test_rls_enforcement.py, test_fk_relationship_rls.py, test_authorization.py, test_route_authentication.py, test_security_artifacts.py and security_mutations.py — a mutation suite that proves the policies fail closed. The frontend is Next.js 16 / React 18 / TypeScript with @supabase/ssr. The MindUnlock entity model maps onto this almost one-to-one. A second Supabase project means a second RLS model, a second auth config, a second migration history and a second security test suite — and the proven security properties do not transfer. You would be shipping children's education records plus IEP contents (disability status, arguably the most sensitive category of student record) on an unproven tenancy model while a proven one sits in the same repository. Against the founder's own stated principle this is a direct contradiction, not a preference.

**Evidence**

Direct inspection of /home/user/AEOS: migrations 001-004, backend/app/services/tenant_scope.py, backend/app/core/auth.py, and the eleven files under backend/tests/ including security_mutations.py. frontend/package.json pins next ^16.3.4, react ^18.2.0, @supabase/ssr ^0.12.4.

**Recommendation**

Build MindUnlock as an AEOS module on the existing stack. Reuse unchanged: organizations/schools tenancy, FORCE RLS, tenant_scope.py, core/auth.py, dependencies.py, audit_logs, the assessments + assessment_service.py + assessment_result_service.py pipeline for all three diagnostic instruments, ai_recommendations for model outputs, intervention_plans/intervention_actions for BARS blocks and anxiety protocols, progress_events for streaks and reviews. Extend security_mutations.py to every new table — that file is the most valuable artifact in the repo and must not be rebuilt from scratch. Genuinely new code: the deterministic core, the LLM gateway + eval harness, the content corpus and its review workflow, the PWA client, COPPA verifiable parental consent, and the crisis-escalation workflow. Replace Pinecone with pgvector in the existing Postgres (the corpus is tens of thousands of vectors, not millions); replace Redis/ElastiCache with Postgres plus the provider's own prompt cache; replace Celery with one worker (arq, or a Supabase scheduled function); replace ECS/RDS Multi-AZ/CloudFront with Vercel (already the AEOS deploy path — AEOS_Vercel_Deploy.sh is in the repo) plus one container plus managed Supabase Postgres.

### F04 — Eight chained stochastic agents cannot be regression-tested, and the chain contradicts the document's own latency KPI

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> AI Agents tab: five named LangGraph workflows, e.g. 'Daily Study Session: BARS Schedule Agent → Learning Path Agent → Tutor Agent → Cultural Identity Agent → [Test Anxiety Coach if flagged]' and 'Pre-Test 24 Hours: BARS Schedule Agent (clear blocks) → Learning Path (priority review) → Tutor (gaps) → Test Anxiety Coach (protocol) → Parent Coach (morning ritual)'. Roadmap Phase 2 KPI: 'Agent response time < 2 seconds'.

**The problem**

Two independent failures. (a) Testability: if each agent has ~8 meaningfully different output modes, a 5-agent chain has ~32,768 reachable states. You cannot enumerate them, cannot diff them across a prompt change, and cannot attribute a bad answer to a stage. You will ship prompt changes blind. (b) Latency: at a realistic p95 of 2.5-4s per model call, a 5-call sequential chain has a p95 of 12-20s, against the document's own '<2s' KPI stated in the same artifact. The architecture and the KPI contradict each other. Worse, the Onboarding chain fires five agents at registration — before the system knows anything about the user — producing a ~20s wait and a ~400K-token bill at the point of highest abandonment risk. Separately, eight independent 'Memory:' stores (each agent card lists its own) will diverge within a week, and no conflict-resolution rule is stated for when the Diagnostic Agent's 'learning profile' disagrees with the Learning Path Agent's 'mastery levels'.

**Evidence**

Combinatorial argument is deterministic. Latency figures are my estimates (INFERENCE) from typical p95s for a ~9K-token prompt with thinking enabled. The KPI contradiction is internal to the artifact and verifiable by reading two tabs.

**Recommendation**

Replace eight stateful agents with a deterministic state machine plus THREE narrow model call types, each with a fixed input schema, fixed output schema, and a golden fixture set: explain(concept, level, profile); socratic_turn(history, goal); critique_notes(text, rubric). Plus, off the request path: extract_iep(pdf) in batch with human confirmation, and a cheap always-on safety classifier. Everything else becomes code: scheduling (constraint solve, ~400 lines, deterministic and offline-capable), spacing intervals (pure math), diagnostic scoring (a scoring key and norm table — a 'psychometric engine' is arithmetic, not an LLM), accommodation mapping (a reviewed lookup table; a model mapping IEP accommodations is a compliance incident waiting to happen, because an IEP is a legal document under IDEA), routing (a decision table), escalation thresholds (numeric comparison with hysteresis), Eisenhower prioritisation (a sort), streaks and progress (SQL). One state object, one writer. The argument is not primarily about tokens — the chain is expensive because it is untestable, and untestable software operated by one person at 3am is a liability.

### F05 — 'Confidence scoring on ALL outputs; human review if score < 0.85' is not a mechanism, and there is no eval harness anywhere in the document

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.92 |

**What the artifact says**
> Appears twice and is load-bearing in both: Project Doc risk card ('AI hallucination in educational content — Confidence scoring on ALL outputs; human expert review queue for score < 0.85; citations required') and AI Agents Failure Handling card (identical wording).

**The problem**

LLMs do not emit calibrated confidence. A self-reported 0.85 is a token the model generated, not a measurement, and it correlates poorly with correctness. The entire hallucination mitigation for an educational product serving children rests on a number with no meaning. Beyond that, the artifact has no fixture corpus, no rubric, no automated graders, no offline/online metric split, no labelling plan, no release gate, and no regression test for AI behaviour. The only stated quality signal in the whole roadmap is 'Agent response time < 2 seconds'.

**Evidence**

That LLM self-reported confidence scores are not calibrated probabilities is well established in the calibration literature; the specific framing here (a scalar emitted alongside the answer) has no measurement semantics at all.

**Recommendation**

Build the minimum viable eval system in ~2 weeks before the pilot (full spec in Addition A4). Fixture corpus: 120 tutor openers (incl. 15 adversarial answer-extraction attempts), 60 note-feedback samples across the 6 methods incl. blank/one-word/copied-textbook edge cases, 80 safety probes (20 explicit, 20 ambiguous, 20 third-party, 20 NEGATIVES that must not fire), 40 IEP extraction fixtures with hand-labelled gold accommodation sets, 30 diagnostic gaming patterns. Rubrics written down BEFORE looking at outputs. Graders: deterministic first (length, readability, answer-giving regex, PII scan, forbidden-claim scan), LLM-judge second on a stronger pinned model with frozen versioned prompts — and CALIBRATE the judge against 60 human-scored fixtures, reporting Cohen's kappa; if kappa < 0.6 the judge is not an instrument. That calibration step is what the 0.85 score is pretending to be. Release gate blocks deploy on: safety recall >= 0.95 AND false-positive rate <= 0.05 (both, no override), tutor rubric mean >= 4.0/5 with no fixture below 2, zero PII leaks, zero forbidden-claim hits, p95 latency in budget, and cost-per-fixture-run within 10% of last release (this catches silent prompt bloat). Human spot-check: 20 live transcripts/week, stratified (10 random, 5 lowest-judge, 5 safety-flagged), 30 min/week, scheduled not aspirational — it is the only part of the system that finds failure modes you did not imagine.

### F06 — 'Anki SM-18' is a category error and 'AnkiConnect sync' cannot do what the mobile product implies — the feature cannot ship as written

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.95 |

**What the artifact says**
> Four places: Project Doc ('Spaced repetition Anki engine (SM-18)'); Top-10 action #7 ('Integrate Anki SM-18 spaced repetition engine'); Gap Analysis app table ('Anki ... Best-in-class SM-18 algorithm'); Tech Stack ('SM-18 Algorithm | Spaced Repetition | Anki-compatible; AnkiConnect sync; neurodivergent-adjusted ease factors'); Roadmap Phase 2 milestone ('Anki SM-18 integration + AnkiConnect sync') and KPI ('Anki daily use in 80%+ of pilot families').

**The problem**

Three distinct factual errors. (1) SM-18 is SuperMemo's algorithm, used in SuperMemo 18 for Windows — not Anki's. SuperMemo states the algorithm will not be open source because core equations are a trade secret, and that it withdrew from licensing the commercial algorithm versions. You cannot implement SM-18. SM-19 and SM-20 are the later versions. (2) Anki historically used SM-2 (publicly available, implementable with attribution); its modern scheduler is FSRS (Free Spaced Repetition Scheduler), open source, integrated into Anki — third-party sources report it became the default in Anki 23.10 (2023-10-31). Note: I could not fetch Anki's own FAQ in this session (docs.ankiweb.net did not resolve under the session's network allowlist), so treat the 'default since 23.10' detail as third-party-reported and verify. (3) AnkiConnect is a DESKTOP add-on: it starts an HTTP server on 127.0.0.1:8765 inside Anki Desktop, bound to loopback, and Anki Desktop must be kept running for anything to reach it. It is not available on AnkiMobile; on Android only an unofficial from-scratch reimplementation exists. For a product whose users are middle schoolers on phones, there is no desktop Anki in the loop — 'AnkiConnect sync' as a mobile feature cannot work. What the artifact likely means (cards appearing in the student's own Anki) would require AnkiWeb sync, which has no public API, or one-way .apkg export with no review-state sync back.

**Evidence**

SuperMemo's official position that the algorithm will not be open source and that it withdrew from commercial-version licensing (supermemo.com blog / SuperMemopedia Algorithm FAQ); Algorithm SM-18 'currently in use only in SuperMemo 18 for Windows' (supermemo.guru). AnkiConnect's own documentation: 'this plugin will initialize a minimal HTTP server running on port 8765 every time Anki executes', bound to 127.0.0.1, with Anki required to be running (AnkiWeb addon 2055492159 / foosoft anki-connect). AnkiconnectAndroid describes itself as an unofficial from-scratch reimplementation. FSRS open-source status and Anki integration: open-spaced-repetition/fsrs4anki.

**Recommendation**

Delete every reference to SM-18 and to AnkiConnect. Adopt FSRS and say so. Do not write the algorithm — use a reference implementation (py-fsrs / fsrs-rs / ts-fsrs, permissively licensed). Your ~200 lines are the WRAPPER, not the algorithm: per-card state (stability, difficulty, last_review, due, reps, lapses); grade ingestion (again/hard/good/easy); due-queue assembly; +/-5% interval fuzz to prevent review pile-ups; a daily review cap and due-load smoother; timezone-correct day boundaries (the single most common bug in every SRS implementation); and offline reconciliation via an APPEND-ONLY review log that is replayed server-side — last-write-wins on review events silently loses reviews. Parameter fitting is a nightly batch job per user with enough review history, not an online computation. If you want a student's cards in their own Anki, ship .apkg export and be explicit that it is one-way.

### F07 — The crisis-escalation path terminates in a notification to nobody, and '<500ms crisis detection' conflates two different systems

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.87 |

**What the artifact says**
> Project Doc risk card: 'Crisis detection layer; automatic counselor + parent notification; hotline display; AI conversation paused immediately'. App Design IEP workflow step 5: 'Anxiety markers exceed threshold → counselor alert + parent notification + crisis resources displayed'. Tech Stack security card: 'AI Safety Layer: Content safety classifier on ALL AI outputs; PII detection pipeline; crisis escalation detection with latency < 500ms'.

**The problem**

Two problems. (a) There is no named human. An escalation that terminates in 'counselor alert' names no person, no channel, no agreed response window, and no fallback — and it may fire at 11pm on a Saturday to a school counselor who never agreed to receive it. That is not a safety system; it is a notification into a void, and it creates liability precisely because the product promised a response. (b) '<500ms' is attached to 'content safety classifier on ALL AI outputs'. If detection means screening model OUTPUT, you cannot be under 500ms end-to-end including the generation you are screening. If it means screening the student's INPUT the moment it is sent, 500ms is achievable with a small classifier running in parallel with generation. These are different systems with different guarantees, and the document conflates them. Input-side screening is also the correct design, because you want to intercept before the tutor responds at all. Additionally, the stated safety evaluation has no false-positive consideration: a crisis classifier with a 20% FPR will alert parents and counselors dozens of times a week, the school will turn it off, and then it protects no one.

**Evidence**

Latency argument is arithmetic (you cannot screen output in less time than it takes to produce it). The false-positive failure mode is a standard property of alerting systems. The absence of a named escalation recipient is verifiable by reading the three cards.

**Recommendation**

Make the crisis path a written runbook with a named person, an agreed channel, an agreed response window, documented hours, and a documented out-of-hours fallback (988 Suicide & Crisis Lifeline and the local crisis line, displayed in-app). Get the school counselor's and the parent's written agreement to the channel and window BEFORE the pilot enrolls anyone. Split the two latency claims honestly: input-side classification of every student message, p95 <= 400ms, running in parallel, fail-CLOSED (if the classifier errors, no tutor response is shown); output screening is a separate, slower, post-generation check. Make '100% of student messages classified before a tutor response is shown' a correctness SLO, not a latency one. Measure recall AND false-positive rate on the 80-probe set from F05, with 20 of those probes being normal test-anxiety distress language that must NOT fire — and gate releases on both numbers.

### F08 — Routing student records and IEP contents to a PRC-jurisdiction API provider is a procurement non-starter for a public school district

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.84 |

**What the artifact says**
> Tech Stack: 'Claude 3.5 Sonnet / DeepSeek-V3 | LLM Layer | Primary: Claude (safety, nuance, education); Cost layer: DeepSeek; Fallback: GPT-4o'. Top-10 action #2 and #6 also assign schema and agent code generation to a 'DeepSeek Code Agent'.

**The problem**

Using DeepSeek for code generation on the founder's own machine is a different question from routing production inference. The 'cost layer' as described sends student free text — which will include self-harm disclosures, IEP accommodation details and disability status — to a provider under PRC jurisdiction. Independent of any geopolitical judgement, this is caught in the first data-processing-agreement review by any US public school district, and MCPS is the named target customer. The cost saving does not exist either: DeepSeek flash is reported at roughly $0.15/$0.60 per MTok off-peak, versus Haiku 5.5 at $0.10/$0.50 — a US-hosted small model is already cheaper at the volumes here, before counting the second vendor, second DPA, and second failure mode.

**Evidence**

DeepSeek pricing figures are third-party-reported (mid-October 2026 trackers: flash $0.15/$0.60 off-peak, doubling at peak; peak windows 01:00-04:00 and 06:00-10:00 UTC weekdays) and I could not retrieve the official rate table — treat as unverified. Haiku 5.5 at $0.10/$0.50 is from the published Anthropic rate table (cached 2026-10-06). The DPA/procurement consequence is INFERENCE from how district vendor reviews work, not from a cited policy.

**Recommendation**

Remove DeepSeek (and any non-US-hosted provider) from the production inference path entirely. Keep it, if you like, as a local coding assistant on the founder's machine where no student data is involved — but say so explicitly in the document, because as written a district reviewer will read 'DeepSeek | LLM Layer' and stop reading. Use Haiku-tier for the cost layer: cheaper, US-hosted, one vendor, one DPA, one set of zero-retention settings to assert. Add a startup check that fails the deploy if the provider's no-training / zero-data-retention setting is not enabled.

### F09 — 'Offline-first' and 'eight server-side agents' and '<2s agent response' and 'real-time WebSockets' are mutually incompatible

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Tech Stack frontend: 'React Native (Expo SDK 51) | iOS + Android; offline-first (Expo SQLite)'; 'Zustand + TanStack Query | Offline sync; optimistic updates; real-time agent WebSocket; background sync'. Alongside the 8 server-side agents and the Phase 2 KPI 'Agent response time < 2 seconds'.

**The problem**

An offline-first app cannot run server-side agents. The document never states which features survive loss of connectivity, which is the most important design decision in a product for families on constrained data plans. A persistent WebSocket on a metered phone belonging to a child who closes the app is a battery and data tax with no payoff — nothing in this product is multiplayer or collaborative. And the 5-agent chain cannot meet <2s (F04).

**Evidence**

Architectural; verifiable by reading the Tech Stack and AI Agents tabs together.

**Recommendation**

Draw the line explicitly. MUST run on-device: schedule rendering, SRS scheduling and review, note capture, timers, breathing and somatic exercises, streaks, all module text and audio. A student must be able to complete a full study session on an airplane. MUST be precomputed overnight by one cron job writing a per-family JSON blob: tomorrow's block plan, tomorrow's due queue, the ancestor card, the parent digest, the next module. This single decision is the highest-leverage move for both cost and latency. CANNOT work offline, and must degrade gracefully with an honest message: tutor chat, note AI feedback. Drop WebSockets; use HTTP with polling for the little that is live. Honest p95 latency budget: app open to today's plan 300ms (local); card flip 50ms; exercise start 100ms; ancestor card 100ms; safety classification 400ms; tutor FIRST TOKEN 1.2s streamed (so perceived latency is 1.2s, not 4s for the full turn); note feedback 8s and explicitly async ('we'll have this in a minute'); IEP parse: minutes, batch, never blocking; monthly report: overnight. Set and test hard device budgets: initial payload <= 500KB gzipped, daily sync <= 200KB, audio 32kbps mono opus downloaded on wifi, images AVIF/WebP <= 40KB, works on a 2019 Android Go device with Data Saver on. Buy a $120 Android phone and make it the acceptance device — the artifact discusses 'sensory-aware palette' and 'ADHD-friendly tokens' but never a device or data budget, which is the accessibility constraint most likely to exclude the target families.

### F10 — A 99.9% SLA commits a solo founder to 43.2 minutes of downtime per month and should not be promised in year one

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.91 |

**What the artifact says**
> Tech Stack deployment card, Production: 'Blue/green deployment; 99.9% SLA target; multi-region failover (us-east-1 primary → us-west-2 DR)'. Plus 'Quarterly external pen test; bug bounty program' in the security card.

**The problem**

99.9% is 43.2 minutes of downtime per month, 8.76 hours per year. Honouring it requires 24/7 paging, a second responder (you cannot be sole on-call and also sleep, teach, and have a family), multi-AZ with TESTED failover, a tested restore, and change control. A solo founder with a full-time MCPS job commits to none of these. Putting 99.9% into a district contract creates a written obligation you will breach, to your most important customer. Multi-region failover for 500 families additionally introduces split-brain — a failure mode strictly harder to debug than the outage it is meant to prevent. A quarterly external pen test plus a bug bounty is typically $15-40K/yr (my estimate), which alone is a material fraction of the stated $175K total operating cost.

**Evidence**

99.9% = 43.2 min/month is arithmetic (0.001 x 30 x 24 x 60). Pen-test cost is my estimate (INFERENCE), not a verified quote.

**Recommendation**

Promise no SLA in year one. Publish a status page and a support commitment instead: business-hours support, next-business-day response, planned maintenance announced 48h ahead, and we will tell you when we are down. A district will accept that from a pilot vendor. Internally run four SLOs, not forty: (1) API availability >= 99.0% monthly, unpublished, 7.2 hrs/mo budget; (2) tutor first-token p95 <= 2.5s; (3) 100% of student messages safety-classified before a tutor response is shown — a correctness SLO, fail-closed; (4) inference COGS per family per month p95 <= $3.00. Exactly THREE things page the founder's phone: API 5xx > 5% for 5 min; safety classifier erroring; any org's daily spend > 3x its 7-day median. Everything else is a daily digest. Page on more than three things and you will mute the pager, and then you have no pager. Design so 3am never requires action: one stateless container the platform restarts; managed Postgres with PITR (restore at 9am from a backup you have actually tested, never at 3am); a feature-flag kill switch on every model-calling path so the 3am action is 'turn off the tutor' from a phone and the app falls back to its offline mode; a hard per-family and per-org spend cap in the gateway, because the realistic 3am incident is a runaway token loop, not a crash; idempotent jobs so a failed nightly run is fixed by re-running it.

### F11 — The production infrastructure costs ~$52/family/month during the 10-family pilot the roadmap says lasts eight months

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.78 |

**What the artifact says**
> Tech Stack Production: 'AWS ECS Fargate (auto-scaling); CloudFront CDN; RDS PostgreSQL Multi-AZ; ElastiCache Redis cluster; S3 media' plus Pinecone, Upstash Redis and 'Supabase cloud (separate project)' from staging. Roadmap: pilot is 10 families from Phase 1 (Months 1-3) through Phase 3; 500 families only in Phase 4 (Months 10-12).

**The problem**

My estimate of the stated stack's fixed monthly cost (ASSUMPTION, US-East list prices from memory, unverified): ECS Fargate 2 tasks 1vCPU/2GB 24/7 ~$70; RDS Multi-AZ db.t4g.medium ~$160 (Multi-AZ doubles the instance cost); ElastiCache 2 x cache.t4g.small ~$50; CloudFront + S3 ~$30; Pinecone ~$70; NAT Gateway ~$35 plus data (the classic silent line item); second Supabase Pro project $25; Sentry/EAS/monitoring ~$80. Total ~$520/month fixed. At the Year-1 target of 500 families that is $1.04/family — negligible. At 10 pilot families it is $52/family/month, or $6,240/year against $3,990 of pilot revenue that is probably waived anyway. The architecture is provisioned for a scale the roadmap says will not exist for ten months, and the pilot — the only phase that produces evidence — pays for it.

**Evidence**

Line-item costs are my estimates (INFERENCE) from AWS/vendor list pricing; I have not verified current rates and the user should price this in the AWS calculator before committing. The 10-families-for-8-months timeline is read directly from the Roadmap tab.

**Recommendation**

Provision for the scale you have, not the scale on the slide. Pilot stack: Vercel for the PWA (already the AEOS deploy path, AEOS_Vercel_Deploy.sh is in the repo), one container on Fly/Railway/Render (~$25), the EXISTING AEOS Supabase project with pgvector (no second project, no Pinecone), Sentry free tier. ~$70/month total, ~$7/family at pilot scale. Revisit multi-AZ when a district contract requires it in writing and pays for it. Write the trigger down: 'we move to Multi-AZ when (a) a signed contract requires >99% availability, or (b) sustained load exceeds X req/s' — so the decision is made by a condition, not by anxiety.

### F12 — The Year-1 financial projection counts restricted grant money as profit and omits the costs its own risk register promises

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.83 |

**What the artifact says**
> Business tab: 'Total Year 1 Revenue $391,850 | Operating Costs (tech + staff + marketing) ~$175,000 | Net Year 1 ~$216,850', built from 500 x $399 + 5 x $7,500 + 100 x $299 + 50 x $499 + $100,000 grants.

**The problem**

Four issues. (1) $100,000 of the $391,850 is federal grant funding — restricted, typically reimbursement-based, and not distributable profit; treating it as net income is a category error. (2) $175,000 of operating cost does not cover what the document elsewhere commits to: inference (F01: $32/family/month x 500 x 12 = $192,000 at frontier, or $16,000 at the re-architected rate), 'African-centered scholars as PAID co-developers' with a community advisory board, a licensed school psychologist for instrument validation, a psychometrician for the 500-item bank, 'legal counsel from Day 1' on a FERPA/COPPA product ($20-50K, my estimate), quarterly external pen testing plus a bug bounty ($15-40K, my estimate), content development for 240+ instructional hours, or any founder salary. The risk-mitigation column alone plausibly exceeds the entire stated operating budget. (3) $399/yr collected upfront is deferred revenue; families enrolling in Phase 4 (Months 10-12) contribute 2-3 months of recognised revenue in Year 1, not $399 each. (4) The projection has no churn assumption, no CAC, and the Phase 4 plan is 'Paid marketing campaign for family subscriptions' with no budget line.

**Evidence**

The arithmetic and the missing line items are verifiable against the artifact's own Risks and Tech Stack tabs. Dollar estimates for legal and pen testing are mine (INFERENCE), unverified.

**Recommendation**

Rebuild the model with: grants on a separate restricted line, excluded from net; inference COGS as a per-family variable cost driven by the F01 model; every risk-mitigation commitment as a budget line with a number; revenue recognised monthly from the enrollment cohort curve rather than counted at signup; an explicit churn assumption and CAC; and a founder salary (even $0, stated, so the reader knows). Then state the actual runway question honestly: at 500 families and the re-architected COGS, contribution margin per family is roughly $33.25 - $1.80 inference - $0.99 payments - ~$1.04 infra = ~$29.42/month, which funds content and support but not a salary until volume is much higher. That is a defensible number. $216,850 net is not.

### F13 — There is no stated prohibition on training models on student data — and the deletion right the product promises makes training irreversible-by-design a company-ending risk

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.86 |

**What the artifact says**
> Tech Stack security card promises 'COPPA (Under 13): Verifiable parental consent; zero behavioral advertising; full data deletion on demand' and 'FERPA Compliance: ... data minimization; deletion rights'. Nothing anywhere in the artifact addresses model training, fine-tuning, or provider data-retention settings.

**The problem**

The document commits to full data deletion on demand while proposing an architecture whose data flows are undefined with respect to training. Four compounding issues. (a) Legal basis: a district contract would rest on FERPA's school-official / contractor exception for a legitimate educational interest; model training for the vendor's product benefit is a secondary commercial use, not a legitimate educational interest in that student's education, and district DPAs routinely prohibit it by name. I am stating the structure of the rule — the operative text lives in 34 CFR Part 99 with the school-official exception around 34 CFR 99.31(a)(1); TREAT MY SECTION CITATION AS UNVERIFIED and have counsel confirm it. Maryland also has its own student-data-privacy statute whose provisions I have not checked. (b) Irreversibility: you can return and delete a parent's rows; you cannot extract their child's text from model weights. You would be structurally unable to honour the deletion right your own COPPA flow promises. (c) Memorization: training on a few hundred students' free text — which will contain self-harm disclosures and IEP details — at low data volume makes verbatim emission a real risk, not a theoretical one. (d) It is unnecessary: everything you would want from training (profile, history, accommodations) belongs in the prompt at inference time, where it is deletable, auditable and RLS-scoped.

**Evidence**

The deletion/irreversibility argument is deterministic. The FERPA structure is INFERENCE from how the school-official exception is used in ed-tech DPAs; the specific CFR section is UNVERIFIED and must be confirmed by counsel. Memorization risk at low data volume is established in the ML privacy literature but I have not cited a specific study here.

**Recommendation**

Write the rule into both the DPA and the code, in the same words: student-generated content and PII are used only for inference, in-prompt, scoped to that student's session; never for training, fine-tuning, or eval-fixture creation without separate, specific, written, revocable consent AND de-identification. Enable zero-data-retention / no-training settings on every model provider and assert them in a startup check that FAILS THE DEPLOY if they are off — a config flag nobody checks is not a control. The eval fixture corpus uses synthetic data and consented, de-identified samples only, with a provenance field on every fixture. Relatedly: fine-tuning and distillation are not justified here anyway (you do not have the data; the quality gap is already closed more cheaply by caching + reviewed content + routing; and a fine-tuned small model must be re-tuned every time the base model moves, which a solo founder will not keep up with). Revisit at >10,000 daily active students with a stable, measured task.

### F14 — Per-student generation of identical cultural content burns ~624M tokens/year to produce one artifact — and structurally prevents the cultural review the risk register promises

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.89 |

**What the artifact says**
> AI Agents tab, Cultural Identity Agent: tools 'Ancestor library (40+ cultures, 100+ profiles); Scholar biography generator; Achievement timeline engine; Daily affirmation generator'; triggers 'Daily login (morning), pre-study session, low motivation detected, pre-test anxiety ritual'; output 'Ancestor of the day card, cultural affirmation, academic heritage story, inspirational quote'. Risk card: 'Cultural appropriation of African-centered content — African-centered scholars as PAID co-developers; community advisory board with VETO POWER; ongoing cultural review process'.

**The problem**

Two failures, one of which is not about money. (a) Cost: ~4K input tokens per student per day x 26 days x 500 families x 12 months = ~624M tokens/year to generate content that is, for the overwhelming majority of cases, identical across students. The actual corpus is a fixed set of maybe 2,000 artifacts (100 profiles x variations + a year of daily cards). Generating it ONCE costs ~6M output tokens, roughly $120 at Opus 5.5 pricing, and then $0 forever. (b) Governance, which matters more: a community advisory board cannot exercise veto power over text that does not exist until a child requests it. Per-request generation makes the artifact's own most important cultural safeguard structurally impossible to implement. The same applies to the 'CBT prompt library (200+ items)' — the document already calls it a library; a library is content, so serve it.

**Evidence**

Token arithmetic from the artifact's own agent triggers and my per-call estimate (INFERENCE). The governance point follows deterministically from the generation model.

**Recommendation**

Precompute the entire cultural corpus as reviewed content in Postgres, served from the CDN and cached on-device. Pipeline: frontier model drafts -> named scholar reviews and edits -> advisory board approves or vetoes -> row written with reviewer identity, approval date and version -> served. Every card carries its provenance, which is exactly what makes the veto real and what a district reviewer will ask to see. Same treatment for module text, the CBT prompt library, affirmations and reading-level variants of module paragraphs (precompute the variants; do not rewrite at request time). This is also the single clearest instance of the general rule: the frontier model belongs in the factory, not in the product.

### F15 — The agent_memory table is the one place a self-harm disclosure will land, and it is the one table with no tenant scoping

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Tech Stack database card, core schema: 'agent_memory (agent_id, user_id, context jsonb, ttl)'. Compare the other listed tables and compare AEOS's own migrations.

**The problem**

Every AEOS table carries organization scoping and has ENABLE + FORCE ROW LEVEL SECURITY with per-operation policies. agent_memory as sketched has agent_id and user_id only — no org column, no school column, and therefore no obvious way to write the same tenant policy. It is an untyped jsonb blob with a TTL. Given the agent cards' own memory descriptions ('anxiety history by test type, trigger patterns', 'child's struggle areas, family dynamic baseline'), this is precisely the table most likely to contain a crisis disclosure, an IEP detail, or a family's private circumstances — and it is the table with the weakest access-control story in the design. A TTL is also not a retention policy; FERPA audit retention and COPPA deletion rights both need explicit handling, and 'ttl' handles neither.

**Evidence**

Direct comparison between the artifact's schema sketch and AEOS backend/supabase/migrations/001_initial_schema.sql + 002_tenant_rls.sql, where all ten tables get ENABLE + FORCE RLS and four per-operation policies each.

**Recommendation**

Delete the table. In the re-architected design there is ONE state object per student, written by one writer, stored in the AEOS schema with the same org scoping and FORCE RLS as everything else, with explicit typed columns for the fields you actually use and a separate append-only event log for history. Conversation transcripts, if retained at all, get their own table with an explicit retention period, explicit RLS, an audit_logs entry on every read, and a documented deletion path — and the default should be to retain the minimum that the crisis-review process requires, not everything with a TTL. Extend backend/tests/security_mutations.py to cover it before it holds a single real row.

### F16 — 'Neurodivergent-adjusted ease factors' is an unvalidated knob, mismatched to the algorithm it is attached to

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `SPECULATION` |
| **Lens confidence** | 0.75 |

**What the artifact says**
> Tech Stack: 'SM-18 Algorithm | Spaced Repetition | Anki-compatible; AnkiConnect sync; neurodivergent-adjusted ease factors; IEP time scaling'. Also the schema sketch 'anki_cards (user_id, content, interval, ease_factor, due)'.

**The problem**

Two layers. (a) Terminology: 'ease factor' is an SM-2 concept. FSRS — the modern, open, evidence-backed choice — models stability and difficulty, not ease. The phrase is already mismatched to the algorithm the product should use. (b) Substance: I am aware of no replicated evidence for ADHD- or autism-specific optimal spacing parameters. The spacing effect itself is robust across populations; a population-level parameter adjustment keyed to a diagnosis is not supported, and shipping it as a feature is a claim of validation that has not occurred — which violates the founder's own stated operating principle. Worse, it is strictly inferior to what FSRS already does: FSRS fits parameters to that individual's own review log, which adapts to the person rather than to a label.

**Evidence**

FSRS models stability and difficulty rather than SM-2 ease (open-spaced-repetition/fsrs4anki). The absence of validated ND-specific spacing parameters is my assessment — I did not find supporting literature and did not exhaustively search; label this SPECULATION and treat it as a claim to retract rather than one to defend.

**Recommendation**

Ship per-user FSRS parameter fitting (nightly batch, once a user has enough review history) and remove the ND-ease claim from the document. Expose the two knobs that ARE defensible and that a student or parent can actually feel: desired retention (lower it to cut daily review load for a student who is drowning) and a hard daily review cap. Frame both as accommodations, not as algorithmic personalization. To test the underlying question honestly: log every review with grade, elapsed interval and predicted retrievability; after ~8 weeks compute per-student calibration (predicted vs. observed recall, binned); systematic overconfidence for a subgroup is evidence of mis-fit, and the fix is refitting, not a hand-set constant. The experiment that would actually answer the question is a within-subject crossover on desired retention (0.90 vs 0.85) with review burden and recall as outcomes, n in the hundreds — a year-3 research question. Say that in the document instead of asserting the feature.

### F17 — Version choices across the stack are 1-2 years stale, indicating the document was assembled from recall rather than from checking

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Tech Stack: 'React Native (Expo SDK 51)'; 'Next.js 14 (App Router)'; 'Claude 3.5 Sonnet / DeepSeek-V3'; 'FastAPI (Python 3.12) ... 10k+ req/sec capable'; 'Pydantic V2'.

**The problem**

Expo SDK 51 shipped in 2024; the current line is SDK 57 (June 30, 2026, bringing React Native 0.86), with the npm registry showing an apparently newer 58.x. A new project pinned to 51 starts roughly six SDK generations behind, which means stale React Native, missed security patches, and an upgrade path through every intermediate breaking change. Next.js 14 is proposed while AEOS's own frontend/package.json already pins next ^16.3.4 — the parallel stack is older than the stack it would sit beside. 'Claude 3.5 Sonnet' is several generations retired. The staleness pattern matters more than any individual version: it means the architecture section records what was true when the author last read about these tools, which is exactly the failure mode that produced the SM-18 error (F06). '10k+ req/sec capable' is also false precision — 500 families generate well under 1 req/s peak — and capacity boasts in a document whose real constraint is one person's calendar are noise.

**Evidence**

Expo SDK 57 released 2026-06-30 bringing React Native 0.86 (expo.dev/changelog/sdk-57; npm shows expo 58.0.19 as latest, unconfirmed against the official SDK page). AEOS frontend/package.json: next ^16.3.4, react ^18.2.0. Current Claude model line: Opus 5.5 / Sonnet 5.5 / Haiku 5.5 (rate table cached 2026-10-06).

**Recommendation**

Replace the version table with 'match AEOS' plus a dated check. Concretely: Next.js 16 (inherit from AEOS), React 18, FastAPI with the pinned versions already in backend/requirements.txt (fastapi 0.115.0, pydantic 2.8.2, supabase 2.5.0), current Claude model IDs, and no React Native at all in year one (see F18). Add a standing practice: any version number or model name in a planning document carries the date it was checked, or it is deleted. Delete the throughput claim; replace it with the actual load estimate and the actual constraint ('peak < 1 req/s at 500 families; the binding constraint is founder-hours, not CPU').

### F18 — A native mobile app costs ~4 engineering months and two store review processes for capability a PWA already provides

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.76 |

**What the artifact says**
> Top-10 action #4: 'Build BARS Mission Schedule Builder MVP in React Native (Expo) — iOS + Android'. Roadmap Phase 1 KPI: 'App store submission (iOS + Android)'. Tech Stack: 'Expo EAS Build | CI/CD Mobile | Staged rollouts; TestFlight + Google Play Internal; OTA patch capability'.

**The problem**

Nothing in the artifact's feature list requires native. The usual argument is push notifications ('Daily ancestor quote push notification'), but web push works on Android Chrome and, for installed PWAs, on iOS 16.4+ — which covers the daily card and the review reminder. Offline works (service worker + IndexedDB). Camera for note photos works (input capture). TTS works (speechSynthesis, free). What native costs: ~4 engineering months, two store review processes, two release channels, EAS spend, two crash-reporting runtimes, and — specifically for a product serving under-13s — the app stores' kids-category review, which is slow and strict. What it buys: App Store presence, which is a marketing channel, and a school-distributed product does not acquire through the App Store.

**Evidence**

PWA web push on iOS 16.4+ for installed apps is widely reported but I did NOT verify it in this session — treat as EMERGING/unverified and confirm current iOS behaviour before committing. The engineering-month figure is my estimate (INFERENCE). The store kids-category review burden is EXPERT-OPINION.

**Recommendation**

Ship a PWA. Install prompt, service worker, IndexedDB for offline state, web push for reminders, input capture for note photos. Reuse the AEOS Next.js 16 frontend and its existing component patterns rather than standing up a second UI stack. Write down the trigger for revisiting: 'we build a native shell when a school tells us MDM distribution requires it, or when web push proves unreliable enough on iOS to break the review-reminder loop, measured by notification delivery rate' — and then build only the shell around the same web app. The 4 months saved is most of the time needed to actually build and validate the anxiety protocol (F02).

### F19 — Unmeasured and unmeasurable claims are stated as product features, and one of them will end a district procurement

| | |
|---|---|
| **Severity** | `LOW` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.82 |

**What the artifact says**
> '90% faster study with AND without AI' (Project Doc, For Students) and 'Module 9: Study 90% Faster — With and Without AI' (MCST certification). 'Triple Reading Speed ... Result: 60-90% speed increase with equal or greater comprehension.' 'African-Centered Pedagogy ... raises Black student achievement (ES: 0.8)'. 'Interleaving ... beats blocked practice for long-term retention by 43%'. 'Child Liberation ... 40% greater intrinsic motivation'. 'TAM: 6.4M students with IEPs, 74M K-12 parents, 1.3M paraeducators'.

**The problem**

Outside my lens to adjudicate the learning-science effect sizes individually — the evidence-and-claims reviewer should take those. But as a systems matter: these are unmeasured numbers stated as product capabilities, and the product has no instrumentation that could ever measure them. '90% faster study' has no defined denominator, no measurement procedure, and appears both as a marketing claim and as the title of a certification module a student is awarded a credential for completing. A district curriculum reviewer who encounters an unsubstantiated 90% efficacy claim will stop the procurement, and the founder's own principle is 'no claims of validation that has not occurred'. Separately, 'TAM: 6.4M students with IEPs, 74M K-12 parents' is not a TAM — a TAM is a dollar figure — and those populations are not addressable by a product targeting neurodivergent, predominantly Black/BIPOC MCPS middle schoolers; the serviceable market is a few thousand students.

**Evidence**

The measurement-procedure gap is verifiable: the artifact defines no study-time metric, baseline, or comparison condition anywhere. TAM-vs-population is a definitional point. The individual effect sizes are outside this lens and should be verified against primary sources by the evidence reviewer — do not treat my listing them as verification.

**Recommendation**

Strike every efficacy percentage from the product-facing surfaces and from the certification module titles, replacing them with the mechanism ('distributed practice and retrieval instead of re-reading') rather than a number. Keep effect sizes only in an internal research appendix with full citations, each marked with its replication status. Then instrument the three things you can actually measure in a pilot and report only those: weekly active days per student, protocol completion rate before tests, and pre/post anxiety score delta with the instrument named and its n stated. Replace the TAM paragraph with a SAM and a SOM: MCPS middle-school enrollment x estimated neurodivergent share x estimated willingness-to-pay, with each factor sourced. A small honest number is more fundable than a large unsupported one.


---

## What is missing and should be added

### A1 — Deterministic core: one Python package, no network, fully unit-tested   `INFERENCE`

**Why it matters.** The artifact routes scheduling, spacing, scoring, accommodation mapping, routing and thresholds through stochastic agents. All six are deterministic functions. Making them code removes ~45K tokens/family/day, removes the chain's latency entirely, makes them testable, and makes them work offline — which is the product's own stated requirement.

**What to build.** A single package `mindunlock/core/` in the AEOS backend, with zero network calls and 100% branch coverage: `scheduler.py` — BARS block placement as constraint solving over (duration, deadline, priority, energy_window, accommodation_ratio) tuples; greedy placement with backtracking, ~400 lines, returns a deterministic plan plus an explanation string for the UI. `srs.py` — thin wrapper over a reference FSRS implementation (py-fsrs, permissively licensed): per-card state (stability, difficulty, last_review, due, reps, lapses), grade ingestion, due-queue assembly, +/-5% interval fuzz, daily cap, due-load smoothing, and TIMEZONE-CORRECT day boundaries (the most common SRS bug). ~200 lines of wrapper; do not write the algorithm. `scoring.py` — diagnostic scoring keys and norm tables for the 52/38/24-domain instruments as DATA files plus arithmetic; a 'psychometric engine' is a scoring key, not a model. `accommodations.py` — a reviewed, versioned lookup table from IEP accommodation text to app config, with every entry carrying a reviewer and approval date; the model may only PROPOSE entries, never apply them. `routing.py` — the model-routing decision table (A2). `thresholds.py` — escalation comparisons with hysteresis windows so a student hovering at a boundary does not trigger repeated alerts. Every function pure, every function fuzz-tested, every function callable from the client for offline use (compile `scheduler` and `srs` to WASM or reimplement in TS against a shared fixture set that both implementations must pass).

**Evidence.** Each of these six is a closed-form computation with no natural-language input; the artifact's own descriptions ('Priority ranker (Eisenhower Matrix)', 'SM-18 spaced repetition scheduler', '52-domain psychometric engine') describe algorithms, not judgement tasks.

### A2 — LLM gateway: three call types, one service, with the model-routing policy written as a table   `ESTABLISHED`

**Why it matters.** Eight agents become three narrow, schema-bounded, independently gradeable calls. This is what makes the system testable (F04), cheap (F01), and operable by one person.

**What to build.** `mindunlock/llm/gateway.py` — the ONLY place in the codebase that calls a model provider. Three request-path call types, each with a Pydantic input schema, a Pydantic output schema, a frozen versioned prompt, and a golden fixture set: `explain(concept, reading_level, profile) -> Explanation`; `socratic_turn(rolling_history, goal, profile) -> Turn`; `critique_notes(note_text, method, rubric) -> Critique`. Two off-path: `extract_iep(pdf) -> list[AccommodationCandidate]` (Batch API, human-confirmed before any config change) and `classify_safety(message) -> SafetyLabel` (small classifier, input-side, parallel, fail-closed). ROUTING POLICY, as an explicit table: default every request-path call to Haiku-tier. Escalate to Sonnet-tier only when (a) a cheap deterministic grader scores the Haiku output below threshold, or (b) the call is on the anxiety-coach path (judgement + safety-sensitive, always Sonnet), or (c) the student has flagged the previous answer as unhelpful. A request may touch a FRONTIER model only if ALL of: it is user-visible and interactive; a cheaper model has already produced an output that failed the grader; the family's month-to-date spend is under the ceiling; and it is not one of the deterministic tasks in A1. In practice this means frontier models never run in the request path — their place is offline (A3, A4). Every call: static prefix marked for prompt caching (system + rubric + profile + accommodation config, ~6-7K of the ~9K input); rolling-window conversation context (last 6 turns + a 300-token running summary) instead of full-history resend; token meter written to the cost table (A5); request and response logged to the eval store with the prompt version.

**Evidence.** Published pricing (2026-10-06): Haiku 5.5 $0.10/$0.50, Sonnet 5.5 $2.00/$10.00, Opus 5.5 $4.00/$20.00 per MTok; cache reads $0.20 on Opus/Sonnet; Batch API 50% discount. These make a 20-40x spread between tiers, which is what the routing table monetizes.

### A3 — Content pipeline: precomputed, human-reviewed, provenance-carrying   `INFERENCE`

**Why it matters.** The cultural corpus, module text, CBT prompt library and reading-level variants are FIXED content, not per-request generation. Precomputing them saves ~624M tokens/year (F14) and is the only way the promised advisory-board veto can actually exist.

**What to build.** A build-time pipeline, not a runtime service. `content/` directory in the repo with source files; a script that (1) drafts with a frontier model, (2) writes to a review queue, (3) requires a named reviewer's approval with identity and date, (4) requires advisory-board sign-off for any culturally-specific item, (5) emits rows into a `content_items` table in the AEOS Postgres with columns: id, kind, locale, body, reviewer_id, approved_at, version, superseded_by, provenance_note. Served from the CDN and cached on-device; zero model calls at request time. Scope for the MVP: the 3 anxiety modules, ~40 CBT reframe prompts, ~20 somatic/breathing scripts, 365 daily cards, and ~30 ancestor profiles — NOT 100+ profiles and 40+ cultures, which is a Year-2 content program with a budget. One-time generation cost for the full corpus: ~6M output tokens, roughly $120 at frontier pricing, then $0 forever. Reading-level variants (grade 4 / grade 6 / grade 8) of every module paragraph are precomputed too — never rewritten at request time.

**Evidence.** The artifact's own risk card promises 'African-centered scholars as PAID co-developers; community advisory board with veto power; ongoing cultural review process' — a governance model that per-request generation cannot implement, since there is nothing to review before a child sees it.

### A4 — Eval harness and release gate (build before the pilot, ~2 weeks)   `INFERENCE`

**Why it matters.** Replaces 'confidence scoring... human review if score < 0.85', which is not a mechanism (F05). Without this, every prompt change is shipped blind to children.

**What to build.** `evals/` with: FIXTURES — 120 tutor openers (40 math, 30 ELA, 20 science, 15 vague 'I don't get it', 15 adversarial answer-extraction/jailbreak); 60 note-feedback samples across the 6 methods incl. blank, one-word, copied-textbook, wrong-subject; 80 safety probes (20 explicit self-harm, 20 ambiguous, 20 third-party 'my friend said', 20 NEGATIVES that are normal test-anxiety distress and must not fire); 40 IEP extraction fixtures with hand-labelled gold accommodation sets; 30 diagnostic gaming patterns (straight-lining, speed-running, contradictions). Every fixture carries a provenance field; synthetic or consented-and-de-identified only. RUBRICS written before looking at any output, 1-5, per call type. GRADERS — deterministic first (length, readability formula, answer-giving regex, PII scan, forbidden-claim scan covering medical advice/diagnosis language/'will cure your anxiety'), LLM-judge second on a stronger pinned model with frozen versioned prompts. JUDGE CALIBRATION — 60 of the 120 fixtures human-scored; report Cohen's kappa; kappa < 0.6 means the judge is not an instrument and must be fixed before use; re-measure monthly. RELEASE GATE in CI, blocking: safety recall >= 0.95 AND FPR <= 0.05 (both, no override); tutor rubric mean >= 4.0/5 with no fixture below 2; zero PII leaks; zero forbidden-claim hits; p95 latency per call type in budget; cost-per-fixture-run within 10% of previous release. HUMAN SPOT-CHECK — 20 live transcripts/week, stratified 10 random / 5 lowest-judge / 5 safety-flagged, 30 min/week, with disagreements becoming new fixtures.

**Evidence.** The false-positive requirement is the load-bearing half: a crisis classifier with a 20% FPR will alert parents and counselors dozens of times weekly, the school will disable it, and it will then protect nobody. The artifact specifies no FPR target anywhere.

### A5 — Cost model, per-family meter, and circuit breaker with a $3.00/month ceiling   `INFERENCE`

**Why it matters.** The design as written has ~3% gross margin at frontier pricing and zero headroom (F01). A ceiling enforced in code is the difference between a bounded business and an unbounded one, and the realistic 3am incident is a runaway token loop, not a crash.

**What to build.** RE-ARCHITECTED BUDGET, per family per day: daily plan call (replaces the 5-agent chain) 3K in of which 2.5K cached / 400 out, Haiku; tutor chat 12 turns at 2K fresh + 6K cached each = 24K fresh + 72K cached / 4.2K out, Haiku default with ~20% Sonnet escalation; note feedback 6K in (4K cached) / 700 out x 0.43 days, Haiku; anxiety coach 6 turns x (2K fresh + 5K cached) x 0.29 days, Sonnet; ancestor content ZERO tokens (precomputed, A3); parent coach 6 turns x (2K fresh + 6K cached) x 0.57 days, Haiku with escalation. Totals: ~40K fresh in / ~105K cache-read / ~6.1K out per family per day; over 26 days 1.04M fresh / 2.73M cached / 159K out. At an 80/20 Haiku/Sonnet token split: Haiku $0.17, Sonnet $0.85, cache writes ~$0.33, batch jobs (monthly IEP reports, weekly digests, 50% off) ~$0.30, amortized onboarding ~$0.15 = **~$1.80/family/month**, 5.4% of the $33.25 gross — an ~18x reduction from $32.15. IMPLEMENTATION: a `usage_events` table (family_id, call_type, model, input_tok, cached_tok, output_tok, cost_cents, prompt_version, ts) written on every gateway call; a materialized month-to-date view per family; a hard gate in the gateway that drops to Haiku-only at $2.00 MTD and refuses request-path model calls entirely at $3.00 MTD, degrading to the offline feature set with an honest message; a per-ORG daily cap at 3x the 7-day median that pages the founder. PRICE ASSUMPTIONS, stated and dated: Opus 5.5 $4.00/$20.00, Sonnet 5.5 $2.00/$10.00, Haiku 5.5 $0.10/$0.50, cache reads $0.20 on Opus/Sonnet, Batch 50% off — published rates cached 2026-10-06. Haiku cache-read at $0.01/MTok and cache WRITE at 1.25x input are ASSUMPTIONS from standard ratios and are unverified; re-derive from the live rate card before relying on them. Prices move; the model must be re-run quarterly.

**Evidence.** Rate table verified as current for 2026-10-06; token volumes are my estimates from the artifact's own architecture and from the re-architected design, labelled as assumptions throughout.

### A6 — Overnight precompute job: one cron, one JSON blob per family   `INFERENCE`

**Why it matters.** The single highest-leverage decision for both cost and latency (F09). It turns the morning experience from a 20-second five-agent chain into a 300ms local read, and it moves work from the expensive interactive path to the cheap batch path.

**What to build.** One idempotent job, run nightly per timezone, writing a `daily_brief` row per family: tomorrow's BARS block plan (from `core/scheduler.py`, zero model calls), tomorrow's SRS due queue (from `core/srs.py`, zero model calls), the day's ancestor card id (from the precomputed corpus, zero model calls), the parent digest (one batched Sonnet call per family on the Batch API, 50% off), and the next module pointer. The client pulls the blob on first connection and renders entirely from local storage thereafter. Monthly IEP progress reports run on the same infrastructure in a monthly pass, also on the Batch API. Idempotency matters more than elegance: a failed run is fixed by re-running it, which is what makes this safe for a solo operator. Implement as `arq` or a Supabase scheduled function — not Celery + Redis + a broker, which is three moving parts for one nightly job.

**Evidence.** The artifact's Daily Study Session chain fires five sequential agents at study-block start; every output in that chain except the tutor turn is derivable the night before from state that does not change overnight.

### A7 — Crisis escalation runbook with a named human, an agreed channel, and a tested fallback   `INFERENCE`

**Why it matters.** The artifact's escalation terminates in 'counselor alert' with no person, channel, hours or response window (F07). A safety promise that cannot be kept is worse than no promise, because families relied on it.

**What to build.** A one-page signed runbook, completed before any child is enrolled: NAMED recipient (school counselor, by name, with a backup), AGREED channel (phone + SMS, not email), AGREED response window with explicit hours, DOCUMENTED out-of-hours fallback (988 Suicide & Crisis Lifeline and the local crisis line, displayed in-app immediately and unconditionally, never gated behind a model decision), and the parent's written acknowledgement of what the system will and will not do. TECHNICAL: input-side classification of every student message, p95 <= 400ms, parallel with generation, FAIL-CLOSED (classifier error means no tutor response is rendered, and the student is shown the human-support screen). On a positive: tutor conversation halts, crisis resources render, the transcript is preserved in an access-logged table, and the escalation fires via the agreed channel with a delivery receipt — an escalation whose delivery is not confirmed must retry and then alert the founder. Quarterly drill: fire a test escalation end-to-end and confirm the named human received it; log the drill. Measure confirmed-true rate on fires monthly and feed disagreements back into the A4 safety fixtures.

**Evidence.** The artifact names the risk as 'Critical' in two places and specifies a mechanism in neither; 'automatic counselor + parent notification' names no recipient, channel or window.

### A8 — AEOS module layout: what to reuse verbatim, what is genuinely new   `ESTABLISHED`

**Why it matters.** Every hour spent re-proving multi-tenant isolation is an hour not spent on the product, and the re-proof will be weaker than the proof that already exists (F03).

**What to build.** Reuse UNCHANGED from the AEOS repo: organizations/schools tenancy and FORCE RLS (migrations 001-004); `backend/app/services/tenant_scope.py`; `backend/app/core/auth.py` and `dependencies.py`; `audit_logs` + policies; the `assessments` + `assessment_service.py` + `assessment_result_service.py` + `/api/assessments` pipeline for all three diagnostic instruments (instrument definitions become DATA rows, not new tables); `ai_recommendations` for every model output; `intervention_plans` + `intervention_actions` for BARS blocks and anxiety protocols; `progress_events` for streaks and review history; the Next.js 16 / @supabase/ssr frontend and its existing component patterns. EXTEND, do not rebuild: `backend/tests/security_mutations.py` must cover every new table before it holds a real row — this file is the most valuable artifact in the repo. NEW migrations, minimal: `content_items` (A3), `srs_cards` + append-only `srs_reviews`, `daily_brief` (A6), `usage_events` (A5), `consent_records` (COPPA verifiable parental consent), `safety_events`. Each gets ENABLE + FORCE ROW LEVEL SECURITY and the same four per-operation policies as the existing ten tables. NOT built: Pinecone (use pgvector in the existing project — the corpus is tens of thousands of vectors), Redis/ElastiCache (use Postgres plus the provider's prompt cache), Celery (use one arq worker), ECS Fargate / RDS Multi-AZ / CloudFront (use Vercel via the existing AEOS_Vercel_Deploy.sh plus one container plus managed Supabase), a second Supabase project (there is no reason for one).

**Evidence.** Direct inspection of /home/user/AEOS: ten tables with ENABLE + FORCE RLS and per-operation policies across migrations 001-004; eleven security/auth test files under backend/tests/ including security_mutations.py; frontend on next ^16.3.4 with @supabase/ssr.

### A9 — PWA client with explicit device and data budgets, tested on a cheap Android phone   `EMERGING`

**Why it matters.** Saves ~4 engineering months and two store review processes (F18), and forces the accessibility constraint that actually determines whether the target families can use the product at all — which the artifact never mentions.

**What to build.** Progressive web app on the existing AEOS Next.js 16 frontend: install prompt, service worker, IndexedDB for offline state, web push for the daily card and review reminder, `<input capture>` for note photos, `speechSynthesis` for TTS. BUDGETS enforced in CI and failing the build: initial payload <= 500KB gzipped; daily sync <= 200KB; audio 32kbps mono opus, downloaded only on wifi, never autoplaying; images AVIF/WebP <= 40KB; no WebSocket; no autoplaying video. ACCEPTANCE DEVICE: buy one budget Android (roughly $120, 2019-era, Android Go) and make passing on it with Data Saver enabled and a throttled 3G profile a release requirement. OFFLINE CONTRACT, documented and tested: schedule, SRS review, note capture, timers, breathing exercises, streaks, all module text and audio work with no network; tutor chat and note AI feedback degrade with an honest message. REVISIT TRIGGER, written down: build a native shell only when a school states MDM distribution requires it, or when measured web-push delivery rate on iOS falls below the threshold that breaks the reminder loop.

**Evidence.** PWA capability claims (iOS 16.4+ web push for installed apps) are widely reported but UNVERIFIED in this session — confirm current iOS behaviour before committing. The device/data budget requirement follows from the stated target population (under-resourced MCPS families), which the artifact describes but never designs for.

### A10 — Four SLOs, three pages, and a deployment a tired person can operate   `EXPERT-OPINION`

**Why it matters.** A 99.9% SLA commits a solo founder to 43.2 minutes/month of downtime he cannot defend (F10). The goal is not high availability; it is that 3am never requires a human.

**What to build.** SLOs (four, internal, unpublished): API availability >= 99.0% monthly (7.2 hr budget); tutor first-token p95 <= 2.5s; 100% of student messages safety-classified before a tutor response renders (correctness, fail-closed); inference COGS per family per month p95 <= $3.00. PAGES (exactly three, to the phone): API 5xx > 5% for 5 min; safety classifier erroring; any org's daily spend > 3x its 7-day median. Everything else is a daily digest email. DEPLOYMENT: GitHub Actions runs unit tests + `security_mutations.py` + the A4 eval gate, builds a container, deploys one stateless instance to one region behind a health check with a 30-second rolling restart (blue/green is unnecessary at this scale); managed Supabase Postgres with PITR; Vercel for the PWA. OPERABILITY, designed so the 3am action is always the same: a feature-flag kill switch on every model-calling path so 'turn off the tutor' is one toggle from a phone and the app falls back to its tested offline mode; the A5 spend circuit breaker so a runaway loop disables a feature instead of generating a $4,000 bill; idempotent nightly jobs so a failure is fixed by re-running; a written restore runbook, drilled quarterly, run at 9am from a backup you have actually restored. EXTERNALLY: publish a status page and a support commitment (business hours, next-business-day response, 48h maintenance notice, we tell you when we are down) — no SLA, no multi-region, no bug bounty in year one.

**Evidence.** 99.9% = 43.2 min/month is arithmetic. The three-page limit is an operational heuristic: a pager that fires more often than it is actionable gets muted, after which it provides no coverage.

### A11 — Build order with kill criteria, and a scorecard the founder reads every Monday   `INFERENCE`

**Why it matters.** The artifact's roadmap has milestones but no stopping rules, so nothing can ever be abandoned — which is how a 45-engineering-month plan gets attempted by one person (F02).

**What to build.** ONE thing first: the pre-test anxiety protocol with pre/post measurement, PWA, 10 families, 8 weeks. It is the artifact's own core thesis, needs 3 modules rather than 240 hours of content, is measurable in 8 weeks, and if the effect is absent nothing downstream matters. KILL IF: <60% of enrolled students complete >= 6 of 8 pre-test protocols. At n=10 the gate is engagement and direction, stated honestly — not a significance claim. Then, each with a written kill criterion checked on a fixed date: (2) deterministic BARS scheduler, no AI, 6 wks — kill if median weekly active days < 3 by week 4. (3) Spaced repetition, 4 wks — kill if <40% reach a 5-day streak by week 3. (4) Tutor chat, 6 wks — kill if COGS/family/month > $3.00 or the A4 gate cannot be held green for two consecutive releases. (5) Parent coaching track, 6 wks — kill if <30% of parents complete module 3. NOT STARTED until 100 paying families: all four certification tracks, LMS integration, district dashboard, Spanish, GED-to-PhD. NEVER started without prepayment: MMEC teacher certification (120 hr of content). MONDAY SCORECARD, one screen: COGS/family p95 MTD, safety fires and confirmed-true rate, weekly active days per student, protocol completion rate, pre/post anxiety delta, eval-gate status, and days remaining to the next kill-criterion date. Seven numbers. If a number is red for two weeks running, the kill criterion applies — the point of writing it down in advance is that the decision is made by a condition, not by how the founder feels that Monday.

**Evidence.** The artifact's Phase KPIs ('5 school contracts closed', '500 family subscriptions') are targets, not gates — none of them specifies what happens if the number is missed, so none of them can stop work.

### A12 — Data-handling rule, asserted at startup, written into the DPA   `INFERENCE`

**Why it matters.** The product promises 'full data deletion on demand' while leaving training policy undefined (F13). Training on student text makes that promise structurally impossible to keep, and it is the failure mode that ends the company rather than merely costing it money.

**What to build.** THE RULE, identical text in the DPA and the code comments: student-generated content and PII are used only for inference, in-prompt, scoped to that student's session; never for model training, fine-tuning, or eval-fixture creation without separate, specific, written, revocable consent AND de-identification. ENFORCEMENT: a startup check that reads the configured provider's zero-data-retention / no-training setting and FAILS THE DEPLOY if it is not enabled — a config flag nobody verifies is not a control. Eval fixtures (A4) are synthetic or consented-and-de-identified only, with a provenance field on every record and a CI check that rejects a fixture without one. Deletion path implemented and tested end-to-end before the pilot: a parent request deletes rows from every table including transcripts and `safety_events` (subject to a documented legal-hold exception), is logged in `audit_logs`, and is confirmable in writing. Explicitly NOT built: any fine-tuning or distillation pipeline — you lack the data, the quality gap is already closed more cheaply by caching + reviewed content + routing, and a fine-tuned small model must be re-tuned every time the base model moves, which a solo founder will not sustain. Revisit at >10,000 daily active students with a stable, measured task. LEGAL: have counsel confirm the FERPA school-official/contractor basis, the COPPA verifiable-consent mechanism, and Maryland's own student-data-privacy provisions before the pilot — I have NOT verified the specific CFR sections and my references to 34 CFR Part 99 / 99.31(a)(1) should be treated as pointers for counsel, not as citations.

**Evidence.** The irreversibility argument is deterministic: rows can be deleted, weights cannot be un-trained. The FERPA structure is INFERENCE from standard ed-tech DPA practice; the section numbers are explicitly unverified.


---

## Open questions

- What is the actual per-turn length distribution of middle-school tutor chat? My cost model assumes 12 turns/day at ~350 output tokens; if the real distribution is long-tailed (a handful of students doing 40+ turns), the per-family ceiling matters far more than the mean and the circuit breaker in A5 becomes the primary cost control rather than a backstop. Instrument this in week 1 of the pilot before trusting any COGS number, including mine.
- Does the founder intend MindUnlock to be a separate company or an AEOS module commercially as well as technically? The build-vs-buy case in F03/A8 is overwhelming on engineering grounds, but if MindUnlock is meant to be separately fundable or sellable, a shared Supabase project creates a data-separation problem at exit. If so, the answer is a separate schema with the same proven RLS pattern and the same mutation test suite — not a separate stack.
- Is the Spielberger Test Anxiety Inventory (cited in the Diagnostics tab) a licensed instrument requiring a per-administration fee? The artifact uses it as a framework source and the Anxiety Coach agent lists a 'Spielberger TAI scorer' as a tool. I did not verify its licensing status. If it is licensed, both the cost model and the MVP's outcome measure need an alternative — candidates to check are the Children's Test Anxiety Scale and the FRIEDBEN, but I have verified neither's licensing or psychometrics.
- I could not reach docs.ankiweb.net in this session (the host did not resolve under the session's network allowlist), so the claim that FSRS became Anki's default in version 23.10 rests on third-party sources. The SM-18 and AnkiConnect findings (F06) do not depend on it and are solidly sourced, but confirm the FSRS default detail against Anki's own FAQ before it goes into any document.
- What are the actual device and connectivity profiles of the target 10 pilot families? A9's budgets assume a 2019-era budget Android on throttled 3G, which is my inference from 'under-resourced MCPS families', not a measurement. A 10-minute survey at enrollment (device model, OS version, data plan, home wifi) would turn every performance budget in this plan from an assumption into a requirement — and might reveal that the constraint is tighter or looser than I guessed.
- Has any MCPS counselor or administrator actually agreed, in writing, to be the named recipient in the crisis-escalation path (A7)? The entire safety design is contingent on this, and it is the one dependency the founder cannot build around. If the answer is no, the honest MVP displays 988 and the local crisis line directly to the student and parent and makes no claim of counselor notification at all.
- What is the founder's genuine weekly hours budget for this, net of the MCPS job and AEOS? My 45-engineering-month estimate (F02) is scope-side only. If the real figure is 10-15 hrs/week, even the single-surface MVP in A11 is a 4-6 month project rather than 8 weeks, and the kill-criterion dates need to be set against that calendar rather than the roadmap's.
- Does MCPS have an existing approved-vendor or data-privacy-agreement process the founder has read? Building to the actual DPA template is enormously cheaper than building and then retrofitting — and as an MCPS employee the founder may have access to it. It would also settle several open questions in this review at once: the training prohibition language, the retention periods, the sub-processor disclosure requirements, and whether any non-US-hosted provider is categorically excluded (F08).

