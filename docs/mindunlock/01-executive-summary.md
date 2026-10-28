# MindUnlock — executive summary

Synthesis across eight expert lenses. Read [`00-README.md`](00-README.md) first for what was and
was not verified.

---

## 1. What is genuinely good, and should survive everything below

It would be easy to read the rest of this document as a demolition. It is not. Four things in
the original are better than most of what is actually shipping in this market, and every one of
them survives the audit:

**The problem identification is correct.** Students left to regulate their own study reliably
choose the worst strategies — and they do it because rereading *feels* effective in the moment
while retrieval feels like failure. That is one of the most robust findings in the learning
sciences, it is the real reason study-skills advice doesn't stick, and the artifact's instinct
that something has to intervene at that point is right.

**Family as the unit of instruction** is the most distinctive idea in the document. No study the
learning-science lens located tests a parent-and-child co-certification model. That makes it an
untested bet rather than an evidence-based feature — but it is a *good* bet, and it is the thing
that would differentiate this product from everything else in the category.

**The identity-and-belonging instinct points at real evidence**, just not the evidence the
artifact cites. Culturally relevant curriculum has produced measured gains in attendance and
credits for at-risk students of colour (Dee & Penner's ethnic-studies regression-discontinuity
work). Brief, well-timed belonging and utility-value interventions have real randomised
support. The artifact reached for invented effect sizes when the genuine evidence was stronger
than what it fabricated.

**"Accommodations without skill-building produce learned helplessness"** is the sharpest
sentence in the document. A student can hold an extended-time accommodation for six years and
still have no study system, because an accommodation changes the conditions of assessment and
teaches nothing. That observation is the product's actual reason to exist.

Keep all four. Everything below is about making it possible to act on them.

---

## 2. The two things that must be resolved before anything else

### 2.1 You are an MCPS employee whose entire go-to-market is MCPS

This is the highest-probability catastrophic risk in the plan, and the artifact does not mention
it once. Its own risk register lists six risks — FERPA, hallucination, crisis, cultural
appropriation, dropout, UI complexity. It does not list the founder.

Stack the facts the way an ethics panel or a reporter would:

| In the artifact | What it is |
|---|---|
| "MCPS district leadership presentation delivered" (Phase 3) | A public employee pitching a for-profit product to their own employer |
| "5 school contracts signed ($37,500 ARR)" | Revenue to the employee from the employer |
| "Pilot cohort: 10 MCPS families" — owner: Founder | Recruiting the employer's families, through what channel? |
| "real MCPS student scenarios" (exam content) | Employer's student information in a commercial product |
| "MCPS subject knowledge base" (tutor agent) | Employer's curriculum materials |
| "MCPS District Partnership", "MCPS paid peer tutoring eligibility" | Representations MCPS has not agreed to |

Maryland's Public Ethics Law treats intentional use of public position for private gain as a
prohibition, not a disclosure item. This is not a Week 12 compliance task; it is a Week 0 gate.

**What to do, in order.** (1) File the MCPS outside-employment pre-approval disclosing the
venture, your role and the intent to sell to MCPS. (2) Request a written advisory opinion from
the MCPS Ethics Panel describing the actual fact pattern, including the pilot and the sales
motion. (3) Until that opinion is in hand: remove MCPS from every revenue target, recruit no
MCPS families, use no MCPS materials, devices, time or rosters, and delete the partnership
claims. (4) Keep a provenance log — for every pilot family, scenario and content asset, how it
was obtained and on whose time.

Treat an opinion that says no as dispositive. The cruel version of this risk is that a
*successful* pilot becomes the evidence of the violation.

> The specific MCPS policy and regulation designators the red-team lens identified could not be
> verified from the audit environment. Confirm them directly with MCPS before relying on them.

### 2.2 The product performs psychological assessment on minors

