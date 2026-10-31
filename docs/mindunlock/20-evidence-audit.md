# Research integrity audit

> Every citation, named method, effect size and numeric claim in the artifact, checked against its source.

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

This artifact fails its own stated standard ("Evidence Before Claims ... Never imply validation that has not occurred") structurally, not clerically.

Three defect classes appear. First, CONFABULATED ARTIFACTS. "NASA BARS Method — Behavioral Anchoring / Mission-Critical Task Scheduling" (line 482) is not a NASA method. BARS is Behaviorally Anchored Rating Scales, a personnel-appraisal technique from Smith & Kendall (1963, J. Applied Psychology 47:149–155); NASA's real workload instrument is NASA-TLX. The artifact invented a methodology, attributed it to a federal agency, and built a core product feature (lines 75, 94, 530), a certification module (338), a paraeducator domain (404) and an AI agent (596) on it. Likewise "Anki SM-18 engine" (75, 97, 226, 679) fuses two unrelated things: SM-18 is Piotr Woźniak's proprietary SuperMemo algorithm, shipped in SuperMemo 18 for Windows; Anki never used it. Anki used an SM-2 variant and has shipped FSRS as its default scheduler since v23.10 (Oct 2023). "Anki SM-18" cannot be built as specified.

Second, INVENTED NUMBERS PRESENTED AS FINDINGS: "African-Centered Pedagogy ... (ES: 0.8)" (465), "40% greater intrinsic motivation" (168, 466), "interleaving ... by 43%" (461), stereotype threat "suppress performance 15–20%" (464), "73% of MCPS families lack both" (165), "38% of middle schoolers" (41), "85% of test anxiety interventions" (164), "60–90% speed increase" (483). None traces to the cited source. Several attach a fabricated number to a real, defensible literature — worse than omitting it, because it renders the credible underlying evidence unusable.

Third, A NEUROMYTH IS EMBEDDED IN THE DIAGNOSTIC INSTRUMENT: "5.1 VARK modality preference" (272) and "4.8 Preferred cultural learning style" (271). Pashler, McDaniel, Rohrer & Bjork (2008, PSPI 9:105–119) found no adequate evidence base for learning-styles matching. Shipping it inside a "psychometrically validated" instrument for Black neurodivergent children converts a debunked construct into a profile label attached to a child.

Fourth, the gap analysis calls itself a "Systematic review across 47 peer-reviewed sources, 24 courses, 38 apps" (159, 186) with no protocol, no search strategy, no inclusion criteria, no screening record and no PRISMA flow. That claim is not defensible and should be withdrawn, not repaired.

The honest summary: this is a credible, well-motivated product vision wrapped in a fabricated evidentiary shell. The vision survives removing the shell. The shell does not survive contact with the sources.

---

## Findings

### RI-01 — "NASA BARS Method" is a confabulation; BARS is a 1963 HR rating technique, not a NASA scheduling system

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.96 |

**What the artifact says**
> Line 482: "NASA BARS Method | Behavioral Anchoring / Mission-Critical Task Scheduling ... NASA-derived time management adapted for student academic life." Also line 75 ("BARS-format AI mission schedule builder"), 94, 137 ("Synthesize NASA BARS + learning science literature"), 338 (Module 7), 404 (paraeducator domain 8), 530, 596.

**The problem**

There is no NASA method called BARS. In the published literature BARS means Behaviorally Anchored Rating Scales, introduced by Smith & Kendall (1963) as a performance-appraisal scale-construction method using critical-incident retranslation — a personnel psychology instrument with no connection to scheduling, time blocking, or NASA. NASA's actual task/workload instruments are NASA-TLX (Hart & Staveland, 1988) for subjective workload and operations-research scheduling tools for mission timelines; neither is called BARS nor resembles "15-minute color-coded blocks." The artifact expands "Behavioral Anchoring" as the A and R, which is a back-formation. A Research Agent is instructed (line 137) to "synthesize NASA BARS ... literature" — a literature that does not exist, which will produce fabricated output. This is the single most dangerous item: the name is doing persuasive work (federal-agency borrowed authority) in front of districts, grant reviewers and parents, for a feature that is actually just time-blocking.

**Evidence**

Smith, P.C. & Kendall, L.M. (1963). "Retranslation of expectations: An approach to the construction of unambiguous anchors for rating scales." Journal of Applied Psychology 47(2):149–155 — verified via search. Flanagan (1954) critical incident technique is the upstream method. NASA-TLX: Hart & Staveland (1988), in Hancock & Meshkati (eds.), Human Mental Workload. No NASA publication, NASA Technical Report, or NASA-affiliated source using "BARS" for task scheduling was located.

**Recommendation**

Delete every occurrence of "NASA" from this feature and rename it. Replacement wording: "Mission Blocks — a 15-minute time-blocking and task-decomposition scheduler. Time-blocking and task decomposition are standard executive-function supports (see Dawson & Guare, Executive Skills in Children and Adolescents); the specific MindUnlock implementation is unvalidated and is being evaluated in our pilot. Not affiliated with or derived from NASA." Remove line 137's instruction to synthesize a non-existent literature. If behaviorally anchored rating scales are genuinely wanted for the certification rubrics (lines 345, 430) — which would be a legitimate, well-matched use — cite Smith & Kendall (1963) there and nowhere else.

### RI-02 — "Anki SM-18" does not exist: SM-18 is proprietary SuperMemo; Anki's current default is FSRS

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.95 |

**What the artifact says**
> Line 75 "Spaced repetition Anki engine (SM-18)"; line 97 "Integrate Anki SM-18 spaced repetition engine"; line 226 "Anki ... Best-in-class SM-18 algorithm"; line 594 "SM-18 spaced repetition scheduler"; line 679 "SM-18 Algorithm | Spaced Repetition | Anki-compatible; AnkiConnect sync"; line 774 "Anki SM-18 integration + AnkiConnect sync".

**The problem**

Three errors compounded. (1) SM-18 is Piotr Woźniak's SuperMemo algorithm, used in SuperMemo 18 for Windows, owned by SuperMemo World — a commercial competitor. Anki has never used it. (2) Anki historically used a modified SM-2 (the 1987-era algorithm), and since Anki 23.10 (October 2023) the default scheduler has been FSRS (Free Spaced Repetition Scheduler, created by Jarrett Ye), now at FSRS-5/6, trained on hundreds of millions of reviews and released open-source under a permissive licence. (3) "AnkiConnect sync" (679) names a third-party local HTTP add-on that requires the Anki desktop client to be running on the same machine; it is not a server-to-server API and cannot back a mobile product for 500 families. The roadmap therefore commits Phase 2 engineering (line 774) to integrating a competitor's proprietary algorithm into an unrelated open-source product via an add-on that does not work in the stated architecture.

**Evidence**

SuperMemo Guru, "Algorithm SM-18" (supermemo.guru/wiki/Algorithm_SM-18): "Algorithm SM-18 is currently in use only in SuperMemo 18 for Windows"; SuperMemo Help confirms SM-19 and later versions. FSRS as Anki default from 23.10: open-spaced-repetition/fsrs4anki docs/tutorial.md, which states SM-2 is the old scheduler; The History of FSRS for Anki (LessWrong). Note: I could not fetch docs.ankiweb.net — that host is outside this session's allowed network domains — so the exact current Anki version/FSRS revision should be confirmed against Anki's own manual before publishing.

**Recommendation**

Replace every instance with: "Spaced repetition powered by FSRS (Free Spaced Repetition Scheduler), the open-source algorithm that is Anki's default scheduler. We use the open-source FSRS implementation directly in our own scheduler; we do not use, licence, or claim compatibility with SuperMemo's SM-18, which is a separate proprietary product." Change line 226 to: "Anki — strong open-source FSRS scheduler; steep UX curve for neurodivergent middle schoolers; desktop-centric; no anxiety, family or cultural layer." Delete "AnkiConnect sync" and replace with "optional .apkg import/export for users who already keep Anki decks." Add to the Phase 2 milestone: "implement FSRS scheduling in-house (Rust/Python bindings are MIT-licensed); verify licence compliance before shipping."

### RI-03 — "Systematic review" is claimed four times with no protocol, search strategy, inclusion criteria or PRISMA flow

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.95 |

**What the artifact says**
> Line 159: "PhD-Level Gap Analysis | Systematic review across 47 peer-reviewed sources, 24 courses, 38 apps (2018–2024)". Line 186: "Systematic review of 24 test anxiety courses, 18 study skills programs, 12 family education platforms (2018–2024)". Line 137: "Map gap analysis: 38 apps reviewed".

**The problem**

"Systematic review" is a term of art with a defined floor: a registered or at minimum documented protocol, a reproducible search string across named databases, dates of search, explicit inclusion/exclusion criteria, dual independent screening with an agreement statistic, a risk-of-bias appraisal, and a PRISMA 2020 flow diagram accounting for every record from identification to inclusion. The artifact has none of these. It also cannot: no bibliography of the 47 sources appears anywhere in 859 lines, and the six apps actually shown (226–231) are not 38. Numbers that total neatly (24+18+12) and a round "47 peer-reviewed sources" with zero visible references are the signature of a narrative scan reported as a systematic review. For a founder whose stated principle is "no claims of validation that has not occurred," and who will present this to MCPS district leadership (line 777) and federal grant reviewers (line 727), this is a misrepresentation that an IES or NSF reviewer will catch immediately and that will contaminate the credibility of everything else in the document.

**Evidence**

PRISMA 2020 statement (Page et al., BMJ 2021;372:n71) specifies the 27-item reporting checklist and flow diagram. Cochrane Handbook v6 ch.1 defines the systematic review minimum (pre-specified eligibility criteria, systematic reproducible search, assessment of validity of findings). Neither standard is approached here.

**Recommendation**

Downgrade the language. Replace line 159 with: "Landscape Scan — informal, non-systematic. We reviewed a convenience sample of commercial products and a reading list of research sources; this is not a systematic review and has no protocol, search strategy, or risk-of-bias appraisal. A PRISMA-conformant review is scoped for Phase 3." Replace line 186 with: "Informal comparison of named commercial programs, selected by market visibility, not by systematic search." Then either (a) publish the actual 47-source bibliography as an appendix with every claim linked to a specific source, or (b) delete the number "47." Do not keep an uncountable count.

