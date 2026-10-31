# Verification

What survived adversarial checking, and what did not.

---

## What ran, and what did not

The audit was designed so every lens would be attacked by a **skeptic** (checking every
citation, statute number and figure independently against primary sources) and, for the four
high-stakes lenses, by a **practitioner** (checking whether a finding is true in the real
operating environment or only on paper).

Three attempts were made. The verification stage hit a usage limit each time.

| Lens | Skeptic | Practitioner |
|---|---|---|
| Research integrity (`20-`) | **ran - results below** | did not run |
| Red team (`30-`) | did not run | did not run |
| Blue team (`31-`) | did not run | did not run |
| MCPS special education (`40-`) | did not run | did not run |
| Learning science (`50-`) | did not run | - |
| Note-taking & metacognition (`51-`) | did not run | - |
| Systems & cost (`60-`) | did not run | - |
| Code & accessibility (`70-`) | did not run | - |
| Business reality (`80-`) | did not run | - |

The cross-lens synthesis stage also did not run.

**The code and accessibility audit (`10-`) is the exception**: every claim in it was measured
directly - contrast ratios computed from the actual composited colour values, axe-core run
against the rendered pages, and the full CI job executed locally. It needs no verification
because it reports measurements rather than judgements.

---

## The error rate you should assume

One lens was verified. The skeptic's bottom line on it:

> Roughly **60%** of the lens's findings survive adversarial checking intact, about **25%**
> survive in **weakened form**, and a handful of its supporting citations and remedies would
> themselves fail the verification gate it proposes.

Six of 23 findings were refuted outright or materially corrected; seven were independently
confirmed and strengthened; six substantive items the lens should have caught were missed.

That is the correction rate on the lens whose *entire job* was citation accuracy, run by an
auditor with the same tools. **Assume at least that rate on the eight unverified lenses**, and
do not carry any specific number, statute section or legal conclusion from them into a grant
application, an investor conversation or a district meeting without reading the primary source
yourself.

The most instructive failure: **the lens introduced a brand-new false product claim inside its
own recommended fix.** It told the founder to publish that FSRS "is Anki's default scheduler."
It is not - Anki's maintainer opened issue #3616, *"Make FSRS the default?"*, in December 2024,
and it was still open in August 2026. A document whose disease is unverified product claims was
nearly handed a fresh one by its own auditor. That is the strongest available argument for why
verification is not optional.

---

## Corrections to the research integrity lens

### RI-02 - "Anki SM-18" does not exist: SM-18 is proprietary SuperMemo; Anki's current default is FSRS

**Why it did not survive**

The finding is two claims welded together. The first is correct and I confirmed it. The second — "since Anki 23.10 (October 2023) the default scheduler has been FSRS" — is false, and it is the claim the lens turns into recommended replacement copy for the founder.

I fetched github.com/ankitects/anki/issues/3616 directly. Title: "Make FSRS the default?". Opened 2024-12-06 by dae (Damien Elmes, Anki's maintainer). Still OPEN; moved to "Solution Spec" on 2026-08-19; an August 2026 comment asks whether the switch is "essentially dead-in-the-water." A maintainer would not file a December 2024 proposal to make FSRS the default if it had already been the default since October 2023. The fsrs4anki project's own tutorial, which the lens cites as its evidence, describes enabling FSRS through deck options in "Anki 23.10 or newer" — that is opt-in language, and the lens read it as a default. Third-party guides split between 23.10, 25.07 and "new profiles only," which is itself a signal that no clean default date exists. HandWiki and SuperMemopedia both state SM-2 (in modified form) is what Anki uses.

The consequence is specific. RI-02's recommendation tells the founder to publish: "FSRS ... the open-source algorithm that is Anki's default scheduler," and to rewrite line 226 as "Anki — strong open-source FSRS scheduler." Adopting that text replaces one false product claim with another, in the one document whose stated remedy is that product claims be "verified against that product's current official documentation" (the lens's own addition #10, gate 4). The lens's open_questions entry concedes it could not reach docs.ankiweb.net — I could not either, that host is outside this session's allowed network domains — but it wrote the assertion into the recommendation anyway rather than leaving it flagged.

Also incorrect in the evidence block: the lens says "SuperMemo Help confirms SM-19 and later versions" while elsewhere treating SM-18 as current. SuperMemo Help documents SM-19; Wikipedia reports SM-20 (2026). Neither changes the core.

**What survives**

SURVIVES, narrowed: "'Anki SM-18' names two unrelated products. SM-18 is Piotr Woźniak's proprietary SuperMemo algorithm — supermemo.guru states it 'is currently in use only in SuperMemo 18 for Windows' — and SuperMemo has since shipped SM-19 and SM-20. Anki has never implemented it; Anki uses a modified SM-2, which SuperMemopedia confirms is the one SuperMemo algorithm that is open to the public and needs no licence. Anki also ships FSRS (Free Spaced Repetition Scheduler), open-source and trained on large review datasets, which users can enable in deck options from Anki 23.10 onward. Whether FSRS is on by default has changed across versions and profiles and is UNVERIFIED as of this audit — ankitects/anki issue #3616, 'Make FSRS the default?', opened by the maintainer in December 2024, remains open as of August 2026, which indicates SM-2 is still the shipped default. Do not write 'Anki's default scheduler' in any outward-facing copy until docs.ankiweb.net has been read directly. Separately, 'AnkiConnect sync' (line 679) names a third-party add-on that requires the Anki desktop client running locally; it is not a server-to-server API and cannot back a mobile product. Replace with '.apkg import/export.' Before vendoring anything: Anki itself is AGPL-3.0, which the lens did not mention and which materially constrains a closed-source commercial product."

---

### EXEC-SUMMARY - "INVENTED NUMBERS PRESENTED AS FINDINGS ... None traces to the cited source" (applied to 43%, 50%, 2×, 15–20%, 40%, ES 0.8, 73%, 38%, 85%, 60–90%, 90%)

**Why it did not survive**

The blanket "None traces to the cited source" is false for at least two of the eleven numbers, and the lens's own RI-18 says so — making the executive summary and the finding body inconsistent with each other. An investor or IES reviewer who checks one number will check the easiest one, and the easiest two are the ones the summary gets wrong.

(a) "43%" (line 461, interleaving). I searched for Rohrer & Taylor (2007), Instructional Science 35(6):481–498, 'The Shuffling of Mathematics Problems Improves Learning'. The widely reported Experiment 2 result is 63% accuracy on the one-week delayed test for mixed practice versus 20% for blocked — a 43-percentage-point gap. I could not open the paper's own tables (uweb.cas.usf.edu is outside this session's allowed domains), so the exact table values remain unverified, but the arithmetic coincidence is not plausibly accidental. The number traces; it is mislabelled, not invented.

