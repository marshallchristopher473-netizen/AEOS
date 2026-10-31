# Red team

> Hostile review: every way this product gets the founder sued, fired, investigated or breached — and every way it harms a child.

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

The single most important finding is this: the artifact is a 859-line plan to sell a psychological-assessment product to the founder's own employer, using the founder's own employer's children as the pilot, and it does not contain the word "ethics," "conflict," "disclosure," or "recusal" anywhere in a self-regarding sense. Tab 1's risk register lists six risks — FERPA/COPPA, hallucination, crisis, cultural appropriation, dropout, UI complexity. It does not list the founder. That omission is the product's highest-probability catastrophic failure, and it is also the cheapest to fix.

Stack the facts as an MCPS Ethics Panel or an investigative reporter would. The founder is an MCPS employee (mcpsmd.net). The named customer is MCPS ("5 school contracts signed ($37,500 ARR)", "MCPS district leadership presentation delivered"). The pilot is "10 MCPS families." The exam content uses "real MCPS student scenarios." The tutor agent runs on an "MCPS subject knowledge base." The certification promises "MCPS paid peer tutoring eligibility" and an "MCPS District Partnership." That is a public employee monetizing position, access, data, and relationships. Under Md. Code, Gen. Prov. §5-506, intentionally using one's position for private gain is a prohibition, not a disclosure item. This is not a compliance checkbox to be resolved at Week 12; it is a precondition to Week 1.

Second: the product performs psychological assessment on minors. A "52-domain psychometric engine," a "Spielberger TAI scorer," an "anxiety severity tracker," a "counselor referral flag," and a "crisis detection layer" are, taken together, the practice of psychology for compensation as Maryland defines it, built by someone with no stated license. The Spielberger TAI is separately a commercially licensed, copyrighted instrument (© 1980 Spielberger, distributed by Mind Garden under licenses that forbid individual feedback under the research license). Advertising crisis detection and then missing a crisis creates a negligent-undertaking duty the product cannot discharge at a "< 500ms" latency promise.

Third: the privacy architecture is not merely incomplete — it is internally contradictory. IDEA Part B confidentiality (34 CFR 300.610–300.627), which governs the IEP PDFs the product ingests, is never mentioned once. PPRA is never mentioned once, despite the instrument probing mental health, family income, religion, and critical appraisals of family. And the product cannot be both a FERPA school official under district direct control and a direct-to-family operator of the same record.

Everything else below is downstream of these three.

---

## Findings

### RT-01 — Founder is an MCPS employee selling to MCPS — use of public position for private gain is a hard prohibition, not a disclosure item

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Roadmap Phase 3: "MCPS district leadership presentation delivered", "5 school contracts signed ($37,500 ARR)"; Business Model: "School / District License ... $2,500–$15,000/school/yr ... MCPS pilot target"; artifact contains zero references to ethics disclosure, recusal, or outside-employment approval.

**The problem**

