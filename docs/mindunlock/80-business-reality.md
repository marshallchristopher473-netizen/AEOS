# Business reality

> The financial model, revenue assumptions, grants, go-to-market and competitive position,
> judged by an operator who has watched many of these die.

**Provenance.** Produced by an independent expert lens in a nine-lens audit of
`MindUnlock_Academy.jsx` (859 lines), using live web search against primary sources.
>
> **Verification status: NOT independently verified.** Its skeptic auditor did not run (usage
> limit). Treat findings as well-reasoned leads. See [`90-verification.md`](90-verification.md)
> for what verification found when it did run on another lens, and for the error rate you
> should assume here.
>
> Nothing here is legal, financial or investment advice.

---

## Executive summary

The Year 1 P&L is wrong by roughly a factor of 20 on revenue and roughly a factor of 4–6 on cost, and the two errors compound in the same direction. "$391,850 revenue / ~$175,000 costs / ~$216,850 net" (lines 755–757) is not a forecast; it is five aspirational unit counts multiplied by five list prices, minus an undefined round number. Rebuilt honestly, a part-time solo founder executing this plan as written spends $600K–$1.1M in Year 1 and collects $7K–$40K. The gap is not a modelling nuance. It is the whole business.

Every revenue line fails independently, and for a different reason: the family line is priced at $399 for households the artifact itself calls "under-resourced" (MCPS middle-school FARMS rates run 6.4% at Pyle to 63.3% at Francis Scott Key — the product is designed for the 63% schools and priced for the 6% schools); the school line requires a board-approved procurement from a vendor whose founder is a current MCPS employee, an ethics exposure the document never mentions once; the two certification lines depend on "CEU-eligible" and "graduate credit" credentials that are claims, not accreditations; and the $100,000 grant line confuses two unrelated things — a district spending Title I/IDEA formula funds on your product (possible, with evidence constraints) and your company receiving a federal grant (ED/IES SBIR, NSF SBIR — different world, 14-month cash cycle, and NSF's PI-must-be->50%-employed rule disqualifies a full-time MCPS employee outright).

The cost line omits founder compensation, content production for 280 certification contact hours, the licensed school psychologist the artifact's own Action #1 requires, legal counsel it promises "from Day 1," the quarterly pen tests and annual audit it promises in the Tech Stack tab, insurance (crisis detection on minors is the line item an underwriter declines), payment processing, app store fees on an in-app $399 subscription, support, and CAC.

The single most valuable thing in this document is not the app. It is the founder's access to the families and his standing inside MCPS SPED practice. The correct Year 1 is one services motion, one buyer who is not his employer, under $5,000 of spend, and an ESSA Tier IV evidence package — a bar the artifact never mentions and which every district buyer asks about first.

---

## Findings

### F01 — Year 1 revenue is overstated roughly 20x; all five lines fail independently

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Lines 741-757: 'Family Subs 500 × $399 = $199,500 / School Licenses 5 × $7,500 avg = $37,500 / Para Certs 100 × $299 = $29,900 / Teacher Certs 50 × $499 = $24,950 / Grant Funding 2 grants avg = $100,000 / Total Year 1 Revenue $391,850'

**The problem**

This is a units-times-price table, not a forecast. There is no funnel, no conversion rate, no CAC, no churn, no sales cycle, and no close rate behind any of the five numbers. The arithmetic is correct ($199,500+$37,500+$29,900+$24,950+$100,000 = $391,850); the inputs are fiction. Rebuilt with explicit assumptions: families 10-40 paying (warm network only, no paid acquisition budget exists) = $4K-$16K; schools 0-1 small paid pilot funded from a principal's discretionary or Title I school budget, not a district contract = $0-$7.5K; para certs 0-5 (nobody pays $299 out of a paraeducator's wage for an unaccredited credential) = $0-$1.5K; teacher certs 0-4 (Maryland recertification requires MSDE-approved CPD, which MMEC is not) = $0-$2K; grants $0 (see F03). Honest Year 1 range $7K-$40K, midpoint ~$18K.

**Evidence**

MCPS 2025-26 middle-school FARMS rates range from 6.4% (Thomas W. Pyle) to 63.3% (Francis Scott Key) per an MCPS Board of Education follow-up document (montgomeryschoolsmd.org ms-farms.pdf) [ESTABLISHED for the figures, retrieved via search, PDF not opened directly]. Kids' education app churn benchmarks cluster near 7.4%/month (~60% annual) with median ARPU ~$12 (retentioncheck.com, vendor-published, 2026) [EMERGING]. No source supports a first-year solo-founder D2C education product reaching 500 paid annual subscriptions without paid acquisition.

**Recommendation**

Replace the table with a driver-based model: (visits → trial → paid → retained) for D2C, (conversations → qualified → LOI → signed → collected) for B2B, each with a stated conversion rate you will measure. Then set the Year 1 revenue target at the number you can defend to yourself: $15,000-$30,000 from one motion. Put the $391,850 in a clearly-labelled 'Year 3 if everything works' column, not in the Year 1 column.

### F02 — Founder is an MCPS employee selling to MCPS; the ethics and procurement exposure is unaddressed anywhere in the document

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Line 724: 'School / District License $2,500-$15,000/school/yr ... MCPS pilot target'. Line 777: '5 school contracts signed ($37,500 ARR)' and 'MCPS district leadership presentation delivered'. Line 725: 'MCPS partnership'. The Risks card (lines 117-122) lists six risks; conflict of interest is not one of them.

**The problem**

The entire B2B revenue line, the district partnership, the paraeducator CEU channel and the Phase 3 roadmap all route through the founder's own employer. MCPS Regulation GCA-RA and Board Policy BBB govern employee conflicts of interest and expressly contemplate the situation of an employee connected to a company 'that has negotiated or is negotiating a contract with the school system.' A finding of violation 'may constitute grounds for removal from office, discipline, or other personnel action.' This is a career-and-company-ending risk sitting unlabelled in the middle of the plan, and it also contaminates the pilot: a pilot recruited through the founder's MCPS role produces evidence a district buyer will discount for exactly this reason.

**Evidence**

MCPS ethics page (montgomeryschoolsmd.org/ethics) and Regulation GCA-RA (ww2.montgomeryschoolsmd.org/departments/policy/pdf/gcara master.pdf), which states it sets expectations 'in addition to those in Maryland ethics law and Board Policy BBB.' The MCPS Ethics Panel and Ethics Officer (240-740-3030) issue advisory opinions. [ESTABLISHED that the policy and panel exist and cover this fact pattern; the specific outcome for this founder is UNVERIFIED and requires a written advisory opinion.] A November 2025 county Inspector General report found MCPS spent funds without required Board approval in FY23-FY24, which means the procurement side is currently under heightened scrutiny — the worst possible moment to be the inside vendor.

**Recommendation**

Before any sales activity: (1) request a written advisory opinion from the MCPS Ethics Officer describing the exact facts — employee, outside company, intent to sell to MCPS or to MCPS staff — and get it in writing; (2) budget $2,000-$5,000 for an independent Maryland employment/ethics attorney to review the opinion and the outside-employment disclosure; (3) until that opinion is in hand, make the first customer someone other than MCPS. Prince George's County Public Schools, a Maryland charter or non-public SPED school, a 21st CCLC afterschool provider, or a county nonprofit all have the same families and none of the conflict.

### F03 — $100,000 of 'Federal Grant Funding' is booked as Year 1 revenue; it conflates district formula funds with company grants and is $0 in Year 1 either way

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.92 |

**What the artifact says**
> Line 727: 'Federal Grant Funding $50K-$500K / grant — Title I eligibility (high-poverty schools); IDEA eligibility (students with disabilities); NSF STEM education grants; IES research grants. Target: 2 grant applications submitted Year 1'. Line 745: 'Grant Funding | 2 grants avg | $100,000'. Line 780: '2 federal grant applications (Title I + IDEA) submitted'.

**The problem**

Three separate errors. (a) Title I Part A and IDEA Part B are formula grants that flow ED → state education agency → local education agency. A company cannot apply for them and cannot receive them. There is no such thing as 'submitting a Title I application' as a vendor. A district can *spend* those funds on your product, subject to supplement-not-supplant, excess-cost (IDEA) and ESSA evidence constraints — that is a sales motion, not a grant motion. (b) The programmes a small edtech can actually apply to are ED/IES SBIR and NSF SBIR/STTR, neither of which is named. (c) The model books 'applications submitted' as cash collected in the same year. Even on a perfect run, a federal award is cost-reimbursement: you spend, then draw down, after SAM.gov registration, an SF-424 package, and (above the Single Audit threshold) audit obligations.

**Evidence**