(b) "50%" (line 460, retrieval practice). Roediger & Karpicke (2006), Psychological Science 17(3):249–255. The one-week retention figures commonly reported from Experiment 1 are 61% (repeated testing) versus 40% (repeated study) — a ~52% relative increase. "50% greater retention than re-reading" is a defensible relative restatement of the study the artifact actually cites. Again unverified at the table level from primary text, but it traces.

This matters beyond pedantry. RI-18's own recommendation is correct — strip the multipliers, keep the effects, add tier badges — and it would be adopted on its merits. The executive summary's charge of fabrication is a stronger and falsifiable accusation that the founder would carry into a room and lose.

What I did confirm: the "2×" for spacing is genuinely untraceable. Cepeda, Pashler, Vul, Wixted & Rohrer (2006), Psychological Bulletin 132(3):354–380, DOI 10.1037/0033-2909.132.3.354, tallies "839 assessments ... in 317 experiments located in 184 articles" — the lens's figures are exact — and its stated main finding is the interaction between inter-study interval and retention interval, with optimal spacing widening as the retention period lengthens. No blanket retention multiplier appears.

**What survives**

"Three defect classes in the quantitative claims, not one. (i) FABRICATED — no source contains them and none was located: 73% of MCPS families (165), 85% of interventions (164), ES 0.8 (465), 40% intrinsic motivation (168, 466), 90% faster study (75, 338, 400, 531), 15–20% stereotype-threat suppression (464), 60–90% speed increase (483). (ii) MISREPORTED — the number traces to the cited study but the unit or scope is wrong: '43%' is a 43-percentage-point gap between conditions in one experiment restated as a 43% improvement; '50%' is a relative restatement of a single one-week contrast presented as a general law. (iii) UNTRACEABLE TO THE SOURCE GIVEN — the effect is real but the citation does not report that figure: '2× retention' from Cepeda et al. (2006), whose finding is the ISI × retention-interval interaction; '38% debilitating test anxiety' from Zeidner (1998). Class (i) must be deleted. Class (ii) must be corrected to the actual contrast with its condition, delay and sample stated, or deleted. Class (iii) must be re-sourced or made magnitude-free."

---

### RI-11 - Growth Mindset is cited from Dweck (2006) with no mention of the replication record

**Why it did not survive**

The finding is correct; its evidence block is not, and it fails in the specific way the lens indicts the artifact for.

The lens writes: "Sisk, V.F., Burgoyne, A.P., Sun, J., Butler, J.L. & Macnamara, B.N. (2018). Psychological Science 29(4):549–571 — k=273, N=365,915; intervention d=0.08 [0.02, 0.14] — verified." I searched the paper. The citation, journal, volume and pages are right. The k is not. Meta-Analysis 1 comprised 129 studies yielding 162 independent samples and 273 effect sizes, N = 365,915. "273 studies" inflates the study count by a factor of ~2.1 by counting effect sizes as studies. The lens's narrative compounds this by saying "273 studies, N≈366,000 for the mindset-achievement correlation" and then separately "43 intervention studies, N≈57,000."

I could not independently verify the Meta-Analysis 2 figures at all. The sources I could reach describe the first meta-analysis's correlation as weak but do not report d = 0.08, its CI, or the k = 43 / N ≈ 57,000 breakdown. alexanderpburgoyne.com and pubmed.ncbi.nlm.nih.gov are both outside this session's allowed network domains, so I could not read the results section. The lens marked these "verified." They are not verified here, and the lens's track record on the k figure in the same sentence is reason not to take the d on trust.

The lens does correctly caveat Yeager et al. (2019) as unverified. It should have applied the same caution one line earlier.

**What survives**

SURVIVES with corrected numbers and an explicit unverified flag: "Citing Dweck (2006), a trade book, for an effect claim and omitting the replication record is overstatement. Sisk, Burgoyne, Sun, Butler & Macnamara (2018), Psychological Science 29(4):549–571, ran two meta-analyses; the first drew 273 effect sizes from 129 studies and 162 independent samples (N = 365,915) and found the mindset–achievement correlation weak. The second meta-analysed intervention studies and reports a small pooled effect; the frequently quoted d ≈ 0.08 and its confidence interval are UNVERIFIED in this audit and must be read off the paper's Meta-Analysis 2 results table before publication. Macnamara & Burgoyne (2023), Psychological Bulletin, is cited as an independent replication of a similar magnitude — also unverified here. Yeager et al. (2019), Nature 573:364–369, a large preregistered US RCT, found a small GPA effect concentrated in lower-achieving students — magnitude unverified. The honest summary the artifact should adopt: real but small, plausibly largest in the low-SES and academically at-risk population this product serves, dependent on implementation fidelity. Do not publish any of the three point estimates until each is read from the source."

---

### RI-13 - TAM figures are stale: "6.4M students with IEPs" understates the current IDEA count

**Why it did not survive**

The finding is right and the remedy is not. The lens's recommended replacement headline is "~8.19M children ages 3–21 served under IDEA Part B nationally," citing a Council for Exceptional Children analysis giving 8,194,424 (+3.8%, +301,991).

I checked. Congressional Research Service report R41833, on congress.gov, states that in the 2023–2024 school year approximately 7.9 million children ages 3 through 21 received services under IDEA Part B. The CEC figure of 8,194,424 is labelled only "2024" and I could not reconcile it against the official count from any source I could reach — it may be a later release, a different age span, or a different denominator. The Department of Education's own 2023-24 Part B Child Count static tables and state-level data file are published on catalog.data.gov and are the authoritative source; I did not download and total them.

So the lens's fix hands the founder a headline TAM number that is ~4% above the official federal figure, unreconciled, in a finding whose entire point is that unchecked numbers destroy diligence credibility. That is the same defect one level up. The lens's own addition #10, gate 2 — "every number is located in a named table/figure/page of a named source, or is deleted" — was not applied to the lens's own replacement text.

The core finding stands: 6.4M corresponds roughly to the Part B count circa 2010–11 and understates the current figure by more than 20%. The "74M K-12 parents" and "1.3M paraeducators" critiques stand as written.

**What survives**

SURVIVES, with the replacement number changed: "TAM figures are stale or unsourced. '6.4M students with IEPs' (line 245) is roughly the IDEA Part B count from around 2010–11 and understates the current figure by over 20%. Use the federal number with its source and retrieval date: approximately 7.9 million children ages 3 through 21 served under IDEA Part B in 2023–24 (CRS R41833, congress.gov), or total it yourself from the Department of Education's 2023-24 Part B Child Count static tables on catalog.data.gov. A Council for Exceptional Children analysis reports 8,194,424 for '2024'; that figure cannot be reconciled against the official 2023-24 count from publicly reachable sources and should not be used as a headline without identifying which release and age span it covers. '74M K-12 parents' has no source and appears to be the US under-18 population, which counts children, not parents. '1.3M paraeducators' is uncited; pick BLS OEWS 25-9045 or NCES instructional-aide FTE, name which, and give the retrieval date. Rule: every TAM number carries its source and retrieval date inline — including numbers supplied by an auditor."