The founder's email domain is mcpsmd.net. The artifact's entire go-to-market is the founder's own employer. An MCPS employee personally presenting a for-profit product to MCPS district leadership, and personally closing school contracts that pay the employee, is using public position to generate private revenue. The artifact assigns Action #8 (pilot recruitment) and the Phase 3 district presentation to "Founder" with no intermediary. The realistic worst outcome is not a fine: it is termination for cause, an Ethics Panel referral, a Montgomery County Inspector General inquiry, local press coverage with the founder's name and job title in the headline, and the permanent unsaleability of the product to any Maryland district. Who gets hurt: the founder (career, livelihood), the pilot families (product collapses mid-pilot holding their children's mental-health data), and MCPS students generally (the next good idea from an employee gets reflexively refused).

**Evidence**

Md. Code, Gen. Prov. §5-506 (Use of Prestige of Office) bars an official or employee from intentionally using their position for their own or another's private gain [verified via Maryland State Ethics Commission compilation and Justia; exact current subsection text unverified]. §5-502 (Employment or Financial Interests — General Restriction) and §5-503 (entities contracting with the State) govern secondary employment. §5-816 (Local Boards of Education) provides that a local board adopts conflict-of-interest regulations for its officials and employees; where it does not, county ethics provisions apply. COMAR 19A.05.02.04 requires board rules prohibiting outside employment that would impair impartiality and independent judgment, and permits boards to prohibit outside employment with an entity subject to the authority of the school system. MCPS Regulation GCA-RA is titled "Employee Conflict of Interest" and Board Policy BBB is "Ethics"; MCPS has an Ethics Panel and an Ethics Officer. MCPS Form 460-50 is a pre-approval form defining outside employment as "any compensated work that a MCPS employee performs for a non-MCPS entity," and expressly includes uncompensated service as officer/director/board member. [GCA-RA and BBB designators confirmed by search of MCPS documents; full operative text UNVERIFIED — ww2.montgomeryschoolsmd.org was not reachable from this session. Verify the current GCA-RA text and BBB directly.]

**Recommendation**

Before any further build: (1) file the MCPS outside-employment pre-approval (Form 460-50 or current equivalent) disclosing the venture, the entity, your role, and the intent to sell to MCPS; (2) request a written advisory opinion from the MCPS Ethics Panel / Ethics Officer under the §19A-7-style advisory mechanism, describing the exact fact pattern including the MCPS pilot and the district sales motion; (3) until that opinion is in hand, delete "MCPS" from every revenue target and substitute a non-employer district; (4) build a hard recusal wall — you personally never present to, negotiate with, or invoice MCPS, and a non-employee officer owns that entire motion. Treat an Ethics Panel opinion that says no as dispositive, not as an obstacle to route around.

### RT-02 — Recruiting pilot families and sourcing content through the employment relationship converts every later success into evidence of misuse

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Action #8: "Launch pilot cohort: 10 MCPS families (5 neurodivergent students + parents, mixed profiles)" — Owner: "Founder". Certification exam Part 2: "10 short-response items using real MCPS student scenarios". Tutor Agent tools: "MCPS subject knowledge base". MCLSS: "CEU-eligible | MCPS District Partnership". MCST: "MCPS paid peer tutoring eligibility".

**The problem**

Each of these is a separate transfer of public-employment value into a private asset. "10 MCPS families" recruited by an MCPS employee: how were they identified? If from a caseload, a roster, an IEP team, a school directory, or a parent relationship formed on the job, that is use of position and potentially of confidential information. "Real MCPS student scenarios": if derived from actual students the founder encountered at work, that is a disclosure of student information into a commercial product. "MCPS subject knowledge base": if it ingests MCPS curriculum, these are the district's materials, likely work-for-hire. "MCPS paid peer tutoring eligibility" and "MCPS District Partnership" are affirmative representations that MCPS has agreed to things it has not agreed to. The mechanism of harm is cumulative: each one is individually arguable, and together they form a pattern that an investigator will read as a single course of conduct. The worst outcome is that a successful pilot becomes the proof of the violation.

**Evidence**

COMAR 19A.05.02.04 requires local board ethics rules to include disqualification from participating in matters with a direct economic impact on the employee. MCPS Form 460-50 requires a leave request and approval for any outside work performed during the regular workday. [ESTABLISHED for the rule; INFERENCE as to how these specific families, scenarios, and knowledge bases were or would be sourced — the artifact does not say, which is itself the problem.]

**Recommendation**

Write and keep a provenance log: for every pilot family, every scenario, every content asset, and every contact, record how it was obtained and on whose time and equipment. Recruit the pilot exclusively through a public channel open to anyone (a public landing page, a community organization, a faith institution) with no use of MCPS rosters, email, devices, buildings, or work hours, and keep the enrollment records to prove it. Strip "real MCPS student scenarios" and replace with synthetic or published vignettes. Remove "MCPS District Partnership" and "MCPS paid peer tutoring eligibility" from all materials until a signed agreement exists; both are currently false statements about a public body.

### RT-03 — The product is unlicensed practice of psychology under Maryland law

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Tab 3 header: "PhD-Level Diagnostic Assessments — Psychometrically validated | Student: 52 domains". Diagnostic Agent tools: "52-domain psychometric engine", "Risk flag detector (crisis + academic)"; output: "counselor referral flag". Test Anxiety Coach tools: "Spielberger TAI scorer". Anxiety Toolkit: "Test anxiety severity tracker over time".

**The problem**

Maryland defines "practice psychology" to include, for compensation, applying psychological methods to constructing, administering, or interpreting tests of mental abilities, aptitudes, attitudes, and personality characteristics. A paid subscription product that administers a 52-domain instrument to a 12-year-old, scores a Spielberger TAI, tracks anxiety severity longitudinally, and emits a clinical referral flag is squarely inside that definition. The word "psychometric" is used by the artifact itself. Nothing in the artifact names a licensed psychologist; Action #1 says the instrument will be "validated with licensed school psychologist" — validation review is not supervision, and does not cover ongoing administration and interpretation. Worst outcome: a Board of Examiners of Psychologists complaint (trivially filed by any competitor, any parent, or any school psychologist who sees the output), a cease-and-desist that halts the product, and a referral that the founder must then disclose to MCPS. Who gets hurt: children receive uncredentialed clinical judgments; families act on them.

**Evidence**

Md. Code, Health Occupations §18-101 defines "practice psychology" to include, for compensation, "constructing, administering, or interpreting tests of mental abilities, neuropsychological functioning, aptitudes, interests, attitudes, personality characteristics." §18-301 requires a license. §18-401: "A person may not practice, attempt to practice, or offer to practice psychology in this State unless licensed or registered by the Board." §18-404 is titled "Penalties" — amounts UNVERIFIED. §18-102 exempts other licensed health professionals only if they do not describe their services using "psychological," "psychologist," or "psychology" — the artifact uses "psychometric" and "Psychometrically validated" throughout.

**Recommendation**

Pick one of two postures and build to it. (A) Non-clinical: delete "psychometric," "psychometrically validated," "diagnostic," "severity tracker," and "PhD-Level" from every surface; reframe as a self-reflection and study-planning inventory that produces no scores, no norms, no referral flags, and no clinical language; state plainly in-product that it is not an assessment and does not detect or diagnose anything. (B) Clinical: retain a Maryland-licensed psychologist as a named clinical director with documented supervisory responsibility for instrument construction, scoring logic, interpretation rules, and the referral threshold, under a written agreement, and budget for it. Option A is the MVP-first, evidence-before-claims path and costs nothing. Option B costs five figures annually minimum. There is no third option in which you keep the clinical language without the license.

### RT-05 — Advertising crisis detection creates a duty to detect; the design guarantees you will miss one

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `EXPERT-OPINION` |
| **Lens confidence** | 0.82 |

**What the artifact says**
> Risk register: "Crisis detection layer; automatic counselor + parent notification; hotline display; AI conversation paused immediately; transcript flagged for human review". IEP workflow step 5: "Crisis Escalation Protocol — Anxiety markers exceed threshold → counselor alert + parent notification + crisis resources displayed". Security: "crisis escalation detection with latency < 500ms".

**The problem**

This is a negligent-undertaking exposure. You are not obligated to build suicide detection. Once you advertise it, families rely on it, and reliance is the element that creates duty where none existed. An LLM classifier over a middle schooler's free text will miss indirect disclosure, coded language, non-English expression, and the most dangerous case of all — the child who stops using the app. The artifact has no detection for disengagement. The realistic worst outcome is a child self-harms, the family's lawyer discovers the marketing copy promising crisis detection, and the case is not about whether you caused the harm but about whether you promised to prevent it and took money for that promise. Secondary mechanism: the "< 500ms" SLO is a specific, quotable performance guarantee that is unachievable for any pipeline involving an LLM inference, and every logged breach of it becomes an exhibit. Who gets hurt: the child, the family, and every subsequent family whose trust in such tools is destroyed.

**Evidence**

[EXPERT-OPINION on the tort theory — negligent undertaking / failure-to-warn as applied to safety features in consumer software is an active and unsettled area; I did not verify a controlling Maryland case and will not invent one.] [ESTABLISHED on the technical point: no LLM-based classification pipeline returns in <500ms end-to-end including the notification side-effects described, and the artifact's own stack (LangGraph orchestration, FastAPI, agent chaining) makes sub-second impossible.]

**Recommendation**

Remove "crisis detection" as a feature claim entirely and replace it with an always-visible, unconditional, zero-latency resource surface: 988 and a local crisis line on every screen of the anxiety toolkit, not triggered by anything. Delete the "< 500ms" SLO from all documents — never publish a latency number for a safety function. If you keep any flagging at all, (a) specify it as best-effort assistive signalling to a named human, never as detection; (b) name that human and their hours in writing, with an explicit statement of what happens outside those hours; (c) state in the ToS and the onboarding, in plain language a parent reads and acknowledges, "This product does not monitor for emergencies and will not detect a crisis. If your child is in danger, call 988 or 911." Write the Safety Case document that states the failure modes you accept.

### RT-06 — Automatic parent notification of a child's distress can deliver a child to the source of the harm

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `EXPERT-OPINION` |
| **Lens confidence** | 0.84 |

**What the artifact says**
> "automatic counselor + parent notification"; IEP accommodation "Check-in / Check-out — Daily emotional check-in; threshold alert to parent + counselor if distress detected"; Test Anxiety Coach output: "counselor referral flag, parent notification"; Parent Coach Agent triggers: "child distress escalation".

**The problem**

The design treats the parent as a uniformly safe escalation target. The diagnostic itself undermines that assumption: Parent Domain 4 asks about "Use of rewards, punishments, or threats around homework completion" and "Communication style during high-stress academic moments (shaming vs. coaching)"; Student Domain 6 asks about the home environment. The product therefore knows, in structured fields, that some fraction of these parents are the stressor — and still routes the child's distress to them automatically. For a neurodivergent child, a queer child, a child in a household where academic failure is punished, or a child whose distress is about the parent, automatic disclosure is the harm. The mechanism is simple and well-documented in school-counseling practice: the child learns the app reports to their parent, and either stops disclosing (the product becomes useless and falsely reassuring) or discloses and is punished. Worst outcome: a child is harmed at home as a direct result of an automated notification your system sent.

**Evidence**

[EXPERT-OPINION — school counseling and adolescent mental health practice treat the decision to involve a caregiver as a clinical judgment requiring assessment of caregiver safety, not an automated threshold. I did not locate a single controlling source and will not cite one I cannot verify.] [INFERENCE from the artifact's own data model: the product collects the exact fields that would predict caregiver risk and does not use them to gate notification.]

**Recommendation**

Never automate caregiver notification from a distress signal. Route every flag to a named licensed human who makes the disclosure decision, or do not flag at all. Give the child a documented, age-appropriate explanation at onboarding of exactly what is shared with their parent and what is not — and honor it. Build an explicit "this stays between us unless someone is in danger" boundary and make the exceptions concrete. If you cannot staff a human reviewer, the correct design is: no distress detection, no notification, prominent unconditional crisis resources. Also note the design conflict with your own "Child Liberation" framing: a surveillance pipeline to parents is the opposite of child agency, and the artifact never notices the contradiction.

### RT-04 — Spielberger Test Anxiety Inventory is a copyrighted commercial instrument — "TAI scorer" and any TAI-derived item bank is infringement absent a license that does not permit this use

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.87 |

**What the artifact says**
> Assessment Framework sources list "Spielberger TAI (1980)"; Test Anxiety Coach tool: "Spielberger TAI scorer"; MCLSS Domain 2: "Spielberger TAI screening"; badge list includes "Spielberger TAI".

**The problem**

The TAI is not public domain. It is © 1980 Charles D. Spielberger, distributed under paid licenses by Mind Garden with per-administration minimums, and the standard License to Administer is explicitly "for research purposes only... for data collection only and not for providing individual feedback to survey participants" — which is precisely what this product does. Building a "TAI scorer" means either (a) reproducing the items (direct infringement), (b) paraphrasing them into a derivative item bank (derivative work infringement, and an unvalidated instrument wearing a validated instrument's name), or (c) having no actual TAI at all and simply using the name as marketing (false advertising plus trademark/attribution problems). All three are bad. Worst outcome: a cease-and-desist and damages claim from the rights-holder, forced withdrawal of the diagnostic (the product's centerpiece), and the discovery during litigation that the founder is a public school employee.

**Evidence**

Mind Garden's TAI product pages: Manual lists "Copyright © 1980 by Charles D. Spielberger"; License to Administer carries minimum purchase quantities (50 for paper/non-Mind-Garden survey systems, 20 hosted) and states the research license is "for data collection only and not for providing individual feedback to survey participants"; instrument access must be controlled and "cannot be posted on the open web or sent to participants by email." Companion STAI-AD terms state the items, directions, manual, and reports "can be used only with purchase or written permission from Mind Garden." [TAI-page-specific wording of the IP clause UNVERIFIED; verify at mindgarden.com/150-test-anxiety-inventory before relying on exact terms.]

**Recommendation**

Build an Instrument Licensing Register before writing another line of diagnostic code: one row per named instrument (TAI, and audit every other name used — PASS, VARK, Phinney measures, Scarborough-derived tools, Saphier rubrics, Anki/SuperMemo), with rights-holder, license type required for commercial per-user administration with individual feedback, cost, and status. Contact Mind Garden directly and ask for a commercial license covering individual feedback to minors; expect that it does not exist in a form you can afford at $49/month. Plan to replace TAI with a genuinely open instrument or an original scale you validate yourself — and if original, never call it "the Spielberger TAI" or "psychometrically validated."

### RT-07 — IDEA Part B confidentiality governs every IEP you ingest and is never mentioned once

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.91 |

**What the artifact says**
> IEP AI 5-Step Workflow step 1: "IEP Document Upload — Parent/school uploads IEP PDF; AI extracts accommodations, goals, and evaluation dates automatically". Schema: "student_profiles (diagnostic_json, iep_id, ancestry[])". Security section lists "FERPA Compliance" and "COPPA (Under 13)" only. MCLSS Domain 12 lists "FERPA, HIPAA-adjacent" — IDEA appears nowhere in the artifact.

**The problem**

IEPs are special education records subject to 34 CFR 300.610–300.627, which layer additional obligations on top of FERPA: parental consent before PII goes to parties not otherwise permitted, named officials responsible for confidentiality, training requirements, a public listing of employees with access, and destruction obligations when the information is no longer needed. The artifact's step 1 allows upload "Parent/school" — two different legal pathways with different consent requirements, collapsed into one button. If the school uploads, you need a lawful basis under 300.622 and FERPA's school-official exception simultaneously. If the parent uploads, you have consent for your use but you have also become a holder of special-education PII with no destruction schedule and no designated responsible official. The artifact has neither. Worst outcome: a complaint to the Maryland State Department of Education or OSEP, a district-level finding, MCPS instantly terminating any relationship, and — because the founder is an MCPS employee — a personal finding that lands in a personnel file.

**Evidence**

34 CFR 300.622(a): parental consent must be obtained before PII is disclosed to parties other than officials of participating agencies, unless the information is contained in education records and the disclosure is authorized without consent under 34 CFR Part 99. US ED's IDEA confidentiality FAQ confirms the confidentiality provisions span §§300.610–300.626, apply to all children with disabilities under IDEA, and that FERPA exceptions are permissive, not mandatory — participating agencies "may, but are not required to" disclose PII without consent. 34 CFR 300.612 requires notice to parents of their rights regarding this information; 300.613 requires inspection access without unnecessary delay and in no case more than 45 days.

**Recommendation**

Add IDEA Part B to every compliance surface in the artifact and build to the stricter standard, not FERPA's. Specifically: designate a named official responsible for the confidentiality of PII (300.623); maintain a current list of employees and contractors with access to IEP data; separate the parent-upload path from the school-upload path in both UI and data model, with different consent records attached; write a destruction schedule and honor it; and train anyone with access. Decide whether you need the IEP PDF at all — the MVP-first answer is that you can deliver accommodation presets from a parent-entered checklist and never touch the document. That single decision removes most of this finding.

### RT-08 — Direct-to-family and district-licensed are incompatible legal postures for the same record; the artifact runs both

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.89 |

**What the artifact says**
> Business Model: "Family Subscription — $49/mo | $399/yr" alongside "School / District License — $2,500–$15,000/school/yr ... admin dashboard; district progress reporting". Diagnostic Center: "Real-time cohort comparison (anonymized)" and "Parent diagnostic portal (separate login)". Security: "FERPA Compliance — Row-level RLS policies; parental consent workflow".

**The problem**

These are two different legal identities and you cannot hold both for the same child's data. As a FERPA school official under 34 CFR 99.31(a)(1)(i)(B), you must perform a function the district would otherwise staff, be under the district's direct control over use and maintenance of education records, and be bound by 99.33(a) redisclosure limits — which means the district, not you, controls the data, and you cannot use it for your own purposes, including product improvement, cohort benchmarking, or marketing to the family. As a consumer operator selling a $399/yr subscription to the parent, you have a contract with the family and the data is yours to use per that contract. The artifact's "School admin dashboard + district progress reporting" plus "Family Subscription" plus "Real-time cohort comparison" means the same record flows to the district, to the parent, to a peer-comparison feature, and into agent memory, under contradictory authorities. "Row-level security" is a database control; it is not a legal posture. Worst outcome: a FERPA complaint establishes you redisclosed without authority, which (a) ends the district channel and (b) is independently a Maryland §4-131 problem.

**Evidence**

34 CFR 99.31(a)(1)(i)(B): an outside party may be a school official only if it "(1) Performs an institutional service or function for which the agency or institution would otherwise use employees; (2) Is under the direct control of the agency or institution with respect to the use and maintenance of education records; and (3) Is subject to the requirements of §99.33(a)." US ED guidance adds that the vendor must meet the criteria in the district's annual FERPA notification, and that unilateral changes to terms of service "make it difficult for a school or district to demonstrate direct control." Md. Code, Educ. §4-131 defines "operator" by reference to the FERPA school-official exception and a contract with a school or system, and §4-131(d)(1) bars targeted advertising from service-derived information, building a student profile outside a PreK-12 school purpose, selling covered information, and disclosing outside the (e) exceptions.

**Recommendation**

Pick one channel for the MVP. The founder's own stated principles (completion > validation > monetization; MVP-first) point to direct-to-family only, because the district channel is also the conflict-of-interest channel. If you later add districts, build a hard tenancy and legal-basis boundary: separate database tenants, separate consent records, separate retention schedules, and a data-flow diagram showing that a record acquired under a district contract never enters a consumer feature, cohort comparison, model training, or marketing. Write the FERPA posture memo before the schema, not after.

### RT-09 — The 52-domain instrument is a PPRA protected-information survey and the artifact never mentions PPRA

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Domain 1 items incl. "1.1 Cognitive worry component — racing thoughts during testing"; Domain 6: "6.4 Extracurricular time demands (sports, faith community, jobs, family care)", "6.5 Family academic support availability — parent confidence AND time"; Parent Domain 4: "Use of rewards, punishments, or threats around homework completion", "Response to child tears, frustration, or complete shutdown"; Parent Domain 2: "Highest level of education completed"; customer profile: "Under-resourced". Crisis detection throughout.

**The problem**

PPRA restricts surveys that reveal protected categories, and this instrument hits at least four: mental and psychological problems of the student or the student's family (Domain 1 entire, crisis detection, anxiety severity); religious practices/affiliations ("faith community"); income beyond program-eligibility needs ("under-resourced," parent education, "family care," "jobs"); and critical appraisals of other family members (the entire Parent Domain 4 battery, plus asking a child about the home). The artifact plans district deployment and federal grant funding — "2 federal grant applications (Title I + IDEA) submitted." Title I and IDEA funds are US Department of Education program funds. The moment this instrument is administered under a district contract or with ED program funding, prior written parental consent is required, not an opt-out, and parents must be able to inspect the instrument before administration. The artifact has a "verifiable parental consent flow" for COPPA but nothing for PPRA, and PPRA consent is a different document with different disclosures. Worst outcome: a Student Privacy Policy Office complaint, a district-level finding, loss of the grant.

**Evidence**

20 U.S.C. §1232h(b) and (c): no student shall be required to submit to a survey revealing protected information without prior consent — and for an unemancipated minor, written parental consent — where the survey is funded in whole or part by a US Department of Education program. Protected categories confirmed in the statutory text include political affiliations/beliefs, mental and psychological problems of the student or family, sex behavior or attitudes, critical appraisals of other individuals with close family relationships, legally recognized privileged relationships, religious practices/affiliations/beliefs, and income (other than as required to determine program eligibility). §1232h also requires direct notification to parents of scheduled covered surveys, an opt-out opportunity for non-ED-funded covered surveys, and parental right to inspect the instrument on request.

**Recommendation**

Treat the instrument as a PPRA covered survey from day one regardless of funding, because your roadmap puts you in ED-funded territory by Month 12. Build: (1) a separate, explicit PPRA consent document listing which protected categories the instrument touches, in plain language; (2) a pre-administration inspection flow — the parent can read every item before the child sees any; (3) per-domain opt-out, so a family can decline the religion, income, and family-appraisal items and still use the product; (4) delete the items you do not need. Audit every one of the 52 and 38 items against the eight PPRA categories and cut anything that is not load-bearing for the study plan. "Faith community" as a scheduling input can be "a weekly recurring commitment" with no label.

### RT-10 — COPPA applies to most of the target population and the stated controls do not meet the current Rule

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.92 |

**What the artifact says**
> Target: "MCPS Middle School (6–8th)"; Security: "COPPA (Under 13) — Verifiable parental consent; zero behavioral advertising; full data deletion on demand". Certification Portal: "Video teaching demo recorder + uploader". Schema: "agent_memory (agent_id, user_id, context jsonb, ttl)".

**The problem**

Sixth graders are 11 and 12. COPPA applies. The artifact's three-item COPPA line misses most of the current Rule's requirements. Missing: a written children's information security program with designated responsible personnel, annual risk reassessment, and vendor oversight. Missing: a data retention policy with a stated retention period — "full data deletion on demand" is a deletion right, not a retention limit, and indefinite retention is now prohibited. Missing: separate verifiable parental consent for disclosure to third parties — and this product has many third parties (Claude/DeepSeek/GPT-4o, Pinecone, Upstash, Supabase, S3, Sentry, PagerDuty, push-notification vendors), each receiving children's data. Missing entirely: biometric identifiers are now personal information under the Rule, and "Video teaching demo recorder + uploader" plus "Video teaching demo analyzer (AI)" means you are collecting and algorithmically processing children's faces and voices. Worst outcome: an FTC enforcement action with civil penalties per violation, which for a solo founder is existential.

**Evidence**

Amended COPPA Rule (16 CFR Part 312), published 90 FR, April 22, 2025; effective June 23, 2025; full compliance date April 22, 2026 (now passed). The amendments require separate verifiable parental consent before disclosing a child's personal information to third parties; add a written information security program requirement with designated responsible personnel, risk assessment, and annual review; require that data be retained only as long as reasonably necessary for the specific purpose collected and prohibit indefinite retention; and add biometric identifiers (including voiceprints and faceprints) to the definition of personal information. The FTC declined to adopt the proposed ed-tech-specific provisions. A February 25, 2026 FTC policy statement limits enforcement for age-verification-only collection in narrow circumstances — it does not help this product.

**Recommendation**

Draft the written children's information security program this month; it is a document, it is cheap, and its absence is a per se violation. Publish a retention schedule with concrete periods per data category (diagnostic responses, chat transcripts, video, IEP extracts, agent memory) and implement automatic deletion — note your schema's agent_memory already has a ttl column, so wire it and set it short. Build a separate consent step for third-party disclosure and enumerate the recipients by name in the consent text. For video: either drop the video teaching demo entirely from the MVP (strongly recommended — see RT-15) or obtain a distinct biometric-specific consent and never run analysis on it.

### RT-11 — IEP PDF ingestion is a direct prompt-injection channel into agents that hold tools and notification powers

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> "IEP Document Upload — Parent/school uploads IEP PDF; AI extracts accommodations, goals, and evaluation dates automatically" feeding "Profile Auto-Configuration — AI maps every accommodation to corresponding app settings; configures UI, timers, TTS, agent behavior". Diagnostic Agent tool: "IEP PDF parser (NLP)". Agents hold "Certificate generation API", "Calendar API integration", and parent/counselor notification outputs.

**The problem**

An uploaded PDF is attacker-controlled text that your pipeline feeds to an LLM whose output "configures ... agent behavior." That is the canonical prompt-injection setup, and the artifact's own words — "configures UI, timers, TTS, agent behavior" — describe a document that rewrites agent instructions. Concrete attacks: (1) hidden white-on-white text in an uploaded IEP instructs the Diagnostic Agent to emit a crisis flag for a target student, triggering counselor and parent notification — a weaponized false report about a child; (2) injected text suppresses crisis flagging for the uploader's own child; (3) injected text instructs the Cert Exam Agent to issue a certificate, or the Schedule Agent to exfiltrate another user's blocks into a summary; (4) a student pastes injection text into the free-text tutor chat, which also runs on an agent with tools. The artifact has no mention of injection, no separation of instructions from data, no output validation, and no privilege boundary between document content and agent control plane. Worst outcome: a child is falsely crisis-flagged to their parent and school by someone else's upload.

**Evidence**

[ESTABLISHED] Indirect prompt injection through retrieved or uploaded documents is the top-ranked risk in the OWASP Top 10 for LLM Applications (LLM01) and is unsolved by prompting alone — no system prompt reliably prevents it. The artifact's own architecture (document text → LLM → agent configuration → notification side-effects) is the textbook vulnerable pattern.

**Recommendation**

Never let extracted document text reach an agent's instruction context. Parse the IEP with a deterministic extractor into a closed enum of accommodation types (extended_time_ratio, tts_enabled, break_interval_minutes, chunk_size) and validate every value against an allowlist with ranges before it touches anything. Nothing that comes out of a PDF or a child's free text may set agent behavior, trigger a notification, issue a certificate, or call a tool. Put a hard human confirmation step between extraction and application — the artifact already has the right instinct in the failure table ("human review before any change applied" for IEP mismatch) but applies it only to mismatches, not to the normal path. Then commission a red-team of the pipeline with adversarial PDFs before the pilot, and write the AI threat model that the artifact lacks.

### RT-12 — Self-reported LLM confidence below 0.85 is not a safety control and is named as one twice

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Risk register and Failure Handling, identically: "Confidence scoring on ALL outputs; human expert review queue for score < 0.85; citations required; zero-tolerance for unverified academic claims".

**The problem**

This control is load-bearing in two places and does not work. LLM self-reported confidence is poorly calibrated and is systematically highest exactly where the model is confabulating — a fluent, well-formed hallucination scores high. A 0.85 threshold therefore filters out the uncertain-and-correct outputs while passing the confident-and-wrong ones, which is worse than no filter because it manufactures a false assurance that someone has reviewed the dangerous cases. "Citations required" compounds it: models fabricate citations with high confidence, and this very artifact demonstrates the failure mode (see RT-20 on the fabricated effect sizes it already contains). There is also no named reviewer, no queue SLA, no volume estimate, and no budget line for the human review the control depends on. Worst outcome: a child is taught something false about their own anxiety or their IEP rights, confidently and with a fake citation, and the stated control reports that everything was fine.

**Evidence**

[ESTABLISHED] Calibration failure of verbalized LLM confidence is well replicated; models are overconfident and confidence does not separate hallucinated from grounded content reliably enough to serve as a gate. [INFERENCE, strongly supported] The artifact itself contains at least four unverifiable effect sizes (RT-20) presented with citation-like attribution, which is direct evidence that the "citations required; zero-tolerance" discipline was not applied to the artifact's own authorship.

**Recommendation**

Replace self-reported confidence with controls that actually bind: (1) retrieval-grounded generation where every factual claim must be extractable from a vetted, human-authored corpus, and anything not extractable is refused rather than generated; (2) a closed content set for all clinical, legal, and IEP-adjacent statements — written by humans, versioned, never model-generated at runtime; (3) adversarial eval suites with human-labelled gold answers run in CI, with a published pass bar; (4) a named reviewer, a queue SLA, an estimated daily volume, and a line in the budget. If you cannot staff review, reduce the surface until you can: a product that only schedules and only drills user-authored flashcards needs almost no review.

### RT-13 — Shared agent_memory with no tenancy boundary is a cross-child data leak waiting to happen

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.8 |

**What the artifact says**
> Schema: "agent_memory (agent_id, user_id, context jsonb, ttl)"; Redis described as "Cache / Agent Memory — Short-term agent memory, session state"; Pinecone/pgvector for "semantic search: content matching, note similarity"; Parent Coach Agent memory includes "cohort connection history"; Cultural Identity Agent memory includes "inspiration journal entries".

**The problem**

The entire multi-tenant isolation story rests on a user_id column and "row-level security." The vector store has no tenancy column shown at all, and semantic retrieval across a shared index is the most common cross-tenant leak in RAG systems: a child's note embedding is retrieved as "similar content" for a different child. Redis agent memory is keyed by agent_id and user_id in the schema but Redis is described as shared session state, and a single key-construction bug leaks one child's anxiety context into another child's chat. The cohort features actively encourage cross-user data flow. Note the contrast with AEOS, which the founder has already built with committed row-level security and a security mutation test suite — this artifact proposes none of that discipline and does not reference reusing AEOS's, despite the founder's stated principle of shared AEOS infrastructure over per-module duplication. Worst outcome: one child's mental-health disclosures surface in another family's app, which is simultaneously a FERPA/IDEA breach, a COPPA violation, a Maryland PIPA notification event, and an unrecoverable trust failure.

**Evidence**

[INFERENCE from the stated schema — the artifact shows no tenant_id, no per-tenant vector namespace, no RLS policy text, and no isolation tests.] [ESTABLISHED as a class of vulnerability: shared-index retrieval leakage and cache-key collision are standard multi-tenant failure modes.]

**Recommendation**

Reuse AEOS's existing hardened multi-tenant model rather than inventing a second one — that is the founder's own stated principle and it saves months. Specifically: add an explicit tenant/family identifier to every table including agent_memory and every vector record; use per-tenant namespaces in the vector store, never a shared index with metadata filtering as the only boundary; port AEOS's security mutation test suite and extend it with cross-tenant read attempts for each new table; make the isolation tests a merge gate. Default agent_memory ttl to days, not indefinite. Treat "anonymized cohort comparison" as a separate, offline, k-anonymized aggregate — never a live query across the live table.

### RT-14 — "PhD-Level" as a marketing adjective, plus named universities that have not agreed, is a deceptive-credential fact pattern

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.91 |

**What the artifact says**
> "PhD-Level Learning Science Platform", "PhD-Level Gap Analysis", "PhD-Level Diagnostic Assessments", "PhD-Level Certification Framework", "PhD-Level Course Architecture", "PhD-Level Certification Exam" (for a 40-hour course for a 12-year-old), "PhD-Level Exam Structure"; "University Partnership Track — 3 graduate credits via partner university | Stackable toward MAT or Ed.D. | Target partners: Howard University, Morgan State, UMCP"; "CEU-eligible" (MCLSS, MMEC).

**The problem**

Three distinct exposures. (1) "PhD-Level" applied to a 40-hour middle-school course is not defensible in any forum; it is a term with an understood meaning in the market the product sells into, and its use to describe a child's certificate is the kind of credential-implication claim the FTC has specifically pursued. (2) Naming Howard University, Morgan State, and UMCP as "Target partners" in a document that will be shown to customers, investors, and grant officers invites each institution's general counsel to send a demand letter about unauthorized use of their names in connection with a credential offering — "target" does not cure the implication, and it will be read as "partners." (3) "3 graduate credits," "CEU-eligible," and "Stackable toward MAT or Ed.D." are representations that an accredited body will confer academic value. Nothing in the artifact shows any accrediting body, university, or CEU-granting authority has agreed. Worst outcome: an FTC Section 5 matter, a university cease-and-desist, and — because the founder is a public school employee marketing credentials to that school system's staff — a simultaneous MCPS ethics problem.

**Evidence**

FTC Notice of Penalty Offenses Concerning Education (issued to 70 for-profit institutions, October 2021) identifies as unfair or deceptive under Section 5: misrepresenting, directly or by implication, the need or demand for individuals who have graduated from or completed courses at a specific institution, and misrepresenting the number or percentage of graduates who obtained employment or their earnings; the underlying case law includes a 1952 matter on misrepresenting the benefits a recipient of a certificate or diploma would gain. Receipt of such a notice establishes actual knowledge, enabling civil penalties. COMAR 13B.02.01 requires approval before an out-of-state degree-granting institution may "operate in Maryland, do business, recruit or enroll students, begin instruction, or promote advanced publicity through advertisements" — authority: Md. Educ. Art. §§10-212, 11-105, 11-201–11-207, 16-108. [MHEC's specific restrictions on use of academic terminology by non-degree-granting entities: UNVERIFIED — I could not retrieve the provision; check Md. Educ. Art. §11-201 et seq. and COMAR 13B directly.]

**Recommendation**

Global find-and-replace: delete every instance of "PhD-Level." It buys nothing and costs the whole credibility of the document. Delete "Howard University, Morgan State, UMCP" until a signed MOU exists; replace with "university partnership to be sought." Delete "CEU-eligible" until a named CEU-granting authority has approved in writing, and name it when it does. Build an Advertising Substantiation File: one row per public claim, with the evidence that supports it and the date, reviewed before any page goes live. Call the credentials what they are — a MindUnlock certificate of completion — and let the quality of the program be the claim.

### RT-15 — Selling a "GED-to-PhD pathway" at $99–$999/level to explicitly under-resourced parents is the artifact's most predatory surface

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.87 |

**What the artifact says**
> "GED-to-PhD Parent Pathway — $99–$999 / level — 8 stackable credential levels"; Levels 4–8 ("GED Preparation", "Associates Degree Pathway", "Bachelor's Completion Pathway", "Graduate Education Certificate", "Doctoral Research in Education (PhD)") all marked "Partner"; parent customer profile: "Under-resourced, wants to help"; problem statement: "No GED-to-PhD pathway exists, keeping families in educational poverty cycles".

**The problem**

Five of the eight levels — everything from the GED upward, which is everything a parent is actually buying the dream for — are marked "Partner," meaning no partner exists. The product controls Levels 1–3 (certificates it invents and sells) and has no ability to deliver Levels 4–8. The marketing frame explicitly targets families the artifact describes as under-resourced and in "educational poverty cycles," and sells them a doctorate at the end of a ladder whose rungs are missing. That is the structure of every predatory-credential enforcement action in the sector. The additional cruelty is that MindUnlock's own Levels 1–3 certificates have no transfer value toward Level 4+ at any institution, because no institution has agreed to recognize them — so the money spent on 1–3 buys nothing toward the promised destination. Worst outcome: state AG consumer-protection action, FTC Section 5, and the specific reputational catastrophe of a Black-founded, Black-serving education venture being reported as having sold fake doctoral pathways to poor Black parents.

**Evidence**

[INFERENCE from the artifact's own text — "Partner" with no named partner for Levels 4–8 is an admission that the pathway does not exist.] FTC Penalty Offense Notice Concerning Education covers misrepresenting, directly or by implication, the benefits a certificate or diploma recipient would gain. [ESTABLISHED for the legal standard; INFERENCE as to how a regulator would characterize this specific offering.]

**Recommendation**

Cut Levels 4–8 from every document today. Sell only what you can deliver: a parent coaching certificate that you describe accurately as a MindUnlock certificate with no academic transfer value, stated in that language on the purchase page. If you want the pathway to be real, go get it: a written articulation agreement with one community college for one specific credit-bearing course, signed, before you advertise anything above Level 3. One real rung beats eight imaginary ones, and the founder's own principle — no claims of validation that has not occurred — already decides this.

### RT-16 — Per-ethnicity "cultural learning style" and ancestry[] as a child's database column is racial essentialism in affirming language

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.86 |

**What the artifact says**
> Student Domain 4 item "4.8 Preferred cultural learning style (call-response, storytelling, movement)"; "4.7 Ancestral pride as potential academic motivator (new construct, MindUnlock)"; schema "student_profiles (diagnostic_json, iep_id, ancestry[])"; "Ethnic origin selector (40+ African cultures)"; "5.1 VARK modality preference (Visual / Auditory / Kinesthetic / Reading-Writing)".

**The problem**

Three compounding problems. (1) "Preferred cultural learning style" tied to an ethnicity selector assigns cognitive traits by ancestry. Dressed as affirmation, it is the same structure as the deficit theories it claims to replace: it tells a Black child that their mind works a particular way because of where their ancestors came from, and then configures the software to deliver less text to them. A competitor, a journalist, or a parent will read it exactly that way, and they will be right. (2) It rests on learning-styles matching, which is the most thoroughly debunked idea in applied education psychology — and the artifact doubles down by also including VARK. (3) "ancestry[]" as an array column on a child record is a racial/ethnic origin field stored on a minor; in most privacy frameworks this is sensitive-category data, and it is here collected for product configuration. The artifact also claims to have invented a psychological construct — "(new construct, MindUnlock)" — in a document that elsewhere calls itself "Psychometrically validated." Flattening 40+ distinct cultures into one selector feeding one "ancestor of the day" engine is the appropriation risk the artifact's own risk register names, arriving through the front door.

**Evidence**

[ESTABLISHED] Pashler, McDaniel, Rohrer & Bjork (2008), "Learning Styles: Concepts and Evidence," Psychological Science in the Public Interest: "at present, there is no adequate evidence base to justify incorporating learning-styles assessments into general educational practice." Willingham, Hughes & Dobolyi (2015) classify learning styles as a neuromyth. A 2024 meta-analysis of the matching hypothesis found the required crossover interaction in 26.19% of 42 outcome measures — contested, and not a basis for product design. [EMERGING at best for any claim that matching instruction to culturally-attributed style improves outcomes; I found no replicated evidence for it and will not cite any.]

**Recommendation**

Delete item 4.8 and item 5.1. Replace both with a format preference the child states for themselves, with no ethnic or style label attached and no inference drawn from ancestry — "how do you want this explained?" asked per-lesson, answered by the child, changeable any time. That preserves agency (which the artifact genuinely cares about) and removes the essentialism. Make ancestry a free-text, optional, child-controlled field for the inspiration feature only, firewalled from anything pedagogical, deletable in one tap, and never used to configure instruction. Remove "(new construct, MindUnlock)" — you cannot claim a construct you have not validated. Then fund the advisory board (RT-17) and let them review these items before a child sees them.

### RT-17 — The cultural-harm mitigation names paid co-developers and a board with veto power; the budget contains neither

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> Risk register: "Cultural appropriation of African-centered content — High — African-centered scholars as PAID co-developers; community advisory board with veto power; ongoing cultural review process". Business Model: "Operating Costs (tech + staff + marketing) ~$175,000" with no itemization.

**The problem**

The mitigation is the right mitigation. It is also unfunded and unscheduled. There is no line item, no named scholar, no board charter, no veto procedure, and no mention anywhere in the 12-month roadmap of recruiting or convening the board — while "Ancestor library expanded to 40+ cultures" is scheduled for Phase 4 and "African-centered identity module (40 cultures)" for Phase 2. So the content ships before the review mechanism exists. Meanwhile the Content Agent is assigned to "Create 40+ ancestor inspiration profiles" — meaning an LLM, not a scholar, authors the cultural content that the mitigation promises scholars will co-develop. The gap between stated mitigation and resourced plan is itself the finding: it is the pattern a critic will use to argue the cultural framing is marketing. Who gets hurt: the communities whose heritage is rendered by a language model and sold back to their children at $399/yr.

**Evidence**

[INFERENCE from the artifact's own contents — Risk table promises PAID co-developers; Tab 1 "What AI Should Do Next" assigns "Create 40+ ancestor inspiration profiles" to the Content Agent; Tab 9 budget has no cultural-content line; Tab 10 roadmap has no advisory board milestone.]

**Recommendation**

Put a number on it before Phase 1 ends: name two or three scholars, agree day rates, write contracts, and add a line to the operating costs. Write the advisory board charter — membership, compensation, meeting cadence, and the exact mechanism by which a veto is exercised and recorded, because "veto power" with no procedure is not veto power. Move the first board convening to Phase 1, ahead of any cultural content shipping. Do not let an LLM author ancestor profiles; use it to draft from scholar-supplied sources and have the scholar sign off per profile. If the budget cannot carry this, cut the cultural module from the MVP rather than shipping it unreviewed — that is the honest version of the founder's own principle.

### RT-18 — Year 1 financials are not survivable arithmetic and showing them to an investor or grant officer is its own risk

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.84 |

**What the artifact says**
> "Total Year 1 Revenue $391,850 | Operating Costs (tech + staff + marketing) ~$175,000 | Net Year 1 ~$216,850", against commitments elsewhere including "Quarterly external pen test; bug bounty program; OWASP Top 10 compliance; annual third-party security audit", "Legal counsel from Day 1", "RDS PostgreSQL Multi-AZ", "African-centered scholars as PAID co-developers", four certification tracks, and "500 families".

**The problem**

The $175,000 does not cover the commitments made elsewhere in the same document. A rough floor, all in year one: four quarterly external pen tests at $15–40k each ($60–160k); an annual third-party security audit ($20–50k); specialized privacy/ed-tech counsel for FERPA, IDEA, PPRA, COPPA, state operator laws, plus a ToS, two consent architectures, and a district contract template ($40–80k); a bug bounty program with any real payout budget ($10k+); a licensed psychologist for clinical oversight ($30k+); paid cultural co-developers ($20k+); instrument licensing (unknown, potentially prohibitive — RT-04); multi-AZ AWS plus LLM inference for 500 families of daily chat ($30–60k); E&O, cyber, media-liability and abuse insurance for a product serving minors ($15–40k); and the content production for four certification tracks totalling 360 hours of curriculum (this alone is a full-time year of work). That is comfortably $250–500k before the founder takes a dollar, against $391,850 of revenue that assumes 500 paying families from a standing start with no marketing budget identified and no customer-acquisition cost modelled. The separate risk: presenting "Net Year 1 ~$216,850" to an investor or a federal grant officer, with these obligations visible elsewhere in the same deck, reads as either unseriousness or misrepresentation. Grant applications carry certifications; a materially unsupportable budget in a federal application is not merely embarrassing.

**Evidence**

[INFERENCE] All cost figures above are my estimates from market ranges, not quotes — they are illustrative of order of magnitude and should be replaced with real quotes. The internal contradiction between the $175,000 figure and the artifact's own commitment list is ESTABLISHED from the document itself and does not depend on my estimates.

**Recommendation**

Rebuild the model bottom-up with real quotes for the five largest items (counsel, security testing, insurance, clinical oversight, LLM inference at projected volume) before showing it to anyone. Then cut scope until the numbers close: the MVP-first answer is one customer segment, one certification track, no video, no district channel, no cultural module, no crisis detection, and a security posture of "one external pen test before the pilot" rather than quarterly. Model CAC explicitly — 500 families is the single most aggressive number in the document and it has no acquisition plan behind it. Present a conservative case and a stretch case, never one number, and never a "Net" line in a pre-revenue document.

### RT-19 — A pilot on 10 families of neurodivergent minors collecting mental-health data, with no IRB and no research protocol

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.82 |

**What the artifact says**
> Action #8 / Phase 1: "Pilot cohort: 10 MCPS families (5 neurodivergent students + parents, mixed profiles)"; KPIs "Diagnostic completion rate ≥ 80%", "BARS daily use ≥ 5 days/week by pilot families"; risk register: "Pilot cohort dropout before data collection"; MMEC Module 15: "Action Research Methodology (IRB-compliant)" — the only mention of IRB in the document, and it is about teachers' research, not the founder's.

**The problem**

The artifact knows what an IRB is — it teaches it — and does not apply it to its own pilot on children. The pilot's own language ("before data collection," completion-rate KPIs, "exit interview for any dropout") is research language. The subjects are minors, in a protected class (disability), from a population the artifact describes as under-resourced, recruited by someone with institutional authority over their schooling, generating mental-health and crisis data. That is close to the maximum-vulnerability configuration. There is no protocol, no child assent process, no parental informed consent document, no stated withdrawal procedure, no data-use limitation, no adverse-event definition, and no independent reviewer. The founder's employment relationship adds coercion risk: families may feel they cannot decline a request from someone connected to their child's school. Worst outcome: a child is harmed during the pilot (a crisis mishandled, a notification that backfires, a distressing diagnostic item) and there is no protocol, no oversight record, and no insurance.

**Evidence**

[INFERENCE] Formal IRB jurisdiction depends on funding and intent to generalize; a private company's product pilot may fall outside Common Rule coverage. That is a legal technicality, not an ethical defense, and it evaporates the moment the work is written up, submitted with a federal grant application, or conducted with any university partner — all three of which the roadmap plans. [ESTABLISHED] The artifact itself treats IRB compliance as a professional standard worth certifying teachers in.

**Recommendation**

Obtain independent ethics review before the pilot — an independent IRB will review a small protocol for a few thousand dollars, and a university partner may do it as part of a research agreement. Write: a protocol with aims, procedures, risks, and stopping rules; a parent informed-consent form and a separate child assent form in plain language; a no-penalty withdrawal procedure with immediate data deletion; an adverse-event definition and escalation path with a named clinician; and a data-use limitation saying what pilot data may and may not be used for. Remove the coercion vector by recruiting through a channel where the founder's MCPS role is invisible and irrelevant. Budget for it.

### RT-20 — The document contains effect sizes and prevalence figures I cannot verify, presented in citation form — in a product whose stated discipline is zero tolerance for unverified claims

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.79 |

**What the artifact says**
> "38% of middle schoolers experience debilitating test anxiety (Zeidner, 1998)"; "Culturally affirming instruction raises Black student achievement (ES: 0.8)" attributed to Hilliard (1997), Nobles (2006), Asante (1987); "Agency in learning design produces 40% greater intrinsic motivation" attributed to Holt/Gray/Freire; "Mixed-topic practice beats blocked practice for long-term retention by 43%" attributed to Rohrer & Taylor (2007) / Bjork (1994); "85% of test anxiety interventions validated only on white, middle-class, neurotypical populations"; "73% of MCPS families lack both" attributed to Hoover-Dempsey & Sandler (1997).

**The problem**

Several of these are precise quantitative claims attached to authors whose cited works are, to my knowledge, books or theoretical papers that do not report them. "73% of MCPS families" attributed to a 1997 national parental-involvement model is the clearest tell — a 1997 theory paper cannot contain a statistic about Montgomery County families. "ES: 0.8" for African-centered pedagogy attributed to three theorists with no meta-analysis among them is a fabricated-looking effect size on the artifact's single most sensitive topic. The mechanism of harm is direct: these numbers will go into grant applications, investor decks, and district presentations. A grant reviewer or a district research office who checks one of them and finds it unsupported does not conclude there was an error; they conclude the applicant fabricates. For a founder whose stated principle is "evidence before claims," this is the document failing its own test in its own foundational tab.

**Evidence**

[INFERENCE — I could not verify any of the listed figures and I will not assert they are false without checking the primary sources.] Zeidner's Test Anxiety: The State of the Art (1998) is a real and substantial book; whether it reports 38% "debilitating" prevalence for middle schoolers is UNVERIFIED. Rohrer & Taylor (2007) is a real interleaving study with large effects; the specific "43%" figure is UNVERIFIED. Hoover-Dempsey & Sandler (1997) is a real theoretical model of parental involvement; it cannot be the source of an MCPS-specific percentage. Gray (2013) Free to Learn is a trade book, not a source of a "40%" intrinsic-motivation effect size. I found no meta-analysis supporting ES 0.8 for African-centered pedagogy. What to check: the primary source for each figure, page number, sample, and whether the quantity is the one stated.

**Recommendation**

Audit every number in the document against its primary source, one by one, and record page numbers in a citations register. Any figure you cannot locate in the cited source comes out — not softened, out. Replace with either a verified figure and a real page cite, or a qualitative statement. Where a claim is your hypothesis rather than a finding, label it as such; the Gap Analysis is stronger, not weaker, for saying "we believe" where that is true. Apply the artifact's own stated standard — "citations required; zero-tolerance for unverified academic claims" — to the artifact first, because it is the document that will be shown to the people most likely to check.

### RT-21 — Recording and AI-scoring children's teaching videos, plus live cohort comparison at n≈10, are two avoidable re-identification and bias surfaces

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.83 |

**What the artifact says**
> MCST exam Part 3: "Video-recorded 15-min tutoring session with a peer; scored on 5-domain MindUnlock rubric"; Certification Portal: "Video teaching demo recorder + uploader"; Cert Exam Agent tool: "Video teaching demo analyzer (AI)"; Diagnostic Center: "Real-time cohort comparison (anonymized)".

**The problem**

Video: a 12-year-old records a session with another 12-year-old — so the uploader is capturing a second child who is not the account holder and whose parent has consented to nothing. The file contains both children's faces and voices, which are now COPPA-defined personal information, stored in S3, and processed by an AI scorer. AI scoring of recorded speech and affect in children is a known bias surface along race, accent, disability, and speech-fluency lines — and this product's users are by design neurodivergent and predominantly Black, i.e. precisely the populations where such scorers underperform. A low score from that scorer is a credential denial with a demographic pattern. Cohort comparison: the pilot is 10 families; "anonymized" at n=10, with grade, school, and neurodivergent status, is not anonymous — any participant can identify any other. "Real-time" makes it worse by allowing differential queries over time. Worst outcome: biased credential denials to Black neurodivergent children, from a product built to affirm them, plus a re-identification incident inside the pilot community.

**Evidence**

[ESTABLISHED] Biometric identifiers including voiceprints and faceprints are personal information under the amended COPPA Rule (effective June 23, 2025). [ESTABLISHED] k-anonymity fails at small n with quasi-identifiers; n=10 with grade/school/status is trivially re-identifiable. [EMERGING→ESTABLISHED] Differential error rates by race, accent, and disability in automated speech and affect scoring are well documented in the fairness literature; I did not verify a specific study for this exact use and will not cite one.

**Recommendation**

Cut the video demo from the MVP. The pedagogical goal — demonstrating you can teach — is achievable with a live observation by a human, or an audio-free artifact, or a peer-and-mentor written attestation. If video returns later: require separate consent from the peer's parent before upload, never run an AI scorer on it (human rubric scoring only), store it encrypted with a short deletion clock, and never use it for training. For cohort comparison: make it offline, aggregated, minimum cell size of 20, suppressed below that, with no grade/school/status crossing — and drop "real-time" entirely. Both changes shrink the MVP, which is the correct direction.

### RT-22 — Mandated-reporter duty and the private product entangle: a disclosure to your app is a disclosure to you

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.86 |

**What the artifact says**
> "Student crisis / self-harm disclosure ... transcript preserved for human review"; "Test anxiety emergency support chat"; parent diagnostic items on "Use of rewards, punishments, or threats", "Response to child tears, frustration, or complete shutdown", "Communication style during high-stress academic moments (shaming vs. coaching)"; artifact contains no mandated-reporting policy.

**The problem**

The founder is an educator and therefore a mandated reporter under Maryland law. The product collects, by design, exactly the information that triggers the duty: a child's distress disclosures, and parent self-reports about punishment and conflict in the home. When a disclosure suggesting abuse or neglect lands in the "human review" queue, the reviewer is the founder — who has a personal legal duty to report, and an institutional duty to notify the head of their school. There is no policy in the artifact for this, no timeline, no record, and no explanation to families that it will happen. Two failure directions, both bad: the founder sees a reportable disclosure and does not report (statutory failure, with a complaint routed to the county board of education that employs them); or the founder reports, and a family who thought they bought a study app discovers it is a reporting channel to Child Protective Services and to their child's school district. Worst outcome: a reportable disclosure sits unread in a queue because there is no queue SLA and no staffed reviewer.

**Evidence**

Md. Code, Family Law §5-704 requires an educator acting in a professional capacity who has reason to believe a child has been subjected to abuse or neglect to notify the local department or appropriate law enforcement agency; a person working at a school must also immediately give all required information to the head of the institution or designee; oral report as soon as possible, written report to the local department within 48 hours with a copy to the local State's Attorney. Per CHILD USA's summary, an investigating agency with substantial grounds to believe a person knowingly failed to report must file a complaint, which for an educator goes to the county board of education or employing agency. [Penalty/enforcement detail via CHILD USA secondary source; the knowing-failure complaint mechanism should be verified against current §5-704 text.]

**Recommendation**

Write a mandated-reporting policy before the pilot: who reviews flagged transcripts, within what time, what triggers a report, how the report is made and recorded, and what the family is told. Disclose it prominently at signup in plain language — "people who work on this product are mandated reporters; if we see something suggesting a child is being harmed, we are required by law to report it." A family that knows this can make an informed choice; one that does not has been deceived. Separately, reconsider collecting the parent-punishment items at all (they are also PPRA protected-category items — RT-09): if you do not ask, you do not create the duty, and the study plan does not need the answer.

### RT-23 — No retention schedule, no deletion plan, and no answer to what happens to children's mental-health data when the company dies

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> Security: "FERPA Compliance — ... data minimization; deletion rights; 7-year audit log retention"; "COPPA (Under 13) — ... full data deletion on demand". Single-founder operation throughout: Action items, pilot, and Phase 3 district presentation all owned by "Founder".

**The problem**

The artifact states deletion rights but never states a retention period for any data category — and the only concrete number given, "7-year audit log retention," retains metadata about children longer than most of them will be in secondary school. Under the amended COPPA Rule, indefinite retention is prohibited and a stated retention policy is required. Worse, there is no wind-down plan. This is a single-founder venture holding IEP extracts, 52-domain psychometric responses, anxiety trajectories, crisis transcripts, children's videos, and ethnic-origin fields on minors. The bus factor is one. If the founder is hit by a bus, loses the MCPS job and the income that subsidizes the venture, or simply stops — what happens to the data? The default answer is that it sits in a Supabase project and an S3 bucket paid for by a lapsing credit card, and then it is sold with the assets or abandoned. Maryland's own student-data law contemplates successor entities inheriting operator obligations, which means an acquirer inherits this data. Worst outcome: a children's mental-health dataset in the hands of whoever buys the domain.

**Evidence**

Amended COPPA Rule: operators may retain children's personal information only as long as reasonably necessary for the specific purpose for which it was collected, and may not retain it indefinitely; a written retention policy is required. Md. Code, Educ. §4-131: "If an operator ... is merged with or acquired by another entity, the successor entity is subject to this section for previously collected covered information." 34 CFR 300.624 (destruction of information when no longer needed) applies to IDEA PII. [INFERENCE on the single-founder failure mode, from the artifact's own task ownership.]

**Recommendation**

Write a Records Retention and Deletion Schedule now: one row per data category, with a period, a trigger, and an automated job. Short periods everywhere — chat transcripts in days, agent_memory via the ttl column you already have, diagnostic responses for the subscription term plus a short tail, video deleted on certification decision, IEP extracts deleted when the accommodation profile is set (keep the structured settings, not the document). Then write the wind-down clause into the ToS and into a standing instruction: on cessation, all child data is deleted within 30 days and families are notified; data is explicitly excluded from any asset sale. Name a second person with the access and the instruction to execute it. This is a weekend of writing and it is the difference between a responsible failure and a scandal.

### RT-24 — "SM-18" is SuperMemo's proprietary algorithm and Anki does not implement it — a licensing exposure wrapped in a false product claim

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.94 |

**What the artifact says**
> Tech Stack: "SM-18 Algorithm — Spaced Repetition — Anki-compatible; AnkiConnect sync; neurodivergent-adjusted ease factors; IEP time scaling"; repeated as "Spaced repetition Anki engine (SM-18)", "Anki deck creator + smart reviewer (SM-18)", "SM-18 spaced repetition scheduler", "Anki SM-18 integration".

**The problem**

SM-18 is SuperMemo's proprietary algorithm. Anki does not and cannot ship it; Anki offers SM-2 and FSRS specifically because SuperMemo's current algorithms are proprietary and require licensing. So "SM-18 ... Anki-compatible" is incoherent: either you license SM-18 from SuperMemo (a commercial negotiation that is not in the plan or the budget), or you implement something and call it SM-18 (a false claim about a named third-party product, repeated five times across the document and therefore in every customer-facing derivative of it), or you use FSRS and mislabelled it. Minor relative to the rest of this list, but it is the kind of error that an investor's technical diligence finds in ten minutes and then uses to discount every other technical claim in the document — including the ones that are correct.

**Evidence**

Anki's official FAQ: SuperMemo's latest algorithm is proprietary and requires licensing; because Anki is open source it can only use algorithms made freely available, such as FSRS. As of Anki 23.10 Anki offers two algorithms: one based on SM-2, and FSRS. Anki's FAQ notes preliminary tests indicate FSRS is roughly on par with SM-17.

**Recommendation**

Replace every instance of "SM-18" with "FSRS" and verify what you actually intend to implement. FSRS is free, open, actively maintained, Anki-native, and at least comparable to SM-17 — it is strictly the better choice here and removes the licensing question entirely. While editing: "Claude 3.5 Sonnet primary" is also stale as of this document's date and should be updated to a current model, and the same diligence should be applied to every other named third-party product in the Tech Stack tab.

### RT-25 — "Paid peer tutoring eligibility ($15–20/hr)" for certified middle schoolers is an unexamined child-labor and liability surface

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.76 |

**What the artifact says**
> MCST: "12 modules | 40 hours | Digital badge + physical cert | Paid peer tutoring eligibility ($15–20/hr)"; "Upon Certification ... MCPS paid peer tutoring eligibility"; Module 12 practicum: "Certify 3 Peers (Documented + Observed)"; App Design: "Peer tutor matching after certification".

**The problem**

The product promises 11–14-year-olds paid work at a stated wage, and then offers to match them with the people who will pay. Three issues the artifact does not address: (1) Maryland child labor law requires work permits for minors and restricts hours — the artifact states a rate and a matching feature with no mention of either; (2) "MCPS paid peer tutoring eligibility" again asserts a decision MCPS has not made (see RT-02), and the person asserting it is an MCPS employee; (3) "Peer tutor matching" means your platform introduces minors to other families for in-person or online paid sessions, which is a safeguarding function with background-check, supervision, and liability implications nowhere acknowledged. The $15–20/hr figure is also a specific earnings representation to a child and their under-resourced parent, which is exactly the category of claim the FTC's education penalty notice covers. Worst outcome: a safeguarding incident arising from a match your platform made, or a wage/permit complaint, either of which also reaches the founder's employer.

**Evidence**

[ESTABLISHED] Maryland requires work permits for minors and restricts hours and occupations; specific provisions UNVERIFIED — check Md. Code, Labor & Employment Title 3, Subtitle 2 and the Maryland Department of Labor's work permit requirements. [ESTABLISHED] FTC Notice of Penalty Offenses Concerning Education covers misrepresenting how much graduates may earn. [INFERENCE] The safeguarding exposure of minor-to-minor paid matching is my reasoning from the described feature.

**Recommendation**

Remove the "$15–20/hr" figure and the "MCPS paid peer tutoring eligibility" claim from all materials. Cut "peer tutor matching" from the MVP — it is a marketplace with a safeguarding duty, and it is not the product. If peer tutoring stays as a pedagogical activity (it is genuinely good pedagogy — the protégé effect is real), scope it to supervised, unpaid, within-cohort practice with parental consent on both sides and an adult present. Revisit paid matching only with counsel, a safeguarding policy, and insurance.


---

## What is missing and should be added

### MCPS Ethics Panel written advisory opinion + outside-employment pre-approval file   `ESTABLISHED`

**Why it matters.** This is the gate. Every other document on this list is wasted effort if the Ethics Panel says the venture cannot sell to MCPS, and the opinion is free. Obtaining it before building also converts the biggest risk into a documented, defensible position: you asked, in writing, before you started.

**What to build.** A dated packet containing: (1) the completed MCPS outside-employment pre-approval form (460-50 or current equivalent) disclosing the entity, your role, ownership, and intended customers; (2) a written request to the MCPS Ethics Officer / Ethics Panel describing the exact fact pattern — MCPS employee, product targeting MCPS, pilot of MCPS families, planned district presentation, planned school contracts, use of MCPS-adjacent content — and asking specifically what is prohibited, what requires approval, and what recusal structure would make it permissible; (3) the Panel's written response; (4) your recusal plan conforming to it.

**Evidence.** Md. Code, Gen. Prov. §5-506 (use of prestige of office for private gain), §5-502 (employment/financial interests), §5-816 (local boards of education conflict rules); COMAR 19A.05.02.04 (minimum content of board ethics rules, incl. outside employment impairing impartiality and employment with entities subject to the system's authority); MCPS Regulation GCA-RA "Employee Conflict of Interest" and Board Policy BBB "Ethics"; MCPS Ethics Panel and Ethics Officer; MCPS Form 460-50. [GCA-RA/BBB designators confirmed via search; operative text UNVERIFIED — ww2.montgomeryschoolsmd.org was unreachable from this session.]

### Conflict-of-Interest and Recusal Policy (written, dated, signed, with a provenance log)   `INFERENCE`

**Why it matters.** The Ethics Panel opinion tells you the rule; this document proves you followed it. Its real function is evidentiary: when someone later asks how you got your first ten families, you produce a contemporaneous record instead of a reconstruction.

**What to build.** A standing policy stating: the founder does not present to, negotiate with, or invoice MCPS; no MCPS time, device, account, network, facility, roster, directory, curriculum, or student information is used by the venture; all recruitment occurs through public channels; a named non-employee officer owns any MCPS-facing motion. Plus a running provenance log with one row per pilot family, content asset, contact, and work session — how obtained, on whose time, on whose equipment.

**Evidence.** COMAR 19A.05.02.04 disqualification requirement; MCPS Form 460-50's requirement of advance leave approval for outside work during the workday. [ESTABLISHED for the obligations; the log is INFERENCE — a control I am recommending, not one any rule names.]

### Legal Posture Memo: FERPA / IDEA Part B / PPRA / COPPA / Md. Educ. §4-131 — one channel, one basis per record   `ESTABLISHED`

**Why it matters.** The artifact treats compliance as six bullet points in a security card. These five regimes impose conflicting obligations and the product currently straddles them. The memo forces the architectural decision (consumer vs. district) before the schema is written, which is where it is cheap.

**What to build.** A counsel-reviewed memo stating, per data category: the legal basis for collection, who the controller is, what consent document authorizes it, what may and may not be done with it, who it may be disclosed to, and the retention period. Must explicitly resolve: whether you are a FERPA school official or a direct-to-consumer operator (you cannot be both for one record); whether IEP data is handled under IDEA Part B's stricter rules; which instrument items are PPRA protected categories; and COPPA applicability by user age band.

**Evidence.** 34 CFR 99.31(a)(1)(i)(B) (school official: institutional function, direct control, §99.33(a) redisclosure limits); 34 CFR 300.610–300.627 (IDEA Part B confidentiality, incl. 300.622 consent, 300.623 safeguards, 300.624 destruction); 20 U.S.C. §1232h (PPRA protected categories and prior written parental consent); 16 CFR Part 312 as amended (effective 6/23/2025, compliance 4/22/2026); Md. Code, Educ. §4-131(d)(1), (e).

### Consent Architecture: four distinct documents, not one checkbox   `ESTABLISHED`

**Why it matters.** The artifact says "verifiable parental consent flow" as though it is a single thing. It is four legally distinct consents with different content, different timing, and different revocation consequences, and bundling them invalidates all of them.

**What to build.** (1) COPPA verifiable parental consent for collection from under-13s, using an approved method; (2) a separate COPPA consent for disclosure to named third parties, with the recipients enumerated; (3) a PPRA consent listing the protected categories the instrument touches, with a pre-administration inspection flow and per-domain opt-out; (4) an IDEA/FERPA authorization specific to the IEP document, separate from the rest. Plus a child assent flow in age-appropriate language, and a one-tap revocation path for each that states what happens to already-collected data.

**Evidence.** 16 CFR Part 312 as amended — separate verifiable parental consent required before third-party disclosure; 20 U.S.C. §1232h(c) — prior written parental consent for protected-category surveys and parental right to inspect; 34 CFR 300.622 — consent before PII disclosure to non-permitted parties.

### Clinical Governance Charter with a named Maryland-licensed psychologist, or a documented decision to be non-clinical   `ESTABLISHED`

**Why it matters.** Finding RT-03 forces a binary and the product cannot ship until it is chosen. The charter either establishes lawful clinical oversight or records the decision to remove all clinical function — and in the latter case it is the artifact against which every piece of copy gets audited for the word "psychometric."

**What to build.** Either: a signed agreement with a Maryland-licensed psychologist naming them clinical director, with documented responsibility for instrument construction, scoring logic, interpretation rules, referral thresholds, and periodic review of flagged cases — plus a budget line. Or: a Non-Clinical Scope Statement listing every term removed (psychometric, diagnostic, severity, validated, referral flag, PhD-Level), the in-product disclaimer text, and a standing copy-review checklist.

**Evidence.** Md. Code, Health Occupations §18-101 (definition of practice psychology includes constructing, administering, interpreting tests of mental abilities, aptitudes, attitudes, personality characteristics for compensation); §18-301 (license required); §18-401 (may not practice, attempt to practice, or offer to practice without a license); §18-102 (scope).

### Crisis Response Protocol and Safety Case   `EXPERT-OPINION`

**Why it matters.** The artifact promises crisis detection in four places and has no protocol behind it anywhere. The Safety Case is the document that makes you state, in writing, what your system will not catch — which is the only honest basis for the promises you then make to families.

**What to build.** A protocol naming: the human reviewer and their hours; the queue SLA; what happens outside those hours; the escalation matrix including when a caregiver is and is not notified and who decides; the unconditional always-visible resource surface (988 and local lines) that is never gated by detection; the mandated-reporting pathway (see below); and an adverse-event log. Paired with a Safety Case enumerating known detection failure modes — indirect disclosure, coded language, non-English, and above all disengagement — and stating plainly that the product does not monitor for emergencies. No latency SLO anywhere in either document.

**Evidence.** [EXPERT-OPINION] Negligent undertaking / reliance-based duty from advertised safety features; no controlling Maryland authority verified. [ESTABLISHED] A <500ms end-to-end LLM crisis-detection-and-notification SLO is technically unachievable in the described stack.

### Mandated Reporting Policy and family-facing disclosure   `ESTABLISHED`

**Why it matters.** The founder's personal §5-704 duty attaches to anything they read in the review queue. Without a policy there are only two outcomes, both bad: an unreported disclosure, or a report that blindsides a family who was never told the product was a reporting channel.

**What to build.** A policy stating who reviews flagged content, within what time, what constitutes reason to believe, how the oral and written reports are made and logged, and the parallel obligation to notify the head of the institution. Plus plain-language disclosure at signup: "People who work on this product are mandated reporters under Maryland law." Plus a decision record on whether the parent-punishment diagnostic items are retained at all.

**Evidence.** Md. Code, Family Law §5-704 — educator acting in professional capacity must notify local department or law enforcement; school staff must immediately inform the institution head; oral report as soon as possible, written report within 48 hours with copy to the local State's Attorney.

### AI Threat Model and Red-Team Report   `ESTABLISHED`

**Why it matters.** The product feeds attacker-controlled PDFs and children's free text into agents that hold notification, calendar, and certificate-issuance powers. Nothing in the artifact acknowledges prompt injection. A threat model written now costs days; discovering it in production costs a child being falsely crisis-flagged.

**What to build.** A document enumerating trust boundaries (uploaded documents, student free text, parent free text, LLM outputs, agent-to-agent messages), the privilege held on each side, and the control at each boundary. Required controls: deterministic extraction into a validated enum for IEP data; no document- or user-derived text in any instruction context; allowlist validation before any agent config change; human confirmation before any notification, certificate, or external call. Plus a red-team report from adversarial testing with crafted PDFs and injection prompts, run before the pilot.

**Evidence.** [ESTABLISHED] Indirect prompt injection is OWASP LLM01 and is not mitigable by prompting alone. The artifact's own pipeline description — document text → LLM → "configures ... agent behavior" → notification — is the vulnerable pattern verbatim.

### Multi-Tenant Isolation Specification + ported AEOS security mutation tests   `INFERENCE`

**Why it matters.** The founder has already solved this once in AEOS, with row-level security and a committed security mutation test suite, and the founder's own stated principle is shared AEOS infrastructure over per-module duplication. This artifact proposes a second, weaker isolation story from scratch. Porting is faster than rebuilding and strictly safer.

**What to build.** A spec requiring an explicit tenant identifier on every table including agent_memory, per-tenant namespaces in the vector store (never a shared index with metadata filtering as the only boundary), documented RLS policies per table, and short TTLs on agent memory. Plus the AEOS security mutation test suite extended with cross-tenant read attempts for every new table, wired as a merge gate.

**Evidence.** [INFERENCE] The artifact's schema ("agent_memory (agent_id, user_id, context jsonb, ttl)") shows no tenant boundary and the vector store shows none at all. [ESTABLISHED] Shared-index retrieval leakage and cache-key collision are standard multi-tenant failure modes.

### Records Retention and Deletion Schedule + Wind-Down and Data-Disposition Plan   `ESTABLISHED`

**Why it matters.** The amended COPPA Rule prohibits indefinite retention and requires a policy; the artifact has none. The wind-down plan answers the question nobody has asked: a single-founder company holding children's mental-health data has a bus factor of one, and the default disposition of that data on failure is abandonment or sale.

**What to build.** A table with one row per data category (diagnostic responses, chat transcripts, agent memory, IEP extracts, video, certificates, audit logs), each with a retention period, a deletion trigger, and the automated job that enforces it. Plus a wind-down clause in the ToS and a standing instruction: on cessation, all child data deleted within 30 days, families notified, data explicitly excluded from any asset sale — with a named second person holding the access and the instruction to execute it.

**Evidence.** 16 CFR Part 312 as amended — retention only as long as reasonably necessary for the specific collection purpose, no indefinite retention, written retention policy required. 34 CFR 300.624 — destruction of IDEA PII when no longer needed. Md. Code, Educ. §4-131 — successor entities inherit operator obligations for previously collected covered information.

### Instrument Licensing Register and Advertising Substantiation File   `ESTABLISHED`

**Why it matters.** Two registers that together close the two cheapest-to-lose exposures in the document: using someone else's copyrighted instrument, and making claims you cannot support. Both are spreadsheets. Both are reviewed before anything ships.

**What to build.** Register one: every named instrument, framework, rubric, and algorithm in the document (Spielberger TAI, PASS, VARK, Phinney, Scarborough, Saphier Skillful Teacher, Anki/SuperMemo, Cutler) with rights-holder, the license actually required for commercial per-user administration with individual feedback to minors, cost, and status. Register two: every public-facing claim with its primary source, page number, and verification date — with a standing rule that any claim without a verified source is deleted, not softened. First pass must resolve the "PhD-Level" usage, the Howard/Morgan State/UMCP naming, "CEU-eligible," "MCPS District Partnership," "MCPS paid peer tutoring eligibility," the "$15–20/hr" figure, "SM-18," and every effect size in the Gap Analysis and Course Design tabs.

**Evidence.** Mind Garden TAI licensing terms (© 1980 Spielberger; research License to Administer is "for data collection only and not for providing individual feedback to survey participants"; minimum purchase quantities; controlled access). FTC Notice of Penalty Offenses Concerning Education (October 2021, 70 institutions) — misrepresenting credential benefits, demand for graduates, employment and earnings; receipt establishes actual knowledge for civil penalties. Anki FAQ — SuperMemo's current algorithms are proprietary and require licensing; Anki ships SM-2 and FSRS.

### Pilot Research Protocol with independent ethics review, consent and assent forms   `INFERENCE`

**Why it matters.** The artifact certifies teachers in IRB-compliant action research and runs an unreviewed study on ten families of neurodivergent minors collecting mental-health data. Whether the Common Rule technically applies is beside the point — it will apply the moment this is written up, submitted with a federal grant, or run with a university partner, all three of which the roadmap plans.

**What to build.** A protocol with aims, procedures, inclusion criteria, risks, stopping rules, and adverse-event definitions; a parent informed-consent form and a separate child assent form in plain language; a no-penalty withdrawal procedure with immediate data deletion; a data-use limitation stating what pilot data may and may not be used for; and independent IRB review. Recruitment must run through a channel where the founder's MCPS role is invisible, to remove the coercion vector.

**Evidence.** [INFERENCE] Formal IRB jurisdiction depends on funding and generalizable-knowledge intent; a product pilot may fall outside the Common Rule. That is a technicality, not a defense, and it fails on first contact with a grant application or university partner. [ESTABLISHED] The artifact itself treats IRB compliance as a professional standard (MMEC Module 15).

### Cultural Content Governance Charter with funded compensation and a real veto mechanism   `INFERENCE`

**Why it matters.** The artifact's own mitigation promises paid African-centered scholars and an advisory board with veto power. Neither appears in the budget or the roadmap, while the cultural content itself is scheduled to ship in Phase 2 and expand in Phase 4 — authored by a Content Agent. The gap between the promise and the plan is the thing a critic will quote.

**What to build.** A charter naming the scholars, their day rates, signed contracts, and a corresponding operating-cost line item; board membership, compensation, and meeting cadence moved into Phase 1 ahead of any cultural content shipping; and a written veto procedure — how it is invoked, by whom, what it blocks, and how the decision is recorded. Plus a content rule: no LLM-authored ancestor or cultural profile ships without a named scholar's per-profile signoff. Plus a review pass over the essentialism items (Domain 4.7, 4.8, 5.1 and the ancestry[] field) before a child sees them.

**Evidence.** [INFERENCE from the artifact's own contents: the Risk table promises PAID co-developers and veto power; "What AI Should Do Next" assigns "Create 40+ ancestor inspiration profiles" to the Content Agent; the budget has no cultural line; the roadmap has no board milestone.] [ESTABLISHED] Pashler et al. (2008), Psychological Science in the Public Interest — no adequate evidence base for learning-styles matching, which item 4.8 and item 5.1 both rest on.


---

## Open questions

- How were the ten pilot families identified, and through what channel will they be contacted? This single answer determines whether RT-01 and RT-02 are manageable disclosure matters or a terminable use of position. Nothing else on this list matters as much.
- Has any MCPS ethics disclosure already been filed, or any advisory opinion requested? If a disclosure exists, the entire top of this analysis changes character. If one does not, the first action is to file one.
- What exactly is the "Spielberger TAI scorer"? Licensed items, paraphrased derivative items, or a name applied to original items? Each answer has a different and incompatible remedy, and only the founder knows which it is.
- Is the founder, or anyone currently committed to the venture, a licensed mental health professional in Maryland? The RT-03 binary cannot be resolved without this answer.
- Where did the quantitative claims come from — "ES: 0.8" for African-centered pedagogy, "73% of MCPS families" attributed to Hoover-Dempsey & Sandler (1997), "40% greater intrinsic motivation," "38%" from Zeidner (1998), "43%" from Rohrer & Taylor? If these were generated rather than read, the same question applies to every other citation in the document.
- Does "real MCPS student scenarios" mean actual students the founder encountered professionally? If yes, this is a student-information disclosure finding, not a content-sourcing one.
- Why is this a separate platform rather than an AEOS module? The founder's stated principle is shared AEOS infrastructure over per-module duplication, and AEOS already has the hardened multi-tenant security model, RLS, and security mutation test suite this artifact proposes to rebuild from scratch. The artifact never addresses the relationship between the two.
- What is actually in MCPS Regulation GCA-RA and Board Policy BBB? I confirmed the designators and titles but could not retrieve the operative text — ww2.montgomeryschoolsmd.org and law.justia.com do not resolve from this session and would need to be allowed in the session's network settings. Every conclusion in RT-01 and RT-02 should be re-checked against the current text before it is relied on.
- Which of the 52 and 38 diagnostic items are actually load-bearing for the study plan? My strong suspicion is that the PPRA protected-category items — religion, income, family appraisals, mental health — could be cut entirely with no loss of product function, which would dissolve RT-09 and shrink RT-22. Nobody has asked the question.
- What does the MVP look like with every item on this list removed — no clinical language, no crisis detection, no video, no district channel, no cultural module, no peer-tutor marketplace, no GED-to-PhD ladder? My guess is: a BARS scheduler, a flashcard engine, and a parent coaching course. That product is shippable in months, breaks no laws, and is worth more than the document as written.