A "52-domain psychometric engine", a "Spielberger TAI scorer", an "anxiety severity tracker", a
"counselor referral flag" and a "crisis detection layer" are, together, what Maryland law
describes as the practice of psychology for compensation. Nothing in the artifact names a
licensed psychologist; "validated with licensed school psychologist" is a one-time review, not
ongoing supervision of administration and interpretation.

Separately, the Spielberger Test Anxiety Inventory is a copyrighted commercial instrument whose
standard research licence explicitly forbids giving individual feedback to participants — which
is exactly what this product would do.

There are two coherent postures and no third:

- **Non-clinical (recommended, costs nothing).** Delete "psychometric", "psychometrically
  validated", "diagnostic", "severity tracker" and "PhD-Level" from every surface. Reframe as a
  study-planning inventory that produces no scores, no norms and no referral flags. State in the
  product that it is not an assessment and does not detect or diagnose anything.
- **Clinical (five figures a year, minimum).** Retain a Maryland-licensed psychologist as a
  named clinical director with documented responsibility for the instrument, the scoring logic
  and the referral threshold.

What you cannot do is keep the clinical language without the licence.

---

## 3. The evidence base does not survive contact with its sources

The artifact's own stated standard is *"Evidence Before Claims — never imply validation that has
not occurred."* Judged against that standard, it fails in its own foundational tab.

**Methods that do not exist as described:**

- **"NASA BARS Method"** — there is no NASA method called BARS. In the literature BARS means
  *Behaviorally Anchored Rating Scales* (Smith & Kendall, 1963), a personnel performance-appraisal
  technique with no connection to scheduling. NASA's actual workload instrument is NASA-TLX. The
  artifact built a core feature, a certification module, a paraeducator competency domain and an
  AI agent on a borrowed federal-agency name for what is, in fact, time-blocking. Time-blocking
  is fine. It cannot borrow NASA's name.
- **"Anki SM-18"** — SM-18 is SuperMemo's proprietary algorithm. Anki has never implemented it;
  it ships an SM-2 derivative and FSRS, which is open source and free. "AnkiConnect sync" is a
  desktop-only loopback add-on that cannot back a mobile product. The spacing *evidence* is
  excellent; the engineering claim attached to it describes a thing that does not exist.

**Numbers attributed to sources that do not report them:**

| Claim | Problem |
|---|---|
| African-centred pedagogy "(ES: 0.8)" | Attributed to three theorists, none of whom published a meta-analysis. The real quantitative evidence (Dee & Penner) is stronger than the invented number. |
| "40% greater intrinsic motivation" | Attributed to Holt, Gray and Freire — trade books and theory, not effect sizes. |
| "73% of MCPS families lack both" | Attributed to a 1997 national theory paper, which cannot contain a Montgomery County statistic. |
| "Interleaving ... by 43%", "15–20%" stereotype threat, "38%" test anxiety prevalence, "85%" of interventions | Unverified against their cited sources. |

**Debunked constructs embedded in the instrument:** VARK modality preference (item 5.1) and
"Preferred cultural learning style" (item 4.8). Learning-styles matching has no adequate evidence
base. The second version is worse than the first: it attaches a disproven cognitive trait to
ethnicity, which is racial essentialism wearing affirmation's clothes — and it will be read that
way, correctly, by a journalist or a parent.

**Speed reading.** "60–90% speed increase with equal or greater comprehension" contradicts the
reading-science consensus that large rate gains cost comprehension, and that rate is governed
mainly by language skill and prior knowledge. Selling it to families whose children have literacy
difficulties is both ineffective and an unsubstantiated performance claim.

**"Systematic review"** requires a protocol, a search strategy, inclusion criteria and a flow
diagram. None exists. Call it a competitive scan — which is a legitimate thing to have done.