---

### RI-06 - "Wade Cutler's Triple Reading Speed" and "60–90% speed increase" contradict the reading-science consensus

**Why it did not survive**

The finding's spine is CONFIRMED and I am not refuting it — Rayner, Schotter, Masson, Potter & Treiman (2016), Psychological Science in the Public Interest 17(1):4–34, DOI 10.1177/1529100615623267, is exactly as the lens describes it, and I verified the speed–accuracy tradeoff conclusion in Schotter's own words. Two supporting sub-claims do not hold and should be struck before the founder repeats them.

(a) "a 1980s trade paperback." Wrong. Simon & Schuster's publisher page and the book's own copyright page give editions © 1970, 1988, 1993, with the 4th edition in 2002 (ISBN 9780768909036 / 9780743475761). It is a 1970 book with a 2002 fourth edition, still commercially in print. The lens's dating would be corrected in the first thirty seconds of a pushback, which weakens a finding that does not need weakening.

(b) "no evidence Cutler holds the doctorate some editions advertise." I searched specifically for Cutler's credentials and found no source asserting a doctorate and no source denying one. The lens has introduced an insinuation about a named private individual that rests on nothing, inside an audit whose governing rule is that absolute claims require a documented search. It is also strategically useless — the argument is won on Rayner et al., not on Cutler's CV.

What I did confirm and the lens could have used: the publisher's only evidentiary support is the self-reported claim that the method was taught to "over 10,000 persons ... primarily in the Southwest between the mid-1960s and early 1970s." That is attendance, not outcome. No controlled study of Acceleread surfaced.

**What survives**

SURVIVES, with the two sub-claims deleted: "'Wade Cutler's Triple Reading Speed' (line 483; also 167, 338 Module 6, 423, 531, 774) is the Acceleread method from Wade E. Cutler's trade book Triple Your Reading Speed (Simon & Schuster; © 1970, 1988, 1993; 4th ed. 2002). No peer-reviewed trial of the method was located; the publisher's only support is a self-reported claim that it was taught to over 10,000 people in the Southwest between the mid-1960s and early 1970s, which is attendance, not outcome. The specific claim — '60–90% speed increase with equal or greater comprehension' — is the claim the field's authoritative review rejects. Rayner et al. (2016, PSPI 17(1):4–34) conclude there is a speed–accuracy tradeoff, that eye movements account for no more than ~10% of reading time, that removing the ability to reread worsens comprehension, and that rate is driven by language skill and vocabulary rather than eye-movement training. This matters doubly because line 41 targets 'students with literacy deficits' and line 167 correctly cites Scarborough's Reading Rope — structured literacy, not speed training, is the indicated support. Keep the three-pass structure, which is SQ3R-family previewing and has modest comprehension support; drop the branded attribution and every speed number. Make no claim about the author."

---

### ADD-05 - Addition: "A real competitive-scoring rubric ... This is literally what Behaviorally Anchored Rating Scales are for (Smith & Kendall, 1963) — the technique the artifact misattributed to NASA"

**Why it did not survive**

Rhetorically satisfying, methodologically wrong, and self-undermining given the audit it closes.

I verified Smith & Kendall (1963), Journal of Applied Psychology 47(2):149–155, DOI 10.1037/h0047060, 'Retranslation of expectations: An approach to the construction of unambiguous anchors for rating scales'. The method is a procedure for rating the job performance of PEOPLE: subject-matter experts generate critical incidents of job behaviour, a second independent group retranslates them back into performance dimensions and levels, and only incidents a clear majority place consistently survive as anchors. It is a personnel-appraisal scale-construction technique. It is not a framework for evaluating competing software products, which have no job behaviours and no incident pool, and for which there is no retranslation step to perform.

What the lens actually wants in addition #5 — a pre-specified dimension set, written 0–3 behavioural level descriptors, explicit weights, two raters and an agreement statistic — is good practice for any structured rubric and borrows the word "behaviourally anchored" loosely. That is fine as a design, but claiming it is "literally what BARS are for" asserts a methodological pedigree the technique does not confer, in the closing paragraph of an audit whose headline finding is that this document borrows authority it has not earned. If the founder repeats the line to a methodologist, it lands as the same move in a different costume.

Note also that RI-01's recommendation already makes the correct, narrower version of this point — that BARS would be a legitimate fit for the certification rubrics at lines 345 and 430, which DO rate human performance. Addition #5 then overreaches past it.

**What survives**

"Replace the 'Meets Our Needs' percentages with a structured rubric: ten dimensions derived from parent and student interviews rather than from the MindUnlock roadmap, each with written 0–3 level descriptors and an explicit weight summing to 1.0, two independent raters, a reported agreement statistic, the evaluation date and product version, and the filled scoring sheet published. Report weighted scores with the sheet attached, never a bare percentage. This is ordinary structured-rubric practice; it is not Behaviorally Anchored Rating Scales, which are a method for rating the job performance of people (Smith & Kendall, 1963, J. Applied Psychology 47(2):149–155) and have no retranslation analogue for competitor products. The legitimate place to use BARS, correctly cited, is the certification performance rubrics at lines 345 and 430, where humans are being rated — and nowhere else."

---

## Findings independently confirmed

### RI-01 - "NASA BARS Method" is a confabulation; BARS is a 1963 HR rating technique, not a NASA scheduling system

**How it was verified.** Three independent checks. (1) I confirmed the real BARS: Smith & Kendall (1963), 'Retranslation of expectations: An approach to the construction of unambiguous anchors for rating scales,' Journal of Applied Psychology 47(2):149–155, DOI 10.1037/h0047060 — volume, issue and pages corroborated by the APA DOI record, PsycNET record 1963-07981-001, and a SciELO reference list. The method is critical-incident collection plus retranslation by an independent rater group, for personnel appraisal. (2) I searched for any NASA BARS and for 'behaviorally anchored rating scale' on NASA's technical report server. Nothing. The second search returned no NASA documents at all; the first returned only commercial HR vendor glossaries, none NASA-connected. (3) I searched specifically for a NASA 15-minute-block scheduling method named BARS. The closest real things are unrelated and contradict the artifact's specification: ISS crew timelines are logged in 5-minute increments, not 15; a NASA ISS blog post records astronaut Don Pettit keeping personal 5-, 15- and 30-minute task lists, which is an individual practice, not a NASA method; a NASA Johnson Space Center oral history describes ground-side flight planners timelining crew days. None is called BARS.