### RI-04 — "African-Centered Pedagogy ... raises Black student achievement (ES: 0.8)" — the effect size is invented and it displaces a real, strong body of evidence

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Line 465: "African-Centered Pedagogy | Hilliard (1997), Nobles (2006), Asante (1987) | Culturally affirming instruction raises Black student achievement (ES: 0.8)".

**The problem**

Hilliard (1997, SBA: The Reawakening of the African Mind), Nobles (2006, Seeking the Sakhu) and Asante (1987, The Afrocentric Idea) are theoretical and philosophical works. None reports an effect size; none is an intervention study; none could produce a pooled d = 0.8. An ES of 0.8 is Cohen's conventional 'large' threshold — the number has the texture of a placeholder that was never replaced. This is the most self-defeating error in the document, because culturally relevant and ethnic-studies pedagogy has genuinely strong causal evidence that the artifact does not cite. Dee & Penner (2017, AERJ 54:127–166), a fuzzy RD study of San Francisco's ninth-grade ethnic studies course, found roughly +1.4 GPA points, +21 percentage points in attendance and +23 credits earned for students near the 2.0 assignment cutoff; Bonilla, Dee & Penner (2021, PNAS 118:e2026386118), preregistered, found increases in high school graduation and college enrollment. Those are real, large, defensible, and directly on point for a BIPOC middle-school product — and citing them instead of a made-up 0.8 would make the case stronger, not weaker.

**Evidence**

Dee, T.S. & Penner, E.K. (2017). "The Causal Effects of Cultural Relevance: Evidence from an Ethnic Studies Curriculum." American Educational Research Journal 54(1):127–166 (NBER w21865) — verified. Bonilla, Dee & Penner (2021), PNAS 118(37):e2026386118 — verified, preregistered follow-up. Caveat to report honestly: the Dee & Penner effects come from a small subgroup at an RD cutoff (critics note roughly 112 students below the 2.0 threshold) and from one high-fidelity district; they are high-school, not middle-school; generalization is not established. Aronson & Laughter's (2016, Review of Educational Research 86:163–206) synthesis of culturally relevant education is a narrative/qualitative synthesis, not a meta-analysis with a pooled effect size — I could not verify a pooled d from it and would not cite one.

**Recommendation**

Replace line 465 with: "Culturally Relevant / Ethnic Studies Pedagogy | Ladson-Billings (1995); Dee & Penner (2017); Bonilla, Dee & Penner (2021) | A quasi-experimental study of San Francisco's ethnic studies course found large gains in attendance, GPA and credits for students assigned near the eligibility cutoff, with follow-on gains in graduation and college enrollment. [ESTABLISHED for high-school ethnic studies in one district; not yet established for middle school, and not established for the specific African-centered framing we use.] Hilliard (1997), Nobles (2006) and Asante (1987) are the philosophical foundation of our design; they are theory, not outcome evidence, and we do not cite them for effect sizes." Delete "(ES: 0.8)" entirely. Do not substitute another number.

### RI-05 — VARK learning-styles matching is embedded as diagnostic Domain 5.1 — a debunked construct used to label neurodivergent Black children

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.94 |

**What the artifact says**
> Line 272: "5.1 VARK modality preference (Visual / Auditory / Kinesthetic / Reading-Writing)" within "Domain 5: Neurodivergent & Sensory Profile." Line 271: "4.8 Preferred cultural learning style (call-response, storytelling, movement)." Line 258 frames the whole instrument as "Psychometrically validated."

**The problem**

The meshing hypothesis — that instruction matched to a learner's modality preference improves learning — is the single most thoroughly tested and most thoroughly unsupported idea in applied learning science. Pashler, McDaniel, Rohrer & Bjork (2008) found that almost no study used the crossover-interaction design required to test it, and that several studies which did contradicted it. Subsequent modality-specific reviews report effect sizes near zero. Two aggravations specific to this product: (a) the construct sits inside a 52-domain instrument the artifact calls "psychometrically validated" (258) and which feeds an "AI-generated personalized learning plan PDF" (529) and an "adaptive difficulty engine" (594) — so a debunked label will be algorithmically acted upon; (b) item 4.8 assigns a "cultural learning style" to Black children (call-response, storytelling, movement). Even where Boykin's (1994) Afrocultural ethos work describes verve and communalism as cultural orientations, that is a description of cultural context, not a claim that matching modality to ethnicity improves learning. Operationalizing it as a per-child diagnostic score risks producing exactly the essentialized, lowered-expectation profiling the project exists to oppose.

**Evidence**

Pashler, H., McDaniel, M., Rohrer, D. & Bjork, R. (2008). "Learning Styles: Concepts and Evidence." Psychological Science in the Public Interest 9(3):105–119: "there is no adequate evidence base to justify incorporating learning-styles assessments into general educational practice" — verified. Modality-specific mini-review (Front. Psychol., PMC6113575) reports overall effect sizes "very low and non-significant" in methodologically adequate studies. Boykin, A.W. (1994) on Afrocultural ethos describes cultural orientation, not a modality-matching prescription.

**Recommendation**

Delete item 5.1 outright. Replace with: "5.1 Representation preference and access needs — which formats the student can access, not which format they 'learn best' in. We record preference for engagement and accessibility reasons (UDL multiple means of representation), and we state explicitly that matching instruction to a preferred modality is NOT supported by evidence (Pashler et al., 2008) and does not drive our content sequencing." Rewrite 4.8 as: "4.8 Culturally familiar instructional formats the student responds to (call-and-response, oral narrative, movement) — recorded to inform engagement and classroom ritual design, not to assign a learning type or to route content. Cultural orientation is not an ability profile." Add a hard product constraint: no diagnostic domain may change content routing unless it has a documented validity argument.

### RI-06 — "Wade Cutler's Triple Reading Speed" and "60–90% speed increase with equal or greater comprehension" contradict the reading-science consensus

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Line 483: "Wade Cutler's Triple Reading Speed | 3-Pass Reading Comprehension & Acceleration System ... Result: 60–90% speed increase with equal or greater comprehension" and "Speed building: Preview Read alone = 60% speed gain." Also lines 167, 338 (Module 6), 423, 531, 774.

**The problem**

Wade E. Cutler is the author of a 1980s trade paperback (Triple Your Reading Speed, the 'Acceleread' method). There is no peer-reviewed research base for the method, no published trial, and no evidence Cutler holds the doctorate some editions advertise. The specific claim — large speed gains with 'equal or greater comprehension' — is the exact claim the field's authoritative review rejects. Rayner, Schotter, Masson, Potter & Treiman (2016, Psychological Science in the Public Interest 17:4–34) conclude that doubling or tripling reading rate while maintaining comprehension is not achievable; speed above roughly normal rates buys skimming, which yields gist at the cost of comprehension; and the main real levers on reading rate are language skill and vocabulary, not eye-movement technique. This matters doubly here because the target users are students with literacy deficits (line 41: "Students with literacy deficits cannot access study strategies built for fluent readers"). Selling a speed-reading module to struggling decoders is the opposite of what the artifact's own Scarborough Rope framing (167, 270) implies they need. Separately, the three-pass structure (preview, deep read, review) is itself fine — it is essentially SQ3R/preview-reading, which has modest support as a comprehension strategy. The structure is salvageable; the speed claim and the branded attribution are not.

**Evidence**

Rayner, K., Schotter, E.R., Masson, M.E.J., Potter, M.C. & Treiman, R. (2016). "So Much to Read, So Little Time: How Do We Read, and Can Speed Reading Help?" Psychological Science in the Public Interest 17(1):4–34 — verified. Cutler: LibraryThing author record and an independent blog self-test reporting a rise from ~280 wpm to ~300–380 wpm (a ~10–35% gain, not tripling) — no peer-reviewed source located. Scarborough, H.S. (2001), "Connecting early language and literacy to later reading (dis)abilities," in Neuman & Dickinson (eds.), Handbook of Early Literacy Research — correctly cited by the artifact and squarely against the speed-reading framing.

**Recommendation**

Rename and restate. Replace line 483 with: "Three-Pass Reading Protocol | Preview → Deep Read → Review-and-Encode. A structured previewing-and-review routine drawn from the SQ3R family. We make no speed claim. The evidence (Rayner et al., 2016, PSPI) is that reading rate cannot be doubled or tripled without losing comprehension, and that rate is driven by vocabulary and language skill, not by eye-movement training. The purpose of this protocol is comprehension and retention, not speed. For students with decoding difficulty, structured literacy instruction — not speed training — is the indicated support." Delete Module 6's title (338) and the teacher module "Speed Reading & Literacy Acceleration Methods" (423); rename to "Structured Previewing and Academic Language Development." Remove "Triple Reading Speed (Cutler)" from line 167.

### RI-07 — "Study 90% Faster — With and Without AI" is an unsourced efficiency claim appearing in a paid certification and a paid product feature

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.92 |

**What the artifact says**
> Line 75 "90% faster study with AND without AI"; line 338 Module 9 "Study 90% Faster — With and Without AI"; line 400 "90% faster study facilitation" (paraeducator competency domain 4); line 531 "90%-faster study timer with/without AI mode".

**The problem**

No source is given anywhere, and none exists. There is no literature reporting a 90% reduction in study time from any combination of strategies. The best-evidenced study techniques (distributed practice, retrieval practice, interleaving) produce moderate improvements in retention per unit time, not order-of-magnitude reductions in time required; Dunlosky et al. (2013, PSPI 14:4–58) rate distributed practice and practice testing as the only two techniques with high utility and reports no such efficiency multiplier. The claim is also commercially load-bearing: it is a module inside a $299 paraeducator certification (725) and the $49/mo family subscription (723). An unsubstantiated quantified performance claim attached to a priced educational product aimed at under-resourced families is a consumer-protection exposure (FTC Act §5 substantiation doctrine for express performance claims), independent of its research-integrity problem.

**Evidence**

No source located for any "90% faster study" claim. Dunlosky, J., Rawson, K.A., Marsh, E.J., Nathan, M.J. & Willingham, D.T. (2013). "Improving Students' Learning With Effective Learning Techniques." Psychological Science in the Public Interest 14(1):4–58 — the standard utility rating of ten study techniques; reports no time-reduction multiplier. [INFERENCE] on the FTC exposure: express quantified performance claims require competent and reliable substantiation at the time the claim is made; I have not had counsel review this and the specific application to an ed-tech subscription is unverified.

