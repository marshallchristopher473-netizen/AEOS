# MCPS special education review

> The artifact judged against IDEA, COMAR, MSDE and how MCPS special education actually operates.

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

The single most important finding: the artifact's centerpiece school-facing feature — the "IEP/504 AI Accommodation Engine" that ingests an uploaded IEP PDF, "auto-configures" the profile, and performs "Daily Dynamic Monitoring" that "dynamically adjusts difficulty, pacing, and breaks" (App Design tab, 5-Step Workflow steps 2–3; AI Agents tab, "IEP accommodation reminders + auto-adjust") — is a design that relocates a legally reserved team decision into a vendor's algorithm. Under IDEA Part B, accommodations and supplementary aids are determined by the IEP Team (34 CFR 300.321; 300.320; 300.324) with parent participation (300.322), and any proposal to change identification, evaluation, placement or FAPE provision requires prior written notice (300.503). Maryland adds its own procedural layer in COMAR 13A.05.01.07–.09 (team composition, team responsibilities, IEP document). A product that silently changes a child's accommodation set is not a compliance feature; it is a compliance liability, and MCPS's Office of Special Education will read it that way in the first meeting.

Three more things will stop this product at the MCPS door before pedagogy is ever discussed. First, the artifact never mentions IDEA's own confidentiality subpart, 34 CFR 300.610–300.627, which governs PII in special education records and is stricter and more specific than the general FERPA framing the Tech Stack tab relies on. Second, there is no path through Maryland's vendor regime: Md. Code, Educ. §4-131 operator duties, MCPS's own data-privacy vetting committee, and a signed data privacy agreement must precede any student data touching the system — and MCPS Policy DJA plus Educ. Art. §5-112 put a $25,000 Board-approval threshold on purchases, which a 5-school, $7,500-average license trips in aggregate. Third, the artifact's best argument for existing is one it never makes: MCPS is under a state finding of significant disproportionality in suspensions of Black students with disabilities, with a documented ~$5.64M IDEA set-aside consequence. That, not test anxiety, is the budget line with a buyer attached.

---

## Findings

### SPED-01 — The IEP AI Accommodation Engine displaces a legally reserved IEP Team decision

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.95 |

**What the artifact says**
> App Design tab, 'IEP AI 5-Step Workflow': Step 2 'Profile Auto-Configuration — AI maps every accommodation to corresponding app settings; configures UI, timers, TTS, agent behavior'; Step 3 'Daily Dynamic Monitoring — AI agent monitors real-time engagement; dynamically adjusts difficulty, pacing, and breaks'. Also AI Agents tab: 'IEP accommodation reminders + auto-adjust'.

**The problem**

Accommodations and supplementary aids/services are determined by the IEP Team, not by a vendor and not by a model. 34 CFR 300.321 fixes Team membership (parents, at least one general education teacher, at least one special education teacher/provider, an agency representative, someone who can interpret evaluation results). 34 CFR 300.320/300.324 govern IEP content and its review and revision. 34 CFR 300.322 requires parent participation in those decisions. 34 CFR 300.503 requires prior written notice before a public agency proposes or refuses to change identification, evaluation, educational placement, or the provision of FAPE. COMAR 13A.05.01.07, .08 and .09 layer Maryland-specific team, responsibility and document requirements on top, including the 5-business-day pre-meeting document rule and the 5-business-day post-meeting completed-IEP rule. 'Dynamically adjusts' means the product is changing the operative accommodation set between meetings, with no team, no notice, and no parental consent. If a school adopts this, the school — not the vendor — is the one out of compliance, which is exactly why a district will not adopt it.

**Evidence**