**Strengthened evidence.** The confabulation is load-bearing across six separate places in the artifact, which the lens enumerated correctly: line 482 defines it, lines 75 and 94 ship it as a student feature and a Week 3–5 build task, line 338 makes it Module 7 of a certification, line 404 makes it paraeducator competency domain 8 inside the $299 MCLSS, line 530 makes it an app surface, and line 596 makes it an AI agent. Line 137 is the worst: it instructs a Research Agent to 'Synthesize NASA BARS + learning science literature.' There is no such literature, so the agent will generate one — a citation-fabrication loop inside a document whose line 118 promises 'citations required; zero-tolerance for unverified academic claims.' I add one detail the lens did not note: the artifact's expansion of the acronym, 'Behavioral Anchoring / Mission-Critical Task Scheduling,' back-forms B-A from the genuine term and invents S for scheduling, which is the signature of a name reverse-engineered from a half-remembered acronym rather than drawn from any source. Severity blocker is correct — this is the single item most likely to end a grant review or a district meeting, because 'NASA' is the easiest word in the document for a reviewer to check.

### RI-04 - "African-Centered Pedagogy ... (ES: 0.8)" — the effect size is invented and it displaces a real, strong body of evidence

**How it was verified.** I verified the replacement literature the lens proposes, because that is what makes this finding actionable rather than merely corrective. Dee, T.S. & Penner, E.K. (2017), 'The Causal Effects of Cultural Relevance: Evidence from an Ethnic Studies Curriculum,' American Educational Research Journal 54(1):127–166, NBER working paper w21865, ERIC EJ1132535, Stanford CEPA. The reported effects are exactly as the lens states: assignment to the ninth-grade ethnic studies course increased attendance by 21 percentage points, GPA by 1.4 grade points, and credits earned by 23. I also confirmed the design and two caveats the lens handled honestly: it is a fuzzy regression discontinuity exploiting an eighth-grade GPA assignment threshold in several San Francisco high schools, and the GPA and credits outcomes deliberately exclude the ES course, other social studies and PE to avoid confounds. The authors themselves flag the effects as 'surprisingly large' and attribute them partly to reduced dropout rather than purely to performance gains among enrolled students.

**Strengthened evidence.** The lens is right that this is the artifact's most self-defeating error, and I can sharpen why. Line 465 credits Hilliard (1997), Nobles (2006) and Asante (1987) with 'ES: 0.8'. Those are works of philosophy and epistemology; none is an intervention study; none reports an effect size. 0.8 is Cohen's conventional large-effect threshold, which is the texture of a placeholder. Meanwhile the artifact's own line 120 lists 'Cultural appropriation of African-centered content' as a High risk and names 'African-centered scholars as PAID co-developers' as the mitigation — so the people whose participation the project depends on are precisely the readers most likely to notice that three foundational theorists have been credited with a number none of them produced. The lens's recommended two-layer split (theory cited as theory; Dee & Penner and Bonilla, Dee & Penner cited as outcome evidence with scope limits stated) is correct and I would add one constraint: Dee & Penner is a high-school result from one high-fidelity district estimated locally at a cutoff, and the artifact serves grades 6–8, so the transfer is not established and must be labelled as such. The lens's refusal to attach a pooled d to Aronson & Laughter (2016), which is a narrative synthesis rather than a meta-analysis, is the right call and should be preserved.

### RI-09 - "38% of middle schoolers experience debilitating test anxiety (Zeidner, 1998)" — not traceable to the cited source

**How it was verified.** I verified the replacement evidence. von der Embse, N., Jester, D., Roy, D. & Post, J. (2018), 'Test anxiety effects, predictors, and correlates: A 30-year meta-analytic review,' Journal of Affective Disorders 227:483–493, PMID 29156362. The review covers 238 studies from 1988 forward. Two findings quoted in the sources I reached match the lens exactly: test anxiety's effects were 'most pronounced at the middle grades level,' and overall effect magnitudes were 'in the small to moderate range.' It is negatively related to standardized tests, university entrance exams and GPA, with self-esteem a strong predictor. I did not locate any prevalence figure in this paper, consistent with it being a meta-analysis of effects, predictors and correlates rather than an epidemiological study.

**Strengthened evidence.** The strategic argument in this finding is the strongest thing in the whole audit and should be moved up in priority: the real meta-analytic finding is a BETTER opening line for the problem statement than the fabricated prevalence figure, because 'most pronounced at the middle grades level' is precisely the grade band the product targets. Line 41 is the first bullet of the Problem Statement and therefore the single most-quoted sentence in any pitch deck or grant narrative derived from this document; it currently cites a 1998 review monograph for a two-digit US prevalence figure and sharpens it with 'debilitating,' a word with no operational cut score in any instrument. I accept the lens's own honest caveat that the 10–30% and 15–22% ranges it offers as replacement framing were seen in secondary reviews and not traced to primary studies — which is the correct way to handle it, and is exactly the discipline the lens failed to apply to itself in RI-11 and RI-13.

### RI-12 - "Stereotype Threat ... suppress performance 15–20%" — fabricated magnitude on a literature with documented publication bias

**How it was verified.** I verified the contested-literature evidence. Flore, P.C. & Wicherts, J.M. (2015), 'Does stereotype threat influence performance of girls in stereotyped domains? A meta-analysis,' Journal of School Psychology 53(1):25–44. Confirmed: 47 effect sizes on schoolgirls in math, science and spatial tasks; estimated mean d = −0.22, significantly different from zero; no significant moderators; and the authors' own conclusion that there were 'several signs for the presence of publication bias' which 'might seriously distort the literature on the effects of stereotype threat among schoolgirls,' with a call for a large replication. I also found a trim-and-fill-corrected estimate of d ≈ .07, not significantly different from zero, reported in secondary analysis — I flag that as secondary-source, not read from the paper. The lens's framing of the literature as EMERGING/CONTESTED rather than ESTABLISHED is correct.

**Strengthened evidence.** The product consequence is the part worth escalating, and the lens identified it correctly: the artifact does not merely cite a contested effect, it operationalises it as a scored diagnostic construct on individual Black children — item 1.12 'Stereotype threat susceptibility' inside Domain 1 (line 268) and item 4.5 'Stereotype threat vulnerability' inside Domain 4 (line 271) — and then prescribes 'African ancestor activation before every assessment' (line 464) as the countermeasure. That chains a mechanism-specific intervention claim to a contested mechanism and a fabricated magnitude, inside an instrument the artifact calls 'Psychometrically validated' (line 258) and which feeds an 'adaptive difficulty engine' (line 594). I add: the artifact scores the same contested construct twice in two different domains of a single instrument, which is also a straightforward construct-redundancy defect independent of the evidence question. The lens's recommendation — demote 1.12 to a non-scored context note, keep identity affirmation on design grounds rather than on a promised performance gain — is right and I would make it a hard constraint rather than a suggestion.

