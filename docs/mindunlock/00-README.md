# MindUnlock — audit and expansion

A nine-lens expert audit of the MindUnlock Academy planning document
(`MindUnlock_Academy.jsx`, 859 lines), plus the rebuilt, evidence-graded version of the
document itself.

---

## Start here

| If you have | Read |
|---|---|
| 10 minutes | [`01-executive-summary.md`](01-executive-summary.md) |
| 30 minutes | the executive summary, then [`90-verification.md`](90-verification.md) |
| An hour | add [`30-red-team.md`](30-red-team.md) and [`40-mcps-sped.md`](40-mcps-sped.md) |
| You want to build | [`31-blue-team.md`](31-blue-team.md) and [`60-deepseek-engineering.md`](60-deepseek-engineering.md) |

**Before you act on any single finding, read `90-verification.md`.** It is short, and it tells
you how much to trust the rest.

---

## The documents

| File | Lens | What it covers |
|---|---|---|
| [`01-executive-summary.md`](01-executive-summary.md) | — | Synthesis across all lenses. What survives, what must change, what to do next. |
| [`02-remediation-checklist.md`](02-remediation-checklist.md) | — | **Gate 0a.** Every unsupported claim, its exact line, and its replacement wording. The highest-leverage hour of work available. |
| [`10-code-and-accessibility-audit.md`](10-code-and-accessibility-audit.md) | — | The code and WCAG audit **I ran and verified myself**, with measured contrast ratios and axe results. |
| [`20-evidence-audit.md`](20-evidence-audit.md) | Research integrity | Every citation, named method, effect size and number, checked against its source. |
| [`30-red-team.md`](30-red-team.md) | Red team | Legal, ethical, clinical, privacy, AI-security and reputational exposure. |
| [`31-blue-team.md`](31-blue-team.md) | Blue team | The defensible version: controls, architecture, governance, sequencing. |
| [`40-mcps-sped.md`](40-mcps-sped.md) | MCPS special education | IDEA, COMAR, MSDE, MCPS procurement, and what would actually sell. |
| [`50-learning-science-expansion.md`](50-learning-science-expansion.md) | Learning science | The world evidence base the artifact is missing. |
| [`51-notetaking-metacognition.md`](51-notetaking-metacognition.md) | Note-taking & metacognition | Replacement specification for both sections. |
| [`60-deepseek-engineering.md`](60-deepseek-engineering.md) | Systems & cost | Unit economics, scope, architecture, evaluability. |
| [`70-code-modernization.md`](70-code-modernization.md) | Code & a11y | The independent code lens (compare with `10-`). |
| [`80-business-reality.md`](80-business-reality.md) | Business reality | P&L, revenue assumptions, grants, go-to-market, competition. |
| [`90-verification.md`](90-verification.md) | Verification | What survived adversarial checking on the research-integrity lens, and the error rate to assume elsewhere. |
| [`91-targeted-verification.md`](91-targeted-verification.md) | Targeted verification | **The career- and liability-critical claims, checked. Read this before acting on anything in `30-` or `40-`.** |

The rebuilt document itself lives in the app, not in this folder:
`frontend/src/content/mindunlock/` (content as graded claims),
`frontend/src/lib/briefing/` (the model and its integrity gate),
`/briefings/mindunlock` (the reader).

---

## How this was produced, and what that is worth

Nine independent expert lenses each read the full source and used live web search to check
statutes, regulations, effect sizes and product facts against primary sources. Each lens
returned findings with an explicit evidence tier.

**What ran:** all nine lenses — research integrity, red team, blue team, MCPS special education,
learning science, note-taking and metacognition, systems and cost engineering, code and
accessibility, and business reality. **188 findings and 118 proposed additions.**

**What did not:** the full verification suite. Across three attempts, the thirteen-auditor stage
hit a usage limit each time; **one skeptic completed**, on the research-integrity lens, and the
cross-lens synthesis never ran.

**What was done instead:** four skeptics were pointed at only the claims that could cost the
founder his job, expose him to liability, or embarrass him in front of a district. All four
completed — see [`91-targeted-verification.md`](91-targeted-verification.md). They produced the
sharpest corrections in the whole exercise, including retiring a figure this audit had
previously called the single most valuable finding in it.

**A caveat that applies to all of it:** the targeted verifiers were largely unable to reach
primary sources — `mgaleg.maryland.gov`, `ethics.maryland.gov`, `law.justia.com`,
`law.cornell.edu`, `labor.maryland.gov`, `ecfr.gov`, `ftc.gov` and both MCPS domains were
blocked from this environment. Much of what they report rests on search returns and secondary
summaries rather than statute text read directly. They flagged this themselves. It means those
documents are **a map of what to open**, not a substitute for opening it.

[`90-verification.md`](90-verification.md) records exactly what that one verifier found — and it
is the most important file in this folder, because it tells you the **error rate to assume on
everything else**:

> Roughly 60% of the lens's findings survive adversarial checking intact, about 25% survive in
> weakened form, and a handful of its supporting citations and remedies would themselves fail
> the verification gate it proposes.

Six of 23 findings refuted or materially corrected. Six substantive items missed. And the lens
**introduced a new false claim inside its own recommended fix** — it told the founder to publish
that FSRS is "Anki's default scheduler," which it is not.

That is the correction rate on the lens whose *entire job* was citation accuracy. Assume at
least that rate on the eight unverified lenses. **Do not carry any specific number, statute
section or legal conclusion from them into a grant application, an investor conversation or a
district meeting without reading the primary source yourself.**

The exception is [`10-code-and-accessibility-audit.md`](10-code-and-accessibility-audit.md):
every claim in it was measured directly rather than reasoned, so it needs no verification.

### Reading the evidence tiers

| Tier | Means |
|---|---|
| `ESTABLISHED` | Replicated meta-analytic evidence, or the text of a statute or regulation. |
| `EMERGING` | Real empirical support that is thin, contested or unreplicated. |
| `EXPERT-OPINION` | A credible professional position, not empirically settled. |
| `INFERENCE` | The lens's own reasoning from the above. Defensible, but reasoning. |
| `SPECULATION` | Flagged as unsupported. |

Within a finding's **Evidence** field, anything marked `UNVERIFIED` is a lead the lens could not
confirm — several hosts (including `ww2.montgomeryschoolsmd.org` and `docs.ankiweb.net`) were
unreachable from the audit environment. Those specific items need checking against the primary
source before you rely on them. The lenses were instructed never to invent a citation, statute
section or effect size, and they flagged their own gaps rather than filling them; that
discipline is visible throughout and is the main reason to trust the rest.

### What this is not

Not legal advice. Several findings turn on Maryland ethics law, IDEA confidentiality, PPRA,
COPPA and FTC substantiation standards. They identify questions a lawyer should answer, and in
two cases identify questions that should be answered **before** any further building. They do
not answer them.

---

## The one-line version

The problem identification is sound and the three structural insights — family as the unit of
instruction, identity and belonging as academic levers, and accommodations without skill-building
producing learned helplessness — are worth building on. The evidence base presented around them
is substantially fabricated, and the go-to-market plan, as written, is an MCPS employee selling
a psychological-assessment product to MCPS using MCPS children as the pilot.

Fix the second thing before touching the first.
