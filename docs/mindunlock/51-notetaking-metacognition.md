# Note-taking and metacognition

> A replacement specification for the artifact’s note-taking and metacognition content, built on the actual literature.

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

The artifact's two most load-bearing learning-science claims — "6 Note-Taking Methods (Research-Validated)" (line 498) and "African-Centered Metacognitive Science" (line 485) — are the weakest content in the document, and they are weak in a specific, fixable way: the artifact selected methods by cultural familiarity rather than by evidence, and treated metacognition as vocabulary to be taught rather than monitoring accuracy to be measured and corrected.

On note-taking: all six methods are sourced to trade books and popular authors — a 1962 study-skills textbook (Pauk), a 1970 popular-psychology brand (Buzan, falsely tagged "validated UCL"), a 2013 design handbook (Rohde), a self-help blog author (Young 2011), a German sociologist's 1981 essay on his filing cabinet (Luhmann), and a misattribution of Ausubel's advance organizers to the outline method. Meanwhile the two interventions with the strongest evidence for *exactly this population* — guided/partial notes (an established special-education practice) and Boyle's Strategic Note-Taking for middle-school students with LD in science — are absent entirely. The artifact also picked mind mapping over concept/knowledge mapping, which is the better-evidenced cousin (Nesbit & Adesope 2006; Schroeder et al. 2017, g = 0.58). And it never addresses that its product is mobile-first and typing-based despite Mueller & Oppenheimer (2014) being the most famous finding in this literature — a finding whose conceptual-recall advantage failed to replicate twice (Morehead et al. 2019; Urry et al. 2021).

On metacognition: Flavell (1979) appears twice and the framework stops there. There is no Nelson & Narens monitoring/control architecture, no judgments of learning, no calibration measurement, and — most damagingly — no SRSD (Graham & Harris), which is arguably the best-evidenced metacognitive intervention in all of special education and is a perfect fit for this population. The EEF's metacognition guidance report, the strongest cost-effectiveness argument the founder could put in front of MCPS (+8 months, very low cost), is missing — and its central caveat condemns the artifact's own design: EEF explicitly warns against standalone "learning to learn" sessions, which is precisely what twelve decontextualised modules are.

The product's central design risk — AI writing the student's notes — is named nowhere, despite the Study Lab shipping an "AI note feedback and knowledge gap finder" and the Tutor Agent outputting "note feedback (gaps + improvements)."

---

## Findings

### NT-01 — Guided/partial notes — the highest-yield note-taking intervention for this exact population — is absent

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Line 498: "📝 6 Note-Taking Methods (Research-Validated)" — the six are Cornell, Mind Mapping, Sketchnoting, Outline, Flow Notes, Atomic/Zettelkasten. Guided notes appear nowhere in the artifact. Para cert Domain 4 (line 400): "Note-Taking & Study Skills Instruction — 6 evidence-based methods, metacognitive coaching, study system design, 90% faster study facilitation".

**The problem**

Guided notes (teacher-prepared skeletal handouts with strategic blanks the student completes during instruction) is a long-standing evidence-based practice in special education, with the strongest and most consistent note-taking evidence for students with disabilities. The artifact targets neurodivergent grade 6-8 students with literacy deficits, working-memory limits and EF deficits (its own Domain 2 and Domain 3 diagnostics say so) — the precise profile for which unsupported open note-taking fails and guided notes succeed. Teaching six open-format capture methods to students who, per the artifact's own Domain 2.1 diagnostic, have constrained working memory is a direct mismatch between the learner profile the product diagnoses and the intervention it prescribes. This is the single largest evidence omission in the note-taking section.

**Evidence**