### RI-17 - Diagnostics labelled "Psychometrically validated" and "PhD-Level" before an item has been written

**How it was verified.** Verified by direct reading of the artifact rather than by external search, which is the appropriate method here because the defect is an internal contradiction. Line 258 renders the instrument as 'PhD-Level Diagnostic Assessments | Psychometrically validated | Student: 52 domains | Parent: 38 domains | Staff: 24 domains.' Line 91 lists as next action #1, Week 1–2: 'Build PhD-level student diagnostic instrument (52 domains) — validated with licensed school psychologist.' Line 771 lists 'PhD-level student diagnostic (52 domains) validated' as a Phase 1 (Months 1–3) milestone. The document therefore asserts in the present tense that an instrument is validated, while scheduling its construction for weeks one and two and its validation for months one through three. I also confirmed the lens's structural point by counting the items: the student instrument is six domains containing 12+10+8+8+8+6 = 52 items, so '52 domains' is a mislabel that inflates the instrument's apparent scope by a factor of about nine.

**Strengthened evidence.** The lens correctly identifies that line 91's 'validated with licensed school psychologist' describes content-expert review by one person, which is not validation. I can add specificity on exposure. Three items in Domain 3 are individually administered cognitive and literacy measures, not self-report: 2.1 'Working memory functional capacity (digit span + forward/backward task)', 3.1 'Phonological awareness — decoding and fluency baseline assessment', and 3.2 'Reading fluency and automaticity (words per minute + prosody score)'. The artifact then routes the resulting profile into an 'AI-generated personalized learning plan PDF' (line 529) and a 'Monthly IEP Progress Report ... formatted for IEP meeting submission' (line 571). IDEA's evaluation regulations at 34 C.F.R. § 300.304(c)(1) require that assessments be used for purposes for which they are valid and reliable and be administered by trained and knowledgeable personnel; an unnormed self-administered instrument generating IEP-meeting-facing output is squarely in that zone. The lens's validation sequence — item review, cognitive interviews, pilot at n ≥ 300 for factor structure, then measurement invariance across race and disability status before any cross-group comparison — is the right order and the invariance step is the one most often skipped and most consequential for this population.

### RI-19 - Named assessment instruments that appear not to exist: "Learning Science Literacy Tool (UVA, 2023)" and "UDL Competency Guide (CAST 2020)"

**How it was verified.** I verified the CAST half directly, which is the checkable one. CAST released UDL Guidelines 3.0 on 30 July 2024; this is stated on CAST's own 'About the Guidelines 3.0 Update' page and corroborated independently by University of Colorado Denver's TIPS resource ('On July 30, 2024, the Center for Applied Special Technology (CAST) released important updates'), Ohio State's ASC Office of Distance Education, and ADCET. The immediately prior version was 2.2, which CAST still hosts on its Downloads page alongside a 2.2-to-3.0 comparison. CAST's product line is the UDL Guidelines; no CAST publication titled 'UDL Competency Guide' surfaced, and 2020 corresponds to the launch of the update effort, not to a Guidelines release. The lens's appropriate hedging on the UVA instrument — absence of search results is not proof of non-existence, check UVA SEHD project pages, ERIC and ETS instrument databases first — is the correct epistemic posture and I did not improve on it.

**Strengthened evidence.** The stakes are higher than the lens states. Line 306 is the source list for the STAFF diagnostic framework, and that framework underpins credentials the artifact prices at $299 (paraeducator, line 725) and $499 (teacher, line 726) and markets as CEU-eligible to a named public school district. A professional-learning product sold for CEU credit cannot rest its competency framework on instruments that cannot be retrieved. I also note that only one of the four named sources is solid — Saphier, Haley-Speca & Gower, The Skillful Teacher (7th ed., 2018) — and that Hilliard's SBA: The Reawakening of the African Mind (1997) is a book of essays being cited as an 'Assessment,' which is the same theory-as-outcome-evidence substitution the artifact commits at line 465. One correction to the lens's remedy: line 264 does already say 'UDL Guidelines 3.0,' and the lens acknowledges this, but line 306's 'CAST 2020' and line 311's generic 'UDL framework proficiency' should both be conformed to 3.0 with the July 2024 date.

### RI-21 - The artifact violates the AI-content standard it sets for itself two screens earlier

**How it was verified.** Verified by direct comparison within the artifact. Line 118, in the Risks table: 'AI hallucination in educational content | Critical | Confidence scoring on ALL outputs; human expert review queue for score < 0.85; citations required; zero-tolerance for unverified academic claims.' Line 634 repeats the identical text as an agent safety protocol. I then cross-checked this against the defects I independently confirmed in this review — the NASA BARS confabulation, the SM-18 product error, the ES 0.8 attribution, the CAST 2020 instrument, the 73% and 85% and 38% figures for which no source exists, and the VARK construct — and the gap is as the lens describes it.

**Strengthened evidence.** I would reframe the finding to make it sharper and more useful. The lens characterises the gap as 'roughly total,' which is rhetorical. The precise and more damaging version is structural: the artifact applies the citations-required rule exclusively to MODEL output and exempts human-authored design and marketing copy, and the design and marketing copy is where every confirmed fabrication lives. That asymmetry is the root cause, and it is fixable by one sentence of policy rather than by a tone shift. I also add a founder-specific consequence the lens gestures at but does not land: AEOS's distinguishing asset is a hardened multi-tenant security model with a committed mutation test suite — an evidence-backed claim. A master project document that asserts a federal-agency methodology and a district statistic about the founder's own employer, if circulated to the same audience, prices down the security claim by association, because both rest on the identical representation that this team does not assert what it has not verified. The lens's remedy — publish the withdrawal list in the document rather than let a reviewer discover it — is the right instinct and is also the cheapest credibility purchase available here.

---

## What the lens missed

Substantive items the verifier found that the lens did not look for. Several are sharper than anything in the original lens output.

### Third-party instrument licensing: the artifact embeds the Spielberger TAI, VARK, MEIM and PASS/CAS as product features and training content without any licence   `HIGH`

The lens audited whether citations are real and never asked whether the named instruments can lawfully be used. Several cannot, as specified.

