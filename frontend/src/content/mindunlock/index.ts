import type { Briefing } from '@/lib/briefing/types';
import { MINDUNLOCK_SOURCES } from './sources';

/**
 * MindUnlock, re-expressed as graded claims.
 *
 * The original planning document asserted roughly two hundred things in the voice of
 * settled science. This version keeps the assertions that survive scrutiny, demotes the
 * ones that are really design bets, and keeps the ones that were wrong — marked
 * `retracted` — so the correction stays visible to anyone who read the earlier draft.
 */
export const MINDUNLOCK_BRIEFING: Briefing = {
  slug: 'mindunlock',
  title: 'MindUnlock',
  subtitle:
    'A study-skills and test-anxiety module for AEOS, serving middle-school students with ' +
    'IEPs and 504 plans and the adults around them.',
  revised: '2026-10-28',
  scope:
    'This briefing states what we believe, how strongly, and on what basis. It is a design ' +
    'and governance document, not marketing material and not evidence of efficacy. ' +
    'MindUnlock has not been evaluated with students. Every claim below carries the tier of ' +
    'its weakest supporting source, and anything we have not tested is labelled as an ' +
    'untested hypothesis wherever it appears.',
  sources: MINDUNLOCK_SOURCES,
  sections: [
    // ─────────────────────────────────────────────────────────────────────────────
    {
      slug: 'premise',
      title: 'The premise',
      summary:
        'What the original document got right, stated at the strength the evidence allows.',
      tone: 'neutral',
      groups: [
        {
          id: 'problem',
          heading: 'The problem being solved',
          intro:
            'Four observations motivate the work. Three are supported; the fourth is our own ' +
            'reading of the field and is labelled accordingly.',
          claims: [
            {
              id: 'premise-anxiety-performance',
              text:
                'Test anxiety is reliably associated with lower academic performance across three ' +
                'decades of studies, and the association is stronger for students already at ' +
                'academic risk.',
              tier: 'established',
              sources: ['von-der-embse-2018'],
              note:
                'The original document asserted "38% of middle schoolers experience debilitating ' +
                'test anxiety (Zeidner, 1998)". A prevalence figure that precise, attributed to a ' +
                'single 1998 monograph, should not be repeated without locating the underlying ' +
                'sample. The association claim above is what the meta-analytic record supports.',
            },
            {
              id: 'premise-strategy-choice',
              text:
                'Students left to regulate their own study reliably choose rereading over ' +
                'retrieval practice, and they do so because rereading feels more effective in ' +
                'the moment.',
              tier: 'established',
              sources: ['karpicke-2009', 'kornell-bjork-2007', 'soderstrom-bjork-2015'],
              note:
                'This is the strongest justification for the product existing. The problem is not ' +
                'that students lack motivation; it is that their monitoring is miscalibrated, and ' +
                'miscalibration is addressable by design.',
            },
            {
              id: 'premise-accommodation-gap',
              text:
                'Accommodations change the conditions of assessment but do not themselves teach ' +
                'the strategies a student needs, so a student can hold an accommodation for years ' +
                'and still have no study system.',
              tier: 'inference',
              sources: ['idea-iep-team', 'graham-harris-srsd'],
              note:
                'The original document stated this as a research finding attributed to DuPaul and ' +
                'colleagues. We could not verify a source making exactly that claim. It is a sound ' +
                'reading of how accommodations are defined in regulation alongside the strength of ' +
                'the strategy-instruction literature, so it is recorded as our inference.',
            },
            {
              id: 'premise-adults-untrained',
              text:
                'The adults closest to a struggling student — parents and paraeducators — are ' +
                'rarely taught learning science explicitly, so the student receives encouragement ' +
                'rather than technique.',
              tier: 'expert-opinion',
              sources: ['eef-metacognition', 'rosenshine-2012'],
              note:
                'The original document asserted "73% of MCPS families lack both" content knowledge ' +
                'and confidence. No source exists for that figure and it must not be used. The ' +
                'claim above is defensible as a professional judgement and should be tested ' +
                'directly in the pilot rather than asserted.',
            },
          ],
        },
        {
          id: 'what-carries-over',
          heading: 'What carries over from the original design',
          claims: [
            {
              id: 'carry-family-unit',
              text:
                'Treating the household rather than the individual student as the unit of ' +
                'instruction is the most distinctive idea in the original document and is worth ' +
                'building.',
              tier: 'hypothesis',
              sources: [],
              note:
                'No study we located tests a parent-and-child co-certification model. This is a ' +
                'genuine bet and the pilot exists to test it. It must never be described as ' +
                'evidence-based until it has been evaluated.',
            },
            {
              id: 'carry-belonging',
              text:
                'Brief interventions that address belonging and the perceived value of academic ' +
                'work have produced real achievement effects, concentrated among the students ' +
                'this module targets.',
              tier: 'emerging',
              sources: ['walton-cohen-2011', 'hulleman-harackiewicz-2009', 'yeager-2019'],
              magnitude: {
                value: 'Small average effects; larger for lower-achieving subgroups',
                metric: 'Grade point average and course performance in randomised trials',
                population:
                  'US secondary and post-secondary students; the belonging work is strongest ' +
                  'for African American students in a selective-college setting',
              },
              note:
                'These are short, carefully worded, well-timed interventions. The evidence does ' +
                'not support a platform-wide identity layer; it supports a handful of precisely ' +
                'placed moments.',
            },
            {
              id: 'carry-cultural-curriculum',
              text:
                'Culturally relevant curriculum has produced measured gains in attendance and ' +
                'credits earned for academically at-risk students of colour.',
              tier: 'emerging',
              sources: ['dee-penner-2017', 'aronson-laughter-2016', 'ladson-billings-1995'],
              magnitude: {
                value:
                  'Large gains in attendance and credits earned at the assignment threshold',
                metric: 'Regression-discontinuity estimates around a GPA cutoff',
                population:
                  'Ninth-grade students in San Francisco Unified assigned to an ethnic studies ' +
                  'course on a GPA threshold',
              },
              note:
                'This is evidence for curriculum content and relationship, not for storing a ' +
                'child’s heritage as a configuration field. See the identity section.',
            },
          ],
        },
      ],
    },

    // ─────────────────────────────────────────────────────────────────────────────
    {
      slug: 'corrections',
      title: 'Corrections',
      summary:
        'Claims in the original document that the evidence does not support. Kept visible ' +
        'rather than deleted, because the draft has already been read.',
      tone: 'correction',
      groups: [
        {
          id: 'retractions',
          heading: 'Retracted claims',
          intro:
            'Each of these appeared in the original planning document as settled science. ' +
            'None of them should be repeated, in the product, in a pitch, or in a grant ' +
            'application.',
          claims: [
            {
              id: 'retract-learning-styles',
              text:
                'Diagnosing a learner’s sensory modality preference and matching instruction to ' +
                'it does not improve learning, and should not be a field in any assessment.',
              tier: 'retracted',
              sources: ['pashler-2008'],
              note:
                'The original listed "5.1 VARK modality preference" as a diagnostic domain and ' +
                '"4.8 Preferred cultural learning style (call-response, storytelling, movement)" ' +
                'as another. The meshing hypothesis has no adequate supporting evidence. The ' +
                'second version is worse than the first: it attaches a disproven cognitive trait ' +
                'to ethnicity. Both domains are removed.',
            },
            {
              id: 'retract-speed-reading',
              text:
                'Speed-reading technique does not produce large reading-rate gains at constant ' +
                'comprehension; rate is governed mainly by language skill and prior knowledge.',
              tier: 'retracted',
              sources: ['rayner-2016'],
              note:
                'The original promised "Triple Reading Speed ... 60–90% speed increase with equal ' +
                'or greater comprehension" and a module built on it. Selling that to families ' +
                'whose children have literacy difficulties would be both ineffective and, as an ' +
                'objective performance claim without substantiation, an advertising exposure.',
            },
            {
              id: 'retract-90-percent',
              text:
                'There is no basis for claiming that any study method makes a student 90 per cent ' +
                'faster, with or without AI.',
              tier: 'retracted',
              sources: ['ftc-act-5'],
              note:
                'The original used "Study 90% Faster" as a module title and a feature bullet. ' +
                'An unsubstantiated quantified performance claim made to parents is the clearest ' +
                'consumer-protection exposure in the document.',
            },
            {
              id: 'retract-sm18',
              text:
                'Anki does not implement SM-18; SM-18 is SuperMemo’s proprietary algorithm. ' +
                '"Anki SM-18 engine" describes a thing that does not exist.',
              tier: 'retracted',
              sources: ['cepeda-2006'],
              note:
                'The original named "Anki SM-18" in four places, including the database and ' +
                'backend sections. Anki historically shipped an SM-2 derivative and has since ' +
                'added FSRS, a free open scheduler. The spacing evidence is sound; the engineering ' +
                'claim attached to it was not.',
            },
            {
              id: 'retract-nasa-bars',
              text:
                'We could not locate a NASA method called BARS. In the published literature BARS ' +
                'refers to behaviourally anchored rating scales, a performance-appraisal technique ' +
                'unrelated to scheduling.',
              tier: 'retracted',
              sources: ['rosenshine-2012'],
              note:
                'The original built an entire scheduling feature on "NASA BARS Method — Behavioral ' +
                'Anchoring / Mission-Critical Task Scheduling". The underlying feature — ' +
                'decomposing work into short, concrete, scheduled blocks with sleep protected — ' +
                'is worth building. It simply cannot borrow NASA’s name. Verify before reuse: if ' +
                'a NASA scheduling instrument of this name exists, we did not find it.',
            },
            {
              id: 'retract-effect-sizes',
              text:
                'The effect sizes attached to African-centred pedagogy and to self-directed ' +
                'learning in the original document do not appear in the works cited.',
              tier: 'retracted',
              sources: ['aronson-laughter-2016', 'dee-penner-2017'],
              note:
                'The original stated African-centred pedagogy "raises Black student achievement ' +
                '(ES: 0.8)" citing Hilliard, Nobles and Asante, and that agency in learning design ' +
                'produces "40% greater intrinsic motivation" citing Holt, Gray and Freire. These ' +
                'are works of theory and advocacy; they do not report those quantities. The real ' +
                'quantitative evidence for culturally relevant curriculum is Dee and Penner, and ' +
                'it should be cited instead — it is strong enough not to need embellishment.',
            },
            {
              id: 'retract-systematic-review',
              text:
                'The gap analysis is not a systematic review and must not be described as one.',
              tier: 'retracted',
              sources: ['dunlosky-2013'],
              note:
                'The original claimed a "systematic review across 47 peer-reviewed sources, 24 ' +
                'courses, 38 apps". A systematic review requires a registered protocol, a stated ' +
                'search strategy, inclusion and exclusion criteria, and a flow diagram accounting ' +
                'for every record. None exists. Call it a competitive scan, which is a legitimate ' +
                'and useful thing to have done.',
            },
            {
              id: 'retract-paid-tutoring',
              text:
                'Maryland’s minimum working age is 14 and work permits are not issued below it, ' +
                'so paid tutoring cannot lawfully be delivered to most of a grades 6–8 cohort.',
              tier: 'retracted',
              sources: ['md-child-labor'],
              note:
                'The student certification advertised "Paid peer tutoring eligibility ' +
                '($15–20/hr)" and "MCPS paid peer tutoring eligibility" to a cohort the document ' +
                'defines as grades 6–8 — roughly ages 11 to 14. Unlike the efficacy claims, no ' +
                'amount of pilot evidence can make this one true. It also raises a question the ' +
                'original never asked: if the product pays the tutors, the product is the ' +
                'employer, with permit, hour, wage and recordkeeping obligations in every ' +
                'household it serves.',
            },
            {
              id: 'retract-ferpa-posture',
              text:
                'FERPA does not govern a product a parent subscribes to directly; it binds ' +
                'educational agencies and reaches a vendor only through the school-official ' +
                'exception. The operative regimes for the family channel are COPPA and state ' +
                'student-privacy law.',
              tier: 'retracted',
              sources: ['ferpa', 'coppa-rule', 'md-pipa'],
              note:
                'The original invoked FERPA nine times as the governing regime, including as a ' +
                'property of the database itself ("PostgreSQL (Supabase) … FERPA-compliant"), ' +
                'while its primary revenue line was a direct-to-family subscription. The tell is ' +
                'the stated "72-hour breach notification protocol": that is the GDPR Article 33 ' +
                'clock. FERPA imposes no breach-notification duty at all, and Maryland’s PIPA ' +
                'gives 45 days. Row-level security is good practice but it is not what makes a ' +
                'consumer product compliant — verifiable parental consent, minimisation at ' +
                'collection and deletion rights are, and those are COPPA mechanics.',
            },
            {
              id: 'retract-phd-level',
              text:
                '"PhD-Level" is not a property a forty-hour course for a twelve-year-old can have, ' +
                'and naming universities as partners before they have agreed is a representation ' +
                'we cannot make.',
              tier: 'retracted',
              sources: ['ftc-act-5'],
              note:
                'The original used "PhD-Level" roughly ten times, advertised certifications as ' +
                '"CEU-eligible", offered "3 graduate credits via partner university", named ' +
                'Howard, Morgan State and UMCP as "target partners", and sold a "GED-to-PhD" ' +
                'pathway at up to $999 per level to low-income families. Every one of those is a ' +
                'claim about a credential’s value made to a buyer who cannot easily verify it.',
            },
            {
              id: 'retract-mindset-overstated',
              text:
                'Growth-mindset framing produces small average effects, concentrated among ' +
                'lower-achieving students in supportive settings — not a reliable lift for ' +
                'everyone.',
              tier: 'retracted',
              sources: ['sisk-2018', 'yeager-2019'],
              magnitude: {
                value: 'Approximately 0.1 grade points in the targeted subgroup',
                metric: 'Core-course GPA in a pre-registered national randomised trial',
                population: 'US ninth-grade students, lower-achieving subgroup',
              },
              note:
                'The original asserted that "malleable intelligence framing raises achievement and ' +
                'resilience" and built it into every module. The honest version is narrower, and ' +
                'happens to point at exactly the students this module serves — which is a better ' +
                'argument than the overstated one.',
            },
            {
              id: 'retract-stereotype-threat',
              text:
                'The 1995 stereotype-threat result should not be cited with a 15–20 per cent ' +
                'performance figure; the field now carries serious publication-bias and ' +
                'replication concerns, particularly in children and in field settings.',
              tier: 'retracted',
              sources: ['flore-wicherts-2015'],
              note:
                'The original used stereotype threat to justify an "ancestor activation ritual ' +
                'before every assessment". The belonging and utility-value literature supports ' +
                'something adjacent and is better evidenced; build on that instead.',
            },
          ],
        },
      ],
    },

    // ─────────────────────────────────────────────────────────────────────────────
    {
      slug: 'learning-engine',
      title: 'The learning engine',
      summary:
        'What to build instead: the techniques with the strongest evidence for this ' +
        'population, and the ones to leave out.',
      tone: 'opportunity',
      groups: [
        {
          id: 'high-utility',
          heading: 'High-utility techniques',
          intro:
            'These are the two techniques rated high-utility across the widest range of ' +
            'learners, materials and conditions. They are also cheap to implement and easy ' +
            'to measure, which makes them the right core for a first release.',
          claims: [
            {
              id: 'engine-retrieval',
              text:
                'Practice testing — answering from memory rather than reviewing — produces ' +
                'better long-term retention than restudying, and is rated high-utility across ' +
                'learners, materials and criterion tasks.',
              tier: 'established',
              sources: ['dunlosky-2013', 'roediger-karpicke-2006'],
              note:
                'Implementation rule: the product never shows a student their notes as a review ' +
                'step. Review is always a retrieval attempt first, then the answer.',
            },
            {
              id: 'engine-spacing',
              text:
                'Distributing practice across sessions produces better retention than massing it, ' +
                'with the optimal gap scaling to how long the material must be retained.',
              tier: 'established',
              sources: ['dunlosky-2013', 'cepeda-2006'],
              note:
                'Implementation rule: the scheduler takes the test date as an input. "Space it ' +
                'out" without a retention interval is not actionable.',
            },
            {
              id: 'engine-low-utility',
              text:
                'Highlighting, rereading, summarisation, imagery use and the keyword mnemonic are ' +
                'rated low-utility, and three of them were planned features.',
              tier: 'established',
              sources: ['dunlosky-2013'],
              note:
                'Removed from scope: the AI note-summarisation feature, the "re-read to review" ' +
                'flow, and highlight-based study. Each felt like an obvious feature and each is a ' +
                'documented waste of a student’s limited attention.',
            },
          ],
        },
        {
          id: 'calibration',
          heading: 'Calibration, not strategy lectures',
          intro:
            'The original planned to teach strategies. Teaching strategies to students who ' +
            'cannot tell whether they are learning does not change behaviour, because the ' +
            'student will revert to whatever feels effective.',
          claims: [
            {
              id: 'engine-calibration',
              text:
                'Learners systematically overestimate how well they have learned material they ' +
                'have just reread, and this miscalibration is what drives their strategy choice.',
              tier: 'established',
              sources: ['kornell-bjork-2007', 'karpicke-2009', 'soderstrom-bjork-2015'],
              note:
                'Implementation rule: before every retrieval attempt the student predicts whether ' +
                'they will get it right; afterwards they see prediction against outcome. The ' +
                'product’s primary metric is the gap between the two, narrowing over time.',
            },
            {
              id: 'engine-srl',
              text:
                'Teaching metacognition and self-regulation is among the highest impact-per-cost ' +
                'interventions in the school-improvement evidence base, and is most effective ' +
                'when taught inside a subject rather than as a standalone study-skills course.',
              tier: 'emerging',
              sources: ['eef-metacognition'],
              note:
                'The months-progress figure in the EEF toolkit is an average across a ' +
                'heterogeneous set of programmes. It justifies the direction, not a prediction ' +
                'about MindUnlock. The "taught inside a subject" finding is the one that should ' +
                'change the design: a general study-skills module is the format with the worst ' +
                'transfer record.',
            },
            {
              id: 'engine-dashboard-risk',
              text:
                'Performance during practice is an unreliable indicator of learning, so a ' +
                'dashboard that rewards practice performance can push a student toward conditions ' +
                'that look good and teach less.',
              tier: 'established',
              sources: ['soderstrom-bjork-2015'],
              note:
                'Implementation rule: streaks and accuracy percentages are not primary metrics. ' +
                'The student-facing dashboard shows calibration and delayed retention.',
            },
          ],
        },
        {
          id: 'notes',
          heading: 'Note-taking, rebuilt',
          intro:
            'The original listed six methods ranked by nothing. Here is what the evidence ' +
            'actually distinguishes.',
          claims: [
            {
              id: 'notes-guided',
              text:
                'Guided notes — a prepared skeleton with key content left blank — improve ' +
                'accuracy and achievement, and the evidence is concentrated in special education.',
              tier: 'emerging',
              sources: ['konrad-2009'],
              note:
                'This is the single highest-yield note-taking intervention for students with ' +
                'disabilities, and it was absent from the original entirely. It becomes the ' +
                'default note format for v1.',
            },
            {
              id: 'notes-concept-maps',
              text:
                'Concept and knowledge maps — structured representations with labelled relations ' +
                'between ideas — have meta-analytic support; freeform mind mapping does not have ' +
                'an equivalent base.',
              tier: 'established',
              sources: ['nesbit-adesope-2006'],
              note:
                'The original chose mind mapping, citing "Buzan (1970) — validated UCL", a ' +
                'provenance we could not verify. Concept mapping is the better-evidenced cousin ' +
                'and requires the student to name the relationship between two ideas, which is ' +
                'the part that does the work.',
            },
            {
              id: 'notes-modality',
              text:
                'The reported advantage of handwritten over typed notes did not replicate; what ' +
                'the student does with the notes afterwards matters more than the input method.',
              tier: 'emerging',
              sources: ['mueller-oppenheimer-2014', 'morehead-2019'],
              note:
                'Useful because it removes an objection to a typing-based product. It also means ' +
                'the product must force a post-session revision-and-retrieval pass, which is ' +
                'where the benefit actually lives.',
            },
            {
              id: 'notes-ai-offloading',
              text:
                'Having the AI generate a student’s notes removes the generative work that makes ' +
                'note-taking useful, and is the central design risk of an AI study product.',
              tier: 'inference',
              sources: ['dunlosky-2013', 'soderstrom-bjork-2015'],
              note:
                'Not directly tested for AI note generation in adolescents, so recorded as an ' +
                'inference. The design response: the AI may question, prompt and check a ' +
                'student’s notes; it may not write them.',
            },
          ],
        },
        {
          id: 'anxiety',
          heading: 'Test anxiety without clinical claims',
          claims: [
            {
              id: 'anxiety-expressive-writing',
              text:
                'A brief expressive-writing exercise immediately before an exam has improved ' +
                'performance for anxious students, though replication has been mixed.',
              tier: 'emerging',
              sources: ['ramirez-beilock-2011'],
              note:
                'Ten minutes, no clinician, no data retained. This is the right shape for a ' +
                'non-clinical product: a specific, timed, low-risk practice rather than an ' +
                '"anxiety severity tracker".',
            },
            {
              id: 'anxiety-retrieval-link',
              text:
                'Low-stakes retrieval practice is the point where the learning engine and the ' +
                'anxiety work meet: repeated non-consequential testing is both the best-evidenced ' +
                'study technique and a form of exposure to the testing format.',
              tier: 'inference',
              sources: ['dunlosky-2013', 'von-der-embse-2018'],
              note:
                'Stated as an inference deliberately. It is the most promising hypothesis in the ' +
                'whole design and the pilot should be built to test it.',
            },
            {
              id: 'anxiety-no-assessment',
              text:
                'The product does not screen, score, diagnose or track anxiety as a clinical ' +
                'construct, and does not administer licensed instruments.',
              tier: 'inference',
              sources: ['ftc-act-5', 'ppra'],
              note:
                'The original specified a "Spielberger TAI scorer", a "52-domain psychometric ' +
                'engine" and an "anxiety severity tracker". The Spielberger inventory is ' +
                'commercially licensed, and the activity described is assessment. Removing it ' +
                'costs the product very little and removes most of its clinical exposure.',
            },
          ],
        },
      ],
    },

    // ─────────────────────────────────────────────────────────────────────────────
    {
      slug: 'identity',
      title: 'Identity and belonging',
      summary:
        'The strongest instinct in the original document, separated from the mechanism that ' +
        'would have undermined it.',
      tone: 'opportunity',
      groups: [
        {
          id: 'identity-sound',
          heading: 'What the evidence supports',
          claims: [
            {
              id: 'identity-curriculum',
              text:
                'Curriculum that reflects students’ histories and communities has produced ' +
                'measured gains in attendance and credits for at-risk students of colour.',
              tier: 'emerging',
              sources: ['dee-penner-2017', 'aronson-laughter-2016'],
              note:
                'The effect came from a course — content, discussion, a teacher — not from a ' +
                'profile setting. Build content and relationship.',
            },
            {
              id: 'identity-belonging-moment',
              text:
                'Brief, well-timed belonging interventions have improved outcomes for Black ' +
                'students in at least one well-known randomised trial, with effects persisting ' +
                'over years.',
              tier: 'emerging',
              sources: ['walton-cohen-2011'],
              note:
                'These interventions work partly because they are brief and non-obvious. A ' +
                'permanent, loud identity layer is a different intervention with no evidence ' +
                'behind it and a real risk of feeling like being singled out.',
            },
          ],
        },
        {
          id: 'identity-wrong',
          heading: 'What the original would have built instead',
          claims: [
            {
              id: 'identity-essentialism',
              text:
                'Treating call-and-response, storytelling and movement as the learning style of ' +
                'an ethnic group assigns cognitive traits by ancestry, which is both unsupported ' +
                'and the opposite of what the design intends.',
              tier: 'retracted',
              sources: ['pashler-2008', 'ladson-billings-1995'],
              note:
                'Domain 4.8 of the student instrument. Culturally relevant pedagogy is about ' +
                'what is taught, whose knowledge counts, and the relationship in the room. It is ' +
                'not a claim that Black children process information differently.',
            },
            {
              id: 'identity-ancestry-field',
              text:
                'Storing a child’s ancestry as a database column that configures the product ' +
                'converts heritage into a processing attribute and creates a sensitive data ' +
                'holding with no operational need.',
              tier: 'inference',
              sources: ['coppa-rule', 'ferpa'],
              note:
                'The original schema included `student_profiles (… ancestry[])` and an "ancestor ' +
                'selector" across "40+ African cultures". A content library a student can browse ' +
                'and choose from needs no stored ethnicity at all — and a library of real ' +
                'intellectual history, paid for and attributed, is a stronger product than a ' +
                'selector.',
            },
            {
              id: 'identity-new-construct',
              text:
                'Describing ancestral pride as a "new construct" invented by the product claims ' +
                'scholarly priority over a question with an existing literature.',
              tier: 'retracted',
              sources: ['ladson-billings-1995', 'aronson-laughter-2016'],
              note:
                'Item 4.7 of the student instrument read "Ancestral pride as potential academic ' +
                'motivator (new construct, MindUnlock)". Racial and ethnic identity development ' +
                'and its relation to achievement is a decades-old field. Engaging with it is a ' +
                'better position than claiming to have founded it.',
            },
          ],
        },
        {
          id: 'identity-governance',
          heading: 'Governance',
          claims: [
            {
              id: 'identity-paid-scholars',
              text:
                'Cultural content is commissioned from and attributed to paid scholars, with a ' +
                'named budget line, before any of it ships.',
              tier: 'inference',
              sources: ['ladson-billings-1995'],
              note:
                'The original listed "African-centered scholars as PAID co-developers" as a risk ' +
                'mitigation while its financial model contained no line item for them. A control ' +
                'with no budget is not a control.',
            },
          ],
        },
      ],
    },

    // ─────────────────────────────────────────────────────────────────────────────
    {
      slug: 'safeguards',
      title: 'Safeguards',
      summary:
        'The legal and ethical perimeter. Several items here are stop conditions, not ' +
        'improvements.',
      tone: 'risk',
      groups: [
        {
          id: 'employment',
          heading: 'Employment and conflict of interest',
          intro:
            'This is the highest-probability serious risk in the whole plan and the original ' +
            'document does not mention it once.',
          claims: [
            {
              id: 'safeguard-conflict',
              text:
                'A public school system employee who sells, or seeks to sell, a product to that ' +
                'same system is in a conflict-of-interest posture governed by state and local ' +
                'ethics law, and the question must be resolved in writing before any sales ' +
                'activity, pilot recruitment, or use of the employer’s name in materials.',
              tier: 'established',
              sources: ['md-ethics'],
              note:
                'The original plan named MCPS as the pilot source, the reference customer, the ' +
                'presentation audience and the first five contracts. The applicable MCPS ethics ' +
                'provisions and panel process must be confirmed directly with MCPS — the specific ' +
                'policy designators are not recorded here because they were not verified. Until ' +
                'that is resolved, the safe posture is: no recruitment of MCPS families, no use ' +
                'of MCPS student data or materials, no work on the venture on MCPS time or ' +
                'equipment, and no approach to MCPS as a buyer.',
            },
          ],
        },
        {
          id: 'data',
          heading: 'Student data',
          claims: [
            {
              id: 'safeguard-iep-upload',
              text:
                'Ingesting IEP documents places the product inside the IDEA Part B ' +
                'confidentiality regime, which imposes obligations beyond general FERPA, and the ' +
                'first release should not accept them at all.',
              tier: 'established',
              sources: ['idea-confidentiality', 'ferpa'],
              note:
                'The original made IEP PDF upload step one of its accommodation engine. A short ' +
                'parent-selected list of supports — more time, read aloud, shorter chunks, quiet ' +
                'space — delivers the same product behaviour and holds none of the record.',
            },
            {
              id: 'safeguard-ppra-domains',
              text:
                'An instrument asking a minor about psychological problems, family income, ' +
                'religious practice and appraisals of their family touches categories that ' +
                'federal law treats as protected.',
              tier: 'established',
              sources: ['ppra'],
              note:
                'Domains 1.1–1.12, 6.3–6.5 and the parent instrument’s Domain 2 reach these ' +
                'categories. When the consent requirement attaches depends on funding and how ' +
                'the survey is administered, which is exactly why the safe design is not to ask. ' +
                'The v1 instrument is fifteen minutes and asks only about study behaviour and ' +
                'preferences.',
            },
            {
              id: 'safeguard-coppa',
              text:
                'Collecting personal information from users under 13 requires verifiable parental ' +
                'consent, which is a defined process rather than a checkbox.',
              tier: 'established',
              sources: ['coppa-rule'],
              note:
                'Sixth-graders are routinely 11. The consent flow is a product surface and needs ' +
                'to be designed, not assumed. Confirm the current Rule text before building it.',
            },
            {
              id: 'safeguard-school-official',
              text:
                'A product cannot simultaneously be a direct-to-family service and a school ' +
                'official acting under the school’s direct control; the two postures carry ' +
                'different obligations over the same record.',
              tier: 'established',
              sources: ['ferpa'],
              note:
                'The original sold both a $399 family subscription and a school licence covering ' +
                'the same student. Pick one for v1. The family-direct posture is simpler and ' +
                'avoids the district data-privacy agreement process entirely.',
            },
          ],
        },
        {
          id: 'clinical',
          heading: 'The clinical boundary',
          claims: [
            {
              id: 'safeguard-crisis',
              text:
                'Advertising crisis detection creates an expectation the product will be held ' +
                'to, and a sub-second detection guarantee on a statistical classifier cannot be ' +
                'met.',
              tier: 'inference',
              sources: ['ftc-act-5'],
              note:
                'The original promised "crisis escalation detection with latency < 500ms" and ' +
                'automatic parent and counsellor notification. Missing one incident is the ' +
                'scenario that ends the company. The v1 design: no detection claim, always-visible ' +
                'crisis resources, no automated notification to anyone, and a documented ' +
                'escalation path that is explicitly described to families as human-dependent.',
            },
            {
              id: 'safeguard-parent-notification',
              text:
                'Automatically disclosing a child’s distress to a parent can be the harm rather ' +
                'than the remedy, because the parent is sometimes the source of the distress.',
              tier: 'expert-opinion',
              sources: ['von-der-embse-2018'],
              note:
                'The original specified "threshold alert to parent + counselor if distress ' +
                'detected" as an accommodation feature. Any disclosure design needs a reason to ' +
                'believe it helps this child, which software does not have.',
            },
            {
              id: 'safeguard-iep-autochange',
              text:
                'Accommodations are determined and revised by the IEP team through a defined ' +
                'process; software that silently adjusts them is operating outside that process.',
              tier: 'established',
              sources: ['idea-iep-team'],
              note:
                'The original described an engine that would "auto-configure" and "dynamically ' +
                'adjust" accommodations and generate reports "formatted for IEP meeting ' +
                'submission". The defensible version: the student or parent sets preferences in ' +
                'the app, the app never claims those are the IEP, and anything produced for a ' +
                'meeting is labelled as family-generated information.',
            },
          ],
        },
        {
          id: 'claims-governance',
          heading: 'Claims governance',
          claims: [
            {
              id: 'safeguard-substantiation',
              text:
                'Objective product claims require substantiation at the time they are made, and ' +
                'claims about educational outcomes aimed at parents are a recurring enforcement ' +
                'area.',
              tier: 'established',
              sources: ['ftc-act-5'],
              note:
                'Operational rule, enforced by this repository: no customer-facing surface may ' +
                'assert anything above the tier of its backing claim record. See ' +
                'lib/briefing/validate.ts — the build fails on violation.',
            },
            {
              id: 'safeguard-essa-tier',
              text:
                'District buyers assess products against statutory evidence tiers, and a ' +
                'well-designed small pilot with a logic model and ongoing data collection can ' +
                'legitimately meet the fourth level, which demonstrates a rationale.',
              tier: 'established',
              sources: ['essa-evidence-tiers'],
              note:
                'This is the realistic bar for a first product and the original never mentioned ' +
                'it. It also sets the pilot design: a logic model, a measure, and a plan to study ' +
                'effects is worth more to a buyer than a longer feature list.',
            },
          ],
        },
      ],
    },

    // ─────────────────────────────────────────────────────────────────────────────
    {
      slug: 'validation',
      title: 'Validation',
      summary: 'What the first pilot has to produce for any of this to continue.',
      tone: 'neutral',
      groups: [
        {
          id: 'pilot',
          heading: 'The pilot',
          claims: [
            {
              id: 'validation-primary',
              text:
                'The primary outcome is calibration: the gap between a student’s predicted and ' +
                'actual retrieval accuracy, measured at intake and after six weeks.',
              tier: 'inference',
              sources: ['kornell-bjork-2007', 'soderstrom-bjork-2015'],
              note:
                'Chosen because it is the mechanism the product claims to act on, it is measured ' +
                'by the product itself at no extra burden, and it is not confounded by whatever ' +
                'else is happening in a student’s term.',
            },
            {
              id: 'validation-secondary',
              text:
                'Secondary outcomes are delayed retention on material the student chose, and ' +
                'whether the student still uses the system in week six without an adult ' +
                'prompting them.',
              tier: 'inference',
              sources: ['dunlosky-2013'],
              note:
                'Unprompted week-six use is the honest early signal. Most study tools die there ' +
                'and the original roadmap had no measure that would have detected it.',
            },
            {
              id: 'validation-safety',
              text:
                'The pilot stops if any student reports increased anxiety attributable to the ' +
                'product, or if any safeguarding concern surfaces that the design did not ' +
                'anticipate.',
              tier: 'inference',
              sources: ['von-der-embse-2018'],
              note:
                'A stop condition defined in advance, because a founder evaluating their own ' +
                'product will not define one in the moment.',
            },
            {
              id: 'validation-no-claims',
              text:
                'Until the pilot reports, no outcome claim of any kind may appear in any ' +
                'customer-facing material.',
              tier: 'inference',
              sources: ['ftc-act-5', 'essa-evidence-tiers'],
              note:
                'This is the founder’s own stated operating rule. It is recorded here so it ' +
                'survives contact with a sales conversation.',
            },
          ],
        },
      ],
    },
  ],
};

export default MINDUNLOCK_BRIEFING;