**Recommendation**

Delete the number everywhere. Replace Module 9's title with: "Studying Less and Remembering More — Using Retrieval Practice, Spacing and Interleaving (With and Without AI)." Replace line 531 with "Study session timer with spaced-review scheduling." Replace line 400 with "evidence-based study-strategy facilitation." Add to the module description: "We do not claim a specific percentage improvement. The techniques taught here have the strongest evidence of any study strategies (Dunlosky et al., 2013), but the size of the benefit for any individual student is not something we can promise. We will report our own pilot results, whatever they show."

### RI-08 — "73% of MCPS families lack both" content knowledge and confidence — a fabricated district statistic about a real, identifiable school district

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.91 |

**What the artifact says**
> Line 165: "Hoover-Dempsey & Sandler (1997): Parent involvement is most effective when parents have BOTH content knowledge AND confidence in academic support strategies. 73% of MCPS families lack both."

**The problem**

The sentence is constructed so the 73% appears to follow from the citation. It does not. Hoover-Dempsey & Sandler (1997, Review of Educational Research 67:3–42) is a theoretical model of why parents become involved; it contains no MCPS data and no such percentage. No MCPS, Maryland State Department of Education, or NCES instrument measures "content knowledge AND confidence" as a joint construct at the household level, so the figure cannot have been derived from any published source. The author is an MCPS employee; attributing an invented deficit statistic to his own employer's families — and to a specific, named, majority-minority district — is the highest-liability item in the document after the NASA claim. It is both a research-integrity failure and a professional and reputational risk: if this reaches a district leadership presentation (line 777) or a grant application (727), the first person to ask 'where does 73% come from?' ends the conversation.

**Evidence**

Hoover-Dempsey, K.V. & Sandler, H.M. (1997). "Why do parents become involved in their children's education?" Review of Educational Research 67(1):3–42 — a model-building paper on parental role construction, self-efficacy, and invitations; contains no district prevalence data. [INFERENCE] I could not locate any MCPS or MSDE published statistic resembling this; I would check MCPS's annual Family Engagement survey reports and MSDE's Maryland Report Card family-survey items before concluding definitively that none exists.

**Recommendation**

Delete the number. Replace with: "Hoover-Dempsey & Sandler (1997) model parent involvement as a function of role construction, self-efficacy and invitations from the school — parents act when they believe helping is their job AND believe they can do it. [EXPERT-OPINION / theoretical model; widely used, not an outcome trial.] We do not have data on how many MCPS families lack content knowledge or confidence. Measuring this is the first thing our parent diagnostic is for, and we will publish the pilot baseline." Apply the same rule to every other MCPS-specific assertion in the document: if MCPS is named, the source must be an MCPS or MSDE public document, cited by name and year.

### RI-09 — "38% of middle schoolers experience debilitating test anxiety (Zeidner, 1998)" — number not traceable to the cited source and far above published prevalence estimates

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Line 41, the first bullet of the Problem Statement: "38% of middle schoolers experience debilitating test anxiety (Zeidner, 1998)".

**The problem**

Zeidner (1998), Test Anxiety: The State of the Art, is a review monograph; it does not report a 38% US middle-school prevalence for 'debilitating' test anxiety, and the term 'debilitating' is not an operational diagnostic category with an agreed cut score. Published prevalence estimates for high test anxiety cluster in the 10–30% range depending on instrument, cut score and population, with commonly cited figures around 15–22%. The artifact has taken the top of a contested range, sharpened it to a false-precision two-digit figure, attached 'debilitating', and placed it as the opening sentence of the problem statement — the single most quoted line in any pitch document. The underlying problem is real and the von der Embse meta-analysis actually strengthens the case for a middle-school product, because it found the negative association between test anxiety and performance was most pronounced at the middle grades. That is the finding to lead with.

**Evidence**

von der Embse, N., Jester, D., Roy, D. & Post, J. (2018). "Test anxiety effects, predictors, and correlates: A 30-year meta-analytic review." Journal of Affective Disorders 227:483–493 — 238 studies; negative association with performance, "most pronounced at the middle grades level"; effect sizes small to moderate — verified. Prevalence range 15–22% and 10–30% for secondary students appear in secondary literature reviews — I verified these appear but did not trace each to its primary study, so treat the range as approximate, not as a citable point estimate.

**Recommendation**

Replace with: "Test anxiety is most strongly associated with depressed academic performance at the middle-grades level — the exact years our students are in (von der Embse et al., 2018, meta-analysis of 238 studies; effect sizes small to moderate). [ESTABLISHED association; small-to-moderate magnitude.] Published prevalence estimates for high test anxiety in secondary students range roughly 10–30% depending on instrument and cut score; there is no agreed clinical threshold for 'debilitating' test anxiety and we do not cite a single prevalence figure. [EMERGING]." Delete "Zeidner, 1998" as the source of any number; retain it only where cited for the construct model (line 264, 338), which is appropriate.

### RI-10 — "85% of test anxiety interventions validated only on white, middle-class, neurotypical populations" — a real and important equity gap reported as a fabricated statistic

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.89 |

**What the artifact says**
> Line 164: "85% of test anxiety interventions validated only on white, middle-class, neurotypical populations (Zeidner, 1998; von der Embse et al., 2018). No published program uses Ubuntu, Sankofa, or ancestral identity as therapeutic anchors."

**The problem**

Neither cited source reports an 85% figure. von der Embse et al. (2018) is a meta-analysis of test anxiety effects, predictors and correlates — not a sample-demographics audit of intervention trials. Producing an 85% figure would require coding the participant demographics of every intervention trial in the field, which is a real and publishable piece of work that nobody in this document has done. The underlying claim is almost certainly directionally true and is the strongest argument in the entire artifact: WEIRD-sample dominance in psychological intervention research is extensively documented, and the US clinical and educational intervention literature badly underrepresents Black and neurodivergent adolescents. By inventing a number, the artifact converts its best argument into its most falsifiable one. The second sentence ('No published program uses Ubuntu, Sankofa, or ancestral identity as therapeutic anchors') is an absolute negative claim about the entire published literature, made without a search strategy — unsupportable as stated, and unnecessary.

**Evidence**

Henrich, Heine & Norenzayan (2010), "The weirdest people in the world?", Behavioral and Brain Sciences 33:61–83 — the foundational documentation of WEIRD-sample dominance. Roberts, Bareket-Shavit, Dollins, Goldie & Mortenson (2020), "Racial inequality in psychological research," Perspectives on Psychological Science 15:1295–1309 — documents under-reporting and under-sampling of race in US psychology publications. [INFERENCE] that this generalizes to test-anxiety intervention trials specifically: plausible and likely, but I located no study that has coded that literature's demographics, so the 85% has no empirical anchor.

**Recommendation**

Replace with: "Psychological intervention research overwhelmingly samples WEIRD populations (Henrich et al., 2010), and US psychology journals systematically under-report and under-sample race (Roberts et al., 2020). [ESTABLISHED for the field as a whole; INFERENCE as applied to test-anxiety interventions specifically — we have not audited that literature's demographics and we do not have a percentage.] We are not aware of a published, evaluated test-anxiety program built on Ubuntu, Sankofa or ancestral identity; we have not conducted a systematic search, so we say 'we are not aware of' rather than 'none exists.' Auditing the demographic composition of test-anxiety intervention trials is a piece of work worth doing and we intend to do it." Note: this rewrite is a stronger pitch than the original, because it is defensible.

### RI-11 — Growth Mindset is cited from Dweck (2006) with no mention of the replication and meta-analytic record that halved it

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.94 |

**What the artifact says**
> Line 463: "Growth Mindset | Dweck (2006) — Stanford University | Malleable intelligence framing raises achievement and resilience | Every module reframes 'I can't' as 'I can't YET'".

**The problem**

Citing a 2006 trade book for an effect claim in 2026 and omitting the intervening replication record is the textbook pattern of overstatement. The actual record: Sisk et al. (2018, Psychological Science 29:549–571) ran two meta-analyses — 273 studies, N≈366,000 for the mindset-achievement correlation (weak; roughly 1% of variance), and 43 intervention studies, N≈57,000, giving a pooled d = 0.08 [95% CI 0.02, 0.14]. Macnamara & Burgoyne (2023, Psychological Bulletin) independently replicate that d ≈ 0.08 and report that effects shrink further under publication-bias correction. Yeager et al.'s (2019, Nature 573:364–369) National Study of Learning Mindsets — a large preregistered US RCT — found a small GPA effect concentrated in lower-achieving students. The honest summary is: real but small, strongest in exactly the population this product serves (lower-achieving, at-risk students), and dependent on implementation fidelity and school norms. Sisk et al. themselves note larger benefits for low-SES and academically at-risk students. That nuance is the artifact's friend; omitting it is what makes the claim indefensible.

**Evidence**

Sisk, V.F., Burgoyne, A.P., Sun, J., Butler, J.L. & Macnamara, B.N. (2018). Psychological Science 29(4):549–571 — k=273, N=365,915; intervention d=0.08 [0.02, 0.14] — verified. Macnamara & Burgoyne (2023), Psychological Bulletin — independent replication of d≈0.08 — verified via the 2022 preprint. Yeager et al. (2019), Nature 573:364–369 — I did not independently verify the exact GPA point estimate (commonly reported as ~0.1 GPA points in lower-achieving students) in this session; treat the magnitude as unverified and check the paper before publishing a number.

**Recommendation**

Replace with: "Growth Mindset | Dweck (2006); Sisk et al. (2018) meta-analysis; Yeager et al. (2019) national RCT | Brief growth-mindset interventions produce a small average achievement effect (pooled d ≈ 0.08 across 43 studies, N≈57,000), with larger effects for low-SES and academically at-risk students — the population we serve. Early claims were substantially larger than the replicated effect. [ESTABLISHED, small.] We use mindset language as one supporting element, not as a mechanism of change, and we do not promise achievement gains from it."

### RI-12 — "Stereotype Threat ... suppress performance 15–20%" — a fabricated magnitude on a literature with a documented publication-bias problem in exactly this population

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Line 464: "Stereotype Threat | Steele & Aronson (1995) — Stanford | Identity-based negative stereotypes suppress performance 15–20%". Also line 268 (diagnostic item 1.12), 271 (4.5), 312, 423.