**"PhD-Level"**, used about ten times including for a 40-hour course for a 12-year-old, plus
"CEU-eligible", "3 graduate credits" and "Target partners: Howard University, Morgan State,
UMCP" — none agreed — is a deceptive-credential fact pattern. The **"GED-to-PhD pathway"** at
$99–$999 a level is the most exposed surface in the document: five of its eight rungs are marked
"Partner" with no partner, sold to families the artifact itself describes as under-resourced.

---

## 4. The economics do not close

The systems lens modelled the artifact's own architecture — eight stateful agents, a five-agent
daily chain, tutor chat, note feedback, anxiety coach, per-student generated cultural content —
and found roughly **262K input tokens per family per day**.

| Scenario | Cost per family per month | Against $33.25 revenue |
|---|---|---|
| Frontier model, as designed | ~$32.15 | ~0% gross margin |
| Mid-tier model, as designed | ~$16.09 | 48% of revenue |
| Re-architected | ~$1.80 | ~18× reduction |

The design sits exactly on the break-even line with no headroom — one engaged student doing 30
tutor turns instead of 12 is immediately loss-making. And the fixed stack (ECS Fargate multi-AZ,
RDS Multi-AZ, ElastiCache, CloudFront, Pinecone, a second Supabase project) runs ~$520/month,
which is $1.04/family at 500 families but **$52/family during the 10-family pilot the roadmap
says lasts eight months.**

The re-architecture is not a compromise: deterministic code for everything deterministic
(scheduling, spacing intervals, accommodation mapping, escalation thresholds), three narrow model
call types instead of eight agents, prompt caching, small-model routing with graded escalation,
and precomputed human-reviewed cultural content. It is cheaper, faster, testable, and operable by
one person — which the current design is not.

Three further structural problems:

- **Scope.** ~45 engineering-months plus ≥25 person-months of content, against one founder with
  a full-time job, in 12 months. Over-scoped roughly 6–8×.
- **Evaluability.** Eight chained stochastic agents cannot be regression-tested. The only stated
  quality control — "confidence scoring; human review if score < 0.85" — is not a mechanism:
  LLM self-reported confidence is highest exactly where the model is confabulating, so a 0.85
  threshold filters out uncertain-but-correct outputs and passes confident-but-wrong ones. That
  is worse than no filter, because it manufactures assurance.
- **The strongest asset is unused.** AEOS already has a committed, mutation-tested, FORCE-RLS
  multi-tenant model over exactly the right entities — students, assessments, AI recommendations,
  intervention plans, audit logs. The artifact proposes a parallel stack instead, contradicting
  the founder's own shared-infrastructure principle.

---

## 5. The MCPS reality

**The accommodation engine is the product's biggest school-facing liability, not its selling
point.** Under IDEA, accommodations are determined by the IEP team with parent participation, and
changes to FAPE provision require prior written notice. A product that "auto-configures" and
"dynamically adjusts" a child's accommodations relocates a legally reserved team decision into a
vendor's algorithm. MCPS's Office of Special Education will read it that way in the first meeting.

**Three things stop this at the door before pedagogy is discussed:** IDEA's own confidentiality
subpart (34 CFR 300.610–300.627), which is stricter than the general FERPA framing and is never
mentioned; Maryland's vendor regime (Educ. §4-131 operator duties, MCPS's data-privacy vetting,
a signed data privacy agreement) which must precede any student data touching the system; and a
Board-approval threshold that a five-school licence trips in aggregate.

**And the artifact never makes its own best argument.** The MCPS lens found that the district is
under a state finding of significant disproportionality in suspensions of Black students with
disabilities, carrying a documented IDEA set-aside consequence in the millions. *That* is a budget
line with a buyer attached. Test anxiety is not.

> This specific finding is high-value and currently unverified. Confirm the finding and the
> set-aside figure against MSDE and MCPS sources before using it in any pitch.

---

## 6. What to build instead

The learning-science and note-taking lenses converge on a smaller, better-evidenced product.

**Core (high-utility, cheap, measurable):**

- **Retrieval practice.** The product never shows notes as a review step; review is always a
  retrieval attempt first, then the answer.