The Spielberger Test Anxiety Inventory is the clearest. Line 264 names it as a source for the student diagnostic framework and line 265 renders it as a badge. Line 398 makes 'Spielberger TAI screening' a competency inside the 80-hour MCLSS paraeducator certification sold at $299 (line 725). Line 595 makes a 'Spielberger TAI scorer' one of four tools belonging to the Test Anxiety Coach AI agent. The TAI is published commercially by Mind Garden under Charles Spielberger's copyright. Mind Garden's licence to administer is a research licence for data collection only; it states the instrument may not be made available via the open web nor sent in a message body or as an attachment, that each time a participant opens a survey containing the items counts as one chargeable administration, and that the copyright statement must appear on every page containing items. Mind Garden's standing policy is that items, directions and manual may be used only with purchase or written permission. A consumer mobile app that scores the TAI for subscribers, and a paid certification that trains paraeducators to administer it, are both outside that licence and would need a negotiated commercial agreement.

The same question applies to three more named instruments the lens passed over: 'VARK modality preference' (line 272) — VARK is a trademarked, licensed questionnaire; the 'Phinney Ethnic Identity Model (1992)' / 'Phinney 3-stage model' (lines 264, 271) — the MEIM is a published scale with use conditions; and 'PASS Theory (Das)' (line 264), whose operationalisation is the CAS/CAS2, a restricted-level test requiring qualified-purchaser status.

A fourth, adjacent: line 679 specifies the spaced-repetition layer as 'Anki-compatible.' Anki is AGPL-3.0. Any vendoring of Anki code into a closed-source commercial product triggers the AGPL's network-use copyleft. The lens discussed SM-18 ownership at length and did not mention the licence of the product it recommended building on.

**Evidence.** Mind Garden's TAI and STAI-AD licence pages (mindgarden.com, 'License to Administer: Test Anxiety Inventory' and the STAI-AD licence to reproduce) state the research-only scope, the per-administration charge, the prohibition on open-web availability, and the requirement that the copyright statement appear on every page containing items; the publisher's standing position is that items, directions and manual may be used only with purchase or written permission. SuperMemopedia confirms by contrast that SM-2 'is open to the public' and needs no licence, which is the model the artifact should follow where it can. Artifact lines 264, 265, 271, 272, 398, 595, 679.

---

### The student certification's advertised payoff — paid tutoring at $15–20/hr for grade 6–8 students — is unlawful for most of the intended cohort under Maryland child labor law   `HIGH`

Line 334 describes the MindUnlock Certified Student Tutor track as '12 modules | 40 hours | Digital badge + physical cert | Paid peer tutoring eligibility ($15–20/hr).' Line 356 repeats it as a certification outcome: 'MCPS paid peer tutoring eligibility.' Line 338 Module 12 requires a practicum certifying three peers. The target population is stated throughout as MCPS middle school, grades 6–8 (lines 34, 54), which is approximately ages 11 to 14.

Maryland's minimum working age is 14. Minors aged 14 to 17 generally require a work permit issued by the Division of Labor and Industry, and permits are not issued to minors under 14 and are not issued until a job has actually been offered. The minor, a parent or guardian, and the employer each sign, and the employer must retain the permit for three years. Fourteen- and fifteen-year-olds additionally may not work before 7:00 a.m. or after 8:00 p.m. (9:00 p.m. between Memorial Day and Labor Day). Maryland also warns that where state law is less restrictive than the FLSA, following only the state provision violates federal law.

So: for sixth and seventh graders and most eighth graders, the headline benefit of the certification cannot lawfully be delivered. For the subset who turn 14, it can only be delivered through a permitted employment relationship with a named employer — which raises the unaddressed question of who the employer is. If MindUnlock pays the tutors, MindUnlock is the employer and inherits permit, hour, wage and recordkeeping obligations across every household it serves. If MCPS pays them, that is a district employment decision no vendor can promise.

This is a quantified, consumer-facing inducement attached to a priced product sold to under-resourced families, which is also the FTC substantiation concern the lens raised in RI-07 — but with a harder failure mode, because no amount of pilot data can make it true.

**Evidence.** Maryland Division of Labor and Industry, Employment of Minors / work permit guidance (labor.maryland.gov/labor/wages/empm.shtml and the Minor Fact Sheet at labor.maryland.gov/labor/wages/minorfactsheet.pdf): minimum age 14; 'Work permits are not issued to minors under the age of 14'; permits issued only after a job offer; employer retains the permit for 3 years; 14–15 year olds restricted to 7:00 a.m.–8:00 p.m. (9:00 p.m. Memorial Day to Labor Day); express warning that following a less restrictive Maryland provision where the FLSA is stricter violates federal law. Maryland People's Law Library, 'Getting a Work Permit.' Artifact lines 34, 54, 334, 338, 356.

---

### FERPA is invoked nine times as the governing privacy regime for a product sold directly to families, where FERPA does not reach; and the "72-hour breach notification" is a GDPR clock, not a US K-12 one   `HIGH`

The artifact treats FERPA as the controlling statute for the entire product. 'FERPA-compliant' or FERPA obligations appear at lines 92, 117, 408, 638, 656, 660, 679, 691 and 771 — including as a property of the database itself ('PostgreSQL (Supabase) ... FERPA-compliant', line 660) and as a tab subtitle ('FERPA-compliant | AI-native | Scalable', line 656).

FERPA binds educational agencies and institutions receiving Department of Education funds. It reaches a vendor only derivatively, through the school-official exception at 34 C.F.R. § 99.31(a)(1), which applies when a school contracts with the vendor to perform a service it would otherwise use employees for, under the school's direct control. Where a parent or student signs up directly and no school discloses an education record, FERPA does not apply at all. The artifact's primary revenue line is exactly that: a $49/mo, $399/yr family subscription targeting 500 households in Year 1 (lines 723, 741). For that track the operative regimes are COPPA for users under 13 — and grades 6–8 includes many — plus state student-privacy law, neither of which the artifact treats as primary.

The practical cost is misallocated engineering and misallocated legal spend. Row-level security (lines 92, 660, 691) is good practice but it is not what makes a consumer product compliant; verifiable parental consent, data-minimisation at collection, and deletion rights are, and those are COPPA mechanics. The document also runs two tracks simultaneously — family subscriptions and district licences (line 724) — which is precisely the configuration that lands a vendor on both sides and requires two distinct compliance postures, not one label applied to both.

Separately, lines 117 and 638 both specify a '72-hour breach notification protocol.' Seventy-two hours is the GDPR Article 33 supervisory-authority clock. FERPA imposes no breach-notification requirement at all. Maryland's Personal Information Protection Act, Md. Code Com. Law § 14-3504, requires notice as soon as reasonably practicable but not later than 45 days after the business discovers or is notified of the breach, with notice to the Attorney General in advance of notice to affected individuals. A US K-12 product advertising a European regulator's deadline is a tell that the compliance section was assembled from ambient material rather than from the statutes that govern it — the same defect as the research citations, in the one section where the lens assumed competence.