**The problem**

Steele & Aronson (1995, JPSP 69:797–811) reported a between-condition difference on a lab verbal test with covariate adjustment for prior SAT; it does not report a 15–20% performance suppression, and no meta-analysis supports that magnitude as a general figure. More importantly, the artifact silently presents a contested literature as settled. Flore & Wicherts (2015, Journal of School Psychology 53:25–44), meta-analysing 47 effect sizes on schoolgirls, found a mean d = −0.22 with multiple indicators of publication bias and concluded that bias "might seriously distort the literature"; bias-adjusted estimates shrink substantially (Shewach et al., 2019, reanalysis). Flore, Mulder & Wicherts' (2018) large preregistered replication in Dutch schools found no threat effect. Field-setting and child/adolescent effects are weakest, which is precisely the setting this product operates in. The artifact then builds on this: it makes 'stereotype threat susceptibility' a scored diagnostic item on individual Black children (1.12, 4.5) and prescribes an 'African ancestor activation before every assessment' as the countermeasure — a mechanism-specific intervention claim resting on a contested mechanism and a fabricated magnitude.

**Evidence**

Flore, P.C. & Wicherts, J.M. (2015). "Does stereotype threat influence performance of girls in stereotyped domains? A meta-analysis." Journal of School Psychology 53(1):25–44: mean d = −0.22, significant, "several signs for the presence of publication bias" — verified. Shewach, Sackett & Quint (2019), Journal of Applied Psychology, reanalysis: the 2015 estimate "decreased substantially after conducting adjustments for publication bias" — verified. Sackett, Hardison & Cullen (2004), American Psychologist 59:7–13, on widespread misinterpretation of Steele & Aronson (1995) as showing threat eliminates the Black–white test gap. Note: Flore & Wicherts is a gender/schoolgirl meta-analysis; the race-based adolescent field literature is thinner still, and a PLOS ONE protocol for a Black-American stereotype-threat meta-analysis indicates no settled pooled estimate yet existed at registration.

**Recommendation**

Replace with: "Stereotype Threat | Steele & Aronson (1995); Flore & Wicherts (2015) meta-analysis; Flore, Mulder & Wicherts (2018) preregistered replication | Laboratory studies find that making a negative group stereotype salient can depress test performance. [EMERGING / CONTESTED: the school-age meta-analytic estimate is small (d ≈ −0.22) and shows clear signs of publication bias; a large preregistered school replication found no effect; field effects in children are the weakest part of the literature.] We design for identity affirmation because our families tell us it matters and because the downside risk is nil — not because we can promise a measured performance gain." Delete item 1.12 as a scored construct on individual children, or demote it to a non-scored context note. Do not advertise ancestor activation as a stereotype-threat countermeasure with a quantified effect.

### RI-13 — TAM figures are stale or unsourced: "6.4M students with IEPs" understates the current IDEA count by ~20–25%

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.92 |

**What the artifact says**
> Line 245: "TAM: 6.4M students with IEPs, 74M K-12 parents, 1.3M paraeducators — all currently underserved."

**The problem**

6.4M is roughly the IDEA Part B child count from the late 2000s/early 2010s. The current figures are materially higher: approximately 7.9 million children ages 3–21 served under IDEA Part B in 2023–24 (of which ~7.3M school-age, 5-in-K through 21), and the most recent federal release analysed by CEC reports 8,194,424 — a 3.8% year-over-year increase. The error is in the conservative direction, so it understates the market, but it signals that the numbers were not checked, which is what a diligence reader will conclude about every other number on the page. "74M K-12 parents" has no source and appears to be derived from the US under-18 population (~73M), which is a count of children, not of K-12 parents, and double-counts two-parent households against a per-child figure. "1.3M paraeducators" is in the right neighbourhood for public-school instructional aides but is uncited; BLS's current Occupational Outlook Handbook projects little or no change in teacher-assistant employment with ~176,200 annual openings, and NCES reports instructional aide FTE counts separately — the two sources do not give the same number and the artifact must pick one and name it.

**Evidence**

IDEA Part B: CRS R41833 reports ~7.9 million children ages 3–21 under Part B for 2023–24; Advocacy Institute's analysis of the federal release gives 7,892,433 (ages 3–21), with 587,908 ages 3–5 and 7,304,525 school-age; CEC analysis of the most recent release gives 8,194,424 (+3.8%, +301,991). NCES reported 7.5 million for 2022–23 as an all-time high. BLS Occupational Outlook Handbook, Teacher Assistants: little or no change projected 2025–2035, ~176,200 annual openings, median wage $36,780 (May 2025). I could not retrieve the BLS OEWS 25-9045 national employment total in this session — that specific number remains unverified.

**Recommendation**

Replace with: "TAM (sourced, as of the most recent federal release): ~8.19M children ages 3–21 served under IDEA Part B nationally (US Dept. of Education Part B Child Count, most recent release; 7.89M in 2023–24). Paraeducators/teacher assistants: [cite BLS OEWS 25-9045 national employment, retrieved <date>] — BLS projects little or no employment change through 2035 with ~176,200 annual openings. We do not have a defensible count of 'K-12 parents' and have removed that figure; our addressable unit is households with an enrolled K-12 child, which we will size from NCES enrollment and Census household composition." Add a rule: every TAM number carries its source and retrieval date inline.

### RI-14 — "Meets Our Needs" percentages (Anki 45%, Headspace 20%, Duolingo 30%, Notion 15%, Google Classroom 10%, Brainly 25%) have no rubric behind them

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Lines 226–231, each app card rendering a "Meets Our Needs" score as a large orange percentage; line 244: "Market Conclusion: No Comparable App Exists."

**The problem**

Every score is a round multiple of 5, every competitor scores below 50%, and the product that scores highest (Anki, 45%) is praised for an algorithm it does not use (see RI-02). There is no stated dimension set, no weights, no scoring anchors, no rater, no inter-rater check, and no date of evaluation. A score with a percent sign and a 2xl font implies measurement; this is a self-assessment rendered as data. The structural problem is that the rubric is implicitly the product's own feature list — the '8 Innovation Pillars' at line 215, which the artifact itself says are 'Present in Zero Existing Programs.' Scoring competitors against your own feature list guarantees they lose and tells a reader nothing. This is the kind of chart that reads as rigour to a friendly audience and as a red flag to an investor or district procurement officer.

**Evidence**

[INFERENCE] from the internal structure of the artifact: no rubric, weights, anchors, rater or date appears anywhere in 859 lines. Standard practice for a defensible competitive scoring rubric: a pre-specified dimension set derived from user needs (not from your own roadmap), explicit weights summing to 1, behaviourally anchored levels per dimension (0/1/2/3 with written descriptors), at least two independent raters with a reported agreement statistic, the evaluation date and product version, and publication of the filled scoring sheet.

**Recommendation**

Either build the rubric or drop the numbers. Minimum defensible version: "Competitive fit assessment (internal, single-rater, <date>): we scored six products against 10 user-need dimensions drawn from our parent and student interviews — not from our roadmap — with written 0–3 anchors per dimension and stated weights. Scoring sheet: [link]. This is a single-rater internal judgement, not a benchmark." Fix the Anki row to reflect FSRS. Replace line 244 with: "We have not found a product that combines these capabilities for this population. We have not conducted a systematic market search, so this is 'we have not found one', not 'none exists.'"

### RI-17 — The diagnostics are labelled "Psychometrically validated" and "PhD-Level" before a single item has been written or piloted

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Line 258: "PhD-Level Diagnostic Assessments | Psychometrically validated | Student: 52 domains | Parent: 38 domains | Staff: 24 domains." Line 91 lists building the instrument as next action #1, Week 1–2. Line 771 lists "PhD-level student diagnostic (52 domains) validated" as a Phase 1 milestone.

**The problem**

The instrument is simultaneously described as already validated (258) and as a thing to be built in Weeks 1–2 (91). Psychometric validation is not a week-two deliverable: it requires item development, cognitive interviews, a pilot sample large enough for factor analysis (conventionally 5–10 respondents per item, so 260–520 students for a 52-item instrument), reliability estimates per subscale, evidence of convergent and discriminant validity against established measures, and — critically for this population — measurement invariance testing across race and disability status before any score is compared across groups. A 52-'domain' instrument that also claims to measure working memory via digit span (item 2.1), phonological awareness (3.1) and reading fluency with prosody scoring (3.2) is making assessment claims that in most states require administration by a licensed school psychologist and that overlap directly with IDEA evaluation procedures. Line 91 says 'validated with licensed school psychologist' — one psychologist reviewing items is content-expert review, not validation. Also, '52 domains' is a misnomer: the document describes 6 domains with 52 items.

**Evidence**

AERA/APA/NCME Standards for Educational and Psychological Testing (2014), esp. Standard 1 (validity evidence) and Chapter 3 (fairness, including measurement invariance across subgroups). IDEA 34 C.F.R. §300.304(c)(1) requires that assessments used for evaluation be 'used for the purposes for which the assessment or measures are valid and reliable' and administered by trained and knowledgeable personnel — relevant because the product outputs an 'AI-generated personalized learning plan' (529) and 'Monthly IEP Progress Report ... formatted for IEP meeting submission' (571). [INFERENCE] on state licensure requirements for individual cognitive assessment — varies by state and I have not checked Maryland's specific provisions (COMAR 13A.05.01); this should be confirmed with counsel.

**Recommendation**

Replace line 258 with: "Diagnostic Instruments — in development, not yet validated. Student: 52 items across 6 domains. Parent: 38 items. Staff: 24 items. These are intake and planning instruments, not psychological or educational evaluations. They are not normed, have no published reliability or validity evidence, and must not be used for eligibility, placement, or diagnosis. Validation plan: item review by licensed school psychologists (Phase 1) → cognitive interviews with 15–20 students (Phase 1) → pilot with n≥300 for factor structure and reliability (Phase 3) → measurement invariance testing across race and disability status before any cross-group comparison is reported (Phase 4)." Change milestone 771 to 'drafted and expert-reviewed', not 'validated.' Remove the digit-span, phonological-awareness and prosody-scored fluency items from the self-administered instrument, or route them explicitly to school-administered assessment, and add a disclaimer anywhere a plan or IEP-facing report is generated.