Konrad, Joseph & Eveleigh (2009), meta-analytic review of guided notes, Education and Treatment of Children — note this review included only five peer-reviewed studies. A later K-12 meta-analysis (ERIC EJ1001064, "Impact of Guided Notes on...") reports effects by publication type: d = 0.940 (peer-reviewed), d = 1.293 (dissertations), d = 1.486 (master's theses) — I could not retrieve the full PDF because files.eric.ed.gov does not resolve in this session's network settings, so the POOLED overall effect size is UNVERIFIED and should be read from the primary article before quoting. Heward's programme of research on guided notes/active student responding is the originating line. The claim "guided notes is an evidence-based practice in special education" is ESTABLISHED; any specific d I quote should be treated as unverified until the primary PDFs are read.

**Recommendation**

Make guided notes Tier 1 of the note-taking curriculum and the default for all grade 6-7 content and all students with working-memory or writing-fluency flags. Build it as a product feature, not a lesson: the Tutor Agent generates a skeletal note frame from the day's content (headings + 30-50% of the propositions pre-filled, blanks at the criterion ideas), the student completes blanks during/after instruction, and the system scores blank-completion accuracy. This is also the cheapest thing in the entire artifact to build — it is template generation plus string matching — and it is the only note-taking feature whose evidence base would survive an MCPS special-education director's scrutiny.

### MC-01 — SRSD (Self-Regulated Strategy Development) is completely absent despite being the best-evidenced metacognitive intervention for this population

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Line 485: "African-Centered Metacognitive Science... 'Know Your Mind' self-assessment opens every module". Line 169 (gap analysis): "Metacognition taught as individual cognitive strategy (Flavell, 1979). Never connected to cultural identity or collective knowing." Staff Domain 1 (line 309): "Metacognitive strategy explicit instruction (not just modeling)". SRSD, Graham, or Harris appear nowhere in 859 lines.

**The problem**

SRSD is a six-stage instructional model (develop background knowledge → discuss it → model it → memorize it → support it → independent performance) that explicitly teaches goal-setting, self-monitoring, self-instruction and self-reinforcement alongside a task strategy. It was developed for and validated primarily with students with learning disabilities and ADHD — the artifact's exact target. It is the closest thing in special education to a complete, packaged, validated answer to the question the artifact is asking ("how do we explicitly teach metacognition to neurodivergent middle schoolers?"), and the artifact instead invents 'Know Your Mind' self-assessment and a Sankofa journal. The artifact's own stated principle is "evidence before claims"; here it built a novel construct where a validated one already exists.

**Evidence**

Graham & Harris (2003), "Students with learning disabilities and the process of writing: A meta-analysis of SRSD studies," in Swanson, Harris & Graham (Eds.), Handbook of Learning Disabilities — 18 studies. Graham, Harris & McKeown (2013) update, same Handbook, 2nd ed. IMPORTANT CAVEAT TO CARRY FORWARD: 14 of the 18 studies in Graham & Harris (2003) were authored by Harris and Graham themselves, with the rest by their students and colleagues — this is a developer-heavy evidence base and the founder should say so rather than quote it uncritically. The widely circulated "average effect size of 1.17 for writing quality" figure is attributed inconsistently across sources (sometimes to Graham & Harris 2003, sometimes to a separate 13-approach elementary meta-analysis) — treat the specific number as UNVERIFIED pending reading the primary papers. A 2013 component analysis reported the added value of the explicit self-regulation component at ~0.48 SD, from only five comparison studies.

**Recommendation**

Rebuild the metacognition track on the SRSD six stages as the instructional spine, and say so by name in any MCPS-facing document. Map it directly: 'Know Your Mind' becomes Stage 1-2 (develop and discuss background knowledge); the AI Tutor's Socratic mode becomes Stage 3 (model, with think-aloud); a mnemonic card becomes Stage 4 (memorize); scaffolded fading becomes Stage 5 (support); and the certification practicum becomes Stage 6. State the developer-authorship caveat explicitly in the evidence ledger — doing so is itself a credibility asset with a research-literate district reviewer.

### NT-02 — Strategic Note-Taking for students with LD in middle-school science — a direct-hit RCT for this population — is absent

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> Student cert Module 4 (line 338): "Note-Taking Mastery (6 Evidence-Based Methods)". Teacher cert module (line 423): "Note-Taking Curriculum Design (School-Wide Implementation)". No strategy-instruction note-taking approach appears anywhere.

**The problem**

There exists a line of research that randomised middle-school students with learning disabilities to note-taking strategy instruction versus conventional note-taking, in science classes — the artifact's target grade band, target disability profile, and one of its four named subjects. The artifact's six methods are all *formats* (how the page is laid out). Strategic Note-Taking is a *strategy* (what cognitive moves the student makes while listening: activating prior knowledge, clustering 3-7 main points, naming relationships, summarising at the end of the lecture). Format instruction without strategy instruction is the known failure mode for this population — the artifact itself argues this at line 166 ("Accommodations without skill-building produce learned helplessness") and then does exactly the format-only thing in its own curriculum.

**Evidence**

Boyle (2010), "Strategic Note-Taking for Middle-School Students with Learning Disabilities in Science Classes," Learning Disability Quarterly — 40 students with LD randomly assigned to trained vs. conventional note-taking while viewing a videotaped science lecture; trained students outperformed controls on immediate recall and comprehension. Boyle & Weishaar (2001) reported a similar advantage for high school students with LD on recall, test performance, and total words recorded. CAVEATS: n = 40 is small; the work comes substantially from one research group; I did not locate an independent replication. An IES-funded extension developed a version for inclusive general-education middle-school science classes. Tier is EMERGING, not ESTABLISHED, for this reason — but it remains the most on-target evidence in existence for what the artifact is trying to do. Related LD lecture-note strategies (e.g. AWARE, attributed to Suritsky & Hughes) exist in the same literature; the precise acronym attributions are UNVERIFIED in this pass.

**Recommendation**

Add Strategic Note-Taking as Tier 2 of the curriculum (the bridge between guided notes and independent notes) and implement it as a cued digital note form: before the lesson the app prompts prior-knowledge activation and a prediction; during the lesson it prompts "name the main point + 3 details" per cluster; after the lesson it forces a written summary. This is the single feature most defensible to an MCPS special-education audience. Report its evidence honestly as promising-but-thin (one small RCT, same-group replications) rather than filing it under "PhD-level."

### NT-03 — "Research-Validated" is false: all six methods are sourced to trade books, and two citations are outright misattributions

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> Line 498 header: "6 Note-Taking Methods (Research-Validated)". Line 501: Cornell Notes, r:"Pauk (1962) — Cornell University". Line 502: Mind Mapping, r:"Buzan (1970) — validated UCL". Line 503: Sketchnoting, r:"Rohde (2013) — visual learning research". Line 504: Outline Method, r:"Ausubel Advance Organizers (1960)". Line 505: Flow Notes, r:"Young (2011) — self-directed learning". Line 506: Atomic / Zettelkasten, r:"Luhmann (1981) — PKM research".

**The problem**

Not one of these six is a citation to a controlled study of the method. Pauk (1962) is How to Study in College, a study-skills textbook. Buzan (1970) is a popular-psychology trade work, and "validated UCL" has no identifiable referent — I could find no UCL validation study of mind mapping; this reads as invented provenance. Rohde (2013) is The Sketchnote Handbook, a design trade book. Ausubel's advance organizers (1960) are prose passages presented BEFORE instruction to provide a subsuming conceptual framework — they are not the outline note-taking method, and the attribution is simply wrong. Young (2011) is a self-directed-learning blogger/author, not a research source. Luhmann (1981) is an essay about his own filing practice. The artifact's masthead principle is "evidence before claims" and "no claims of validation that has not occurred" (founder's stated operating principles) — this section violates both in its own headline. A single research-literate MCPS reviewer or grant panelist who checks one of these loses confidence in all 859 lines.

**Evidence**

Direct inspection of the cited works' nature (textbooks/trade books vs. empirical studies) — ESTABLISHED by the primary sources' own publication type. The "validated UCL" claim: I searched for a UCL validation of mind mapping and found none; I am recording it as UNVERIFIED-AND-PROBABLY-UNFOUNDED rather than asserting it is fabricated. The Ausubel misattribution is ESTABLISHED by Ausubel's own 1960 definition of advance organizers (introductory material at a higher level of abstraction presented in advance of the learning material).

**Recommendation**

Delete the phrase "Research-Validated" from line 498 this week — it is the cheapest credibility repair in the document. Replace each method's `r:` field with an honest three-tier label: EVIDENCE-BASED (controlled trials with this population), PROMISING (some controlled evidence, thin or contested), or PRACTITIONER TRADITION (widely used, no controlled evidence). Under that rule the current six are: Cornell = PROMISING, Mind Mapping = PROMISING (weaker cousin of concept mapping), Sketchnoting = PRACTITIONER TRADITION, Outline = PRACTITIONER TRADITION, Flow Notes = PRACTITIONER TRADITION, Zettelkasten = PRACTITIONER TRADITION (no adolescent evidence). Ship the honest labels; they cost nothing and they are the differentiator against every competitor in the gap-analysis table.

### NT-04 — The product is mobile-first and typing-based and never confronts the longhand/laptop literature — including what actually replicates

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Line 525: "App Design: MindUnlock Academy — Mobile-first". Line 531 Study Lab: "Note-taking method selector + guided tutorial". Line 685: "React Native (Expo SDK 51) — Mobile App". Student cert Part 4 portfolio (line 346): "3 note-taking samples (3 different methods)". Mueller & Oppenheimer is not cited anywhere in 859 lines.

**The problem**

The best-known single finding in note-taking research is a claim that typing is worse than handwriting. A mobile-first, typing-based note product that does not address it will be asked about it in the first district meeting and the first investor meeting, and the artifact has no answer prepared. Worse, it has no answer prepared for the thing that IS robust. What failed to replicate: the conceptual-learning advantage for longhand. What replicated every time: laptop/typing note-takers record more words and more VERBATIM transcription from the source. Verbatim transcription is the actual enemy — it is shallow, non-generative capture — and it is a property of the input affordance, not of the device. The artifact's mobile typing interface maximises exactly the behaviour that is reliably bad, and it has no countermeasure.

**Evidence**

Mueller & Oppenheimer (2014), "The Pen Is Mightier Than the Keyboard," Psychological Science (note: a corrigendum was later published, PMID 30063408). Morehead, Dunlosky & Rawson (2019), "How Much Mightier Is the Pen than the Keyboard for Note-Taking? A Replication and Extension," Educational Psychology Review — performance did not consistently differ between longhand, laptop, eWriter, or even a no-notes control; the authors concluded that declaring a superior medium is premature. Urry et al. (2021), "Don't Ditch the Laptop Just Yet," Psychological Science 32(3), 326-339 — direct replication (n ≈ 142-145, Tufts) plus mini meta-analysis of eight similar studies; no longhand advantage on conceptual recall; laptop users again recorded more words and more verbatim phrases. NOTE: the task framing called Urry et al. a "multi-site replication" — the published paper is a single-site direct replication plus mini meta-analyses; use the accurate description.

**Recommendation**

Take the position explicitly in the artifact and in sales material: "The device does not determine learning; the processing does. Typed notes are fine. Verbatim typed notes are not." Then build the countermeasure into the input: (a) a character/word budget per concept block that makes transcription impossible; (b) paraphrase detection — flag any note segment with high n-gram overlap against the source transcript and prompt "say this in your own words"; (c) a voice-to-paraphrase mode for students with writing-fluency deficits, which keeps the generative demand while removing the motor demand. This turns the biggest apparent weakness of a mobile product into a defensible design claim.

### NT-05 — AI-generated notes are the product's central learning risk and appear nowhere in the risk register

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.84 |

**What the artifact says**
> Line 531 Study Lab: "AI note feedback and knowledge gap finder". Line 597 Tutor Agent tools: "Note review analyzer"; output: "note feedback (gaps + improvements)". Line 536: "Note review and improvement AI feedback". Risk register (lines 116-122) lists FERPA, hallucination, crisis, cultural appropriation, dropout, and UI overload — not offloading. Failure-handling table (lines 634-639) likewise omits it.

**The problem**

The generation effect and the offloading literature converge on one point: when a system produces the artifact the learner was supposed to produce, measured learning falls even while perceived learning and in-session performance rise. An AI that "improves" a student's notes is doing the student's encoding. This matters more here than in a general-purpose product because the target population has the weakest metacognitive monitoring and will therefore be the least able to detect that the help is hurting. The artifact's own risk register treats AI risk as a truthfulness problem (hallucination, confidence scoring < 0.85) when the real risk is a pedagogical one: a perfectly accurate AI-written note is still a learning loss. There is no stated boundary anywhere on what the AI may and may not author.

**Evidence**

Bastani et al. (2025) field experiment with ~1,000 secondary mathematics students: chatbot access raised practice-problem performance but LOWERED later unaided exam performance, and students believed they had learned as much as peers without access — the canonical illusion-of-learning result. Stadler et al. (2024): students researching a socio-scientific issue with an LLM reported significantly lower cognitive load than search-engine peers but produced lower-quality reasoning and argumentation. Emerging reviews (e.g. Educational Psychology Review 2026 on regulating cognitive offloading in GenAI-supported STEM learning) frame the effect as a property of the partition of cognitive labour between learner and machine, not of the tool. Tier is EMERGING: these are recent, some are preprints or not yet replicated, and there are counter-findings (a 2025 quasi-experiment with 240 first-year students reported gains from structured offloading). The DIRECTION of risk is well enough supported to design against; specific effect sizes are UNVERIFIED.

**Recommendation**

Write and publish an AI Notes Contract as a first-class product document, and put offloading in the risk register at Critical: (1) the AI never writes, completes, rewrites or 'improves' a student's note — one hard rule, enforced in the Tutor Agent's system prompt and in an output filter; (2) the AI may only ASK (Socratic prompts), SCORE (completeness against a criterion idea list), and QUIZ (generate retrieval items FROM the student's own note, so a thin note yields a thin quiz and the consequence is visible); (3) instrument the counterfactual — every AI-assisted study block is followed by an unaided retrieval check, and the dashboard shows assisted vs. unaided performance side by side so the illusion is made visible to student, parent and teacher. This single pairing is also the most compelling demo in the whole product and the most publishable pilot result the founder could generate.

### NT-06 — Mind mapping was chosen over concept mapping — the artifact picked the weaker-evidenced of the two

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.89 |

**What the artifact says**
> Line 502: Mind Mapping, r:"Buzan (1970) — validated UCL", best:"Concept relationships + brainstorm", steps include "Central concept in page center", "Color-code by topic or importance", "Add icons/images for visual memory anchoring". Line 196 (course gap table) treats "Tony Buzan / Mind Genius (Mind Mapping)" as the comparison incumbent. Concept mapping and Novak appear nowhere.

**The problem**

Mind maps (radial, hierarchical, unlabelled links) and concept/knowledge maps (node-link graphs with LABELLED relationships between concepts) are different instruments with different evidence bases. The labelled link is the cognitive work — it forces the learner to name a relation rather than merely cluster. Concept mapping has solid, large-n meta-analytic support; mind mapping's meta-analyses are heterogeneous and methodologically weaker. The artifact's own stated use case for mind mapping — "Concept relationships" — is precisely what concept mapping does and mind mapping does not. For comparative content (compare photosynthesis vs. respiration; compare three causes of the Civil War), Kiewra's line of work indicates matrix/graphic-organiser notes outperform linear outlines, and a matrix is a concept-map relative, not a mind map.

**Evidence**

Nesbit & Adesope (2006), "Learning With Concept and Knowledge Maps: A Meta-Analysis," Review of Educational Research 76(3), 413-448 — 67 effect sizes from 55 studies, 5,818 participants, Grade 4 through postsecondary; effects varied small-to-large by use and comparison condition; group construction with individual time produced g = .96 vs. g = .12 for individual-only. Schroeder, Nesbit, Anguiano & Adesope (2017), "Studying and Constructing Concept Maps: A Meta-Analysis" — 142 independent effect sizes, n = 11,814, overall g = 0.58; CONSTRUCTING maps (g = 0.72) beat STUDYING provided maps (g = 0.43). Mind-mapping meta-analyses by contrast: Batdı (2015), 15 studies, reported ~1.06 but with no moderator analysis and 83.7% of included studies from a single country; Shi et al. (2023), 21 studies, g = 0.67 with subject and level as significant moderators. Hattie's list does not give graphic organizers a single effect size because it is not a specific method. Time-on-task as a confound in the mind-mapping primary studies is NOT addressed in any source I retrieved — UNVERIFIED.

**Recommendation**

Replace Mind Mapping with Concept Mapping as the Tier 2 relational method, and specify the one feature that carries the evidence: every link must be LABELLED with a relation verb (causes / enables / is a type of / contradicts / precedes). Keep radial mind mapping only as a pre-writing brainstorm tool, explicitly labelled as an idea-generation aid rather than a study method. Add matrix notes (rows = items compared, columns = dimensions) as the mandated format for comparative content — this is the Kiewra finding and it is trivially implementable on mobile as a table widget. Build the map CONSTRUCTOR, not a map viewer: the meta-analytic moderator is construction, and a product that shows students pre-made maps is building the g = 0.43 version instead of the g = 0.72 version.

### MC-02 — Metacognition is taught as vocabulary; the monitoring/control architecture that makes it operational is missing

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Line 264 diagnostic sources: "Flavell Metacognitive Framework (1979)". Line 269 item 2.10: "Metacognitive awareness — knowing what you know and don't know (Flavell, 1979)" — one item out of 52. Line 485: "'Know Your Mind' self-assessment opens every module". Line 169: "Metacognition taught as individual cognitive strategy (Flavell, 1979)." Nelson & Narens, Brown, judgments of learning, and calibration appear nowhere.

**The problem**

Flavell's 1979 distinction (metacognitive knowledge vs. metacognitive experiences/regulation) is the starting point of the field, not the field. Everything the product actually needs lives downstream: Nelson & Narens (1990) formalised metacognition as a two-level architecture — an object level (the cognition doing the work) and a meta level (a model of it), connected by MONITORING (information flowing up: judgments of learning, feelings of knowing, confidence) and CONTROL (information flowing down: allocate study time, terminate study, select a strategy, restudy or move on). This is not academic decoration; it is the engineering specification for the product. Every feature the artifact wants — the adaptive difficulty engine, the study-plan co-builder, the "knowledge gap finder" — is a control decision, and control decisions are only as good as the monitoring that feeds them. A single self-report diagnostic item asking a 12-year-old whether they know what they know is the weakest possible measurement of exactly the thing the product exists to fix. Ann Brown's distinction between knowledge about cognition and regulation of cognition makes the same point: the artifact built the knowledge half, which is the half that transfers least.

**Evidence**

Flavell (1979), "Metacognition and cognitive monitoring," American Psychologist 34(10), 906-911. Nelson & Narens (1990), "Metamemory: A theoretical framework and new findings," Psychology of Learning and Motivation vol. 26 — the meta-level/object-level, monitoring/control framework. Brown (1987) on knowledge of cognition vs. regulation of cognition. ESTABLISHED: this is the canonical architecture of the field and is uncontested as a framework (specific mechanisms within it remain debated).

**Recommendation**

Rewrite the metacognition module around the monitoring/control loop and make the loop visible in the UI. Concretely: every study block ends with a monitoring act (a confidence rating on specific content, not a mood check) and every monitoring act drives a control decision the student makes and sees (restudy this / schedule it / move on). Replace diagnostic item 2.10 with a calibration task that yields a NUMBER (see MC-03) rather than a Likert self-report. State in the gap analysis that the product's innovation is correcting monitoring accuracy — that is a defensible, differentiated, testable claim, unlike "PhD-level metacognitive science."

### MC-03 — No calibration measurement or correction — the product teaches strategies without fixing the judgment that selects them

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Line 594 Learning Path Agent memory: "Mastery levels per domain, engagement patterns, performance history" — performance, never confidence. Line 341-346 certification exam: four parts, all scored on accuracy, none on calibration. Line 289 parent item: "Knowledge of study techniques beyond re-reading and highlighting" — the artifact knows rereading is the problem and still has no mechanism to correct the judgment that produces it.

**The problem**

The hard finding in this literature is not that students lack strategies — it is that students are systematically OVERCONFIDENT and, when given free choice, select the least effective strategies, because the ineffective strategies feel better in the moment. Rereading feels fluent; retrieval practice feels hard and therefore feels like failure. A product that hands a 12-year-old six note-taking methods and a self-build study schedule ('Child-designed: self-build mode', line 530; 'Democratic module sequencing: student chooses their learning path', line 486) is handing maximum strategic autonomy to the learners with the least accurate monitoring — the artifact's agency principle and its learning-science goal are in direct, unacknowledged conflict. Agency is a good design value; unguided strategy choice by a miscalibrated novice is not agency, it is abandonment.

**Evidence**

Karpicke, Butler & Roediger (2009), "Metacognitive strategies in student learning: Do students practise retrieval when they study on their own?", Memory 17(4), 471-479 — survey of 177 students; a majority report repeatedly rereading notes/textbook, relatively few self-test; the authors attribute this to illusions of competence. (Commonly quoted percentages — ~84% listing rereading, 11% mentioning recall — come from secondary write-ups; I could not confirm them against the results section: UNVERIFIED. A 2019 reexamination argues the rereading framing overstates the finding.) Kornell & Bjork (2007) on self-regulated study choices and learners' preference for massed over spaced practice. Dunlosky, Rawson, Marsh, Nathan & Willingham (2013), Psychological Science in the Public Interest 14(1), 4-58 — practice testing and distributed practice rated HIGH utility; summarization, highlighting, and rereading rated LOW utility; the low-utility set is, as the authors note, among the most commonly used by students.

**Recommendation**

Build a Calibration Engine as a named product feature, and make it the metric the pilot reports. Mechanics, all cheap: (1) before every quiz item the student predicts whether they will get it right; (2) after every quiz the student predicts their score before seeing it; (3) the system computes and displays a calibration score (mean absolute deviation between predicted and actual, or a Brier score) tracked over time as a first-class number next to accuracy; (4) when overconfidence exceeds a threshold, the control decision is taken away from the student for that content and the system schedules retrieval instead of rereading, with a one-line explanation. A measurable reduction in overconfidence in a 10-family pilot is a publishable, grant-fundable, district-sellable result — and nothing in the gap-analysis competitor table has it.

### MC-04 — The EEF metacognition guidance report is missing — and its central caveat condemns the artifact's own course structure

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.87 |

**What the artifact says**
> Lines 458-466 "Research Foundation" lists eight frameworks: spacing, retrieval, interleaving, cognitive load, growth mindset, stereotype threat, African-centered pedagogy, child liberation. Metacognition and self-regulated learning is not among them. Student cert (line 338): 12 standalone modules; Para cert: 12 domains, 80 hours; Teacher cert: 16 modules, 120 hours — all delivered as separate study-skills instruction.

**The problem**

Two separate failures. First, the omission: the EEF's metacognition and self-regulation strand is the highest impact-per-cost intervention in their toolkit, and it is the single most persuasive exhibit the founder could put in front of an MCPS budget holder — it speaks the exact language (months of additional progress, cost rating) that district decision-makers use. It is absent from a document whose entire course-design tab is a bid for research credibility. Second, and more serious: the EEF guidance explicitly reports LITTLE evidence of benefit from teaching metacognitive approaches in standalone 'learning to learn' or 'thinking skills' sessions — the benefit comes from metacognitive strategies taught WITHIN subject content by subject teachers. MindUnlock's entire architecture is standalone sessions: 12 decontextualised student modules, a separate Study Lab, a separate certification track. The best evidence in the field says this delivery model is the one that does not work, and the artifact has adopted it as its core product shape without noticing.

**Evidence**

Education Endowment Foundation, Metacognition and Self-Regulated Learning guidance report (updated edition) and the EEF Teaching and Learning Toolkit entry for metacognition and self-regulation: average impact given on the current toolkit as +8 months additional progress; cost rated very low (costs arising mainly from staff professional development). The older and Australian (Evidence for Learning) phrasing gives +7 months — use +8 and note the provenance. The guidance report's caution against standalone 'learning to learn'/thinking-skills sessions, and its increased prominence for classroom talk in the updated edition, are stated in EEF's own materials. The precise EEF 'evidence strength' padlock rating for this strand is UNVERIFIED — read it off the live toolkit page before quoting.

**Recommendation**

Two changes. (1) Add EEF to the research foundation and lead the MCPS pitch with it: +8 months, very low cost, staff-PD-driven — that framing also sells the paraeducator MCLSS track, because EEF locates the cost in professional development, which is precisely what the founder is selling. (2) Restructure delivery to match the evidence: embed the metacognitive strategies inside MCPS subject content (math, ELA, science, social studies) rather than in freestanding modules, and reposition the standalone modules as the TEACHER/PARAEDUCATOR training layer, which is where EEF says the leverage actually is. This is a product-shape change, not a copy edit, and it should be resolved before Phase 2 content build begins.

### NT-07 — No encoding/external-storage framework and no forced revision-and-review pass — the six methods are capture with no loop

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Lines 501-506: of the six methods, only Cornell includes review steps ("Summarize at bottom within 24 hours", "Use cue column as retrieval practice deck"); Mind Mapping, Sketchnoting, Outline, Flow Notes all end at capture. Flow Notes' only review step is the loose "Connect islands in review session after". Study Lab (line 531) lists note-taking and Anki as separate features with no pipeline between them.

**The problem**

Note-taking has two separable functions: ENCODING (the act of taking notes changes what you learn, even if you never reopen them) and EXTERNAL STORAGE (the notes are a record you later review). They have different determinants and different product implications, and the artifact never distinguishes them. The decisive finding is that encoding PLUS storage beats either alone — the review pass is not optional polish, it is half the intervention. For grade 6-8 students with EF deficits, the encoding function is weak (working memory is the binding constraint; this is exactly why guided notes work) and the external-storage function is where the reliable wins are. The product should therefore be optimised for storage-plus-review, and it currently ships six capture formats with no enforced review step and no bridge from notes into the retrieval engine the artifact already plans to build.

**Evidence**

DiVesta & Gray (1972) established the encoding/external-storage distinction. Kiewra (1989), "A review of note-taking: The encoding-storage paradigm and beyond," Educational Psychology Review 1(2) — reviews both functions. Kiewra et al. (1991), "Note-taking functions and techniques," Journal of Educational Psychology — the encoding-plus-storage condition was superior to encoding alone and to external storage alone for recall, and superior to encoding alone for synthesis. ESTABLISHED.

**Recommendation**

Make the review pass structurally unskippable and name it in the product. Every note session auto-schedules a Revision Pass within 24 hours: (1) reopen the note; (2) fill gaps from the source (this is the completeness repair step and it is where the measurable gain is); (3) generate 3-5 retrieval questions FROM the note — these become the Anki/FSRS cards, closing the pipeline the artifact currently leaves open; (4) answer two of them immediately from memory. Reframe the whole curriculum as 'capture → revise → retrieve' rather than as six capture formats, and state the position explicitly: at grade 6-8 with this population, optimise for external storage plus review, scaffold encoding with guided notes, and do not assume unaided encoding.

### NT-08 — Note completeness — the one variable that predicts learning — is measured by a single self-report item

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.86 |

**What the artifact says**
> Diagnostic Domain 3 item 3.8 (line 270): "Note-taking proficiency baseline — what the student currently does naturally". Line 264 format: "5-point Likert + audio-assisted mode + observational task samples". Student cert portfolio (line 346): "3 note-taking samples (3 different methods)" — scored by "Holistic rubric".

**The problem**

The robust, repeatedly observed finding in this literature is that note COMPLETENESS (the proportion of the source's critical ideas that appear in the notes) predicts subsequent learning, and that students record a small fraction of them. This is a quantity that can be counted automatically against a criterion idea list, it moves with intervention, and it is the ideal pilot outcome measure — objective, cheap, sensitive, and not self-reported. The artifact instead asks a 12-year-old to rate on a Likert scale what they 'naturally do', which measures self-perception, is contaminated by exactly the overconfidence the product is supposed to correct, and produces no baseline against which Phase 1 can demonstrate anything. A 'holistic rubric' on three portfolio samples has the same problem at the certification end.

**Evidence**

Kiewra's programme of research establishes note completeness as a predictor of learning and documents that students record a minority of critical ideas. IMPORTANT: the widely circulated figure that students record about one third of a lecture's important ideas appears in secondary sources (including blog summaries attributing it to Kiewra's reviews) but I could NOT locate the primary Kiewra source for that specific fraction — treat '~1/3' as UNVERIFIED and read it off the primary reviews before publishing it. A more traceable older figure, cited in a 2024 International Journal of Instruction article, attributes to Hartley & Marshall (1974) that some freshmen recorded only 11% of critical lecture concepts while 'A' students recorded 62% — also a secondary-source citation and UNVERIFIED at primary. The general claim (completeness is low and predicts learning) is ESTABLISHED; the specific percentages are not yet verified by me.

**Recommendation**

Replace diagnostic item 3.8 with a scored performance task and make the resulting metric the product's headline KPI. Mechanics: the student takes notes on a standardised 6-minute recorded lesson for which a criterion list of 20 critical ideas exists; the system scores idea-unit capture (semantic match, not string match) and verbatim ratio; outputs are Completeness % and Verbatim %. Re-administer monthly. Replace the Phase 1 KPI 'Diagnostic completion rate ≥ 80%' (line 772) with 'mean note completeness rises from baseline X% to Y%' — completion rate measures compliance, completeness measures the thing the product claims to do. Do the same for the certification portfolio: score completeness and verbatim ratio against a criterion list, not a holistic rubric.

### MC-05 — VARK learning styles in the diagnostic (5.1) and 'cultural learning style' (4.8) contradict the evidence base and create a specific reputational risk

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Diagnostic Domain 5 item 5.1 (line 272): "VARK modality preference (Visual / Auditory / Kinesthetic / Reading-Writing)". Domain 4 item 4.8 (line 271): "Preferred cultural learning style (call-response, storytelling, movement)". Line 503: Sketchnoting "Best for: Creative + kinesthetic + ND learners".

**The problem**

Two problems, one of them delicate. First, the meshing hypothesis — that instruction matched to a learner's modality preference produces better learning — lacks the style-by-treatment interaction evidence that would be required to support it; this is the single most widely debunked idea in applied education psychology, and an MCPS reviewer or an IES/NSF grant panel will spot VARK in a diagnostic instrument immediately. It is a one-line credibility hole in a 52-domain instrument. Second and more sensitively: item 4.8 extends modality thinking to ethnicity, which moves the product from an unsupported claim into territory where an unsupported claim about group-level cognitive styles carries real harm and real reputational risk — including to the founder's own African-centered content, which does not need and is not helped by a learning-styles scaffold. Note that line 503 compounds this by assigning sketchnoting to 'kinesthetic + ND learners' as if neurodivergence were a modality.

**Evidence**

Pashler, McDaniel, Rohrer & Bjork (2008/2009), "Learning Styles: Concepts and Evidence," Psychological Science in the Public Interest 9(3), 105-119 — the review's own section heading states that the core style-by-treatment interaction evidence is missing; the required design (assign learners to style groups, randomise teaching method, test all on the same assessment) is essentially absent from the literature. ESTABLISHED. Whether the paper addresses the VARK instrument by name is UNVERIFIED; the critique targets the general meshing hypothesis of which VARK is an instance. Mayer's multimedia principles and Paivio's dual coding support presenting words AND pictures to ALL learners — a modality-general finding, not a modality-matching one.

**Recommendation**

Delete item 5.1 and replace it with constructs that are actually actionable and actually measured: processing-speed comfort (already 5.5), sensory sensitivity thresholds (already 5.2), and access-need flags (text-to-speech need, writing-fluency constraint, reading rate). Reframe item 4.8 away from 'learning style' to 'culturally familiar discourse practices the student values and responds to' — which is an engagement/belonging construct, is defensible, and is what the founder actually means. Remove 'kinesthetic' from line 503. Then make the positive case in its place: dual coding and Mayer's principles say give EVERY student words plus relevant graphics, with coherence (no decorative extras) and redundancy constraints — that is a stronger design rule than VARK and it is actually supported.

### MC-06 — Metacognitive illusions are never named, so the product has no countermeasures against the specific failure modes it will produce

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.87 |

**What the artifact says**
> Line 532 Anxiety Toolkit and line 531 Study Lab contain no confidence or prediction mechanics. Line 594 Learning Path Agent: "Adaptive difficulty engine" with memory of "Mastery levels per domain, engagement patterns". Line 486: "Students design THEIR OWN study system (guided choice, not compliance)". Line 338 Module 10: "Teaching Others (Protégé Effect + Feynman Technique)".

**The problem**

Each named illusion in this literature implies a specific, cheap product countermeasure, and the artifact implements none of them because it never names them. FLUENCY: easily processed material feels learned — so a smooth AI explanation and a beautifully formatted note both inflate confidence; countermeasure is to test, not to admire. STABILITY BIAS: learners judge future memory by current state and under-predict both forgetting and the benefit of further study — countermeasure is to show the forgetting curve against the student's own data and to make judgments at a delay. FORESIGHT BIAS: judging learning while the answer is visible produces large overconfidence — countermeasure is cue-only judgments. ILLUSION OF EXPLANATORY DEPTH: people believe they can explain mechanisms they cannot, and the illusion collapses only when they try to generate the explanation — which is precisely why Module 10's Feynman/protégé framing is the right instinct, but the artifact uses it as a teaching technique rather than as a CALIBRATION probe, which is its sharpest use. The artifact's 'Know Your Mind' self-assessment is in fact an illusion amplifier: it asks students to report metacognitive knowledge without ever testing it.

**Evidence**

Fluency/processing-fluency effects on judgments of learning and the broader illusions-of-competence account in Karpicke, Butler & Roediger (2009). Stability bias and foresight bias are documented in the Koriat and Bjork lines of work on judgment of learning (the specific canonical citations — e.g. Koriat, Bjork, Sheffer & Bar on the foresight bias — are ESTABLISHED as phenomena; I have not re-verified the exact article/year for each in this pass, so cite them from primary sources before publishing). Illusion of explanatory depth: Rozenblit & Keil (2002), Cognitive Science. Nelson & Narens (1990) supplies the architecture these all sit in.

**Recommendation**

Build an Illusion Countermeasure table into the course design tab, one row per illusion, each with a shipped feature: fluency → confidence rating is always followed by a retrieval item, never by a 'does this make sense?' check; stability bias → delayed judgments plus a personal forgetting curve displayed from the student's own FSRS data; foresight bias → all confidence judgments made cue-only with the answer hidden; illusion of explanatory depth → promote the Feynman step from Module 10 to a recurring weekly probe ('explain the mechanism in 60 seconds, out loud, from memory'), scored against the criterion idea list, with the gap shown to the student. Each is a few days of work and together they constitute a genuinely differentiated product claim.

### MC-07 — The delayed-JOL effect is the cheapest shippable metacognitive feature in the field and is absent

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> Line 594 Learning Path Agent triggers: "Module completion, assessment score update, daily login, weekly schedule generation" — no post-study judgment at any point. Line 531 Study Lab has no confidence mechanic. Line 338 Module 2: "How Your Brain Learns — Memory, Retrieval, and Forgetting" — taught as content, never instrumented.

**The problem**

Judgments of learning made immediately after study are poor predictors of later recall, because they read out short-term memory. Judgments made after a short delay, and cued by the prompt alone rather than by the prompt-plus-answer, are dramatically more accurate because they require an actual retrieval attempt from long-term memory. For this product that is not an academic curiosity: it means the single design decision of WHEN and HOW to ask 'do you know this?' determines whether every downstream control decision (what to restudy, what to schedule, what the adaptive engine does) is built on good or garbage information. The artifact's agents make scheduling and difficulty decisions with no monitoring input at all.

**Evidence**

Nelson & Dunlosky (1991), "When People's Judgments of Learning (JOLs) Are Extremely Accurate at Predicting Subsequent Recall: The 'Delayed-JOL Effect'," Psychological Science 2(4). Dunlosky & Nelson (1992), Memory & Cognition — the effect is robust when the JOL cue is the STIMULUS ALONE (all 45 subjects showed it) and little or absent when the cue is the stimulus-response pair; this cue-utilisation detail is the implementable part. Dunlosky & Nelson (1994) — delayed JOL accuracy exceeded immediate JOL accuracy in every condition tested. CAVEAT: a competing memory-based account holds that part of the effect reflects the spaced re-exposure rather than better metamemory (when re-exposure was equated, the effect diminished) — the mechanism is contested, but the practical prescription (ask later, cue-only) is unaffected.

**Recommendation**

Ship this in one sprint. After each study block, wait (minutes to hours, or next session open), then present each item's CUE ONLY with the answer hidden and ask 'will you remember this tomorrow?' — a two-tap judgment. Feed the delayed judgment, not an immediate one, into the FSRS scheduler and into the Learning Path Agent's control decisions. Surface the prediction-vs-outcome comparison to the student the next day. This is perhaps 2-3 days of engineering, it improves the scheduler's input quality, it generates the calibration data from MC-03 for free, and it is directly traceable to a 1991 primary source — exactly the kind of claim that survives scrutiny.

### NT-09 — Cornell notes is the flagship method on the strength of a 1962 study-skills textbook; the controlled evidence is thinner than the artifact implies

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.82 |

**What the artifact says**
> Line 501, listed first of six: Cornell Notes, r:"Pauk (1962) — Cornell University", best:"Lecture + exam review". Parent cert Module 4 (line 368): "5 Note-Taking Methods You Can Teach Tonight".

**The problem**

Cornell is positioned as the lead method and its evidential weight rests on the fact that a university's name is in the title and a book was published in 1962. The controlled literature is small, mixed, mostly non-randomised, and often from outside mainstream journals — some small positive studies, at least one null, and no systematic review or meta-analysis of controlled trials that I could locate. Critically, where Cornell appears to help, the mechanism points at the REVIEW steps (generating cue questions after class, summarising within 24 hours, self-quizzing from the cue column) rather than at the ruled page layout — which means the artifact is selling the wrong part. That matters practically: the three-column layout is awkward on a phone, while the review protocol is trivially implementable and is the part carrying the effect.

**Evidence**

Pauk (1962), How to Study in College — a textbook, not a study. Mixed controlled results: a Nigerian experiment (160 college students, randomly assigned across 8 groups) found Cornell above outline and verbatim notes on free recall, modest and setting-specific; Borr et al. (2012) reported no significant difference in Cornell note-taking on student performance, noting they could not confirm students actually used the notes to study; several EFL studies report gains using intact classes rather than randomisation. A Rutgers dissertation on Cornell note-taking and review strategies concludes there is no general consensus on encoding-function effects and that the review/external-storage benefit is better supported than the encoding benefit. I found no systematic review or meta-analysis of controlled Cornell trials — treat any pooled effect size you encounter as UNVERIFIED. The commonly repeated '10-12% higher scores' figure traces to a single classroom report via secondary sources and is UNVERIFIED.

**Recommendation**

Keep Cornell, demote it from flagship to Tier 3, and re-label it honestly as 'a review protocol with a page layout attached' — then strip the layout and keep the protocol. Build the Cornell cue-and-summary sequence as the default Revision Pass (NT-07) applied to ANY note format: after any note, generate cue questions, write a summary, self-quiz from the cues. That delivers the evidenced component to every method instead of to one, and it solves the mobile layout problem by making the layout irrelevant.

### NT-10 — Zettelkasten is taught to grade 6-8 students while the artifact's own app analysis says the same approach is too complex for them

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.83 |

**What the artifact says**
> Line 506: "Atomic / Zettelkasten", r:"Luhmann (1981) — PKM research", best:"Long-term knowledge + Anki building", steps include "Link related cards explicitly", "Build knowledge network over time". Line 229 (app gap analysis): "Notion / Obsidian — Note-Taking / PKM — 15% [meets our needs] — pro: Powerful knowledge management; Zettelkasten — gap: Too complex for middle schoolers; no literacy support".

**The problem**

The document contradicts itself on the same method within the same artifact: the app gap analysis scores Zettelkasten-based tools at 15% and the stated reason is that the approach is too complex for middle schoolers, and the course design then teaches Zettelkasten as one of six core methods to middle schoolers. There is no controlled evidence for Zettelkasten in adolescents (or, so far as I can find, in anyone). The cognitive-load argument runs directly against it for this population: maintaining a link graph imposes substantial extraneous load — load spent on managing the system rather than on the content — on learners the artifact's own Domain 2.1 diagnostic flags for constrained working memory and Domain 2.8 flags for organisational difficulty. The one genuinely valuable element inside Zettelkasten ('write in YOUR OWN words — no copying') is the generation/paraphrase requirement, which does have support and does not require the filing system.

**Evidence**

Luhmann (1981), "Kommunikation mit Zettelkästen" — a sociologist's essay describing his own working method; not an empirical study, and 'PKM research' is not a research literature in the controlled-trial sense. ESTABLISHED by the source's own nature that this is not an evidence base. The cognitive-load argument is INFERENCE from Sweller's extraneous-load framework (which the artifact itself cites at line 462) applied to this population — plausible and consistent with the artifact's own app-gap verdict, but I am not aware of a direct study of Zettelkasten load in adolescents.

**Recommendation**

Cut Zettelkasten from the student curriculum and put it on the explicit 'what we will NOT teach and why' list — doing so demonstrates exactly the discipline the founder claims as an operating principle, and it resolves an internal contradiction a careful reader will otherwise find. Keep the one evidenced element as a universal rule across ALL note methods: notes must be in the student's own words, enforced by the paraphrase-detection check from NT-04. If a PKM-style track is wanted later, place it in the teacher/adult certification tracks where the load argument does not bite.

### NT-11 — Sketchnoting conflates a popular visual-notes genre with dual coding and multimedia learning, and inverts Mayer's coherence principle

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.84 |

**What the artifact says**
> Line 503: Sketchnoting, r:"Rohde (2013) — visual learning research", best:"Creative + kinesthetic + ND learners", steps: "Combine text with hand-drawn images", "Use containers: boxes, clouds, banners", "Visual hierarchy via size + line weight", "Capture ideas as metaphors and icons", "No artistic skill required". Line 196 (gap table) credits Buzan/Mind Genius with "Visual learning tools". Mayer and Paivio appear nowhere in the artifact.

**The problem**

There is a real, strong evidence base for combining words and pictures — Paivio's dual coding and Mayer's multimedia learning principles — and the artifact does not cite it, citing a design handbook instead. The substitution matters because the real principles carry CONSTRAINTS that the sketchnoting genre violates. Mayer's coherence principle says to exclude extraneous material: decorative drawings, banners, and containers added for aesthetic appeal compete for the same limited processing capacity and depress learning. The spatial contiguity principle says to place words next to the graphics they describe. The signalling principle says to cue the essential structure. 'Capture ideas as metaphors and icons' plus decorative containers is, under those principles, a prescription for seductive detail — and it is being prescribed to the learners with the least spare working-memory capacity, which is where coherence violations hurt most. Assigning it to 'ND learners' compounds the VARK error from MC-05.

**Evidence**

Paivio's dual coding theory; Mayer's Cognitive Theory of Multimedia Learning and its principles (coherence, signalling, redundancy, spatial contiguity, segmenting, pre-training, modality, among the twelve) — ESTABLISHED, with a large experimental base largely in multimedia instruction. Note a real boundary condition: most of Mayer's evidence concerns INSTRUCTIONAL materials presented to learners, and its transfer to learner-GENERATED visual notes is an extension, not a direct finding — mark that extension INFERENCE. Rohde (2013), The Sketchnote Handbook, is a trade design book and is not a research source.

**Recommendation**

Rename the method 'Constrained Visual Notes', cite Paivio and Mayer instead of Rohde, and encode the constraints as rules the product enforces: every drawing must depict a relation or a mechanism (never a mood or a decoration); drawings sit adjacent to the text they explain; no banners, borders or containers; one diagram per concept, not per page. Flag honestly that the direct evidence is for instructional multimedia and that applying it to student-generated notes is a reasoned extension. Remove 'kinesthetic + ND learners' from the 'best for' field.

### MC-08 — The 'Ubuntu Learning Circle' has a rigorous research counterpart the artifact never names, and the novelty claim attached to it is false

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.86 |

**What the artifact says**
> Line 169 (gap analysis, 'African-Centered Metacognitive Science'): existing — "Metacognition taught as individual cognitive strategy (Flavell, 1979). Never connected to cultural identity or collective knowing." missing — "Community-level metacognition". innovation — "MindUnlock Ubuntu Learning Circle: collective metacognitive reflection where each student's insight elevates the entire cohort." Line 485: "Ubuntu Learning Circle: cohort collective metacognitive reflection". Line 271 item 4.6: "Collectivist vs. individualistic learning orientation (Ubuntu vs. Western)".

**The problem**

Two issues. The factual one: the claim that metacognition has 'never' been connected to collective knowing is false and easily falsified by a reviewer — there is a mature research programme on socially shared regulation of learning (SSRL) spanning roughly fifteen years, with a three-level framework (self-regulation, co-regulation, socially shared regulation), validated instruments, and CSCL-based empirical work. Making a false novelty claim in a gap analysis is the fastest way to lose a research-literate audience, and it is unnecessary. The strategic one: the founder's instinct here is good and the research would make it stronger. SSRL gives the Ubuntu Learning Circle a precise operational definition — a group jointly setting goals, jointly monitoring progress, and jointly adjusting strategy, as opposed to one member scaffolding another (co-regulation) — which turns a value statement into something designable, measurable, and publishable. Right now the Circle is a ritual with no specified mechanics and no outcome measure.

**Evidence**

Hadwin, Järvelä & Miller (2011), "Self-regulated, co-regulated, and socially shared regulation of learning," in Zimmerman & Schunk (Eds.), Handbook of Self-Regulation of Learning and Performance, pp. 65-84; revised in Schunk & Greene (Eds.), 2nd ed. (2018), pp. 83-106. Järvelä & Hadwin (2013), "New frontiers: Regulating learning in CSCL," Educational Psychologist — introduces the three social levels. Panadero & Järvelä (2015), "Socially Shared Regulation of Learning: A Review," European Psychologist. Key distinction: co-regulation = an individual's regulatory activity guided/prompted by others; SSRL = group members regulating their COLLECTIVE activity. CAVEATS the founder should know: the co-regulation/SSRL relationship is contested (one review argues it is not a clean on/off distinction and may be subordinated, moderated by group dynamics and expertise asymmetry), and terminology is used inconsistently across papers (socially shared regulation vs. socially shared metacognition). I worked from secondary sources describing these primary works and did not read the chapters directly.

**Recommendation**

Delete the false 'never connected to collective knowing' claim from line 169 and replace it with an accurate and stronger one: 'Socially shared regulation of learning is a well-developed construct (Hadwin, Järvelä & Miller) that has not been operationalised for Black middle-school students or connected to Ubuntu as an indigenous articulation of the same insight — that is our contribution.' That is a real, defensible, publishable gap. Then specify the Circle with SSRL mechanics: the group sets a shared goal, each member posts a private confidence judgment, the group sees the distribution, the group jointly selects the next strategy, and the group reviews whether it worked. Measure group-level calibration, not just satisfaction. The cultural idea then rests on research rather than on vibes, which is exactly what the founder asked for.

### EV-01 — Unverifiable and probably invented effect sizes throughout the learning-science sections, including two that contradict established findings

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> Line 460: "Self-testing produces 50% greater retention than re-reading". Line 461: "Mixed-topic practice beats blocked practice for long-term retention by 43%". Line 465: "Culturally affirming instruction raises Black student achievement (ES: 0.8)". Line 466: "Agency in learning design produces 40% greater intrinsic motivation" attributed to Gray (2013). Line 483: Triple Reading Speed — "Result: 60–90% speed increase with equal or greater comprehension"; "Preview Read alone = 60% speed gain". Line 75 and line 531: "90% faster study with AND without AI". Line 464: stereotype threat "suppress performance 15–20%".

**The problem**

These are presented as research findings with the precision of measured quantities, and I can verify none of them as stated. Several have the signature of numbers generated to sound authoritative: a bare percentage with no outcome measure, no retention interval, no comparison condition, and no effect-size metric. Two are not merely unverified but contradicted. The Triple Reading Speed claim — 60-90% faster with equal or greater comprehension — is the exact claim the definitive review of speed reading concludes is not achievable; and that review is a Psychological Science in the Public Interest monograph, i.e. the same series the founder cites elsewhere. 'Study 90% faster' is a marketing claim, and it appears inside the paraeducator certification curriculum (line 400) where it will be taught to school employees as professional content. For a founder whose stated principle is 'no claims of validation that has not occurred', this is the most direct self-contradiction in the document, and in a Title I or IES grant application unverifiable effect claims are disqualifying.

**Evidence**

Rayner, Schotter, Masson, Potter & Treiman (2016), "So Much to Read, So Little Time: How Do We Read, and Can Speed Reading Help?", Psychological Science in the Public Interest 17(1), 4-34 — concludes there is a speed-accuracy trade-off; it is unlikely readers can double or triple speed (250 → 500-750 wpm) while understanding the text as well; eye movements account for no more than ~10% of reading time so the eye-movement-training premise is misplaced; regressions are a comprehension repair mechanism that RSVP-style tools remove; modest speed gains come from practice and breadth of reading exposure; skimming yields speed with moderate comprehension, which is a different goal. ESTABLISHED. For the other figures, I located no primary source supporting the specific numbers as written — recorded as UNVERIFIED, not disproven. The underlying PHENOMENA (testing effect, interleaving benefit, stereotype threat) are real; the quantities are the problem.

**Recommendation**

Institute an evidence ledger (see additions) and apply one rule before any external document ships: every number carries a primary citation, a comparison condition, an outcome measure, and a retention interval, or it is deleted. Specifically this week: delete '90% faster study' everywhere including the paraeducator curriculum; rewrite the Cutler Triple Reading module as a preview-read/skim-and-structure strategy — which IS supported as a schema-building and skimming aid — and explicitly state that no method increases reading speed without a comprehension cost, citing Rayner et al. (2016). Replacing a false superlative with an honest, cited limitation is a net gain in front of any district or grant reviewer.

### TECH-01 — 'Anki SM-18' is factually wrong and breaks the notes-to-retrieval pipeline the curriculum depends on

| | |
|---|---|
| **Severity** | `LOW` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Line 75: "Spaced repetition Anki engine (SM-18)". Line 97: "Integrate Anki SM-18 spaced repetition engine". Line 226: "Anki — Best-in-class SM-18 algorithm". Line 531: "Anki deck creator + smart reviewer (SM-18)". Line 679: "SM-18 Algorithm — Spaced Repetition — Anki-compatible; AnkiConnect sync". Line 774: "Anki SM-18 integration + AnkiConnect sync".

**The problem**

Anki does not implement SM-18 and cannot: SuperMemo's later algorithms (SM-17/SM-18) are proprietary and require licensing, which is why Anki, being open source, ships freely available algorithms. Anki offers a modified SM-2 scheduler and FSRS (integrated in Anki 23.10). The error is repeated six times across five tabs, including in the technical architecture and in two roadmap milestones, which means an engineer costing Phase 2 is costing an integration that does not exist. It matters for this lens because the notes → retrieval-card pipeline (NT-07) is the mechanism that makes the note-taking curriculum pay off, and its scheduling engine is currently specified wrong. It is also the kind of error that, spotted by a technical reviewer, casts doubt on the rest of the stack.

**Evidence**

Anki's official documentation FAQ "What spaced repetition algorithm does Anki use?" states Anki has two schedulers — one based on the SuperMemo 2 algorithm (differing from pure SM-2 in places, e.g. not lowering ease during the learning stage) and FSRS, developed by Jarrett Ye and integrated in Anki 23.10. The same FAQ states SuperMemo's latest algorithm is proprietary and requires licensing, and that FSRS is roughly on par with SM-17 on preliminary tests. Third-party sources disagree about which scheduler is Anki's current default — UNVERIFIED; read it from the current Anki manual.

**Recommendation**

Global find-and-replace 'SM-18' with 'FSRS' across all ten tabs, and restate the technical line as: 'FSRS (Free Spaced Repetition Scheduler), the open-source algorithm integrated into Anki since 23.10; AnkiConnect sync.' While making the change, add the pipeline the curriculum needs: Revision Pass → auto-generate cards from the student's own note → FSRS schedule → delayed cue-only judgment (MC-07) feeds the scheduler. Also reconsider whether to depend on AnkiConnect at all for a mobile-first product aimed at families — FSRS is implementable directly and avoids a desktop-Anki dependency the target families will not have.

### MC-09 — Growth mindset is stated as a settled effect; the meta-analytic picture is considerably weaker and more conditional

| | |
|---|---|
| **Severity** | `LOW` |
| **Evidence tier** | `EMERGING` |
| **Lens confidence** | 0.78 |

**What the artifact says**
> Line 463: "Growth Mindset — Dweck (2006) — Stanford University — Malleable intelligence framing raises achievement and resilience — Every module reframes 'I can't' as 'I can't YET'".

**The problem**

Growth mindset is presented alongside spacing and retrieval practice as if it carried comparable evidential weight. It does not. Meta-analytic work reports that average effects of mindset interventions on achievement are small, with benefits concentrated in specific subgroups — notably academically at-risk and low-SES students — rather than general. This is actually a point in the founder's favour and he should use it that way: the subgroup where effects are most defensible overlaps substantially with MindUnlock's target population. But stating it as a general effect invites a reviewer to discount it entirely, and taking the conditional version lets the founder make a sharper, better-supported, population-specific claim.

**Evidence**

Sisk, Burgoyne, Sun, Butler & Macnamara (2018), "To What Extent and Under Which Circumstances Are Growth Mindsets Important to Academic Achievement? Two Meta-Analyses," Psychological Science — reports weak overall effects with moderation by student risk status and socioeconomic status. I did not read the article in this pass and the SPECIFIC pooled effect sizes are UNVERIFIED — read them before quoting. Large pre-registered trials (e.g. the National Study of Learning Mindsets) report small average effects concentrated in lower-achieving students; specific figures also UNVERIFIED here.

**Recommendation**

Rewrite line 463 to the conditional, defensible claim: 'Brief mindset interventions show small average effects overall, with the clearest benefits for academically at-risk and lower-SES students (Sisk et al., 2018) — the MindUnlock population.' Drop the 'every module' saturation; mindset framing has diminishing returns and repeating it in all twelve modules is more likely to read as slogan than intervention. Reallocate that module time to calibration work (MC-03), which has stronger evidence and attacks the same underlying problem — a student's model of their own capability — with a measurable outcome.


---

## What is missing and should be added

### REPLACEMENT SPEC — Evidence-Ranked Note-Taking Curriculum (replaces the '6 Note-Taking Methods' section entirely)   `ESTABLISHED`

**Why it matters.** The current six were selected by cultural familiarity and trade-book availability, presented under a false 'Research-Validated' banner, and ordered by nothing. A curriculum for neurodivergent grade 6-8 learners must be ordered by evidence strength FOR THIS POPULATION and must fade scaffolding deliberately, because the binding constraint is working memory during live capture — not aesthetic preference.

**What to build.** Four tiers, taught in order, each with a stated evidence label (EVIDENCE-BASED / PROMISING / PRACTITIONER TRADITION) printed in the UI next to the method name.

TIER 1 — GUIDED NOTES [EVIDENCE-BASED]. Default for all grade 6-7 content and for any student flagged on working memory, writing fluency, or processing speed. Teacher- or AI-prepared skeletal frame: headings plus 50-70% of propositions pre-filled, blanks placed exactly at the criterion ideas. Student completes blanks during instruction. System scores blank accuracy. Fade over the year: 70% pre-filled → 50% → 30% → frame only.

TIER 2 — STRATEGIC NOTE-TAKING [PROMISING, one small RCT]. The bridge from guided to independent. A cued digital form with fixed prompts: (a) before — 'what do I already know about today's topic?' plus a prediction; (b) during — repeating cluster blocks of 'main point + 3 details + how it relates to the last point'; (c) after — a written summary of the three to five most important ideas. This is strategy instruction, not layout instruction, and it is the tier that directly targets the artifact's population.

TIER 3 — STRUCTURED CAPTURE + REVISION [PROMISING]. Two formats only, chosen by content type, each mandatorily followed by the Revision Pass: CONCEPT MAPPING with labelled links (for relational/conceptual content) and MATRIX NOTES, rows = items compared, columns = dimensions (for comparative content). Cornell survives here not as a layout but as the revision protocol applied to either format: cue questions, 24-hour summary, self-quiz from cues.

TIER 4 — INDEPENDENT NOTES [PRACTITIONER TRADITION, earned]. Outline or free-form flow capture, unlocked only once a student's measured note completeness exceeds a threshold (e.g. 60% of criterion ideas) on two consecutive assessments. Framing it as EARNED turns the artifact's agency principle into something coherent: autonomy is granted on demonstrated calibration rather than assumed at intake.

DECISION RULE (ship this as a two-question in-app selector, not as a lesson):
Q1 — CONTENT TYPE: sequential/procedural → guided notes or outline. Comparative (two or more things along shared dimensions) → MATRIX. Relational/causal/conceptual → CONCEPT MAP with labelled links. Dense factual/vocabulary → guided notes feeding directly to FSRS cards. Narrative/historical → timeline + cause-effect map.
Q2 — LEARNER PROFILE: working-memory or writing-fluency flag → stay at Tier 1, no exceptions, regardless of content type. Reading-fluency flag → Tier 1 with audio source and voice-to-paraphrase input. No flags and completeness ≥ 60% → Tier 3 or 4.
TIE-BREAK: when content type and learner profile conflict, LEARNER PROFILE WINS. A matrix is useless to a student who cannot capture the cells in real time.

UNIVERSAL RULES, enforced across all tiers: own words only (paraphrase detection against the source); every note triggers a Revision Pass within 24 hours; every note yields retrieval cards.

**Evidence.** Guided notes: Konrad, Joseph & Eveleigh (2009) meta-analytic review (5 studies) and the later K-12 meta-analysis reporting d = 0.940 peer-reviewed / 1.293 dissertations / 1.486 theses (ERIC EJ1001064 — pooled estimate UNVERIFIED, PDF unretrievable because files.eric.ed.gov does not resolve in this session's network settings); Heward's active-student-responding programme. Strategic note-taking: Boyle (2010), Learning Disability Quarterly, n = 40 randomised, middle-school LD science; Boyle & Weishaar (2001) high school. Concept/knowledge maps: Nesbit & Adesope (2006), RER 76(3), 67 ES / 55 studies / 5,818 participants; Schroeder et al. (2017), 142 ES / n = 11,814, g = 0.58 overall, construction g = 0.72 vs. studying g = 0.43. Matrix/graphic-organiser superiority over linear outlines for comparative content: Kiewra's programme. Revision pass: Kiewra et al. (1991) encoding-plus-storage superiority.

### 'What we will NOT teach, and why' — a published exclusion list   `ESTABLISHED`

**Why it matters.** The founder's differentiator against every product in the gap-analysis table is evidential honesty, and an exclusion list is the only artifact that demonstrates it. It also pre-empts the single most damaging question a district reviewer can ask ('why is Zettelkasten in a sixth-grade curriculum?') by answering it first. Publishing what you refuse to sell is worth more in a district meeting than eight more innovation pillars.

**What to build.** A short public page, reproduced in the Course Design tab:

1. ZETTELKASTEN / PKM — no controlled evidence in adolescents; link-graph maintenance imposes extraneous load on learners already constrained on working memory. Our own app analysis scored PKM tools 15% and said 'too complex for middle schoolers'; we are consistent with our own finding. We keep the one evidenced element — own words only — as a universal rule.
2. SPEED READING (as a speed claim) — the definitive review (Rayner et al., 2016, PSPI) finds a speed-accuracy trade-off and that eye movements are ~10% of reading time. We teach PREVIEW READING as a schema-building and skimming strategy and we state plainly that it does not make you comprehend faster.
3. LEARNING-STYLE MATCHING (VARK) — the style-by-treatment interaction evidence is missing (Pashler et al., 2008). We assess access needs and processing constraints instead.
4. ETHNIC LEARNING STYLES — we will not claim that a cultural group has a cognitive modality. We address identity, belonging and stereotype threat, which are different constructs with real evidence.
5. '90% FASTER STUDY' and similar superlatives — we cannot source them and we will not teach them to school employees as professional content.
6. DECORATIVE SKETCHNOTING — Mayer's coherence principle says extraneous visual material competes for limited capacity. We teach constrained visual notes where every drawing depicts a relation or mechanism.
7. AI-AUTHORED STUDENT NOTES — see the AI Notes Contract. The AI never writes the note.

Each entry: one line of what we exclude, one line of why, one line of what we do instead.

**Evidence.** Rayner et al. (2016), PSPI 17(1), 4-34. Pashler, McDaniel, Rohrer & Bjork (2008/2009), PSPI 9(3), 105-119. Mayer's coherence principle. The artifact's own line 229 app verdict on PKM tools. Absence of controlled Zettelkasten evidence in adolescents: I found none; recorded as absence of evidence, not evidence of absence.

### METACOGNITION MODULE SPEC — built on monitoring and calibration, not vocabulary   `ESTABLISHED`

**Why it matters.** The current metacognition content teaches students the word 'metacognition' and asks them to self-rate their awareness. That is the declarative-knowledge half of the construct and the half that transfers least. Rebuilding on the Nelson & Narens monitoring/control architecture makes every unit produce a NUMBER the product can act on and the pilot can report, and it turns a vague differentiator into a measurable one.

**What to build.** Six units, each ending in a measurement, replacing the current 'Know Your Mind' opener and Sankofa journal (both of which are retained as framing and reflection but no longer carry the instructional load).

U1 — TWO LEVELS. Students learn, through doing rather than defining, that there is the thinking and the watching-the-thinking. Output: first calibration baseline (predict score on a 10-item quiz, take it, see the gap).
U2 — YOUR MONITORING IS BROKEN (AND SO IS EVERYONE'S). Demonstrate overconfidence on the student's own data from U1 rather than assert it. Introduce fluency: easy-to-read is not the same as learned. Output: a personal overconfidence number.
U3 — WHEN TO ASK YOURSELF. Teach that immediate 'do I know this?' is unreliable and delayed, cue-only judgment is far better. Output: delayed JOL habit installed and feeding the scheduler.
U4 — CONTROL DECISIONS. Four moves only: restudy now / schedule it / test myself / move on. Students practise mapping monitoring output to control choice. Output: control decisions logged and later scored against outcomes.
U5 — THE EXPLANATION TEST. Pick something you are confident about; explain the mechanism aloud for 60 seconds from memory; compare against the criterion idea list. The illusion of explanatory depth, experienced rather than described. This absorbs and sharpens the artifact's existing Feynman/protégé Module 10.
U6 — REGULATING TOGETHER. The SSRL unit (see separate addition) — group goal-setting, shared monitoring, joint strategy adjustment.

ASSESSMENT: the module's exit criterion is a calibration improvement, not a quiz score. A student passes when their mean absolute prediction error falls below threshold across three assessments — which is a genuinely novel and genuinely defensible certification criterion.

SRSD is the delivery model for all six units (develop background knowledge → discuss → model with think-aloud → memorize → support with fading → independent), so the module is built on a validated instructional model rather than an invented one.

**Evidence.** Nelson & Narens (1990), monitoring/control, meta-level/object-level architecture. Flavell (1979) for the knowledge/experience distinction; Brown (1987) for knowledge vs. regulation. Nelson & Dunlosky (1991) and Dunlosky & Nelson (1992, 1994) for delayed, cue-only JOLs. Karpicke, Butler & Roediger (2009) and Kornell & Bjork (2007) for the overconfidence and poor-strategy-selection findings. Rozenblit & Keil (2002) for the illusion of explanatory depth. Graham & Harris (2003) / Graham, Harris & McKeown (2013) for SRSD as the delivery model (with the developer-authorship caveat stated).

### Note Quality Score — the measurement instrument that replaces diagnostic item 3.8   `ESTABLISHED`

**Why it matters.** The product currently has no objective measure of the thing it claims to teach. Note completeness is countable, moves with intervention, predicts learning, and is immune to the self-report contamination that makes a Likert item from a miscalibrated 12-year-old close to worthless. This is also the instrument that makes the 10-family pilot produce a publishable result instead of a satisfaction survey.

**What to build.** A standardised 6-minute recorded lesson with an expert-authored criterion list of 20 idea units, administered at intake and monthly. Four scored outputs: (1) COMPLETENESS — proportion of criterion ideas present in the student's notes, scored by semantic match not string match; (2) VERBATIM RATIO — proportion of note text with high n-gram overlap against the source transcript (lower is better; this is the transcription metric from the laptop/longhand literature); (3) ORGANISATION — presence of labelled relations between ideas; (4) REVISION DELTA — completeness gain from the 24-hour Revision Pass, which isolates the external-storage contribution. Build three parallel forms to permit repeat administration without practice effects. Make Completeness the Phase 1 headline KPI in place of 'Diagnostic completion rate ≥ 80%'.

**Evidence.** Kiewra's programme establishing note completeness as a predictor of learning and documenting low capture rates in typical students. The frequently quoted '~1/3 of important ideas' figure is UNVERIFIED at primary source — do not print it until read. Hartley & Marshall (1974), cited secondarily, reports ~11% for freshmen vs. ~62% for 'A' students — also UNVERIFIED at primary. Verbatim-ratio rationale: Mueller & Oppenheimer (2014), Morehead et al. (2019) and Urry et al. (2021) all replicate the finding that typed notes contain more verbatim transcription.

### Guided Notes Engine — the highest-yield, lowest-cost feature in the product   `ESTABLISHED`

**Why it matters.** This is the one place where the best evidence for the target population coincides with the cheapest engineering in the artifact. It is template generation plus blank placement plus string matching. It should be built before the BARS scheduler, before the ancestor library, and before the eight-agent LangGraph system, because it is the feature most likely to produce a measurable effect in a 10-family pilot.

**What to build.** Input: any lesson source (teacher upload, textbook section, MCPS unit content, lecture transcript). The engine extracts a criterion idea list, generates a skeletal note frame with headings and 50-70% of propositions pre-filled, and places blanks at the criterion ideas (never at trivia or at the first word of a sentence). Student completes blanks on mobile during or immediately after instruction. System scores blank accuracy and surfaces misses as FSRS cards. Fading schedule configurable per student and tied to the Note Quality Score: pre-fill drops from 70% to 50% to 30% to frame-only as measured completeness rises. Teacher override on blank placement, so teachers retain professional judgment — which is also how the product gets adopted by teachers rather than imposed on them. This feature alone is a complete, defensible, saleable MVP for the MCPS special-education audience.

**Evidence.** Konrad, Joseph & Eveleigh (2009); the K-12 guided notes meta-analysis (ERIC EJ1001064, d = 0.940 peer-reviewed / 1.293 / 1.486 by publication type; pooled estimate UNVERIFIED, PDF unretrievable in this session); Heward's active-student-responding line. Guided notes' standing as an evidence-based practice in special education is ESTABLISHED; specific pooled effect sizes should be read from the primary articles before being quoted to a district.

### The Revision Pass — a forced 7-minute post-session protocol that closes the notes-to-retrieval loop   `ESTABLISHED`

**Why it matters.** Encoding plus external storage beats either alone, and for grade 6-8 students with EF deficits the storage-plus-review half is where the reliable gains are. The artifact currently treats note-taking and spaced repetition as two unconnected features in the Study Lab. The Revision Pass is the connective tissue, and making it structurally unskippable is the difference between a note app and a learning intervention.

**What to build.** Auto-scheduled 7 minutes within 24 hours of every note session, appearing as a BARS block the student cannot silently delete (they can reschedule it twice, then it blocks the next study block). Four steps, timed: (1) REOPEN — 90 seconds, read your note; (2) REPAIR — 3 minutes, fill gaps from the source; completeness delta is scored and shown, which is the moment the student SEES that their notes were incomplete, making this the single most powerful calibration event in the product; (3) GENERATE — 2 minutes, write 3-5 questions from your own note; these become FSRS cards; (4) RETRIEVE — 90 seconds, answer two of them from memory, cue-only, with a confidence prediction first. For students with writing-fluency constraints, steps 2-3 accept voice input. The protocol is method-agnostic, so it delivers the evidenced component across all four curriculum tiers.

**Evidence.** Kiewra et al. (1991), Journal of Educational Psychology — encoding-plus-storage superior to encoding alone and to external storage alone. DiVesta & Gray (1972) for the functional distinction. Dunlosky et al. (2013), PSPI 14(1) — practice testing and distributed practice rated HIGH utility; rereading rated LOW, which is what the Revision Pass is designed to displace. Nelson & Dunlosky (1991) for the delayed, cue-only judgment in step 4.

### AI Notes Contract — the boundary document the product cannot ship without   `EMERGING`

**Why it matters.** An AI note product's central risk is not hallucination, it is that accurate AI help removes the generative work that produces learning, while simultaneously raising the learner's confidence. The population with the weakest monitoring is least able to detect this. The artifact's risk register treats AI risk purely as a truthfulness problem, which leaves the pedagogical risk entirely unmanaged in a product whose Study Lab already advertises AI note feedback.

**What to build.** A one-page contract, enforced in system prompts and in an output filter, published to parents and schools:
THE AI MAY NOT: write, complete, summarise, rewrite, expand or 'improve' any part of a student's note; supply a missing idea during the Repair step (it may only say WHERE a gap is, by section, not WHAT is missing); produce a study summary in place of the student's own.
THE AI MAY: ask Socratic questions; score completeness against the criterion list and name the LOCATION of gaps; generate retrieval questions from the student's own note text (so a thin note yields a thin quiz and the consequence becomes visible); read content aloud; accept voice and transcribe the student's own words verbatim.
INSTRUMENTED COUNTERFACTUAL: every AI-assisted block is followed by an unaided retrieval check, and the dashboard shows assisted vs. unaided performance side by side for student, parent and teacher. If the gap widens, the system reduces AI availability automatically and says why.
Add 'cognitive offloading / illusion of learning' to the risk register at Critical severity with this contract as the stated mitigation.

**Evidence.** Bastani et al. (2025), field experiment with ~1,000 secondary mathematics students: chatbot access raised in-session practice performance, LOWERED later unaided exam performance, and students believed they had learned as much as unaided peers. Stadler et al. (2024): LLM users showed significantly lower cognitive load than search-engine users but produced lower-quality reasoning and argumentation. Reviews in Educational Psychology Review (2026) framing the effect as dependent on the partition of cognitive labour. Tier EMERGING: recent, some not yet replicated, with counter-findings from a 2025 quasi-experiment reporting gains from structured offloading. Direction of risk is sufficient to design against; effect sizes UNVERIFIED.

### Calibration Engine — predicted-vs-actual as a first-class product metric   `ESTABLISHED`

**Why it matters.** The artifact hands maximum strategic autonomy ('Child-designed: self-build mode', 'Democratic module sequencing') to the learners with the least accurate self-monitoring, which is the known recipe for choosing rereading over retrieval. Measuring and correcting calibration is the mechanism that makes the agency principle survive contact with the evidence — autonomy earned on demonstrated calibration rather than assumed at intake.

**What to build.** Four mechanics, all cheap: (1) PRE-ITEM PREDICTION — before each quiz item, a two-tap 'will I get this right?'; (2) PRE-SCORE PREDICTION — before seeing results, 'what did I score?'; (3) CALIBRATION SCORE — mean absolute deviation between predicted and actual (or Brier score), displayed next to accuracy with equal prominence and tracked over time; (4) GUARDRAIL — when overconfidence exceeds a threshold on a content area, the system temporarily removes the strategy choice for that content and schedules retrieval instead of rereading, with a one-line plain-language explanation to the student. Report calibration improvement as a primary Phase 1 pilot outcome. Add a calibration criterion to the MCST certification exam, which no competitor in the gap-analysis table has.

**Evidence.** Karpicke, Butler & Roediger (2009), Memory 17(4), 471-479 — majority report rereading, few self-test; attributed to illusions of competence (specific percentages UNVERIFIED at primary; a 2019 reexamination argues the rereading framing overstates it). Kornell & Bjork (2007) on self-regulated study choices. Dunlosky et al. (2013), PSPI — the low-utility techniques are among the most commonly chosen by students. Nelson & Narens (1990) for why monitoring quality determines control quality.

### Delayed, cue-only judgments of learning — a 2-3 day build that improves every downstream agent decision   `ESTABLISHED`

**Why it matters.** This is the highest ratio of evidential pedigree to engineering cost anywhere in the artifact. It improves the FSRS scheduler's input, generates the calibration data for free, and traces to a 1991 primary source in Psychological Science — exactly the kind of claim that survives a grant panel.

**What to build.** After a study block, wait (minutes to hours, or until the next session opens), then present each item's CUE ONLY with the answer hidden and ask a two-tap 'will you remember this tomorrow?'. Feed the DELAYED judgment, never an immediate one, into the FSRS scheduler and into the Learning Path Agent's control decisions. Surface prediction-vs-outcome the next day. Critical implementation detail from the primary literature: the cue must be the stimulus ALONE — showing the stimulus-response pair destroys the effect, and a careless UI that displays the answer while asking for the judgment ships the foresight bias instead of correcting it.

**Evidence.** Nelson & Dunlosky (1991), Psychological Science 2(4) — the delayed-JOL effect. Dunlosky & Nelson (1992), Memory & Cognition — robust effect with stimulus-alone cues (all 45 subjects), little or none with stimulus-response pair cues. Dunlosky & Nelson (1994) — delayed JOL accuracy exceeded immediate in every condition. CAVEAT: a competing memory-based account attributes part of the effect to spaced re-exposure rather than improved metamemory; the mechanism is contested but the prescription (ask later, cue-only) is unaffected.

### Illusion Countermeasure Table — one row per illusion, one shipped feature each   `ESTABLISHED`

**Why it matters.** The artifact's 'PhD-level' framing is currently a label. A table that names four specific documented illusions and pairs each with a specific implemented countermeasure is what PhD-level actually looks like, and it is defensible line by line in front of any reviewer. It also replaces 'Know Your Mind' self-assessment, which in its current form amplifies the very illusions it should be correcting.

**What to build.** Four rows, published in the Course Design tab and implemented in product:
FLUENCY (smooth processing feels like learning) → no 'does this make sense?' checks anywhere; every confidence judgment is followed by a retrieval item. Applies with special force to AI explanations, which are maximally fluent.
STABILITY BIAS (under-predicting both forgetting and the benefit of further study) → display the student's own forgetting curve from their FSRS data; make all judgments at a delay.
FORESIGHT BIAS (judging while the answer is visible) → all confidence judgments cue-only, answer hidden, enforced in the component library so no screen can violate it.
ILLUSION OF EXPLANATORY DEPTH (believing you can explain a mechanism you cannot) → weekly 60-second aloud explanation from memory, scored against the criterion idea list, gap shown to the student. This promotes the artifact's existing Feynman/protégé content (Module 10) from a teaching technique to a calibration probe, which is its sharpest use.

**Evidence.** Fluency and illusions of competence: Karpicke, Butler & Roediger (2009). Stability bias and foresight bias: the Koriat and Bjork judgment-of-learning literature — the PHENOMENA are ESTABLISHED; I have not re-verified the exact article and year for each in this pass, so cite from primary sources before publishing. Illusion of explanatory depth: Rozenblit & Keil (2002), Cognitive Science.

### Socially Shared Regulation (SSRL) spec for the Ubuntu Learning Circle   `ESTABLISHED`

**Why it matters.** The founder's cultural instinct here is sound and the research makes it stronger, not weaker. SSRL supplies an operational definition, a measurement approach, and a fifteen-year literature — which converts a ritual into a designable, measurable, publishable intervention and removes a false novelty claim that would otherwise cost credibility with any research-literate reader.

**What to build.** Replace the unspecified 'collective metacognitive reflection' with a five-step Circle protocol, run weekly in the cohort: (1) the group sets a shared goal for the week; (2) each member privately records a confidence judgment on the shared content; (3) the DISTRIBUTION of judgments is shown to the group without names — disagreement is the signal that drives discussion and it is the mechanism that makes individual illusions visible socially; (4) the group jointly selects the next strategy, using the four control moves from the metacognition module; (5) the following week the group reviews whether it worked. Measure GROUP-level calibration and group-level strategy quality, not satisfaction.
And fix the gap-analysis claim: replace 'metacognition has never been connected to collective knowing' with the accurate and stronger framing — 'socially shared regulation of learning is a well-developed construct (Hadwin, Järvelä & Miller) that has not been operationalised for Black middle-school students, nor connected to Ubuntu as an indigenous articulation of the same insight; that is our contribution.'

**Evidence.** Hadwin, Järvelä & Miller (2011), in Zimmerman & Schunk (Eds.), Handbook of Self-Regulation of Learning and Performance, pp. 65-84; 2nd ed. (2018) in Schunk & Greene (Eds.), pp. 83-106. Järvelä & Hadwin (2013), Educational Psychologist. Panadero & Järvelä (2015), European Psychologist, SSRL review. Key distinction: co-regulation = individual regulation prompted/supported by others; SSRL = the group regulating its collective activity. CAVEATS: the co-regulation/SSRL boundary is contested and may be moderated by group dynamics and expertise asymmetry; terminology is inconsistent across the literature (socially shared regulation vs. socially shared metacognition). I worked from secondary descriptions of these primary works.

### SRSD as the delivery model for the whole metacognition and note-taking track   `ESTABLISHED`

**Why it matters.** The artifact invents its instructional sequence. SRSD already specifies a validated one, developed for and tested with students with learning disabilities and ADHD. Adopting it costs nothing, removes the need to defend a homemade sequence, and gives the founder the strongest named evidence base in special education to put in front of MCPS — provided he also states the base's main limitation himself.

**What to build.** Restructure every module in the student, parent and paraeducator tracks to the six SRSD stages rather than to a lecture-plus-quiz shape: (1) DEVELOP background knowledge — what the strategy is and why it works; (2) DISCUSS IT — current performance examined, student commits to using it (this is where the calibration baseline lands); (3) MODEL IT — think-aloud demonstration, including the self-talk, which is the stage most often skipped and most responsible for the effect; (4) MEMORIZE IT — the strategy mnemonic, to automaticity; (5) SUPPORT IT — guided practice with explicit, scheduled fading, mapped directly onto the Tier 1→4 note-taking fade; (6) INDEPENDENT PERFORMANCE with maintenance checks. Include the self-regulation components SRSD specifies: goal-setting, self-monitoring, self-instruction, self-reinforcement. In any external document, state the caveat yourself: most of the foundational meta-analytic evidence comes from the developers' own research group.

**Evidence.** Graham & Harris (2003), 'Students with learning disabilities and the process of writing: A meta-analysis of SRSD studies,' in Swanson, Harris & Graham (Eds.), Handbook of Learning Disabilities — 18 studies, 14 authored by Harris and Graham themselves with the remainder by students and colleagues. Graham, Harris & McKeown (2013) update, 2nd ed. A 2013 component analysis put the added value of the explicit self-regulation component at ~0.48 SD from five comparison studies. The frequently quoted 1.17 writing-quality effect is attributed inconsistently across sources and is UNVERIFIED — read the primary papers before quoting it.

### Matrix notes as the mandated format for comparative content   `EMERGING`

**Why it matters.** Comparative content is pervasive in grades 6-8 (compare three branches of government; compare mitosis and meiosis; compare two characters' motivations) and linear outlines handle it badly, because an outline forces a sequential walk through items when the learner needs to see dimensions aligned across items. This is a specific, implementable Kiewra finding that the artifact's outline-method entry misses entirely while misattributing itself to Ausubel.

**What to build.** A mobile matrix widget: rows = items being compared, columns = dimensions of comparison, cells = the content. Pre-populate the row and column headers as a guided-notes scaffold at Tier 1 (headers given, cells blank), fade to headers-only at Tier 2, then to student-constructed at Tier 3. Auto-detect comparative content in the source and prompt the format. Score cell completeness against the criterion list. Critically: generate retrieval cards BY COLUMN as well as by row — asking 'on dimension X, how do items A, B and C differ?' is the question the matrix format makes askable and the outline format does not, and it is the question tests actually ask.

**Evidence.** Kiewra's programme on graphic organisers and matrix notes outperforming linear outlines for comparative content. Nesbit & Adesope (2006) and Schroeder et al. (2017) for the broader node-link/structured-representation evidence, with construction (g = 0.72) outperforming studying provided representations (g = 0.43) — which is why the fade from provided headers to student-constructed matters. I did not retrieve a standalone meta-analysis of matrix notes specifically; the specific comparative-content superiority claim rests on Kiewra's experimental programme and should be cited to those primary studies.

### Cross-cultural calibration and international reflection practices — honest framing for the cultural track   `SPECULATION`

**Why it matters.** The founder wants the cultural content to rest on research. There IS relevant comparative work on calibration differences across cultures and there ARE well-documented institutional reflection practices internationally — but the evidence is thinner and more contested than the artifact's confident tone implies, and the honest version is more useful than an overclaim that a reviewer dismantles.

**What to build.** A short, carefully hedged research note backing the cultural track:
(a) CALIBRATION ACROSS CULTURES — comparative studies report differences in overconfidence between East Asian and Western samples, but findings are mixed, confounded with task type, response-scale use and sampling, and I did not verify any specific result in this pass. Position this as a RESEARCH QUESTION MindUnlock will investigate in its own cohort (do calibration profiles differ, and does stereotype threat interact with confidence judgments?) rather than as a settled finding to build on. That is both honest and a genuine contribution — calibration data on Black neurodivergent middle schoolers essentially does not exist.
(b) HANSEI (Japanese structured reflection on shortcomings, embedded in schooling and in workplace practice) and JUGYOU KENKYUU / lesson study (collaborative lesson observation and revision, now adopted internationally as teacher PD) — these are strong models for the MMEC teacher track and for the Circle's review step, and lesson study in particular is a well-documented practice with international adoption. Chinese FANSI (self-examination/reflection) belongs in the same comparative frame.
FRAME ALL OF IT as: these are culturally embedded institutional practices with structural similarity to what the research calls socially shared regulation; we are borrowing STRUCTURE, not claiming validated effects. State plainly that effect-size evidence for hansei and fansi as learning interventions is not something I verified and may not exist in that form.

**Evidence.** Hadwin, Järvelä & Miller (2011) and Panadero & Järvelä (2015) for SSRL as the construct these practices instantiate. Lesson study's international adoption as teacher professional development is well documented; its effect on student outcomes is contested and I did not verify it here. Cross-cultural calibration/overconfidence differences: SPECULATIVE as applied to this population — I verified no specific finding in this pass and none exists for Black neurodivergent US middle schoolers so far as I know. Hansei and fansi as described: EXPERT-OPINION / cultural description, not an intervention evidence base.

### Evidence ledger — one row per claim, shipped as a product document   `INFERENCE`

**Why it matters.** The artifact contains at least six effect-size claims I could not source and two that are contradicted by major reviews, inside a document whose founder's stated principle is 'no claims of validation that has not occurred.' A ledger is the mechanism that makes the principle operational rather than aspirational, and it is the single artifact most likely to win over a skeptical district research office or IES panel — nobody else in the gap-analysis table has one.

**What to build.** A spreadsheet-backed table, published, with one row per empirical claim made anywhere in MindUnlock materials, and these columns: CLAIM (verbatim as it appears) | PRIMARY CITATION (author, year, journal, volume, pages — no secondary sources, no blogs) | POPULATION STUDIED | COMPARISON CONDITION | OUTCOME MEASURE | RETENTION INTERVAL | EFFECT SIZE WITH METRIC | REPLICATION STATUS | TIER (ESTABLISHED / EMERGING / EXPERT-OPINION / INFERENCE / SPECULATION) | WHERE USED.
Ship rule: any claim without a filled PRIMARY CITATION and OUTCOME MEASURE does not appear in any external document. Apply it first to the eight 'Research Foundation' entries at lines 458-466 and to the six note-taking entries at lines 501-506; on current evidence roughly half will not survive, and cutting them is the single largest credibility gain available this week. Assign a named owner and review it before each phase gate.

**Evidence.** This is a process recommendation, not an empirical claim. It derives from the founder's own stated operating principles (evidence before claims; no claims of validation that has not occurred) applied to the artifact's own content, and from the specific unverifiable claims catalogued in finding EV-01.


---

## Open questions

- Is the stated pedagogical context lecture-based at all? Most of the note-taking evidence base (Kiewra, Boyle, guided notes, the laptop/longhand studies) concerns LECTURE note-taking. If MCPS grade 6-8 instruction is predominantly activity-, discussion- or worksheet-based, large parts of this literature transfer only partially, and the curriculum should be re-anchored on reading notes and discussion notes instead. The artifact never states what students are actually taking notes ON.
- What is the pooled effect size in the K-12 guided notes meta-analysis (ERIC EJ1001064), and what is Konrad, Joseph & Eveleigh's (2009) reported effect? I could not retrieve either PDF because files.eric.ed.gov does not resolve in this session's network settings — that host would need to be allowed before these numbers can be quoted to a district or a grant panel.
- Is there a primary Kiewra source for the widely repeated '~1/3 of important ideas' completeness figure, or is it a secondary-literature artifact? Everything I found traced to blog summaries. If no primary source exists, the Note Quality Score should be introduced with the founder's own baseline data rather than with a borrowed statistic.
- Has Boyle's middle-school Strategic Note-Taking RCT (n = 40) been independently replicated outside his research group, and did the IES-funded inclusive-classroom extension publish outcomes? This determines whether Tier 2 can be labelled EVIDENCE-BASED or must stay PROMISING.
- Does any controlled study exist of learner-GENERATED visual notes (as opposed to instructor-provided multimedia) testing Mayer's coherence principle? The constrained-visual-notes spec rests on an extension of multimedia-learning findings to student production, which is reasoning rather than a direct finding.
- What does calibration look like in Black, neurodivergent US middle schoolers? I am not aware of any dataset. If none exists, the 10-family pilot could produce the first — which is both a publishable contribution and the strongest possible answer to the artifact's 'PhD-level' framing.
- Does stereotype threat interact with confidence judgments — i.e. does identity threat produce UNDER-confidence in a population the general literature characterises as over-confident? If so, the Calibration Engine's guardrail logic (which currently assumes overconfidence) would need a symmetric branch, and this is a genuinely novel research question sitting at the intersection of the founder's two commitments.
- Is the AI Notes Contract compatible with the IEP accommodation 'Multiple Expression — Audio, video, drawing, or text for ALL demonstrations' (line 556)? A student whose IEP specifies scribing or dictation needs the AI to transcribe, and the line between transcribing a student's own words (permitted) and composing for them (prohibited) needs a written adjudication rule before any IEP-governed student uses the feature.
- Does MCPS have an existing district-adopted note-taking or study-skills framework (e.g. AVID's WICOR, which mandates Cornell notes)? If AVID is in use in the target schools, demoting Cornell is a political problem as well as an evidential one, and the Tier 3 framing ('Cornell's review protocol, applied to any format') becomes the diplomatic path — but this needs checking before the district presentation in Phase 3.