**Evidence.** 34 C.F.R. § 99.31(a)(1), the school-official exception, is the only route by which FERPA reaches a contractor; where students or parents access a product directly with no school acting as intermediary, no education record is disclosed and FERPA does not apply (consistent position across edtech compliance analyses and the Center for Democracy and Technology's survey of commercial companies and the school-official exception). Md. Code, Commercial Law § 14-3504, text retrieved from mgaleg.maryland.gov: notice 'as soon as reasonably practicable, but not later than 45 days after the business discovers or is notified of the breach,' trigger moved from investigation-completion to discovery by 2022 amendment; AG notified in advance. GDPR Art. 33 supplies the 72-hour figure. Artifact lines 92, 117, 408, 638, 656, 660, 679, 691, 771.

---

### The Year 1 financial projection books a full year of revenue from customers the roadmap acquires in the final quarter, and counts restricted grant funds as net profit   `HIGH`

The lens audited the TAM line and stopped. The projection itself (lines 739–757) contains a timing error large enough to change the business case by roughly a factor of four, and an accounting error on top of it.

The roadmap and the projection contradict each other. Phase 4, Months 10–12 (line 779), sets the goal '500 families, 15 schools' and lists '500 family subscriptions' as a Phase 4 KPI (line 781). Phase 3, Months 7–9 (lines 776–778), closes the 5 school contracts. But line 741 books 'Family Subs | 500 × $399 | $199,500' and line 742 books 'School Licenses | 5 × $7,500 avg | $37,500' as Year 1 revenue — a full twelve months of subscription revenue from subscribers the same document says arrive in months 10 through 12, and a full annual licence fee from contracts signed in months 7 through 9. If customers arrive as the roadmap says, recognised Year 1 family revenue is on the order of $50K, not $199,500. The arithmetic within the table is internally correct ($391,850 total; less ~$175,000 opex; $216,850 net) — the error is upstream of the arithmetic, in what gets counted.

Second, line 745 books '$100,000' of federal grant funding (Title I, IDEA, NSF, IES per line 727) into total revenue, and that figure then flows through to 'Net Year 1 ~$216,850' (line 757). Federal grant funds are restricted and purpose-bound; they are not margin, and no grant reviewer or investor will accept them in a net-income line. Strip them and the stated net falls from $216,850 to $116,850 before the timing correction.

Third, the ~$175,000 operating-cost line is doing a great deal of work. It is meant to cover, per the roadmap, a React Native app on two platforms, a Next.js dashboard, a FastAPI backend, an 8-agent LangGraph system, a 52-item instrument, four certification curricula totalling 250+ hours of content, a 40-culture content library, LMS integrations, Spanish localisation, quarterly external penetration testing and a bug bounty (line 691), paid marketing (line 780), and legal counsel from Day 1 (line 117). No founder compensation appears. A 55% Year 1 net margin on that build is not a projection a diligence reader will engage with.

**Evidence.** Artifact lines 723–728 (pricing and targets), 739–757 (the Year 1 table and totals), 771–781 (phase timing and KPIs). 741: '500 × $399 | $199,500'. 742: '5 × $7,500 avg | $37,500'. 745: 'Grant Funding | 2 grants avg | $100,000'. 755–757: '$391,850' / '~$175,000' / '~$216,850'. 779: 'Phase 4: Scale | Months 10–12 ... 500 families, 15 schools'. 781: KPI '500 family subscriptions'. 776: 'Phase 3: School Integration | Months 7–9'. The contradiction is internal to the document and requires no external source.

---

### Citations the lens never checked, including a misattributed anxiety-transmission source and two likely-nonexistent frameworks in the parent diagnostic   `MEDIUM`

The lens audited the Course Design research table (lines 459–466) and the Gap Analysis (164–169) thoroughly and left several other citation surfaces untouched. At least four claims there need the same treatment, and one is a clear misattribution of the same type as the ones the lens did catch.

(a) Line 289, parent Domain 1: 'Own personal test anxiety history (anxiety transmission research, Carey et al., 2017).' The canonical intergenerational anxiety-transmission finding is Maloney, Ramirez, Gunderson, Levine & Beilock (2015, Psychological Science), which found that more math-anxious parents had children who learned less math and grew more anxious — but only when those parents frequently helped with math homework. That moderator is the whole point and is exactly what a parent-coaching product needs to know. Carey and colleagues are known for a 2016 paper on the direction of the math-anxiety/performance link and for the Modified Abbreviated Math Anxiety Scale (2017); neither is a parent-transmission study. The artifact has the right construct and the wrong source, and has dropped the moderator that would make it actionable.

(b) Line 286, parent framework sources: 'Family Learning Theory (Taylor, 2002)' is not a recognised named theory and the citation is unresolvable as given. 'African-centered Family Education (Kunjufu, 1984)' — Kunjufu's Countering the Conspiracy to Destroy Black Boys dates to 1983/1985, and no 1984 work by that description is identifiable.

(c) Line 166: 'DuPaul et al. (2021): Students with ADHD have EF deficits requiring explicit study system instruction... Accommodations without skill-building produce learned helplessness.' The first clause is defensible; the second is a strong causal claim about an iatrogenic effect of accommodations, and it is attributed to a specific paper and year without the paper being identified. It needs the same treatment as the rest.

(d) Line 596: 'Priority ranker (Eisenhower Matrix).' The attribution to Eisenhower is itself apocryphal — the matrix is Covey's (1989) popularisation of a remark Eisenhower quoted from someone else. Trivial on its own, but it is the lens's own category of borrowed institutional authority, sitting inside an AI agent specification, and it was missed.

What the lens also did not do, and should have: note where the artifact is RIGHT. Liebert & Morris (1967) for the worry/emotionality distinction (line 268), Wine's attentional model (1971) (line 268), Flavell (1979) for metacognition (lines 169, 269), Scarborough (2001) (lines 167, 270), Sweller (1988, 2011) for cognitive load (line 462), Dawson & Guare for ADHD executive-function scaffolding (line 311), Gagné's nine events and Wiggins & McTighe's UbD (line 484), and Saphier, Haley-Speca & Gower (2018) (lines 306, 484) are all correctly attributed and make no fabricated quantitative claims. An audit that lists only defects gives the founder no way to tell which parts of the scaffolding survive, which makes the recommended rewrite riskier than it needs to be.

**Evidence.** Maloney, Ramirez, Gunderson, Levine & Beilock (2015), 'Intergenerational Effects of Parents' Math Anxiety on Children's Math Achievement and Anxiety,' Psychological Science, PMID 26253552 — year-long study; effect conditional on frequency of parental homework help. Searches for a 2017 Carey parent-transmission paper returned only the 2016 directionality paper and the 2017 mAMAS scale; the 2020 Frontiers in Psychology intergenerational review (PMC7385133) cites Carey only for the 2016 work. Artifact lines 166, 286, 289, 596; correct citations at 268, 269, 270, 311, 462, 484.

---

### The lens's proposed remedies are not costed, sequenced, or reconciled against the founder's stated priority order, and several are mutually blocking   `MEDIUM`

The audit produces 23 findings and 12 additions and leaves the founder to sequence them. For a solo founder who is also a full-time MCPS employee and is simultaneously building AEOS, and whose stated principles are completion > validation > monetization > scaling and MVP-first, an unsequenced 35-item remediation list is close to unactionable — and two of the additions are blocking dependencies on the one activity that generates evidence.

The pilot is the chokepoint. Addition #6 requires an OSF pre-registration filed before the first family enrols. Addition #7 requires an IRB determination, separate parent consent and student assent documents, a data-use statement, a named data custodian with a retention schedule, and an MCPS employee conflict-of-interest review, all before any pilot data is collected on minors. Both are correct. But the roadmap puts pilot enrolment at Weeks 6–8 (line 98) with the cohort live in Phase 1, Months 1–3 (line 771), and an independent IRB review for research on children under 45 C.F.R. § 46 Subpart D routinely takes longer than that on its own. The audit does not say that the pilot date must move, which is the actual decision these two additions force.

The additions also assume infrastructure the audit itself argues does not exist. Addition #4 specifies a claims register with a CI job that fails the build on any ESTABLISHED claim lacking a DOI; addition #2 specifies a lint rule over marketing copy; addition #3 specifies a CI grep for a neuromyth blocklist. Three CI gates and a schema, for a product that has not been built, by a team whose stated next action #1 is to draft a diagnostic instrument. Under the founder's own completion > validation ordering, the minimum viable version of all three is one reviewed spreadsheet and a rule that nothing ships with a number in it — which is a day of work rather than a sprint, and which the audit should have said.

Most importantly, the audit never states the cheapest and highest-value action available: the seven fabricated figures (73%, 85%, 38%, ES 0.8, 40%, 15–20%, 90% faster, 60–90%) can be deleted in under an hour with no replacement research, and deleting them removes essentially all of the document's falsifiable exposure. Everything else — the tier badges, the register, the rubric, the pre-registration — is improvement on top of a document that is no longer dangerous. Separating 'stop the bleeding' from 'build the system' is the single edit that would make this audit usable, and the lens does not make it.

**Evidence.** Artifact line 98 (pilot at Weeks 6–8), line 771 (pilot cohort as a Phase 1 Months 1–3 milestone), line 91 (diagnostic build as next action #1, Weeks 1–2). 45 C.F.R. § 46 Subpart D governs research involving children and § 46.408 governs assent. The analysis under review, additions #2, #3, #4, #6, #7, and open_questions items 9 and 11. The founder's stated operating principles as given in the task framing: completion > validation > monetization > scaling, MVP-first, security over feature velocity.

---

## The verifier's own bottom line

> The lens is substantively right about the artifact's central defect: /root/.claude/uploads/7b79576e-a60b-565a-8dd7-5dda9b3dad0c/1fcba899-MindUnlock_Academy.jsx attaches quantitative precision and institutional authority to sources that do not supply either, and it does so while declaring "zero-tolerance for unverified academic claims" (line 118). Its two blocker findings on confabulated artifacts (NASA BARS, Anki SM-18) survive adversarial checking on their cores, and its best work is RI-04, where it correctly identifies that a fabricated ES of 0.8 is displacing a real, strong, verifiable causal literature.
> 
> But the lens's own factual spine is weaker than its rhetoric. Three failures matter enough to act on.
> 
> First, the lens ships a NEW false product fact inside a recommended replacement string. RI-02 instructs the founder to write that FSRS "is Anki's default scheduler." It is not. Anki maintainer dae opened ankitects/anki issue #3616, "Make FSRS the default?", on 2024-12-06; it is still open, was moved to "Solution Spec" on 2026-08-19, and carries an August 2026 comment asking whether the switch is "essentially dead-in-the-water." A document whose disease is unverified product claims would have been handed a fresh one by its own auditor.
> 
> Second, the executive summary asserts of eleven numbers that "None traces to the cited source." That is false for at least two of them, and the lens's own RI-18 quietly contradicts it. Rohrer & Taylor's (2007) commonly reported delayed-test accuracies of 63% interleaved vs 20% blocked differ by 43 percentage points; Roediger & Karpicke's (2006) one-week figures of 61% vs 40% are a ~52% relative gain. The artifact's "43%" and "50%" are category errors and over-generalizations from single experiments — which is a real finding — but calling them fabrications is a different and incorrect charge, and it is the charge an informed reader will test first.
> 
> Third, RI-11 states as "verified" that Sisk et al. (2018) is "273 studies, N≈366,000." The paper reports 129 studies, 162 independent samples, 273 effect sizes, N = 365,915. The lens made the same k-inflation error it indicts the artifact for.
> 
> More consequentially, the lens missed an entire category it was built to catch. It audited citations and never audited instrument licensing. The artifact makes the Spielberger Test Anxiety Inventory an AI agent tool ("Spielberger TAI scorer," line 595) and a training competency inside a $299 certification (line 398). The TAI is published by Mind Garden under a per-administration license that forbids making items "available via the open web" and requires the copyright notice on every page containing items. That is a licensing exposure, not a citation error, and it is live the moment the product ships. The same gap covers VARK, Phinney's MEIM, and the PASS/CAS family.
> 
> It also missed the two sharpest legal exposures in the document. The artifact promises middle schoolers "MCPS paid peer tutoring eligibility ($15–20/hr)" (line 334) — Maryland's minimum working age is 14 and work permits are not issued below it, so a sixth-grade cohort is being sold a credential whose stated payoff is illegal for most of them. And it invokes FERPA nine times as the governing regime for a $49/mo direct-to-family subscription, when FERPA binds educational agencies and reaches vendors only through the school-official exception at 34 C.F.R. § 99.31(a)(1); the applicable regimes for the consumer track are COPPA and state student-privacy law. Its "72-hour breach notification protocol" (lines 117, 638) is the GDPR Art. 33 clock; Maryland's MPIPA, Md. Code Com. Law § 14-3504, gives 45 days.
> 
> Net: roughly 60% of the lens's findings survive adversarial checking intact, about 25% survive in weakened form, and a handful of its supporting citations and remedies would themselves fail the verification gate it proposes in addition #10. The founder should act on RI-01, RI-03, RI-04, RI-05, RI-07, RI-08, RI-09, RI-12, RI-17 and RI-21 as written, treat RI-02, RI-11, RI-13 and RI-18 as correct-in-direction but wrong-in-detail, and add the licensing, child-labor and statute-selection findings the lens did not look for.