### RI-18 — Interleaving "by 43%", retrieval practice "50% greater retention", spacing "2x retention" — three real effects reported with numbers that do not come from the cited sources

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Line 461: "Interleaving Effect | Rohrer & Taylor (2007); Bjork (1994) — UCLA | Mixed-topic practice beats blocked practice for long-term retention by 43%". Line 460: "Retrieval Practice Effect | Roediger & Karpicke (2006) | Self-testing produces 50% greater retention than re-reading". Line 459: "Spaced Repetition / Forgetting Curve | Ebbinghaus (1885); Cepeda et al. (2006) | Distributed practice produces 2× retention over massed practice".

**The problem**

These are the three best-evidenced techniques in the document and all three numbers are mishandled. (a) Interleaving: Rohrer & Taylor (2007) is correctly attributed, but '43%' appears to be a percentage-point difference (the commonly reported mixed-vs-blocked delayed-test accuracies differ by roughly that many points in one experiment) reported as a percent improvement — a category error. Bjork (1994) is desirable difficulties, a framework, not an interleaving effect size. (b) Retrieval practice: '50%' is a relative restatement of one condition contrast at one delay in one experiment, presented as a general law; the general finding is that testing beats restudy on delayed tests, with magnitude varying widely by material, delay and format. (c) Spacing: Cepeda et al. (2006) synthesised 839 assessments across 317 experiments in 184 articles and its central finding is that the optimal inter-study interval scales with the retention interval — it does not report a blanket '2×'. Ebbinghaus (1885) is a single-subject nonsense-syllable study and cannot source a retention multiplier for middle-school content. The pattern matters: these effects are genuinely strong and are the correct foundation for the product; decorating them with invented precision is what will get the whole document dismissed.

**Evidence**

Cepeda, N.J., Pashler, H., Vul, E., Wixted, J.T. & Rohrer, D. (2006). "Distributed practice in verbal recall tasks: A review and quantitative synthesis." Psychological Bulletin 132(3):354–380 — "839 assessments of distributed practice in 317 experiments located in 184 articles"; key finding is ISI × retention-interval interaction — verified. Roediger & Karpicke (2006), Psychological Science 17(3):249–255 — testing beats restudy at 2-day and 1-week delays; I could NOT verify the specific 61%/40% figures in this session, so the '50%' restatement remains unverified. Rohrer & Taylor (2007), Instructional Science 35:481–498 — I could not retrieve the abstract; the '43%' figure is unverified and I would check the reported delayed-test accuracies directly. Dunlosky et al. (2013), PSPI 14:4–58 rates distributed practice and practice testing as the only two 'high utility' techniques of ten.

**Recommendation**

Replace all three with magnitude-free statements plus a tier badge. (a) "Interleaving | Rohrer & Taylor (2007); Taylor & Rohrer (2010); Brunmair & Richter (2019) meta-analysis | Mixing problem types within practice produces worse performance during practice and better performance on delayed tests than blocking. [ESTABLISHED for category learning and some math; benefits are not uniform across materials.]" (b) "Retrieval Practice | Roediger & Karpicke (2006); Rowland (2014) meta-analysis | Self-testing produces better delayed retention than restudying; magnitude varies substantially by material, delay and test format. [ESTABLISHED — one of only two techniques Dunlosky et al. (2013) rate as high utility.]" (c) "Distributed Practice | Cepeda et al. (2006), 317 experiments | Spacing study episodes beats massing them, and the optimal gap grows with how long you need to remember. [ESTABLISHED.] Ebbinghaus (1885) is the historical origin, not an effect-size source." Remove every multiplier and percentage unless it is traceable to a named table in a named paper.

### RI-21 — The artifact violates the AI-content standard it sets for itself two screens earlier

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.92 |

**What the artifact says**
> Line 118: "AI hallucination in educational content | Critical | Confidence scoring on ALL outputs; human expert review queue for score < 0.85; citations required; zero-tolerance for unverified academic claims." Line 634 repeats it verbatim as an agent safety protocol. The founder's stated principles include "evidence before claims" and "no claims of validation that has not occurred."

**The problem**

The document that declares zero tolerance for unverified academic claims contains, by this audit's count, at least nine fabricated or untraceable quantitative claims (38%, 85%, 73%, 43%, 50%, 2×, 15–20%, 40%, ES 0.8, 60–90%, 90% faster), one confabulated methodology attributed to a federal agency, one non-existent algorithm/product pairing, two or three non-existent assessment instruments, and a debunked construct embedded in a child-facing diagnostic. This is not hypocrisy; it is the predictable result of generating a document at this scale and speed without a verification pass. But it has a specific consequence for this founder: the credibility of AEOS's security posture — a real, hardened, committed test suite — rests on the claim that this team does not assert things it has not verified. A master project document that asserts a NASA methodology and a 73% district statistic undermines the one asset that distinguishes AEOS from every other ed-tech pitch. The gap between the stated standard and the delivered document is roughly total.

**Evidence**

[INFERENCE] from direct comparison of the artifact's stated standard (lines 118, 634) against the findings RI-01 through RI-20 in this audit. The count of fabricated/untraceable quantitative claims is this auditor's tally of items where the cited source demonstrably does not contain the stated number, or where no source is given and none was located.

**Recommendation**

State the gap in the document rather than letting a reviewer find it. Add to the Project Doc tab, above the Problem Statement: "Evidence status of this document: this is a design document, not a research report. As of <date> it has been audited for citation accuracy and every claim now carries an evidence tier badge. Claims we previously made and have withdrawn as unsupported: [list]. We hold ourselves to the same standard we apply to our AI outputs — zero tolerance for unverified academic claims — and this document did not meet it until this revision." Then make the standard operational: no number ships without a source and a retrieval date; no method ships with an institutional attribution unless that institution published it; the 'citations required' rule in line 118 applies to human-authored marketing and design documents, not only to model outputs.

### RI-15 — "Mind Mapping — Buzan (1970) — validated UCL" is wrong on the date, on the institution, and on the word 'validated'

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.86 |

**What the artifact says**
> Line 502: "Mind Mapping | Buzan (1970) — validated UCL | Best for: Concept relationships + brainstorm".

**The problem**