ED/IES SBIR FY2026 solicitation: Phase IA (novel product, 91990026R0003) and Phase IB (new component for an existing product, 91990026R0004) at $250,000 for 9 months; Phase II at $1,000,000 for 2 years; FY2026 deadline was June 29, 2026 at 2PM EDT — i.e. already passed as of today (2026-10-28), so the next bite is the FY2027 cycle. Applicant must be a for-profit small business. [ESTABLISHED via IES solicitation pages retrieved through search; note that ies.ed.gov could not be fetched directly in this session — the host does not resolve here and would need to be allowed in the session's network settings — so the figures come from the search layer's reading of those IES pages, not from my own fetch of them.] NSF SBIR/STTR solicitation NSF 26-510: Phase I ceiling $305,000 over 6-18 months; an invited Project Pitch is mandatory and a firm may submit at most two pitches per 12 months; fewer than 500 employees; and critically 'the PI must be employed more than half-time at the company' — which a full-time MCPS employee is not. Next NSF full-proposal deadlines Nov 4 2026 and Mar 4 2027. IES research grants (84.305A, 84.305T Transformative Research) do list 'nonprofit and for-profit organizations' as eligible applicants, with FY2025 Education Research Grants estimated at 40-70 awards of $300,000-$800,000/year over five years — but the competitive bar assumes methodological research capacity a solo founder does not have. [Award counts and current-cycle dates UNVERIFIED for FY2027.]

**Recommendation**

Delete the $100,000 from Year 1 revenue; set grant revenue to $0 through December 2027. Then split the motion in two and name them correctly: (1) SALES — build an ESSA Tier IV evidence package (F11) so a Title I school or IDEA-funded SPED department can lawfully spend existing formula money with you; this is where near-term dollars are. (2) NON-DILUTIVE CAPITAL — target ED/IES SBIR Phase IA in the FY2027 cycle (~June 2027 deadline, award ~Q4 2027, first drawdown ~Dec 2027: a 14-month cash lag), budget 80-200 founder hours or $8,000-$25,000 for a proposal writer, and solve the NSF PI-employment problem by either not applying to NSF or joining a university PI's IES application as the vendor/site rather than the applicant. Also note the macro risk: ED's research apparatus saw large contract terminations in 2025 and the federal school-mental-health grant environment has been volatile; treat future IES cycles as uncertain, not as a plan.

### F04 — The ~$175,000 cost line omits at least ten categories, several of which the artifact itself promises elsewhere

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Line 756: 'Operating Costs (tech + staff + marketing) ~$175,000'. No breakdown is given anywhere in the document.

**The problem**

Missing, with the artifact's own promise in brackets: founder compensation / opportunity cost of a full-time MCPS job ($0 cash but 8-15 FTE-years of scope — see F18); content production for 280 certification contact hours across 4 tracks and 100+ cultural profiles [line 141 'Create 40+ ancestor inspiration profiles', lines 338/368/397/423]; psychometric validation and a licensed school psychologist [line 91, 'validated with licensed school psychologist']; legal counsel [line 117, 'Legal counsel from Day 1']; quarterly external pen tests, bug bounty, and an annual third-party security audit [line 691]; paid African-centered scholar co-developers and a community advisory board [line 120, 'African-centered scholars as PAID co-developers']; pilot incentive structure [line 121]; insurance (E&O, cyber, and the crisis-detection problem — see F05); payment processing; app store commission (F09); customer support (F19); CAC; LLM inference (F15); accounting, entity, state filings, registered agent. A plausible as-written Year 1: content $125K-$420K, validation $25K-$75K, legal $14K-$40K, security $52K-$150K, scholars/advisory $21K-$60K, insurance $5K-$40K, infra $24K-$72K, inference $18K-$90K, support $10K-$40K, CAC $37K-$100K, admin $2K-$6K. Total $333K-$1.09M before a dollar of founder salary.

**Evidence**

Content: industry e-learning development ratios commonly quoted at ~100-200 development hours per 1 hour of finished Level 2-3 interactive e-learning (Chapman Alliance) [EXPERT-OPINION, dated, widely cited but not replicated]. Even at a deliberately conservative 30 dev-hours per contact hour, 280 contact hours = 8,400 hours; at $50/hr contract instructional design that is $420,000, and AI-assisted authoring at a 70% reduction still leaves ~$125,000 plus SME review. Security: small-company external pen tests commonly quote $8,000-$25,000 each and SOC 2 Type I readiness plus audit $20,000-$50,000 [EXPERT-OPINION, market ranges, not from a retrieved primary source — get three quotes]. Infra: the stated production stack (AWS ECS Fargate auto-scaling + CloudFront + RDS Multi-AZ + ElastiCache cluster + multi-region us-east-1→us-west-2 DR, line 702) is a $2,000-$6,000/month configuration [INFERENCE from AWS list pricing].

**Recommendation**

Rewrite the cost side as a line-item schedule with a Low/Base/High column and an owner per line, and mark each line 'committed / deferred-until-validated.' Then apply the founder's own rule — no recurring expense before validation — and cut the Base case to the services-only MVP: legal+ethics $8K, instrument licensing and school-psych review $4K, printing and materials $1.5K, Zoom/Notion/Google $600, insurance $3K, entity/accounting $2.5K. Total $20K cash. Everything else moves to a 'post-validation' schedule with a trigger condition written next to it.

### F05 — Crisis detection on minors is the most dangerous line in the document and is likely uninsurable as specified

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `EXPERT-OPINION` |
| **Lens confidence** | 0.82 |

**What the artifact says**
> Line 119: 'Student crisis / self-harm disclosure — Critical — Crisis detection layer; automatic counselor + parent notification; hotline display; AI conversation paused immediately'. Line 572: 'Crisis Escalation Protocol: Anxiety markers exceed threshold → counselor alert + parent notification'. Line 691: 'crisis escalation detection with latency < 500ms'. Line 557: 'threshold alert to parent + counselor if distress detected'.

**The problem**

Promising automated crisis detection creates an affirmative duty where none existed. Once you tell a parent the system detects distress and notifies a counselor, a missed detection is a failure-to-warn claim, and a false positive that discloses a minor's mental state to a parent is a privacy claim. The design also assumes a counselor relationship the company does not have — the artifact never says who that counselor is, who employs them, whether they are on call, or what happens at 11pm on a Saturday. Commercially: technology E&O / cyber for a small edtech is routinely obtainable, but a product performing mental-health-adjacent monitoring of minors frequently draws either a professional-services / bodily-injury / mental-anguish exclusion or an outright declination, pushing you into specialty markets (miscellaneous professional plus abuse-and-molestation wordings). This single feature can make the company uninsurable, and no district will sign a DPA with an uninsured vendor.

**Evidence**

No retrieved primary source. Market behaviour of E&O/cyber underwriters toward minor-facing mental-health monitoring is EXPERT-OPINION based on how this category is underwritten; the specific premium range I would otherwise quote ($15,000-$40,000+ in specialty markets vs. $3,000-$12,000 for plain tech E&O) is UNVERIFIED and must be replaced with real quotes. What I would check: three brokers who write edtech (ask specifically for the mental-health and abuse exclusions in the sample wording), plus whether any carrier will write the crisis-detection feature at all.

**Recommendation**

Cut crisis detection from the product entirely for at least 24 months. Replace it with: (a) a static, always-visible crisis resources panel naming 988 and local county crisis services; (b) Terms of Service and onboarding copy stating in plain language that the product is not a mental-health service, does not monitor for crisis, and must not be relied on in an emergency; (c) a documented human escalation path for anything a human facilitator hears in a live cohort session, owned by the facilitator, not by software. Then get the insurance quotes anyway, before you sell anything, because the quote is also a free independent read on your risk profile. If you later build it, ring-fence it in a separate entity — but the right answer is not to build it.

### F06 — Four go-to-market motions plus a grant motion, run by one person with a full-time job

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.91 |

**What the artifact says**
> Lines 723-728 define five revenue streams simultaneously: Family Subscription (D2C), School/District License (B2B enterprise), Paraeducator Certification (prosumer, individual), Teacher PD Certification (prosumer, individual), Federal Grant Funding, plus GED-to-PhD in Year 2. All targeted for Year 1 except the last.

**The problem**

These are four different companies with four different buyers, four pricing psychologies, four sales cycles, four support models and four compliance postures. D2C needs paid acquisition, onboarding, retention mechanics and app-store operations. District B2B needs a procurement path, a DPA, security review, references and an evidence tier. Prosumer certification needs an accreditation body and a credential that moves someone's pay. Grants need a research partner and a 14-month runway. Doing any one of them well is a full-time job. Doing all four in evenings means doing all four badly, and the failure mode is not 'slower' — it is that none of the four ever reaches the threshold where it produces a signal you can act on. This is the single most reliable killer in this category and the plan contains no sequencing discipline at all, despite the founder's stated rule of completion > validation > monetization > scaling.

**Evidence**