34 CFR 300.321 (IEP Team composition, verified: https://www.ecfr.gov/current/title-34/subtitle-B/chapter-III/part-300/subpart-D/subject-group-ECFR28b07e67452ed7a/section-300.321); 34 CFR 300.322 (parent participation, verified same subpart listing); 34 CFR 300.320/300.324 (IEP development, review, revision — referenced in the eCFR Subpart D listing; exact subsection text UNVERIFIED in session, confirm 300.324(a)(4) amendment-without-a-meeting before citing it); 34 CFR 300.503 (prior written notice — section number from primary regulation, NOT directly verified in this session, confirm on eCFR); COMAR 13A.05.01.07 (IEP Team), .08 (IEP Team Responsibilities), .09 (IEP Document) — verified as existing chapter sections via mdrules.elaws.us and law.cornell.edu/regulations/maryland/COMAR-13A-05-01-09.

**Recommendation**

Rename and re-scope the module to an 'Accommodation Fidelity and Implementation Support' tool. It may (a) display the accommodations a human has entered, (b) log whether each was offered/used/declined in each session, (c) generate a draft, clearly-labelled, non-binding observation summary for a human to take to a team meeting, and (d) raise a 'consider discussing at the next IEP meeting' flag. It may never change an accommodation. Every accommodation record in the schema needs source_of_truth = 'IEP team' | 'parent-entered, unverified', a human_entered_by field, an effective-date range, and a hard constraint that no agent write path can modify it. Put that constraint in the security mutation test suite AEOS already has, the same way row-level security is tested.

### SPED-02 — IDEA's own confidentiality subpart (34 CFR 300.610–300.627) is absent; the compliance story is FERPA/COPPA only

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Tech Stack tab, Security & Compliance: 'FERPA Compliance — Row-level RLS policies; parental consent workflow...' and 'COPPA (Under 13)...'. Risks card: 'FERPA/COPPA non-compliance for minors'. The phrase 'IDEA' does not appear anywhere in the compliance section; neither does 'Part B confidentiality' or any 300.6xx citation.

**The problem**

IDEA Part B has a dedicated confidentiality subpart for PII in special education records — 34 CFR 300.610 through 300.627 — which imposes obligations beyond general FERPA: notice to parents (300.612), access rights with a 45-day outer limit and inspection before IEP meetings (300.613), records on more than one child (300.615), fees, amendment-on-request and hearing rights (300.618–300.621), consent (300.622), safeguards and a named official responsible for confidentiality (300.623), and destruction of information when no longer needed (300.624). The artifact is designing a system whose single most sensitive object is an uploaded IEP PDF — the densest PII document in a child's school file, containing disability category, evaluation data, present levels, goals, service minutes and often health information — and then routes it into an NLP parser, a vector database (Pinecone/pgvector, 'semantic search: content matching'), Redis agent memory, and third-party LLM APIs (Claude / DeepSeek-V3 / GPT-4o fallback). Embedding IEP text into a vector index is a disclosure and a retention decision that Subpart F speaks to directly and that no FERPA checkbox addresses.

**Evidence**

34 CFR Part 300 Subpart F, Confidentiality of Information, §§300.610–300.627, verified: https://www.ecfr.gov/current/title-34/subtitle-B/chapter-III/part-300/subpart-F/subject-group-ECFR1d2a18271819883 and https://sites.ed.gov/idea/regs/b/f. §300.611 defines 'destruction' as physical destruction or removal of personal identifiers; §300.622 governs consent separately from FERPA. Practitioner guidance in the search results notes the Part B rules 'do not simply incorporate or restate FERPA requirements' but address special-education-specific issues.

**Recommendation**

Add a named 'Special Education Records Handling Policy' to the Tech Stack tab citing 300.610–300.627, and make three architectural commitments now, before any code: (1) IEP source documents are stored encrypted, are never sent to a third-party LLM API, and are never embedded into a vector index — a human or a locally-hosted extractor produces a small structured accommodation record and the PDF is then purged on a defined schedule (300.624); (2) the accommodation record itself carries field-level encryption and is excluded from agent memory TTL caches; (3) name an individual responsible for confidentiality (300.623 analogue) in the company, and publish the access/amendment request process. This is also the cheapest version of the founder's 'security over feature velocity' principle: not parsing IEP PDFs at all in v1 is faster AND safer than parsing them.

### SPED-03 — No path exists from this product to legal possession of MCPS student data; the roadmap assumes contracts that cannot be signed on that timeline

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Roadmap Phase 3 (Months 7–9): 'MCPS district leadership presentation delivered'; '5 school contracts signed ($37,500 ARR)'; KPI '5 school contracts closed'. Business Model: 'School / District License $2,500–$15,000/school/yr'. No mention anywhere of a data privacy agreement, vendor vetting, or procurement.

**The problem**

Three separate gates are missing. (1) Md. Code, Educ. §4-131 makes a vendor operating under FERPA's school-official exception an 'operator' with statutory duties: no targeted advertising, no profiling outside PreK-12 purposes, no sale of student information, contractual flow-down restrictions on any sub-processor, and deletion on district request. A system whose agents build persistent cross-session profiles needs §4-131 analysed clause by clause. (2) MCPS requires a district-vetted data sharing agreement before school-wide or district-wide adoption of an online digital tool, and runs requests through a committee of data privacy specialists; Maryland districts commonly paper this with a Student Data Privacy Consortium National Data Privacy Agreement (NDPA v2.2, published 19 Nov 2025). (3) MCPS Policy DJA and Md. Educ. Art. §5-112 require Board of Education approval for purchases over $25,000, including aggregated same-vendor spend in a year — so five schools at a $7,500 average is $37,500 and is a Board item, not a principal's signature. The MCPS Inspector General's Report 26-08 (Nov 2025) found over $1M in FY23–24 spend that bypassed this threshold through piecemeal payments, and MCPS has committed to supplier expenditure monitoring — meaning the aggregation loophole is now actively watched. Months 7–9 is not a realistic window for presentation → vetting → DPA → budget cycle → Board approval.

**Evidence**

Md. Code, Educ. §4-131 (verified: https://mgaleg.maryland.gov/2024RS/Statute_Web/ged/4-131.pdf and https://law.justia.com/codes/maryland/education/division-ii/title-4/subtitle-1/section-4-131/). MCPS Data Privacy and Security page (https://www.montgomeryschoolsmd.org/data-privacy-security/safeguards/) describing the vetted data sharing agreement requirement and the data privacy specialist committee. SDPC National Data Privacy Agreement v2.2 (https://privacy.a4l.org/national-dpa/). MCPS Policy DJA ($25,000 advertising/approval threshold) and Montgomery County OIG Report 26-08 (https://www.montgomerycountymd.gov/OIG/Resources/Files/PDF/IGActivity/FY2026/OIGReport26-08.pdf), citing Educ. Art. §5-112. The exact MCPS vendor questionnaire, required artefacts (SOC 2 / HECVAT) and review SLA are UNVERIFIED — not published publicly in what I could reach.

**Recommendation**

Replace the Phase 3 milestone 'MCPS district leadership presentation delivered' with a sequenced gate list and realistic dates: (1) complete an SDPC NDPA v2.2 and publish it; (2) submit to the MCPS data privacy specialist review and record the date; (3) obtain a §4-131 compliance memo; (4) only then approach the Office of Special Education; (5) budget for a 12–18 month first-contract cycle aligned to MCPS's operating budget calendar, not a 3-month sprint. Separately, price the first school pilot UNDER $25,000 total district spend so it never needs a Board item, and say so explicitly in the sales motion.

### SPED-04 — Counselor-alert and crisis-escalation features promise an action the product cannot perform and no school has agreed to receive

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> App Design tab: 'Check-in / Check-out — Daily emotional check-in; threshold alert to parent + counselor if distress detected'. IEP 5-Step Workflow Step 5: 'Anxiety markers exceed threshold → counselor alert + parent notification'. Test Anxiety Coach agent output: 'counselor referral flag, parent notification'. Risks card: 'automatic counselor + parent notification'.

**The problem**

In MCPS, a school counselor or school psychologist receives referrals through internal school processes and school staff; there is no inbound channel by which a consumer app sends an alert to a named MCPS counselor, and no counselor is contractually obligated to monitor one. For a family-direct subscriber the counselor does not know the product exists. The artifact is therefore promising a safety net that does not attach to anything, to a population it has identified as high-risk, in writing, on a marketing surface. That is the most serious consumer-protection and duty-of-care exposure in the whole document — worse than the privacy issues, because a parent may rely on it. It also inverts the real pathway: school mental health referral in MCPS is a human, documented, time-bounded process; a threshold crossing in an app is not a referral.

**Evidence**

INFERENCE from the artifact's own text plus the absence of any school agreement in the Business Model or Roadmap tabs. MCPS's specific counselor/psychologist referral workflow, notification chain and response-time standards are UNVERIFIED — I could not reach an MCPS page documenting them, and MCPS does not publish an SLA. What I would check: the MCPS Office of Student and Family Support and Engagement (OSFSE) crisis response procedures, the MCPS Comprehensive School Counseling Program plan, and MCPS Regulation JHF/JGB-series on student safety and suicide risk, to document the real chain.

**Recommendation**

Strip every 'counselor alert' claim from the family-direct product immediately and replace it with what is actually true and still valuable: on a distress signal the app (a) surfaces 988 and the Montgomery County crisis line, (b) notifies the linked parent, (c) hands the parent a one-tap, pre-written, dated request to the child's school counselor with the student's school and ID, which the PARENT sends. In the school-licensed product, a 'counselor alert' may only be enabled after a signed agreement that names a receiving role, a monitoring window, an escalation fallback for out-of-hours, and an explicit statement that the product is not a monitoring or crisis service. Document all of this in a safety protocol reviewed by counsel before any pilot.

### SPED-05 — The 52-domain student instrument uses self-report for constructs self-report cannot measure, in the population least able to self-report them

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.92 |

**What the artifact says**
> Diagnostics tab: 'Psychometrically validated | Student: 52 domains'. Items include '2.1 Working memory functional capacity (digit span + forward/backward task)', '5.5 Processing speed comfort and frustration threshold', '3.1 Phonological awareness — decoding and fluency baseline assessment', '3.2 Reading fluency and automaticity (words per minute + prosody score)'. Format: '5-point Likert + audio-assisted mode + observational task samples. Estimated: 35–45 min with scheduled breaks.'

**The problem**

Four distinct measurement failures. (1) Construct-method mismatch: working memory, processing speed, phonological awareness and reading fluency are performance constructs. A Likert rating of 'working memory functional capacity' is not a digit-span task; the item text names a task but the stated format is a rating scale, and nothing in the artifact describes how a task would be administered or normed. (2) Informant bias: adolescents with ADHD systematically under-report executive function difficulty relative to parents and teachers — the positive illusory bias literature and BRIEF multi-informant studies show adolescents self-report EF deficits at a lower level than both parents and teachers, with teachers reporting the highest. A single self-report rater is the least valid available informant for exactly the domains the instrument prioritises. (3) Reading demand: a literacy screener whose items must be read defeats itself. Audio-assist helps with decoding, not with the abstract vocabulary of items like 'metacognitive awareness' or 'cognitive flexibility'. (4) Length: 35–45 minutes of continuous self-rating for students selected for attention and literacy difficulty will produce acquiescence, straight-lining and mid-point responding. The artifact's own failure-handling card anticipates this ('Diagnostic assessment gaming / inconsistent responses'), which is an admission the design generates invalid data. And the header word 'validated' is a claim of work that has not occurred, which contradicts the founder's stated 'no claims of validation that has not occurred'.

**Evidence**

Positive illusory bias / informant discrepancy in ADHD youth: Steward et al., 'Self-Awareness of Executive Functioning Deficits in Adolescents With ADHD', Journal of Attention Disorders (doi 10.1177/1087054714530782); BRIEF adolescent/parent/teacher agreement study, Child Neuropsychology (doi 10.1080/09297049.2023.2174506); prevalence nuance in a latent-profile study finding global PIB in 18.4% of young adolescents with ADHD (PMC5479738). Note the PIB literature is contested on magnitude and informant assumptions — [EMERGING] on effect size, [ESTABLISHED] on the direction that single-rater adolescent self-report is insufficient.

**Recommendation**

Split the instrument by method and cut v1 to 15 minutes. Build three short instruments instead of one long one: (A) a 20–25 item student self-report confined to constructs only the student can report — test-anxiety worry/emotionality, subject- and format-specific anxiety, current homework routine, study environment, sleep, perceived support — using a 4-point forced-choice scale at a grade-4 readability ceiling with audio and an example item; (B) a parallel 15-item parent/caregiver form and a 10-item teacher/para form on observable behaviours, so every EF construct has at least two informants; (C) short, timed, scored PERFORMANCE probes for the performance constructs, or no claim about them at all. Drop 'psychometrically validated' from every surface until you have data. Pre-register the validation plan: cognitive interviews with 8–10 MCPS students, readability analysis, pilot n for internal consistency, and a stated decision rule for cutting items.

### SPED-06 — 'IEP/504' is treated throughout as a single object with one accommodation set; they are different statutes, teams, documents and systems

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Project Doc, For Schools: 'IEP/504 AI accommodation engine'. Diagnostics item '5.7 Current IEP/504 accommodation profile (cross-referenced with school records)'. Certification MCLSS domain 3: 'IEP/504 implementation'. App Design: 'IEP/504 AI Accommodation Engine'.

**The problem**

An IEP is an IDEA Part B entitlement: eligibility under one of the federal disability categories plus a need for specially designed instruction, decided by a composed IEP Team (34 CFR 300.321; COMAR 13A.05.01.07), documented on a state-prescribed form, with full Part B procedural safeguards. A Section 504 plan is a civil-rights accommodation under Section 504 of the Rehabilitation Act and its regulations at 34 CFR Part 104: a different eligibility standard (physical or mental impairment substantially limiting a major life activity), a different and much looser team and documentation requirement, different safeguards, and in most districts a locally-held document rather than a state system record. Operationally in Maryland this matters enormously: the IEP lives in the Maryland Online IEP / Student Compass system that MSDE built with Johns Hopkins CTE, and MCPS runs IEPs through the MOIEP/Student Compass with a named MOIEP project manager; 504 plans do not live there. So 'upload your IEP/504' is not one flow — the documents differ in origin, custody, format, content and legal weight, and a parent's 504 plan may be a one-page Word file a school secretary produced. Conflating them guarantees the extraction logic is wrong for one of the two and signals to any MCPS reader that the author has not worked a 504 process.

**Evidence**

34 CFR Part 104 (Section 504 regulations; §§104.33, 104.35, 104.36 — section numbers from primary regulation, UNVERIFIED in this session, confirm on eCFR before citing). Maryland Online IEP / Student Compass: MSDE + JHU Center for Technology in Education (https://education.jhu.edu/cte/solutions/maryland-online-individualized-education-program-system/; https://iep.online-iep.com/maryland/login.aspx). MCPS use of 'Maryland Online Individualized Education Program/Student Compass (MOIEP/SC)' and MOIEP project manager contact in the MCPS Special Education Compliance Manual (https://sites.google.com/mcpsmd.net/mcps-special-education-complia/home). Maryland Assessment, Accessibility and Accommodations Manual distinguishes IEP, 504 and EL plans as separate documentation vehicles (https://marylandpublicschools.org/programs/Documents/Special-Ed/IEP/MAM508102017.pdf, Aug 2025 edition).

**Recommendation**

Model them separately end to end: plan_type enum ('IEP','504','EL_plan','none'), different intake copy, different field sets, different consent language, and a visible in-product explainer of the difference (which is itself a parent-valued feature — most parents of newly-504'd children do not know). Never render the string 'IEP/504' in user-facing copy again. For MCPS specifically, state plainly in sales material that the product does not integrate with, write to, or read from MOIEP/Student Compass, and that nothing it produces is an IEP record — that single sentence removes the largest objection an Office of Special Education reviewer will raise.

### SPED-07 — A commercial 'diagnostic' that surfaces a suspected disability has no Child Find pathway and risks contaminating a real evaluation

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.89 |

**What the artifact says**
> Diagnostics tab header: 'PhD-Level Diagnostic Assessments'; Diagnostic Agent tools include 'Risk flag detector (crisis + academic)' and output 'counselor referral flag'. Domain 3 includes 'phonological awareness — decoding and fluency baseline assessment'. Nothing in the artifact describes what happens when results suggest an unidentified disability.

**The problem**

Two opposite errors are both live. First, under-response: IDEA's Child Find obligation (34 CFR 300.111) runs to the public agency, and a product used by MCPS families that repeatedly flags decoding deficits in unidentified students is generating exactly the information Child Find exists to act on. The product has no defined, documented route from 'flag' to 'parent makes a written request for an initial evaluation', which is the only legally meaningful action available to a vendor. Second, over-reach: calling an unvalidated self-report a 'diagnostic' invites families and staff to treat it as evaluation data. It is not. Under COMAR 13A.05.01.05–.06, assessment and eligibility determination are agency functions with defined procedures and a 30-day IEP meeting timeline after evaluation; vendor output has no standing and, if submitted, can muddy the record. Using the word 'diagnostic' at all is a liability the product gets nothing for.

**Evidence**

34 CFR 300.111 Child Find (section number from primary regulation; UNVERIFIED in this session — confirm on eCFR). COMAR 13A.05.01.05 (Assessment) and 13A.05.01.06 (Evaluation, Reevaluation, and Eligibility), including the 30-day post-evaluation IEP meeting requirement, verified as existing sections via mdrules.elaws.us. The specific MCPS referral form and timeline are UNVERIFIED; the MCPS Special Education Compliance Manual (sites.google.com/mcpsmd.net/mcps-special-education-complia) is the place to check.

**Recommendation**

Rename the instrument from 'diagnostic' to 'Learning Profile' or 'Study Skills Inventory' across all ten tabs, and add a Child Find response protocol: when results cross a defined threshold, the product (a) states in plain language that this is not a diagnosis and cannot identify a disability, (b) explains the parent's right to request an initial evaluation in writing, (c) generates a dated, editable written request addressed to the principal and the school's special education staff, with the required elements, that the parent sends, and (d) logs that the disclosure was shown. Build an equivalent protocol for students who already have an IEP: route the finding to 'bring this to your next IEP meeting', with a printable summary.

### SPED-08 — The MCLSS paraeducator certification is unsellable to its named buyer: wrong price, wrong time, wrong credential

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.87 |

**What the artifact says**
> Business Model: 'Paraeducator Certification $299 / individual — 80-hour MCLSS program; CEU-eligible; MCPS partnership'. Target: '100 paraeducators Year 1'. Certification tab: 'Paraeducator Track | 12 domains | 80 hours | CEU-eligible | MCPS District Partnership'.

**The problem**

Three independent reasons a real MCPS paraeducator will not buy this. (1) Money: MCPS paraeducators are SEIU Local 500 supporting-services employees on a 10-month schedule with a 17-step scale; $299 of personal, after-tax money is a meaningful fraction of a paycheck for a credential with no salary consequence. (2) Time: there is no 80-hour block in a contractual duty day, and MCPS does not pay supporting-services staff to complete vendor coursework outside it unless it is bargained or district-funded PD. (3) Recognition: MSDE and ESSA recognise a specific, narrow set of paraprofessional qualifications — two years of higher education, an associate degree or higher, or a passing score on a state-approved assessment. Maryland's approved assessment is changing right now: ETS is retiring the ParaPro in August 2026, and MSDE has moved to approve ETS ParaPathways (Reading & Writing and Mathematics subtests) and two Pearson Foundations of Classroom Support exams for Title I paraprofessionals. An unaccredited vendor certificate counts toward none of that. Separately, 'CEU-eligible' is not Maryland's unit at all (see SPED-09). As designed, MCLSS asks the lowest-paid staff in the building to pay for a credential nobody will recognise.

**Evidence**

ESSA §1112(c)(6) Title I paraprofessional requirements and the two-years-of-college / AA / approved-assessment options, per MSDE Title I Part A Program Guide (https://msde.maryland.gov/media/18704). ParaPro retirement and the ParaPathways/Pearson replacements: MSDE State Board item, 'Assessments for Paraprofessionals Working in Title I Schools', Feb 2026 (https://marylandpublicschools.org/stateboard/documents/2026/0224/assessments-for-paraprofessionals-working-in-title-i-schools-a.pdf) — note final State Board approval is UNVERIFIED. MCPS/SEIU Local 500 salary structure and 17-step SEIU scale: MCPS salary schedules (https://www.montgomeryschoolsmd.org/departments/ersc/employees/pay/schedules/salary/) and SEIU contract amendment SY2023-2026. Exact current paraeducator hourly rates UNVERIFIED — the published FY2027 schedule PDF is the place to check.

**Recommendation**

Flip the buyer and shrink the product. (1) The buyer is the school or the Office of Special Education, paying out of IDEA Part B CEIS funds or Title I PD, not the individual. Price it per-cohort, per-school. (2) Cut 80 hours to a 6–10 hour micro-credential on one job-embedded skill a para can use the next morning — Check-In/Check-Out fidelity, or accommodation implementation logging. (3) Build a genuinely useful free adjunct: a ParaPathways/Pearson exam prep module aligned to the assessment MSDE is actually approving, which solves a problem MCPS has right now as the ParaPro sunsets. That gets you in the building. (4) Stop claiming 'MCPS District Partnership' until a signed agreement exists; it is a claim of validation that has not occurred.

### SPED-09 — 'CEU-eligible' and 'graduate credit' are the wrong Maryland currencies and are asserted without the approval that creates them

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Certification tab: MCLSS '80 hours | CEU-eligible'; MMEC '120 hours | CEU-eligible | University graduate credit partnership'; 'University Partnership Track — 3 graduate credits via partner university | Stackable toward MAT or Ed.D. | Target partners: Howard University, Morgan State, UMCP'.

**The problem**

Maryland educators do not renew or advance certificates with 'CEUs'. The state uses MSDE-approved Continuing Professional Development (CPD) credit and, increasingly, Professional Development Points (PDPs), where one MSDE-approved CPD credit equals 15 PDPs and one CPD credit is treated as at least 15 hours of activity. CPD approval is a formal MSDE process: provider application, roughly a 6–8 week review recommended at least eight weeks before the course start date, five-year approval for regular course offerings, a separate accessibility review for online courses, and participant documentation on the MSDE CPD Completion for Credit Form. None of this is in the artifact, and 'CEU-eligible' written next to an MCPS teacher audience signals to that audience that the author has not been through Maryland certification. The graduate-credit claim is worse: naming Howard, Morgan State and UMCP as 'target partners' in a document headed 'Master Project Document' reads as a partnership claim. Graduate credit requires an institutional agreement, faculty of record, a syllabus through the university's curriculum process, and registrar enrolment — typically a 12–24 month process.

**Evidence**

MSDE Continuing Professional Development Manual and provider application (https://msde.maryland.gov/media/18071; https://www.marylandpublicschools.org/about/Documents/DEE/ProgramApproval/CPD_Manual_August_2022.pdf — dated Aug 2022, fees/procedures may have changed); MSDE Professional Development Points page (https://msde.maryland.gov/educator-licensure-certification/professional-development-points) establishing 1 CPD credit = 15 PDPs; MSDE Professional Development Points Guidelines for Providers (https://marylandpublicschools.org/about/Documents/DEE/ProgramApproval/Professional-Development-Points-Guidelines-for-Providers-A.pdf). COMAR 13A.12.01 was NOT located in search; the provider guide cites COMAR 13A.12.02.06E — do not cite 13A.12.01 without checking it.

**Recommendation**

Replace every 'CEU-eligible' with either 'MSDE CPD approval pending' or nothing. Start the MSDE CPD provider application now — it is a 6–8 week review with a five-year approval and an accessibility review, so it is a long-lead item that should sit in Phase 1, not Phase 3. State PDP equivalence (15 PDPs per CPD credit) in the marketing, because that is the number a Maryland teacher actually tracks. Remove all three university names until a signed MOU exists, and replace with 'university partnership not yet established'.

### SPED-10 — Load-bearing statistics across the document appear to be invented, including the headline MCPS figure

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.86 |

**What the artifact says**
> Gap Analysis: 'Hoover-Dempsey & Sandler (1997)... 73% of MCPS families lack both.' Also: '85% of test anxiety interventions validated only on white, middle-class, neurotypical populations (Zeidner, 1998; von der Embse et al., 2018)'; 'Culturally affirming instruction raises Black student achievement (ES: 0.8)'; 'Self-directed learning produces 40% greater intrinsic motivation'; 'Mixed-topic practice beats blocked practice... by 43%'; 'Study 90% Faster'; 'Stereotype threat... suppress performance 15–20%'; '38% of middle schoolers experience debilitating test anxiety (Zeidner, 1998)'.

**The problem**

The '73% of MCPS families' figure is attached to a 1997 parental-involvement paper that cannot possibly contain an MCPS-specific statistic, and no MCPS or MSDE survey producing it is cited. The pattern repeats: a real author and year are attached to a precise percentage the cited work does not support. '90% faster study' is not a research finding in any literature. The 0.8 effect size for culturally affirming instruction, the 43% interleaving figure and the 40% intrinsic-motivation figure are each stated to two significant figures with no study, sample or outcome named. This is the single greatest threat to the founder's credibility with an MCPS special education audience: a doctoral-level reader will test the first citation they recognise, find it does not say that, and discount everything else in the document — including the parts that are sound. It also directly violates the founder's own stated operating principle, 'evidence before claims'.

**Evidence**

INFERENCE from internal inconsistency between the cited sources and the attached numbers. I did not attempt to verify each individual figure; I verified the general methodological point in the areas I checked (e.g. SRSD effect sizes vary meaningfully across meta-analyses — Graham & Harris report 1.14 vs 1.17 for the same study across sources, and IES describes SRSD effects 'typically exceeding 0.85' with a 1.0–2.55 range, which is how an honest effect-size claim reads). Hoover-Dempsey & Sandler (1997) is a real model paper about parental involvement; it contains no MCPS data.

**Recommendation**

Run a citation audit over every numeric claim in the artifact. For each: either (a) produce the source, page and the exact figure, (b) replace with a range and a hedge, or (c) delete. Replace the '73% of MCPS families' claim with real MCPS data you can defend (see SPED-11). Adopt a house rule matching AEOS's 'evidence before claims': no percentage ships without a resolvable citation in a bibliography file in the repo, and an evidence-tier label on every claim in the deck.

### SPED-11 — The product's strongest reason to exist — MCPS disproportionality — is never named, and MCPS's real numbers are better than the invented ones

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.84 |

**What the artifact says**
> Gap Analysis tab's entire case rests on 'Zero culturally affirming test anxiety programs exist for African American/BIPOC youth' and 'Eurocentric curriculum strips BIPOC children of intellectual identity before age 12'. The words 'disproportionality', 'over-identification', 'Child Find', 'MTSS' and 'discipline' appear nowhere in the document.

**The problem**

Disproportionate identification, placement and discipline of Black students in special education is the defining equity problem of the field, it is federally regulated, it is measured, it has money attached, and MCPS is currently inside it. MCPS has reported that the state identified continued disproportionality in suspensions for Black students with disabilities, with roughly $5,638,869 of IDEA funds implicated — because a district identified as significantly disproportionate must reserve 15% of its IDEA Part B funds for comprehensive coordinated early intervening services (CCEIS). MSDE uses a 2.0 risk-ratio threshold with a minimum cell size no greater than 10, applies multi-year and reasonable-progress options, and has put a $3M ROWS grant pool behind reducing over-identification. Meanwhile MCPS's own outcome gaps are public: reporting in Oct 2026 put DIBELS benchmark attainment at 38.6% for students with IEPs, 46% for FARMS-eligible students, and about 33% for English Language Development students. The founder is writing from inside MCPS and arguing from invented percentages when a documented, budgeted, named compliance problem is sitting there with a 15% set-aside attached to it. That set-aside is the single most buyable budget line this product could attach to.

**Evidence**

MCPS report of continued state-identified disproportionality in suspensions for Black students with disabilities and the $5,638,869 IDEA figure (Nov 2025), via CitizenPortal coverage of the MCPS board item — PRIMARY SOURCE UNVERIFIED, confirm against the MCPS Board of Education BoardDocs item and MSDE's determination letter. MSDE methodology (risk-ratio threshold 2.0, cell size ≤10, multi-year and reasonable-progress options): Blueprint for Maryland's Future, 'Issue Brief: Significant Disproportionality', July 2024 (https://blueprint.marylandpublicschools.org/wp-content/uploads/sites/20/2024/07/Issue-Brief-Significant-Disproportionality-A.pdf). 63% of Maryland districts identified in SY2019-20 and SY2020-21 vs 7-8% in prior years, same brief / K-12 Dive (https://www.k12dive.com/news/Maryland-overidentification-special-education/690732/). MCPS DIBELS attainment figures: Bethesda Magazine, 26 Oct 2026 (https://bethesdamagazine.com/2026/10/26/demographic-disparities-mcps-academic-achievement/). MCPS 2024-25 enrolment ~159,671; 2025-26 exact IEP/FARMS/EL percentages UNVERIFIED — the MCPS Official Enrollment 2026 report and the MCPS Schools at a Glance profiles are the sources, and ww2.montgomeryschoolsmd.org did not resolve from this session's network.

**Recommendation**

Rewrite the Problem Statement around disproportionality and name it: over-identification of Black students in specific categories, disproportionate discipline of Black students with disabilities, and the MCPS CCEIS set-aside those findings trigger. Pull the actual figures from the MCPS Official Enrollment report, the MCPS Schools at a Glance profiles, MSDE's Special Education/Early Intervention Services Census (Oct 1 child count) and MSDE's disproportionality determinations, and cite them with dates. Then position the product as a Tier 1/Tier 2 general-education support that reduces referrals and reduces exclusionary discipline — which is literally what CCEIS dollars must be spent on.

### SPED-12 — No MTSS/tier structure, no progress monitoring method, and no measurable goals — the three things a SPED office looks for first

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> The only appearances are MCLSS domain 10, 'Data Collection & Progress Monitoring — Formative assessment tools, behavioral data collection, progress monitoring charts, data-informed adjustment', and the App Design 'Test anxiety severity tracker over time'. There is no tier model, no CBM, no goal structure, no decision rules, no fidelity measure anywhere in ten tabs.

**The problem**

Everything in a modern special education office is organised by tier and by data. A product that cannot say which tier it operates in has no place in the system and no budget code. More damagingly, the artifact proposes to generate a 'Monthly IEP Progress Report... formatted for IEP meeting submission' without ever specifying what is measured, how often, against what goal, with what decision rule, or at what reliability. IEP progress reporting is a legal requirement tied to measurable annual goals; feeding a team a report built from app-engagement telemetry and self-rated anxiety is not progress monitoring, it is dashboard theatre, and a school psychologist will say so in the first meeting. Curriculum-based measurement exists precisely because it provides brief, repeatable, standardised, sensitive-to-growth indicators with established decision rules (trend line vs goal line, four-point rule). None of that infrastructure is present.

**Evidence**

34 CFR 300.320(a)(2) and (a)(3) require measurable annual goals and a description of how progress toward them will be measured and reported (section numbers from primary regulation; UNVERIFIED in this session — confirm on eCFR). COMAR 13A.05.01.09 (IEP Document) requires present levels of performance, verified via https://www.law.cornell.edu/regulations/maryland/COMAR-13A-05-01-09. CBM as the standard progress-monitoring method is ESTABLISHED in the field; the National Center on Intensive Intervention's progress-monitoring tools chart is the source to cite for specific validated measures.

**Recommendation**

Declare a tier. The honest answer for this product is Tier 1 (universal study-skills and anxiety instruction in general education) with a Tier 2 small-group option — NOT a special-education replacement, which also answers the segregation concern in SPED-18. Then build a real progress-monitoring spine: see the 'Progress Monitoring Spine' addition. Separately, remove the 'formatted for IEP meeting submission' language from the Monthly IEP Progress Report until the measures behind it are defensible; replace with 'parent-facing summary you may choose to share with your IEP team'.

### SPED-13 — VARK modality preference is a design input; the meshing hypothesis it depends on is not supported

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.91 |

**What the artifact says**
> Diagnostics, Domain 5 Neurodivergent & Sensory Profile: '5.1 VARK modality preference (Visual / Auditory / Kinesthetic / Reading-Writing)'. Domain 4: '4.8 Preferred cultural learning style (call-response, storytelling, movement)'. Course Design cites UDL 3.0 elsewhere.

**The problem**

The meshing hypothesis — that instruction matched to a stated modality preference improves learning — has repeatedly failed to find support. Pashler, McDaniel, Rohrer and Bjork's 2008 review in Psychological Science in the Public Interest concluded there was no adequate evidence base to justify incorporating learning-styles assessments into general educational practice; Willingham, Hughes and Dobolyi (2015) found virtually no evidence for meshing. Learners do have preferences; matching to them does not improve outcomes. Including VARK in a 'psychometrically validated' instrument is the fastest way for a school psychologist to conclude the instrument was not built by someone who reads the literature — and it sits awkwardly next to the UDL citations, since UDL's multiple means of representation is a universal-design principle, not a learner-matching principle. The 'preferred cultural learning style' item carries the same problem plus an essentialism risk: inferring instructional method from a child's ethnic identity is the mechanism of the stereotyping the product says it opposes.

**Evidence**

Pashler, McDaniel, Rohrer & Bjork (2008), 'Learning Styles: Concepts and Evidence', Psychological Science in the Public Interest 9(3) — conclusion that there is no adequate evidence base; Riener & Willingham (2010), 'The Myth of Learning Styles', Change; Willingham, Hughes & Dobolyi (2015), Teaching of Psychology — 'virtually no evidence' for meshing. Verified via multiple secondary summaries including PMC5366351; the primary articles themselves were NOT retrieved in session. A dissenting view exists (Felder 2020) arguing the critique is overstated for non-VARK models — note it, but it does not rescue VARK.

**Recommendation**

Delete item 5.1 and item 4.8. Replace with UDL-correct design: offer every piece of content in multiple representations to EVERY student, all the time, and let the student choose in the moment — then log which representation they actually chose and whether it helped, which is real data. Replace 'preferred cultural learning style' with student-chosen content interest and student-chosen example contexts, which is culturally responsive without being essentialist.

### SPED-14 — English Learners are effectively absent from a product aimed at MCPS, where EL is one of the largest service populations

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.8 |

**What the artifact says**
> Phase 4 (Months 10–12): 'Spanish-language version (beta) launched'; KPI 'Spanish beta: 50 families'. Parent diagnostic framework: 'Spanish available'. No EL construct appears in the 52-domain student instrument, no EL plan appears in the accommodation engine, and the EL + disability intersection is never mentioned.

**The problem**

MCPS has a large multilingual population and a FARMS/EL/SWD overlap that any MCPS practitioner would treat as the central design constraint, not a month-12 translation task. The artifact cites Cummins (1979) on CALP in its literacy domain — i.e. it invokes a second-language acquisition framework — then builds no EL functionality at all. Operationally this also breaks the accommodation module: Maryland's accommodations manual treats the EL Plan as a third documentation vehicle alongside the IEP and the 504 plan, with its own accommodations, so 'IEP/504' as a binary cannot represent an MCPS student who has both an IEP and an EL plan, which is a very common profile. Translating the UI to Spanish at month 12 is not an EL strategy; it does not address language-of-instruction decisions, the distinction between a language difference and a disability (central to disproportionality), or the other languages in MCPS.

**Evidence**

Maryland Assessment, Accessibility and Accommodations Manual (Aug 2025) treats IEP, 504 and EL Plans as parallel documentation vehicles for accommodations and routes unique accommodation requests through the local Learning Accommodations Coordinator (https://marylandpublicschools.org/programs/Documents/Special-Ed/IEP/MAM508102017.pdf). MCPS OLO budget-equity report notes FARMS-eligible students outnumber English learners roughly 2:1 and students with disabilities roughly 3:1 (https://assets.montgomerycountymd.gov/files/2026-07/OLOReport2026-9BudgetEquityinMCPS.pdf). EXACT MCPS EL percentage for 2025-26 is UNVERIFIED — get it from the MCPS Official Enrollment report or Schools at a Glance.

**Recommendation**

Add plan_type 'EL_plan' to the data model in v1, add an EL-status and home-language field to intake, and put language-of-item-presentation under student control rather than behind a month-12 feature flag. Add a short module for staff on distinguishing language acquisition from disability — this is both an EL need and a disproportionality need, and it is the kind of content an MCPS office will actually ask for. Pull MCPS's top five home languages from the enrolment report and plan against those, not 'Spanish beta'.

### SPED-15 — The design implicitly serves only mild/moderate disability; students with significant cognitive disabilities and twice-exceptional students are excluded

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.82 |

**What the artifact says**
> The entire student product assumes a reader who can complete a 35–45 minute Likert self-report, build an Anki deck, use 'speed reading', and 'design THEIR OWN study system'. The only mention of twice-exceptionality is one bullet in the Staff diagnostic, Domain 3: 'Twice-exceptional learners — gifted + learning difference intersections'. Alternate assessment, significant cognitive disability, AAC and functional curriculum appear nowhere.

**The problem**

'Neurodivergent' is used throughout as a synonym for 'ADHD, dyslexia, mild ASD'. In an MCPS middle school, a special education caseload also includes students with intellectual disability, multiple disabilities, significant communication needs and students on the alternate assessment aligned to alternate academic achievement standards (DLM in Maryland). The product cannot serve them and should say so plainly rather than market to 'students with IEPs' as an undifferentiated 6.4M TAM. The reverse error also matters: twice-exceptional students are a real MCPS population with a specific unmet need, and the artifact has the right instinct but one bullet of content.

**Evidence**

INFERENCE from the artifact's own feature set. Maryland's alternate assessment pathway and its eligibility determination by IEP teams is documented in the Maryland Assessment, Accessibility and Accommodations Manual (https://marylandpublicschools.org/programs/Documents/Special-Ed/IEP/MAM508102017.pdf). The MCPS TAM claim '6.4M students with IEPs' is UNVERIFIED — the federal child count is published in the Annual Report to Congress on IDEA implementation; check the current figure and cite it.

**Recommendation**

State the served population explicitly in one sentence on the Project Doc tab: 'designed for students accessing grade-level general education curriculum with accommodations; not designed for students on alternate academic achievement standards.' This increases credibility rather than shrinking the market — a SPED director trusts a vendor who knows the edges of their product. Then, if 2e is a real interest, build it out properly: it is an underserved, high-advocacy, high-willingness-to-pay segment in Montgomery County specifically.

### SPED-16 — State assessment accommodations are a separate regime the app's 'auto-apply' model actively undermines

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.86 |

**What the artifact says**
> App Design, Accommodations Auto-Applied: 'Extended Time — Auto-adjusts ALL timers proportionally; paces Anki and study sessions per IEP ratio'; 'Read-Aloud / TTS — One-tap TTS on all content, assessments, and instructions'.

**The problem**

Maryland runs a distinct accommodations regime for state assessment through the Maryland Assessment, Accessibility and Accommodations Manual: accommodations must be justified and documented in the IEP, 504 or EL plan, must be used in instruction as well as assessment, accessibility features available to all students are explicitly NOT accommodations, and any accommodation not on the state list requires a Unique Accommodation Request submitted by the local Learning Accommodations Coordinator roughly six weeks before testing. Two instructional consequences follow. (1) A read-aloud of a reading comprehension passage may be a non-standard accommodation on MCAP ELA with score consequences; an app that offers one-tap TTS 'on all content, assessments, and instructions' is teaching a student to depend on something they may not have on the test. (2) 'Auto-adjusts ALL timers proportionally' invents an 'IEP ratio' that is not how extended time is written or administered. The artifact's own risk card calls this 'IEP accommodation mismatch' and proposes to 'revert to last confirmed IEP state' — correct instinct, wrong system: there should be nothing to revert from.

**Evidence**

Maryland Assessment, Accessibility and Accommodations Manual, Aug 2025 edition (https://marylandpublicschools.org/programs/Documents/Special-Ed/IEP/MAM508102017.pdf): documentation requirement in IEP/504/EL plan; accessibility features distinguished from accommodations; Unique Accommodation Request via the local LAC six weeks before testing; alternate assessment eligibility determined by IEP teams. The specific MCAP read-aloud/ELA score-consequence rule is UNVERIFIED — confirm in the current manual's accommodation fact sheets before asserting it.

**Recommendation**

Build the module around alignment and fidelity rather than auto-application. Represent each accommodation with: text as written in the plan, whether it is instructional, assessment, or both, whether it is a state-approved assessment accommodation under the current MAAAM, and a per-session used/offered/declined log. Then surface the most valuable thing this product can honestly give a team: 'this accommodation is in the plan but was declined in 18 of 20 sessions' or 'this accommodation is used in instruction but is not documented for assessment'. That is a finding an IEP team will act on, and it is legally clean.

### SPED-17 — The evidence-based practices a SPED doctorate would expect for this exact population are missing, replaced by weaker or unvalidated methods

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Course Design tab's method set is: NASA BARS, 'Wade Cutler's Triple Reading Speed', Skillful Teacher, African-Centered Metacognitive Science, Child Liberation Studies, plus six note-taking methods. Certification Module 9: 'Study 90% Faster — With and Without AI'; Module 6: 'Speed Reading'.

**The problem**

For middle schoolers with IEPs, the field has a specific, replicated toolkit and almost none of it is here. Self-Regulated Strategy Development is the most robustly supported writing intervention for students with LD, with effect sizes commonly above 0.85 and frequently above 1.0 for writing quality; it is absent. The Homework, Organization and Planning Skills (HOPS) intervention was built and trialled for exactly this population — middle school students with ADHD, delivered by school mental health providers in brief one-to-one sessions — with reported parent-rated effects around d = 0.85–1.05 on organised action, planning and homework completion, plus GPA gains; it is absent, while the artifact invents 'BARS' for the same job. Self-determination and self-advocacy instruction (e.g. SDLMI) is absent despite being directly aligned to IDEA transition requirements and despite the artifact's entire 'child liberation' thesis being an unoperationalised version of it. Check-In/Check-Out as a Tier 2 practice with fidelity requirements, daily behaviour report cards, explicit strategy instruction and guided notes are all absent. Meanwhile 'speed reading' and '90% faster study' occupy two of twelve student modules — speed-reading claims of comprehension-preserving large speed gains are not supported, and for students with decoding deficits this is the opposite of indicated practice.

**Evidence**

SRSD: IES, 'Improving Academic Achievement through Instruction in Self-Regulated Strategy Development' (https://ies.ed.gov/learn/blog/improving-academic-achievement-through-instruction-self-regulated-strategy-development-science) — effects typically exceeding 0.85, commonly 1.0–2.55; Graham & Harris LD meta-analysis reported at d≈1.14–1.17 for writing quality (sources disagree slightly — verify the primary before citing a single number); Graham et al. 2023 middle/high school synthesis, d=1.16 for quality (via Ray 2024, https://nasenjournals.onlinelibrary.wiley.com/doi/full/10.1111/1471-3802.12681). HOPS: Langberg et al., School Psychology Review 2012 (PMC4209597) — n=47, grades 6-8, provider-delivered, parent-rated d=0.88 organised action, 1.05 planning, 0.85 homework completion; larger 2018 RCT n=280. Note HOPS teacher-rated effects were frequently null — report that honestly. CICO meta-analytic effect size NOT verified in session.

**Recommendation**

Rebuild the student module sequence around named, citable practices and map each to a product surface: SRSD → a writing module with the mnemonic-driven strategy and self-statements; HOPS → replace 'BARS' with a HOPS-aligned materials-organisation, planner and homework-recording routine, and cite Langberg rather than NASA; SDLMI → make 'child liberation' concrete as goal-setting, self-monitoring and IEP-meeting participation, which is also IDEA transition-aligned; CICO → the Tier 2 daily check-in feature with an explicit fidelity measure; guided notes and explicit strategy instruction → replace the six-note-taking-methods buffet with one taught to mastery. Delete the speed-reading modules or retitle them as previewing/skimming strategies with honest claims.

### SPED-18 — An identity-affirming product built outside general education risks becoming a parallel, segregated service

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `EXPERT-OPINION` |
| **Lens confidence** | 0.75 |

**What the artifact says**
> The product is a standalone app with its own 'cohort', its own certifications, its own 'Ubuntu Learning Circle', its own curriculum and its own credentials, delivered primarily family-direct at $399/yr. Nothing in the artifact connects it to the general education classroom, the MTSS structure, or the student's actual teachers.

**The problem**

The artifact correctly identifies that Black neurodivergent students are failed by a Eurocentric default, and then responds by building a separate system for them to join. The field's hardest-won lesson about segregated services is that they tend to lower expectations, reduce access to grade-level curriculum, and become the place a student is sent rather than a support that travels with them — which is the mechanism behind LRE in the first place (34 CFR 300.114). A culturally sustaining intervention that lives entirely outside the classroom also has no mechanism to change what happens in the classroom, which is where the disproportionality is produced. The risk is not theoretical: a well-funded parallel program for Black students with IEPs, sold to their families, is exactly the shape a civil-rights reviewer would ask hard questions about.

**Evidence**

EXPERT-OPINION / INFERENCE. LRE requirement at 34 CFR 300.114 (section number from primary regulation, UNVERIFIED in session). The culturally sustaining pedagogy literature (Ladson-Billings, Paris & Alim) and the disproportionality literature both locate the remedy inside general education and MTSS rather than in parallel provision; I did not verify a specific source making this exact argument about commercial products.

**Recommendation**

Anchor the product inside Tier 1 and MTSS: design the core as something a general education teacher runs with a whole class, with the culturally sustaining content as the default for everyone, not as a targeted add-on for Black students. Make the family product the supplement to the classroom version, not the other way round. In the school-facing pitch, lead with 'this runs in your general education classroom and reduces referrals', which is simultaneously the LRE-correct design, the CCEIS-fundable design, and the one that actually touches disproportionality.

### SPED-19 — The $399/yr family-direct model is misaligned with the stated target population, and the named funding sources have restrictions the artifact ignores

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.78 |

**What the artifact says**
> Business Model: 'Family Subscription $49/mo | $399/yr... Primary revenue | Goal: 500 families Year 1'. Customer profile: 'Parent / Guardian — Under-resourced, wants to help'. 'Federal Grant Funding $50K–$500K / grant — Title I eligibility (high-poverty schools); IDEA eligibility'. Year 1 projection: $391,850 revenue, ~$175,000 costs, '~$216,850' net.

**The problem**

The artifact names its target parent as 'under-resourced' and then prices at $399/yr as the primary revenue line — 500 of them in year one, from a standing start, with no sales team. The grant line is worse because it is casually stated: Title I funds flow to LEAs and schools under program rules with supplement-not-supplant constraints and set-aside rules; IDEA Part B funds are for the excess costs of educating children with disabilities with their own supplement-not-supplant and maintenance-of-effort constraints — these are not grants a startup applies for, they are district funds a district may spend on a vendor if the use is allowable. The one genuinely well-matched IDEA pathway, CCEIS, is never named. On the Maryland side, Blueprint Concentration of Poverty Grants have statutorily defined allowable uses (personnel and wraparound services, with a community school needs assessment within one year of receipt) that are currently being amended — a vendor needs to check allowability against the current statute, not assume. Finally, the Year 1 net of ~$216,850 treats $100,000 of hypothetical grant money as revenue and omits founder salary, legal counsel (which the risk card says is needed from Day 1), MSDE CPD approval costs, security audit, and pen testing — which the same document says will be quarterly.

**Evidence**

Blueprint Concentration of Poverty Grant structure, allowable uses for personnel and wraparound services, and the one-year community school needs assessment requirement: Blueprint for Maryland's Future funding page (https://blueprint.marylandpublicschools.org/funding-2/) and DLS fiscal note on HB 352 (2026) describing changes to allowable CPG uses (https://mgaleg.maryland.gov/2026RS/fnotes/bil_0002/hb0352.pdf); SB 289 testimony on eliminating the sunset (https://mgaleg.maryland.gov/cmte_testimony/2026/bat/1qzz6NeIj7ppHoioFvFkDsdmSMfOpCrIw.pdf). Ed. §5-234 minimum school funding at 75% of per-pupil amounts plus 100% of the CPG per-pupil grant. Title I supplement-not-supplant and IDEA excess-cost/MOE rules are ESTABLISHED federal requirements; the specific MSDE Title I set-aside guidance was NOT retrieved — check MSDE's Title I Part A Program Guide (https://msde.maryland.gov/media/18704).

**Recommendation**

Restructure to school-paid-first. Price a school pilot under the $25,000 MCPS Board threshold, target CCEIS dollars (which MCPS must already spend on early intervening services because of its disproportionality finding) and Blueprint CPG wraparound budgets at high-FARMS schools, and make the family product free or near-free where the school has licensed it — which solves the affordability contradiction and creates the usage data you need. Rebuild the Year 1 model with grants excluded from revenue, founder comp included, and legal/CPD/security costs line-itemed. Before writing a grant line into any deck, get an allowability memo for each fund source.

### SPED-20 — 'No comparable app exists' is a claim the artifact cannot support and that MCPS staff will immediately contradict

| | |
|---|---|
| **Severity** | `LOW` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.8 |

**What the artifact says**
> Gap Analysis, App Gaps: '🏆 Market Conclusion: No Comparable App Exists... MindUnlock Academy is the first of its kind. TAM: 6.4M students with IEPs, 74M K-12 parents, 1.3M paraeducators'. The six apps compared are Anki, Headspace/Calm, Duolingo, Notion/Obsidian, Google Classroom and Brainly.

**The problem**

The comparison set is consumer apps, not the category this product competes in. Inside MCPS the relevant incumbents are the district's existing intervention, screening, SEL and progress-monitoring platforms, plus the IEP system itself (MOIEP/Student Compass), plus whatever MTSS data system the district uses. An MCPS reader will look at a comparison table containing Duolingo and conclude the author has not scanned the district's own tool inventory. The 'meets our needs' percentages (45%, 20%, 30%, 15%, 10%, 25%) have no stated methodology, which compounds the citation-integrity problem in SPED-10. The '38 apps reviewed' and '47 peer-reviewed sources' figures in the tab header are likewise unsupported.

**Evidence**

INFERENCE. I could NOT verify which specific intervention or SEL platforms MCPS currently licenses — MCPS's approved Technology Resources list and any Board procurement items are the sources, and ww2.montgomeryschoolsmd.org did not resolve from this session, so the district's vendor list could not be retrieved. This should be treated as an open item, not a finding of fact about specific competitors.

**Recommendation**

Replace the consumer-app table with a real district-tool scan: pull MCPS's published approved digital tools / Technology Resources list and recent Board of Education procurement items, identify the three tools whose job overlaps yours, and state honestly what you do that they do not. Either publish the scoring methodology behind the percentages or delete them. Delete 'first of its kind'. Replace the TAM paragraph with a serviceable obtainable market: MCPS middle schools, number of students with IEPs in grades 6-8, and what a per-school price yields — a number a principal can check.


---

## What is missing and should be added

### The SPED-correct v1 instrument: a 15-minute, three-informant Learning Profile (not a 52-domain diagnostic)   `ESTABLISHED`

**Why it matters.** The current 52-domain, 35–45 minute, single-rater Likert instrument cannot measure most of what it claims to measure and will produce unusable data from the exact population it targets. A shorter, multi-informant, method-matched instrument is both more defensible and cheaper to build — and it is the version a school psychologist will not object to.

**What to build.** Three linked short forms sharing one schema. (A) STUDENT SELF-REPORT, 22 items, 12–15 minutes, 4-point forced choice (no neutral midpoint, which suppresses straight-lining), grade-4 readability ceiling verified by a readability tool, every item audio-recorded by a human voice not TTS, one worked example item, a progress bar, and a save-and-resume. Content restricted to what only the student knows: cognitive worry; somatic/emotionality; subject-specific anxiety (math, ELA, science, social studies); format-specific anxiety (quiz, unit test, state test, oral, group); avoidance behaviours; what they actually do the night before a test; homework start time and place; sleep; who helps them; one open 'what makes tests hard for you' free-text/voice item. (B) CAREGIVER FORM, 15 items, 7 minutes, observable behaviours only, parallel wording to the student form so discrepancy is computable. (C) TEACHER/PARA FORM, 10 items, 3 minutes — this is the one that makes the whole thing credible, and it is also the hook into the school. Scoring: report only two scaled scores in v1 (test anxiety: worry and emotionality subscales) plus a descriptive profile; report NOTHING as a level or a deficit. Validity: include two directed-response checks and a response-time floor, but handle failure by re-engaging the student, not by flagging them as 'gaming'. Explicitly drop: VARK (5.1), cultural learning style (4.8), working memory (2.1), processing speed (5.5), phonological awareness (3.1), reading fluency WPM/prosody (3.2), morphological awareness (3.5) — these are performance constructs and either need real timed probes or need to leave v1. Label the output 'Learning Profile — not a diagnosis, not an evaluation, not a basis for eligibility' on every screen and every PDF.

**Evidence.** Multi-informant necessity: adolescents with ADHD self-report EF difficulty below parent and teacher report (Steward et al., J Atten Disord, doi 10.1177/1087054714530782; BRIEF adolescent/parent/teacher agreement study, Child Neuropsychology doi 10.1080/09297049.2023.2174506). Forced-choice and readability control are standard self-report design practice for youth instruments. Spielberger's TAI and the worry/emotionality distinction (Liebert & Morris 1967) — which the artifact already cites correctly — are the right backbone for the anxiety subscales; use published, properly licensed instruments where they exist rather than writing new items.

### The SPED-correct accommodation module: an Accommodation Fidelity Log, with a one-way data wall   `ESTABLISHED`

**Why it matters.** This replaces the single most legally dangerous feature in the artifact with the single most useful thing a product can honestly offer an IEP team. Teams currently have almost no data on whether documented accommodations are actually offered and used — that is a real, unfilled gap, and filling it is both compliant and sellable.

**What to build.** A read-only-for-the-AI accommodation record with a hard architectural guarantee that no agent can write to it. Fields per accommodation: verbatim text as written in the plan; plan_type (IEP | 504 | EL_plan); setting (instruction | assessment | both); state_assessment_status (approved under the current MAAAM | not approved | unique accommodation request required); entered_by (human user id) ; entered_date; effective_from/effective_to; source_document_reference (a reference, not the document). Then the actual feature: a per-session log capturing offered / used / declined / not applicable, plus an optional one-tap student reason. The app's own behaviour (TTS availability, timer length, chunk size) is set from this record but is presented as a STUDENT-CONTROLLED setting the student can change at any time, with changes logged — not as an auto-applied entitlement. Output: a dated, printable 'Accommodation Use Summary' the parent or teacher may choose to bring to a meeting, headed 'Informational only — not an IEP progress report and not a basis for changing accommodations. Accommodation changes are made by the IEP team (34 CFR 300.324) with prior written notice (34 CFR 300.503).' Build the write-prohibition as a database constraint plus a test in the committed security mutation suite, identical in spirit to the RLS tests AEOS already has. For v1, do not parse IEP PDFs at all: a human types in the accommodations. This removes an entire class of Subpart F exposure and ships faster.

**Evidence.** 34 CFR 300.321, 300.322, 300.324, 300.503 (team decision, parent participation, revision, prior written notice); COMAR 13A.05.01.07–.09; Maryland Assessment, Accessibility and Accommodations Manual (Aug 2025) on documentation, the instruction-and-assessment requirement, the accessibility-feature vs accommodation distinction, and the Unique Accommodation Request route through the local LAC. Section numbers for 300.324 and 300.503 should be confirmed against eCFR before they appear in product copy.

### The SPED-correct progress-monitoring spine: CBM probes, goal lines, and explicit decision rules   `ESTABLISHED`

**Why it matters.** The artifact promises a 'Monthly IEP Progress Report formatted for IEP meeting submission' with no measurement behind it. A real progress-monitoring spine is what turns the product from an engagement app into something a special education office can defend buying, and it is the prerequisite for ever claiming an outcome.

**What to build.** Pick two or three brief, repeatable, standardised indicators and build the whole measurement system on them rather than on telemetry. Candidates: (1) ORAL READING FLUENCY or MAZE comprehension CBM for literacy, weekly, 1–3 minutes, scored against published grade-level benchmarks; (2) a 2-minute writing probe scored for correct word sequences if you build the SRSD module; (3) homework/assignment completion rate from a daily log (which is also the HOPS outcome and the CICO outcome). For each: a baseline of 3 points, a goal set as a rate of improvement, a goal line, an automatically fitted trend line, and a STATED decision rule (e.g. four consecutive points below the goal line triggers a 'change the intervention' prompt; four above triggers 'raise the goal'). Every chart must show the number of data points and the measurement error, and must never display a trend from fewer than 6 points. Separately and clearly, track implementation fidelity — sessions delivered vs planned, and accommodation offer rate — because an outcome claim without a fidelity denominator is not interpretable. Rename the monthly output 'Progress Summary' and state on it that IEP progress reporting toward measurable annual goals is the school's responsibility under 34 CFR 300.320(a)(3).

**Evidence.** CBM is the established standard for repeated academic progress monitoring with validated decision rules; the National Center on Intensive Intervention Progress Monitoring Tools Chart (charts.intensiveintervention.org) is the source for selecting specific validated measures and should be consulted rather than inventing probes. HOPS used GPA and parent-rated homework completion as outcomes with reported d=0.85 for homework behaviours (Langberg et al., School Psychology Review 2012, PMC4209597) and showed null teacher-rated effects — a useful caution about which rater you measure with. 34 CFR 300.320(a)(2)-(a)(3) measurable annual goals and progress reporting (section number UNVERIFIED in session; confirm on eCFR).

### A Child Find and referral protocol with a parent-generated written evaluation request   `ESTABLISHED`

**Why it matters.** The product will surface suspected disability in unidentified students. Right now it does nothing with that, which is both an ethical gap and a missed differentiator — helping a parent make a legally effective evaluation request is a concrete, high-value service no consumer study app provides.

**What to build.** A threshold-triggered flow that: (1) states clearly that the profile is not a diagnosis and cannot identify a disability; (2) explains in plain language, at a grade-6 reading level and in the family's language, what an initial evaluation is, that the parent may request one in writing, and what the timelines are; (3) generates a dated, editable written request addressed to the principal and the school's special education contact, containing the student's name, school, grade, the parent's specific concerns, and an explicit request for an initial evaluation under IDEA, which the PARENT sends and keeps a copy of; (4) offers a second template for an existing-IEP student requesting an IEP team meeting; (5) logs that the disclaimer was displayed. Add signposting to Maryland's parent resources (the Parents' Place of Maryland is the state Parent Training and Information Center) rather than positioning the vendor as the advocate.

**Evidence.** 34 CFR 300.111 Child Find (section number from primary regulation, UNVERIFIED in session — confirm on eCFR); COMAR 13A.05.01.05 (Assessment) and .06 (Evaluation, Reevaluation, and Eligibility), including the requirement to hold an IEP team meeting within 30 days of evaluation, verified as existing sections via mdrules.elaws.us. Parents' Place of Maryland as Maryland's PTI should be verified before citing it in product copy.

### An MTSS placement statement and a Tier 1 classroom version of the core product   `INFERENCE`

**Why it matters.** Every MCPS adoption decision routes through a tier question and a budget code. A product with no tier has no code. A Tier 1 classroom version is also the LRE-correct answer to the segregation risk and the CCEIS-fundable answer to the disproportionality finding.

**What to build.** One paragraph on the Project Doc tab declaring: Tier 1 universal (whole-class study skills, test-preparation routine and anxiety regulation, delivered by the general education teacher in ~15 minutes/week), with a Tier 2 small-group option (CICO-style daily check-in plus the HOPS-aligned organisation routine, 2–3 brief sessions/week by a para or school mental health provider). Then build the Tier 1 teacher-facing artefacts, because they are what makes it buyable: a 6-lesson teacher script, a one-page classroom routine card, and a class-level dashboard with no individual student identification by default. Explicitly state that nothing in the product is specially designed instruction and nothing substitutes for an IEP service.

**Evidence.** INFERENCE from how district adoption and funding decisions work, supported by the CCEIS mechanism: districts identified as significantly disproportionate must reserve 15% of IDEA Part B funds for comprehensive coordinated early intervening services, which are by design general-education-side supports for students not yet identified (Blueprint for Maryland's Future, Issue Brief: Significant Disproportionality, July 2024).

### An SRSD writing module and an SDLMI self-determination module to replace 'speed reading' and 'child liberation'   `ESTABLISHED`

**Why it matters.** Two of twelve student modules are currently spent on speed reading and '90% faster study' — unsupported claims that are contraindicated for students with decoding deficits. The artifact's 'child liberation' thesis is a real and good instinct with an established, IDEA-aligned operationalisation it has not found.

**What to build.** MODULE A (SRSD): a full Self-Regulated Strategy Development sequence for argumentative or informational writing — develop background knowledge, discuss it, model it, memorise the mnemonic, support it, independent performance — with built-in self-statements, goal setting and self-monitoring of a countable outcome (e.g. essay elements included). Score with correct word sequences or an elements rubric so it feeds the progress-monitoring spine. MODULE B (SDLMI / self-determination): teach the student to set an academic goal, plan, self-monitor, evaluate and adjust — then, critically, to participate in their own IEP meeting: what the meeting is, who is there, what they may ask for, and a structured 'my strengths, my needs, my goals, my accommodations and whether they help' one-pager the student prepares and presents. Self-advocacy and student participation in IEP meetings is directly aligned to IDEA transition requirements, which begin at 14 in Maryland practice — so this module is simultaneously the artifact's liberation thesis, an evidence-based practice, and a compliance-relevant service a school values.

**Evidence.** SRSD effect sizes: IES reports effects typically exceeding 0.85 and commonly 1.0–2.55 (https://ies.ed.gov/learn/blog/improving-academic-achievement-through-instruction-self-regulated-strategy-development-science); Graham & Harris LD meta-analysis d≈1.14–1.17 for writing quality (sources disagree — verify primary); Graham et al. 2023 middle/high school synthesis d=1.16. Self-Determined Learning Model of Instruction (Wehmeyer, Shogren et al.) — specific effect sizes UNVERIFIED in this session; check the most recent SDLMI meta-analysis before citing numbers. 34 CFR 300.320(b) transition services and 300.321(b) inviting the child to transition meetings (300.321(b) verified in session).

### A Check-In/Check-Out feature with an explicit fidelity requirement   `EMERGING`

**Why it matters.** The artifact already has 'Check-in / Check-out' listed as an accommodation and a daily emotional check-in feature — but CICO is a specific, structured Tier 2 practice with defined components, and implementing it loosely produces nothing. Doing it properly makes the product a recognisable Tier 2 intervention a school already knows how to fund and staff.

**What to build.** The real CICO structure: a morning check-in with a designated adult, a daily point card tied to 2–3 positively-stated, school-wide expectations, teacher rating at each class period or transition, an afternoon check-out with the same adult, and a home report. The product's job is the data layer, not the relationship: generate the card, collect period ratings on a phone in under 5 seconds per period, compute percent-of-points-earned daily, chart it against a goal, and — the part most implementations omit — measure FIDELITY (percent of scheduled check-ins completed, percent of periods rated) and refuse to display an outcome trend when fidelity is below a stated threshold. Pair with a daily behaviour report card variant for students whose target is academic engagement rather than behaviour.

**Evidence.** CICO is a widely implemented Tier 2 practice within PBIS with an established component structure; a specific meta-analytic effect size was NOT verified in this session — check the CICO literature (e.g. Maggin et al. systematic reviews, and the Center on PBIS Tier 2 resources at pbis.org) before stating any effect size in product or sales material. The fidelity-gating principle is ESTABLISHED practice in intervention research.

### A ParaPathways / Pearson paraprofessional exam preparation module, free to MCPS   `ESTABLISHED`

**Why it matters.** MSDE is replacing the retiring ParaPro assessment, which creates an immediate, concrete, district-level problem with a deadline. Solving it is the cheapest possible way into an MCPS building, and it reaches the exact audience the MCLSS track was aimed at — without asking a paraeducator for $299 or 80 unpaid hours.

**What to build.** A short, free, mobile preparation module aligned to the assessments MSDE is approving for Title I paraprofessionals — ETS ParaPathways (Reading & Writing, Mathematics subtests) and the Pearson Foundations of Classroom Support exams — with practice items, a diagnostic of which subtest a candidate is weakest on, and a study schedule. Confirm the final approved list and the Maryland cut scores with MSDE before building to specific score targets. Keep it genuinely free and unbranded-upsell; it is a relationship instrument, not a revenue line. Then replace the 80-hour MCLSS with a 6–10 hour, school-funded, job-embedded micro-credential on accommodation implementation and CICO fidelity.

**Evidence.** ETS retiring ParaPro in August 2026 and MSDE recommending approval of ParaPathways (split into Reading & Writing and Mathematics subtests) plus two Pearson Foundations of Classroom Support exams: MSDE State Board item, 'Assessments for Paraprofessionals Working in Title I Schools', Feb 2026 (https://marylandpublicschools.org/stateboard/documents/2026/0224/assessments-for-paraprofessionals-working-in-title-i-schools-a.pdf). Final State Board approval and the Maryland cut scores (one third-party site lists 332 Reading & Writing / 334 Mathematics) are UNVERIFIED — confirm with MSDE directly. ESSA §1112(c)(6) baseline per MSDE Title I Part A Program Guide (https://msde.maryland.gov/media/18704).

### A real MCPS data pack to replace every invented percentage   `ESTABLISHED`

**Why it matters.** The founder works inside MCPS and is arguing from numbers that are not real while the real, more damning numbers are publicly available. Fixing this is free and it is the difference between a document a special education director reads to the end and one they stop reading at the first citation they recognise.

**What to build.** A one-page, dated, fully sourced data appendix added as an eleventh tab, containing: total MCPS enrolment and grade 6–8 enrolment; percentage and count of students with IEPs; FARMS percentage; EL percentage and top home languages; racial/ethnic composition; IEP-student performance on MCAP ELA and mathematics and on DIBELS, disaggregated by race where MCPS publishes it; MCPS suspension risk ratios for Black students with disabilities; and the current MSDE disproportionality determination for MCPS with the associated CCEIS set-aside amount. Sources to pull from: the MCPS Official Enrollment report (Department of Shared Accountability), MCPS Schools at a Glance / school profiles, the MCPS Open Data Portal (data.montgomeryschoolsmd.org), MSDE's Maryland Report Card, MSDE's Special Education/Early Intervention Services Census (Oct 1 child count), and the MCPS Board of Education item reporting the state disproportionality finding. Every figure gets a date and a URL. Then delete '73% of MCPS families lack both'.

**Evidence.** Partial figures already located: MCPS enrolment ~159,671 in 2024-25; MCPS DIBELS benchmark attainment 38.6% for students with IEPs, 46% FARMS, ~33% English Language Development (Bethesda Magazine, 26 Oct 2026, https://bethesdamagazine.com/2026/10/26/demographic-disparities-mcps-academic-achievement/); MCPS OLO budget-equity report noting FARMS students outnumber ELs ~2:1 and students with disabilities ~3:1 (https://assets.montgomerycountymd.gov/files/2026-07/OLOReport2026-9BudgetEquityinMCPS.pdf); MCPS report of continued disproportionality in suspensions for Black students with disabilities with $5,638,869 in IDEA funds implicated (Nov 2025, secondary source — verify against BoardDocs). The MCPS official enrolment PDF could not be retrieved because ww2.montgomeryschoolsmd.org does not resolve from this session's network and would need to be allowed in the session's network settings.

### A vendor compliance pack: SDPC NDPA, a §4-131 memo, and a published special education records policy   `ESTABLISHED`

**Why it matters.** No MCPS data touches this system without it, and it is a long-lead item the roadmap currently has no slot for. Producing it early is also a sales asset — most small ed-tech vendors cannot hand a district a completed NDPA on first contact.

**What to build.** Four documents, produced in Phase 1 not Phase 3: (1) a completed Student Data Privacy Consortium National Data Privacy Agreement v2.2 with Maryland exhibits, published at a stable URL; (2) a Md. Code Educ. §4-131 compliance memo walking each statutory prohibition and the sub-processor flow-down requirements against the actual architecture, with specific attention to whether agent memory constitutes profiling outside a PreK-12 purpose; (3) a Special Education Records Handling Policy citing 34 CFR 300.610–300.627, naming the individual responsible for confidentiality, and stating the access, amendment and destruction processes; (4) a data flow diagram showing exactly which fields reach which third-party LLM provider, with a stated commitment that no IEP text and no identified special education record leaves the primary datastore. Submit the package to the MCPS data privacy specialist review as the first contact with the district, before any pedagogical pitch.

**Evidence.** Md. Code, Educ. §4-131 (https://mgaleg.maryland.gov/2024RS/Statute_Web/ged/4-131.pdf); MCPS Data Privacy and Security page describing the required district-vetted data sharing agreement and the data privacy specialist committee (https://www.montgomeryschoolsmd.org/data-privacy-security/safeguards/); SDPC National Data Privacy Agreement v2.2, published 19 Nov 2025 (https://privacy.a4l.org/national-dpa/); 34 CFR Part 300 Subpart F (https://www.ecfr.gov/current/title-34/subtitle-B/chapter-III/part-300/subpart-F/subject-group-ECFR1d2a18271819883).

### The two wedges that would actually get bought in MCPS, ranked   `INFERENCE`

**Why it matters.** The founder's stated principle is completion > validation > monetization. The artifact currently has ten tabs and no wedge. These are the two things an MCPS special education office or an MCPS principal could plausibly pilot, and the reasons are structural rather than persuasive.

**What to build.** WEDGE 1 — the Accommodation Fidelity Log, sold to the Office of Special Education as a compliance-adjacent tool. It answers a question MCPS cannot currently answer ('are documented accommodations actually being delivered?'), it does not touch the IEP system, it requires no student self-report, it is cheap to pilot in two middle schools, and it produces data a district can use in its own CCEIS work. Price the pilot under $25,000 total so no Board item is needed. WEDGE 2 — a Tier 1 whole-class test-preparation and anxiety-regulation routine, 15 minutes a week, teacher-delivered, sold to a single middle school principal from CCEIS or Blueprint Concentration of Poverty wraparound funds at a high-FARMS school, positioned explicitly as a referral-reduction and exclusion-reduction measure. Both wedges are LRE-correct, both sit inside general education, both avoid every blocker in this review, and both generate the outcome data the family-direct product will eventually need. Do not build the certification tracks, the GED-to-PhD pathway, the 8-agent LangGraph system, the ancestor library or the IEP PDF parser until one of these two wedges has a signed pilot and a result.

**Evidence.** INFERENCE from the procurement, funding and compliance constraints verified elsewhere in this review: the $25,000 MCPS/Educ. Art. §5-112 Board threshold (MCPS Policy DJA; OIG Report 26-08), the CCEIS 15% set-aside consequence of MCPS's disproportionality finding, Blueprint CPG allowable uses for wraparound services at high-poverty schools, and the absence of any legal path for the currently-designed accommodation engine.


---

## Open questions

- Exact MCPS 2025-26 figures could not be retrieved: total enrolment, grade 6-8 enrolment, percentage of students with IEPs, FARMS percentage, EL percentage and racial composition. ww2.montgomeryschoolsmd.org did not resolve from this session's network and would need to be allowed in the session's network settings. The MCPS Official Enrollment 2026 report, the MCPS Schools at a Glance profiles and the MCPS Open Data Portal (data.montgomeryschoolsmd.org) are the sources.
- The $5,638,869 IDEA CEIS figure and MCPS's current significant-disproportionality determination came from a secondary report of an MCPS board item (Nov 2025). The primary sources — the MCPS BoardDocs item and MSDE's determination letter to MCPS — were not retrieved and should be confirmed before the number appears in any deck.
- Which intervention, screening, SEL and MTSS platforms MCPS currently licenses is unknown. The MCPS approved Technology Resources list and recent Board procurement items are needed to write a real competitive scan; without them, the 'no comparable app exists' claim cannot be fixed, only deleted.
- The MCPS third-party application review process is documented only in outline on the public Data Privacy and Security page. The actual vendor questionnaire, required artefacts (SOC 2, HECVAT, NDPA exhibits), review timeline and the responsible office are not public — the founder, as an MCPS employee, can obtain these internally and should, because they are the critical path.
- Whether MSDE's State Board gave final approval to ParaPathways and the two Pearson Foundations of Classroom Support exams, and what the official Maryland cut scores are. A February 2026 committee recommendation was located; final adoption was not. The third-party cut scores (332 Reading & Writing, 334 Mathematics) are from a prep-site, not MSDE.
- Section numbers used here but not directly verified in this session and which should be confirmed against eCFR before appearing in product or legal copy: 34 CFR 300.111 (Child Find), 300.114 (LRE), 300.320 and 300.324 (IEP content, review and revision, including 300.324(a)(4) amendment without a meeting), 300.503 (prior written notice), and 34 CFR Part 104 §§104.33, 104.35, 104.36 (Section 504). COMAR 13A.12.01 could not be located; the MSDE provider guide cites COMAR 13A.12.02.06E instead, so do not cite 13A.12.01.
- Current MCPS SEIU Local 500 paraeducator hourly rates and contractual duty day were not retrieved; the FY2027 salary schedule PDF and the current SEIU agreement are the sources. The argument that $299 and 80 hours is unviable does not depend on the exact rate, but the pitch to MCPS should use the real number.
- MCPS's actual school counsellor and school psychologist referral and crisis-response pathway — who is notified, by what mechanism, with what response window — is not publicly documented and is the factual basis for the safety finding. The MCPS Office of Student and Family Support and Engagement and the relevant MCPS regulations are where to confirm it.
- Whether the artifact's African-centered pedagogy claims can be supported at the effect sizes asserted (notably 'ES: 0.8') is unresolved. Culturally sustaining pedagogy has a substantial qualitative and theoretical literature; the quantitative effect-size literature is thinner and more contested than the artifact implies. Someone should run a proper evidence review before any effect size is printed.
- Whether MCPS has an existing Comprehensive Coordinated Early Intervening Services plan already committing the 15% set-aside, and to what. If those funds are already allocated for the current cycle, the CCEIS wedge has a timing constraint that determines when the pitch should land.