- **Spaced practice with the test date as an input.** "Space it out" without a retention interval
  is not actionable.
- **Calibration as the primary metric.** Before every retrieval attempt the student predicts
  whether they'll get it right; afterwards they see prediction against outcome. The product's
  headline number is the gap between the two, narrowing over time. This targets the actual
  mechanism — miscalibration — rather than lecturing about strategies.

**Cut (documented low-utility, and three were planned features):** highlighting, rereading,
AI-generated summarisation, imagery use, keyword mnemonics.

**Note-taking, rebuilt:** guided/skeletal notes become the default — the single highest-yield
note-taking intervention for students with disabilities, and absent from the original entirely.
Concept mapping replaces mind mapping (the better-evidenced cousin; it forces the student to name
the relation between two ideas, which is the part that does the work). The longhand-versus-typing
advantage did not replicate, which removes an objection to a typing-based product — but it means
the product must force a post-session revision-and-retrieval pass, because that is where the
benefit actually lives.

**The central design risk of an AI study product:** if the AI writes the notes, it removes the
generative work that makes note-taking useful. The AI may question, prompt and check a student's
notes. It may not write them.

**The missing evidence base for this exact population:** Self-Regulated Strategy Development —
among the strongest evidence bases in all of special education — appears nowhere in the original.
Neither do HOPS organisational-skills training, self-determination instruction (which is the
IDEA-aligned, evidence-based version of the artifact's "child liberation" aspiration), guided
notes, or curriculum-based progress monitoring.

**Dashboards.** Performance during practice is an unreliable index of learning, so a dashboard
that rewards practice performance can push a student toward conditions that look good and teach
less. Streaks and accuracy percentages are not primary metrics.

---

## 7. Sequence

**Gate 0 — before any further building.**
1. MCPS outside-employment disclosure and written Ethics Panel advisory opinion.
2. Decide the clinical posture. (Recommended: non-clinical. Then delete the clinical vocabulary
   everywhere.)
3. Strike from every document: "PhD-Level", "90% faster", "systematic review", "NASA BARS",
   "Anki SM-18", "CEU-eligible", the named universities, GED-to-PhD levels 4–8, and every
   unverifiable number. Replace each with a verified figure and page cite, or a qualitative
   statement, or nothing.

**Gate 1 — the defensible MVP (~8 weeks).** One segment, direct-to-family, outside MCPS. No IEP
upload (a parent-selected accommodation checklist delivers the same product behaviour and holds
none of the record). No crisis detection claim — unconditional always-visible crisis resources
instead. No video. No district channel. No cultural module until the advisory board exists and is
funded. A 15-minute instrument asking only about study behaviour, with every PPRA-protected
domain cut.

**Gate 2 — the pilot.** Primary outcome: calibration gap at intake and six weeks. Secondary:
delayed retention, and unprompted week-six use (the honest early signal — most study tools die
there, and the original roadmap had no measure that would have detected it). Independent ethics
review, parent consent and child assent, a defined withdrawal procedure, and pre-defined stop
conditions. No outcome claim in any customer-facing material until this reports.

**Gate 3 — only then** consider schools, and lead with disproportionality rather than test anxiety.

---

## Highest-leverage next action

**File the MCPS outside-employment disclosure and request a written Ethics Panel advisory
opinion describing the actual fact pattern** — the venture, your role, the intended MCPS pilot,
and the intended MCPS sales motion.

- **Where:** MCPS Ethics Panel / Ethics Officer, via the current outside-employment pre-approval
  form.
- **What to produce:** the filed form, and a written request for an advisory opinion that
  describes the fact pattern accurately rather than favourably.
- **Done when:** you hold a written opinion. Not a verbal assurance, not a manager's nod.

Everything else in this document is reversible. This one is not, and it gets more expensive to
fix with every week of building, every family recruited, and every slide that says MCPS.