[INFERENCE from the artifact's own structure.] Supporting: the roadmap (lines 770-781) runs all four motions concurrently across Phases 1-4 with no gate between them and no stated kill criteria for any one.

**Recommendation**

Pick one. My recommendation is institutional B2B services (see F13/wedge) — sell a facilitated cohort to an organisation that already has the families and the budget, not software to families who have neither. Formally defer the other three with a written trigger: D2C does not start until a cohort has ≥70% completion and ≥3 unsolicited referrals; certification does not start until an accreditation partner is signed; grants do not start until the ESSA Tier IV package exists. Write the deferral down so it is a decision, not drift.

### F07 — 'No Comparable App Exists' is a category error, and the gap analysis's own app table contains zero direct competitors

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.89 |

**What the artifact says**
> Line 244-245: '🏆 Market Conclusion: No Comparable App Exists — No app or combination of apps delivers all 8 innovation pillars simultaneously ... MindUnlock Academy is the first of its kind.' Line 159 claims a review of '38 apps (2018-2024)'; lines 226-231 then list six: Anki, Headspace/Calm, Duolingo, Notion/Obsidian, Google Classroom, Brainly.

**The problem**

The conclusion is true only because the category was defined as 'everything I am building, at once.' That is unfalsifiable positioning, not a market finding, and an investor reads it as a signal the founder has not met the competition. The tell is the evidence table: of the six apps actually named, not one is a competitor. Anki is a free algorithm, Duolingo is language learning, Notion is a notes app, Google Classroom is an LMS, Brainly is homework answers. The real adjacent occupants — the vendors a district or a parent actually chooses between — are entirely absent. 'No comparable product' almost never means 'open field'; in a market this old it usually means 'this configuration does not get bought.' There is no scaled test-anxiety-only K-12 vendor, and that is information about demand, not about opportunity.

**Evidence**

Real current occupants, verified or named from current market presence: SCHOOL SEL/MTSS/mental health — Panorama Education (one cited district contract: Palo Alto Unified, $396,900 over three years for surveys, well-being check-ins and MTSS analytics), Branching Minds, Closegap, Satchel Pulse, 7 Mindsets (contracts cited $3,498-$26,250), Care Solace ($10,000 to $133,000+), and the teletherapy vendors a district actually buys for student anxiety (Hazel Health, Daybreak Health, Cartwheel). AI TUTORS — Khanmigo (free for verified US K-12 teachers; $4/month or $44/year for learners; district deals reported secondhand at ~$10-$35/student/year), MagicSchool (free tier, Plus $12.99/mo or $99.96/yr, custom district Enterprise), SchoolAI, Brisk Teaching — plus ChatGPT/Claude/Gemini, which are the actual free substitute for '24/7 homework scaffolding (Socratic method)' (line 536). EF/ADHD COACHING — Beyond BookSmart (programs 'start at $165 per week', 45-minute prepaid session packages; broader market quoted at $115-$265/hour), EF Specialists, Life Skills Advocate. ADHD/EF APPS — Joon, Tiimo, Goblin Tools, Inflow, Brili, Finch. IEP/ADVOCACY — Frontline IEP, PowerSchool Special Programs, SpedTrack, AbleSpace (free tier plus paid district offering), Undivided (parent-side; price not published), Wrightslaw and COPAA (free). TUTORING — Paper, Varsity Tutors for Schools, Littera, Air Tutors, Tutor.com (free through many public libraries). CULTURALLY RESPONSIVE CURRICULUM — Newsela, EL Education, Learning for Justice (free), plus MCPS's own CRE/anti-racist-audit workstream, which means the district may regard this layer as internally owned. [Pricing figures above are from vendor pages and third-party vendor-intelligence blogs retrieved via search; district per-student figures are secondhand and UNVERIFIED — confirm with quotes.]

**Recommendation**

Replace the 'No Comparable App Exists' card with a two-column honest statement. Column 1, Differentiation (three items, no more): the specific combination of EF scaffolding + test-anxiety protocol + Black/BIPOC identity affirmation delivered to the parent-child dyad rather than the student alone; the founder's standing inside MCPS SPED practice; and — once it exists — pre/post outcome data in this specific population. Column 2, Honest substitutes a parent buys instead: a $60-80/hour private tutor, the IEP/504 accommodations they already have, free Khanmigo or ChatGPT, library Tutor.com, or nothing. Then add a third card naming the incumbents who could add your layer in a quarter: Khan Academy (free distribution, could ship an EF/anxiety coach prompt set), MagicSchool and SchoolAI (already hold district contracts and teacher trust), Panorama (already owns the SEL/MTSS data relationship), Newsela (culturally responsive content at scale), Understood.org (brand plus neurodivergent audience plus philanthropic funding), ClassDojo (parent relationship at scale). Your moat is not the feature list — it is the cohort relationship and the data. Say so.

### F08 — The product is designed for families who cannot afford it and priced for families who do not need it

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Line 55 defines the parent customer as 'Under-resourced, wants to help.' Line 41: 'Parents were never taught HOW to study.' Line 723 prices the family subscription at '$49/mo | $399/yr' with a goal of '500 families Year 1.' Line 198 criticises Princeton Review/Kaplan for being 'upper-income market only' and claims MindUnlock's advantage is 'Equitable access.'

**The problem**

This is the central contradiction and the document never addresses it. $399/year is a real decision for a household at a 63%-FARMS middle school, and the families for whom $399 is trivial are at the 6%-FARMS schools, where the child typically already has a private tutor, an outside neuropsych evaluation and an advocate. You are either selling to the wrong families or at the wrong price, and criticising Kaplan for income-gating while charging $399 D2C is the same business model with better language. Worse, $399 is simultaneously too high for the stated user and too low for the product's actual cost to serve (support-heavy population, LLM inference, human review queue).

**Evidence**

MCPS 2025-26 middle-school FARMS rates: Francis Scott Key 63.3%, Gaithersburg 63.2%, A. Mario Loiederman 62.8% at the top; Thomas W. Pyle 6.4%, Herbert Hoover 11.8%, Cabin John 12.3% at the bottom (MCPS Board of Education follow-up document, ms-farms.pdf). Note MCPS adopted the Community Eligibility Provision in 60 schools for 2025-26, so FARMS figures in CEP schools are USDA-multiplier estimates rather than household counts. MCPS Grades 6-8 enrollment is in the 35,000-36,000 range per the capital-planning appendix, though the column year is ambiguous in that document [UNVERIFIED which school year].

**Recommendation**

Resolve it by choosing who pays, not by discounting. The right structure is institutional payer, free to family: an organisation (Title I school, 21st CCLC provider, county nonprofit, faith-based education ministry, or a foundation) buys a cohort at $625-$1,000 per family and the family pays $0 or a $25 commitment deposit. This preserves the mission, removes the affordability contradiction, removes CAC, removes churn, and removes app store fees in one move. Keep a D2C price in your pocket for the 6%-FARMS parent who finds you — but price it against the real substitute (8-12 hours of EF coaching at $115-$265/hour, i.e. $1,400-$2,600), not against a $49/month app.

### F09 — No app store commission or payment processing line; at the plan's own volume that is a ~$36,000 hole

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.94 |

**What the artifact says**
> Line 94 and line 685: the product is 'React Native (Expo SDK 51) — Mobile App, iOS + Android.' Line 723 sells a '$49/mo | $399/yr' subscription. Lines 755-757 show no distribution or processing cost of any kind.

**The problem**

A subscription sold inside an iOS or Android app pays store commission. At 15% on the plan's own $199,500 family line that is $29,925, plus roughly $5,900 at 2.9% + $0.30 on any card-processed portion. Together ~$36,000, or about 9% of total stated revenue and 21% of the stated total cost base — a line item larger than most of what is in the undefined $175,000. The plan also books gross revenue, not net proceeds, which is the wrong number to forecast from.

**Evidence**

Apple's App Store Small Business Program sets a 15% commission for developers with proceeds at or below $1 million in the prior calendar year (developer.apple.com/app-store/small-business-program). Google Play subscriptions are widely reported at an effective 15% (10% service fee plus 5% billing), with market-by-market changes rolling out in 2026. [The year-two subscription rule on Apple's standard tier is reported inconsistently across sources and is UNVERIFIED; for a Small Business Program member it is moot, since the rate is already 15% from the first payment.] Note also that following the 2025 US injunction in the Epic matter, external purchase link-outs are permitted on the US storefront — this is a real lever worth ~$30K at the plan's own volume, but confirm the current rules before architecting around it.

**Recommendation**

Add two explicit lines to the model: 'Store commission 15% of IAP revenue' and 'Payment processing 2.9% + $0.30.' Then make the deliberate choice: sell the subscription on the web, deliver the content in a mobile web app or a free native shell, and keep the 15%. For the institutional motion recommended elsewhere, this problem disappears entirely — invoiced B2B revenue pays no store fee. That is another reason the institutional motion is the right first one.

### F10 — 'Psychometrically validated' is asserted for instruments that do not exist, which breaks the founder's own rule and is a material misrepresentation to a district buyer

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.87 |

**What the artifact says**
> Line 258: 'PhD-Level Diagnostic Assessments — Psychometrically validated | Student: 52 domains | Parent: 38 domains | Staff: 24 domains'. Line 91 simultaneously lists as an unstarted Action #1: 'Build PhD-level student diagnostic instrument (52 domains) — validated with licensed school psychologist, Week 1-2'.

**The problem**

The header claims a property that Action #1 says has not been built. The founder's own stated principles include 'evidence before claims' and 'no claims of validation that has not occurred' — this is the clearest violation of both in the document. Operationally it is also a sales landmine: the first special education director who asks 'validated against what criterion, with what sample, what internal consistency, what factor structure?' gets no answer, and the relationship is over. And 'validated in Week 1-2' is not achievable: establishing content validity, internal consistency, factor structure and any criterion validity on a 52-item multi-construct instrument needs an expert review panel plus a pilot sample of roughly n=200-300, which is months and real money.

**Evidence**

