# Learning science expansion

> What the world evidence base says the platform should contain that it currently does not.

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

MindUnlock's instructional core is built on a thin, partly dated, and in several places actively contradicted slice of the learning sciences — and the places where it is wrong are its flagship, most-marketed features, not its margins.

Four load-bearing elements fail against evidence that is settled, not contested. (1) "Module 6: Speed Reading — Wade Cutler's Triple Reading Speed Method," promising "60–90% speed increase with equal or greater comprehension," contradicts Rayner et al. (2016, PSPI 17(1):4–34), which establishes a speed–accuracy tradeoff, shows eye movements are ≤10% of reading time, and finds speed-reading training teaches skimming. The artifact proposes to sell this to students it itself describes as having "literacy deficits" — the worst possible audience. (2) Diagnostic item "5.1 VARK modality preference" operationalises the meshing hypothesis, which Pashler et al. (2008) and Rogowsky et al. (2015) found unsupported; the artifact then wires an AI engine to match the diagnosed modality. (3) "Spaced repetition Anki engine (SM-18)" names an algorithm Anki does not and cannot use — SM-17/18 are proprietary SuperMemo; Anki ships modified SM-2 and FSRS. (4) "NASA BARS," the spine of the entire product, appears to be a confabulation: BARS is Behaviorally Anchored Rating Scales (Smith & Kendall, 1963), a performance-appraisal method with no NASA scheduling lineage I could find.

Compounding this, the Research Foundation table asserts precise effect sizes that no cited source supports — "African-Centered Pedagogy (ES: 0.8)," "40% greater intrinsic motivation (Gray, 2013)," stereotype threat "suppress performance 15–20%" — in a document whose author's stated principle is "no claims of validation that has not occurred." A district reviewer or IES panel will check these.

The remedy is not retreat but substitution. Nearly every instinct in this artifact — agency, cultural identity, family involvement, anxiety reduction — has a rigorous, replicated, IDEA-aligned, cheap-to-ship counterpart: Self-Determined Learning Model of Instruction instead of "child liberation"; utility-value and purpose-for-learning writing instead of pervasive "yet" scripting; HOPS and the Daily Report Card instead of EF games; morphology and fluency instead of speed reading; variation theory, bansho, and CPA instead of six competing note formats. The superset below is larger, better evidenced, and cheaper than what is there now.

---

## Findings

### LS-01 — Speed reading is a flagship module and it is contradicted by settled evidence — for exactly this population

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.92 |

**What the artifact says**
> "Module 6: Speed Reading — Wade Cutler's Triple Reading Speed Method" (MCST curriculum); "Result: 60–90% speed increase with equal or greater comprehension"; "Speed building: Preview Read alone = 60% speed gain"; also MCLSS Domain 4 ("90% faster study facilitation") and MMEC module "Speed Reading & Literacy Acceleration Methods".

**The problem**

The core claim — large speed gains with equal or greater comprehension — is the specific claim the field's definitive review rejects. Rayner, Schotter, Masson, Potter & Treiman (2016) conclude there is a speed–accuracy tradeoff; that eye movements account for no more than ~10% of total reading time (so there is little to optimise there); that regressions (rereading) exist to repair comprehension failures, so suppressing them worsens comprehension; and that what speed-reading training actually teaches is skimming, which is useful for gist but not for the comprehension-dependent academic tasks this product targets. Worse, the artifact's own Problem Statement says "Students with literacy deficits cannot access study strategies built for fluent readers" — and speed reading is the paradigm case of a strategy that only functions (as skimming) for readers with strong existing decoding, fluency and domain knowledge. The artifact also names the method "research-validated"; I could locate no peer-reviewed validation of Wade Cutler's Triple Reading Speed, and the 60–90% figure is unverified.

**Evidence**

Rayner, K., Schotter, E. R., Masson, M. E. J., Potter, M. C., & Treiman, R. (2016). So Much to Read, So Little Time: How Do We Read, and Can Speed Reading Help? Psychological Science in the Public Interest, 17(1), 4–34. https://journals.sagepub.com/doi/full/10.1177/1529100615623267 (PMID 26769745). Wade Cutler 'Triple Reading Speed' peer-reviewed validation: UNVERIFIED — I found no indexed study; I would check ERIC, PsycINFO and Google Scholar for 'Cutler triple reading speed' before any further use.

**Recommendation**

Delete the speed claim and the WPM framing entirely this week. Keep the three-pass structure but rename and re-ground it: Pass 1 becomes a pre-reading survey (structure scan, heading-to-question conversion) — defensible as a pretesting/advance-organiser device; Pass 2 stays close reading; Pass 3 becomes retrieval-based consolidation into FSRS cards. For students with decoding/fluency gaps, substitute the adolescent-literacy package in Addition 14 (repeated/partner reading for fluency, morphology, vocabulary depth). In the pilot, measure comprehension-per-minute on a fixed passage set rather than WPM, and publish whatever it shows.

### LS-02 — The student diagnostic measures VARK learning style and the AI engine is designed to match it — the meshing hypothesis, operationalised

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Diagnostic Domain 5, item "5.1 VARK modality preference (Visual / Auditory / Kinesthetic / Reading-Writing)"; Domain 4, item "4.8 Preferred cultural learning style (call-response, storytelling, movement)"; App Design: "Note-taking method selector" and Learning Path Agent "Curriculum Personalization" keyed to profile.

**The problem**

Measuring a child's modality preference and then personalising instruction to it is precisely the meshing hypothesis. Pashler, McDaniel, Rohrer & Bjork (2008) found that of the published studies using the required crossover-interaction design, essentially none supported it; Rogowsky, Calhoun & Tallal (2015), the cleanest replication following Pashler's criteria, found no relationship between learning-style preference and instructional mode on immediate or delayed comprehension. Shipping this does three kinds of damage: it burns diagnostic minutes from a child with EF deficits on a construct with no predictive validity; it hard-codes a neuromyth into the agent architecture, where it will silently misroute content; and it hands a reviewer (district, IES, IRB) the single fastest way to dismiss the whole evidence claim. The cultural-learning-style item (4.8) has the same structural defect: it converts a relational/engagement variable into a processing-channel prescription and risks essentialising Black children's cognition — the opposite of the artifact's stated intent.

**Evidence**

Pashler, H., McDaniel, M., Rohrer, D., & Bjork, R. (2008/2009). Learning Styles: Concepts and Evidence. Psychological Science in the Public Interest, 9(3), 105–119. https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/07/Pashler_McDaniel_Rohrer_Bjork_2009_PSPI.pdf. Rogowsky, B. A., Calhoun, B. M., & Tallal, P. (2015). Matching Learning Style to Instructional Method: Effects on Comprehension. Journal of Educational Psychology, 107(1), 64–78. https://www.apa.org/pubs/journals/features/edu-a0037478.pdf. Cuevas (2018) mini-review and Nancekivell et al. / Newton reviews document the myth's persistence among educators.

**Recommendation**

Delete item 5.1 outright. Replace with access-provision logic, not style-matching: offer text-to-speech, captions, and visual alternatives to every learner as a UDL access right (which is also what the IEP engine already needs), decoupled from any diagnosed 'type'. Rewrite 4.8 as 'cultural and family practices the learner already uses at home (storytelling, call-and-response, communal study)' and use it to shape social framing, examples and relatedness — not to route content modality. Add a single explicit line to the Staff certification: 'learning styles matching is a neuromyth; we do not use it,' which is itself a differentiator with MCPS PD leadership.

### LS-03 — "Anki SM-18" names an algorithm Anki cannot legally or technically use — a build-blocking spec error repeated across four tabs

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.95 |

**What the artifact says**
> "Spaced repetition Anki engine (SM-18)" (Solution/For Students); Next Action #7 "Integrate Anki SM-18 spaced repetition engine"; Tech Stack: "SM-18 Algorithm | Spaced Repetition | Anki-compatible; AnkiConnect sync; neurodivergent-adjusted ease factors"; Roadmap Phase 2: "Anki SM-18 integration + AnkiConnect sync"; Learning Path Agent tool "SM-18 spaced repetition scheduler".

**The problem**

SM-17 and SM-18 are proprietary SuperMemo algorithms requiring a licence. Anki's own documentation states that because the latest SuperMemo algorithm is proprietary and Anki is open source, Anki can only use freely available algorithms like FSRS, and that Anki's two schedulers are a modified SM-2 and FSRS. There is therefore no 'Anki SM-18' to integrate. This is not cosmetic: Phase 2 of the roadmap has an engineering milestone and an agent tool definition pointing at a nonexistent integration, and 'neurodivergent-adjusted ease factors' is an SM-2 concept that FSRS does not use (FSRS uses difficulty/stability/retrievability and a desired-retention parameter). The spec will not survive contact with a developer.

**Evidence**

Anki Manual / FAQ, 'What spaced repetition algorithm does Anki use?' https://docs.ankiweb.net/faqs/what-spaced-repetition-algorithm — states the first scheduler is based on SuperMemo 2, the second is FSRS, that SuperMemo's latest algorithm is proprietary and requires licensing, and that preliminary tests put FSRS roughly on par with SM-17. FSRS added in Anki 23.10 (open-spaced-repetition/fsrs4anki).

**Recommendation**

Globally replace 'SM-18' with 'FSRS (Free Spaced Repetition Scheduler)' and rewrite the tuning language: the per-learner knob is desired retention (e.g. 0.90 default), not 'ease factor'. This is strictly better for the IEP use case — FSRS lets you set a retention target and, with a known exam date, optimise the review schedule against that date (see Addition 7). If any SuperMemo algorithm is genuinely wanted, budget for a commercial licence and say so in the business model; otherwise remove every SM-18 reference before this document goes to a developer or a district.

### LS-04 — "NASA BARS" — the product's organising spine — appears to be a confabulation; BARS is a 1963 performance-appraisal method

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.8 |

**What the artifact says**
> "NASA BARS Method | Behavioral Anchoring / Mission-Critical Task Scheduling | NASA-derived time management adapted for student academic life"; MCST Module 7 "NASA BARS Mission Schedule Building"; MCLSS Domain 8 "NASA BARS adaptation for students"; BARS Schedule Agent; "BARS-format AI mission schedule builder".

**The problem**

BARS in the research literature is Behaviorally Anchored Rating Scales — Smith & Kendall (1963), a method for anchoring performance-appraisal rating scales in retranslated critical incidents, descended from Flanagan's critical incident technique. It is a measurement method for rating people, not a scheduling method, and has no NASA provenance. I searched and found no source for a 'NASA BARS' time-management or mission-scheduling method. The artifact makes this invented construct the backbone of the scheduler, an AI agent, a student certification module, a paraeducator competency domain, and a parent module. If a district curriculum reviewer, a grant reviewer, or a partner university checks one citation in this document, it will be this one, because it is named most often. The underlying feature (time-blocked, decomposed, externalised planning for students with EF deficits) is sound and well supported — it just has a different and better-evidenced genealogy.

