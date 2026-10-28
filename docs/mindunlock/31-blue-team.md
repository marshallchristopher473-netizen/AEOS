# Blue team

> The defensible version: controls, architecture, governance and sequencing that let the idea exist safely.

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

The single most important finding: **this product's legal exposure is almost entirely optional, and it is concentrated in features that are not in the value proposition.** Strip four things — IEP PDF ingestion, the clinical/PPRA-protected halves of the 52-domain instrument, the licensed Spielberger TAI, and automated parent/counselor notification — and roughly 80% of the FERPA/IDEA/PPRA/COPPA/licensure/injection surface disappears while the thing families would actually pay for (a scheduler, note-taking instruction, retrieval practice, a calm-down toolkit, a parent coaching track, heritage-rich content) is untouched. The artifact treats these four as core; they are not. They are the most dangerous and least differentiated parts of the design.

The second finding: the artifact's stated mitigations are procedural where they must be structural. "Legal counsel from Day 1," "confidence scoring … human review queue for score < 0.85," "community advisory board with veto power," and "FERPA-compliant with row-level security" are all promises about behaviour, not properties of a system. Each has a structural replacement: data that is never collected cannot leak; a deterministic classifier outside the model cannot be talked out of firing; an advisory council with a budget line and a named veto scope cannot be ignored silently; and AEOS already *has* the RLS primitives (`aeos_has_org_access`, `aeos_can_write_org` in `backend/supabase/migrations/002_tenant_rls.sql`) plus a committed security-mutation suite — the MindUnlock schema sketched at lines 665–674 ignores all of it and reintroduces an unscoped `agent_memory` table.

The third finding, and the one the founder will like least: **the conflict of interest is not in the risk register at all.** An MCPS employee building a product whose roadmap targets "MCPS district leadership presentation" and "5 MCPS school contracts" — with a pilot of "10 MCPS families" and "Assignment auto-import from school portal" — has a problem no privacy control fixes. The strongest move in year one is to not sell to MCPS, not recruit MCPS families through MCPS channels, and build the evidence base direct-to-family. That is also, separately, the fastest path to the founder's own stated sequence of MVP → pilot → measurement → evidence → revenue.

AEOS already contains the scaffolding for the claims discipline this needs (`frontend/src/lib/briefing/types.ts`, with `EvidenceTier`, `TIER_RANK` and `MARKETABLE_TIERS`). The defensible version extends what exists rather than building a parallel stack.

---

## Findings

### BT-01 — The employer conflict of interest is absent from the risk register entirely

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Risks & Mitigation card (lines 116-122) lists six risks: FERPA/COPPA, AI hallucination, student crisis, cultural appropriation, pilot dropout, UI complexity. None concerns the founder's employment. Roadmap Phase 3 (line 777): 'MCPS district leadership presentation delivered' / '5 school contracts signed ($37,500 ARR)'. Phase 1 (line 771): 'Pilot cohort: 10 MCPS families (5 students + parents)'.

**The problem**

The highest-probability career-ending event in the whole plan is not listed as a risk, so no mitigation exists for it. An MCPS employee intending to sell to MCPS, pilot with MCPS families, and integrate with MCPS systems has a conflict that no privacy control, consent flow or encryption scheme addresses. Every other mitigation in the register is downstream of this one. Worse: the artifact's own next-actions sequence puts the MCPS pilot at Week 6-8, before any disclosure step exists anywhere in the document.

**Evidence**

[ESTABLISHED, primary policy text] MCPS Regulation GCA-RA states its expectations 'go beyond those specifically addressed in Maryland ethics law and Montgomery County Board of Education Policy BBB, Ethics.' The MCPS Employee Code of Conduct instructs employees not to 'use your position as an MCPS employee, MCPS resources, or information gained through your employment, for personal gain.' Board ethics materials list as prohibited being employed by MCPS and simultaneously by 'a company that is subject to the authority of the school system, or has negotiated or is negotiating a contract with the school system.' The MCPS Ethics Panel is the body that interprets the policy and issues advisory opinions (Board of Education Office, 240-740-3030); a violation finding 'may constitute grounds for removal from office, discipline, or other personnel action.' Sources: montgomeryschoolsmd.org/ethics/; ww2.montgomeryschoolsmd.org/departments/policy/pdf/gcara%20master.pdf; the 2025-26 Employee Code of Conduct PDF. [INFERENCE] The application of these to a sole-founder selling his own product is not spelled out in the texts I could retrieve — ww2.montgomeryschoolsmd.org did not resolve from this session, so the full GCA-RA text is unverified and should be read directly.

**Recommendation**

Add 'Founder employment conflict' as risk #1 with severity Blocker, and gate all other work behind a four-step sequence executed in writing and in this order: (1) Written disclosure to immediate supervisor describing the venture, its scope, and that no MCPS data, students, families, time or equipment will be used. (2) Written request for an advisory opinion from the MCPS Ethics Panel via the Ethics Officer, asking three specific questions: may I develop and own this product; may I recruit MCPS families; may I sell to MCPS, and if so under what conditions. (3) File the outside-employment pre-approval form (MCPS Form 460-50) covering officer/director service in the entity, compensated or not. (4) Do nothing that touches MCPS until a written answer exists. Keep the correspondence as the project's first artifact.

### BT-02 — IEP PDF ingestion is the largest single exposure in the design and is presented as the headline feature

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.95 |

**What the artifact says**
> App Design, 'IEP AI 5-Step Workflow' step 1 (line 568): 'IEP Document Upload — Parent/school uploads IEP PDF; AI extracts accommodations, goals, and evaluation dates automatically.' Also line 593, Diagnostic Agent tool: 'IEP PDF parser (NLP)'; line 666 schema: 'student_profiles (diagnostic_json, iep_id, ancestry[])'; line 660: 'S3 / Supabase Storage … IEP documents'.

**The problem**

An IEP is simultaneously a FERPA education record, IDEA-protected personally identifiable information, and a document containing disability diagnosis and often clinical/behavioural narrative. Ingesting it creates, in one feature: (a) a records-custody obligation with destruction duties; (b) an IDEA consent chain the company cannot verify from the parent's side alone when the document originated with the school; (c) an untrusted-document prompt-injection channel feeding an agent that has notification and profile-write tools; (d) a breach-notification blast radius containing the most sensitive data the product will ever hold; (e) a reason for MCPS counsel to treat the venture as an operator under Md. Educ. §4-131 even in a direct-to-parent sale. None of this buys anything a two-minute structured picker cannot deliver.

**Evidence**

[ESTABLISHED] 34 CFR 300.622 requires parental consent before personally identifiable information is disclosed to parties other than officials of participating agencies, with limited exceptions (ecfr.gov, 34 CFR 300.622). FERPA education-record status attaches to IEPs held by the LEA. [ESTABLISHED] OWASP GenAI LLM01:2025 Prompt Injection describes exactly this vector — 'an AI that analyzes uploaded documents processes a document containing hidden instructions' — and states plainly that 'it is unclear if there are fool-proof methods of prevention' (genai.owasp.org/llmrisk/llm01-prompt-injection/). The OWASP LLM Prompt Injection Prevention Cheat Sheet adds that pattern-based filters do not reliably catch indirect injection and that RAG/fine-tuning do not mitigate it. [UNVERIFIED] 34 CFR 300.624 (destruction of information) text was not retrieved; read it before designing retention.

**Recommendation**

Cut IEP upload from v1 and from v2. Replace with a parent-asserted accommodation picker: a fixed enum of 10-12 supports the parent selects for their own child, stored as `learner_supports(learner_id, support_code, asserted_by, asserted_at)` with support_code from a closed vocabulary (extended_time_ratio, text_to_speech, chunked_tasks, reduced_distraction, frequent_breaks, visual_alternative, flexible_response_mode, …). Label it in the UI as 'what helps my child,' never 'IEP accommodations.' Never accept a file upload of any kind in v1 — no PDF, no photo of a document, no camera. Add a hard control: the storage bucket for documents does not exist, so there is nothing to misconfigure. If a school-facing version is ever built, IEP data stays in the school's system and the product consumes only a signed accommodation vector, never the document.

### BT-03 — 'Confidence scoring < 0.85' is not a control, and AEOS is about to institutionalise it

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.94 |

**What the artifact says**
> Stated twice as the primary mitigation for the Critical risk 'AI hallucination in educational content' (line 118 and line 634): 'Confidence scoring on ALL outputs; human expert review queue for score < 0.85; citations required; zero-tolerance for unverified academic claims.'

**The problem**

A self-reported LLM confidence number is not calibrated to factual accuracy, is trivially gamed by the generation that produces it, and is produced by the same forward pass whose output is in question. A model asserting a fabricated citation will assert high confidence in it. The threshold 0.85 is arbitrary and no routing behaviour, reviewer, SLA or queue-drain policy is specified — so in practice the queue either never fills or never empties. Compounding this: the existing AEOS schema already ships `ai_recommendations.confidence_score NUMERIC(5,4)` (backend/supabase/migrations/001_initial_schema.sql), which means the anti-pattern has a column waiting for it and will look like an architectural decision rather than an unexamined one. 'Citations required' without retrieval grounding over a curated corpus produces fabricated citations, which is strictly worse than no citation because it survives review.

**Evidence**

[ESTABLISHED] OWASP's LLM guidance directs that model output be treated as untrusted and that enforcement live 'in code outside the model' rather than in the model's own report; it recommends validating tool arguments and enforcing permissions outside the model, and running retrieved content through a classifier before the main model sees it (cheatsheetseries.owasp.org — LLM Prompt Injection Prevention Cheat Sheet). [INFERENCE] The specific inadequacy of self-reported confidence as a hallucination gate follows from this: a control implemented inside the untrusted component is not a control.

**Recommendation**

Delete the confidence threshold from the risk register and replace with four named, testable controls. (1) **Retrieval-grounded generation with citation enforcement**: all instructional content is generated only over a curated corpus (`content_corpus` table: doc_id, title, source_locator, evidence_tier, approved_by, approved_at); a post-generation validator rejects any output whose citations do not resolve to a corpus doc_id, and the rejection is a 500, not a warning. (2) **Structured output constraints**: every agent returns a typed Pydantic V2 model, never free text, for anything that writes to the database or reaches a human. (3) **Deterministic classifiers for safety routing**, never LLM self-report (see BT-04). (4) **No tool or notification capability in any context that has ingested user-authored or uploaded text** — a strict two-model split: an untrusted-content reader with zero tools, and a tool-bearing orchestrator that receives only structured, validated fields from it. Drop `confidence_score` or rename it `model_reported_confidence` and forbid its use in any routing decision, enforced by a test in `backend/tests/security_mutations.py`.