[INFERENCE from the artifact's internal contradiction — lines 258 vs 91.] Separately: Spielberger's Test Anxiety Inventory, cited at line 264 and line 398 as an instrument the product will administer and score, is a copyrighted commercial instrument; using it inside a product requires a license from its publisher. [Current licensor, per-administration fee and whether a derivative-use license is even available are UNVERIFIED — I would check the publisher's permissions page and get a written quote before any item appears in a build.]

**Recommendation**

Change the header today to 'Draft instrument — research-informed, not yet validated' and add a one-line validation roadmap under it. Then do the cheap version first: hire a licensed school psychologist for 15-25 hours at $150-$250/hour ($2,250-$6,250) to do an expert content-validity review and to select an appropriate, properly licensed published anxiety measure for pre/post rather than inventing one. Full psychometric validation ($25,000-$75,000) is a Year 2-3 expense that only makes sense after the intervention shows it does something.

### F11 — ESSA evidence tiers are never mentioned, and they are the first question every district buyer asks

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> The document contains no reference to ESSA, evidence tiers, efficacy, or What Works Clearinghouse. Line 777 nonetheless plans '5 school contracts signed' and 'MCPS district leadership presentation delivered' in Months 7-9, and line 727 claims Title I and IDEA eligibility.

**The problem**

You cannot claim Title I eligibility and simultaneously not know what evidence tier you occupy — the tier is the thing that makes the spend lawful and defensible for the district. ESEA §8101(21)(A) defines four levels: strong (experimental), moderate (quasi-experimental), promising (correlational with statistical controls for selection bias), and 'demonstrates a rationale.' Section 1003 school-improvement funds require Tiers I-III; other Title I-IV uses may rely on Tier IV. Walking into an MCPS presentation without a tier answer is walking in without the one document the buyer's compliance officer needs.

**Evidence**

ESEA §8101(21)(A) four-tier structure and the §1003 Tier I-III restriction are reflected consistently across state education agency guidance (CA Dept of Education evidence page; Rhode Island DE guidance; North Dakota DPI; New Hampshire DOE; AIR's 'Selecting Evidence-Based Practices' 2019). Tier IV ('demonstrates a rationale') requires a well-specified logic model informed by research or an evaluation, plus an ongoing or planned effort to study its effects — sources paraphrase the evaluation element slightly differently, so quote ED's 2016 non-regulatory guidance or the statute itself rather than a secondary summary. [ESTABLISHED on the four-tier structure; the exact statutory wording of the Tier IV evaluation requirement is UNVERIFIED here because no primary text was retrieved — read the statute before putting a tier claim in a sales document.]

**Recommendation**

Build the Tier IV package in the next 30 days; it is nearly free and it is the single highest-leverage sales asset you can make. It needs three parts: (1) a one-page logic model — inputs, activities, outputs, short-term outcomes, long-term outcomes — drawn directly from the course-design tab; (2) a citation appendix for each component practice (retrieval practice, distributed practice, CBT for test anxiety, EF scaffolding) with the actual papers, not the paraphrases currently in the gap analysis; (3) a written evaluation plan naming the measure, the timepoints, who collects, and who analyses. That is a legitimate Tier IV today. Tier III (promising) becomes reachable at roughly n=60-100 across several cohorts *with a matched comparison group* — note that a self-selected cohort makes the required statistical control for selection bias hard, so design the comparison in from cohort 2, not after. Tiers I and II are multi-year, funded research. Never claim a tier you have not earned.

### F12 — Content production for 280 certification contact hours and 100+ cultural profiles is the largest real cost and appears nowhere

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.86 |

**What the artifact says**
> Four certification tracks are fully specified: MCST '12 modules | 40 hours' (line 334), MCPT '10 modules' (line 364), MCLSS '12 domains | 80 hours' (line 394), MMEC '16 modules | 120 hours' (line 419). Plus 'Scholar + inventor + leader profiles (100+)' (line 534), a '500-item adaptive item bank' (line 600), '200+ CBT prompt library' (line 595), and a '60-source PhD bibliography' (line 137).

**The problem**

That is roughly 280 contact hours of assessed, media-bearing instruction, 50 modules, 100+ researched biographical profiles, a 500-item psychometric item bank, four exam structures with rubrics including video-scored teaching demonstrations and an 8,000-word blind-peer-reviewed action research paper. This is the single largest cost in the business and it has no line, no owner (the plan assigns it to 'Content Agent' and 'Curriculum Agent' — which are prompts, not people), and no quality gate beyond 'confidence scoring' on AI output. Content at this volume generated primarily by LLM and shipped without SME review is also the fastest path to the cultural-appropriation risk the artifact itself rates High (line 120), since the ancestor profiles are exactly the content that must not be hallucinated.

**Evidence**

[INFERENCE.] Commonly cited e-learning benchmarks put development at ~100-200 hours per finished hour of Level 2-3 interactive content (Chapman Alliance) [EXPERT-OPINION, dated, not replicated]. At a deliberately conservative 30 development hours per contact hour, 280 contact hours = 8,400 hours ≈ 4 FTE-years. The artifact's own mitigation commits to 'African-centered scholars as PAID co-developers' and a 'community advisory board with veto power' (line 120) — at 100 profiles × $150-$400 per reviewed profile that is $15,000-$40,000, plus $6,000-$20,000 in advisory stipends, none of it budgeted.

**Recommendation**

Cut to one track and six contact hours. The 90-day wedge needs a six-session family workbook, roughly 9 contact hours of live facilitation, and 10 ancestor profiles, not 50 modules and 100 profiles. Build those 10 profiles properly — paid scholar review, sourced, fact-checked — so the quality bar is established on a small surface. Then price the rest honestly in the model as a post-validation expense with a per-module unit cost you have actually measured from building the first six.

### F13 — Both certification revenue lines depend on accreditations that do not exist; 'CEU-eligible' and 'graduate credit' are stated as facts

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> Line 725: 'Paraeducator Certification $299 / individual — 80-hour MCLSS program; CEU-eligible; MCPS partnership'. Line 726: 'Teacher PD Certification $499 / individual — 120-hour MMEC program; university partnership track; optional graduate credit'. Line 440: 'Target partners: Howard University, Morgan State, UMCP'. Line 419: 'CEU-eligible'.

**The problem**

'CEU-eligible' is not a property a provider can self-assert — it requires an accrediting relationship (IACET accreditation, or a state/university/professional-body approval pathway). 'Graduate credit' requires a signed articulation agreement with an accredited institution; the artifact names three targets, which means zero agreements exist. 'MCPS partnership' is also asserted, not signed, and runs straight into the conflict-of-interest problem in F02. Strip the accreditation claims and you are asking a paraeducator to pay $299 out of a support-staff wage, and a teacher $499, for 80-120 hours of training from an unknown provider that moves neither their pay nor their license. The realistic take-up at that price is near zero, which means $54,850 of the stated revenue (14% of the total) rests entirely on paperwork that does not exist. In Maryland, teacher recertification runs through MSDE-approved CPD; a non-approved program earns nothing a teacher can use. [MSDE's specific CPD approval process and IACET's current fees and timelines are UNVERIFIED — check mdcert/MSDE's certification pages and iacet.org directly.]

**Evidence**

[INFERENCE from the artifact's own text — it names 'target partners,' which concedes none are signed.] Market context: free and employer-paid PD dominates this space (Khanmigo is free for verified US K-12 teachers; MagicSchool has a free teacher tier), so an individual-pay $499 program competes against $0.

**Recommendation**

Remove both lines from Year 1 revenue entirely and reclassify them as Year 2+ contingent on a signed agreement. If you want this channel, invert the payer: sell the paraeducator training to the employer as contracted professional development at $3,000-$8,000 per session-day for a group, which is how PD actually gets bought, and which also removes the individual-affordability problem. Pursue one accreditation pathway at a time, and only after a buyer has said in writing that accreditation is what is blocking the purchase.

### F14 — Production infrastructure is over-architected by roughly an order of magnitude and violates the founder's own 'no recurring expense before validation' rule

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Line 702: 'Production — AWS ECS Fargate (auto-scaling); CloudFront CDN; RDS PostgreSQL Multi-AZ; ElastiCache Redis cluster; S3 media ... Blue/green deployment; 99.9% SLA target; multi-region failover (us-east-1 primary → us-west-2 DR)'. Line 660 simultaneously specifies Supabase, Pinecone/pgvector, Upstash Redis and S3. Line 679 adds FastAPI '10k+ req/sec capable' and Celery.

**The problem**

This is a configuration for tens of thousands of concurrent users, specified for a product whose Year 1 goal is 500 families and whose Phase 1 goal is 10. Multi-region DR, Multi-AZ RDS and an ElastiCache cluster alone are a $2,000-$6,000/month standing commitment, $24,000-$72,000/year, for a user base that would fit comfortably on a single $25/month Supabase project and a $30/month app server. It also duplicates itself — Supabase Postgres and RDS Postgres, Upstash Redis and ElastiCache, Pinecone and pgvector are each two answers to one question. The founder's stated principles include cost discipline, shared AEOS infrastructure over per-module duplication, and no recurring expense before validation; this tab contradicts all three, and it is also a second, independent stack from the AEOS repo (Next.js 16 + React 18 + TypeScript, FastAPI + Supabase), meaning two security models and two things to keep patched.

**Evidence**

[INFERENCE from the stated architecture vs. the stated user counts, priced against AWS and Supabase public list pricing.]

**Recommendation**

Delete the production tab and replace it with: Supabase Pro ($25/mo), one small app host ($20-$50/mo), Cloudflare free tier, nightly logical backups. Total under $100/month. Reuse the AEOS stack and the AEOS row-level-security model rather than standing up a second one — that is the founder's own shared-infrastructure principle, and it also means the committed security mutation test suite covers this product too. Pick one database, one cache, one vector store. Revisit the architecture at 5,000 paying users, not at 10 pilot families.

### F15 — LLM inference cost per family is unmodelled and uncapped at a $49/month price point

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.83 |

**What the artifact says**
> Line 536: '24/7 homework scaffolding (Socratic method)' and 'Test anxiety emergency support chat'. Lines 593-600 specify eight agents with persistent memory. Line 679: 'Claude 3.5 Sonnet / DeepSeek-V3'. Line 723 prices at '$49/mo | $399/yr'. No per-user cost appears anywhere.

**The problem**

The product promises unlimited 24/7 conversational AI to the heaviest-usage population imaginable — middle schoolers doing homework every weeknight — at a flat $33/month effective price ($399/12), of which 15% goes to the app store, leaving ~$28. An eight-agent orchestration with persistent memory re-sends context on every turn, so cost scales superlinearly with session length. At a plausible 200 sessions/year/family and ~15K tokens per session across agents, a 500-family base is on the order of 1.5B tokens before any retries, evaluation passes, or the 'confidence scoring on ALL outputs' plus human review queue promised at line 634 — which is a second inference pass on everything. A $3-$15/family/month inference bill is entirely plausible, i.e. 10-50% of net revenue, and the design contains no usage cap, no cheaper-model routing by task, and no caching strategy.

**Evidence**

[INFERENCE from the stated architecture; the token estimate is my own and should be replaced with measured data from the first 10 users. The model named at line 679, 'Claude 3.5 Sonnet', is also outdated as a 2026 build target — check current model availability and pricing before committing a cost model to it.]

**Recommendation**

Instrument cost-per-user from user #1 and make it a first-class metric on the same dashboard as revenue. Add a monthly token budget per account with graceful degradation, route cheap tasks (summaries, card generation) to a small model and reserve the frontier model for the tutoring turn, cache aggressively, and drop the 'confidence scoring on ALL outputs' double-pass in favour of scoring a sampled subset. Then set price from measured gross margin, not from what felt affordable.

### F16 — Grant funds are treated as margin-bearing revenue; restricted federal funds do not work that way

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.86 |

**What the artifact says**
> Line 745 places '$100,000' grant funding in the same revenue row as subscriptions, and line 755-757 flows it straight into 'Total Year 1 Revenue $391,850' and 'Net Year 1 ~$216,850'.

**The problem**

Federal award dollars are restricted to the awarded scope and are generally drawn down on a cost-reimbursement basis — you spend first, then request funds, often on a 30-day cycle. They do not produce net income; by construction they net to approximately zero against the allowable costs they fund. Booking $100,000 of grant money as revenue inflates 'Net Year 1' by the full $100,000, which is 46% of the stated net. There is also unbudgeted compliance overhead: SAM.gov registration and renewal, a negotiated indirect cost rate or the 10% de minimis rate, time-and-effort reporting, procurement standards, and Single Audit obligations above the threshold (raised to $1,000,000 for fiscal years beginning on or after October 1, 2024 under the 2024 Uniform Guidance revision — [UNVERIFIED, confirm at 2 CFR 200.501 before relying on it]).

**Evidence**

Uniform Guidance cost-reimbursement and audit mechanics at 2 CFR Part 200 [ESTABLISHED in general structure; specific section numbers and the current audit threshold are UNVERIFIED here — read 2 CFR 200 directly]. ED/IES SBIR is a contract-based programme with its own payment schedule distinct from a grant [the exact payment mechanics are UNVERIFIED; ies.ed.gov did not resolve in this session and would need to be allowed in the session's network settings].

**Recommendation**

Move grants out of the revenue statement entirely and into a separate 'non-dilutive capital' schedule with its own timeline and its own probability weighting. Show operating revenue, operating cost, and operating net without grant money, so you can see whether the business works. Then show grant capital as a financing line that extends runway, which is what it actually is.

### F17 — No churn, retention or LTV anywhere; $399 of ARR is not $399 of LTV

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.84 |

**What the artifact says**
> Line 723: 'Goal: 500 families Year 1'. Line 780: '500 family subscriptions' as a Phase 4 KPI. Lines 772-781 list KPIs including 'Diagnostic completion rate ≥ 80%', 'BARS daily use ≥ 5 days/week', 'NPS ≥ 70' — but no retention, renewal or churn KPI appears in any phase.

**The problem**

In a subscription business, retention is the business. Consumer kids' education is one of the worst-retaining categories there is, for a structural reason the plan actively worsens: the product's success condition — the child becomes a confident self-directed learner — is also the cancellation trigger. A 500-family Year 1 ending number is not the same as 500 families × $399; with 50-60% annual churn you need to acquire 700-900 to end at 500, which multiplies CAC by the same factor. The plan also has no renewal mechanic, no reason to stay after the certification is earned, and no second-year value proposition.

**Evidence**

Vendor-published benchmarks: kids' education apps ~7.4% monthly churn (~60% annual) with 'child lost interest or engagement dropped' cited as 36% of cancellations; broader edtech estimates range from 3.8% to 9.6% monthly across sources, so treat the range as wide; consumer learning apps commonly quoted at 30-50% annual retention versus ~85% for B2B; education-app first-renewal survival just over 50%; involuntary (failed-payment) churn commonly 20-40% of total churn. [EMERGING — these are vendor and aggregator blogs, not peer-reviewed; the spread between sources is large enough that none should be used as a point estimate. The B2B-vs-B2C retention gap is the robust part and is the part that matters here.]

**Recommendation**

Add retention as a Phase 1 KPI, not a Phase 4 one, and model gross LTV as ARPU × expected tenure × (1 − store fee − processing − inference − support). Then notice what the benchmarks are telling you: B2B retains at ~85% and B2C at ~40%, which is a second independent argument for the institutional motion. Add dunning and card-updater from day one — 20-40% of churn is just failed payments and it is the cheapest retention you will ever buy.

### F18 — Twelve-month roadmap scope is 8-15 FTE-years, to be executed by one employed person

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.89 |

**What the artifact says**
> Lines 770-781 commit, within 12 months, to: a validated 52-domain student instrument, a 38-domain parent instrument, a 24-domain staff instrument, a React Native app shipped to both stores, a Next.js web dashboard, an eight-agent LangGraph system, Anki SM-18 integration with AnkiConnect sync, an IEP PDF-parsing accommodation engine, four certification tracks (50 modules), a 40-culture ancestor library with 100+ profiles, Google Classroom and Canvas LMS integrations, a district admin dashboard, a cohort community platform, a Spanish-language beta, a university partnership, two federal grant applications, five signed school contracts and 500 family subscriptions.

**The problem**

Any one of these items — the LMS integrations alone, or app store review for a minor-facing app with in-app purchase, or the IEP parser — is a quarter of engineering for a team. The combined scope is on the order of 8-15 FTE-years. The founder is a full-time MCPS employee. Even assuming heavy AI assistance and a generous 25 hours/week, that is roughly 0.6 FTE-years of founder capacity in Year 1. The plan is therefore over-committed by a factor of 15-25x, and over-commitment at that ratio does not produce a late product — it produces no product, because nothing reaches a shippable state and no experiment ever runs. Phase 1 alone (Months 1-3) gates the 10-family pilot behind building the diagnostic, the parent diagnostic, the BARS MVP, three anxiety modules, the FERPA database and a 20-culture ancestor library — so the first contact with a real user is deferred six months behind a build the founder does not have capacity to finish.

**Evidence**

[INFERENCE from the stated scope against one person's available hours.]

**Recommendation**

Invert the sequence. The pilot is not the output of the build; it is the input. Run the first cohort in the next 90 days with paper, Zoom, a Google Form and a Notion page — zero engineering. Let what the families actually use decide what gets built. Then cut the Year 1 roadmap to the three things the cohort proved people used, and delete the rest from the document so it stops consuming attention.

### F19 — Support cost is zero in a plan serving the highest-support-need population in consumer edtech

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.8 |

**What the artifact says**
> The product serves neurodivergent middle schoolers (line 54), under-resourced parents who 'can't teach what they don't know' (line 55), and promises 'Parent-to-parent peer messaging (cohort)' (line 535), 'Family cohort community discussion board' (line 535), crisis escalation (line 572), IEP document upload and parsing (line 568), and a Spanish-language version (line 780). No support, moderation, or community-management cost appears in the model.

**The problem**

This is a high-touch population by design — that is the thesis — and high touch is a cost. Onboarding a parent who has never used a study system through a 38-domain diagnostic, an IEP upload, a family schedule merge and a certification portal is not self-serve. At 500 families and a conservative 0.5-1.5 contacts per family per month at 10 minutes each, that is 40-110 hours/month, or $10,000-$40,000/year at $20-$30/hour — before the moderation obligation that comes with running a minor-adjacent community, and before Spanish-language support, which the plan promises but staffs with nobody. Community moderation of a space containing minors also carries its own liability and is not a volunteer job.

**Evidence**

[INFERENCE from the product surface area and the stated population.]

**Recommendation**

Add a support line at $25-$60 per family per year and a community-moderation line, and then use that number to kill features: every surface in the App Design tab that generates a support contact should have to justify itself against that cost. Specifically, defer the community/discussion board — it is the highest-moderation, lowest-early-value surface in the product, and a cohort of 10 families on a group call does the same job with zero platform risk.

### F20 — No kill criteria, no decision gates, and no definition of failure anywhere in the plan

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.87 |

**What the artifact says**
> Lines 770-781 define four phases with milestones and KPIs, all of which are success targets ('10 pilot families enrolled', '5 school contracts closed', 'NPS ≥ 70'). No phase contains a condition under which the next phase does not start, and no KPI has a floor that triggers a stop.

**The problem**

A plan with only success criteria cannot be falsified, which means it cannot be learned from, which means it consumes capital and years until the founder runs out of either. This is the most common cause of death in this category and it is entirely self-inflicted. It also directly contradicts the founder's stated ordering of completion > validation > monetization > scaling: validation implies the possibility of invalidation, and there is none here.

**Evidence**

[INFERENCE from the roadmap structure.]

**Recommendation**

Write three numbered gates with explicit stop conditions before doing anything else. Gate 1 (Week 6): ≥3 paid deposits or one signed institutional LOI from 20 qualified conversations — if not, the willingness-to-pay hypothesis is falsified and the offer changes. Gate 2 (Week 14): ≥60% of enrolled families attend ≥5 of 6 sessions — if not, the engagement hypothesis is falsified and the format changes. Gate 3 (Week 16): pre/post shows direction-consistent movement on the anxiety measure and on one academic behaviour measure, plus ≥3 families say unprompted that they would pay — if not, the efficacy hypothesis is unsupported and the content changes before anything is built. Publish these gates to yourself and to one outside person who will hold you to them.


---

## What is missing and should be added

### Corrected Year 1 financial model structure (replace the five-tile table on lines 739-758)   `INFERENCE`

**Why it matters.** The current model is five products of unit counts and list prices minus an undefined round number. It cannot be stress-tested, cannot be shown to an investor or a grant reviewer, and cannot tell the founder when to stop. A driver-based model with Low/Base/High columns converts a wish into a set of testable assumptions and makes the breakeven visible.

**What to build.** A single spreadsheet, four tabs. TAB 1 ASSUMPTIONS — every number used anywhere, each with a source cell and a 'measured / estimated / guessed' flag. TAB 2 REVENUE, driver-based, not unit-times-price: Institutional cohorts = (conversations → qualified → LOI → signed) with stated rates × price per cohort; D2C = (visits → trial → paid → retained at 12 months) × net price after 15% store and 2.9%+$0.30 processing; certification = 0 until an accreditation agreement is signed (show as a separate contingent block, not in the total); grants = $0, moved to Tab 4. TAB 3 COSTS, one row per item with Low/Base/High and a 'committed / deferred-until-validated' flag: founder comp (show as $0 cash plus an explicit note of 0.6 available FTE-years); content production at a measured $/contact-hour; school psychologist and instrument licensing; legal, including a Maryland ethics opinion; insurance (E&O, cyber, and a flag for the crisis-detection exclusion); security testing, marked deferred; infrastructure at the real MVP number (<$100/mo, not $2-6K/mo); LLM inference at measured $/family/month; support at $/family/year; CAC blended; payment processing; store commission; admin, entity, accounting. TAB 4 CAPITAL & GATES — non-dilutive capital timeline (ED/IES SBIR FY2027, ~14-month cash lag) kept out of operating revenue, plus the three kill gates with their dates and thresholds. HEADLINE NUMBERS to carry: Base case Year 1 revenue $15,000-$30,000; Base case Year 1 cash cost ~$20,000; Base case net roughly breakeven. As-written-plan case for contrast: revenue $7,000-$40,000, cost $600,000-$1,100,000, net −$600,000 to −$1,050,000.

**Evidence.** Rebuilt from the artifact's own line items (lines 723-757) plus verified external rates: Apple App Store Small Business Program 15% at ≤$1M prior-year proceeds (developer.apple.com); Google Play subscriptions at an effective 15%; MCPS middle-school FARMS 6.4%-63.3% (MCPS BoE ms-farms.pdf); kids' edtech churn ~60% annual (retentioncheck.com, vendor-published); ED/IES SBIR Phase I $250K/9mo, Phase II $1M/2yr; NSF SBIR Phase I ceiling $305,000 with mandatory invited Project Pitch and a >50%-employment PI requirement (NSF 26-510).

### The 90-day single-motion plan: one institutional buyer, one facilitated cohort, zero software   `INFERENCE`

**Why it matters.** Four simultaneous motions by a part-time solo founder produce no signal from any of them. One motion, run to completion, produces cash, evidence, testimonials and a reference — in that order — and it is the only sequence consistent with completion > validation > monetization > scaling.

**What to build.** DAYS 1-14, LEGAL AND OFFER. Request a written MCPS Ethics Officer advisory opinion on outside employment and selling to the district; retain a Maryland attorney for 3-5 hours to read it ($2,000-$5,000 total). Form the entity. Write a one-page offer (see separate addition). Build the Tier IV logic model. Get three E&O/cyber quotes and read the mental-health exclusions. DAYS 15-35, SELL. Build a list of 25 institutional buyers who are NOT MCPS: 21st CCLC and afterschool providers in Montgomery County, Identity Inc. and similar county youth nonprofits, Black church education ministries, the county NAACP education committee, Boys & Girls Clubs, PGCPS Title I middle school principals, Maryland non-public SPED schools, and two or three PTAs at high-FARMS MCPS middle schools (PTA money is not district procurement, but still run it past the ethics opinion first). Hold 15-20 conversations. Target three LOIs. DAYS 36-49, CLOSE ONE. Sign one cohort at $7,500-$12,000, invoice 50% up front. GATE 1: if zero LOIs from 20 qualified conversations, stop and change the offer. DAYS 50-90, DELIVER COHORT 1. Eight to twelve families, six weeks, two 75-minute evening sessions per week, virtual or in the partner's space. Printed family workbook. A one-page family study plan per family. Pre/post on a properly licensed published test-anxiety measure plus one academic behaviour measure (assignment completion from the gradebook the partner already has). Three recorded testimonials. GATE 2 at week 14: ≥60% attend ≥5 of 6. GATE 3 at week 16: direction-consistent pre/post movement and ≥3 unprompted willingness-to-pay statements. TOTAL CASH OUT: under $20,000, of which $10,000-$14,000 is legal, ethics and insurance you need regardless. TOTAL CASH IN: $7,500-$12,000. NOT IN THE 90 DAYS: no app, no Supabase, no LangGraph, no React Native, no app store, no certification tracks, no grant application, no MCPS sale.

**Evidence.** [INFERENCE, constructed from the founder's stated constraints — employed full-time, limited capital, legal exposure around selling to his own employer — plus the verified ethics position (MCPS Regulation GCA-RA, Ethics Officer at 240-740-3030) and the verified B2B-vs-B2C retention gap (~85% vs ~40% annual).]

### The wedge offer one-pager: 'The Test-Ready Family Cohort'   `INFERENCE`

**Why it matters.** Section 6 asks for one offer sellable to a real buyer within 90 days for real money that generates evidence and fits the constraints. This is it. It converts the strongest asset in the document — the founder's credibility with these families and inside SPED practice — into revenue without building anything, without CAC, without churn, without store fees, and without the crisis-detection liability.

**What to build.** OFFER: six weeks, twelve 75-minute live sessions, 8-12 parent-child pairs, delivered by the founder. Family workbook (printed). One personalised family study plan per family. Pre/post measurement. A written summary report to the partner organisation at the end. PRICE: $7,500-$12,000 per cohort to the institution (≈$625-$1,000 per family), 50% on signature. D2C fallback if a parent pays directly: $1,800 per family — priced against the real substitute, 8-12 hours of executive-function coaching at $115-$265/hour, i.e. $1,400-$2,600, not against a $49/month app. BUYER: the director of an afterschool or youth-services organisation that already serves these families and already holds the budget — 21st CCLC provider, county nonprofit, church education ministry, Title I school principal with schoolwide funds. Explicitly not the founder's employer for cohort 1. PITCH, verbatim: 'Your students' grades are being suppressed by test anxiety and the absence of a study system, not by content gaps. Their parents want to help and were never taught how. Give me twelve families for six weeks and I will give you pre/post data you can put in your own report to your own funder — and the families keep the system.' DEFINITION OF DONE: cash received; ≥10 families complete ≥5 of 6 sessions; pre/post collected on every completer; three recorded testimonials; one written logic model; one letter of support naming intent to run cohort 2.

**Evidence.** Beyond BookSmart programs 'start at $165 per week' on prepaid 45-minute session packages; the broader EF coaching market is quoted at $115-$265 per hour (Life Skills Advocate), and EF coaching is explicitly not insurance-reimbursable, so families in this category already pay cash for this outcome. [EMERGING — vendor and third-party pages, dates vary; confirm current pricing before anchoring to it.]

### The ESSA Tier IV evidence package (the sales asset the document is missing)   `ESTABLISHED`

**Why it matters.** Every district buyer's compliance officer asks for the evidence tier before the budget conversation, and it is the precondition for a school lawfully spending Title I or IDEA money with you. It costs almost nothing to produce, and it is the asset that makes the 10-family pilot legitimately useful instead of anecdotal.

**What to build.** A six-page PDF. PAGE 1, logic model: inputs → activities → outputs → short-term outcomes → long-term outcomes, drawn from the Course Design tab. PAGES 2-4, component evidence: for each practice in the intervention (retrieval practice, distributed practice, CBT for test anxiety, EF scaffolding, parent academic involvement), the actual primary citations with effect sizes as reported, replication status noted honestly, and any contested findings flagged — not the paraphrases currently in the gap analysis, several of which assert effect sizes that need independent verification before they go in front of a buyer. PAGE 5, evaluation plan: measure, timepoints, who collects, who analyses, sample size, and the comparison-group design for cohort 2 onward. PAGE 6, a plain statement of what you have NOT established, which is what makes the rest credible. Add a cover line: 'This intervention currently demonstrates a rationale (ESSA Tier IV). It does not yet meet Tier III, II or I, and we will not claim otherwise.'

**Evidence.** ESEA §8101(21)(A) defines four evidence levels — strong (experimental), moderate (quasi-experimental), promising (correlational with statistical controls for selection bias), and demonstrates a rationale. Section 1003 school-improvement funds require Tiers I-III; other Title I-IV uses may rely on Tier IV. Tier IV requires a well-specified logic model informed by research or an evaluation plus an ongoing or planned effort to study effects. Reflected consistently in CA Dept of Education, RIDE, ND DPI and NH DOE guidance and in AIR's 2019 'Selecting Evidence-Based Practices' — but the exact statutory wording of the Tier IV evaluation element is UNVERIFIED here and should be read from the statute or ED's 2016 non-regulatory guidance before publication.

### Non-MCPS buyer list with budget sources named   `INFERENCE`

**Why it matters.** The plan's entire institutional motion points at the founder's own employer, which is the one buyer he structurally cannot sell to cleanly. There are adjacent buyers with the same families, real budget, far shorter procurement cycles and no conflict — the document names none of them.

**What to build.** A 25-row target list, each with: organisation, contact, which budget line pays (21st CCLC federal afterschool funds; county youth-services grants; foundation program budgets; PTA funds; a Title I school's schoolwide allocation; a non-public SPED school's tuition revenue; IDEA Part B through a PGCPS SPED department), approximate decision-maker authority level, cycle timing, and warm-intro path. Prioritise by (budget authority of a single person) × (urgency of their current problem) × (shortness of their cycle). A 21st CCLC site director who can sign a $10,000 enrichment contract this quarter beats a district with a $150,000 budget and an 18-month cycle, every time, at this stage.

**Evidence.** [INFERENCE.] Grounding: MCPS adopted CEP in 60 schools for 2025-26 and middle-school FARMS rates reach 63.3%, so the target population is concentrated and identifiable by school. A November 2025 county Inspector General finding that MCPS spent funds without required Board approval means district procurement is under heightened scrutiny right now — an additional reason not to make MCPS the first customer.

### Honest competitive battlecard replacing the 'No Comparable App Exists' card (lines 243-246)   `EMERGING`

**Why it matters.** The current card is the thing in this document most likely to end an investor meeting, and it is the thing most likely to get the founder blindsided by a competitor he has not met. Replacing it with a real one also forces the differentiation question to a real answer.

**What to build.** A one-page card with four blocks. BLOCK 1, who occupies the ground today, by buyer: school SEL/MTSS (Panorama, Branching Minds, Closegap, Satchel Pulse, 7 Mindsets, Rethink Ed), school mental health (Hazel Health, Daybreak Health, Cartwheel, Care Solace), AI tutors (Khanmigo, MagicSchool, SchoolAI, Brisk — plus ChatGPT/Claude/Gemini as the free substitute for the AI Tutor surface at line 536), EF coaching (Beyond BookSmart, EF Specialists, Life Skills Advocate), ADHD/EF apps (Joon, Tiimo, Goblin Tools, Inflow, Brili), tutoring (Paper, Varsity Tutors for Schools, Littera, Tutor.com free via public libraries), culturally responsive curriculum (Newsela, EL Education, Learning for Justice), IEP and advocacy (Frontline IEP, PowerSchool Special Programs, SpedTrack, AbleSpace, Undivided, COPAA, Wrightslaw). BLOCK 2, honest differentiation, exactly three items: the parent-child dyad as the unit of intervention; EF + test anxiety + identity affirmation in one protocol for this specific population; founder proximity and, once it exists, outcome data in that population. BLOCK 3, honest substitutes a parent actually buys: a $60-80/hour tutor, the 504/IEP accommodations they already have, free Khanmigo or ChatGPT, library Tutor.com, or nothing. BLOCK 4, who could add your layer in a quarter: Khan Academy, MagicSchool, SchoolAI, Panorama, Newsela, Understood.org, ClassDojo — and the one-sentence answer to why that does not kill you (relationship and data, not features).

**Evidence.** Verified current product facts: Khanmigo free for verified US K-12 teachers, $4/month or $44/year for learners; MagicSchool free tier, Plus $12.99/month or $99.96/year, custom district Enterprise; Panorama district contract example $396,900 over three years; Care Solace district contracts $10,000-$133,000+; 7 Mindsets $3,498-$26,250; Beyond BookSmart from $165/week. [Vendor pages and third-party vendor-intelligence blogs; district per-student figures for Khanmigo (~$10-$35/student/year) are secondhand and UNVERIFIED.] Undivided's price is not published anywhere I could find.

### Three kill gates with dates, thresholds and a named witness   `INFERENCE`

**Why it matters.** The roadmap contains only success criteria across four phases. A plan that cannot fail cannot teach, and the founder's stated principle of validation before monetization is meaningless without a defined invalidation.

**What to build.** GATE 1 — WILLINGNESS TO PAY, week 6. Threshold: ≥3 paid deposits or 1 signed institutional LOI from 20 qualified conversations. Cost to reach: ~$400 (landing page, printing). If failed: the offer is wrong, not the market — rewrite the offer and re-run once; if it fails twice, the thesis that this buyer pays is falsified. GATE 2 — ENGAGEMENT, week 14. Threshold: ≥60% of enrolled families attend ≥5 of 6 sessions. Cost: ~$1,500. If failed: the format is wrong — this is the cheapest possible discovery that a family-dyad model does not survive contact with real family schedules, and it is far better learned here than after building a React Native app. GATE 3 — EFFECT, week 16. Threshold: direction-consistent pre/post movement on the licensed anxiety measure plus one academic behaviour measure, and ≥3 families stating unprompted that they would pay. Cost: $1,500-$4,000 (school psychologist to select, administer and score). If failed: the content changes before anything is built. Total cost to falsify the entire core hypothesis: under $5,000 and under 16 weeks. Name one outside person who holds you to each gate in writing.

**Evidence.** [INFERENCE.] The comparison that makes this compelling: the artifact's own Phase 1 and Phase 2 (lines 770-775) require six months of building — diagnostic, parent diagnostic, BARS MVP, three anxiety modules, FERPA database, ancestor library, Anki integration, eight-agent LangGraph — before the same questions get answered.

### AEOS portfolio decision memo: MindUnlock is content IP and a services program inside AEOS, not a second company and not a Year 1 software module   `INFERENCE`

**Why it matters.** Section 8 asks for the call. Here it is, with the reasoning, because getting this wrong doubles every fixed cost the founder has and halves the only scarce resource he has, which is attention.

**What to build.** THE CALL: one company, one platform. AEOS is the company and the infrastructure. MindUnlock is a program and content brand inside it, delivered first as services. It is not a separate legal entity, not a separate cap table, and not a second stack. REASONING. (1) FOCUS — two companies means two sets of filings, two insurance policies, two DPAs, two security reviews, two accounting trails, two brands to market, run by one person with a full-time job. That is a guaranteed loss, and it is the opposite of the founder's own completion-first rule. (2) SHARED INFRASTRUCTURE — AEOS already has the hardened multi-tenant model, row-level security and a committed security mutation test suite. That is the single hardest and most expensive asset to build for a district sale, and the MindUnlock tech tab proposes to rebuild all of it from scratch in a parallel stack (AWS ECS/RDS/ElastiCache alongside AEOS's Supabase). Reusing it is worth six figures and months, and it is the founder's own stated principle of shared infrastructure over per-module duplication. (3) WEDGE STRENGTH — AEOS's existing direction, teacher/SPED intervention workflow tooling with audit trails, is the stronger wedge on every dimension that matters: the buyer has a funded, recurring, compliance-driven pain (IDEA documentation, progress monitoring, MTSS logging); there is no consumer CAC; no app store commission; no churn curve; no psychometric validation prerequisite; and no crisis-detection liability. MindUnlock's content is what differentiates it — 'an intervention library with a cultural and executive-function layer' rather than 'another compliance tool' — which is precisely the position incumbents like Frontline and PowerSchool Special Programs cannot easily copy because they are compliance-first. (4) BRAND — keep MindUnlock as the family-facing program name; it is a good one and it carries the mission. Do not let it become a second corporate identity. (5) WHAT STAYS OUT — crisis detection does not go into AEOS under any circumstances. It would contaminate AEOS's compliance posture, its insurability and its district security review, and it is the one feature most likely to make the whole platform unsellable. THE ONLY CONDITION UNDER WHICH THIS CALL CHANGES: if the family cohort business reaches ~$150K of annual services revenue with a dedicated operator who is not the founder, it can be spun into its own entity. Not before.

**Evidence.** [INFERENCE from the founder's stated principles — completion > validation > monetization > scaling, MVP-first, shared AEOS infrastructure over per-module duplication, security over feature velocity — applied against the artifact's parallel-stack proposal at lines 658-702, which duplicates Postgres, Redis and the vector store and specifies a multi-region DR production configuration for a 10-family pilot.]

### Legal, ethics and insurance pre-work checklist (must complete before any selling)   `EXPERT-OPINION`

**Why it matters.** The document contains a six-item risk card that omits the two risks most likely to actually end this: the founder's employment conflict, and the insurability of crisis detection on minors. Both are cheap to resolve now and catastrophic to discover later.

**What to build.** Eleven items with owner, cost and date. (1) Written MCPS Ethics Officer advisory opinion on outside employment and sales to the district — $0, 2-4 weeks. (2) Independent Maryland attorney review of that opinion plus the outside-employment disclosure — $2,000-$5,000. (3) Entity formation, operating agreement, registered agent — $800-$2,500. (4) Three tech E&O and cyber quotes, with the specific question put in writing to each broker: does the policy cover or exclude a product that performs automated detection of student distress and notifies parents or counsellors — $0, 2-3 weeks. (5) Terms of Service and Privacy Policy drafted by counsel, including an explicit non-mental-health-service disclaimer — $4,000-$10,000. (6) COPPA verifiable-parental-consent flow reviewed by counsel before any under-13 account exists — included in (5). (7) Maryland student data privacy statute review and a standard DPA template a district can sign — $3,000-$8,000. [The applicable Maryland statute and its section numbers are UNVERIFIED here; counsel should identify them.] (8) Written license or permission for any published assessment instrument used, including the Spielberger TAI if it is used at all — quote required from the publisher, cost UNVERIFIED. (9) Paid agreements with African-centred scholar reviewers before any cultural content ships — $150-$400 per reviewed profile. (10) A written decision, signed and dated, that crisis detection is out of scope for 24 months. (11) Confirm with counsel whether any sale to a Maryland public school requires vendor registration, W-9/SAM, or background-check clearance for an adult working with students.

**Evidence.** MCPS Regulation GCA-RA and Board Policy BBB govern employee conflicts and state that violations 'may constitute grounds for removal from office, discipline, or other personnel action'; the MCPS Ethics Panel and Ethics Officer (240-740-3030) issue opinions. [ESTABLISHED that the process exists.] Insurance cost ranges and carrier behaviour toward minor-facing mental-health monitoring are EXPERT-OPINION and must be replaced with actual quotes.

### Unit economics worksheet: what a family actually costs to serve   `INFERENCE`

**Why it matters.** The plan prices at $399/year without ever computing cost to serve, in a product that promises unlimited AI tutoring, human review of AI outputs, crisis monitoring, community moderation and Spanish support to the most support-intensive population in the category. Price set above an unknown cost is not a business model.

**What to build.** A one-page per-family annual P&L: gross price $399; less store commission 15% ($59.85) or $0 if sold via web; less payment processing ~$11.90; less LLM inference (measure from the first 10 users — model $36-$180/year); less support ($25-$60/year); less content amortisation; less infrastructure per seat; less the human-review queue cost implied by 'human expert review for confidence score < 0.85' (line 118) — which is a per-conversation human cost nobody has priced. Then compute contribution margin, multiply by expected tenure (at ~60% annual churn, roughly 1.6 years), and compare to blended CAC. If contribution margin × tenure < CAC, the D2C motion is structurally unprofitable at $399 and no amount of growth fixes it. Run the same worksheet for a cohort family at $625-$1,000 institutional price with zero CAC, zero store fee and zero churn, and compare the two numbers side by side. That comparison is the single clearest argument for the motion recommended in these findings.

**Evidence.** Apple Small Business Program 15%; Stripe standard 2.9% + $0.30; kids' edtech churn ~60% annual (vendor-published); education-app average subscription $8.13/month or $56.09/year (Business of Apps) — note that last figure is a sharp warning: $399/year is roughly 7x the category average annual price, which raises the conversion bar substantially. [EMERGING — vendor and aggregator sources.]

### Scope-cut list: what to delete from the document this week   `INFERENCE`

**Why it matters.** The roadmap is over-committed by roughly 15-25x against the founder's available capacity. Deleting scope from the document matters as much as deleting it from the plan, because an aspirational document keeps consuming attention and keeps being shown to people who then evaluate the founder against it.

**What to build.** DELETE OR DEFER 24+ MONTHS: crisis detection and the counsellor notification pipeline (liability, see F05); the eight-agent LangGraph system (one well-prompted assistant does the job at a tenth of the cost and complexity); Google Classroom and Canvas LMS integrations (each a quarter of engineering, neither needed by a cohort); the IEP PDF parser and auto-configuration engine (high effort, high error cost, touches the most sensitive document in the student's file); the district admin dashboard; the cohort community and discussion board (moderation liability, low early value); the Spanish beta; three of the four certification tracks; the 500-item adaptive item bank; the 40-culture, 100+ profile ancestor library (build 10 properly); the GED-to-PhD pathway; the multi-region production architecture; the university graduate-credit partnership. KEEP FOR 90 DAYS: a six-session family workbook, a one-page family study plan template, 10 properly sourced and scholar-reviewed ancestor profiles, one licensed pre/post anxiety measure, a Google Form, a Notion page, and a Zoom account. REWRITE THE HEADERS: 'Psychometrically validated' → 'Draft instrument, not yet validated'; 'No Comparable App Exists' → the battlecard; 'PhD-Level' throughout → delete the phrase entirely, it reads as a credibility claim to an investor and as a red flag to an academic.

**Evidence.** [INFERENCE from the capacity analysis in F18: ~8-15 FTE-years of stated scope against ~0.6 FTE-years of available founder capacity in Year 1.]


---

## Open questions

- What does the MCPS Ethics Officer's written advisory opinion actually say about (a) forming a company that sells to MCPS, (b) selling to individual MCPS paraeducators and teachers, and (c) recruiting pilot families through the founder's MCPS role? All three are in the plan and none can be assessed without that opinion. This is the single highest-value unknown in the document.
- Will any carrier write tech E&O and cyber for a minor-facing product that performs automated distress detection and parent/counsellor notification, and at what premium and with what exclusions? Three written quotes would answer in three weeks and would also independently price the risk. My premium ranges are expert-opinion, not verified.
- What is the actual MCPS procurement threshold above which Board approval is required for a software purchase, and what is the cycle time from vendor contact to signed contract for a new, unproven vendor? Not published in the sources I could reach; the November 2025 county Inspector General report likely states the dollar figures.
- Is the Spielberger Test Anxiety Inventory (cited at lines 264 and 398 as an instrument the product administers and scores) licensable for commercial product use, from which publisher, and at what per-administration cost? If not, which validated, licensable alternative should be used for pre/post in a middle-school population?
- What is the historical number of ED/IES SBIR Phase I awards per year versus applications received, i.e. the real base rate? I could not retrieve it — ies.ed.gov does not resolve in this session and would need to be allowed in the session's network settings. Without the base rate, the expected value of a 200-hour proposal effort cannot be computed.
- Given federal education research disruption through 2025, is the ED/IES SBIR programme funded and running an FY2027 cycle at all? The FY2026 deadline (June 29, 2026) has passed. This should be checked directly on the IES solicitation page before any grant effort is scheduled.
- What is MCPS's current position on culturally responsive curriculum — is there an internal office or existing vendor already occupying this ground? If the district considers this layer internally owned, the differentiation argument weakens substantially for the MCPS buyer specifically.
- What does a paraeducator in MCPS actually earn, and what does the district currently pay per head for paraeducator professional development? Both numbers determine whether the para channel is an individual-pay or employer-pay motion, and the plan assumes individual-pay without evidence.
- Does any existing provider already sell a facilitated parent-and-child study-skills cohort to afterschool providers or Title I schools in the DMV, and at what price? I found no such vendor, but absence of evidence here is weak — this is a services market that does not advertise, and a few phone calls to 21st CCLC directors would resolve it.
- What is the real measured LLM cost per family per month at the usage intensity this product invites? Unknowable until the first 10 users are instrumented, and it determines whether $399/year is a viable price or a structurally loss-making one.
- Are the effect-size claims in the Course Design tab (line 465 'African-Centered Pedagogy ... ES: 0.8'; line 461 'interleaving beats blocked practice ... by 43%'; line 466 'agency in learning design produces 40% greater intrinsic motivation'; line 464 'stereotype threat ... suppress performance 15-20%'; line 41 '38% of middle schoolers experience debilitating test anxiety') traceable to the cited primary sources at those magnitudes, and what is their replication status? I did not verify any of them — that is the learning-science lens's job — but flagging it here because these numbers are load-bearing for the Tier IV evidence package, and a district buyer's research office will check them. Any one that does not hold up damages the credibility of all the others.
- Would a university partner (Howard, Morgan State, UMCP are named at line 440 as targets) take this on as a research collaboration with a faculty PI? That single relationship would solve the IES eligibility problem, the psychometric validation problem, the graduate-credit problem and the Tier III evidence problem simultaneously — it may be worth more than any of the four revenue lines in the plan.