**Evidence**

Smith, P. C., & Kendall, L. M. (1963). Retranslation of expectations: An approach to the construction of unambiguous anchors for rating scales. Journal of Applied Psychology, 47(2), 149–155. doi:10.1037/h0047060. 'NASA BARS' scheduling method: UNVERIFIED — no source located in web search; I would next check NASA Technical Reports Server (ntrs.nasa.gov) and the NASA Human Research Program task-scheduling literature before concluding it does not exist.

**Recommendation**

Either produce the primary NASA source this week or rename the feature. If renamed, re-ground it in evidence that is actually strong for this population: implementation intentions / if-then planning (Gollwitzer), the HOPS planner-and-materials routine with its RCT effect sizes (see Addition 13), and task decomposition as an extraneous-load reduction under CLT. That re-grounding makes the feature defensible to MCPS Special Education leadership and to an IES reviewer, which 'NASA-derived' never will be.

### LS-05 — "African-Centered Pedagogy ... (ES: 0.8)" is an effect size with no study behind it — and it is in the document's own Research Foundation table

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Course Design / Research Foundation: "African-Centered Pedagogy | Hilliard (1997), Nobles (2006), Asante (1987) | Culturally affirming instruction raises Black student achievement (ES: 0.8)".

**The problem**

None of the three cited authors published a meta-analysis producing a d=0.8 for African-centred pedagogy; Hilliard, Nobles and Asante are theorists of Afrocentric epistemology, not sources of pooled effect sizes. The number appears to be fabricated or borrowed from an unrelated benchmark (0.8 is Cohen's conventional 'large' threshold). This directly violates the founder's own stated principle, 'no claims of validation that has not occurred,' and it does real harm to the cause it serves: it invites a reviewer to dismiss culturally sustaining pedagogy as hype when there is a genuine and defensible quantitative record to cite instead. That record is narrower than d=0.8 and comes with scope conditions the artifact should state.

**Evidence**

Real quantitative evidence: Dee, T. S., & Penner, E. K. (2017). The Causal Effects of Cultural Relevance: Evidence from an Ethnic Studies Curriculum. American Educational Research Journal, 54(1), 127–166 — fuzzy regression discontinuity, San Francisco USD; assignment to the 9th-grade ethnic studies course raised attendance by ~21 percentage points, GPA by ~1.4 points (IV estimate; reduced-form ~0.4) and credits earned by ~23, for students near a sub-2.0 8th-grade GPA threshold. Bonilla, S., Dee, T. S., & Penner, E. K. (2021). PNAS 118(37) — graduation gains of ~16–19 percentage points. Both are contested on identification grounds (see Bisht, Bonilla, Kim & Penner on the districtwide expansion). Aronson, B., & Laughter, J. (2016). Review of Educational Research, 86(1) — synthesis of culturally relevant education across subject areas. Hilliard/Nobles/Asante effect size: NOT FOUND — unverified and almost certainly nonexistent.

**Recommendation**

Replace the '(ES: 0.8)' cell with the Dee & Penner / Bonilla et al. citation plus its explicit scope conditions (one 9th-grade course, one district, students near a low-GPA threshold, contested identification). Then add a second row that states the Afrocentric-epistemology commitment as a value claim argued on its own terms — citing Gyekye, Wiredu, Mkabela, Dei/Emeagwali — with no effect size attached. Separating those two registers (see Addition 16) is the intellectually honest move and it is also the move that survives peer review.

### LS-06 — "40% greater intrinsic motivation (Gray, 2013)" and the other precise numbers in the Research Foundation table are unsourced paraphrase

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> Gap Analysis: "Peter Gray (2013): Self-directed learning produces 40% greater intrinsic motivation"; Course Design: "Child Liberation Studies | Holt (1964), Gray (2013), Freire (1968) | Agency in learning design produces 40% greater intrinsic motivation". Adjacent: "Distributed practice produces 2× retention over massed practice"; "Self-testing produces 50% greater retention than re-reading"; "Mixed-topic practice beats blocked practice for long-term retention by 43%".

**The problem**

Peter Gray's Free to Learn (2013) is a trade book; it reports no 40% intrinsic-motivation figure, and no study I can locate does. Holt (1964) and Freire (1968) are likewise works of argument, not sources of effect sizes. The neighbouring numbers are the same genre of error in a milder form: they are single-experiment results stated as general laws. Roediger & Karpicke's '50%' comes from a particular passage-recall design at a particular retention interval; Rohrer & Taylor's interleaving advantage is from a specific maths-practice design; 'distributed practice produces 2× retention' collapses Cepeda et al.'s entire ridgeline function, whose point is that the advantage depends on the gap-to-retention-interval ratio. Presented as a table of laws, these numbers will not reproduce in a 10-family pilot, and when they do not, the founder will have no way to distinguish implementation failure from an overstated prior.

**Evidence**

Gray 'd=40% intrinsic motivation': NOT FOUND — unverified; I would check Free to Learn's endnotes and Gray's peer-reviewed papers in American Journal of Play before any further use. Roediger, H. L., & Karpicke, J. D. (2006). Psychological Science, 17(3), 249–255 — the percentage depends on retention interval and is not a constant. Rohrer, D., & Taylor, K. (2007). Instructional Science, 35, 481–498 — UNVERIFIED at primary for the '43%' figure. Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., & Pashler, H. (2008). Psychological Science, 19(11), 1095–1102 — optimal gap ≈20% of the retention interval at a few weeks, falling to ≈5% at one year; >1,350 participants. The ridgeline, not a 2× constant, is the finding.

**Recommendation**

Rewrite the Research Foundation table so each row carries: the exact study, the population, the retention interval, and the effect in the study's own units — plus a 'boundary conditions' column. Where the number cannot be sourced, write 'directional evidence; effect size not established' rather than inventing one. Replace the Holt/Gray/Freire row entirely with Self-Determination Theory and the Self-Determined Learning Model of Instruction (Addition 10), which supports the same design instinct with real intervention evidence in students with disabilities.

### LS-07 — Growth mindset is a cross-cutting design principle, delivered in a way the replication record does not support

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> "Growth Mindset | Dweck (2006) | Malleable intelligence framing raises achievement and resilience → Every module reframes 'I can't' as 'I can't YET'".

**The problem**

Making 'yet' scripting pervasive across every module is the highest-dose, lowest-evidence version of this intervention. Sisk et al. (2018), two meta-analyses covering 129 studies and 365,915 students on the correlational side, found a weak mindset–achievement association and an intervention effect of d = 0.08, 95% CI [0.02, 0.14]; Macnamara & Burgoyne's 2023 update in Psychological Bulletin reported largely non-significant effects. The National Study of Learning Mindsets (Yeager et al., 2019, Nature) found a small effect concentrated in lower-achieving students in schools with supportive peer norms — the effect is real but conditional, small, and produced by a brief, carefully scripted one-off session, not by saturation. Pervasive 'yet' language with anxious adolescents also risks the known failure mode of being heard as a demand ('your failure is a mindset problem') rather than as support, which is the opposite of what this population needs.

**Evidence**

Sisk, V. F., Burgoyne, A. P., Sun, J., Butler, J. L., & Macnamara, B. N. (2018). Psychological Science, 29(4), 549–571. https://pubmed.ncbi.nlm.nih.gov/29505339 — intervention d = 0.08 [0.02, 0.14] (figure as reported in Macnamara & Burgoyne's review; I did not open the Sage full text). Macnamara, B. N., & Burgoyne, A. P. (2023). Psychological Bulletin — updated review, effects largely non-significant. Yeager, D. S., et al. (2019). Nature, 573, 364–369 — NSLM; small conditional effect for lower-achieving students (effect magnitude REPORTED, not verified here).

**Recommendation**

Demote growth mindset from a cross-cutting principle to a single ~25-minute online session delivered once, with fidelity to the NSLM script, and measure it. Redirect the freed design budget to the motivation interventions that do replicate at this age — utility-value writing and purpose-for-learning (Addition 11). Keep the ancestral-heritage content, but attach it to belonging and purpose, which are better-evidenced mechanisms than implicit theories of intelligence.

### LS-08 — Pre-test ancestral/racial identity activation before every assessment is a plausible-harm design built on a contested effect size

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> "Stereotype Threat | Steele & Aronson (1995) | Identity-based negative stereotypes suppress performance 15–20% → African ancestor activation before every assessment; community affirmation ritual"; Cultural Identity Agent trigger: "pre-test anxiety ritual"; Diagnostic items 1.12 and 4.5.

**The problem**

Two problems compound. First, the '15–20%' figure has no source in Steele & Aronson (1995), whose results are in standardised units on a specific verbal-test design; the modern record is far weaker than the artifact implies. Flore & Wicherts (2015), meta-analysing stereotype threat in schoolgirls, found an uncorrected d ≈ .22 that fell to d ≈ .07 and non-significance after trim-and-fill, and explicitly concluded that publication bias might seriously distort the literature; Flore, Mulder & Wicherts (2018) ran the proposed registered replication and found no effect. Second — and this is the design risk — the stereotype-threat mechanism is that making a stigmatised identity salient in an evaluative setting impairs performance. The product proposes to make racial/ancestral identity maximally salient in the minutes before every assessment, to 12- and 13-year-olds. Even on the artifact's own theory of the effect, that is the wrong timing. Well-evidenced affirmation protocols (Cohen et al.) deliver values-affirmation writing in class, early in a term, away from the evaluative moment — not as a pre-test ritual.

**Evidence**

Flore, P. C., & Wicherts, J. M. (2015). Does stereotype threat influence performance of girls in stereotyped domains? A meta-analysis. Journal of School Psychology, 53(1), 25–44. http://icelab.psych.uw.edu.pl/wp-content/uploads/2018/10/florewicherts2015-Stereotype-threat.pdf (d values .22 uncorrected / .07 trim-and-fill are REPORTED via Replicability-Index secondary analysis; I did not verify at primary). Flore, Mulder & Wicherts (2018), Comprehensive Results in Social Psychology — registered replication, null. Cohen, G. L., Garcia, J., Purdie-Vaughns, V., Apfel, N., & Brzustoski, P. (2009). Science, 324, 400–403 — affirmation delivered in class early in the term; heterogeneous and context-dependent (UNVERIFIED at primary here).

**Recommendation**

Delete the '15–20%' figure. Move the identity/affirmation content out of the pre-test window and into a scheduled, in-class-style writing activity early in each unit, following the Cohen et al. protocol. Keep the ancestral content — it is the project's heart — but attach it to belonging, purpose and relatedness, which have better evidence and no salience-timing hazard. Then A/B it in the 10-family pilot: pre-test ritual vs. no ritual, with state anxiety and performance as outcomes. If the ritual helps, you will have an original finding; if it harms, you will have caught it at n=10 instead of n=500.

### LS-09 — Four of the six "research-validated" note-taking methods sit in Dunlosky's LOW-utility bucket, and teaching six formats is itself a load error

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> "📝 6 Note-Taking Methods (Research-Validated)": Cornell, Mind Mapping, Sketchnoting, Outline Method, Flow Notes, Atomic/Zettelkasten. MCST Module 4 "Note-Taking Mastery (6 Evidence-Based Methods)"; MCPT Module 4 "5 Note-Taking Methods You Can Teach Tonight"; MMEC "Note-Taking Curriculum Design".

**The problem**

Dunlosky, Rawson, Marsh, Nathan & Willingham (2013) classify summarisation, highlighting/underlining, imagery use for text learning, the keyword mnemonic, and rereading as LOW utility, and only practice testing and distributed practice as HIGH. Mind mapping, sketchnoting, outlining and flow notes are, in encoding terms, summarisation-plus-imagery variants: they produce an artefact at encoding time but nothing in them forces retrieval or self-explanation. Cornell and Zettelkasten are defensible only because of the steps the artifact lists last ('use cue column as retrieval practice deck'; 'write in YOUR OWN words'; 'becomes Anki deck') — i.e. the parts that are generation and retrieval, not the parts that are note formatting. Separately, requiring a grade 6–8 student with EF deficits and working-memory limitations to learn, select among, and be certified on six competing formats imposes exactly the extraneous load the artifact elsewhere promises to reduce, and the Outline Method row miscites Ausubel (advance organisers are a pre-reading device, not a note format).

**Evidence**

Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., & Willingham, D. T. (2013). Improving Students' Learning With Effective Learning Techniques. Psychological Science in the Public Interest, 14(1), 4–58. https://pubmed.ncbi.nlm.nih.gov/26173288/ — HIGH: practice testing, distributed practice. MODERATE: elaborative interrogation, self-explanation, interleaved practice. LOW: summarisation, highlighting/underlining, keyword mnemonic, imagery for text, rereading. 'Mind Mapping | Buzan (1970) — validated UCL': UNVERIFIED — I found no UCL validation study; mind-mapping evidence is modest and largely small-sample.

**Recommendation**

Cut to two, and make the retrieval step non-optional in both: (a) Cornell, where the app refuses to mark a note 'done' until the cue column is populated with questions and the student has self-tested on them; (b) one-idea-per-card atomic notes that export directly into FSRS. Delete mind mapping, sketchnoting, flow notes and outlining from the certified curriculum (offer them as optional tools, not competencies). Add a standing build rule — the 'Dunlosky gate' in Addition 1 — so no future feature enters the backlog without being classified against that taxonomy.

### LS-10 — Streaks, due-counts and a "90% faster" timer are a dashboard that rewards performance and can suppress learning

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.8 |

**What the artifact says**
> Home Dashboard: "Study streak + Anki due-card count"; Study Lab: "90%-faster study timer with/without AI mode"; Roadmap KPIs: "BARS daily use ≥ 5 days/week", "Anki daily use in 80%+ of pilot families".

**The problem**

Soderstrom & Bjork (2015) draw the distinction this product most needs: performance during training is an unreliable and often inverse index of durable learning, because the manipulations that make a session feel fluent and fast (massing, blocking, rereading, immediate feedback) typically reduce long-term retention, while the manipulations that feel effortful improve it. Every headline metric on the dashboard is a performance/engagement metric: streak length, cards cleared, minutes saved, days used. An anxious 12-year-old optimising a streak will choose the easiest deck and the shortest interval, which is exactly the behaviour that destroys spaced-retrieval benefit. The Phase 1–2 KPIs then lock this in as the definition of success, so the organisation will be steered by the same wrong signal.

**Evidence**

Soderstrom, N. C., & Bjork, R. A. (2015). Learning versus performance: An integrative review. Perspectives on Psychological Science, 10(2), 176–199 (UNVERIFIED at primary here; the learning/performance dissociation is nonetheless an established position in the literature and consistent with Bjork's desirable-difficulties programme). Dunlosky et al. (2013), as above, on why fluency-producing techniques rate LOW.

**Recommendation**

Rebuild the dashboard around delayed retention. Primary metric: FSRS-predicted retrievability of the student's exam-relevant cards at the exam date (the scheduler already computes this). Secondary: performance on a monthly delayed, mixed, cumulative check over material last seen ≥2 weeks ago. Remove the streak from the home screen entirely, or recast it as 'days you showed up,' explicitly decoupled from learning. Delete the '90% faster' timer. Change the Phase 1 KPI from 'BARS daily use ≥5 days/week' to a retention KPI; engagement can stay as a health metric, not a success metric.

### LS-11 — Agents emit continuous feedback to anxious children with no feedback-harm policy anywhere in the architecture

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> Tutor Agent output: "note feedback (gaps + improvements)"; trigger "confusion marker detected"; Home Dashboard "AI insight notification feed"; Study Lab "AI note feedback and knowledge gap finder"; Learning Path Agent "difficulty adjustment"; Failure-handling table lists hallucination, crisis and privacy — but no feedback-harm entry.

**The problem**

Feedback is not uniformly beneficial. Kluger & DeNisi's (1996) review of 131 studies and >12,000 participants found a mean effect of ~0.38 with roughly one third of effects negative; Wisniewski, Zierer & Hattie (2020), pooling 435 studies (k=994, N>61,000), found d = 0.48 with very large heterogeneity and showed that what matters is the information content — high-information task- and process-level feedback helps, while person/self-level feedback and praise are the weak-to-harmful kinds. A system whose agents continuously surface 'gaps', 'confusion markers' and 'insights' to a child screened into the product for test anxiety is a plausible-harm design: repeated deficit-framed feedback is a known driver of avoidance and of the cognitive-worry component the Test Anxiety Coach is supposed to reduce. Nothing in the 8-agent spec constrains level, valence, frequency, or timing relative to an anxiety flag.

**Evidence**

Wisniewski, B., Zierer, K., & Hattie, J. (2020). The Power of Feedback Revisited: A Meta-Analysis of Educational Feedback Research. Frontiers in Psychology, 10:3087. https://pmc.ncbi.nlm.nih.gov/articles/PMC6987456/ — d = 0.48; information content is the dominant moderator; larger effects for cognitive/motor than motivational/behavioural outcomes. Kluger, A. N., & DeNisi, A. (1996). Psychological Bulletin, 119(2), 254–284 — 131 studies, mean ~0.38, about one third of effects negative (as characterised in Wisniewski et al.).

**Recommendation**

Add a Feedback Policy layer between every agent and the learner, enforced in code, with four rules: (1) task- and process-level only — ban person-level statements ('you're a strong/weak reader') via an output classifier; (2) every deficit statement must be paired with a next action the student can take in under five minutes; (3) rate-limit — at most one improvement item per session, chosen by impact; (4) suppression — no corrective feedback inside an active anxiety-flag window; the Test Anxiety Coach holds the lock. Add 'feedback-induced disengagement' to the Failure Handling table with a measurable trip-wire (session abandonment rate after a feedback event) and review it weekly in the pilot.

### LS-12 — The parent-tutor model ignores the evidence that math-anxious parents who help with homework can make achievement worse

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.8 |

**What the artifact says**
> Parent diagnostic item: "Own personal test anxiety history (anxiety transmission research, Carey et al., 2017)"; MCPT Module 3 "Becoming a Master Homework Coach"; Gap Analysis: "73% of MCPS families lack both" content knowledge and confidence; business model premised on parent certification driving child outcomes.

**The problem**

The artifact collects the parent's anxiety history and then does nothing structural with it: every parent is routed to the same content-coaching certification. The relevant finding runs the other way. Maloney, Ramirez, Gunderson, Levine & Beilock (2015, Psychological Science) found that children of math-anxious parents learned less maths across the school year and ended with more maths anxiety — but only when those parents frequently helped with maths homework. Berkowitz et al. (2015, Science) showed that routing the same parents through a structured, app-mediated maths activity instead largely removed the transmission. So 'more parent homework help' is not monotonically good; for the high-anxiety subgroup it is the mechanism of harm, and that subgroup is disproportionately the one this product recruits ('was never taught HOW to study'). Separately, the '73% of MCPS families' figure is unsourced and the Carey et al. (2017) citation is a review of the maths-anxiety/performance direction-of-causation question, not of transmission.

**Evidence**

Maloney, E. A., Ramirez, G., Gunderson, E. A., Levine, S. C., & Beilock, S. L. (2015). Intergenerational effects of parents' math anxiety on children's math achievement and anxiety. Psychological Science, 26(9), 1480–1488 (UNVERIFIED at primary in this session; widely cited and consistent with Berkowitz et al.). Berkowitz, T., et al. (2015). Math at home adds up to achievement in school. Science, 350(6257), 196–198 (UNVERIFIED at primary). '73% of MCPS families': NOT FOUND — unverified; I would ask what instrument and sample produced it, or delete it.

**Recommendation**

Screen parent maths anxiety at intake with a short validated measure (sMARS short form or AMAS) and branch on the result. High-anxiety parents are routed to a coaching role with no maths content: protect the routine, the environment, sleep and affect; read the problem aloud; run the app-mediated activity together without evaluating correctness. Low-anxiety parents may take the content-tutoring track. Make this branch visible in MCPT Module 3 — it is also a genuinely novel, defensible differentiator that no competitor in the Gap Analysis table has. Replace or source the 73% figure.

### LS-13 — The test-anxiety design cites a meta-analysis of effects as if it were a meta-analysis of interventions, and ships three parallel modules instead of the combined protocol the evidence supports

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.8 |

**What the artifact says**
> Gap Analysis: "85% of test anxiety interventions validated only on white, middle-class, neurotypical populations (Zeidner, 1998; von der Embse et al., 2018)"; Next Action #5 and Phase 1: "3 test anxiety modules: CBT Thought Reframe + Mindfulness + Somatic Grounding"; "38% of middle schoolers experience debilitating test anxiety (Zeidner, 1998)".

**The problem**

Three issues. (1) The citation is wrong in kind: von der Embse et al. (2018, Journal of Affective Disorders) is a 30-year meta-analytic review of test anxiety's effects, predictors and correlates across 238 studies — it reports correlations with performance roughly in the r = −.13 to −.40 range. It is not a review of intervention samples and cannot support an '85% validated on white populations' claim; I could find no source for that 85%. (2) The intervention evidence that does exist (von der Embse, Barterian & Segool's systematic review of 2000–2010 studies with school-age students) finds very few studies with elementary and secondary students, finds promise for biofeedback, behaviour therapy, CBT, competency priming and mixed approaches, and explicitly notes that most of the intervention procedures examined have not been replicated. The defensible design implication is a combined cognitive-behavioural plus skills-based protocol, not three decoupled standalone modules a student may use in isolation — the skills half matters because some test anxiety is accurate appraisal of under-preparation (the artifact's own parent item 'ability to distinguish anxiety from genuine lack of preparation' notices this and then does not act on it). (3) The 38% prevalence figure is unverified and prevalence estimates swing widely with instrument and cut-point.

**Evidence**

von der Embse, N., Jester, D., Roy, D., & Post, J. (2018). Test anxiety effects, predictors, and correlates: A 30-year meta-analytic review. Journal of Affective Disorders, 227, 483–493. https://pubmed.ncbi.nlm.nih.gov/29156362/ — 238 studies; effects/correlates, not interventions. von der Embse, N., Barterian, J., & Segool, N. (2013). Test anxiety interventions for children and adolescents: A systematic review of treatment studies from 2000–2010. Psychology in the Schools, 50(1), 57–71 — few school-age studies; most procedures unreplicated. '85%' and '38%': NOT FOUND — both unverified; I would check Zeidner (1998) Test Anxiety: The State of the Art directly for any prevalence figure and report the instrument and cut-score alongside it.

**Recommendation**

Rebuild as one combined protocol with two interlocking strands delivered together — cognitive-behavioural (appraisal reframing, worry postponement, exposure to test-like conditions) and skills-based (retrieval practice and spaced review on the actual exam content), because reducing under-preparation is itself an anxiolytic. Keep somatic/breathing as an in-the-moment adjunct, not as a co-equal module. Fix the citations. Measure with a validated instrument at pre/post in the 10-family pilot (Children's Test Anxiety Scale or the FRIEDBEN; Spielberger's TAI is adult-normed — check age appropriateness before using it as the artifact plans).

### LS-14 — A 52-item/35–45-minute student diagnostic plus a 38-domain parent instrument, called "psychometrically validated" before it exists, is the project's biggest pilot-attrition risk

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> Tab header: "PhD-Level Diagnostic Assessments | Psychometrically validated | Student: 52 domains | Parent: 38 domains | Staff: 24 domains"; "Estimated: 35–45 min with scheduled breaks"; parent instrument "Estimated: 30–40 min"; Risk table already names "Pilot cohort dropout before data collection" as High; KPI "Diagnostic completion rate ≥ 80%".

**The problem**

Two defects. First, the subtitle asserts psychometric validation of an instrument that Next Action #1 says will be written in Weeks 1–2 — a validation claim for work that has not occurred, which the founder's own principles forbid. Having a school psychologist review items confers content-validity input, not validation; validation requires reliability estimation, factor structure, and criterion evidence in this population. Second, 35–45 minutes of 5-point Likert self-report is an adverse instrument design for the exact population recruited: adolescents with EF deficits, sustained-attention difficulty and literacy gaps. The predictable results are high attrition at the first gate, and systematic measurement error (straight-lining, acquiescence) concentrated in the students with the most severe profiles — i.e. the measurement will be worst precisely where it matters most. The artifact's own validity-check mitigation ('response time, pattern detection, contradiction flags') confirms the risk and then requires a *second* assessment from a student who already could not finish the first.

**Evidence**

INFERENCE from (a) the artifact's own stated population and risk register, (b) standard survey-methodology findings on satisficing and response-set bias under respondent burden, and (c) the absence of any psychometric study. No single citation establishes a 52-item threshold; the claim here is about the mismatch between instrument burden and the named population, not a specific effect size.

**Recommendation**

Ship a ≤15-item, ≤10-minute intake screener for the pilot, built where possible from existing validated short forms (AMAS for maths anxiety, a brief test-anxiety scale, a brief EF/organisation report, a reading-fluency probe) so you inherit their psychometrics instead of claiming your own. Defer the remaining 37 items to optional, in-context micro-assessments surfaced over the first six weeks, which also gives you repeated measures. Strike 'psychometrically validated' from every heading until a validation study with a reported n, alpha/omega and factor structure exists; replace with 'draft instrument, content review pending'. Report completion rate and time-to-complete as Phase 1 findings.

### LS-15 — "Desirable difficulties" and "productive struggle" are taught as competencies with no expertise-reversal guard — the wrong default for novices with limited working memory

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> Staff diagnostic Domain 1: "Desirable difficulties (Bjork, 1994) — designs productive struggle intentionally"; MCLSS Domain 1 lists "desirable difficulties" as a competency; Learning Path Agent tool "Adaptive difficulty engine"; Child Liberation: "Students design THEIR OWN study system".

**The problem**

Desirable difficulties are real, but they are difficulty manipulations applied to *retrieval and scheduling* for learners who already have the relevant schemas — not a licence for unguided problem-solving by novices. The worked-example effect and its boundary, the expertise-reversal effect (Sweller, Kalyuga and colleagues), establish that for novices, studying worked examples produces better learning at lower cost than solving equivalent problems, and that this advantage shrinks and then reverses as expertise grows. For a grade 6–8 learner with an IEP, low working-memory capacity and a knowledge gap, 'productive struggle' as a default is a recipe for cognitive overload, failure experience and — given the product's own thesis — anxiety. Certifying paraeducators and teachers in 'designing productive struggle' without the fading rule will push them toward the worse default with the most vulnerable students. Separately, there is a tension the artifact never resolves: 'students design their OWN study system' is maximal germane-plus-extraneous load for exactly the learners least equipped to carry it.

**Evidence**

Sweller, J., van Merriënboer, J. J. G., & Paas, F. (2019). Cognitive architecture and instructional design: 20 years later. Educational Psychology Review, 31, 261–292 — element interactivity as the organising construct; worked-example and expertise-reversal effects (UNVERIFIED at primary in this session; both effects are long-established and replicated). Kalyuga, S., Ayres, P., Chandler, P., & Sweller, J. (2003). The expertise reversal effect. Educational Psychologist, 38(1), 23–31. Related: IES and NCII guidance on explicit, systematic instruction for students with learning disabilities.

**Recommendation**

Replace 'productive struggle' with an explicit, codified fading sequence in both the product and the certifications: full worked example → completion problem (last step removed) → completion problem (last two steps removed) → independent problem, with advancement gated on demonstrated success, not elapsed time. Build this as the Learning Path Agent's actual difficulty policy rather than an unspecified 'adaptive difficulty engine'. Reserve desirable difficulties for scheduling and retrieval decisions (spacing, interleaving, delayed feedback) where the evidence actually sits. Keep student agency, but scope it to goals, topics, timing and reward structure — not to the design of the instructional sequence itself.

### LS-16 — "Confidence scoring on ALL outputs; human review queue for score < 0.85" is a safety control that does not work as specified

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `EXPERT-OPINION` |
| **Lens confidence** | 0.8 |

**What the artifact says**
> Risk table and Failure Handling table (identical text, twice): "AI hallucination in educational content | Critical | Confidence scoring on ALL outputs; human expert review queue for score < 0.85; citations required; zero-tolerance for unverified academic claims".

**The problem**

This is the named mitigation for a Critical risk, and it rests on LLM self-reported confidence, which is not calibrated — models are routinely confidently wrong, and the correlation between a self-assessed score and factual accuracy is weak and distribution-shift-sensitive. A 0.85 threshold on an uncalibrated score gives the appearance of a gate with none of the function, and it will let through precisely the fluent-and-wrong content most likely to be believed by a 12-year-old and a parent who, by the artifact's own account, cannot evaluate it. 'Citations required' without retrieval grounding also invites fabricated citations — a risk this very document demonstrates (see LS-04, LS-05, LS-06).

**Evidence**

EXPERT-OPINION / INFERENCE. The miscalibration of LLM verbalised confidence is widely documented in the evaluation literature, but I did not verify a specific citation in this session; I would check the recent calibration literature (e.g. work on verbalised vs. token-level confidence and selective prediction) before writing this into a safety spec.

**Recommendation**

Replace with controls that have mechanism: (1) retrieval-grounded generation over a curated, versioned corpus of MCPS curriculum and vetted sources, with every factual claim required to resolve to a retrieved span — not a model-asserted citation; (2) a claim-type blocklist that refuses to state effect sizes, prevalence figures, statute sections or diagnostic conclusions at all; (3) a fixed-rate human audit (e.g. 5% of outputs, 100% of any output touching IEP content or crisis language) rather than a threshold-triggered queue; (4) log every ungrounded generation and review the rate weekly. If a calibrated confidence signal is wanted, derive it from retrieval coverage, not from the model's self-report.

### LS-17 — A product whose thesis is that testing harms these students gates its own credentials behind a 3-hour proctored exam

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.7 |

**What the artifact says**
> MCST "Part 1: Knowledge Assessment — 60-item multiple choice... 80% passing"; MMEC "Part 1: Comprehensive Proctored Exam — 3 hours | 100 items | Passing: 75%"; alongside Course Design: "Portfolio-based demonstrations over compliance tests wherever possible".

**The problem**

The artifact states a design principle and then violates it in its own assessment architecture. For the student track especially, gating a credential behind a 60-item high-stakes multiple-choice exam reproduces the exact stimulus the product exists to defuse, for children recruited because that stimulus is debilitating for them. It also conflates two uses of testing that the learning-science literature keeps apart: low-stakes retrieval practice (a learning event, HIGH utility in Dunlosky et al.) and high-stakes summative assessment (an evaluation event, the anxiety trigger). The product is well designed to do the first and has imported the second by default.

**Evidence**

INFERENCE from the artifact's own stated principles and population, plus Dunlosky et al. (2013) on practice testing as a learning technique and the test-anxiety literature on evaluative threat (von der Embse et al., 2018). No single study establishes that portfolio assessment outperforms exams for this population — that is an open question (see open_questions).

**Recommendation**

For the student (MCST) track, replace Part 1 with cumulative low-stakes retrieval distributed across the 12 modules — the student's accumulated retrieval record *is* the knowledge evidence, with no single gating event — and keep Parts 2–4 (case application, observed teaching demonstration, portfolio) as the credential. Keep the proctored format for the adult MMEC track if a university partner requires it for graduate credit, but say explicitly in the curriculum why the student and adult tracks differ. That contrast is itself a teachable artefact for the MMEC capstone.

### LS-18 — "Study 90% faster — with and without AI" is an unfalsifiable marketing claim embedded as a certification competency

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> "90% faster study with AND without AI" (Solution/For Students); MCST "Module 9: Study 90% Faster — With and Without AI"; MCLSS Domain 4 "90% faster study facilitation"; Study Lab "90%-faster study timer with/without AI mode".

**The problem**

The claim has no referent: 90% faster than what baseline, to what criterion, on what material, measured how? It has no source. It is simultaneously a marketing headline, a product feature, a paraeducator competency and a student certification module, so it will be taught as fact by certified adults to children and their parents. This is the clearest single violation of the founder's stated 'evidence before claims' and 'no claims of validation that has not occurred', and it is the kind of claim that attracts consumer-protection scrutiny when sold to families at $399/year.

**Evidence**

NOT FOUND — no source; unverified. INFERENCE from the absence of any defined baseline, criterion or measurement procedure in the artifact.

**Recommendation**

Delete the number from all four locations before any external document is produced. Replace the module with 'Studying in Less Time: What Actually Saves Time' and teach the mechanism honestly — spaced retrieval reduces total time-to-criterion because it reduces relearning, which is a real and measurable effect. Then measure it in the pilot: minutes-to-criterion on a fixed item set, baseline vs. after four weeks, per student. If the result is 25%, publish 25%. A real number from ten families is worth more to MCPS than a fabricated one.

### LS-19 — "No comparable app exists" overstates the competitive claim because the comparison axis is feature-bundling, not efficacy

| | |
|---|---|
| **Severity** | `LOW` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.7 |

**What the artifact says**
> "🏆 Market Conclusion: No Comparable App Exists... MindUnlock Academy is the first of its kind"; "8 Innovation Pillars — Present in Zero Existing Programs"; app scores ("Anki 45%", "Headspace 20%"...).

**The problem**

The gap analysis scores competitors on whether they contain MindUnlock's feature list, which guarantees the conclusion. It does not compare on the axis a district or a funder cares about — demonstrated learning or wellbeing outcomes — where several listed competitors have published evidence and MindUnlock has none. It also omits the actual near-neighbours a reviewer will name: school-delivered CBT/study-skills test-anxiety programmes, HOPS as a packaged organisational-skills intervention with RCT evidence, Check-In/Check-Out and Daily Report Card systems already running in many MCPS schools, structured-literacy intervention programmes, and district ethnic-studies curricula. Claiming first-of-its-kind against a strawman set weakens an otherwise genuine differentiation claim (the family-cohort certification model does appear unusual).

**Evidence**

INFERENCE from the artifact's own scoring method. Comparators with published evidence include Langberg's HOPS (RCT; see LS-20/Addition 13) and school-based Daily Report Card interventions. 'TAM: 6.4M students with IEPs, 74M K-12 parents, 1.3M paraeducators' — figures UNVERIFIED; the IDEA Part B child count and NCES/BLS paraprofessional counts are the sources I would check.

**Recommendation**

Add an efficacy column to the competitor table ('what outcome evidence exists for this product, and of what design') and populate it honestly, including an empty cell for MindUnlock. Add the five omitted near-neighbours above. Narrow the first-of-its-kind claim to the specific combination you can defend — simultaneous family-cohort certification with a culturally sustaining strand — and drop it elsewhere. Source or remove the TAM figures.


---

## What is missing and should be added

### 1. The Dunlosky utility gate and a published negative-evidence registry   `ESTABLISHED`

**Why it matters.** The artifact has no filter that would have caught speed reading, VARK, or four low-utility note formats before they became certification modules. A single standing build rule catches all of them and every future one, at zero recurring cost. Publishing the negative list is also a trust asset with MCPS: most ed-tech vendors cannot say what they refuse to ship.

**What to build.** (a) A one-page build rule in the repo: no feature enters the backlog without a classification against Dunlosky et al.'s ten techniques (HIGH: practice testing, distributed practice; MODERATE: elaborative interrogation, self-explanation, interleaved practice; LOW: summarisation, highlighting/underlining, keyword mnemonic, imagery for text, rereading) plus a named primary source, population, and boundary condition. LOW-utility features require an explicit written override. (b) A public 'What We Will Never Ship' page: learning-style matching, working-memory/brain-training games, speed reading, neuro-myth content (left/right brain, VAK), unvalidated diagnostic labels, and any claim of validation that has not occurred. Each with its one-line citation. (c) For a 12-year-old with an IEP, the user-facing consequence is simple: every study activity in the app ends in retrieval, and nothing in the app rewards highlighting.

**Evidence.** Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., & Willingham, D. T. (2013). Psychological Science in the Public Interest, 14(1), 4–58 (PMID 26173288). Melby-Lervåg, M., Redick, T. S., & Hulme, C. (2016). Perspectives on Psychological Science, 11(4), 512–534 — 87 publications, 145 comparisons, no reliable far transfer from working-memory training vs. treated controls. Pashler et al. (2008) PSPI 9(3) and Rogowsky et al. (2015) JEP 107(1) on learning styles. Rayner et al. (2016) PSPI 17(1) on speed reading.

### 2. A generative-learning event library: pretesting, generation, self-explanation, elaborative interrogation   `ESTABLISHED`

**Why it matters.** The artifact's instructional events are overwhelmingly receptive (read the module, watch the video, take notes, then quiz). The largest cheap wins in the last fifteen years of learning science are generative events placed *before* and *during* exposure, not after. Self-explanation alone carries a pooled g = 0.55 across 69 effect sizes — larger than almost anything else on the artifact's feature list — and costs a text prompt.

**What to build.** Four prompt types, implemented as reusable components the Learning Path Agent can insert anywhere: (a) PRETEST / 'Guess First' — before any new concept, the learner answers 2–3 questions they cannot yet know, gets immediate corrective feedback, and the app explicitly tells them wrong guesses help (errorful generation). (b) GENERATE — the app never shows a definition the student could produce; it asks first. (c) SELF-EXPLAIN — after each worked example step: 'Why does that step work?' with a scaffolded sentence starter for students with written-expression difficulty, and an audio option. (d) ELABORATIVE INTERROGATION — 'Why would that be true?' attached to every declarative fact in a card deck. For a grade 6–8 learner with an IEP: these are 10–20-second interactions, voice-input enabled, with no spelling penalty.

**Evidence.** Bisra, K., Liu, Q., Nesbit, J. C., Salimi, F., & Winne, P. H. (2018). Inducing Self-Explanation: a Meta-Analysis. Educational Psychology Review, 30(3), 703–725 — overall weighted g = 0.55, 69 effect sizes from 64 reports, 20 moderators coded (https://link.springer.com/article/10.1007/s10648-018-9434-x). Dunlosky et al. (2013) rate self-explanation and elaborative interrogation MODERATE (promising, less broadly tested). Pretesting/errorful generation: Richland, Kornell & Kao (2009, JEP:Applied); Potts & Shanks (2014, JEP:General); Carpenter & Toftness (2017) — UNVERIFIED at primary here; the benefit is replicated but moderated by feedback presence, which the design must therefore guarantee.

### 3. A worked-example → completion → independent fading engine, with an expertise-reversal guard (4C/ID as the curriculum architecture)   `ESTABLISHED`

**Why it matters.** This is the direct counterweight to the artifact's 'productive struggle' and 'desirable difficulties' framing, and it is the single most important instructional-design change for novice ND learners. It also replaces the artifact's flat module list with a curriculum architecture that is actually designed for complex-skill acquisition rather than topic coverage.

**What to build.** (a) Every procedural skill ships as a 4-step ladder: full worked example (student studies and self-explains) → completion problem with the final step removed → completion problem with the final two steps removed → independent problem. Advancement is gated on two consecutive successes, never on elapsed time. (b) A reversal guard: once a student passes the gate twice, the engine stops showing worked examples for that skill, because continuing is redundant and harmful. (c) Re-architect the curriculum as 4C/ID: whole authentic task classes of increasing complexity (van Merriënboer), supportive information for the non-routine parts, just-in-time procedural information for the routine parts, and part-task practice only where automation is required (e.g. maths facts, decoding). For a 12-year-old with an IEP: this means they never face a blank page on a new skill, and they are never stuck re-reading an example they have already mastered.

**Evidence.** Sweller, J., van Merriënboer, J. J. G., & Paas, F. (2019). Cognitive architecture and instructional design: 20 years later. Educational Psychology Review, 31, 261–292. Kalyuga, S., Ayres, P., Chandler, P., & Sweller, J. (2003). The expertise reversal effect. Educational Psychologist, 38(1), 23–31. van Merriënboer, J. J. G., & Kirschner, P. A., Ten Steps to Complex Learning (4C/ID). The worked-example and expertise-reversal effects are long-replicated; I did not verify specific effect sizes at primary in this session.

### 4. Retrieval practice at classroom scale — and the anxiety finding, which is this product's single most load-bearing fact   `EMERGING`

**Why it matters.** The artifact treats quizzing as an academic tool and anxiety as a separate emotional module. The field-research finding that low-stakes classroom retrieval is associated with *reduced* reported test anxiety — because repeated, consequence-free exposure to the retrieval format defuses it — unifies the product's two halves. If it holds, the anxiety intervention and the learning intervention are the same intervention, which is a much stronger pitch to MCPS than two bolted-together ones.

**What to build.** (a) Every study block ends with 3–5 low-stakes retrieval items drawn from material last seen ≥2 days ago, with no score shown to anyone and no effect on any streak or badge. (b) An explicit onboarding message to students and parents: 'quizzing here is practice, not judgement — it is the thing that makes tests feel smaller.' (c) Pre-exposure to format: the week before a real MCPS assessment, retrieval items are rendered in the actual format the student will face (bubble sheet, short response, oral). (d) Instrument it in the pilot: state anxiety rating before and after each retrieval block, so you can test the claim rather than assert it.

**Evidence.** Agarwal, P. K., Bain, P. M., & Chaffee, R. (2012/2021) classroom field studies, and Agarwal, Bain & Chaffee's Powerful Teaching; Agarwal et al. have reported that a majority of middle-school students surveyed said frequent low-stakes quizzing reduced rather than increased their anxiety about unit tests — FIGURES UNVERIFIED in this session; I would retrieve Agarwal, Bain & Chaffee (2012, Educational Psychology Review) and Agarwal, D'Antonio, Roediger, McDermott & McDaniel (2014, J. Applied Research in Memory and Cognition) to confirm the exact proportions and the measure used before putting any number in front of a district. The retrieval-practice benefit itself is ESTABLISHED (Dunlosky et al. 2013, HIGH utility); the anxiety-reduction result is EMERGING.

### 5. Rebuild progress reporting around learning, not performance (Soderstrom & Bjork)   `ESTABLISHED`

**Why it matters.** A dashboard that rewards fluency will teach a 12-year-old to seek fluency, and fluency is the signal that most reliably misleads. This is the cheapest high-leverage fix in the whole product: it is a metric change, not a feature build, and it protects every other evidence-based component from being gamed into uselessness.

**What to build.** (a) Primary learner-facing metric: predicted retention at the exam date, computed from the FSRS state of exam-relevant cards, displayed as 'how much of this you'll still have on test day.' (b) A monthly 'Delayed Check' — mixed, cumulative, on material last studied ≥2 weeks ago — reported as the real progress number. (c) Remove streaks and due-counts from the home screen; if retained anywhere, label them 'showing up' and decouple from learning claims. (d) Teach the distinction explicitly in MCST Module 2 and MCPT Module 1: 'feeling fluent is not the same as having learned' — this is the single most useful thing a parent who was never taught how to study can be told, and it directly corrects the rereading-and-highlighting habit the parent diagnostic already probes (item: 'knowledge of study techniques beyond re-reading and highlighting').

**Evidence.** Soderstrom, N. C., & Bjork, R. A. (2015). Learning versus performance: An integrative review. Perspectives on Psychological Science, 10(2), 176–199 — UNVERIFIED at primary in this session; the learning/performance dissociation is an established position supported by the desirable-difficulties literature and by Dunlosky et al.'s LOW rating of fluency-producing techniques.

### 6. Spacing schedule science beyond "use Anki": FSRS with an exam-date-anchored retention target   `ESTABLISHED`

**Why it matters.** The artifact's spacing story is a brand name and a nonexistent algorithm. The actual science says something the product can use as a differentiator: when the retention interval is a known date (and in a school, it almost always is), the optimal schedule is computable, and it is different from the default. No consumer study app does this.

**What to build.** (a) FSRS as the scheduler, with per-learner desired retention (default 0.90) exposed to the IEP engine so pacing accommodations change a principled parameter rather than a fudge factor. (b) EXAM MODE: the student enters the MCPS assessment date; the scheduler optimises review placement against that date rather than against an open-ended horizon, and the app states plainly how many minutes per day that costs. (c) A visible 'why now' explanation on each review ('you're about 7 days from forgetting this'), which doubles as metacognitive instruction. (d) Teach the ridgeline finding in MCST Module 5 in plain language: the right gap grows as the test gets further away, but shrinks as a proportion of it — the concrete rule for a 12-year-old being 'if your test is three weeks away, review about every 3–4 days,' derived rather than asserted.

**Evidence.** Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., & Pashler, H. (2008). Spacing Effects in Learning: A Temporal Ridgeline of Optimal Retention. Psychological Science, 19(11), 1095–1102 — >1,350 participants; optimal gap ≈20% of the test delay for delays of a few weeks, falling to ≈5% at one year (https://files.eric.ed.gov/fulltext/ED505660.pdf). Cepeda et al. (2006), Psychological Bulletin 132(3) — the distributed-practice meta-analysis. Settles, B., & Meeder, B. (2016). A trainable spaced repetition model for language learning. ACL — half-life regression, the direct ancestor of modern data-driven schedulers (UNVERIFIED at primary here). Anki Manual FAQ on FSRS vs. SM-2 vs. proprietary SM-17.

### 7. A transfer architecture — because standalone study-skills programmes historically do not transfer   `EMERGING`

**Why it matters.** This is the existential risk to the entire certification concept and the artifact does not mention it once. The modal finding for generic study-skills courses is that students improve on the course's own measures and change little in their actual classes. The programmes that do transfer share identifiable features, and those features are design decisions the founder can make now, cheaply, before building twelve modules.

**What to build.** (a) Discipline-embedding: every strategy is taught and practised on the student's actual current MCPS assignment — never on generic exemplar content. The app pulls this week's science unit; the student self-explains *that*. (b) Duration and distribution: strategies recur across the whole term rather than being covered once in a module. (c) Conditional knowledge: explicitly teach *when* each strategy applies and when it does not (near vs. far transfer, in Barnett & Ceci's terms: same vs. different knowledge domain, physical context, functional context, social context, modality). (d) Measure transfer directly in the pilot: an unprompted transfer probe in a subject the programme never used. (e) Delete any 'study skills' module whose practice material is not real coursework.

**Evidence.** Barnett, S. M., & Ceci, S. J. (2002). When and where do we apply what we learn? A taxonomy for far transfer. Psychological Bulletin, 128(4), 612–637 — the six-dimension taxonomy (UNVERIFIED at primary here). Hattie, Biggs & Purdie (1996, Review of Educational Research) on study-skills interventions: effects are largest for structured, context-embedded, metacognitive programmes and weakest for generic standalone ones (UNVERIFIED at primary). Donker, de Boer, Kostons, Dignath van Ewijk & van der Werf (2014, Educational Research Review) on learning-strategy instruction in subject domains.

### 8. A Cognitive Load Theory UI rule-set (2019 update), written as enforceable interface constraints   `ESTABLISHED`

**Why it matters.** The artifact invokes cognitive load three times as a slogan ('BARS micro-chunking reduces extraneous load') but derives no interface rules from it. CLT's modern formulation around element interactivity converts directly into a short list of concrete, testable UI constraints — which is exactly what a React Native team needs and exactly what protects a working-memory-limited learner.

**What to build.** Nine binding rules in the design system, each with a lint check or design-review gate: (1) ELEMENT INTERACTIVITY — cap simultaneously interacting elements per screen for novices; sequence before you parallelise. (2) SPLIT-ATTENTION — labels inside diagrams, never in a separate legend; worked-example explanation adjacent to the step, never below the fold. (3) REDUNDANCY — never narrate on-screen text verbatim; TTS replaces the text channel, it does not duplicate it (this is the rule the artifact's 'read-aloud on all content' currently violates). (4) MODALITY — pair transient narration with visuals, not with text. (5) TRANSIENT INFORMATION — any audio or animation longer than ~30 seconds must be pausable, scrubbable and transcript-backed; auto-advancing content is banned. (6) GOAL-FREE — early practice asks 'find everything you can' rather than 'find x'. (7) One decision per screen in the scheduler. (8) No more than one notification per study block (this also serves the feedback policy in LS-11). (9) Progressive disclosure defaults ON, parent-adjustable. Each rule gets a line in the paraeducator certification so adults can apply it to paper materials too.

**Evidence.** Sweller, J., van Merriënboer, J. J. G., & Paas, F. (2019). Cognitive architecture and instructional design: 20 years later. Educational Psychology Review, 31, 261–292 — element interactivity as the unifying construct; split-attention, redundancy, modality, transient-information, goal-free and worked-example effects (UNVERIFIED at primary in this session; these effects are long-established and replicated).

### 9. A self-regulated learning cycle as the core app loop (Zimmerman / Winne & Hadwin / Panadero)   `ESTABLISHED`

**Why it matters.** The artifact's loop is 'schedule → study → quiz', with metacognition appearing as a diagnostic item and a Sankofa journal rather than as the operating structure. SRL models give a validated three-phase cycle that this app is unusually well placed to instrument — and SRL instruction is one of the better-evidenced levers for exactly this age band and for students with learning difficulties.

**What to build.** Make the session loop the SRL cycle, visibly: (a) FORETHOUGHT (60 seconds) — set a specific goal, predict how long it will take, predict how well it will go, choose a strategy from a short menu. (b) PERFORMANCE — strategy applied, with a single self-monitoring prompt mid-session. (c) SELF-REFLECTION (60 seconds) — compare predicted vs. actual time and accuracy, attribute the gap to strategy rather than ability, choose one change for next time. The prediction/outcome discrepancy is the metacognitive teaching mechanism and it is free data. Rename the Sankofa journal as the reflection phase rather than a separate artefact — the cultural frame and the cognitive frame are describing the same act, which is a genuinely good insight already latent in the document. Winne & Hadwin's COPES model gives the field names for the telemetry (conditions, operations, products, evaluations, standards) so the agent memory schema has principled structure instead of ad-hoc JSON.

**Evidence.** Zimmerman, B. J. (2000, 2002) cyclical phases model; Winne, P. H., & Hadwin, A. F. (1998) COPES model; Panadero, E. (2017). A Review of Self-regulated Learning: Six Models and Four Directions for Research. Frontiers in Psychology, 8:422 — the standard comparative review (UNVERIFIED at primary in this session). Dignath & Büttner (2008, Metacognition and Learning) meta-analysis of SRL training in primary and secondary school reports positive effects, with design features mattering (UNVERIFIED).

### 10. Self-Determination Theory + the Self-Determined Learning Model of Instruction: the evidence-based, IDEA-aligned version of "child liberation"   `EMERGING`

**Why it matters.** The founder's liberation instinct is right and the citations are wrong. Holt, Gray and Freire are arguments, not evidence; SDT is a large empirical programme, and SDLMI is a manualised, IDEA-aligned instructional model with intervention evidence specifically in students with disabilities — including randomised and quasi-experimental work on self-determination and goal attainment. This substitution loses nothing the founder cares about and gains everything a district special-education office needs to say yes.

**What to build.** (a) Audit every agent's language against SDT's three needs: autonomy (choice and rationale, never pressure language — ban 'you must', 'you should have'), competence (optimally challenging tasks plus informational feedback), relatedness (cohort and family presence). Ship an autonomy-supportive phrasing library the Parent Coach Agent uses verbatim. (b) Implement SDLMI as the actual student goal module: the student answers the three phases' student questions — 'What do I want to learn? What do I know now? What must change? What can I do?' then 'What is my plan? What barriers? What support? When will I act?' then 'What action did I take? What barriers were removed? What do I know now? Do I know what I want to know?' (c) STUDENT-LED IEP: scaffold the learner to present one goal and one accommodation request at their own IEP meeting, with a rehearsal mode and a one-page script. For a 12-year-old with an IEP this is the most powerful, lowest-cost liberation feature in the product — it is legally supported, it is what IDEA transition planning is heading toward anyway, and no competitor in the Gap Analysis table offers it.

**Evidence.** Ryan, R. M., & Deci, E. L. (2000, 2017) Self-Determination Theory — autonomy, competence, relatedness; large meta-analytic literature on autonomy-supportive teaching. Shogren, K. A., Wehmeyer, M. L., Palmer, S. B., et al. — Self-Determined Learning Model of Instruction; cluster-randomised and quasi-experimental trials showing effects on self-determination and goal attainment for students with disabilities (UNVERIFIED at primary in this session; I would retrieve Shogren et al. (2012, Exceptional Children) and Wehmeyer et al. (2012) for exact designs and effect sizes). IDEA (20 U.S.C. §1414(d)) requires that the child be invited to IEP team meetings where transition services are considered — PRIMARY TEXT, cite the statute directly rather than paraphrasing.

### 11. The motivation interventions that actually replicate: utility-value writing and purpose-for-learning   `EMERGING`

**Why it matters.** The artifact bets its motivational architecture on growth mindset (d = 0.08) and an invented 40% figure. The brief social-psychological interventions with the better replication record at this age are utility-value and purpose-for-learning, and they are cheaper to build than anything else in the product: they are writing prompts.

**What to build.** (a) UTILITY-VALUE: three times per term, after a unit, the student writes 150 words on how this specific content connects to something they or someone they care about actually does. Critically, it must be the student generating the connection, not the app asserting relevance — the generation is the mechanism. Voice-dictation and sentence starters for students with written-expression goals. (b) PURPOSE-FOR-LEARNING: once per term, a short reflective write on a self-transcendent reason to learn — contributing to family, community, or the world. This is where the artifact's Ubuntu and ancestral content belongs, and it is a far better-evidenced home for it than a pre-test ritual. (c) PARENT VARIANT: Harackiewicz's work shows a parent-directed utility-value intervention (a brochure/website prompting parents to discuss course usefulness) affected course-taking — a natural fit for the family-cohort model and a two-page build. (d) Deliver each ONCE, with fidelity, and measure; do not saturate.

**Evidence.** Hulleman, C. S., & Harackiewicz, J. M. (2009). Promoting interest and performance in high school science classes. Science, 326(5958), 1410–1412. Harackiewicz, J. M., Rozek, C. S., Hulleman, C. S., & Hyde, J. S. (2012). Helping parents to motivate adolescents in mathematics and science. Psychological Science, 23(8), 899–906. Yeager, D. S., et al. (2014). Boring but important: A self-transcendent purpose for learning. Journal of Personality and Social Psychology, 107(4), 559–580. ALL UNVERIFIED at primary in this session — I would retrieve each before quoting an effect size, and would also check the recent replication and heterogeneity literature on utility-value, which is mixed in some settings.

### 12. A belonging/affirmation strand built to protocol — with the heterogeneity and failed-replication record stated plainly   `EMERGING`

**Why it matters.** The artifact wants identity affirmation and has placed it in the worst possible slot (minutes before a test, every test). The wise-intervention literature is precise about delivery, and equally precise that effects are heterogeneous and context-dependent. Getting the protocol right converts a liability into a credible, publishable component.

**What to build.** (a) VALUES AFFIRMATION per Cohen et al.: 10–15 minute in-class-style writing where the student selects and writes about values that matter to them, delivered early in a term and repeated a small number of times — never immediately pre-test, never framed as remediation, never explicitly about race. (b) BELONGING (Walton & Cohen): a brief reading of near-peer narratives showing that belonging worries are common, improve with time, and are not evidence of not belonging, followed by the student writing their own version to pass on to next year's cohort (the saying-is-believing step is the mechanism). (c) Write the honest caveat into the paraeducator and teacher certifications: these effects are real in some contexts, null in others, depend on a psychologically hospitable environment, and have failed to replicate at scale in several settings — adults must be taught not to expect magic and not to blame the child when it does not appear. That honesty is itself a differentiator against every PD vendor in the market.

**Evidence.** Walton, G. M., & Cohen, G. L. (2011). A brief social-belonging intervention improves academic and health outcomes of minority students. Science, 331(6023), 1447–1451. Cohen, G. L., Garcia, J., Apfel, N., & Master, A. (2006). Science, 313, 1307–1310; Cohen et al. (2009). Science, 324, 400–403. Walton, G. M., & Wilson, T. D. (2018). Wise interventions. Psychological Review, 125(5), 617–655. Heterogeneity and replication limits: Walton & Yeager and subsequent large-scale trials report context-dependence and some nulls. ALL UNVERIFIED at primary in this session — retrieve before citing any effect size.

### 13. The ADHD academic package that actually has randomised evidence: HOPS, the Daily Report Card, and behavioural parent training   `ESTABLISHED`

**Why it matters.** This is the highest-evidence, lowest-cost thing a 10-family pilot could ship, and the artifact currently contains none of it by name. Organisational-skills training in middle school has direct RCT support with large parent-rated effects in exactly the grade band targeted; the Daily Report Card is a one-page, free, school-home feedback loop with a substantial behavioural evidence base; behavioural parent training is a first-line evidence-based treatment. Meanwhile 'executive function training' games — which the product's agent architecture could easily drift toward — do not transfer.

**What to build.** (a) HOPS as a digital routine: a materials-organisation check (binder/backpack/digital files) with a simple scored checklist, a planner-recording routine for every assignment, and a brief weekly coaching contact — this is a concrete, manualised replacement for the undefined 'BARS'. (b) DAILY REPORT CARD: 3–5 individually targeted, observable, teacher-rated daily behaviours (e.g. 'recorded all homework in planner'), a home reward tied to the rating, a one-tap teacher interface. This is the single feature most likely to produce a visible effect inside eight weeks with ten families, and it integrates with MCPS staff rather than around them. (c) BEHAVIOURAL PARENT TRAINING content in the MCPT track — antecedent management, effective commands, planned ignoring, contingency contracts — replacing the undefined 'homework conflict resolution system'. (d) An explicit prohibition: no working-memory or EF 'brain training' game, ever (see Addition 1).

**Evidence.** Langberg, J. M., Epstein, J. N., Becker, S. P., Girio-Herrera, E., & Vaughn, A. J. (2012). Evaluation of the HOPS intervention for middle school students with ADHD as implemented by school mental health providers. School Psychology Review, 41(3) — n = 47, grades 6–8, randomised vs. waitlist; parent-rated effects d = 0.88 (organised actions), 1.05 (planning), 0.85 (homework completion), 0.63 (materials management); homework problems d = .83 (vs. d = .71 in the 2008 research-staff trial); teacher-rated differences non-significant (https://pmc.ncbi.nlm.nih.gov/articles/PMC4209597/). A cluster-randomised conceptual replication is in progress, powered for d = 0.50. Melby-Lervåg, Redick & Hulme (2016), Perspectives on Psychological Science 11(4), 512–534 — no far transfer from working-memory training. Daily Report Card and behavioural parent training evidence: see Evans, Owens & Bunford (2014/2018) evidence-based update for ADHD in J. Clinical Child & Adolescent Psychology — UNVERIFIED at primary here.

### 14. Adolescent structured literacy — morphology, fluency, vocabulary depth, knowledge — replacing the speed-reading module   `ESTABLISHED`

**Why it matters.** The artifact correctly identifies that students with literacy deficits cannot access strategies built for fluent readers, then prescribes speed reading, which is the strategy most dependent on fluency. The adolescent-literacy evidence base specifies what actually helps a struggling grade 6–8 reader, and almost all of it is buildable as low-cost app content.

**What to build.** (a) MORPHOLOGY as the spine: explicit instruction in high-utility Latin/Greek roots, prefixes and suffixes, with a 'word surgery' routine the student applies to real vocabulary from their current MCPS science and social-studies units. This is the highest-leverage decoding-plus-vocabulary lever at this age because academic words are morphologically transparent. (b) FLUENCY for students below benchmark: repeated reading of short, content-relevant passages with a model, a timed second read, and a self-graphed WPM-with-accuracy chart (note: this is the ONE legitimate use of a reading-rate metric in the product — it is fluency building on a fixed easy passage, not speed reading on novel text). (c) VOCABULARY DEPTH: a small number of words taught deeply with multiple exposures across contexts, not long lists. (d) KNOWLEDGE-BUILDING: sequence content so that comprehension is supported by accumulated topic knowledge, since knowledge is the dominant driver of comprehension at this age. (e) ACADEMIC LANGUAGE: keep the artifact's CALP framing but operationalise it as sentence-level academic syntax practice (because/although/therefore frames), which is concrete and ND-friendly. (f) Build a decision rule: screen fluency at intake; students below benchmark get the fluency strand before anything that assumes independent reading.

**Evidence.** IES Practice Guide: Improving Adolescent Literacy: Effective Classroom and Intervention Practices (Kamil et al., 2008, NCEE 2008-4027) — recommends explicit vocabulary instruction, direct comprehension-strategy instruction, discussion, motivation/engagement, and intensive individualised intervention for struggling readers; I did not re-verify the recommendation tiers in this session. Scarborough's Reading Rope (2001) — correctly cited by the artifact. Cummins (1979) on CALP — correctly cited in spirit; the '5–7 years' figure is the commonly cited estimate and is UNVERIFIED here. Morphological-awareness intervention meta-analyses (e.g. Goodwin & Ahn, 2010/2013) report modest positive effects, larger for struggling readers — UNVERIFIED at primary.

### 15. Test anxiety and maths anxiety built on the intervention evidence, including expressive writing with its replication caveat   `EMERGING`

**Why it matters.** The artifact's three decoupled anxiety modules do not match what the intervention literature supports, and it omits maths anxiety entirely despite its own diagnostic item 1.6 ('subject-specific anxiety: math vs. ELA...'). Maths anxiety has its own mechanism (working-memory consumption by worry) and its own cheap, specific interventions.

**What to build.** (a) ONE combined protocol, delivered together, not three modules: cognitive-behavioural (appraisal reframing, worry postponement, graded exposure to test-like conditions) interlocked with skills-based (spaced retrieval on the actual exam content) — because under-preparation is a legitimate source of anxiety and treating only the affect leaves it intact. (b) EXPRESSIVE WRITING: a 10-minute write about test worries immediately before a high-stakes test. Ramirez & Beilock (2011, Science) reported benefits concentrated in highly test-anxious students; the replication record is mixed, with some failures to replicate, so ship it as an A/B-tested option in the pilot rather than a certainty, and say so in the certification materials. (c) MATHS ANXIETY: screen with AMAS; teach the working-memory-consumption mechanism explicitly (it is reassuring and it is true); protect maths practice from timed, public, speed-based formats, which are the known amplifiers. (d) Route high-maths-anxiety parents away from content tutoring (see finding LS-12). (e) Measure with an age-appropriate validated instrument; verify Spielberger's TAI norms cover grade 6–8 before adopting it as the artifact plans.

**Evidence.** von der Embse, N., Barterian, J., & Segool, N. (2013). Test anxiety interventions for children and adolescents: A systematic review of treatment studies from 2000–2010. Psychology in the Schools, 50(1) — few school-age studies; CBT, behaviour therapy, biofeedback and mixed approaches show promise; most procedures unreplicated. von der Embse et al. (2018). Journal of Affective Disorders, 227, 483–493 — 238 studies; test anxiety negatively related to performance, correlations roughly r = −.13 to −.40 (https://pubmed.ncbi.nlm.nih.gov/29156362/). Ramirez, G., & Beilock, S. L. (2011). Writing about testing worries boosts exam performance in the classroom. Science, 331(6014), 211–213 — replication record MIXED and UNVERIFIED here; retrieve the subsequent replication attempts before building it as a core feature. Ashcraft & Krause (2007) and Maloney & Beilock (2012) on the working-memory mechanism of maths anxiety — UNVERIFIED at primary.

### 16. A global instructional repertoire: variation theory/bianshi, Japanese structured problem-solving, Singapore CPA, and memorisation-with-understanding   `EXPERT-OPINION`

**Why it matters.** The founder asked for 'around the world' and the artifact's international content is currently absent except as African-centred philosophy. These four traditions are the ones with real instructional substance for grade 6–8, they are free to adopt, and the last of them directly dissolves a false dichotomy the artifact has inherited.

**What to build.** (a) VARIATION THEORY / BIANSHI (Marton; Gu Lingyuan): an item generator that holds the critical feature invariant while systematically varying everything else, so the learner can discern what actually matters. Concrete rule for the content pipeline: no concept ships with fewer than four examples whose surface features vary and whose critical feature does not, plus at least one non-example. This is a better-specified version of 'interleaving' than the artifact currently has. (b) JAPANESE STRUCTURED PROBLEM-SOLVING + BANSHO: a lesson template of one rich problem → independent attempt → comparison of several student methods → teacher consolidation, with BANSHO (the whole lesson's thinking preserved on one board, left to right) as the collective note-taking artefact. For the app, bansho becomes a shared session canvas that the student keeps — far better evidenced as a note artefact than sketchnoting. Add HANSEI (structured reflection) as the close, which maps cleanly onto the SRL reflection phase and onto Sankofa. LESSON STUDY (jugyou kenkyuu) with kyouzai kenkyuu (study of materials) is the cheapest possible replacement for a 120-hour proprietary teacher PD programme and has far better international credibility. (c) SINGAPORE CPA: concrete → pictorial → abstract progression with the bar model for word problems — exceptionally well suited to ND learners because it externalises the relational structure that working memory would otherwise have to hold. (d) MEMORISATION-WITH-UNDERSTANDING (Watkins & Biggs, the 'Chinese learner paradox'): repetition used as a route to deeper understanding rather than as its opposite. Product consequence: every spaced-repetition card must be paired with a generation step ('say it in your own words'), so the deck is never pure rote — which resolves the artifact's unexamined tension between an Anki engine and an anti-rote rhetoric.

**Evidence.** Marton, F., & Booth, S. (1997) and Marton & Pang on variation theory; Gu, L., Huang, R., & Marton, F. (2004) on bianshi teaching in Chinese classrooms. Stigler, J. W., & Hiebert, J. (1999) The Teaching Gap and the TIMSS 1995/1999 video studies on Japanese structured problem-solving. Watkins, D. A., & Biggs, J. B. (1996, 2001) The Chinese Learner / Teaching the Chinese Learner — memorisation-with-understanding. Singapore CPA derives from Bruner's enactive-iconic-symbolic progression; bar-model evidence is largely descriptive plus favourable TIMSS/PISA system-level outcomes, which is correlational. ALL UNVERIFIED at primary in this session. NOTE ON TIER: variation theory and CPA have strong design rationale and classroom-descriptive evidence but thin randomised-trial support in Western settings; lesson study's effects on student outcomes are mixed in Western replications. Present them as well-reasoned design frames, not as effect sizes.

### 17. An African-centred and culturally sustaining strand built behind an explicit epistemic firewall   `EMERGING`

**Why it matters.** This is the heart of the project and it is currently its most citation-fragile section, because value claims and outcome claims are mixed in the same table ('ES: 0.8'). Separating them makes both stronger: the philosophy is argued on its own terms by serious scholars and needs no effect size to be legitimate, and the measured strand has real, citable, district-relevant numbers.

**What to build.** (a) Split the content architecture into two explicitly labelled registers. REGISTER A — PHILOSOPHICAL/NORMATIVE, argued as such: ubuntu in educational philosophy, Gyekye and Wiredu on African philosophical thought, Mkabela's Afrocentric research method, Dei and Emeagwali on African indigenous knowledge systems, Omolewa on indigenous education. These are curriculum content and design values; they carry citations, not effect sizes, and the certification materials say so. REGISTER B — EMPIRICAL, with scope conditions: Dee & Penner (2017) and Bonilla, Dee & Penner (2021) on ethnic studies; Aronson & Laughter (2016) on culturally relevant education across subjects; Byrd (2016) on culturally relevant teaching and school racial climate from the student perspective. (b) A standing editorial rule enforced in the content pipeline: no normative claim may be rendered with a numeric effect size, and no empirical claim may appear without population, design and boundary conditions. (c) Build the community advisory board the artifact already promises, give it sign-off on Register A, and give a methodologist sign-off on Register B. (d) For a 12-year-old: the shippable feature is a unit built on the SFUSD ethnic-studies model — identity, systems, and student-generated connection to their own community — which is what Dee & Penner actually studied, rather than a daily ancestor push notification, which is not.

**Evidence.** Dee, T. S., & Penner, E. K. (2017). American Educational Research Journal, 54(1), 127–166 — fuzzy RD; ~+21pp attendance, ~+1.4 GPA (IV; ~0.4 reduced form), ~+23 credits for students near a sub-2.0 threshold; identification contested. Bonilla, S., Dee, T. S., & Penner, E. K. (2021). PNAS, 118(37) — ~+16–19pp graduation; authors flag a concurrent early-warning-indicator programme as a confound. Aronson, B., & Laughter, J. (2016). Review of Educational Research, 86(1), 163–206. Byrd, C. M. (2016). Does culturally relevant teaching work? An examination from student perspectives. SAGE Open. Philosophical sources: Gyekye, Wiredu, Mkabela, Dei, Emeagwali, Omolewa — these are scholarly works of philosophy and method, not outcome studies, and must not be cited as evidence of achievement effects.

### 18. Sleep, chronotype and movement, specified honestly — the BARS sleep block's real evidence base   `ESTABLISHED`

**Why it matters.** The artifact's sleep block and chronotype diagnostic item (5.3) are among its better instincts and are currently unsupported by any citation. The adolescent sleep literature is strong enough to anchor a product feature, and the school-start-time experiments give defensible magnitudes. The movement claim needs the opposite treatment: it is currently smuggled in as a cultural learning style, which is not what the exercise literature supports.

**What to build.** (a) SLEEP as a scheduling constraint, not a suggestion: the scheduler refuses to place study blocks that push total sleep opportunity below the AAP-recommended 8.5–9.5 hours for adolescents, and surfaces the trade-off explicitly ('this study block costs you 40 minutes of sleep; here is where else it fits'). (b) CHRONOTYPE-AWARE placement of the hardest block, with a plain-language explanation of adolescent phase delay that students and parents can both read — this reframes 'he won't get up' from a character failure to a biological fact, which is itself a family-conflict intervention. (c) CONSOLIDATION: schedule a short review immediately before sleep and a brief retrieval check the next morning, and teach why. (d) MOVEMENT, honestly: a 10-minute moderate aerobic break before a study block, framed as arousal and attention regulation with a small, short-lived effect — explicitly NOT as modality matching or a cultural learning style. The paraeducator certification must state that 'kinesthetic learner' is not a thing while 'movement breaks help many students attend' is.

**Evidence.** Minges, K. E., & Redeker, N. S. (2016). Delayed school start times and adolescent sleep: A systematic review of the experimental evidence. Sleep Medicine Reviews, 28, 82–91 — across six experimental studies, start-time delays of 25–60 minutes produced increases in total sleep time of 25–77 minutes per weeknight (https://pmc.ncbi.nlm.nih.gov/articles/PMC4844764/). Widome, R., et al. (2020). Association of Delaying School Start Time With Sleep Duration, Timing, and Quality Among Adolescents. JAMA Pediatrics — actigraphy in five Minneapolis–St. Paul high schools; delayed-start students gained a mean 41 and 43 additional minutes of night sleep at two follow-ups (https://jamanetwork.com/journals/jamapediatrics/fullarticle/2765038). Dunster et al. (2018, Science Advances) — Seattle's 55-minute delay, wrist-actigraphy, longer sleep plus improved grades and attendance. AAP (2014). School Start Times for Adolescents. Pediatrics, 134(3), 642–649 — 8.5–9.5 hours recommended. Exercise and adolescent executive function: acute-bout effects are small and transient; chronic-training effects on academic achievement are modest and heterogeneous — UNVERIFIED at primary; retrieve a recent meta-analysis before quoting magnitudes.


---

## Open questions

- Does a 'NASA BARS' scheduling or mission-task method exist in any primary source? I searched and found only Behaviorally Anchored Rating Scales (Smith & Kendall, 1963, J. Applied Psychology 47(2):149–155), a performance-appraisal method with no NASA lineage. The founder should either produce the source (NASA Technical Reports Server would be the place to look) or rename the feature. Everything downstream — a scheduler, an agent, two certification domains, two modules — rests on this.
- Is there any peer-reviewed validation of Wade Cutler's 'Triple Reading Speed'? I found none indexed. If none exists, the method cannot be described as 'research-validated' in a document headed to a school district.
- What is the actual source and measurement basis for the artifact's five unsourced numbers: 38% test-anxiety prevalence; 85% of interventions validated on white populations; 73% of MCPS families lacking content knowledge and confidence; African-centred pedagogy ES = 0.8; 40% greater intrinsic motivation? Each should be sourced with instrument and sample, or deleted. I could not verify any of them.
- Does the Agarwal classroom finding — that low-stakes retrieval practice reduces rather than raises reported test anxiety in middle-schoolers — hold with the proportions commonly quoted, and does it hold specifically for students with clinically elevated test anxiety and for Black students in predominantly white evaluative settings? This is the single most load-bearing empirical question for the product's core thesis, and I could not verify the figures in this session.
- Is Spielberger's Test Anxiety Inventory normed for grades 6–8? The artifact plans to use it in the diagnostic and as a Test Anxiety Coach agent tool. If it is adult-normed, the scoring is not interpretable for this population and an age-appropriate instrument (e.g. the Children's Test Anxiety Scale) is needed.
- What does the replication record for Ramirez & Beilock (2011) expressive writing now look like? Reports of failed replications exist; the effect's status determines whether it ships as a core pre-test feature or as an A/B-tested option.
- Does pre-test racial/ancestral identity activation help or harm? The stereotype-threat mechanism predicts harm from identity salience in the evaluative moment; the affirmation literature predicts benefit when delivered early and away from it. This is directly testable in the 10-family pilot and no one appears to have tested it in this configuration. It may be the project's most publishable original question.
- For families where the parent screens high on maths anxiety, does the artifact's parent-tutor certification increase or decrease child achievement? Maloney et al. (2015) implies it could decrease it. This should be a pre-registered hypothesis of the pilot, not a discovery made at n=500.
- What is MCPS's own policy position on (a) IEP document upload to a third-party vendor, (b) AI-generated content in IEP progress reporting, and (c) the paraeducator CEU approval pathway? The artifact assumes all three. These are district-policy questions I cannot resolve from the document and they gate Phases 1 and 3.
- Can the certification credential be made meaningful without an accrediting body? 'PhD-level' is used nineteen times as a quality adjective with no accreditation behind it. The artifact's own partner-university track (Howard, Morgan State, UMCP) suggests the founder knows this; until a partner signs, the term is a claim of validation that has not occurred and should be dropped from external materials.
- Which single component should the 10-family pilot actually test? The artifact proposes to pilot the whole system at once, which will produce an uninterpretable result. On the evidence, the Daily Report Card plus HOPS routine plus spaced retrieval on real MCPS coursework is the highest-prior-probability bundle and could be run on paper plus a thin app in eight weeks — the AEOS principle of completion over validation over monetisation argues for shipping that, measuring it, and building the other nine tabs on what it shows.