Three errors in six words. (1) Date: Buzan's mind-mapping work dates to the mid-1970s, usually cited as Buzan (1974, Use Your Head) — 1970 does not correspond to a Buzan publication. (2) "validated UCL": no UCL (University College London) validation study of Buzan mind mapping exists, and the phrase appears to be ambient marketing copy absorbed as a citation. (3) "validated" overstates what the evidence supports. The meta-analytic literature that is usually cited for 'mind mapping' is mostly about *concept maps* (Novak's hierarchical, labelled-link diagrams), not Buzan's radial mind maps — Schroeder et al. report a pooled benefit for concept/knowledge mapping that falls substantially when the comparison condition is students writing their own outline or text. Direct trials of Buzan-style radial maps are few, small, and mixed; at least one medical-education trial found no significant short-term recall or critical-thinking advantage over standard note-taking, and a 2026 meta-analysis in residency training rated overall certainty of evidence as 'very low' under GRADE. Buzan's own theoretical claim (that radial maps mirror the brain's 'radiant thinking') has no controlled support.

**Evidence**

Buzan, T. (1974). Use Your Head. BBC Books. Lee, Y.-J. et al. (2023), "Effects of mind mapping-based instruction on student cognitive learning outcomes: a meta-analysis," Asia Pacific Education Review (k=21) — positive vs traditional instruction, moderated by subject and level. 2026 systematic review/meta-analysis of mind mapping vs lecture-based learning in Chinese residency training (Front. Med.): "GRADE assessment showed that the overall certainty of evidence was very low." Schroeder et al. concept-mapping meta-analysis (g≈0.58 overall; g≈0.194 vs self-generated text/outline comparison) — reported via secondary source, exact figures unverified in this session. No UCL validation study located.

**Recommendation**

Replace with: "Mind Mapping | Buzan (1974) | Best for: concept relationships and brainstorming. [EMERGING: most meta-analytic support is for hierarchical *concept maps* rather than Buzan's radial maps, and the advantage shrinks when compared against students writing their own outlines. Evidence certainty for radial mind maps specifically is low.] We offer it as one of six formats because format choice supports engagement and UDL multiple means of expression, not because it outperforms the alternatives." Delete "validated UCL" and never use the bare word 'validated' without naming the study.

### RI-16 — "Cornell Notes — Pauk (1962)" is attributed correctly but presented as research-validated when the experimental base is thin and format is not the active ingredient

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.87 |

**What the artifact says**
> Line 501: "Cornell Notes | Pauk (1962) — Cornell University"; the section header (line 498) is "6 Note-Taking Methods (Research-Validated)".

**The problem**

The attribution is right — Walter Pauk introduced the system in How to Study in College (1st ed., 1962) — but Pauk (1962) is a study-skills textbook, not an experimental validation. The header 'Research-Validated' applies to all six methods and is not supportable for any of them individually. What the note-taking literature actually supports is narrower and more useful: the benefit comes predominantly from *reviewing* notes rather than from the act or the format of taking them, and the Cornell system's cue column and summary are valuable precisely because they force review and self-testing — i.e., Cornell is a delivery vehicle for retrieval practice, which is the construct with real evidence. Head-to-head studies favouring Cornell over verbatim or outline notes exist but are small, often EFL or single-classroom, and a 2025 four-arm randomized comparison reports no a priori power analysis and a 5-week intervention. There is no meta-analysis isolating Cornell against other formats.

**Evidence**

Pauk, W. (1962). How to Study in College. Houghton Mifflin. Kobayashi's and related note-taking meta-analyses find that taking notes alone does little for recall but reviewing one's notes produces clearly superior recall. Zhang et al. (2024), "The effectiveness of note taking through exposure to L2 input: a meta-analysis," Studies in Second Language Acquisition (g = 0.56 [0.24, 0.88]) — does not separate Cornell from other formats and explicitly calls for such comparisons. Small head-to-head studies (Cornell vs verbatim vs outline; Cornell vs REAP) favour Cornell but are underpowered.

**Recommendation**

Change the section header (line 498) from "6 Note-Taking Methods (Research-Validated)" to "6 Note-Taking Formats — Evidence Varies by Format (see tier badge on each)." Replace the Cornell entry with: "Cornell Notes | Pauk (1962), How to Study in College — a study-skills textbook, not an experimental study. [EMERGING: small head-to-head studies favour Cornell over verbatim notes; no meta-analysis isolates it. What IS well established is that reviewing notes, not the format of taking them, drives the benefit — and Cornell's cue column is a retrieval-practice device. That is why we teach it.]" Add the same honest framing for Sketchnoting (Rohde 2013 is a trade handbook, not research), Flow Notes (Young 2011 is a self-published method, not research), Zettelkasten (Luhmann 1981, 'Kommunikation mit Zettelkästen', is a sociologist's essay on his own practice, not a learning study) and Outline (Ausubel 1960 is about advance organizers, which is a related but distinct construct — using it to source the outline method is a misattribution).

### RI-19 — Two named assessment instruments appear to not exist: "Learning Science Literacy Tool (UVA, 2023)" and "African-Centered Pedagogy Assessment (Hilliard, 1997)"

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.84 |

**What the artifact says**
> Line 306: "Sources: Saphier Skillful Teacher (2018), UDL Competency Guide (CAST 2020), African-Centered Pedagogy Assessment (Hilliard, 1997), Learning Science Literacy Tool (UVA, 2023)."

**The problem**

Three of these four are doubtful as named instruments. (1) "Learning Science Literacy Tool (UVA, 2023)": no such instrument surfaced in search; the phrase has the shape of a plausible-sounding invention. (2) "African-Centered Pedagogy Assessment (Hilliard, 1997)": Hilliard's SBA: The Reawakening of the African Mind (1997) is a book of essays, not an assessment instrument; no instrument by that name is known. (3) "UDL Competency Guide (CAST 2020)": CAST's product is the UDL Guidelines; version 2.2 preceded version 3.0, which CAST released on 30 July 2024. There is no CAST 2020 'Competency Guide' I can locate, and the 2020 date corresponds to no CAST Guidelines release. Only Saphier, Haley-Speca & Gower, The Skillful Teacher (7th ed., 2018) is solid. A staff-facing certification that will be sold to MCPS for CEU credit (line 394, 725) cannot rest its framework on instruments that cannot be located.

**Evidence**

CAST UDL Guidelines 3.0 released 30 July 2024 (udlguidelines.cast.org/more/about-guidelines-3-0/; confirmed by UCDenver TIPS and ASC/OSU) — verified; prior version was 2.2. Hilliard, A.G. III (1997). SBA: The Reawakening of the African Mind. Makare Publishing — a book, not an instrument. "Learning Science Literacy" + University of Virginia: search returned zero results. [INFERENCE] absence of search results is not proof of non-existence; I would check UVA School of Education and Human Development project pages and the ETS/ERIC instrument databases before stating flatly that it does not exist.

**Recommendation**

Replace line 306 with only what can be cited: "Sources: Saphier, Haley-Speca & Gower, The Skillful Teacher (7th ed., 2018); CAST UDL Guidelines 3.0 (released 30 July 2024). Our African-centered pedagogy competencies are drawn from Hilliard (1997, SBA: The Reawakening of the African Mind), Ladson-Billings (1995) and Gay (2018) — these are theoretical and practice frameworks, not published assessment instruments, and our competency rubric is original work that has not been validated. Our learning-science competency items are original and unvalidated." Delete "Learning Science Literacy Tool (UVA, 2023)" and "UDL Competency Guide (CAST 2020)" unless a retrievable citation can be produced. Update every UDL reference to 3.0 with the correct July 2024 date (line 264 already says 3.0, which is correct).

### RI-20 — Cummins (1979) is cited for "CALP takes 5–7 years" — a figure that comes from different studies, and the inference drawn from it does not apply to this population

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> Line 167: "Cummins (1979): Academic language (CALP) takes 5–7 years to develop — never explicitly taught." Line 270, item 3.4: "Academic vocabulary — CALP level (Cummins, 1979) in each content area."

**The problem**

Two issues. (1) Attribution: Cummins (1979, Working Papers on Bilingualism 19:121–129, and the 1980 TESOL Quarterly paper) introduced the BICS/CALP distinction; the specific 5–7 year estimate for academic language proficiency derives from later empirical work on second-language learners — principally Collier (1987, TESOL Quarterly 21:617–641) and Cummins' own later syntheses drawing on Collier and Thomas & Collier. Citing the 1979 paper for the number is a misattribution. (2) Applicability: the 5–7 year figure describes the time for *English language learners* to reach grade-level academic English proficiency relative to native-speaker norms. The artifact applies it to US-born, English-dominant Black middle schoolers with literacy deficits — a different population with a different developmental picture. The underlying point (academic language is a real barrier and is rarely taught explicitly) is sound and well supported; the specific number and its source are not, and applying an ELL timeline to non-ELL students could lead to inappropriate instructional decisions.

**Evidence**

Cummins, J. (1979). "Cognitive/academic language proficiency, linguistic interdependence, the optimum age question and some other matters." Working Papers on Bilingualism 19:121–129. Collier, V.P. (1987). "Age and rate of acquisition of second language for academic purposes." TESOL Quarterly 21(4):617–641 — the primary source of the multi-year estimate. [EMERGING] the 5–7 year figure has been contested and varies widely by prior schooling, L1 literacy and program model. Scarborough (2001) Reading Rope — correctly cited at line 167 and 270.

**Recommendation**

Replace with: "Academic language is a distinct register from conversational language (Cummins, 1979, BICS/CALP) and is rarely taught explicitly in content instruction. [ESTABLISHED as a construct.] Estimates that English learners need roughly 5–7 years to reach grade-level academic English come from Collier (1987) and Thomas & Collier, not from Cummins (1979), and describe English learners — not English-dominant students with literacy gaps, which is our primary population. We cite the construct, not the timeline. The directly relevant evidence for our students is Scarborough's Reading Rope (2001): comprehension requires both word recognition and language comprehension, and test prep that addresses neither will not transfer."

### RI-22 — "Child Liberation Studies ... 40% greater intrinsic motivation" attributes a fabricated statistic to three philosophers

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.91 |

**What the artifact says**
> Line 168: "John Holt (1964): Schools create anxiety by stripping children of agency. Peter Gray (2013): Self-directed learning produces 40% greater intrinsic motivation. Freire (1968): Compliance-based education produces oppression." Repeated at line 466.

**The problem**

Holt (1964, How Children Fail), Gray (2013, Free to Learn) and Freire (Pedagogia do Oprimido, 1968; English 1970) are correctly dated and correctly characterized as thinkers — but none reports a 40% intrinsic-motivation effect. Gray's book is a popular synthesis and argument, not a trial; it reports no such statistic. There IS a real empirical literature behind the underlying idea: self-determination theory (Deci & Ryan) has a large body of evidence that autonomy support increases intrinsic motivation, including meta-analyses of autonomy-supportive teaching. Citing that literature would make the point properly. Attaching '40%' to Peter Gray does not.

**Evidence**

Gray, P. (2013). Free to Learn. Basic Books — a trade book of argument and anecdote; no controlled trial, no percentage. Holt, J. (1964). How Children Fail. Pitman. Freire, P. (1968/1970). Pedagogy of the Oppressed. Deci, E.L. & Ryan, R.M. self-determination theory; see Su & Reeve (2011), Educational Psychology Review 23:159–188, meta-analysis of autonomy-supportive teaching interventions, and Ryan & Deci (2000), American Psychologist 55:68–78. [INFERENCE] I did not verify the Su & Reeve pooled effect in this session — cite it only after checking the reported value.

**Recommendation**

Replace with: "Agency and Autonomy in Learning | Holt (1964); Freire (1968); Gray (2013) for the philosophical case; Deci & Ryan's self-determination theory and meta-analyses of autonomy-supportive teaching for the empirical case. [Philosophy: EXPERT-OPINION. Autonomy support → intrinsic motivation: ESTABLISHED, moderate effects.] We do not have a percentage and the thinkers we cite did not report one."

### RI-23 — "PhD-Level" is used as a quality descriptor eleven times and functions as an unverifiable credential claim

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> "PhD-Level Learning Science Platform" (34), "PhD-Level Gap Analysis" (159), "PhD-Level Diagnostic Assessments" (258), "PhD-Level Certification Framework" (330), "PhD-Level Certification Exam" (341), "PhD-Level Course Architecture" (454), "PhD-Level Exam Structure" (426), "Paraeducator + Teacher PhD Certification" (215), "compile 60-source PhD bibliography" (137), header badge "PhD Certified" (839).

**The problem**

"PhD-Level" has no referent. It is not a credential, not an accreditation, not a standard. Used on a certification product it is closer to a credential claim than a quality adjective — and the header badge "PhD Certified" (839) crosses the line: it states that something is PhD certified, which nothing in this document is. For a product sold to paraeducators at $299 and teachers at $499 (725, 726) with CEU and graduate-credit claims, this is the kind of language that attracts attention from state credentialing bodies and from the universities named as prospective partners (line 440: Howard, Morgan State, UMCP — named as targets, which risks reading as an existing relationship). The substance of the certification tracks may well be rigorous; the label does no work except to borrow unearned authority, and it is the first thing a skeptical reviewer will attack.

**Evidence**

[INFERENCE] No accrediting body, state education agency, or credentialing standard defines 'PhD-level' as a descriptor for a non-degree certificate. CEU eligibility (claimed at 394, 419, 725, 726) is governed by state and district approval processes, and graduate credit requires an executed articulation agreement with the awarding institution — line 440 says 'Target partners', which is honest, but the surrounding 'PhD-Level' framing is not.

**Recommendation**

Strike 'PhD-Level' and 'PhD Certified' everywhere. Replace with specific, checkable descriptors: '80-hour paraeducator certificate', '120-hour educator professional learning certificate', 'graduate-level' only if and when an articulation agreement exists. Replace the header badge 'PhD Certified' with 'Evidence-Graded'. Change line 440 to: 'University partnership track: not yet established. We intend to approach Howard University, Morgan State and UMCP. No agreement is in place and no graduate credit is currently available.' Change CEU claims to: 'We intend to seek CEU approval; not yet approved.'


---

## What is missing and should be added

### Visible evidence-tier badge on every claim, in the product and in this document   `ESTABLISHED`

**Why it matters.** The artifact's failure mode is that a fabricated number and a meta-analytic finding render identically — same font, same card, same authority. A tier badge makes the distinction structural rather than a matter of the author's memory, and it is the only mechanism that scales to a team and to AI-generated content. It also converts the project's weakness into a differentiator: no competitor in this space grades its own claims.

**What to build.** Five tiers rendered as a coloured chip next to every research claim, in the app and in all collateral: ESTABLISHED (replicated meta-analysis or systematic review, or primary legal/statutory text) — green; EMERGING (some empirical support, contested or thin) — blue; EXPERT-OPINION (credible authority, not empirically settled) — amber; INFERENCE (our reasoning from the above, labelled as ours) — grey; SPECULATION (plausible, unsupported, stated as such) — outlined. Every badge is clickable and opens the source: author, year, venue, and either a DOI or a retrieval date. A claim with no source cannot be rendered — the component throws in development and renders a visible 'UNSOURCED' placeholder in staging. Store claims in a `claims` table (id, text, tier, source_citation, doi_or_url, retrieved_at, reviewer, reviewed_at) and reference claims by id from content; never inline prose research assertions in components.

**Evidence.** Model: GRADE (Guyatt et al., 2008, BMJ 336:924–926) uses exactly this pattern — four certainty levels attached to every recommendation — and is the dominant standard in clinical guidelines. The 2026 mind-mapping meta-analysis cited in RI-15 reports GRADE certainty as 'very low', which is precisely the information this artifact currently hides.

### A marketing claim rule: only ESTABLISHED tier may appear in anything a customer sees before purchase   `INFERENCE`

**Why it matters.** The artifact's most dangerous claims (90% faster, 60–90% speed gain, ES 0.8, 73% of MCPS families) are all in acquisition-facing surfaces: the problem statement, the gap analysis, the module titles, the competitive chart. These are the claims that create FTC substantiation exposure and that destroy district trust. A tier-gated marketing rule is a single, enforceable line.

**What to build.** Written policy, enforced by a lint rule in CI over marketing copy files and the claims table: (1) Only ESTABLISHED-tier claims may appear in pricing pages, module titles, pitch decks, grant narratives or district presentations. (2) No quantified performance claim — any number with %, ×, or a point estimate — may appear in marketing at all, regardless of tier, unless it is a citation of a published study rendered with its full source and its confidence interval. (3) No claim about MindUnlock's own effectiveness may be made until pilot data exists; until then the permitted phrasing is 'designed around' and 'we are measuring whether.' (4) No institution's name (NASA, a university, a district, CAST) may appear as a source unless that institution published the thing cited. Route every exception through a named reviewer who signs off in the claims table.

**Evidence.** FTC Act §5 and the FTC's advertising substantiation policy require competent and reliable evidence, typically scientific evidence for health/efficacy claims, at the time an express performance claim is made. [INFERENCE] on the precise application to an ed-tech subscription — I have not had this reviewed by counsel and the ed-tech enforcement record is thinner than the health-claims record; confirm with counsel before relying on the specific standard.

### A neuromyth blocklist enforced in code and in content review   `ESTABLISHED`

**Why it matters.** VARK got into the diagnostic (RI-05) because nobody had a list of things that are not allowed in. A blocklist is cheaper than relitigating each one, and it protects against the specific risk that an AI content agent (lines 138–141 instruct agents to draft the diagnostic and the module guides) regenerates a debunked construct from training data.

**What to build.** A versioned deny-list with a one-line reason and a citation for each entry, checked by a CI grep over content and by a pre-publish prompt constraint on every content-generating agent: learning styles / VARK / modality matching (Pashler et al., 2008); left-brain/right-brain dominance; the 10% of the brain claim; the learning pyramid / Dale's Cone retention percentages (no empirical source; the numbers are fabricated); 'digital natives'; Brain Gym; multiple intelligences as an instructional-matching prescription; the Mozart effect; 'we remember 10% of what we read, 20% of what we hear'; speed reading with maintained comprehension (Rayner et al., 2016). Each entry names an approved replacement construct so the content writer has somewhere to go — e.g. VARK → 'UDL multiple means of representation, offered to all students rather than assigned per student.'

**Evidence.** Dekker, Lee, Howard-Jones & Jolles (2012), "Neuromyths in education: prevalence and predictors of misconceptions among teachers," Frontiers in Psychology 3:429 — found ~49% of UK/Dutch teachers endorsed the 10% myth and a large majority endorsed learning styles. Pashler et al. (2008), PSPI 9:105–119. Rayner et al. (2016), PSPI 17:4–34.

### A machine-checkable claims register as the single source of truth, replacing inline prose citations   `INFERENCE`

**Why it matters.** There are roughly forty distinct research assertions scattered across 859 lines of JSX string literals. They cannot be audited, cannot be updated when a field moves (as growth mindset and stereotype threat have), and cannot be reused across the app, the certification content and the grant narrative without drift. Every finding in this audit required reading prose to find a citation. That does not scale and it is why the errors accumulated.

**What to build.** A `claims.yaml` (or Supabase table, reusing AEOS's existing schema conventions rather than a new store) with one record per assertion: id, claim_text, tier, sources[{authors, year, title, venue, doi}], effect_size (nullable, with CI), population (who the evidence is about), applicability_note (how far it transfers to Black neurodivergent middle schoolers — often the honest answer is 'not established'), last_verified, verifier. Content references claims by id. A CI job fails the build on any claim older than 12 months without re-verification, any claim with tier ESTABLISHED and no DOI, and any effect_size without a CI. Seed it with the ~40 claims in this artifact, each re-graded per this audit.

**Evidence.** [INFERENCE] from the structure of the artifact and standard practice in systematic-review data extraction (Cochrane Handbook ch.5, data collection forms). The specific schema is this auditor's proposal, not a published standard.

### A real competitive-scoring rubric to replace the "Meets Our Needs" percentages   `ESTABLISHED`

**Why it matters.** The current chart (RI-14) is the artifact's most reviewer-hostile element: round numbers, self-serving dimensions, a factual error about the top-scoring competitor. A defensible rubric costs two days and converts the weakest slide into a credible one.

**What to build.** Ten dimensions derived from parent and student interviews (not from the MindUnlock roadmap), each with written 0–3 behavioural anchors and an explicit weight summing to 1.0. Candidate dimensions: accessibility for a student reading two grades below level; setup time to first value for a parent with no study-skills background; cost at the household level; offline capability; IEP accommodation configurability; evidence base published by the vendor; crisis/safety handling; cultural representation in content; data practices for minors; teacher/para workflow fit. Two independent raters, report Cohen's κ or percent agreement, record evaluation date and product version, publish the filled sheet. Report results as weighted scores with the sheet attached — never as a bare percentage.

**Evidence.** This is literally what Behaviorally Anchored Rating Scales are for (Smith & Kendall, 1963) — the technique the artifact misattributed to NASA. Using BARS here, correctly cited, would redeem the term and give the founder a genuine methodological hook.

### A pre-registered pilot protocol for the 10-family cohort, written before enrollment   `ESTABLISHED`

**Why it matters.** The Phase 1 pilot (lines 98, 771–772) is the only place in the roadmap where real evidence can be generated, and it is currently specified only by vanity KPIs (enrollment count, completion rate, days of app use). Without pre-specified outcomes the pilot can produce a narrative but cannot produce a claim — and the founder's own principle is completion > validation, which means the pilot must be able to validate something.

**What to build.** A short pre-registration (OSF, free, timestamped) filed before the first family enrolls, specifying: primary outcome (e.g. change in a published test-anxiety measure — the Spielberger TAI or the Children's Test Anxiety Scale — from baseline to week 12), secondary outcomes, the measurement schedule, who administers, the analysis plan including how missing data and dropout are handled, and an explicit statement that n=10 families is a feasibility and acceptability study, not an efficacy study, and will not support an effectiveness claim whatever it shows. Commit to publishing the result regardless of direction. Add a line to the Phase 1 KPI list: 'pre-registration filed before first enrollment.'

**Evidence.** Thabane et al. (2010), "A tutorial on pilot studies: the what, why and how," BMC Medical Research Methodology 10:1 — pilot studies should test feasibility, and should not be analysed or reported as efficacy trials. Eldridge et al. (2016), CONSORT extension for pilot and feasibility trials, BMJ 355:i5239.

### An IRB/human-subjects determination before any pilot data is collected on minors   `INFERENCE`

**Why it matters.** The artifact plans to collect diagnostic, anxiety, behavioural and IEP data from neurodivergent minors (lines 98, 529, 571, 639) and to publish results (line 423 mentions 'Action Research Methodology (IRB-compliant)' as a module, implying awareness, but no IRB step appears in the roadmap). If this data is ever used in a publication, a grant report, or a district evaluation, retroactive IRB approval is not available. Collecting first and asking later forecloses the research pathway the whole document aspires to.

**What to build.** Before pilot enrollment: (1) obtain an IRB determination — an independent IRB for unaffiliated investigators, or a university partner's IRB if an academic collaborator is recruited; (2) separate consent (parent/guardian) and assent (student) documents written at the appropriate reading level; (3) a data-use statement distinguishing operational product data from research data, with the research pathway opt-in; (4) a named data custodian and a retention/deletion schedule; (5) a conflict-of-interest disclosure, given that the founder is an MCPS employee recruiting MCPS families to a commercial product he owns — this needs explicit review under MCPS employee ethics rules before any recruitment, independent of the IRB.

**Evidence.** 45 C.F.R. §46 (the Common Rule), Subpart D (additional protections for children). 45 C.F.R. §46.102(l) definition of research; §46.408 on assent. [INFERENCE] on MCPS-specific employee conflict-of-interest rules — I have not reviewed MCPS Board policy or the Maryland Public Ethics Law provisions applicable to local school system employees; this must be checked directly and is potentially the highest-consequence item in this list for the founder personally.

### A "what we do not know" panel, published in the product and the pitch   `EXPERT-OPINION`

**Why it matters.** The artifact has ten tabs of assertions and zero statements of uncertainty. Reviewers, districts and grant panels read confidence without caveats as naivety or as sales. A published limitations panel inverts that read, and it is cheap because the content already exists — it is this audit's findings, restated as the founder's own.

**What to build.** A short, permanent section: 'What we don't know yet.' Entries, each one sentence: we have not validated our diagnostic instruments; we have no outcome data on MindUnlock; the culturally-relevant-pedagogy evidence we rely on comes from high-school ethnic studies in one district and may not transfer to middle school; the test-anxiety intervention literature is thin for Black and neurodivergent adolescents specifically; growth-mindset and stereotype-threat effects are smaller than early reports; we do not know whether family co-learning improves student outcomes, which is the central bet of the product. Each with a tier badge and a line on what study would settle it.

**Evidence.** [EXPERT-OPINION] Standard practice in systematic reviews (the 'limitations' section is a PRISMA 2020 checklist item, #23) and increasingly in preregistered reports. The product application is this auditor's recommendation.

### Replace the fabricated NASA scheduling method with a correctly-cited executive-function scaffolding basis   `INFERENCE`

**Why it matters.** Removing the NASA attribution (RI-01) leaves a feature with no stated rationale, which invites the next fabrication. The feature itself — 15-minute blocks, task decomposition, student-built schedules — has a real and well-matched evidence base that is stronger than the invented one.

**What to build.** Re-source the scheduler to: Dawson & Guare, Executive Skills in Children and Adolescents (3rd ed., 2018) and Smart but Scattered, for the task-decomposition and externalized-planning approach; the ADHD organizational-skills training literature (e.g. Evans, Owens & Bunford's evidence-based-treatment reviews in J. Clinical Child & Adolescent Psychology) for school-based organizational interventions with empirical support; Zimmerman's self-regulated learning cycle (forethought–performance–self-reflection) for the student-built framing; and implementation-intention research (Gollwitzer) for the if-then planning element. State plainly: 'Time-blocking and task decomposition are standard, evidence-supported executive-function supports. Our specific implementation is unvalidated.' Keep the student-authorship design — it is the best idea in the document — and justify it from self-determination theory, not from a made-up agency method.

**Evidence.** Dawson, P. & Guare, R. (2018). Executive Skills in Children and Adolescents, 3rd ed. Guilford. Evans, S.W., Owens, J.S. & Bunford, N. (2014), "Evidence-based psychosocial treatments for children and adolescents with ADHD," J. Clinical Child & Adolescent Psychology 43:527–551 — organizational-skills interventions among the supported school-based approaches. Zimmerman, B.J. (2002), Theory Into Practice 41:64–70. [INFERENCE] on exactly which organizational-skills trials best match a 15-minute-block scheduler — I did not verify specific trials of time-blocking per se in this session.

### A citation verification pass as a required gate before any document leaves the building   `EXPERT-OPINION`

**Why it matters.** Every error in this audit would have been caught by one person spending four hours with a search engine. The absence of that pass is the root cause, not any individual claim. Making it a gate is the only durable fix, and it is the direct analogue of the security mutation test suite AEOS already runs — the founder already believes in this pattern, applied to code.

**What to build.** A checklist run against any outward-facing document (pitch, grant, district deck, module content, marketing page), signed and dated in the claims register: (1) every named person + year resolves to a retrievable publication; (2) every number is located in a named table/figure/page of a named source, or is deleted; (3) every institutional attribution is verified against that institution's own site; (4) every product/technology claim is verified against that product's current official documentation (this would have caught Anki/SM-18); (5) every absolute negative ('no program exists', 'first of its kind') is softened to 'we have not found' unless a documented search backs it; (6) every effect size carries its CI and its population. Treat an unverified claim as a build-breaking defect, with the same severity as a failing security mutation test.

**Evidence.** [EXPERT-OPINION] Analogous to editorial reference-checking in journals and to the Cochrane data-extraction double-check. The specific gate design is this auditor's proposal; its justification is empirical — this audit found ~15 defects a single verification pass would have caught.

### Re-cite the African-centered foundation honestly: theory as theory, outcome evidence as outcome evidence   `ESTABLISHED`

**Why it matters.** The ES-0.8 fabrication (RI-04) is the finding most likely to be read as bad faith by the very scholars and community the project depends on — and the artifact itself identifies 'cultural appropriation of African-centered content' as a High risk (line 120) with 'African-centered scholars as PAID co-developers' as the mitigation. Those scholars will be the first readers to notice that Hilliard, Nobles and Asante have been credited with an effect size none of them reported. Fixing this protects the partnership the project cannot proceed without.

**What to build.** Split the citation into two layers everywhere it appears (lines 169, 465, 485, 312, 401). Layer 1 — Philosophical/epistemological foundation [EXPERT-OPINION]: Asante (1987), Hilliard (1997), Nobles (2006), Akbar (1994), Kambon (1992), Myers (1988), Boykin (1994). These ground the design; they report no outcomes and we cite no numbers from them. Layer 2 — Outcome evidence for culturally relevant and ethnic-studies curricula [ESTABLISHED, with scope limits]: Ladson-Billings (1995); Dee & Penner (2017, AERJ); Bonilla, Dee & Penner (2021, PNAS); Aronson & Laughter (2016, RER) as a qualitative synthesis. State the scope limits explicitly: high-school, one district, RD-local estimates, not yet replicated at middle-school level. Then put this split in front of the community advisory board (line 120) before publication and ask them to check it.

**Evidence.** Dee & Penner (2017), AERJ 54(1):127–166 and Bonilla, Dee & Penner (2021), PNAS 118(37):e2026386118 — both verified. Ladson-Billings, G. (1995), "Toward a theory of culturally relevant pedagogy," AERJ 32:465–491. Aronson, B. & Laughter, J. (2016), Review of Educational Research 86:163–206 — a synthesis, not a meta-analysis; do not cite a pooled effect size from it.

### A disclaimer and scope boundary wherever the product touches IEP, diagnosis or crisis   `INFERENCE`

**Why it matters.** The app auto-parses IEP PDFs, auto-configures accommodations, generates 'Monthly IEP Progress Report ... formatted for IEP meeting submission' (line 571), and detects crisis/self-harm (119, 572, 635). Each of these is a point where an unvalidated instrument or an AI inference could enter a child's legal educational record or a safety decision. The artifact names the risks but states no scope boundary.

**What to build.** Explicit, user-visible scope statements at each touchpoint: (1) Diagnostics — 'not a psychological or educational evaluation; not for eligibility, placement or diagnosis; not normed.' (2) IEP reports — 'generated from app usage data only; informational input for the IEP team; not a progress report under 34 C.F.R. §300.320(a)(3) and does not substitute for the school's reporting.' (3) Accommodation auto-configuration — a human confirmation step before any IEP-derived setting takes effect, with the parsed values shown to a parent or case manager for approval (the artifact's own failure-handling table at line 637 says 'human review before any change applied' — make it a product requirement, not a risk-register aspiration). (4) Crisis — 'this is not a crisis service'; display 988 and local resources; define the human escalation path and its SLA; never leave an AI as the terminal responder.

**Evidence.** IDEA 34 C.F.R. §300.304(c)(1) (assessments valid for the purpose used; administered by trained personnel); §300.320(a)(3) (periodic progress reporting is the IEP team's and the agency's obligation). FERPA 34 C.F.R. Part 99 and COPPA 16 C.F.R. Part 312 for the data side, which the artifact already addresses at lines 117, 691. [INFERENCE] on whether an AI-generated usage report would be treated as an education record once shared with the IEP team — likely yes, which has retention and access consequences; confirm with counsel.


---

## Open questions

- Rohrer & Taylor (2007), Instructional Science 35:481-498 — I could not retrieve the abstract or results in this session. The '43%' in line 461 needs to be checked against the paper's reported delayed-test accuracies; my working hypothesis is that it is a percentage-point difference restated as a percent improvement, but that is unverified.
- Roediger & Karpicke (2006), Psychological Science 17(3):249-255 — I could not confirm the specific 1-week retention percentages (commonly cited as 61% vs 40%) in this session. The '50% greater retention' in line 460 should be checked against Experiment 1's reported figures before it is either kept or discarded.
- Anki's current official documentation (docs.ankiweb.net) could not be fetched — that host is outside this session's allowed network domains. The exact current Anki version, FSRS revision (5 vs 6), and whether the legacy SM-2 scheduler remains selectable should be confirmed against Anki's own manual before publishing the corrected RI-02 wording.
- BLS OEWS 25-9045 (Teaching Assistants, Except Postsecondary) national employment total — I retrieved the Occupational Outlook Handbook projections and wage data but not the employment base. The '1.3M paraeducators' TAM figure needs the actual OEWS or NCES instructional-aide FTE number with a retrieval date.
- 'Learning Science Literacy Tool (UVA, 2023)' returned zero search results. Before stating flatly that it does not exist, check UVA School of Education and Human Development project pages, ERIC, and the ETS instrument database. Same for any CAST publication titled 'UDL Competency Guide' dated 2020.
- Does MCPS or MSDE publish any family-survey statistic on parent academic confidence or content knowledge? If one exists, the 73% claim in line 165 could be replaced with a real figure rather than deleted. Check MCPS annual family engagement survey reports and the Maryland Report Card family-survey items.
- Is there any published stereotype-threat meta-analysis specific to Black American students, as opposed to the schoolgirl/math literature? A PLOS ONE protocol for one was registered; whether it has been completed and what it found would materially change how RI-12 should be worded.
- Yeager et al. (2019), Nature 573:364-369 — I did not independently verify the National Study of Learning Mindsets GPA point estimate or its subgroup pattern in this session. The exact magnitude should be checked before it appears in the corrected line 463.
- MCPS employee conflict-of-interest and outside-employment rules, and the Maryland Public Ethics Law provisions applicable to local school system employees: what is required before an MCPS employee recruits MCPS families into a commercial product he owns, and before presenting that product to MCPS district leadership (line 777)? This is outside my lens but is the highest-consequence unresolved question in the artifact for the founder personally.
- Does an articulation agreement or even a preliminary conversation exist with Howard University, Morgan State or UMCP (line 440)? The document says 'Target partners', which is honest, but the surrounding 'graduate credit' and 'PhD-Level' framing will be read as an existing relationship. The distinction needs to be unambiguous in anything shown to a district or a grant panel.
- Who is the named accountable reviewer for research claims? Every recommendation in this audit presumes someone signs off. If that person is the founder alone, the verification gate will fail under time pressure the same way it just did. An external reviewer — an MCPS school psychologist, a university collaborator, or a paid methodologist — is the structural fix, and the choice of that person is a decision only the founder can make.