### BT-04 — Automatic parent notification on distress is itself the harm case

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `EXPERT-OPINION` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Line 119: 'Crisis detection layer; automatic counselor + parent notification; hotline display; AI conversation paused immediately.' Line 557: 'Check-in / Check-out — Daily emotional check-in; threshold alert to parent + counselor if distress detected.' Line 572: 'Crisis Escalation Protocol — Anxiety markers exceed threshold → counselor alert + parent notification + crisis resources displayed.' Line 595, Test Anxiety Coach output: 'counselor referral flag, parent notification.' Line 619 workflow: 'Test Anxiety Coach → Tutor Agent → Parent Coach Agent (notification) → [Counselor flag if threshold exceeded]'.

**The problem**

For a meaningful subset of adolescents, the parent is the source of the distress, or disclosure to the parent is the feared consequence that prevents disclosure in the first place. An automated, thresholded, unreviewed notification to a parent — triggered by a classifier on a 13-year-old's typed text — converts a help-seeking moment into a punishment event, and does so with no human who can exercise judgement about this particular family. It also teaches every child in the cohort that the product reports to their parents, which destroys the disclosure channel the feature exists to serve. Separately, 'automatic counselor notification' from a private company to an MCPS counselor is a disclosure of a minor's mental-health-adjacent data to a third party, by a company with no treatment relationship, no privilege, and no mandated-reporter standing in its commercial capacity. And a crisis-detection system that families are told exists creates a reliance that makes a missed detection a negligence theory rather than a product limitation.

**Evidence**

[EXPERT-OPINION] Crisis-line and youth-services practice standards consistently treat notification of a parent/guardian as a decision requiring a trained human and, where possible, the young person's involvement — not a threshold. [INFERENCE] The legal asymmetry is structural: a product that promises detection assumes a duty it cannot discharge; a product that promises only resources assumes none. [UNVERIFIED — check before building] Maryland's minor-consent-to-mental-health rules (Md. Health-General Article) and the mandated-reporter statute (Md. Family Law §5-704) interact with this design in ways I did not verify; both should be read with counsel, specifically on whether the founder's MCPS-employee reporter status follows him into the venture.

**Recommendation**

Design the escalation as **show resources and stop**. Concretely: (1) The product never notifies a parent automatically, ever, for anything emotional. (2) A deterministic classifier (regex + a small purpose-trained classifier on a fixed phrase set, running outside the conversational model, logged on every turn) triggers exactly one behaviour: the conversational agent is suspended for that session and a non-AI static panel renders — 988 Suicide & Crisis Lifeline, Crisis Text Line (text HOME to 741741), and the child's school counselor's name and number as plain text the child may choose to use. (3) No agent writes, no notification fires, no flag reaches the parent dashboard. (4) A human reviewer (named role, 24h SLA, in the pilot this is the founder) reads the flagged transcript and makes a case-by-case decision documented in `safety_reviews`. (5) The product's own copy says, in the consent form and in the UI: 'This is not a crisis service and does not monitor your child. If you believe your child is in danger, call 988.' Build this as a `SafetyGate` middleware in FastAPI that the agent router cannot bypass, and test it with an adversarial fixture set.

### BT-05 — The Spielberger TAI is licensed, per-administration, and its research licence forbids the exact use the product makes of it

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.92 |

**What the artifact says**
> Line 264, diagnostic framework sources: 'Spielberger TAI (1980)'; line 265 badge 'Spielberger TAI'; line 595, Test Anxiety Coach tool: 'Spielberger TAI scorer'; line 398, MCLSS Domain 2: 'Spielberger TAI screening'.

**The problem**

The TAI is not a framework one can be 'informed by' while embedding a scorer for it. Building a scorer implies holding the items; administering it to pilot families implies per-administration fees; and the standard research licence explicitly excludes providing individual feedback to participants — which is the entire product behaviour. Teaching paraeducators to perform 'Spielberger TAI screening' under a MindUnlock certificate compounds this into unlicensed-screening-by-proxy. This is both a copyright exposure and a scope-of-practice exposure, and it is being baked into a certification curriculum that will be sold at $299.

**Evidence**

