import type { Source } from '@/lib/briefing/types';

/**
 * Sources cited by the MindUnlock briefing.
 *
 * Rules for this file:
 * - Full author lists, not "et al.", so a reader can find the work.
 * - `caveat` records what the source does NOT support. Most citation drift happens when a
 *   finding is quoted away from its boundary conditions, so the boundary lives next to it.
 * - Nothing goes in here that has not been located. A half-remembered citation is worse
 *   than none, because it survives review.
 */
export const MINDUNLOCK_SOURCES: Source[] = [
  // ─── Learning science: the high-utility core ────────────────────────────────────
  {
    id: 'dunlosky-2013',
    kind: 'systematic-review',
    authors: 'Dunlosky, Rawson, Marsh, Nathan & Willingham',
    year: 2013,
    title: 'Improving Students’ Learning With Effective Learning Techniques',
    venue: 'Psychological Science in the Public Interest, 14(1), 4–58',
    locator: 'https://doi.org/10.1177/1529100612453266',
    caveat:
      'Rates ten techniques for utility. Practice testing and distributed practice are rated ' +
      'high; highlighting, rereading, summarisation, imagery and the keyword mnemonic are ' +
      'rated low. It does not evaluate note-taking formats or any culturally specific pedagogy.',
  },
  {
    id: 'cepeda-2006',
    kind: 'meta-analysis',
    authors: 'Cepeda, Pashler, Vul, Wixted & Rohrer',
    year: 2006,
    title: 'Distributed Practice in Verbal Recall Tasks: A Review and Quantitative Synthesis',
    venue: 'Psychological Bulletin, 132(3), 354–380',
    locator: 'https://doi.org/10.1037/0033-2909.132.3.354',
    caveat:
      'Overwhelmingly verbal recall in laboratory conditions. The optimal gap depends on the ' +
      'retention interval, which means "space it out" is underspecified without a target date.',
  },
  {
    id: 'roediger-karpicke-2006',
    kind: 'primary-study',
    authors: 'Roediger & Karpicke',
    year: 2006,
    title: 'Test-Enhanced Learning: Taking Memory Tests Improves Long-Term Retention',
    venue: 'Psychological Science, 17(3), 249–255',
    locator: 'https://doi.org/10.1111/j.1467-9280.2006.01693.x',
    caveat:
      'Undergraduates, prose passages, laboratory setting. The retrieval advantage appears on ' +
      'delayed tests; on immediate tests rereading can look better, which is why students ' +
      'reliably choose the worse strategy.',
  },
  {
    id: 'soderstrom-bjork-2015',
    kind: 'systematic-review',
    authors: 'Soderstrom & Bjork',
    year: 2015,
    title: 'Learning Versus Performance: An Integrative Review',
    venue: 'Perspectives on Psychological Science, 10(2), 176–199',
    locator: 'https://doi.org/10.1177/1745691615569000',
    caveat:
      'Argues performance during training is an unreliable index of learning. Directly limits ' +
      'what any progress dashboard can honestly tell a learner.',
  },
  {
    id: 'sweller-2019',
    kind: 'systematic-review',
    authors: 'Sweller, van Merriënboer & Paas',
    year: 2019,
    title: 'Cognitive Architecture and Instructional Design: 20 Years Later',
    venue: 'Educational Psychology Review, 31, 261–292',
    locator: 'https://doi.org/10.1007/s10648-019-09465-5',
    caveat:
      'Cognitive load effects are conditional on learner expertise; several reverse for ' +
      'experts (the expertise-reversal effect).',
  },
  {
    id: 'kalyuga-2003',
    kind: 'systematic-review',
    authors: 'Kalyuga, Ayres, Chandler & Sweller',
    year: 2003,
    title: 'The Expertise Reversal Effect',
    venue: 'Educational Psychologist, 38(1), 23–31',
    locator: 'https://doi.org/10.1207/S15326985EP3801_4',
    caveat:
      'Shows that guidance which helps novices harms experts, and vice versa. The practical ' +
      'consequence is that "desirable difficulty" is not a universal setting.',
  },
  {
    id: 'rosenshine-2012',
    kind: 'practice-guide',
    authors: 'Rosenshine',
    year: 2012,
    title: 'Principles of Instruction: Research-Based Strategies That All Teachers Should Know',
    venue: 'American Educator, 36(1), 12–19',
    caveat:
      'A synthesis for teaching practice, not a controlled evaluation of a named programme.',
  },
  {
    id: 'hattie-timperley-2007',
    kind: 'systematic-review',
    authors: 'Hattie & Timperley',
    year: 2007,
    title: 'The Power of Feedback',
    venue: 'Review of Educational Research, 77(1), 81–112',
    locator: 'https://doi.org/10.3102/003465430298487',
  },
  {
    id: 'kluger-denisi-1996',
    kind: 'meta-analysis',
    authors: 'Kluger & DeNisi',
    year: 1996,
    title:
      'The Effects of Feedback Interventions on Performance: A Historical Review, a Meta-Analysis, ' +
      'and a Preliminary Feedback Intervention Theory',
    venue: 'Psychological Bulletin, 119(2), 254–284',
    locator: 'https://doi.org/10.1037/0033-2909.119.2.254',
    caveat:
      'A substantial minority of feedback interventions reduced performance, particularly when ' +
      'feedback drew attention to the self rather than the task.',
  },

  // ─── Metacognition and self-regulation ──────────────────────────────────────────
  {
    id: 'nelson-narens-1990',
    kind: 'book',
    authors: 'Nelson & Narens',
    year: 1990,
    title: 'Metamemory: A Theoretical Framework and New Findings',
    venue: 'The Psychology of Learning and Motivation, 26, 125–173',
    caveat:
      'A theoretical architecture (meta-level monitoring and control), not an intervention ' +
      'with an effect size.',
  },
  {
    id: 'kornell-bjork-2007',
    kind: 'primary-study',
    authors: 'Kornell & Bjork',
    year: 2007,
    title: 'The Promise and Perils of Self-Regulated Study',
    venue: 'Psychonomic Bulletin & Review, 14(2), 219–224',
    locator: 'https://doi.org/10.3758/BF03194055',
    caveat: 'College students. Documents what learners choose, not what instruction can change.',
  },
  {
    id: 'karpicke-2009',
    kind: 'primary-study',
    authors: 'Karpicke, Butler & Roediger',
    year: 2009,
    title:
      'Metacognitive Strategies in Student Learning: Do Students Practise Retrieval When They ' +
      'Study on Their Own?',
    venue: 'Memory, 17(4), 471–479',
    locator: 'https://doi.org/10.1080/09658210802647009',
    caveat: 'Survey of undergraduates; self-report of study habits.',
  },
  {
    id: 'eef-metacognition',
    kind: 'practice-guide',
    authors: 'Education Endowment Foundation',
    year: 2021,
    title: 'Metacognition and Self-Regulated Learning: Guidance Report',
    venue: 'Education Endowment Foundation (UK)',
    locator: 'https://educationendowmentfoundation.org.uk/education-evidence/guidance-reports/metacognition',
    caveat:
      'The EEF toolkit figure is an average months-progress estimate across a heterogeneous ' +
      'evidence base, not a predicted effect for any one programme.',
  },
  {
    id: 'graham-harris-srsd',
    kind: 'meta-analysis',
    authors: 'Graham & Perin',
    year: 2007,
    title: 'A Meta-Analysis of Writing Instruction for Adolescent Students',
    venue: 'Journal of Educational Psychology, 99(3), 445–476',
    locator: 'https://doi.org/10.1037/0022-0663.99.3.445',
    caveat:
      'Strategy instruction (the family that includes Self-Regulated Strategy Development) ' +
      'shows the largest effects in this synthesis; the evidence is strongest for writing, ' +
      'and should not be generalised to test preparation without further support.',
  },

  // ─── Note-taking ────────────────────────────────────────────────────────────────
  {
    id: 'konrad-2009',
    kind: 'meta-analysis',
    authors: 'Konrad, Joseph & Eveleigh',
    year: 2009,
    title:
      'A Meta-Analytic Review of Guided Notes',
    venue: 'Education and Treatment of Children, 32(3), 421–444',
    caveat:
      'Guided/partial notes studies are concentrated in special education and small-n designs; ' +
      'effects are consistent but the literature is not large.',
  },
  {
    id: 'nesbit-adesope-2006',
    kind: 'meta-analysis',
    authors: 'Nesbit & Adesope',
    year: 2006,
    title: 'Learning With Concept and Knowledge Maps: A Meta-Analysis',
    venue: 'Review of Educational Research, 76(3), 413–448',
    locator: 'https://doi.org/10.3102/00346543076003413',
    caveat:
      'Covers concept and knowledge maps — structured, relation-labelled representations. It ' +
      'is not evidence for freeform "mind mapping" in the popular sense.',
  },
  {
    id: 'mueller-oppenheimer-2014',
    kind: 'primary-study',
    authors: 'Mueller & Oppenheimer',
    year: 2014,
    title: 'The Pen Is Mightier Than the Keyboard: Advantages of Longhand Over Laptop Note Taking',
    venue: 'Psychological Science, 25(6), 1159–1168',
    locator: 'https://doi.org/10.1177/0956797614524581',
    caveat:
      'Widely cited and widely misused. Subsequent replication attempts did not reproduce the ' +
      'headline advantage; see morehead-2019.',
  },
  {
    id: 'morehead-2019',
    kind: 'primary-study',
    authors: 'Morehead, Dunlosky & Rawson',
    year: 2019,
    title:
      'How Much Mightier Is the Pen Than the Keyboard for Note-Taking? A Replication and ' +
      'Extension of Mueller and Oppenheimer (2014)',
    venue: 'Educational Psychology Review, 31, 753–780',
    locator: 'https://doi.org/10.1007/s10648-019-09468-2',
    caveat:
      'Did not replicate the longhand advantage. Taken together with the original, the honest ' +
      'position is that modality matters less than what the note-taker does with the notes.',
  },
  {
    id: 'mayer-multimedia',
    kind: 'book',
    authors: 'Mayer',
    year: 2021,
    title: 'Multimedia Learning (3rd ed.)',
    venue: 'Cambridge University Press',
    caveat:
      'The multimedia principles are well supported for designed instructional materials; they ' +
      'are not a licence for decorative illustration.',
  },

  // ─── Things the original document got wrong ─────────────────────────────────────
  {
    id: 'pashler-2008',
    kind: 'systematic-review',
    authors: 'Pashler, McDaniel, Rohrer & Bjork',
    year: 2008,
    title: 'Learning Styles: Concepts and Evidence',
    venue: 'Psychological Science in the Public Interest, 9(3), 105–119',
    locator: 'https://doi.org/10.1111/j.1539-6053.2009.01038.x',
    caveat:
      'Found no adequate evidence for the meshing hypothesis — that matching instruction to a ' +
      'stated style improves learning. Learners do have preferences; preferences are not a ' +
      'basis for differentiating instruction.',
  },
  {
    id: 'rayner-2016',
    kind: 'systematic-review',
    authors: 'Rayner, Schotter, Masson, Potter & Treiman',
    year: 2016,
    title: 'So Much to Read, So Little Time: How Do We Read, and Can Speed Reading Help?',
    venue: 'Psychological Science in the Public Interest, 16(1), 4–34',
    locator: 'https://doi.org/10.1177/1529100615623267',
    caveat:
      'Concludes that large reading-speed gains come at the cost of comprehension, and that the ' +
      'main lever on reading rate is language skill and prior knowledge, not technique.',
  },
  {
    id: 'sisk-2018',
    kind: 'meta-analysis',
    authors: 'Sisk, Burgoyne, Sun, Butler & Macnamara',
    year: 2018,
    title:
      'To What Extent and Under Which Circumstances Are Growth Mind-Sets Important to Academic ' +
      'Achievement? Two Meta-Analyses',
    venue: 'Psychological Science, 29(4), 549–571',
    locator: 'https://doi.org/10.1177/0956797617739704',
    caveat:
      'Overall effects were weak. Effects were somewhat larger for academically at-risk and ' +
      'low-SES students, which is the subgroup this product targets.',
  },
  {
    id: 'yeager-2019',
    kind: 'primary-study',
    authors: 'Yeager and the National Study of Learning Mindsets team',
    year: 2019,
    title: 'A National Experiment Reveals Where a Growth Mindset Improves Achievement',
    venue: 'Nature, 573, 364–369',
    locator: 'https://doi.org/10.1038/s41586-019-1466-y',
    caveat:
      'A large, pre-registered US trial. The effect was real but small and concentrated among ' +
      'lower-achieving students in schools with supportive peer norms — a short intervention, ' +
      'not a platform-wide philosophy.',
  },
  {
    id: 'flore-wicherts-2015',
    kind: 'meta-analysis',
    authors: 'Flore & Wicherts',
    year: 2015,
    title:
      'Does Stereotype Threat Influence Performance of Girls in Stereotyped Domains? ' +
      'A Meta-Analysis',
    venue: 'Journal of School Psychology, 53(1), 25–44',
    locator: 'https://doi.org/10.1016/j.jsp.2014.10.002',
    caveat:
      'Found evidence of publication bias; the adjusted estimate was close to zero. This is ' +
      'about girls in stereotyped domains specifically, not all stereotype-threat research, ' +
      'but it is the kind of correction any citation of the 1995 original now has to carry.',
  },
  {
    id: 'melby-lervag-2016',
    kind: 'meta-analysis',
    authors: 'Melby-Lervåg, Redick & Hulme',
    year: 2016,
    title:
      'Working Memory Training Does Not Improve Performance on Measures of Intelligence or Other ' +
      'Measures of “Far Transfer”',
    venue: 'Perspectives on Psychological Science, 11(4), 512–534',
    locator: 'https://doi.org/10.1177/1745691616635612',
  },

  // ─── Intervention evidence for this population ──────────────────────────────────
  {
    id: 'von-der-embse-2018',
    kind: 'meta-analysis',
    authors: 'von der Embse, Jester, Roy & Post',
    year: 2018,
    title: 'Test Anxiety Effects, Predictors, and Correlates: A 30-Year Meta-Analytic Review',
    venue: 'Journal of Affective Disorders, 227, 483–493',
    locator: 'https://doi.org/10.1016/j.jad.2017.11.048',
    caveat:
      'Establishes the association between test anxiety and performance and its predictors. ' +
      'Treatment-outcome evidence is a separate literature and should be cited separately.',
  },
  {
    id: 'ramirez-beilock-2011',
    kind: 'primary-study',
    authors: 'Ramirez & Beilock',
    year: 2011,
    title: 'Writing About Testing Worries Boosts Exam Performance in the Classroom',
    venue: 'Science, 331(6014), 211–213',
    locator: 'https://doi.org/10.1126/science.1199427',
    caveat:
      'Short expressive-writing intervention immediately before an exam. Later replication ' +
      'attempts have been mixed; treat as promising rather than settled.',
  },
  {
    id: 'walton-cohen-2011',
    kind: 'primary-study',
    authors: 'Walton & Cohen',
    year: 2011,
    title: 'A Brief Social-Belonging Intervention Improves Academic and Health Outcomes',
    venue: 'Science, 331(6023), 1447–1451',
    locator: 'https://doi.org/10.1126/science.1198364',
    caveat:
      'Effects were concentrated among African American students in a selective-college ' +
      'context. Scaling to middle school is an open question, not a settled result.',
  },
  {
    id: 'hulleman-harackiewicz-2009',
    kind: 'primary-study',
    authors: 'Hulleman & Harackiewicz',
    year: 2009,
    title: 'Promoting Interest and Performance in High School Science Classes',
    venue: 'Science, 326(5958), 1410–1412',
    locator: 'https://doi.org/10.1126/science.1177067',
    caveat: 'Benefit concentrated among students with low initial expectations of success.',
  },
  {
    id: 'dee-penner-2017',
    kind: 'primary-study',
    authors: 'Dee & Penner',
    year: 2017,
    title:
      'The Causal Effects of Cultural Relevance: Evidence From an Ethnic Studies Curriculum',
    venue: 'American Educational Research Journal, 54(1), 127–166',
    locator: 'https://doi.org/10.3102/0002831216677002',
    caveat:
      'A regression-discontinuity study of a San Francisco ethnic studies course for students ' +
      'assigned on a GPA threshold. Large effects on attendance and credits for that at-risk ' +
      'group. It is evidence for culturally relevant *curriculum*, not for identity as a ' +
      'cognitive-profile field.',
  },
  {
    id: 'aronson-laughter-2016',
    kind: 'systematic-review',
    authors: 'Aronson & Laughter',
    year: 2016,
    title:
      'The Theory and Practice of Culturally Relevant Education: A Synthesis of Research Across ' +
      'Content Areas',
    venue: 'Review of Educational Research, 86(1), 163–206',
    locator: 'https://doi.org/10.3102/0034654315582066',
    caveat:
      'A synthesis of largely qualitative and quasi-experimental work. Supports the practice; ' +
      'does not yield a pooled effect size.',
  },
  {
    id: 'ladson-billings-1995',
    kind: 'book',
    authors: 'Ladson-Billings',
    year: 1995,
    title: 'Toward a Theory of Culturally Relevant Pedagogy',
    venue: 'American Educational Research Journal, 32(3), 465–491',
    locator: 'https://doi.org/10.3102/00028312032003465',
  },

  // ─── Legal and regulatory ───────────────────────────────────────────────────────
  {
    id: 'ferpa',
    kind: 'regulation',
    authors: 'US Department of Education',
    year: 1974,
    title: 'Family Educational Rights and Privacy Act regulations',
    venue: '34 CFR Part 99',
    locator: 'https://www.ecfr.gov/current/title-34/subtitle-A/part-99',
    caveat:
      'The school-official exception at 34 CFR 99.31(a)(1) requires the school to retain direct ' +
      'control over the vendor’s use of the record. A product sold direct to families is not ' +
      'operating under that exception.',
  },
  {
    id: 'idea-confidentiality',
    kind: 'regulation',
    authors: 'US Department of Education',
    year: 2006,
    title: 'IDEA Part B — Confidentiality of Information',
    venue: '34 CFR 300.610–300.627',
    locator: 'https://www.ecfr.gov/current/title-34/subtitle-B/chapter-III/part-300/subpart-F',
    caveat:
      'Imposes obligations on special education records beyond general FERPA, including ' +
      'destruction of personally identifiable information when no longer needed.',
  },
  {
    id: 'idea-iep-team',
    kind: 'regulation',
    authors: 'US Department of Education',
    year: 2006,
    title: 'IDEA Part B — IEP Team and development of the IEP',
    venue: '34 CFR 300.321 and 300.324',
    locator: 'https://www.ecfr.gov/current/title-34/subtitle-B/chapter-III/part-300',
    caveat:
      'Accommodations are decided and revised by the IEP team through a defined process. ' +
      'Nothing in the regulation contemplates unilateral adjustment by a vendor’s software.',
  },
  {
    id: 'ppra',
    kind: 'statute',
    authors: 'US Congress',
    year: 1978,
    title: 'Protection of Pupil Rights Amendment',
    venue: '20 U.S.C. § 1232h',
    locator: 'https://www.law.cornell.edu/uscode/text/20/1232h',
    caveat:
      'Lists protected categories including mental or psychological problems, income, religious ' +
      'practices and critical appraisals of family members. The consent requirements attach in ' +
      'defined circumstances — chiefly surveys funded by the Department of Education — so the ' +
      'precise obligation depends on how an instrument is funded and administered.',
  },
  {
    id: 'coppa-rule',
    kind: 'regulation',
    authors: 'US Federal Trade Commission',
    year: 2013,
    title: "Children's Online Privacy Protection Rule",
    venue: '16 CFR Part 312',
    locator: 'https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-312',
    caveat:
      'Applies to operators collecting personal information from children under 13 and requires ' +
      'verifiable parental consent. The Rule has been amended; check the current text before ' +
      'relying on any specific provision.',
  },
  {
    id: 'ftc-act-5',
    kind: 'statute',
    authors: 'US Congress',
    year: 1914,
    title: 'Federal Trade Commission Act, Section 5 — unfair or deceptive acts or practices',
    venue: '15 U.S.C. § 45',
    locator: 'https://www.law.cornell.edu/uscode/text/15/45',
    caveat:
      'Objective product claims require substantiation at the time they are made. Education and ' +
      'efficacy claims aimed at parents are a recurring enforcement area.',
  },
  {
    id: 'md-ethics',
    kind: 'statute',
    authors: 'State of Maryland',
    year: 2014,
    title: 'Maryland Public Ethics Law — conflicts of interest',
    venue: 'Md. Code, General Provisions, Title 5',
    locator: 'https://law.justia.com/codes/maryland/general-provisions/title-5/',
    caveat:
      'Local school system employees are additionally covered by their system’s own ethics ' +
      'regulations and panel. The operative rules for an MCPS employee are the MCPS ethics ' +
      'provisions; the specific designators must be confirmed with MCPS before relying on them.',
  },
  {
    id: 'essa-evidence-tiers',
    kind: 'statute',
    authors: 'US Congress',
    year: 2015,
    title: 'Every Student Succeeds Act — definition of evidence-based',
    venue: '20 U.S.C. § 7801(21)',
    locator: 'https://www.law.cornell.edu/uscode/text/20/7801',
    caveat:
      'Defines strong, moderate and promising evidence, plus a fourth level that demonstrates a ' +
      'rationale. District buyers increasingly ask which tier a product meets.',
  },
];