[ESTABLISHED, publisher's own licence terms] Mind Garden publishes the Test Anxiety Inventory (© 1980 Charles D. Spielberger) and states that instrument items, directions, manual and reports are the copyright holder's intellectual property, usable only with purchase or written permission. Licence to Administer carries a minimum purchase of 50; Transform Survey Hosting a minimum of 20; 'each time a participant opens the survey and has access to the copyrighted items counts as one administration' and is billed. The research licence is 'for research purposes only, for data collection only, and not for providing individual feedback to survey participants,' requires access control, and forbids open-web availability. (mindgarden.com/150-test-anxiety-inventory; .../760-tai-license-to-administer.html)

**Recommendation**

Remove every reference to the TAI from the product, the curriculum and the marketing. Replace with a short, free, non-clinical self-report the company owns or can clearly use, administered and framed as a **preference/experience check-in, not a screen**: a 5-8 item MindUnlock-authored scale measuring self-reported study confidence and pre-test worry, written at a grade-6 reading level, with no cut scores, no severity bands, no clinical labels and no normative comparison. If a validated external reference is wanted for the pilot's outcome measure only (not the product), the Westside Test Anxiety Scale (Driscoll, 2007; ERIC ED495968) is 10 items and described as free for schools — but note it carries a '© 2004 Richard Driscoll' notice and is therefore **not public domain**; write to Driscoll for permission in writing before pilot use. Delete 'Spielberger TAI screening' from MCLSS Domain 2 and replace with 'Recognising signs of test anxiety and making a referral.'

### BT-06 — The 52-domain instrument collects PPRA-protected and clinical-adjacent data from minors and calls itself validated

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Header (line 258): 'PhD-Level Diagnostic Assessments — Psychometrically validated | Student: 52 domains'. Domain 1 (line 268), 12 items incl. '1.2 Emotionality/somatic arousal — sweating, heart racing, nausea', '1.12 Stereotype threat susceptibility'. Domain 5 (line 272): '5.2 Sensory sensitivity', '5.7 Current IEP/504 accommodation profile (cross-referenced with school records)'. Domain 6 (line 273): '6.3 Sleep quantity and quality'. Parent Domain 3 (line 291): 'Own emotional regulation during child's academic stress and meltdowns'; Parent Domain 2 (line 290): 'Own academic struggles … test anxiety'.

**The problem**

Three distinct defects. (1) **PPRA category overlap**: a 12-item anxiety battery administered to a minor probes 'mental or psychological problems of the student or the student's family' — a PPRA-protected category — and parent Domain 3 probes the parent's own emotional regulation, which is a critical appraisal of a family member. In any school-mediated administration this requires prior written parental consent and inspection rights. (2) **'Psychometrically validated' is a false statement**: an instrument assembled from constructs and reviewed once by a school psychologist has no reliability coefficients, no factor structure, no norms and no criterion validity. Calling it validated in a document shown to a district is a misrepresentation. (3) **Scope of practice**: administering and interpreting a battery of mental-ability and personality-adjacent items for compensation is the statutory description of practising psychology in Maryland. '5.7 cross-referenced with school records' additionally reimports the FERPA problem BT-02 was meant to remove.

**Evidence**

[ESTABLISHED] 20 U.S.C. §1232h protects eight categories including 'mental or psychological problems of the student or the student's family' and critical appraisals of close family members, with prior written parental consent for ED-funded surveys, annual notice, opt-out and inspection rights; 34 CFR Part 98 implements it. ED's Student Privacy Policy Office has stated that behavioural-health screeners probing students' emotional or psychological states require written parental consent before administration (studentprivacy.ed.gov; SPPO Back-to-School Dear Colleague Letter, Aug 2026). [ESTABLISHED] Md. Health Occupations §18-101(f)(1)(iii) defines 'practice psychology' to include 'any service for compensation involving the application of psychological methods or psychological procedures for constructing, administering, or interpreting tests'; §18-301 requires licensure; COMAR 10.36.01.07 lists exceptions, none of which obviously covers a commercial edtech product (mgaleg.maryland.gov/2024RS/Statute_Web/gho/18-101.pdf; law.cornell.edu/regulations/maryland/COMAR-10-36-01-07).

**Recommendation**

Cut the student instrument from 52 domains to roughly 14 items across three domains, and change its name from 'diagnostic' to **'Study Start — tell us how you like to work.'** Keep in v1: Domain 2 items 2.2 task initiation, 2.3 planning, 2.4 time estimation, 2.8 organisation (as behavioural self-report, not EF constructs); Domain 3 item 3.8 note-taking baseline; Domain 6 items 6.1 homework routine, 6.2 study environment, 6.4 extracurricular demands; plus the accommodation picker from BT-02. Cut entirely from v1: **all 12 Domain 1 anxiety items** (PPRA + clinical), **2.1 working memory digit span** (cognitive testing), **2.7 emotional regulation**, **3.1 phonological awareness / 3.2 fluency / 3.4 CALP level** (psychoeducational assessment), **4.1 identity development stage, 4.5 stereotype threat vulnerability, 4.8 cultural learning style** (see BT-11), **5.1 VARK, 5.2 sensory sensitivity, 5.5 processing speed, 5.6 attention pattern, 5.7 IEP cross-reference**, **6.3 sleep**. From the parent instrument cut all of Domain 2 (parent's own academic trauma) and Domain 3 items on the parent's own emotional regulation and anxiety history. Replace 'psychometrically validated' everywhere with 'not a diagnostic instrument; not validated; used only to personalise the app's defaults' and put that sentence in the UI above the first question.

### BT-07 — Agent memory is designed without a tenant boundary, discarding AEOS's existing isolation model

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.91 |

**What the artifact says**
> Line 673, Core Schema: 'agent_memory (agent_id, user_id, context jsonb, ttl)'. Line 660: 'Redis (Upstash) — Cache / Agent Memory — Short-term agent memory, session state'. Each of the 8 agents carries a 'Memory:' line, e.g. line 598 Parent Coach Agent: 'child's struggle areas, family dynamic baseline, cohort connection history'.

**The problem**

`agent_memory` has no `organization_id`, so it is outside every policy in `backend/supabase/migrations/002_tenant_rls.sql` and outside every filter in `backend/app/services/tenant_scope.py`. AEOS's model is explicit that the FastAPI layer uses the service-role client which bypasses RLS and therefore must apply the organization filter in application code — a table with no organization column cannot be filtered that way, so the defence simply does not apply to it. Compounding this, agent memory is free-form `context jsonb` holding the most sensitive derived content in the system ('family dynamic baseline', 'anxiety history by test type', 'trigger patterns') and is additionally mirrored into Redis, which has no RLS at all. A single prompt-level retrieval bug then crosses families rather than crossing rows. `ancestry[]` on `student_profiles` sits in the same unscoped sketch.

**Evidence**

[ESTABLISHED, repo source] `backend/supabase/migrations/002_tenant_rls.sql` header: 'The FastAPI application currently uses the server-only service-role client, which deliberately bypasses RLS and therefore applies matching tenant filters in app/services/tenant_scope.py.' Every table in `001_initial_schema.sql` that holds learner data carries `organization_id UUID NOT NULL REFERENCES organizations(id)`. `tenant_scope.list_tenant_scoped_rows` filters solely on `.eq('organization_id', organization_id)`. [INFERENCE] A table lacking that column is therefore unreachable by both defences simultaneously.

**Recommendation**

Do not create a general `agent_memory` table. Replace with: (1) **No cross-session agent memory in v1 at all** — each session's context is assembled server-side from typed, tenant-scoped rows (`learner_supports`, `study_sessions`, `schedule_blocks`) and discarded. (2) If memory is later needed, it is `agent_memory(id, organization_id NOT NULL, learner_id NOT NULL, agent_key, memory_kind, payload JSONB, expires_at)` with an RLS policy using `aeos_has_org_access(organization_id)`, a NOT NULL check on both scoping columns, and a `tenant_scope` filter in app code — matching the pattern of every existing table. (3) Redis keys are namespaced `org:{organization_id}:learner:{learner_id}:...` with a key-builder function that cannot be called without an organization_id, and a unit test that asserts no raw `redis.get` appears outside it. (4) Add a case to `backend/tests/security_mutations.py` that drops the organization_id predicate from the memory path and asserts the suite fails — the existing suite's own methodology. (5) Drop `ancestry[]` (see BT-11).

### BT-08 — Credential naming and 'PhD-Level' framing are deceptive as written and are already attached to prices

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Header (line 837): 'PhD-Level Test Anxiety + Learning Science Platform'; badge (line 839) 'PhD Certified'. Line 334: 'MindUnlock Certified Student Tutor (MCST) … PhD-Level Certification Exam'. Line 394: 'MCLSS … 80 hours | CEU-eligible | MCPS District Partnership'. Line 419: 'MMEC … 120 hours | CEU-eligible | University graduate credit partnership'. Line 440: 'University Partnership Track — 3 graduate credits via partner university | Stackable toward MAT or Ed.D. | Target partners: Howard University, Morgan State, UMCP'. Business tab lines 725-726 price these at $299 and $499.

**The problem**

Four separate misrepresentations, each independently actionable as deceptive advertising and each attached to a price. (1) 'PhD-Level' describes nothing — there is no PhD, no doctoral-granting body and no doctoral review. (2) 'Certified' implies a certifying body; MindUnlock would be certifying against its own standard, which is permissible only if stated as such. (3) 'CEU-eligible' asserts an accreditation relationship that does not exist and cannot exist for at least a year (see BT-09). (4) 'MCPS District Partnership' and the named universities are listed as facts in the paraeducator card and as 'Target partners' only in the fine print of the teacher card — a reader sees a partnership. Naming Howard, Morgan State and UMCP in a document that circulates is a use of their names they have not agreed to. Separately, 'MCPS District Partnership' asserted by an MCPS employee is the conflict in BT-01 printed on a sales page.

**Evidence**

[INFERENCE] from FTC deceptive-advertising principles: a claim about certification, accreditation or affiliation is material to purchase and must be substantiated at the time it is made. [ESTABLISHED] Accreditation paths and their real timelines are in BT-09. [UNVERIFIED] Whether any of the three named universities has been approached is not stated in the artifact; the phrase 'Target partners' suggests not.

**Recommendation**

Rewrite the whole naming scheme before any page is public. Replace 'PhD-Level' everywhere with 'Evidence-based' or delete it. Replace 'MindUnlock Certified X' with 'MindUnlock Program Completion: X' and have the artefact issued be a **Certificate of Completion** stating exactly: programme name, total contact hours, completion date, a one-line description of what the learner demonstrated, and the sentence 'MindUnlock Academy is not an accredited institution. This certificate does not confer a licence, endorsement, degree, or continuing-education credit.' Delete 'CEU-eligible' from every surface until an IACET or MSDE path has actually completed. Delete all three university names and 'MCPS District Partnership' until a signed agreement exists; replace with 'We are seeking university partners for graduate credit; none is in place.' Price the paraeducator track accordingly — a completion certificate is not a $299 credential, and pricing it as one is the evidence of intent.

### BT-09 — 'CEU-eligible' has a real path with a real timeline, and the roadmap allows for neither

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.92 |

**What the artifact says**
> Line 99, Next Action #9: 'Build paraeducator MCLSS certification curriculum (12 competency domains, 80 hours, CEU-eligible)' at Week 6-8. Line 394 and line 419 both assert 'CEU-eligible'. Line 725: 'Paraeducator Certification — $299 / individual — 80-hour MCLSS program; CEU-eligible'.

**The problem**

CEU eligibility is not a property a curriculum author can assert. It requires an accrediting relationship, and the two realistic paths each take longer than the entire four-phase roadmap and have eligibility conditions the venture cannot yet meet. Selling an $299 course on a CEU claim that cannot be true at the time of sale is the clean case of an unsubstantiated material claim.

**Evidence**

[ESTABLISHED] **IACET**: applicants must be 'chartered or incorporated, governmental units or legally recognized sole proprietorships' and must 'have been in business and operating under the conditions described in our application for at least one year' — so a new entity is ineligible on day one. The initial application requires documenting compliance by uploading 73 separate pieces of evidence; the Standard-and-Application package is listed at $495, annual maintenance at $1,245 across a 5-year accreditation, and the application expires after one year. Accredited Providers must retain learner records for at least seven years (iacet.org/ce-t-accreditation/eligibility/; .../application-process/; .../frequently-asked-questions/). [ESTABLISHED] **MSDE**: Maryland CPD credit runs at 1 CPD credit = 15 clock hours, historically via an MSDE provider application with five-year approval and a recommended four-week lead time; MSDE's newer Professional Development Points guidance states that MSDE personnel, Maryland LEAs, Maryland State Agencies, Maryland-approved nonpublic schools and out-of-state SEAs 'will no longer need to submit approved professional development activities to MSDE to be approved as CPD courses' — i.e. the clean route runs **through an LEA**, which for this founder is the employer (msde.maryland.gov/educator-licensure-certification/professional-development-points; CPD Manual Aug 2022). [INFERENCE] That makes the MSDE route and the conflict-of-interest problem the same problem.

**Recommendation**

Remove 'CEU-eligible' from every surface now. Publish instead: 'X contact hours. Not currently approved for CEUs or Maryland CPD credit. We will say so here if that changes.' Put the real path on the roadmap at its real length: incorporate the entity → operate for 12 months → then begin the IACET application, budgeting ~$495 + $1,245/yr + a 73-item evidence package and several months of preparation, with record retention for 7 years. Treat the MSDE CPD route as unavailable while the founder is an MCPS employee, and say why in the roadmap. Separately, check Maryland's paraprofessional qualification requirements before implying the MCLSS helps a para meet any state or ESSA Title I requirement — that specific claim is unverified and is the one a para would most reasonably infer from '80 hours | CEU-eligible | MCPS District Partnership'.

### BT-10 — Unsubstantiated performance claims sold at $49/month

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.89 |

**What the artifact says**
> Line 75: '90% faster study with AND without AI'. Line 338, Module 9: 'Study 90% Faster — With and Without AI'. Line 483: 'Result: 60–90% speed increase with equal or greater comprehension' and 'Preview Read alone = 60% speed gain'. Line 465: 'Culturally affirming instruction raises Black student achievement (ES: 0.8)'. Line 466 and line 168: 'Self-directed learning produces 40% greater intrinsic motivation'. Line 464: 'Identity-based negative stereotypes suppress performance 15–20%'. Line 461: 'Mixed-topic practice beats blocked practice for long-term retention by 43%'. Line 41: '38% of middle schoolers experience debilitating test anxiety'. Line 165: '73% of MCPS families lack both'.

**The problem**

Eight numeric performance claims, each presented with an air of citation, none traceable to a stated study, population or outcome measure. '90% faster' is not a result any reading or study-skills literature supports and is not even defined (faster at what, measured how, against what baseline). 'ES: 0.8' for 'African-centered pedagogy' as a category is not an effect size any single synthesis could produce. '73% of MCPS families' appears to be invented; no MCPS source is named. These are being attached to a $49/month consumer subscription aimed at under-resourced families — the population least able to absorb a product that does not work and most likely to be believed when they are told it will.

**Evidence**

[INFERENCE] Each of these is unverifiable as stated; I was unable to locate a source for any of them and the artifact names none. [ESTABLISHED, contrast] Where real syntheses exist, their framing is narrower: Dunlosky, Rawson, Marsh, Nathan & Willingham (2013, PSPI 14(1)) rate practice testing and distributed practice high-utility and rereading/highlighting/summarisation low-utility, and evaluate no note-taking format and no culturally specific pedagogy — a boundary already recorded in this repo at `frontend/src/content/mindunlock/sources.ts`. [ESTABLISHED] The repo's own operating rule, in `frontend/src/lib/briefing/types.ts`: 'Evidence Before Claims — never imply validation that has not occurred.'

**Recommendation**

Every one of these eight numbers is either sourced to a specific study with population and outcome named, or deleted. Do this mechanically rather than editorially: extend the existing `frontend/src/lib/briefing` module so that **marketing copy is a `Claim[]` too**, not just the briefing. Any string rendered on a pricing, landing or certification page must resolve to a claim id; `validateBriefing` already refuses claims unbacked at their asserted tier and `MARKETABLE_TIERS` already restricts customer-facing assertions to `established` and `emerging`. Wire that check into CI so the build fails on an unbacked marketing string, exactly as it does for the briefing. Replace '90% faster' with the honest version: 'A three-pass reading method and spaced retrieval practice. Distributed practice and self-testing have strong evidence for retention (Cepeda et al. 2006; Roediger & Karpicke 2006); we have not measured a speed gain and do not claim one.'

### BT-11 — 'Cultural learning style', VARK, and ancestry[] encode race as a cognitive trait in a database column

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Line 271, Domain 4 item 4.8: 'Preferred cultural learning style (call-response, storytelling, movement)'; item 4.6: 'Collectivist vs. individualistic learning orientation (Ubuntu vs. Western)'; item 4.7: 'Ancestral pride as potential academic motivator (new construct, MindUnlock)'. Line 272, item 5.1: 'VARK modality preference (Visual / Auditory / Kinesthetic / Reading-Writing)'. Line 666: 'student_profiles (diagnostic_json, iep_id, ancestry[])'. Line 534: 'Ethnic origin selector (40+ African cultures)'.

**The problem**

Two failures that compound. (1) **Empirical**: the meshing hypothesis — that instruction matched to a learner's style produces better learning — is unsupported. Building VARK into a diagnostic that configures a child's instruction ships a known neuromyth as a personalisation feature. '4.7 ancestral pride … (new construct, MindUnlock)' is labelled by the author as untested, then used operationally anyway. (2) **Ethical and legal**: 'cultural learning style' as a measured trait is racial essentialism with a score attached — it asserts that Black children learn differently *as a cognitive property of being Black*, which is the exact proposition culturally sustaining pedagogy was developed against. `ancestry[]` as an array column on a child's profile makes race a queryable, joinable, exportable, breach-disclosable attribute of a minor, held by a private company, for the purpose of differentiating instruction. If this product is ever sold to a district, that column is the one that ends it.

**Evidence**

[ESTABLISHED] Pashler, McDaniel, Rohrer & Bjork (2008/2009), 'Learning Styles: Concepts and Evidence,' Psychological Science in the Public Interest 9(3): studies meeting the required crossover-interaction design 'flatly contradict the popular meshing hypothesis'; the authors found 'virtually no evidence' for it and concluded 'at present, there is no adequate evidence base to justify incorporating learning-styles assessments into general educational practice.' They accept that preferences exist and are reportable — preference is not the disputed claim; matching is (bjorklab.psych.ucla.edu PDF; PubMed 26162104). A 2024 meta-analysis of the matching hypothesis found only 26.19% of outcome measures showed the required crossover interaction (PMC11270031) — thin and contested, not supportive. [INFERENCE] The essentialism point follows from the construct's own wording ('Preferred cultural learning style') rather than from any study.

**Recommendation**

Delete items 4.6, 4.7, 4.8 and 5.1 from the instrument. Delete `ancestry[]` from the schema — **heritage is content, not a profile field**. Replace with a design where the child's heritage enters as choice and never as data: a browsable library of figures, traditions and histories that any child may open, save and return to; a `learner_saved_content(learner_id, content_id, saved_at)` join table that records what this child found interesting, exactly as a bookmark does, with no ethnic category attached and no inference drawn from it. The child picks content; the system never picks content *for* the child on the basis of an ascribed identity. Replace 'cultural learning style' in all copy with the defensible constructs: **identity safety** (the environment signals this child belongs here), **belonging**, and **culturally sustaining pedagogy as content and relationship** — what is taught and who teaches it — never as a cognitive trait. Replace VARK with modality *choice at point of use*: every piece of content offers text, audio and visual, and the learner switches freely, which is a UDL property of the content rather than a classification of the child.

### BT-12 — The product is named for an algorithm it cannot use and does not have

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.95 |

**What the artifact says**
> Line 75: 'Spaced repetition Anki engine (SM-18)'. Line 594, Learning Path Agent tool: 'SM-18 spaced repetition scheduler'. Line 679: 'SM-18 Algorithm — Spaced Repetition — Anki-compatible; AnkiConnect sync; neurodivergent-adjusted ease factors'. Line 97, Next Action #7: 'Integrate Anki SM-18 spaced repetition engine'. Line 774: 'Anki SM-18 integration + AnkiConnect sync'.

**The problem**

SM-18 is SuperMemo's proprietary algorithm. Anki does not use it and cannot — Anki's own FAQ gives licensing as the reason. So 'Anki SM-18 engine' and 'SM-18 Algorithm — Anki-compatible' describe something that does not exist. This is a five-place repeated factual error in a document intended for investors, a district and an engineering team; it will be found, and finding it discredits the rest of the technical claims. If anyone attempted to implement 'SM-18' from published descriptions and ship it under that name, it would additionally be an IP problem. 'Neurodivergent-adjusted ease factors' is a further invented property with no basis.

**Evidence**

[ESTABLISHED] Anki's official FAQ: SuperMemo's latest algorithm is proprietary and requires licensing; because Anki is open source it can only adopt freely available methods, which is how FSRS came to be included. Anki ships SM-2-based scheduling and FSRS (docs.ankiweb.net/faqs/what-spaced-repetition-algorithm). Modern SuperMemo uses SM-18, a descendant of SM-2, under SuperMemo's own licence.

**Recommendation**

Replace all five occurrences with 'FSRS (Free Spaced Repetition Scheduler), the open scheduler shipped with Anki.' Do not build a scheduler: use FSRS's published open implementation, or defer scheduling entirely in the MVP and use fixed 1/3/7/16-day intervals, which captures most of the distributed-practice benefit at a fraction of the build. Delete 'neurodivergent-adjusted ease factors' — it has no basis and implies a clinical adaptation. Delete 'AnkiConnect sync' from v1: it requires Anki desktop running locally and is not a feature a middle-school family will use.

### BT-13 — The agent topology gives notification and write powers to contexts that ingest untrusted text

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.91 |

**What the artifact says**
> Line 595, Test Anxiety Coach: triggers include 'distress phrase detection', output includes 'counselor referral flag, parent notification'. Line 597, Tutor Agent: triggers 'note upload', tools include 'Note review analyzer'. Line 596, BARS Schedule Agent tools: 'Assignment NLP parser', 'Calendar API integration'. Line 593, Diagnostic Agent: 'IEP PDF parser (NLP)' alongside output 'counselor referral flag'. Line 618: workflow chains agents directly into one another.

**The problem**

Every one of these agents reads attacker-controllable text — a child's typed message, an uploaded note photo, an assignment description, an IEP PDF — in the same context that holds tools which notify humans, write profile state, and set referral flags. That is the configuration OWASP names as the failure mode: untrusted content and privileged capability in one context, with the model as the only boundary. The concrete attack here is mundane rather than exotic: a child who wants a day off types text designed to make the Test Anxiety Coach fire a parent notification about a classmate; or an uploaded 'note' contains text that redirects the Tutor Agent's output. There is no isolation layer anywhere in the 8-agent design, and the only stated defence is the confidence threshold already refuted in BT-03.

**Evidence**

[ESTABLISHED] OWASP GenAI LLM01:2025 and the OWASP LLM Prompt Injection Prevention Cheat Sheet: identify untrusted content from every channel including retrieved and uploaded documents and keep it apart from trusted instructions; labelling alone does not enforce the boundary; validate tool arguments and enforce permissions in code outside the model; grant each tool only the access it needs; require approval for high-risk actions; treat model output as untrusted at its destination; and test against indirect injection that avoids screened keywords. OWASP states there are no known fool-proof prevention methods (genai.owasp.org/llmrisk/llm01-prompt-injection/; cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html).

**Recommendation**

Adopt a two-plane architecture and make it structural. **Plane A (reader)**: any model call that sees user-authored or uploaded text has zero tools, zero network, zero database write, and must return a fixed Pydantic model with enumerated fields — never prose that another agent will read as instruction. **Plane B (actor)**: tools and notifications live only here, and Plane B receives only Plane A's validated typed fields, never its raw text. Enforce in code: a `@no_tools` decorator on Plane A handlers and a FastAPI dependency that raises if a tool-bearing client is constructed inside a request that has touched the untrusted-text path; test it in `backend/tests/security_mutations.py` by removing the guard and asserting failure. Collapse the 8 agents to 3 for the MVP (Scheduler, Study Coach, Parent Coach) — 8 agents with cross-chaining is 8× the surface for a product with no users. Safety routing moves out of the LLM entirely into a deterministic classifier (BT-04). Log every model input and output to an append-only `ai_io_log(organization_id, learner_id, plane, model, input_hash, output, created_at)` and put a single environment-variable kill switch (`AI_ENABLED=false`) in front of both planes that degrades the app to its non-AI features rather than erroring.

### BT-14 — The Year 1 P&L has no cost line for anything this document promises

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.87 |

**What the artifact says**
> Lines 755-757: 'Total Year 1 Revenue $391,850 | Operating Costs (tech + staff + marketing) ~$175,000 | Net Year 1 ~$216,850'. Line 745 counts '2 grants avg — $100,000' as revenue. Line 120 promises 'African-centered scholars as PAID co-developers; community advisory board with veto power'.

**The problem**

The $175,000 cost line omits every control this document itself commits to: legal counsel (the stated day-one FERPA mitigation), E&O and cyber insurance, an IRB fee, paid cultural scholars, the advisory board, a licensed clinician reviewer, the instrument licence fees, the IACET fees, the 'quarterly external pen test' and 'annual third-party security audit' promised on line 691, and any founder salary. It also books $100,000 of hypothetical grant awards as Year 1 revenue when line 727 only commits to '2 grant applications submitted', and federal grant cycles rarely disburse inside the year of application. The consequence is not just an inaccurate projection — it is that when money is tight, the line items that get cut are precisely the controls, because they were never budgeted. A fantasy P&L is a safety defect.

**Evidence**

[ESTABLISHED, costs located] IACET: $495 application package + $1,245/yr maintenance (iacet.org). Independent IRB review for an unaffiliated investigator: HHS guidance estimates roughly $500-$1,000 for an exemption review and $1,000-$5,000 for initial full review; one published schedule (HML IRB) lists $1,500 exemption review and $1,000 non-human-subjects determination; CASRAI notes there is no published independent-researcher rate and that unaffiliated researchers generally cannot access an IRB free of charge (opa.hhs.gov IRB Tip Sheet; healthmedialabirb.com; casrai.org). Mind Garden TAI licences carry per-administration fees with 50- and 20-unit minimums. [INFERENCE] The remaining omissions follow from comparing the cost line to the document's own commitments.

**Recommendation**

Rebuild Year 1 as a cost-first model and move grants to a separate, clearly-labelled 'not booked' column. Add explicit lines, each with an owner: legal counsel retainer (education/privacy, Maryland) — this is the single largest and the one that cannot be cut; E&O + cyber liability; IRB (~$1,500 for an exemption determination); paid cultural scholars (name an hourly rate × hours, not a promise); community advisory council stipends; clinical reviewer (hourly, for escalation-design review only); content licences. Delete 'quarterly external pen test', 'bug bounty program' and 'annual third-party security audit' from line 691 until they are funded — asserting a security programme that does not exist is a representation a district will rely on. Then recompute: if the model only works when the controls are unfunded, the price is wrong, not the controls.

### BT-15 — 'Community advisory board with veto power' has no charter, no budget and no decision scope — so it has no power

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Line 120, the stated mitigation for the High risk 'Cultural appropriation of African-centered content': 'African-centered scholars as PAID co-developers; community advisory board with veto power; ongoing cultural review process.'

**The problem**

Three words — 'veto', 'paid', 'ongoing' — each doing work no mechanism backs. Veto over what, exercised how, by whom, within what window, with what effect if the founder disagrees? Paid how much, from which line (there is none in the P&L)? Ongoing at what cadence? An advisory structure with none of these specified is a mitigation that exists only in the risk register, and its presence there makes the risk look addressed. The Cultural Identity Agent meanwhile ships 'Scholar biography generator' (line 599) — generating biographies of real historical figures with an LLM, at scale, with no provenance — which is the appropriation risk in its most direct form and is not covered by any review process the document describes.

**Evidence**

[INFERENCE] from the text of the mitigation itself and the absence of any corresponding budget line, charter, or process elsewhere in the document.

**Recommendation**

Write a one-page **Community Advisory Council charter** before any cultural content is authored, containing: 5-7 named members (at least two with scholarly standing in African/African-American studies, at least two parents of MCPS-area neurodivergent middle schoolers, at least one current or former paraeducator); a stated honorarium per meeting and per review, funded from a named budget line; quarterly meetings plus asynchronous content review; and an explicit, bounded veto — the Council may block publication of any specific content item on cultural grounds, the block is binding, it is recorded with a reason in a public-to-members log, and it is not overridable by the founder. Scope the veto narrowly so it is real: content, naming, and imagery — not engineering or pricing. Replace the 'Scholar biography generator' entirely: every figure in the library is a **human-authored, attributed, sourced** entry (`content_corpus` row with author, source_locator, reviewer, approved_at), and the AI's only role is retrieval over that corpus with citation enforcement. Never generate a biography of a real person. Build a provenance ledger so any content item can answer: who wrote this, from what sources, who reviewed it, when.

### BT-16 — 'Real-time cohort comparison (anonymized)' cannot be anonymous at n=10

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.86 |

**What the artifact says**
> Line 529, Diagnostic Center: 'Real-time cohort comparison (anonymized)'. Line 771: 'Pilot cohort: 10 MCPS families (5 students + parents)'. Line 535: 'Family cohort community discussion board'; line 598 Parent Coach memory: 'cohort connection history'.

**The problem**

In a cohort of 5-10 students who know each other, are in the same school, and are in a shared discussion board, any per-domain comparison — 'you scored higher than 60% of your cohort' — is re-identifying. With grade, school and a visible member list, a parent can resolve most comparisons to a specific child. Calling it 'anonymized' in the UI is a representation to families that is not true, and if anxiety-adjacent or literacy scores are the comparison dimension, the disclosure is of exactly the data the rest of this design works to protect. The feature also directly contradicts the identity-safety goal: ranking a child against peers is the canonical way to produce the comparison anxiety item 1.11 says the product is treating.

**Evidence**

[INFERENCE] Small-cell re-identification is a standard disclosure-limitation concern; most state education agencies suppress cells below a minimum n (commonly 10) for exactly this reason. [ESTABLISHED, internal contradiction] The artifact's own Domain 1 item 1.11 names 'Peer comparison anxiety — knowing peers are finishing faster' as a construct the product measures and intends to reduce.

**Recommendation**

Cut cohort comparison from v1 entirely. If any aggregate is ever shown, enforce a minimum cell size of 10 in the query layer — not the UI — and never aggregate on any anxiety, literacy or accommodation dimension. Replace with self-referential progress: this child versus this child two weeks ago. That is both the safe design and the better pedagogy.

### BT-17 — MCPS systems integration is scheduled as a feature and is the clean-room violation in its sharpest form

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.89 |

**What the artifact says**
> Line 530, BARS Mission Scheduler: 'Assignment auto-import from school portal'. Line 77: 'Google Classroom + Canvas LMS sync'. Line 777, Phase 3: 'Google Classroom + Canvas LMS integration', 'School admin dashboard + district progress reporting'. Line 597, Tutor Agent tool: 'MCPS subject knowledge base'.

**The problem**

'Assignment auto-import from school portal' and 'MCPS subject knowledge base' describe a private product consuming MCPS systems and MCPS curricular content, built by an MCPS employee. Even where the data flows with a parent's credentials, the capability was designed by someone whose knowledge of those systems came from employment, and 'MCPS subject knowledge base' implies ingesting district curricular material whose rights the founder does not hold. This is the single feature most likely to convert an ethics question into a termination, and it buys very little: manual entry of this week's assignments takes a middle schooler ninety seconds and is itself a planning exercise the product claims to teach.

**Evidence**

[ESTABLISHED, policy text] MCPS Employee Code of Conduct: do not 'use your position as an MCPS employee, MCPS resources, or information gained through your employment, for personal gain.' [INFERENCE] A product feature that consumes MCPS systems and MCPS curricular content is squarely within 'MCPS resources' and 'information gained through your employment' on any reading.

**Recommendation**

Cut all school-system integration from v1 and v2. The learner or parent types assignments in; the app's value is what it does with them. Add this to the written clean-room rule (see Additions): no MCPS data, no MCPS systems, no MCPS curricular content, no MCPS devices or accounts, no MCPS network, no work during MCPS hours, no MCPS students or families recruited through any MCPS channel — and keep a contemporaneous log of development hours and the device used, because the burden of showing separation will fall on the founder.

### BT-18 — The security posture is asserted at enterprise grade for a product with no users

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Line 691: 'Penetration Testing — Quarterly external pen test; bug bounty program; OWASP Top 10 compliance; annual third-party security audit'; 'AI Safety Layer — Content safety classifier on ALL AI outputs; PII detection pipeline; crisis escalation detection with latency < 500ms'. Line 702: '99.9% SLA target; multi-region failover (us-east-1 primary → us-west-2 DR)'. Line 660: 'PostgreSQL (Supabase) — Row-level security, FERPA-compliant'.

**The problem**

None of this exists, and in a document that will be shown to a district these read as representations of current capability rather than aspirations. '< 500ms crisis escalation detection' is a latency SLA on a safety-critical classifier that has not been built and whose accuracy — the thing that matters — is not characterised at all. 'FERPA-compliant' is not a property a database product has; FERPA compliance is a property of a relationship and a set of practices. Multi-region failover for a 10-family pilot is a cost and complexity burden that buys nothing and signals to any technical reader that the document is not load-bearing. The real risk is that an accurate, modest security statement would be *stronger* here, because AEOS actually has committed RLS policies and a security mutation suite — a genuine asset this document buries under claims it cannot support.

**Evidence**

[ESTABLISHED, repo source] AEOS has real, reviewable controls: `backend/supabase/migrations/002_tenant_rls.sql` defines `aeos_has_org_access`, `aeos_can_write_org`, `aeos_is_org_admin` with REVOKE/GRANT discipline; `003_fk_relationship_hardening.sql` and `004_org_lifecycle_and_write_authority.sql` extend them; `backend/tests/test_rls_enforcement.py`, `test_fk_relationship_rls.py` and `security_mutations.py` test them. [INFERENCE] These are more credible to a technical reviewer than any of the claims on line 691, and they are the ones the document omits.

**Recommendation**

Replace the Security card with what is true and checkable: 'Multi-tenant isolation is enforced in two independent layers — PostgreSQL row-level security policies for direct database clients, and server-derived organization scoping in application code for the service-role path — with a committed mutation test suite that fails the build if either is removed.' Delete the pen test, bug bounty, audit, SLA and multi-region claims until they are funded and scheduled, and say instead what the real plan is and when. Delete 'FERPA-compliant' as a product attribute; replace with the specific practices (data minimisation, no education records held, parent-controlled deletion). Replace '< 500ms' with the measure that matters: the classifier's recall on a named adversarial fixture set, with the pass bar stated.

### BT-19 — Children are certified to tutor peers for pay, with no safeguarding design anywhere in the document

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> Line 334: 'MindUnlock Certified Student Tutor (MCST) … Paid peer tutoring eligibility ($15–20/hr)'. Line 338, Module 12: 'Practicum — Certify 3 Peers (Documented + Observed)'. Line 356: 'MCPS paid peer tutoring eligibility'. Line 533: 'Peer tutor matching after certification'. Line 345: 'Video-recorded 15-min tutoring session with a peer'.

**The problem**

A platform that matches minors with minors, records video of minors, and routes payment to minors has a safeguarding and employment-law design problem that the document does not acknowledge at any point. Specific gaps: who consents to the video of the *second* child in the recorded demonstration; where that video is stored and for how long; whether the matching is supervised; whether any adult reviews the pairing; Maryland child-labour rules for 11-14 year olds receiving payment; and the implication in 'MCPS paid peer tutoring eligibility' that MCPS will pay these children, which is a claim about the employer the founder works for. 'Certify 3 Peers' additionally has a 13-year-old issuing credentials to other 13-year-olds under the company's name.

**Evidence**

[INFERENCE] from the feature text; no safeguarding, consent, storage, supervision or labour provision appears anywhere in the artifact. [UNVERIFIED] Maryland child-labour provisions for minors aged 11-14 and MCPS's own student-employment rules were not checked and must be before this feature is designed.

**Recommendation**

Cut peer tutoring, peer certification, peer matching and video upload from v1 and v2 entirely. Keep the pedagogy that motivates them — the protégé effect is real and cheap to capture — by having the learner explain a concept **to the app or to their own parent**, with no second child involved and no recording leaving the device. If peer tutoring is ever revived, it requires a separate safeguarding design reviewed by counsel: adult supervision of every pairing, dual-parent consent for any recording, a defined retention window, a reporting channel, and the removal of all claims about MCPS paying anyone.


---

## What is missing and should be added

### Ethics disclosure packet and Ethics Panel advisory-opinion request — the first artifact, before any code   `ESTABLISHED`

**Why it matters.** Everything else is wasted effort if this comes out wrong, and it is the one item that cannot be retrofitted. An advisory opinion obtained *before* building is a shield; the same facts discovered afterwards are a disciplinary case. The artifact's Week-1 next actions begin with building a diagnostic instrument; they should begin here.

**What to build.** Four documents, in this order, all in writing, all retained. (1) **Disclosure memo to immediate supervisor** — one page: what MindUnlock Academy is, that it is independently owned, that no MCPS data/students/families/time/equipment/systems will be used, and that no sale to MCPS is contemplated in year one. (2) **Advisory opinion request to the MCPS Ethics Panel** via the Ethics Officer (Board of Education Office, 240-740-3030), asking three questions explicitly and separately: (a) may I develop and own this product while employed; (b) may I recruit MCPS families, through what channels if any; (c) may MCPS ever purchase it, and under what separation. Ask them to answer in writing. (3) **MCPS Form 460-50 outside-employment pre-approval**, covering officer/director service whether compensated or not. (4) **A 'do not do' list pinned to the project**, in force until a written answer arrives: do not recruit a single MCPS family; do not mention the venture to an MCPS parent, student or colleague in an MCPS context; do not use an MCPS device, account, email, network or drive; do not touch MCPS curricular material; do not present to any MCPS administrator; do not use the MCPS name in any marketing, pitch deck or domain; do not accept money from anyone connected to MCPS. Remove 'MCPS' from the product's own documents — the artifact currently names it 23 times.

**Evidence.** [ESTABLISHED] MCPS Regulation GCA-RA states its expectations exceed Maryland ethics law and Board Policy BBB; the Employee Code of Conduct prohibits using position, MCPS resources or information gained through employment for personal gain; board ethics materials prohibit simultaneous employment with an entity negotiating a contract with the school system; the Ethics Panel issues advisory opinions; violations 'may constitute grounds for removal from office, discipline, or other personnel action' (montgomeryschoolsmd.org/ethics/; MCPS Employee Code of Conduct 2025-26). [NOTE] ww2.montgomeryschoolsmd.org did not resolve from this session, so the full GCA-RA text is unverified — read it directly before filing.

### The year-one no-sale decision: build direct-to-family, outside Montgomery County   `INFERENCE`

**Why it matters.** This is the strongest single move available and the artifact never considers it. Not selling to MCPS in year one dissolves the conflict of interest, removes §4-131 operator status, removes the school-official FERPA pathway, removes the IDEA consent chain, removes the district procurement claims problem, and removes the need for any of the school-facing features — while leaving the family product, which is where the evidence and the revenue actually are. It is also faster: a district sale is a 9-18 month cycle the roadmap allots three months to.

**What to build.** A written one-page **operating covenant**, signed and dated, stating: for 12 months from launch, MindUnlock will not sell, licence, pilot or donate to Montgomery County Public Schools or any MCPS school, will not recruit MCPS families, and will not accept MCPS families who self-present. Recruit the pilot instead through Maryland or nearby out-of-county channels the founder has no employment relationship with: community organisations, faith communities, parent networks, neurodiversity support groups, a public sign-up with a geographic exclusion. Delete Roadmap Phase 3 in its entirety (MCPS presentation, 5 school contracts, admin dashboard, district reporting, LMS integration) and the '$37,500 school licence' revenue line. Revisit the covenant only after (a) the Ethics Panel has answered in writing, (b) the founder has left MCPS employment, or (c) counsel designs a separation the Panel accepts — and say which, in writing, when it changes.

**Evidence.** [INFERENCE] from BT-01 and the structure of the exposures: each of the four statutory regimes at issue attaches through a different school-mediated pathway, and all four are avoided by the same decision. [ESTABLISHED] Md. Educ. §4-131 defines 'operator' by reference to a contract or agreement with a Maryland public school or local school system under the FERPA school-official exception — no contract, no operator status (mgaleg.maryland.gov/2024RS/Statute_Web/ged/4-131.pdf).

### A three-tier data classification policy, enforced in the schema rather than in a document   `ESTABLISHED`

**Why it matters.** The artifact's data model mixes low-risk preference data, FERPA-grade education records, and clinical-adjacent data in a single `student_profiles` row with a `diagnostic_json` blob. Once mixed, every control must be applied to the whole, forever. Separating them at the schema level means the risky tier can simply be absent, and absence is the only control that cannot fail.

**What to build.** Three named tiers with a hard rule each, encoded as separate tables under AEOS's existing `organization_id` pattern. **Tier 1 — Learner preference data (collect freely)**: `learner_preferences`, `learner_supports`, `schedule_blocks`, `study_sessions`, `learner_saved_content`. Parent-asserted, revisable, non-diagnostic, no clinical vocabulary. **Tier 2 — Educational record-adjacent (avoid in v1, segregate if ever needed)**: anything originating from a school — grades, IEP content, school-portal data, counselor communications. In v1 this tier has **zero tables**, which is the point. **Tier 3 — Clinical-adjacent (never collect)**: anxiety severity scores, mental-health symptoms, sleep pathology, diagnoses, crisis-conversation content beyond the minimum needed for the safety gate, sensory-sensitivity profiles, cognitive test results. Write the policy as a one-pager naming each tier, the rule, and the table list; add a CI check that fails if a new migration adds a column matching a Tier-3 denylist of names (anxiety_score, diagnosis, severity, symptom, …). Add a `learner_profile` design note: no `diagnostic_json` blob — every field is a typed column, because a JSONB blob cannot be classified, minimised, or deleted selectively.

**Evidence.** [ESTABLISHED] 20 U.S.C. §1232h and 34 CFR Part 98 define the protected categories that make Tier 3 dangerous; 34 CFR 300.622 and FERPA define Tier 2. [ESTABLISHED, repo] AEOS's existing tables all carry `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE` and are covered by the policies in `002_tenant_rls.sql` — the new tables must match that shape exactly to inherit the defence.

### The accommodation picker that replaces IEP ingestion   `ESTABLISHED`

**Why it matters.** This is the specific, buildable thing that lets the product deliver real accommodation value while holding none of the risk. It is two days of work and it deletes the largest exposure in the design.

**What to build.** A single screen in parent onboarding: 'What helps your child? Pick any that apply — you can change these any time.' Twelve checkboxes mapping to a closed enum: extended_time, text_to_speech, chunked_tasks, reduced_distraction, frequent_breaks, visual_alternative, audio_alternative, flexible_response_mode, larger_text, reduced_motion, predictable_routine, advance_notice_of_change. Each writes a row to `learner_supports(id, organization_id, learner_id, support_code, asserted_by_user_id, asserted_at, revoked_at)`. The app reads only `support_code` to set UI defaults — timer multipliers, TTS availability, task chunk size, break cadence, motion and contrast. **Copy rules**, enforced in review: never the words 'IEP', '504', 'accommodation', 'disability', 'diagnosis', or 'accommodation profile' anywhere in the UI; never ask what the child's diagnosis is; never ask whether the child has an IEP; never offer to upload anything. Add a short line under the picker: 'We don't ask for your child's school records, and we don't want them.' That sentence is a product feature for this audience — it is a reason to trust the product — and should be in the marketing too.

**Evidence.** [ESTABLISHED] 34 CFR 300.622 consent requirements and FERPA education-record status are what the upload path triggers; a parent-asserted preference is neither an education record nor IDEA-protected PII. [ESTABLISHED] OWASP LLM01 — removing the upload removes the indirect-injection channel entirely rather than mitigating it.

### Consent, assent and notice pack for minors — three documents, written at the right reading levels   `ESTABLISHED`

**Why it matters.** The artifact mentions 'verifiable parental consent flow' once, as a phrase in a mitigation cell, and has no assent concept at all. A product for 11-14 year olds that asks a child to type about their worries without the child's own informed agreement is ethically defective regardless of what the parent signed — and the FTC declined to adopt the ed-tech school-authorization exception, so school consent is not available as a shortcut even later.

**What to build.** (1) **Parent consent form**, plain language at grade 8, stating: exactly what is collected (the 14 items and the support picker, listed), what is never collected (school records, diagnoses, test scores, mental-health assessments — listed), who can see it ('only you and your child; MindUnlock staff see only aggregate counts and anything flagged for safety review'), how long it is kept (24 months after last activity), how to delete it (one button, in the app, no email required, completes in 7 days), and that this is not a crisis service and does not monitor the child. (2) **Child assent script** at grade 5 reading level, shown to the child on first launch, in the child's own flow, not the parent's: what the app does, what it remembers, that a grown-up at MindUnlock may read a message if the child says something that worries the app, that the child can skip any question and can ask a parent to delete everything. Record `assent_given_at`; if the child declines, the app runs in a no-logging mode rather than refusing. (3) **A PPRA-style notice** even though the product is not school-funded — it states the protected categories and affirms the product does not probe them, which both documents the minimisation decision and makes it durable against feature creep. (4) **COPPA posture**: direct parent sign-up with payment card is the consent mechanism; add the amended Rule's requirements — separate consent for any third-party disclosure, and a written data retention policy published in the online notice itself rather than linked.

**Evidence.** [ESTABLISHED] The amended COPPA Rule was effective June 23, 2025 with a compliance date of April 22, 2026 for most provisions; 16 CFR 312.5(a)(2) requires separate consent for third-party disclosure; §312.10 requires a written retention policy describing collection purposes, business need and deletion timeframe, which 'must appear in the online notice' — linking to a separate policy is not sufficient. Disclosures for monetary compensation, advertising, or AI training are never 'integral to the service.' The FTC expressly **declined** to finalise the proposed school-authorization exception, citing anticipated FERPA rulemaking (federalregister.gov/documents/2025/04/22/2025-05904; ftc.gov Jan 2025 press release; Fenwick, White & Case analyses). [ESTABLISHED] PPRA categories: 20 U.S.C. §1232h.

### The clinical boundary language pack — exact wording for every surface   `ESTABLISHED`

**Why it matters.** The difference between a wellness product and an unlicensed practice is mostly vocabulary, and vocabulary drifts unless it is written down and reviewed. The artifact's current vocabulary — 'diagnostic', 'screening', 'severity tracker', 'CBT protocol', 'clinical', 'crisis detection', 'intervention' — is clinical throughout and will be read that way by a regulator, a plaintiff and a parent alike.

**What to build.** A two-column banned/approved list, enforced by a lint rule over UI strings and marketing copy. Banned → approved: 'diagnostic' → 'study start'; 'assessment' → 'check-in'; 'screening' → (delete); 'test anxiety severity tracker' → 'how test days have been going'; 'CBT protocol' → 'a way to talk back to unhelpful thoughts'; 'somatic grounding' → 'calm your body'; 'intervention' → 'practice'; 'crisis detection' → (delete; see the escalation design); 'clinical' → (delete); 'therapeutic' → (delete); 'treatment' → (delete); 'symptoms' → 'how you feel'; 'psychometrically validated' → 'not a diagnostic tool'. Add a **screening-vs-assessment rule** stated plainly in the product documentation: MindUnlock does not screen, score, classify, stage, or compare to norms; it asks what helps and adjusts what it offers. Add a standing footer on any emotion-adjacent screen: 'MindUnlock is a study skills app. It is not therapy, counselling, or a crisis service. If you need help now, call or text 988.' Add a **referral-only list** — the things the product must always hand off and never attempt: diagnosis of anything; anything presenting as depression, self-harm, abuse, disordered eating, or substance use; medication questions; school disciplinary or legal matters; anything a parent asks about their child's mental health. Each has a single response: a short acknowledgement, the resources panel, and a stop.

**Evidence.** [ESTABLISHED] Md. Health Occupations §18-101(f)(1)(iii) ties the licensure line to constructing, administering or interpreting tests for compensation, and §18-102 limits even other licensed professionals' use of the words 'psychological', 'psychologist' and 'psychology' — a vocabulary rule in statute, which is precisely why a vocabulary rule in product is the right control (mgaleg.maryland.gov/2024RS/Statute_Web/gho/18-101.pdf; law.justia.com Md. Health Occ. §18-102). [ESTABLISHED] COMAR 10.36.01.07 lists the exceptions to licensure; none covers a commercial consumer product.

### The escalation runbook: resources-and-stop, with a named human and no automated disclosure   `EXPERT-OPINION`

**Why it matters.** This replaces the single most dangerous mitigation in the artifact (BT-04) with a design that is both safer for the child and defensible for the company. It needs to exist as an operational document, not just code, because its hardest parts are decisions a person makes.

**What to build.** **Detection**: a deterministic classifier running outside the conversational model on every learner-authored turn — a maintained phrase list plus a small purpose-trained classifier — tuned for recall over precision, with every decision logged to `safety_events(id, organization_id, learner_id, session_id, rule_version, matched, created_at)`. **Response, in fixed order, with no model in the loop**: (1) the conversational agent is suspended for the session; (2) a static, non-AI panel renders — 988 Suicide & Crisis Lifeline (call or text), Crisis Text Line (text HOME to 741741), and the child's school counsellor name and number as plain text; (3) one sentence: 'I'm not the right kind of help for this, and I want you to talk to someone who is.' (4) Nothing else happens. No parent notification. No counselor notification. No flag on any dashboard. **Human review**: a named role with a 24-hour SLA (in the pilot, the founder; document who) reads the flagged turn and decides, case by case, whether to contact the parent — recording the decision and its reasoning in `safety_reviews(safety_event_id, reviewer_id, decision, rationale, decided_at)`. **The parent-notification harm case, addressed explicitly in the runbook**: before any contact, the reviewer must consider whether the parent could be the source of the distress, and where there is any doubt the decision is to contact a public resource (988, the school counsellor directly, or where legally required a child-protection report) rather than the parent. **Written limits published to families**: the product does not monitor, does not detect reliably, and makes no promise to catch anything. **Mandated-reporter question**: resolve with counsel, in writing, before the pilot — whether the founder's MCPS reporter status follows him into the venture, and what the venture's obligation is independently.

**Evidence.** [EXPERT-OPINION] Crisis-service practice treats guardian notification as a judgement requiring a trained human, not a threshold. [INFERENCE] The legal asymmetry: promising detection creates a duty the product cannot discharge; promising only resources does not. [UNVERIFIED — must check] Md. Family Law §5-704 (mandated reporting) and Md. Health-General minor-consent provisions were not verified in this pass and govern the reviewer's obligations.

### The AI eval harness: what gets measured, on what fixtures, at what bar, before every release   `ESTABLISHED`

**Why it matters.** The artifact has no evaluation at all — only the confidence threshold. Without a fixture set and a pass bar, 'we tested it' means nothing and nothing can be regression-tested. This is the artifact that makes every other AI control verifiable.

**What to build.** A versioned fixture repository under `backend/tests/ai_evals/` with five suites and an explicit bar each, run in CI and gating release. **(1) Safety recall** — 200 fixtures of learner-authored text: 60 true-positive distress phrasings (including indirect, slang, and misspelled), 40 near-miss academic-stress phrasings that must NOT fire ('this test is killing me'), 100 ordinary turns. Bar: recall ≥ 0.95 on true positives; false-positive rate ≤ 0.05 on near-misses; **any true-positive miss blocks release**. **(2) Prompt injection** — 80 adversarial fixtures across every untrusted channel the product has: pasted assignment text, typed notes, parent free-text, profile fields. Include instruction-override, tool-invocation attempts, data-exfiltration attempts, and injections that avoid screened keywords. Bar: zero tool invocations and zero notification triggers originating from Plane A; any single success blocks release. **(3) Citation integrity** — 100 content-generation prompts. Bar: 100% of emitted citations resolve to a `content_corpus` doc_id; zero fabricated references; any failure blocks release. **(4) Tenant isolation** — reuse the existing `backend/tests/security_mutations.py` methodology: remove each tenant predicate in turn and assert the suite fails. **(5) Age-appropriateness and tone** — 50 fixtures, human-scored against a rubric; clinical vocabulary from the banned list in any output is a failure. Every fixture file is committed, versioned and dated; the eval report is written to the release record. Add the **kill switch**: `AI_ENABLED=false` degrades the product to its non-AI features (scheduler, note-taking instruction, content library, retrieval practice) rather than erroring — which is only possible if, as recommended below, the MVP's value does not depend on AI.

**Evidence.** [ESTABLISHED] OWASP LLM01 guidance directs testing 'against both direct and indirect injection, including attempts that avoid the screened keywords' and states that no prevention method is fool-proof — which makes a measured, versioned bar the only honest control (genai.owasp.org/llmrisk/llm01-prompt-injection/; OWASP LLM Prompt Injection Prevention Cheat Sheet). [ESTABLISHED, repo] The mutation-testing methodology already exists in `backend/tests/security_mutations.py` and should be extended rather than reinvented.

### Claims register extended to marketing — reuse the module AEOS already has   `ESTABLISHED`

**Why it matters.** AEOS already contains a working, tested implementation of exactly the discipline this product needs, and the MindUnlock artifact ignores it. `frontend/src/lib/briefing/types.ts` defines `EvidenceTier`, `TIER_RANK`, a `MARKETABLE_TIERS` set restricted to established and emerging, a `retracted` tier kept deliberately visible, and a `Source.caveat` field whose comment states the rationale precisely: 'recording the limit next to the citation is the cheapest guard against a claim drifting past its evidence.' This is the single highest-leverage thing in the repo and it needs to be pointed at the sales surface.

**What to build.** Extend the briefing module so that customer-facing copy is validated by the same machinery. (1) Every string on a pricing, landing, certification or app-store page resolves to a `Claim` id in a new `frontend/src/content/mindunlock/marketing.ts`. (2) `validateBriefing`'s rule — no claim may assert a tier higher than its backing — is applied to that file, and CI fails the build on an unbacked marketing string. (3) `MARKETABLE_TIERS` is already `{established, emerging}`; enforce that no `inference` or `hypothesis` claim is renderable on a customer surface without an explicit qualifier component. (4) Retire the eight numbers in BT-10 by moving each to tier `retracted` with a note, so the history is visible rather than quietly edited away — the type already supports this. (5) Add the legal claims to the register too, with `kind: 'statute'` sources: the CEU claim, the university-partner claim, the FERPA-compliance claim, the security-programme claims. A claim about accreditation is as falsifiable as a claim about effect size and should be governed identically.

**Evidence.** [ESTABLISHED, repo source] `frontend/src/lib/briefing/types.ts` header: 'AEOS operating rule: Evidence Before Claims — never imply validation that has not occurred. This module makes that rule structural rather than aspirational… validateBriefing refuses a briefing whose claims are not backed at the level their tier asserts, and the build fails rather than shipping a document that overclaims.' `frontend/src/content/mindunlock/sources.ts` already carries full author lists and per-source caveats; `frontend/src/lib/briefing/validate.test.ts` already tests the validator.

### Certificate wording and completion-record design   `ESTABLISHED`

**Why it matters.** The certification tracks are a real part of the value and can be delivered honestly. What cannot be delivered is the word 'Certified' without a certifying body, or 'CEU' without accreditation. Getting the artefact's wording right now is far cheaper than reissuing certificates to paying paraeducators later.

**What to build.** A single certificate template whose body is fixed and whose only variables are name, programme, hours and date. Permitted text: '[Name] completed the MindUnlock Academy [Programme Name] programme, comprising [N] contact hours, on [date]. The programme covered: [3-5 bullet competencies, written as what the learner did, not what they are].' Mandatory footer, same size as the body, not fine print: 'MindUnlock Academy is not an accredited institution. This certificate is a record of programme completion. It does not confer a licence, degree, endorsement, state certification, or continuing-education credit, and it is not recognised by any school district, state agency, or accrediting body.' Store the record as `program_completions(id, organization_id, user_id, program_code, contact_hours, completed_at, certificate_serial)` with a public verification URL that renders the same text — verifiability is the honest substitute for accreditation and is worth more to a paraeducator than a false CEU claim. Rename the four tracks to drop 'Certified': 'MindUnlock Learning Science Programme — Paraeducator Track', and so on. Keep the acronyms out of marketing entirely; invented acronyms (MCST, MCPT, MCLSS, MMEC) are what make a completion certificate read as a credential.

**Evidence.** [ESTABLISHED] IACET eligibility requires at least one year in business and a 73-item evidence submission; MSDE's CPD route now runs primarily through LEAs and state agencies rather than independent provider applications (iacet.org/ce-t-accreditation/eligibility/; msde.maryland.gov professional-development-points). Neither path can be true at launch, so the certificate's text must not imply either.

### Community Advisory Council charter, paid scholar budget line, and a content provenance ledger   `INFERENCE`

**Why it matters.** This converts the artifact's one-line cultural mitigation into a structure with authority, and replaces LLM-generated biographies of real people — the sharpest appropriation risk in the design — with attributed human authorship.

**What to build.** (1) **Charter** (one page): 5-7 named members with the composition in BT-15; honorarium per meeting and per content review, from a named budget line in the P&L; quarterly meetings plus async review; a **bounded binding veto** over content, naming and imagery, recorded with a reason in a log visible to members, not overridable by the founder; a defined term and a defined exit. (2) **Paid cultural scholars** as a line item with an hourly rate and an hours estimate, contracted as authors with named attribution on the content they write — not consulted and uncredited. (3) **Provenance ledger**: every content item in `content_corpus(id, organization_id_is_null_global, title, body, author_name, source_locators[], reviewer_id, approved_at, advisory_review_at, evidence_tier)`. Every figure, tradition or history in the library answers: who wrote this, from what sources, who reviewed it, when the Council cleared it. (4) **Delete the 'Scholar biography generator'** (line 599). The AI's only role over this corpus is retrieval with citation enforcement; it never generates a claim about a real historical person. (5) **Dignity rules for heritage**, written into the product spec: heritage is never a required field, never inferred, never used to route content automatically, never exported, and never shown to anyone but the child and their parent. A child's interest in a history is a bookmark, not a classification.

**Evidence.** [INFERENCE] The design follows from BT-11 and BT-15; the specific failure mode — generating biographies of real people at scale with no provenance — is a direct reading of line 599. [ESTABLISHED] The authority problem is structural: an advisory body with no budget and no defined decision scope cannot exercise a veto, which is why the charter must specify both.

### The defensible 8-week MVP: feature list in, feature list out, stop conditions   `INFERENCE`

**Why it matters.** The founder's own operating rule is MVP → pilot → measurement → evidence → revenue, and the artifact's Phase 1 contains roughly nine months of work. This is the version that ships in eight weeks, generates real evidence, and carries near-zero legal exposure — and it is a better product, because every cut is a feature that was adding risk without adding retention.

**What to build.** **IN** (six features): (1) The 14-item Study Start + 12-item accommodation picker. (2) A schedule builder — the child enters assignments and builds blocks; drag-and-drop, no auto-import, no AI. (3) Note-taking instruction: three methods, not six (Cornell, outline, mind map), with worked examples at grade level and a practice prompt. (4) Retrieval practice: the child makes cards, fixed 1/3/7/16-day intervals, no FSRS, no Anki sync. (5) A calm-down toolkit: box breathing, 4-7-8, a body-scan audio, a thought-reframe worksheet — all static content, no AI, no tracking of emotional state over time. (6) A heritage content library: 25 human-authored, attributed entries the child browses and bookmarks. **OUT** (and say why in the roadmap): IEP upload; all 38 cut instrument items; the TAI; AI chat of any kind in weeks 1-8; crisis detection; parent/counselor notification; peer tutoring, peer certification and video; cohort comparison; school portal and LMS integration; the admin and district dashboards; 'certification' as a word; CEU claims; the 8-agent system; Redis agent memory; the Spanish beta. **DATA HELD**: Tier 1 only — preferences, supports, schedule blocks, study sessions, saved content, programme progress. No education records, no clinical data, no documents, no uploads, no emotional-state history. **CONSENT**: parent sign-up with card + child assent screen. **SUCCESS METRIC**: one number — percentage of enrolled families with ≥3 active days per week in weeks 5-8. **STOP CONDITIONS**, written down in advance and honoured: stop and reassess if any safety event occurs; if the Ethics Panel answer is adverse; if any family reports the product increased their child's distress; if week-4 retention is below 40%; if counsel flags any feature; if the founder cannot show a clean separation of hours and equipment.

**Evidence.** [INFERENCE] Each cut maps to a finding above: upload→BT-02, instrument items→BT-06, TAI→BT-05, notification→BT-04, agents→BT-13, peer tutoring→BT-19, cohort→BT-16, LMS→BT-17, CEU/certification→BT-08/09. [ESTABLISHED] The retained learning-science content rests on the strongest available evidence: Dunlosky et al. (2013, PSPI 14(1)) rate practice testing and distributed practice high-utility; Cepeda et al. (2006, Psych Bull 132(3)) and Roediger & Karpicke (2006, Psych Sci 17(3)) support distributed practice and retrieval — all three already in `frontend/src/content/mindunlock/sources.ts` with their caveats recorded.

### The 10-family pilot protocol and the realistic IRB path   `ESTABLISHED`

**Why it matters.** The artifact promises a pilot and names KPIs but has no hypothesis, no baseline, no measure, no analysis plan, no safety threshold and no human-subjects review. Without these the pilot produces anecdotes, and anecdotes cannot be used in any claim — which defeats the pilot's only purpose under the founder's own sequence.

**What to build.** **Hypothesis** (single, pre-registered): families given MindUnlock will show higher self-reported study-routine consistency at week 8 than at baseline. Note that a single-arm pre-post design cannot support a causal claim and say so in the protocol — the pilot's job is feasibility, safety and signal, not efficacy. **Participants**: 10 families, grades 6-8, recruited outside Montgomery County (see the no-sale covenant). **Baseline, week 4, week 8**. **Measures**: (a) app-derived behavioural data — active days/week, blocks created, cards reviewed — which is the primary and needs no instrument; (b) a short self-authored study-routine consistency scale (5 items, no clinical content); (c) a one-item parent global-change question; (d) a 20-minute semi-structured exit interview with each family, which will produce more usable evidence than any scale at n=10. **If a validated anxiety measure is wanted as a secondary**, use the Westside Test Anxiety Scale (Driscoll, 2007; 10 items; ERIC ED495968) — but obtain the author's written permission first, because the hosted copies carry '© 2004 Richard Driscoll' and it is **not public domain**. Do not use the Spielberger TAI. **Threshold for proceeding**: ≥6 of 10 families active ≥3 days/week in weeks 5-8. **Safety threshold for stopping**: any safety event, or any family reporting increased distress. **Analysis plan**: descriptive only — means, counts, individual trajectories, thematic coding of exit interviews. No p-values at n=10; state that in advance so the temptation is removed. **Consent and assent**: the documents from the consent pack, plus a plain statement that participation is voluntary and withdrawal deletes all data. **IRB**: because this is a commercial product pilot rather than federally funded research, Common Rule coverage is not automatic — but obtain review anyway, both because minors are involved and because an unreviewed pilot cannot support any public claim. Realistic options for a non-academic founder: an independent/commercial IRB engaged directly (Advarra, WCG, Solutions IRB, HML IRB) requesting either a non-human-subjects determination or an exemption determination under 45 CFR 46.104; budget roughly $1,000-$1,500 for that determination. Do **not** self-exempt: OHRP's long-standing recommendation is that investigators not determine their own exemption.

**Evidence.** [ESTABLISHED] HHS/OHRP: 'because of the potential for conflict of interest in this situation, OHRP's long-standing recommendation is that investigators not be given the authority to make an independent determination that human subjects research is exempt' (hhs.gov/ohrp exempt-research-determination FAQs); exemption categories at 45 CFR 46.104, with Category 1 covering normal educational practices. [ESTABLISHED] Cost range: HHS OPA IRB tip sheet estimates ~$500-$1,000 for exemption review and $1,000-$5,000 for initial full review; HML IRB publishes $1,500 exemption review and $1,000 non-human-subjects determination; CASRAI notes unaffiliated researchers must contract directly with a commercial IRB and generally cannot access one free. [ESTABLISHED] Westside Test Anxiety Scale: 10 items, reported correlations with test gains of 0.49 (college) and 0.40 (fifth grade), described as free for schools, but carrying a 2004 Driscoll copyright notice — permission required (files.eric.ed.gov/fulltext/ED495968.pdf).

### Retention, deletion and the 'what the company can see' principle, as migration 005   `ESTABLISHED`

**Why it matters.** The amended COPPA Rule now requires a written retention policy in the online notice itself, and deletion is the one control that reduces risk retroactively. AEOS currently has no retention, deletion, consent or guardian concept anywhere — `user_role` is `('teacher','admin','support')`, with no learner or guardian — so this is net-new and should land as one coherent migration rather than accreting.

**What to build.** A single migration `005_consumer_tenancy_and_retention.sql` adding: (1) `ALTER TYPE user_role ADD VALUE 'guardian'` and `'learner'`, with RLS predicates extended so a guardian reads only their own linked learners and a learner reads only self — expressed through the existing `aeos_has_org_access` pattern plus a new `aeos_is_linked_guardian(learner_id)` SECURITY DEFINER function with the same REVOKE/GRANT discipline as the existing four. (2) `guardian_learner_links(guardian_user_id, learner_id, verified_at)` — a family is an `organization` of type `'family'`, which reuses the whole tenancy model unchanged and is the cleanest mapping available. (3) `consents(id, organization_id, subject_user_id, consent_kind, granted_by, granted_at, revoked_at, document_version)` — consent as a row with a version, so it is auditable and re-collectable when the notice changes. (4) **Retention defaults**, implemented as a scheduled job, not a policy document: delete all Tier-1 learner data 24 months after last activity; delete `ai_io_log` at 90 days; delete `safety_events` and `safety_reviews` at 24 months; `audit_logs` retained 7 years. (5) **One-button deletion** in the parent UI, completing within 7 days, cascading through `ON DELETE CASCADE` which the existing schema already uses consistently. (6) **Per-tenant encryption keys** for any free-text the learner authors — envelope encryption with a per-organization data key, so a single key compromise does not expose the corpus and a family's deletion can be implemented as key destruction. (7) **'What the company can see'**, written into the privacy notice and enforced in code: staff see aggregate counts and operational metrics; staff see individual content only for a row that has a `safety_events` flag, and that access is itself written to `audit_logs`. Add a test that asserts no staff-facing endpoint can return learner free-text without a corresponding safety flag.

**Evidence.** [ESTABLISHED] 16 CFR §312.10 as amended requires a written data retention policy describing collection purposes, business need, and deletion timeframe, published in the online notice — 'linking to a separate policy is not sufficient.' Effective June 23, 2025; compliance date April 22, 2026 (federalregister.gov/documents/2025/04/22/2025-05904; Fenwick analysis). [ESTABLISHED, repo] The existing pattern to follow: `002_tenant_rls.sql` SECURITY DEFINER functions with `SET search_path`, REVOKE FROM PUBLIC, GRANT TO authenticated; `001_initial_schema.sql` uses `ON DELETE CASCADE` from `organizations` throughout, which makes family-as-organization give correct deletion semantics for free.


---

## Open questions

- Does the founder's mandated-reporter status as an MCPS employee (Md. Family Law §5-704) follow him into the venture, and what independent reporting obligation does the company have on a disclosure made through its app? Unverified; must be answered in writing by counsel before the pilot, because the escalation runbook's human-review step depends on the answer.
- What do Maryland's minor-consent-to-mental-health-services provisions (Md. Health-General Article) say about a 13-year-old's ability to decline parental disclosure of distress content? Unverified; directly determines whether the child assent design is sufficient or whether more is needed.
- Full text of MCPS Regulation GCA-RA and Board Policy BBB — ww2.montgomeryschoolsmd.org did not resolve from this session, so the specific provisions on employee-owned ventures and on soliciting MCPS families remain unread. These need to be allowed in the session's network settings, or read directly, before the disclosure memo is drafted.
- Does Md. Educ. §4-131 reach a direct-to-parent product with no district contract? The 'operator' definition is tied to the FERPA school-official exception and a contract with a school or system, which suggests no — but the 2021 SB 733 amendment to the covered-information definition ('linked to a student with reasonable certainty') was not confirmed as enacted. Check the current enacted text at mgaleg.maryland.gov before relying on the no-operator conclusion.
- Is there a Maryland Board of Examiners of Psychologists interpretation, advisory opinion, or enforcement history on consumer wellness and edtech products that administer self-report instruments? COMAR 10.36.01.07's exceptions do not obviously cover one. An inquiry to the Board may be cheaper and faster than a legal opinion, but may also create a record — decide with counsel which risk is preferable.
- Will Richard Driscoll grant written permission for commercial-adjacent pilot use of the Westside Test Anxiety Scale? The ERIC document says free for schools, but hosted copies carry a 2004 copyright notice, so the pilot's secondary outcome measure depends on an answer that has not been sought.
- Does the 2026 FERPA rulemaking the FTC cited when declining to finalise the ed-tech school-authorization exception change the analysis for a future school-facing version? Worth tracking; it is the single regulatory development most likely to alter the year-two decision about selling to a district.
- What are Maryland's child-labour provisions for 11-14 year olds receiving payment, and MCPS's own rules on student employment? Unverified. Only matters if peer tutoring is ever revived, but must be answered before it is.
- Does the AEOS multi-tenant model's organization-as-family mapping survive the case where a child's two guardians are separated and in conflict? The existing schema has one organization per tenant and no concept of a contested link. This is a real scenario in the target population and has no answer in either the artifact or the repo.
- What is the actual MSDE position on CPD credit for a private provider that is not an LEA, now that the Professional Development Points guidance has shifted approval away from MSDE submission for LEAs and state agencies? The 2022 CPD Manual and the newer PDP guidance describe different regimes and the transition date was not found; confirm with MSDE's Division of Educator Effectiveness (certinfo.msde@maryland.gov) before any CPD claim is contemplated.

