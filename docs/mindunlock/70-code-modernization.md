# Code and accessibility (lens output)

> The independent code/a11y lens. See 10-code-and-accessibility-audit.md for the audit I ran and verified myself.

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

The single most important finding: this file contains **zero** accessibility affordances. A grep for `aria-`, `role=`, `<main`, `<nav`, `<header`, `<footer`, `alt=` and `lang=` across all 858 lines returns **0 matches**. Not "incomplete" — absent. Meanwhile the content it renders claims `accessibility-native (WCAG 2.1 AA)` (L685), `Sensory-aware palette; dark/high-contrast modes; ADHD-friendly custom tokens; accessible components` (L685), `sensory-aware design system; focus mode` (L122), `UDL progressive disclosure`, and `Read-Aloud / TTS`, `Reduced Distractions`, `Visual Supports` as auto-applied IEP accommodations (L550-557). The artifact is the product's first and only shipped code, and it is a counter-example to its own specification. For a document whose purpose is to persuade MCPS that this team can build for neurodivergent and literacy-impaired children, that gap is the strongest argument against the pitch that the pitch itself makes.

Three structural facts drive everything else. (1) The ten tab buttons (L846-853) and every sub-tab bar (L24-28) are plain `<button>`s with click handlers — no `role="tablist"/"tab"/"tabpanel"`, no `aria-selected`, no `aria-controls`, no roving tabindex, no arrow-key handling, and no focus or live-region strategy when the entire page body swaps underneath the user. (2) `text-xs` (12px) appears **79 times** versus 33 `text-sm` and **zero** `text-base`; 12px is the dominant body size for an audience defined by reading difficulty. (3) Every assertion in the document is a bare string literal inside JSX — citations such as `(Zeidner, 1998; von der Embse et al., 2018)` (L164) and effect sizes such as `(ES: 0.8)` (L465) are *prose*, not data, so nothing in the system can distinguish a meta-analysis from a guess. That is the direct violation of the founder's own "evidence before claims" rule.

Important: a modernised replacement **already exists in this repo** at `/home/user/AEOS/frontend/src/` (typed `Briefing` model, build-failing validator, 6 sections, 50 graded claims, 40 sources, routed pages, token-based CSS, `npm test` → 14/14 pass). My `additions` close the gaps that remain in it rather than re-specifying it from scratch.

---

## Findings

### A11Y-01 — Tab bar is ten undecorated buttons: no tab/tablist/tabpanel semantics, no keyboard model

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.98 |

**What the artifact says**
> L846-853: `<div className="max-w-7xl mx-auto flex overflow-x-auto px-3 gap-1 py-2">{tabs.map(t=>(<button key={t.id} onClick={()=>setActiveTab(t.id)} className={...}>{t.e} {t.label}</button>))}</div>` — and L855 `<div className="max-w-7xl mx-auto p-4 pb-12">{content[activeTab]}</div>`

**The problem**

A screen reader user hears ten generic buttons with no indication of which is current, how many there are, or that activating one replaces the page body. There is no `role="tablist"` on the container, no `role="tab"` on the buttons, no `aria-selected`, no `aria-controls` pointing at the panel, no `id`/`aria-labelledby` pairing, no `role="tabpanel"` on L855, and no roving tabindex — all ten buttons sit in the Tab sequence, so reaching the body content of the Roadmap tab requires ten Tab presses past controls the user has no reason to visit. Arrow keys do nothing; Home/End do nothing. The selected state is carried only by `bg-purple-700 text-white` (L849), i.e. by styling with no programmatic equivalent, which is the textbook SC 4.1.2 failure: state is not exposed to assistive technology.

**Evidence**

WCAG 2.2 SC 4.1.2 Name, Role, Value (Level A) requires that for all UI components, states and properties set by the author be programmatically determinable and notification of changes be available to user agents including AT. The W3C ARIA Authoring Practices Tabs pattern specifies: tablist container role, tab role per control, tabpanel per panel, `aria-selected="true"` on the active tab and `false` on all others, `aria-controls` on each tab referring to its panel, `aria-labelledby` on each panel referring back to its tab, arrow-key movement between tabs with wrap-around, and a roving tabindex so only one tab is in the Tab sequence. Verified via W3C APG Tabs pattern (https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) and MDN ARIA tab role; note w3.org could not be fetched directly from this session (host not in the allowed network domains), so these were confirmed through search result summaries of the W3C pages rather than the primary HTML.

**Recommendation**

Do not reimplement tabs. Replace client tab state with real routes — one URL per section — which fixes SC 4.1.2, bookmarking, the back button and server rendering simultaneously. This is already done in the repo at `/home/user/AEOS/frontend/src/app/briefings/mindunlock/[section]/page.tsx` with `/home/user/AEOS/frontend/src/components/briefing/SectionNav.tsx` using `<nav aria-label="Briefing sections"><ol>` + `<Link aria-current="page">`. If an in-page tab widget is ever genuinely needed, use a vetted headless primitive (Radix `Tabs`, React Aria `useTabList`) rather than hand-rolling the roving-tabindex logic.

### A11Y-02 — Zero landmarks and zero ARIA in 858 lines: the whole document is nested <div>s

| | |
|---|---|
| **Severity** | `BLOCKER` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.98 |

**What the artifact says**
> L832-857 `return (<div className="min-h-screen bg-slate-950 text-white"><div className="bg-gradient-to-r ...">...<div className="sticky top-0 z-20 ...">...<div className="max-w-7xl mx-auto p-4 pb-12">{content[activeTab]}</div></div>` — plus `Card` (L18) and `SH` (L21) which emit only `div`/`h2`/`p`.

**The problem**

`grep -c 'aria-\|role=\|<main\|<nav\|<header\|<footer\|lang='` over the file returns 0. There is no banner, no navigation, no main, no contentinfo. A screen reader user cannot use landmark navigation (NVDA `D`, VoiceOver rotor) to reach the content; they must linearly traverse the masthead, the eight decorative pills at L839-841, and the ten tab buttons before reaching anything. There is also no skip link, so keyboard users repeat that traversal on every tab change. Programmatic structure is being communicated entirely through Tailwind class names, which are invisible to the accessibility tree.

**Evidence**

WCAG 2.2 SC 1.3.1 Info and Relationships (Level A): information, structure and relationships conveyed through presentation must be programmatically determined or available in text. SC 2.4.1 Bypass Blocks (Level A) requires a mechanism to skip repeated blocks of content; its strict applicability to a single-document SPA is an interpretation question, but the ten-item sticky bar at L845-854 is functionally a repeated block across every view change. [INFERENCE on 2.4.1 scope; ESTABLISHED on 1.3.1.]

**Recommendation**

Emit `<header>` (banner), `<nav aria-label="...">`, `<main id="main" tabindex="-1">`, `<footer>`, and a `.skip-link` that is visible on focus. The repo's `[section]/page.tsx` already does exactly this (`<a className="skip-link" href="#briefing-main">`, `<main className="briefing__main" id="briefing-main" tabIndex={-1}>`). Extend the same treatment to `src/app/layout.tsx`, which currently ships only `<html lang="en"><body>{children}</body></html>` with no skip link for the rest of the portal (`/students`, `/assessments`).

### A11Y-03 — Measured contrast failures: five text/background pairs fall below 4.5:1 at 12px

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.96 |

**What the artifact says**
> L62 `<p className="text-slate-500 text-xs mb-2">{c.sub}</p>` on `bg-slate-700` (L59); L63 `<p className="text-red-400 text-xs mb-1">Pain: {c.pain}</p>`; L145 `<p key={t} className="text-slate-400 text-xs py-0.5">`; L489 `<p className="text-slate-500 text-xs">{m.full}</p>`; L510 `<p className="text-slate-500 text-xs mb-1">📖 {n.r}</p>`; L664 `<p className="text-slate-500">-- Core Schema (DeepSeek DDL)</p>`.

**The problem**

I computed every text/background pair in the file against the default Tailwind v3 palette, resolving `bg-slate-800/80` over the page's `bg-slate-950` to rgb(24,34,52). Failures at SC 1.4.3's 4.5:1 threshold for normal-size text (all of these are `text-xs` = 12px, nowhere near the 18.66px-bold/24px large-text exemption): **text-slate-500 on bg-slate-700 = 2.18:1** (L62 customer-profile subtitles, L510 note-taking method citations) — worst in the file, less than half the requirement; **text-slate-500 on bg-slate-800/80 = 3.35:1** (L489 method full names, L385 hours column, L707 deployment CI detail, L749); **text-slate-400 on bg-slate-700 = 4.04:1** (L145 agent task lists, L540 App Design feature bullets, L561, L576, L680, L686, L692, L804 — the single most repeated muted-text pattern in the file); **text-red-400 on bg-slate-700 = 3.74:1** (L63 every "Pain:" line); **text-slate-500 on bg-slate-900 = 3.75:1** (L664 SQL comment). Note two corrections to the common assumption: `text-slate-400` on `bg-slate-800/80` actually **passes** at 6.22:1, and `text-slate-600` is **never used** anywhere in the file (0 occurrences) — I will not report a violation that is not there.

**Evidence**

WCAG 2.2 SC 1.4.3 Contrast (Minimum), Level AA: 4.5:1 for normal text, 3:1 for large text (≥18pt, or ≥14pt bold). Ratios computed with the WCAG relative-luminance formula (sRGB linearisation, L = 0.2126R+0.7152G+0.0722B, (L1+0.05)/(L2+0.05)) in /tmp/claude-0/-home-user-AEOS/7b79576e-a60b-565a-8dd7-5dda9b3dad0c/scratchpad/contrast.py. CAVEAT: the artifact ships no `tailwind.config`, so I assumed the stock Tailwind v3 palette (slate-500 #64748b, slate-700 #334155, slate-800 #1e293b, slate-950 #020617, red-400 #f87171). If a custom theme overrides these, re-run against the real values — the method holds, the numbers would shift.

**Recommendation**

Delete `text-slate-500` entirely and never place `text-slate-400` on `bg-slate-700`. In the token system, define exactly two text roles — `--text` and `--text-muted` — and pin `--text-muted` at ≥7:1 against every surface it is permitted on, which leaves headroom when a surface is later darkened. The repo's `briefing.css` already does this (`--text-muted: #4a5668; /* 7.0:1 on --surface */`, dark `#a9b5c5; /* 7.4:1 */`). Add the automated guard described in ADD-04 so a regression fails CI rather than a design review.

### A11Y-04 — Sub-tab bars repeat the same SC 4.1.2 failure in three more places, with worse contrast

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.97 |

**What the artifact says**
> L24-28 `const SubTab = ({ tabs, active, setActive }) => (<div className="flex flex-wrap gap-2 mb-5">{tabs.map(t => <button key={t.id} onClick={() => setActive(t.id)} className={`... ${active===t.id?"bg-purple-700 text-white":"bg-slate-700 text-slate-400 hover:bg-slate-600 hover:text-white"}`}>{t.label}</button>)}</div>)` — instantiated at L160, L259, L331.

**The problem**

Identical defects to A11Y-01 (no tablist/tab/tabpanel, no `aria-selected`, no `aria-controls`, no arrow keys), compounded by two extras. First, the inactive state is `text-slate-400` on `bg-slate-700` = **4.04:1**, failing SC 1.4.3 for the 14px (`text-sm`) label. Second, the panels these control are rendered by bare `{sub==="idea" && (...)}` conditionals (L161, L183, L222, L260, L282, L302, L332, L362, L392, L417) with no container element at all, so there is nothing an `aria-controls` could point at even if one were added. The widget is unbuildable as ARIA without restructuring.

**Evidence**

SC 4.1.2 (A) and SC 1.4.3 (AA) as above. Contrast computed: slate-400 #94a3b8 on slate-700 #334155 = 4.04:1.

**Recommendation**

Promote the sub-tabs to the same routing model as the top-level sections — they are sub-sections of a document, not a stateful widget. In the repo model this means a nested `groups` array rendered as `<section aria-labelledby>` headings in one scrollable page (already the shape used in `[section]/page.tsx`), which removes the widget entirely rather than fixing it. If disclosure is wanted for cognitive load, use `<details>`/`<summary>` or a vetted Disclosure primitive, both of which are keyboard- and AT-correct for free.

### A11Y-05 — No focus management and no live region when the entire page body is replaced

| | |
|---|---|
| **Severity** | `CRITICAL` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> L848 `onClick={()=>setActiveTab(t.id)}` and L855 `<div className="max-w-7xl mx-auto p-4 pb-12">{content[activeTab]}</div>`

**The problem**

Activating a tab unmounts roughly 100-200 DOM nodes and mounts a different set, while keyboard focus stays on the button and the viewport does not move. A screen reader announces nothing — no `aria-live` region, no `role="status"`, no programmatic focus move to the new content, no heading focus. A blind user has no way to know whether the activation worked; a sighted keyboard user must Tab forward blindly past the remaining nine tabs to find out. The same silence applies to every sub-tab at L160/L259/L331. Reading order is also broken: because the panel is a sibling *after* the tab strip but there is no tabpanel relationship, there is no programmatic link between the control and what it changed.

**Evidence**

SC 4.1.2 (A) requires that changes to states and properties be available to user agents including AT. W3C APG Tabs pattern specifies that the tabpanel is referenced by the tab's `aria-controls` and labelled by the tab via `aria-labelledby`, which is what gives AT the relationship this code lacks. [ESTABLISHED on the normative requirement; INFERENCE that the practical consequence is total silence — I did not run a screen reader against this file in this session.]

**Recommendation**

With real routes, Next.js App Router handles the announcement and focus reset on navigation, which is why routing is the better fix than patching ARIA onto the buttons. Where a panel genuinely swaps in place, move focus to the panel's heading container (`tabIndex={-1}` + `.focus()`) after activation and give it an accessible name; the repo already ships `<main ... id="briefing-main" tabIndex={-1}>` with `.briefing__main:focus { outline: none; }` so the programmatic focus does not paint a stray ring. Add the keyboard/focus test in ADD-05 to hold it.

### A11Y-06 — text-xs (12px) is the dominant body size — 79 occurrences — for an audience defined by reading difficulty

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Counted across the file: `text-xs` ×79, `text-sm` ×33, `text-base` ×0, `text-lg` ×14, `text-xl` ×11, `text-2xl` ×6, `text-3xl` ×1. Examples: L41/L45 problem statements, L277/L297/L316 all 52/38/24 diagnostic items, L338/L368/L423 all certification module lists, L491 method applications, L540 app feature lists.

**The problem**

Tailwind's `text-xs` is 0.75rem = 12px. Every substantive body passage in this document — the problem statement, the entire 52-domain diagnostic, all four certification tracks, the whole App Design tab — renders at 12px. The stated readers include "Students with literacy deficits" (L41), students with "Phonological awareness" and "Reading fluency" deficits (L270), parents who "were never taught HOW to study" (L41), and the document promises "Visual Supports" and "Read-Aloud / TTS" accommodations (L551-555). There is no `text-base` anywhere: the type scale skips from 12px/14px straight to 18px headings, so there is no comfortable reading size in the system at all. This is not a WCAG AA failure in itself — SC 1.4.4 Resize Text (AA) is satisfied because Tailwind sizes are rem-based and survive 200% zoom — but it is a direct contradiction of the product's own accessibility contract, and 12px at a 1.33 line-height gives a cramped measure for dyslexic readers.

**Evidence**

Tailwind font-size scale: `text-xs` = 0.75rem with a default line-height of 1rem (tailwindcss.com/docs/font-size; the 16px line-height figure is from third-party documentation, not the current official v4 theme table, so treat the exact leading as unverified). WCAG 2.2 SC 1.4.4 Resize Text (AA) — satisfied here. SC 1.4.12 Text Spacing (AA) — untested; the dense `py-0.5`/`py-1` rows throughout would need checking under the 1.5× line-height / 0.12em letter-spacing overrides. That specific check is unverified and I would run it with the Text Spacing bookmarklet.

**Recommendation**

Set the document body at 1.0625rem (17px) minimum with line-height 1.65 and a 68ch measure, and reserve 0.8125-0.9375rem strictly for metadata (eyebrows, dates, source kinds). The repo's `briefing.css` already sets `.briefing { font-size: 1.0625rem; line-height: 1.65; }` with `max-width: 68ch` on content columns. Add a `data-density="comfortable|compact"` switch (ADD-06) rather than shrinking the default for information-dense views, and lint against raw `font-size` values outside the token scale.

### A11Y-07 — Heading order skips h2 → h4 in at least nine places; the panels form no coherent outline

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.95 |

**What the artifact says**
> `SH` (L21-23) emits `<h2>`. `Card` (L18-20) emits a bare `<div>`. L159 renders `<SH ... title="PhD-Level Gap Analysis" />` (h2) and the next heading in the DOM is L172 `<h4 className="text-white font-bold mb-3">{g.gap}</h4>` — no h3 between them. Same pattern at L213, L244, L263, L276, L285, L296, L306, L315, L509, L539.

**The problem**

The outline is: h1 (L836, once, in the masthead) → h2 (per tab, from `SH`) → then an arbitrary mixture of h3 (L37, L51, L71, L88, L114, L133, L456, L479, L498, L545, L614, L631, L659, L678, L684, L690, L697, L738) and h4 with no consistent nesting. In the Gap Analysis, Diagnostics, App Design and Course Design tabs the h3 level is skipped entirely, so screen reader users navigating by heading level jump from a section title straight to a leaf. Worse, `Card` renders no sectioning element, so none of these headings label a region — `H` navigation lands on a heading with no programmatic scope. The emoji prefixes on `SH` (L22 `{icon} {title}`) and on every h3/h4 further pollute the heading text that AT announces in a headings list.

**Evidence**

WCAG 2.2 SC 1.3.1 Info and Relationships (Level A): structure conveyed visually must be programmatically determinable. Skipped heading levels are the canonical 1.3.1 structure failure; SC 2.4.6 Headings and Labels (AA) additionally requires headings that describe topic or purpose, which emoji-prefixed headings degrade.

**Recommendation**

Make the content model own the hierarchy rather than the markup: `Briefing → Section → ClaimGroup → Claim` maps deterministically to h1 → h2 → h3, and a card never invents a level. The repo does this — `[section]/page.tsx` renders `<h2 className="briefing__section-title">` then `<section aria-labelledby={`${group.id}-heading`}><h3 id={...}>`, so every heading labels a real region and no level can be skipped by an author. Add an eslint rule or an axe `heading-order` assertion in CI (ADD-03) so a future hand-written page cannot regress it.

### A11Y-08 — Comparison table has no caption, no scope on headers, and sits in a scroll container no keyboard can reach

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.94 |

**What the artifact says**
> L187-210: `<div className="overflow-x-auto"><table className="w-full text-xs"><thead><tr className="text-slate-400 border-b border-slate-600 text-left"><th className="py-2 pr-3">Program</th><th ...>Strengths</th><th ...>Critical Gaps</th><th className="py-2">MindUnlock Advantage</th></tr></thead><tbody className="divide-y divide-slate-700">...`

**The problem**

Three defects in one element. (1) No `<caption>`: the table's purpose is explained only by a preceding `<p className="text-slate-400 text-xs mb-4">` at L186, which is not programmatically associated, so a screen reader user who lands on the table by table navigation gets no title. (2) No `scope="col"` on any `<th>` (L190) and no `scope="row"` / `<th>` for the program name cell at L202 (it is a `<td>`), so cell-to-header association is left to AT heuristics across a 4×6 grid of long prose cells. (3) The `overflow-x-auto` wrapper at L187 has no `tabindex="0"` and no `role="region"`/`aria-label`, so when it does overflow — which it will at `text-xs` with four prose columns on a phone — a keyboard-only user cannot scroll it. Chrome and Firefox have begun making scrollers focusable by default, but that behaviour is not something to rely on for conformance.

**Evidence**

WCAG 2.2 SC 1.3.1 (A) for caption/scope — data-table header association is the archetypal 1.3.1 requirement. SC 2.1.1 Keyboard (A) for the unreachable scroll container. Note SC 1.4.10 Reflow (AA) explicitly excepts content requiring two-dimensional layout, and data tables fall under that exception, so the horizontal scroll itself is *not* a Reflow violation — only the inability to operate it by keyboard is a failure.

**Recommendation**

`<figure role="group" aria-labelledby>` or a real `<caption>`; `scope="col"` on every `<th>` in `<thead>`; promote the first cell of each row to `<th scope="row">`; and wrap in `<div tabindex="0" role="region" aria-labelledby={captionId} class="table-scroll">`. Below ~640px, render the same rows as a definition-list stack instead of a scroller, which removes the problem rather than mitigating it.

### A11Y-09 — Sticky tab bar can fully obscure the focused element — SC 2.4.11, new at AA in WCAG 2.2

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.88 |

**What the artifact says**
> L845 `<div className="sticky top-0 z-20 bg-slate-900 border-b border-slate-700">` containing the tab strip at L846-853, above the content region at L855.

**The problem**

The sticky bar is roughly 48px tall and opaque (`bg-slate-900`, `z-20`). No element in the document sets `scroll-margin-top` or `scroll-padding-top`. When a keyboard user Tabs to a focusable element — the external-source links that a modernised version will contain, or any control added later — and the browser scrolls it into view, the browser's default scroll-into-view can place the focused element exactly under the sticky bar, hiding it entirely. Today the content panels contain no focusable elements at all, which masks the defect; the moment one link is added, it manifests.

**Evidence**

WCAG 2.2 SC 2.4.11 Focus Not Obscured (Minimum), Level AA (new in WCAG 2.2): when a user-interface component receives keyboard focus, it must not be entirely hidden by author-created content. The W3C Understanding document names sticky headers, sticky footers and non-modal dialogs as the typical culprits, and permits partial obscuring (the AAA sibling 2.4.12 forbids any). Confirmed via W3C Understanding SC 2.5.8 / 2.4.11 pages (https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html) through search; w3.org was not directly fetchable from this session.

**Recommendation**

Set `scroll-margin-top: calc(var(--sticky-h) + 0.5rem)` on `:target` and on every focusable element inside the scroll container, publish the bar's height as a CSS custom property, and assert it with a Playwright test that focuses each tabbable element and checks `getBoundingClientRect().top >= stickyHeight`. Also note what *passes*: tab buttons at `px-3 py-1.5 text-xs` compute to ~28px tall (12px text + 16px line-box + 12px padding), which clears SC 2.5.8 Target Size (Minimum)'s 24×24 CSS-pixel floor — I checked rather than assumed.

### A11Y-10 — Decorative emoji are the only icon system and become part of every accessible name

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.85 |

**What the artifact says**
> L850 `{t.e} {t.label}` on each tab button (e.g. `📋 Project Doc`, `🧠 Diagnostics`); L22 `<h2 ...>{icon} {title}</h2>`; L41 `⚠ {p}`; L45 `→ {p}`; L81 `✓ {item}`; L126 `✅ {r.m}`; L238 `✅ {app.pro}` / L239 `❌ {app.gap}`; L786 `□ {m}`; L259 tab labels `🧒 Student (52 Domains)` / `👨‍👩‍👧 Parent (38 Domains)`.

**The problem**

Every emoji is bare text inside the accessible name of its control or heading. A screen reader computes the tab's name as the emoji's CLDR name plus the label — "clipboard Project Doc", "brain Diagnostics" — and the ZWJ sequences are worse: `👨‍👩‍👧` (L55, L259, L331, L535) announces as "family: man, woman, girl" and `👩‍🏫` (L56, L331) as "woman teacher", prefixed to every one of those labels. In a headings list the h2s read as emoji-first strings, which destroys alphabetical scanning. `⚠` at L41 is U+26A0 without a variation selector, so it may render as a monochrome text glyph on some platforms and a coloured emoji on others — inconsistent both visually and in announcement. None of these are marked `aria-hidden="true"`, and none has a text equivalent where it carries meaning (the `✅`/`❌` pair at L238-239 is the closest to load-bearing).

**Evidence**

Emoji are Unicode text, so SC 1.1.1 Non-text Content does not strictly apply; the operative requirements are SC 4.1.2 (the control's accessible name is what AT announces) and SC 2.4.6 Headings and Labels (AA) (labels must describe purpose). [ESTABLISHED that emoji enter the accessible name via standard name computation; INFERENCE on the exact announced strings, which vary by platform, AT and emoji dictionary version — I did not run NVDA/VoiceOver in this session.] Emoji names are from the Unicode CLDR annotation set.

**Recommendation**

Two rules. (1) Decorative glyphs get `aria-hidden="true"` and live in a sibling span, never inside the accessible name. (2) Anything carrying meaning gets a real text equivalent, not an emoji — the repo's `EvidenceBadge.tsx` is the pattern: `<span aria-hidden="true" className="evidence-badge__symbol">{SYMBOL[tier]}</span><span className="evidence-badge__label">{tierLabel(tier)}</span><span className="visually-hidden"> — {tierDescription(tier)}</span>`, so the word is always present, the symbol is redundant, and AT hears what the tier *means*. Replace the decorative set with an icon component drawing from a single inline SVG sprite so stroke weight, optical size and forced-colors behaviour are controllable.

### ENG-11 — Unguarded colour-map lookups `C[x.col].l` throw at eight call sites while `Badge` silently falls back

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.97 |

**What the artifact says**
> L16 (guarded): ``className={`... ${C[color]?.bdg || C.purple.bdg}`}``. L171, L275, L295, L314, L488, L602, L730, L783 (unguarded): e.g. L171 ``<Card key={g.gap} className={`border-l-4 ${C[g.col].l}`}>`` and L602 ``<Card key={a.name} className={`border-t-4 ${C[a.color].t}`}>``.

**The problem**

`C` (L3-13) has exactly nine keys: red, blue, purple, green, orange, yellow, teal, indigo, gold. The colour key is supplied by inline data written by hand in eight different places — `col:"gold"` (L169), `color:"teal"` (L598), `color:"gold"` (L293). A single typo (`"amber"`, `"grey"`, `"Gold"`) makes `C[key]` undefined and `.l` throws a TypeError during render, which in React 18 unmounts the entire tree to a blank screen — there is no error boundary anywhere in the file. Meanwhile `Badge` at L16 handles the same class of error gracefully with `?.` + `||`. Two different defensive postures for the same lookup in the same module is the clearest possible signal that no type system is enforcing the contract: the fallback in `Badge` exists because someone was bitten, and the eight other sites were never revisited.

**Evidence**

Direct reading of the source; `grep -n "C\[[a-z]*\.\(col\|color\)\]\.\(l\|t\)"` returns exactly eight lines (171, 275, 295, 314, 488, 602, 730, 783). JavaScript property access on `undefined` throws TypeError; React 18 unmounts the root on an uncaught render error absent an error boundary — standard documented behaviour.

**Recommendation**

The fix is not `?.` at eight sites, it is making the key unrepresentable: `type Accent = 'red'|'blue'|...` and `const ACCENT: Record<Accent, AccentTokens>`, so `tsc` rejects the typo at author time. Better still, remove the nine-family literal map entirely in favour of semantic tokens (DS-13) so content authors choose `tone: 'risk'`, not `col: 'red'`.

### ENG-12 — No TypeScript in a TypeScript-strict repo, and no module boundary at all

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.97 |

**What the artifact says**
> File extension `.jsx`; no type annotations anywhere; one default export (`export default function App()` L814) and ten unexported local components (L31, L155, L254, L326, L451, L522, L587, L653, L717, L765).

**The problem**

The target repo is TypeScript 5.5.4 with `"strict": true` and `noEmit` type-checking (`/home/user/AEOS/frontend/tsconfig.json`). This file would not merge: it is untyped JSX, and every component's props are implicit `any` (`Badge({children, color})`, `Card({children, className})`, `SH({title, sub, icon})`, `SubTab({tabs, active, setActive})`). Nothing is exported, so nothing is testable or reusable — the ten tab components cannot be unit-tested, Storybook'd, or imported by any other surface. 858 lines in one module also means every change touches the same file, so two people cannot work on Business Model and Diagnostics without conflicting. A further repo mismatch: the artifact is Tailwind-dependent but `/home/user/AEOS/frontend/package.json` has **no Tailwind dependency** — the portal uses plain CSS (`globals.css`, `briefing.css`). Dropping this file into AEOS would render completely unstyled.

**Evidence**

`/home/user/AEOS/frontend/tsconfig.json` (`"strict": true`, `"allowJs": false`, `"jsx": "react-jsx"`) — `allowJs: false` alone rejects this file. `/home/user/AEOS/frontend/package.json` dependencies: next ^16.3.4, react ^18.2.0, @supabase/*; devDependencies: typescript ^5.5.4, eslint ^9.39.5, eslint-config-next. No `tailwindcss`, no `@tailwindcss/*`, no `postcss` config beyond an override.

**Recommendation**

Rebuild as typed modules under `src/lib/briefing/` (model), `src/components/briefing/` (presentation) and `src/content/<module>/` (data), which is exactly the split already present in the repo. Decide Tailwind explicitly: either adopt it repo-wide with a token-mapped config, or stay on the CSS-custom-property system `briefing.css` already uses. Do not let one artifact introduce a styling system by accident.

### ENG-14 — No URL state: no section can be linked, bookmarked, shared or server-rendered, and the back button is inert

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.98 |

**What the artifact says**
> L815 `const [activeTab,setActiveTab]=useState("overview");` — the only source of truth for which of ten sections is visible. Sub-selection likewise: L156 `useState("idea")`, L255 `useState("student")`, L327 `useState("student")`.

**The problem**

This is billed as a "Master Project Document" (L34) and an "AI Executive Team Brief". Its primary use is being sent to other people — a district administrator, a grant reviewer, a prospective co-developer — with a pointer to a specific part. That is impossible: every reader lands on Project Doc and must be told in prose which tab to click. The browser back button does nothing (pressing it leaves the document entirely, losing the reader's place). Nothing is crawlable or server-renderable, so the Tech Stack tab's own claim of `SEO for marketing site` (L685) cannot be satisfied by this architecture. There is also no persistence of any kind: a reader who refreshes returns to tab one.

**Evidence**

Direct reading of L815 and L855; there is no `useSearchParams`, no `history.pushState`, no `location.hash`, no `localStorage` anywhere in the file.

**Recommendation**

One route per section: `/briefings/mindunlock/premise`, `/briefings/mindunlock/safeguards`, etc., with `generateStaticParams()` so all sections are statically generated and individually indexable. Already implemented in the repo: `/home/user/AEOS/frontend/src/app/briefings/mindunlock/[section]/page.tsx` exports `generateStaticParams()` and a per-section `generateMetadata()` returning `${section.title} — ${briefing.title}` and `section.summary` as the description, plus `/home/user/AEOS/frontend/src/app/briefings/mindunlock/page.tsx` which redirects the index to the first section.

### ENG-18 — Every assertion is a string literal: no claim carries an evidence tier, citation or status, so the document cannot be checked

| | |
|---|---|
| **Severity** | `HIGH` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.96 |

**What the artifact says**
> L164 `research:"85% of test anxiety interventions validated only on white, middle-class, neurotypical populations (Zeidner, 1998; von der Embse et al., 2018). No published program uses Ubuntu, Sankofa, or ancestral identity as therapeutic anchors."`; L465 `f:"Culturally affirming instruction raises Black student achievement (ES: 0.8)"`; L466 `f:"Agency in learning design produces 40% greater intrinsic motivation"`; L460 `f:"Self-testing produces 50% greater retention than re-reading"`; L41 `"38% of middle schoolers experience debilitating test anxiety (Zeidner, 1998)"`.

**The problem**

Citations and effect sizes are embedded *inside prose strings*. There is no field on any record that says what tier of evidence backs it, which source supports it, or whether it has been verified — so no tooling can tell a replicated meta-analysis from a number someone typed. The file renders `(ES: 0.8)` (L465), `50% greater retention` (L460), `43%` (L461), `40% greater intrinsic motivation` (L466), `15–20%` (L464), `2× retention` (L459), `60–90% speed increase` (L483), `90% faster study` (L75) and `38%` (L41) in exactly the same visual treatment as every unsupported design intention in the document. A reader — including an MCPS reviewer — has no way to distinguish them, and a future editor has no mechanical barrier against adding another. This is the direct violation of the founder's own "evidence before claims / no claims of validation that has not occurred" rule, embedded in the data structure rather than in anyone's judgement.

**Evidence**

Direct reading of the source: there is no object key anywhere in the file named `tier`, `evidence`, `citation`, `source`, `status` or `verified`. The sole structure is ad-hoc per-section literals (`{gap, col, research, existing, missing, innovation}`, `{t, r, f, a}`, `{domain, count, color, items}`).

**Recommendation**

Make every assertion a typed `Claim` record — `{ id, text, tier, sources[], note?, magnitude? }` — with a validator that fails the build when a tier's evidentiary requirement is unmet. This is implemented in the repo: `/home/user/AEOS/frontend/src/lib/briefing/types.ts` (tiers established → emerging → expert-opinion → inference → hypothesis → retracted, plus `MARKETABLE_TIERS`) and `/home/user/AEOS/frontend/src/lib/briefing/validate.ts`, whose `QUANTITY_PATTERN = /(\d+(?:\.\d+)?\s*(?:%|×|x\b)|\bES[:=]|\bd\s*=|\bg\s*=|\$\s?\d)/i` fires an **error** when a claim's text states a quantity with no `magnitude` record naming metric and population — catching `(ES: 0.8)` and `40% greater intrinsic motivation` exactly. `assertBriefingValid()` is called at module load in `[section]/page.tsx`, so `next build` fails rather than publishing. `npm test` currently passes 14/14. See ADD-01/ADD-02 for extending coverage to the four tabs not yet modelled.

### ENG-13 — The `content` object does NOT render ten trees per render — the real costs are different, and worth naming precisely

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.95 |

**What the artifact says**
> L828-831: `const content={overview:<ProjectOverview/>,gap:<GapAnalysis/>,diagnostic:<DiagnosticAssessments/>,cert:<CertificationFramework/>,course:<CourseArchitecture/>,app:<AppDesign/>,agents:<AIAgentSystem/>,tech:<TechStack/>,business:<BusinessModel/>,roadmap:<Roadmap/>,};` used at L855 `{content[activeTab]}`.

**The problem**

The common reading — that all ten tab trees are *built* on every render — is wrong, and getting it right matters because the wrong diagnosis produces the wrong fix. `<ProjectOverview/>` compiles to `jsx(ProjectOverview, {})`, which allocates a small element descriptor; it does **not** invoke the component function. React only calls the function for the element actually returned from `App`. So the per-render cost is ten tiny object allocations plus one object literal — genuinely negligible. The real costs are three others: (a) **no code splitting** — all ten components are statically imported into one module, so the first paint downloads and parses the Business Model and Roadmap code to show the Project Doc; (b) **sub-tab state is destroyed on every switch** — `GapAnalysis` (L156), `DiagnosticAssessments` (L255) and `CertificationFramework` (L327) each hold `useState`, and switching away unmounts them, so returning to Gap Analysis silently resets the user to "idea" regardless of what they were reading; for a user with working-memory difficulty, that is a real cognitive cost, not a micro-optimisation; (c) the literal is **recreated every render**, which pre-emptively defeats `React.memo` or `useMemo` if either is ever added.

**Evidence**

React 18 element semantics: `React.createElement`/`jsx` returns a descriptor object; component functions are invoked during reconciliation only for elements present in the returned tree. Direct reading of L156/L255/L327 confirms the three stateful children. Direct reading of L1 confirms a single static import (`useState`) and no `lazy`/`dynamic`.

**Recommendation**

Replace the map with routes — `app/briefings/[briefing]/[section]/page.tsx` — which gives per-section code splitting, server rendering, and persistence of position in the URL instead of in volatile state, all three at once. If any in-page switching survives, hoist the sub-selection into the URL as a search param so it survives navigation. Do not reach for `useMemo` on the content map: it would be optimising a cost that does not exist.

### A11Y-15 — No authored focus indicator, and `transition-all` with no reduced-motion handling

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.78 |

**What the artifact says**
> L26 `className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${...}`}` and L849 `className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${...}`}` — no `focus:`, `focus-visible:` or `ring-` utility anywhere in the file.

**The problem**

Two issues. (1) Focus: the file never removes outlines, so the user-agent default ring survives — this is **not** an automatic SC 2.4.7 failure, and I will not claim one. But the default ring was never designed against `bg-slate-900`/`bg-purple-700`, and Chrome's adaptive ring, Firefox's, and Safari's differ markedly; on a `rounded-lg` button with a custom dark fill the result ranges from adequate to nearly invisible depending on browser. For a WCAG-2.2-AA claim that is an untested dependency on browser defaults, not a design decision. (2) Motion: `transition-all` animates every animatable property (including layout-affecting ones) on both tab bars, and there is no `@media (prefers-reduced-motion: reduce)` anywhere. The product promises a "sensory-aware design system" and "focus mode" (L122) and "Reduced Distractions" as an IEP accommodation (L553); ignoring the one motion preference the platform already exposes is the smallest possible version of that promise, unkept.

**Evidence**

SC 2.4.7 Focus Visible (Level AA) requires a visible focus indicator; the UA default can satisfy it, so the failure is conditional, not certain — [INFERENCE], and I would verify with a cross-browser screenshot matrix. SC 2.4.13 Focus Appearance (which sets the 2px-perimeter / 3:1 contrast thresholds) is **Level AAA** in WCAG 2.2, not AA — stating otherwise would overclaim. `prefers-reduced-motion` relates to SC 2.3.3 Animation from Interactions, which is **Level AAA**; the AA argument here is product-contract, not conformance.

**Recommendation**

Author the indicator explicitly: `:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }` scoped to the document root, with `forced-colors` mapping `--accent` to `LinkText`. Replace `transition-all` with named properties (`transition: background-color 120ms, color 120ms`) and wrap in the reduced-motion guard. The repo's `briefing.css` already ships both: `.briefing :focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }` and a `@media (prefers-reduced-motion: reduce)` block neutralising animation, transition and `scroll-behavior`.

### A11Y-16 — Structural borders and surfaces sit at 1.5–2.1:1 — below the 3:1 non-text threshold

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.72 |

**What the artifact says**
> L19 `Card`: `bg-slate-800/80 rounded-xl border border-slate-700`; L59/L79/L102/L124 etc. `bg-slate-700 rounded-xl`; L16 `Badge`: `bg-${c}-900 text-${c}-300 border border-${c}-700`; L189 `border-b border-slate-600`; L192 `divide-y divide-slate-700`; L41/L45 `border-b border-slate-700`.

**The problem**

Computed ratios: card `border-slate-700` against the page `bg-slate-950` = **1.95:1** and against the card's own fill = **1.54:1**; `bg-slate-700` inner tiles against the card fill = **1.54:1**; the table head rule `border-slate-600` on card = **2.10:1**; every `Badge` border against its own `-900` fill = **1.55–1.82:1**. The active tab's `bg-purple-700` against the strip's `bg-slate-900` = **2.56:1**. In practice these lines are the only thing separating one card from the next in a page of near-identical dark rectangles. What *passes*, and should be said: the meaning-carrying accent bars all clear 3:1 — `border-l-red-500` 4.24:1, `blue-500` 4.33:1, `indigo-500` 3.57:1, `teal-500` 6.40:1, `green-500` 7.00:1, `amber-400` 9.55:1. So the decorative hierarchy fails while the semantic accents pass, which is exactly backwards from where the effort should have gone.

**Evidence**

SC 1.4.11 Non-text Contrast (Level AA) requires 3:1 for "visual information required to identify user interface components and states" and for graphical objects required to understand content. Whether a purely decorative card border is in scope is genuinely debatable — a border that merely decorates is exempt — which is why this is [INFERENCE] and medium, not high. The active-tab case is also softened because the state is additionally carried by text colour (white 6.98:1 on purple-700 vs slate-400 6.96:1 on slate-900). Ratios computed in the scratchpad script against stock Tailwind v3 hex values.

**Recommendation**

Define `--line` and `--line-strong` as tokens with a stated minimum against every surface they may appear on, and reserve `--line-strong` (≥3:1) for any boundary that is load-bearing. The repo's `briefing.css` separates these (`--line: #d2d9e4` / `--line-strong: #9aa6b8` light; `#2e3845` / `#5a687a` dark) and hands everything to the UA under `@media (forced-colors: active)`. Add the token-pair contrast test in ADD-04 so the minimum is enforced, not commented.

### ENG-17 — Conflicting Tailwind utilities and card-inside-card alpha stacking make the rendered result non-deterministic from the source

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> L19 `Card` base: `bg-slate-800/80 rounded-xl border border-slate-700 p-5 ${className}`. L468 (inside the Card opened at L455): `<Card key={r.t} className="border-l-4 border-l-indigo-500 p-4">`.

**The problem**

Two compounding defects. (1) L468 emits `class="... p-5 border-l-4 border-l-indigo-500 p-4"`. Tailwind resolves conflicts by stylesheet source order, not by position in the class string, and it emits the padding scale ascending, so `.p-5` comes after `.p-4` and **wins** — the author's `p-4` silently does nothing. The same shadowing pattern is latent wherever a caller passes a utility in the same group as `Card`'s base (`p-*`, `border-*`, `rounded-*`). (2) The same line nests a `Card` inside a `Card`, so `bg-slate-800/80` composites over `bg-slate-800/80`: the outer resolves to rgb(24,34,52), the inner to rgb(29,40,58). Every contrast figure for that block differs from every other card (slate-400 reads 5.78:1 there vs 6.22:1 elsewhere). Alpha-over-alpha surfaces mean the rendered contrast is not statically knowable from the source — which is precisely why a design system must express surfaces as opaque tokens, not translucent literals.

**Evidence**

Tailwind conflict resolution by generated-stylesheet order is documented behaviour (and the reason `tailwind-merge` exists). Composite values computed in the scratchpad script: `blend(slate-800, 0.8, slate-950)` = (24,34,52); `blend(slate-800, 0.8, (24,34,52))` = (29,40,58).

**Recommendation**

Never let a shared component's base utilities be overridden positionally: use `tailwind-merge` (`twMerge`) if staying on Tailwind, or `data-*` variants on the component rather than a free-form `className` escape hatch. Define surfaces as opaque tokens (`--surface`, `--surface-sunken`, `--surface-raised`) so any nesting depth yields a known colour — which is what `briefing.css` already does — and forbid `/opacity` on background colours in the lint rules.

### ENG-19 — No print path for a document whose whole purpose is being printed and taken into meetings

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `INFERENCE` |
| **Lens confidence** | 0.82 |

**What the artifact says**
> L833 `<div className="min-h-screen bg-slate-950 text-white">` — dark background, light text, no `@media print` rule anywhere in the file.

**The problem**

This is a district pitch deck, a grant appendix and an "AI Executive Team Brief" (L34). It will be printed and PDF'd. A full-bleed `bg-slate-950` page with `text-white` body prints as either a blank page (most browsers drop background graphics by default, leaving white text on white paper) or a solid black page that empties a toner cartridge (if the user enables background graphics to get readable text). The sticky tab bar prints on every page; the nine other sections do not print at all, because only the active one exists in the DOM. There is no way to produce a complete printed copy of the document short of printing ten separate times.

**Evidence**

Browsers disable background-graphics printing by default (Chrome, Firefox, Safari print dialogs all expose it as an opt-in). [INFERENCE on the exact rendering outcome per browser; the mechanism is well-established. I did not print the file in this session.]

**Recommendation**

Ship an `@media print` block that flips surface tokens to white/black, hides navigation and skip links, sets `break-inside: avoid` on card-level blocks, and expands link hrefs so printed citations remain checkable. The repo's `briefing.css` already does all four, including `.claim__sources a::after { content: ' (' attr(href) ')'; }`. Add `@page { margin: 18mm; }` and a running section title/revision date, and provide a `/briefings/mindunlock/print` route that server-renders every section into one document so a complete copy is one print job.

### ENG-20 — Spanish availability is asserted while the UI is 100% hard-coded English literals

| | |
|---|---|
| **Severity** | `MEDIUM` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.93 |

**What the artifact says**
> L286 `Format: Conversational audio + written; Spanish available.`; L780 `"Spanish-language version (beta) launched"`; L781 `"Spanish beta: 50 families"`.

**The problem**

Every user-visible string in the file is an inline English literal inside JSX — several hundred of them, interleaved with layout. There is no message catalogue, no `next-intl`/`react-intl`, no locale routing, no `lang` attribute anywhere (grep for `lang=` returns 0), and no pluralisation or date/number formatting layer. Adding Spanish to this architecture means forking the file. Beyond translation, there is no `lang` mechanism for the mixed-language content the document itself calls for: Ubuntu, Sankofa, and the 40+ African cultures of the ancestor library (L534, L599) will carry non-English names which, without `lang` on the containing element, a screen reader will pronounce with English phonemes — the opposite of the cultural affirmation the product is built around.

**Evidence**

Direct reading; `grep -c 'lang='` over the file = 0. WCAG 2.2 SC 3.1.2 Language of Parts (Level AA) requires the human language of each passage that differs from the page language to be programmatically determinable. SC 3.1.1 Language of Page (A) applies to `<html>`, which lives outside this fragment — `/home/user/AEOS/frontend/src/app/layout.tsx` does set `<html lang="en">`, so that one is satisfied at the app level.

**Recommendation**

Either remove the Spanish claim until it exists (consistent with "no claims of validation that has not occurred"), or build for it now: locale segment in the route (`/[locale]/briefings/...`), content modules keyed by locale, and a `lang` field on any `Claim`/`Source` whose text is not in the page language so `ClaimCard` can emit `<span lang="zu">`. The content-as-data model makes this cheap — a translated briefing is another `Briefing` object validated by the same gate — which is a third argument for doing the refactor.

### ENG-21 — Six duplicated card shapes, index-as-key and content-as-key throughout — symptoms, not causes

| | |
|---|---|
| **Severity** | `LOW` |
| **Evidence tier** | `ESTABLISHED` |
| **Lens confidence** | 0.9 |

**What the artifact says**
> Byte-identical markup at L123-129 (Risks & Mitigation: `<Badge color={r.s==="Critical"?"red":"orange"}>{r.s}</Badge>` + title + green mitigation line) and L640-645 (Failure Handling: `<Badge color={f.sev==="Critical"?"red":"orange"}>{f.sev}</Badge>` + title + green handling line). Index keys at L41, L45, L277, L297, L316, L338, L368, L423, L512, L786, L787. Content-as-key at L81 `key={item}`, L145 `key={t}`, L215 `key={p}`, L265 `key={f}`.

**The problem**

The same `Badge + title + ✅ detail` card is written twice, the same `{icon, name, sub, pain, outcome}` tile shape three times, the same `{domain, count, color, items}` card three times (L275, L295, L314), and the same `{s, d}` exam-part block twice (L348, L433). Index keys on static lists are harmless in themselves; content-as-key is the sharper edge — two identical strings in one list (easy in a 52-item domain list) produce duplicate keys and a React warning plus unstable reconciliation. The underlying cause is the same one as ENG-18: because content is not data, there is no record type to key on, so authors key on whatever is at hand.

**Evidence**

Direct reading; `grep -n 'key={i}'` returns 11 lines. React requires keys to be unique among siblings and stable across renders.

**Recommendation**

Once content is typed records, every item carries a stable `id` and keying is solved by construction (`key={claim.id}`, `key={section.slug}`), with the validator rejecting duplicates — `validate.ts` already errors on `Duplicate claim id` and `Duplicate section slug`. Collapse the six duplicated shapes into two generic components, `ClaimCard` and `ClaimGroup`, which already exist at `/home/user/AEOS/frontend/src/components/briefing/`.


---

## What is missing and should be added

### Finish the content migration: four of ten tabs have no typed model yet   `ESTABLISHED`

**Why it matters.** The repo's `MINDUNLOCK_BRIEFING` covers 6 sections / 50 claims / 40 sources (premise, corrections, learning-engine, identity, safeguards, validation). The artifact's Certification (L326-448), Diagnostics (L254-323), Tech Stack (L653-714), Business Model (L717-762) and Roadmap (L765-811) tabs are not represented, which means the most overclaim-prone material — `$391,850` Year-1 revenue (L755), `~$216,850` net (L757), `TAM: 6.4M students with IEPs, 74M K-12 parents, 1.3M paraeducators` (L245), `PhD-Level` on four certifications, `Psychometrically validated` on an instrument that does not exist (L258) — is still outside the gate.

**What to build.** Add sections `credentialing`, `instrumentation`, `commercials` and `delivery` to `src/content/mindunlock/index.ts`. Every financial figure becomes a claim with `tier: 'hypothesis'` and a `magnitude` record whose `population` names it as an unvalidated projection; `Psychometrically validated` (L258) becomes `tier: 'retracted'` with a `note` recording the original wording — the validator already requires that note. Expect the build to fail on first run: that is the gate working. Add a `claimCount` assertion test so sections cannot be added without claims.

**Evidence.** `/home/user/AEOS/frontend/src/content/mindunlock/index.ts` (880 lines, 50 `tier:` records); `grep -n "slug: '"` yields premise, corrections, learning-engine, identity, safeguards, validation. `validate.ts` `QUANTITY_PATTERN` and the `retracted`-requires-`note` rule are already implemented. [ESTABLISHED — read directly from the repo.]

### The generic `evidence-graded briefing` component set vs. MindUnlock-specific content — draw the line explicitly   `ESTABLISHED`

**Why it matters.** AEOS's operating principle is "shared AEOS infrastructure over per-module duplication". Right now the briefing components are generic in substance but MindUnlock-specific in location: `briefing.css` is imported from `app/briefings/mindunlock/[section]/page.tsx`, and the page hard-codes `MINDUNLOCK_BRIEFING`. The second module to need a briefing will copy the directory.

**What to build.** Generic (ships with AEOS, zero MindUnlock knowledge): `src/lib/briefing/{types,validate,registry}.ts`; `src/components/briefing/{BriefingShell,SectionNav,ClaimGroup,ClaimCard,EvidenceBadge,MagnitudeTable,SourceList,TierLegend,PrintView}.tsx`; `src/styles/{tokens.css,briefing.css}`. MindUnlock-specific (content only, no JSX): `src/content/mindunlock/{index,sources}.ts`. Route becomes `app/briefings/[briefing]/[section]/page.tsx` resolving through a registry: `export const BRIEFINGS: Record<string, Briefing> = { mindunlock: MINDUNLOCK_BRIEFING };` with `generateStaticParams()` crossing briefings × sections. Rule to state in the README: a component may not import from `src/content/`.

**Evidence.** Current layout read from disk: `src/components/briefing/{SectionNav,EvidenceBadge,ClaimCard}.tsx`, `src/lib/briefing/{types,validate,validate.test}.ts`, `src/content/mindunlock/{index,sources}.ts`, `src/app/briefings/mindunlock/[section]/{page.tsx,briefing.css}`. The components already take `briefing` as a prop, so the generalisation is a move plus a registry, not a rewrite. [ESTABLISHED.]

### axe-core accessibility tests in CI — the gate that makes the WCAG claim auditable   `INFERENCE`

**Why it matters.** The product asserts `accessibility-native (WCAG 2.1 AA)` (L685). There is currently no automated accessibility check of any kind in the repo: `package.json` has no axe, no Playwright, no Testing Library, and `.github/workflows/` contains only `p0-backend-tests.yml` (Postgres RLS). An unverified AA claim is exactly the class of assertion the evidence rule exists to prevent — and it is about the code, not the pedagogy.

**What to build.** Add `@playwright/test` + `@axe-core/playwright`. New `frontend/e2e/a11y.spec.ts`: for every route from `generateStaticParams()`, run `new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']).analyze()` and assert `violations.length === 0`; run each route three times — default, `colorScheme: 'dark'`, and `forcedColors: 'active'`. Add `.github/workflows/frontend-quality.yml` running `tsc --noEmit`, `eslint`, `npm test`, and the axe suite on PRs to main. Be explicit in the README that axe catches roughly a third of issues and does not substitute for the manual screen-reader pass.

**Evidence.** `/home/user/AEOS/frontend/package.json` dependency list contains no axe/playwright/jest/vitest/storybook (verified by grep). `/home/user/AEOS/.github/workflows/` contains one file, `p0-backend-tests.yml`. The ~30% automated-detection figure is widely cited by Deque and others — [EXPERT-OPINION], not a settled measurement, and I would not put a number in the README without sourcing it.

### Contrast as a unit test over the token table, not a design review   `ESTABLISHED`

**Why it matters.** The artifact's five contrast failures (A11Y-03) all came from hand-picked Tailwind shades with no stated minimum. `briefing.css` now records minima in comments (`/* 7.0:1 on --surface */`), but a comment is not a check — the next person who darkens `--surface-sunken` by two points breaks it silently.

**What to build.** `src/styles/tokens.ts` as the single source of truth for colour values; `src/styles/tokens.css` generated from it (or a test asserting the two agree). `src/styles/contrast.test.ts` ports the WCAG relative-luminance formula and asserts, for each theme in {light, dark, high-contrast}: `--text` ≥ 7:1 on every surface; `--text-muted` ≥ 7:1 on every surface it is permitted on (headroom above the 4.5:1 floor); every tier colour ≥ 4.5:1 on its badge background; `--line-strong` ≥ 3:1 on every surface. The reference implementation is at `/tmp/claude-0/-home-user-AEOS/7b79576e-a60b-565a-8dd7-5dda9b3dad0c/scratchpad/contrast.py` — port it to TypeScript so it runs under the existing `node --test` setup with no new dependency. Add a Stylelint rule banning raw hex outside `tokens.css`.

**Evidence.** WCAG 2.2 SC 1.4.3 (4.5:1 / 3:1) and SC 1.4.11 (3:1) thresholds; relative-luminance formula applied in the scratchpad script, which reproduced known Tailwind pairs correctly. `npm test` already runs `node --test` over `src/**/*.test.ts`, so this test needs no new tooling. [ESTABLISHED.]

### Keyboard-navigation and focus-management tests   `ESTABLISHED`

**Why it matters.** A11Y-01, -02, -05 and -09 are all keyboard defects, and all four are invisible to axe — static analysis cannot tell you that Tab order is 10 buttons deep, that focus went nowhere after activation, or that the sticky bar swallowed the focused element.

**What to build.** `frontend/e2e/keyboard.spec.ts`: (1) first Tab from page load reaches the skip link, and activating it moves focus into `#briefing-main`; (2) tab order through `SectionNav` matches DOM order and contains no positive `tabindex`; (3) after client navigation to another section, `document.activeElement` is inside the new `<main>`, not left on the link; (4) **focus-not-obscured**: for every tabbable element, focus it and assert `rect.top >= stickyHeaderHeight && rect.bottom <= viewportHeight` (SC 2.4.11); (5) **target size**: for every interactive element, assert `rect.width >= 24 && rect.height >= 24`, or that a 24px-diameter circle centred on it overlaps no other target (SC 2.5.8); (6) **reflow**: at a 320×256 viewport, assert `document.scrollingElement.scrollWidth <= clientWidth + 1` (SC 1.4.10), excepting elements explicitly marked `data-two-dimensional` such as data tables.

**Evidence.** SC 2.4.11 Focus Not Obscured (Minimum) AA and SC 2.5.8 Target Size (Minimum) AA — 24×24 CSS pixels with a spacing exception measured as a 24px-diameter circle centred on the target's bounding box, independent of page zoom (W3C Understanding docs, confirmed via search; w3.org itself was not reachable from this session and would need allowing in the session's network settings to quote the normative text verbatim). SC 1.4.10 Reflow AA: 320 CSS px without two-dimensional scrolling, excepting content requiring 2D layout. [ESTABLISHED on thresholds; the test formulations are mine — INFERENCE.]

### The theme triad plus density and focus mode — the three switches the product already promises   `EXPERT-OPINION`

**Why it matters.** The artifact hard-codes nine Tailwind families at dark-mode-only values with no light theme, no user-selectable high contrast, no density control and no focus mode — while L685 claims `dark/high-contrast modes; ADHD-friendly custom tokens`, L122 promises `sensory-aware design system; focus mode`, and L553 ships `Focus mode removes non-essential UI` as an IEP accommodation. `briefing.css` now has light + dark + `forced-colors`, but dark is reachable only via `prefers-color-scheme`: a student on a light OS who needs dark has no way to get it, and there is no author-controlled high-contrast theme at all.

**What to build.** Three orthogonal attributes on `<html>`, each persisted and each defaulting to the system preference: `data-theme="system|light|dark|high-contrast"`, `data-density="comfortable|compact"` (comfortable is the default: 1.0625rem/1.65/68ch; compact only tightens vertical rhythm, never type size), `data-focus-mode="off|on"` (hides the section nav, pager, decorative accents and tier symbols, keeps claim text, tier word and citation, narrows the measure to 56ch, and sets `scroll-padding`). Token definition order: `:root` light → `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]):not([data-theme="high-contrast"]) }` → `:root[data-theme="dark"]` → `:root[data-theme="high-contrast"]` → `@media (forced-colors: active)`. Semantic token set, nine colour families retired: `--surface / --surface-sunken / --surface-raised`, `--line / --line-strong`, `--text / --text-muted / --text-inverse`, `--accent / --accent-contrast`, and severity `--sev-critical / --sev-high / --sev-medium / --sev-low` each paired with a required word and shape so hue is never the sole carrier (SC 1.4.1). Apply the attributes server-side from a cookie to avoid a flash.

**Evidence.** Current `briefing.css` defines `--surface/--surface-sunken/--surface-raised/--line/--line-strong/--text/--text-muted/--accent/--accent-contrast` plus six tier colours, with `@media (prefers-color-scheme: dark)` and `@media (forced-colors: active)` blocks — verified by reading the file. What is absent, also verified by grep: no `data-theme`, no `data-density`, no `focus-mode`, no `prefers-contrast`. [ESTABLISHED on what exists; the switch design is EXPERT-OPINION.]

### Unify tokens across the whole portal, not just the briefing route   `ESTABLISHED`

**Why it matters.** `globals.css` hard-codes a light-only palette (`background: #f7f9fc; color: #14213d;`, `.primary-btn { background: #1d4ed8; color: white; }`) with no dark mode, no forced-colors handling and no tokens, while `briefing.css` has a full token system scoped to `.briefing`. The `/students` and `/assessments` routes — the ones teachers actually use — get none of the accessibility work. A design system that applies to one route is a stylesheet.

**What to build.** Promote the token block out of `.briefing` into `src/styles/tokens.css` on `:root`, imported by `app/layout.tsx`. Rewrite `globals.css` in terms of those tokens. Audit `.primary-btn`/`.secondary-btn`/`.ghost-btn` against SC 1.4.3 and 1.4.11 and add `:focus-visible` rings (currently `button, input, select { font: inherit; }` is the only button styling touched, and `a { text-decoration: none; }` removes link underlines globally, which is itself a 1.4.1 risk wherever links sit in body text). Add the skip link and landmark structure to `layout.tsx` so every route inherits them.

**Evidence.** `/home/user/AEOS/frontend/src/app/globals.css` (181 lines) read directly: literal hex throughout, `a { text-decoration: none; }`, no `@media (prefers-color-scheme)`, no `:focus-visible`. `/home/user/AEOS/frontend/src/app/layout.tsx` is 15 lines with no skip link and no landmarks. [ESTABLISHED.]

### Target file tree   `ESTABLISHED`

**Why it matters.** Concrete enough to execute against this week, and expressed as a delta from what is already on disk so nothing working is thrown away.

**What to build.** ```
frontend/
  src/
    lib/briefing/
      types.ts          EXISTS — add `lang?`, `confidence?`, `reviewedBy?`, `reviewedOn?` to Claim
      validate.ts       EXISTS — add: tier may not exceed weakest cited source; stale-review warning
      registry.ts       NEW    — BRIEFINGS: Record<string, Briefing>
      validate.test.ts  EXISTS (14 tests passing)
      registry.test.ts  NEW    — every registered briefing passes assertBriefingValid
    components/briefing/
      BriefingShell.tsx NEW    — banner/main/contentinfo, skip link, theme+density+focus controls
      SectionNav.tsx    EXISTS — nav + ol + Link + aria-current
      ClaimGroup.tsx    NEW    — extracted from [section]/page.tsx
      ClaimCard.tsx     EXISTS
      EvidenceBadge.tsx EXISTS — word + symbol + visually-hidden description
      MagnitudeTable.tsx NEW   — value/metric/population as a real <table> with scope
      SourceList.tsx    NEW    — extracted from ClaimCard; <cite> + caveat + locator
      TierLegend.tsx    NEW    — what each tier means, linked from every section
      PrintView.tsx     NEW    — all sections, one document
    content/mindunlock/
      index.ts          EXISTS — 6 sections / 50 claims; add 4 more sections
      sources.ts        EXISTS — 40 sources
    styles/
      tokens.ts         NEW    — canonical token values
      tokens.css        NEW    — :root + data-theme + forced-colors
      contrast.test.ts  NEW    — asserts every token pair clears its stated minimum
      briefing.css      MOVED  from app/briefings/mindunlock/[section]/
    app/
      layout.tsx        EXISTS — add skip link, landmarks, tokens.css, theme attrs
      briefings/[briefing]/
        page.tsx                    redirect to first section
        [section]/page.tsx          generateStaticParams over briefings × sections
        print/page.tsx              whole document, one page
  e2e/
    a11y.spec.ts        NEW — axe, 3 colour modes
    keyboard.spec.ts    NEW — tab order, focus after nav, 2.4.11, 2.5.8, 1.4.10
.github/workflows/
  frontend-quality.yml  NEW — tsc --noEmit, eslint, npm test, playwright
```

**Evidence.** Every path marked EXISTS was read from disk in this session; `npm test` → `# pass 14 / # fail 0`. [ESTABLISHED.]

### Key interfaces — the additions to the existing model   `ESTABLISHED`

**Why it matters.** The shipped `Claim`/`Source`/`Section`/`Briefing` types are sound. Four fields are missing that the artifact's own content demands, and one validator rule closes the largest remaining hole.

**What to build.** ```ts
// src/lib/briefing/types.ts — additions
export type Claim = {
  id: string; text: string; tier: EvidenceTier; sources: string[];
  note?: string;
  magnitude?: { value: string; metric: string; population: string };
  /** BCP-47 tag when text is not in the page language — Ubuntu, Sankofa,
   *  the 40+ culture names at artifact L534/L599. Rendered as <span lang>. */
  lang?: string;
  /** Who checked this claim against its sources, and when. A claim whose
   *  review is older than the briefing's `revised` date warns. */
  review?: { by: string; on: string };
};

// src/lib/briefing/registry.ts
export const BRIEFINGS: Record<string, Briefing>;
export function getBriefing(slug: string): Briefing | undefined;
export function allBriefingSectionParams(): Array<{briefing: string; section: string}>;

// src/styles/tokens.ts
export type ThemeName = 'light' | 'dark' | 'high-contrast';
export type SurfaceToken = 'surface' | 'surface-sunken' | 'surface-raised';
export type TextToken = 'text' | 'text-muted' | 'text-inverse';
export const THEMES: Record<ThemeName, Record<SurfaceToken|TextToken|'line'|'line-strong'|'accent'|'accent-contrast', string>>;
/** Minimum each pair must clear; contrast.test.ts asserts it. */
export const CONTRAST_FLOORS: Array<{fg: TextToken|'line-strong'; bg: SurfaceToken; min: number}>;
```
New validator rule — the biggest remaining gap: **a claim's tier may not exceed the weakest tier its cited sources can support.** Today `validate.ts` checks that `established` cites a meta-analysis/systematic-review/practice-guide/statute/regulation/agency-data kind, but nothing stops an `emerging` claim resting solely on a `book`. Add a `kind → maximum supportable tier` table and assert `TIER_RANK[claim.tier] <= min(maxTier(source.kind))`.

**Evidence.** Existing `types.ts` and `validate.ts` read in full; `ESTABLISHED_SOURCE_KINDS` covers only the `established` tier, confirming the gap. `TIER_RANK` and `MARKETABLE_TIERS` already exist and give the comparison its ordering for free. [ESTABLISHED.]

### How the UI must render an unverified claim differently from an established one   `ESTABLISHED`

**Why it matters.** The refactor is worthless if every tier renders identically — the document would carry provenance in its data and hide it from the reader, which is the same overclaim with extra steps. The differentiation has to be visible, non-colour-dependent and impossible to switch off.

**What to build.** Five simultaneous differentiators, none of them hue alone: (1) **the word**, always rendered — 'Established' / 'Emerging' / 'Expert opinion' / 'Our inference' / 'Untested hypothesis' / 'Retracted'; (2) **a shape/symbol** varying per tier (`●●● / ●●○ / ●○○ / ◆ / ? / ✕`), `aria-hidden` and redundant to the word; (3) **border treatment** — solid for established/emerging, dashed for inference, dotted for hypothesis, struck-through text for retracted, so the distinction survives greyscale, forced-colors and print; (4) **a visually-hidden description** so a screen reader hears what the tier means rather than a bare word — `'A design bet we have not tested. Do not repeat this as fact.'`; (5) **citation adjacency** — the source sits under the claim, not in a footnote, with its `caveat` ('what this source does NOT support') inline, and a hypothesis renders the explicit line `'No source. This is our own untested position.'` rather than an empty space a skim-reader reads as endorsement. Additionally: any `magnitude` renders as a table of value / metric / population, so `ES: 0.8` can never appear without 'Hedges' g, immediate post-test' and the population beside it.

**Evidence.** Items 1, 2, 4 and the no-source line are implemented in `/home/user/AEOS/frontend/src/components/briefing/{EvidenceBadge,ClaimCard}.tsx`, read in full. Items 3 and the magnitude table are partially present (`.claim--${claim.tier}` class hook exists in `ClaimCard`; `claim__magnitude` renders as a `<dl>`, which should become a `<table>` with `scope` for a three-column comparison). SC 1.4.1 Use of Color (Level A) is the requirement driving redundancy. [ESTABLISHED on the implementation state and the SC; EXPERT-OPINION on the five-signal design.]

### Manual screen-reader and zoom pass, scheduled and recorded   `EXPERT-OPINION`

**Why it matters.** axe plus the keyboard suite will not catch announcement quality, reading order sense, or whether the tier distinctions actually land for a non-specialist. For a product whose users are neurodivergent middle-schoolers and their parents, an automated-only accessibility record would be the same category of unvalidated claim the evidence rule exists to stop.

**What to build.** A short, repeatable checklist run before each release and recorded in the repo: NVDA + Firefox and VoiceOver + Safari over every section — headings list reads sensibly with no emoji noise; landmark list is complete; every tier badge announces its meaning; tables announce headers. Then 400% browser zoom at 1280px (equivalent to a 320px viewport) with no horizontal page scroll; Windows High Contrast on; `prefers-reduced-motion` on. File results as a dated markdown record under `docs/accessibility/` with the tester named. Mark any claim about conformance in the product copy at the tier its testing actually supports — which until that pass exists is `inference`, not `established`.

**Evidence.** The artifact asserts `accessibility-native (WCAG 2.1 AA)` (L685) with no evidence of any testing; the repo contains no accessibility test of any kind. [ESTABLISHED on both. The checklist content is EXPERT-OPINION.] Note also that the claim cites WCAG **2.1** AA while 2.2 has superseded it — 2.2 adds 2.4.11, 2.5.7, 2.5.8, 3.2.6, 3.3.7 and 3.3.8 at A/AA, and a 2024-era product targeting 2.1 is targeting a retired bar.

### Storybook plus visual-regression on the token matrix   `EXPERT-OPINION`

**Why it matters.** The design system's whole value is that `theme × density × focus-mode × tier × tone` renders correctly in every combination. That is 4 × 2 × 2 × 6 states for the badge alone; nobody checks that by hand twice.

**What to build.** Storybook 8 with `@storybook/addon-a11y` (runs axe per story) over the generic briefing components only — never over MindUnlock content. One story per component per theme; a matrix story rendering all six tiers in all four themes; Chromatic or Playwright `toHaveScreenshot()` for the matrix, wired into the same `frontend-quality.yml`. This is also where a reviewer can see, side by side, that an `established` claim and a `hypothesis` are visibly different in greyscale — the thing that most needs checking and is most easily eroded.

**Evidence.** `package.json` has no Storybook or visual-regression tooling (verified by grep). [ESTABLISHED on absence; EXPERT-OPINION that the matrix is the right coverage shape.]


---

## Open questions

- w3.org is not in this session's allowed network domains (`getaddrinfo ENOTFOUND www.w3.org` on both WCAG 2.2 and the ARIA APG Tabs pattern). SC numbers, levels and thresholds in this audit were confirmed through search-result summaries of the W3C pages rather than the primary normative HTML. Before any of this is quoted to MCPS or in a grant application, re-verify the exact normative wording of SC 1.4.3, 1.4.10, 1.4.11, 2.4.11, 2.5.8 and 4.1.2 against https://www.w3.org/TR/WCAG22/ with that host allowed.
- The artifact ships no `tailwind.config`. All 50+ contrast ratios assume the stock Tailwind v3 palette (slate-500 #64748b, slate-700 #334155, slate-800 #1e293b, slate-950 #020617, red-400 #f87171, etc.). If the host app overrides any of these, every number shifts — the method in /tmp/claude-0/-home-user-AEOS/7b79576e-a60b-565a-8dd7-5dda9b3dad0c/scratchpad/contrast.py holds, the inputs must be re-sourced. Also unresolved: does AEOS adopt Tailwind at all? `frontend/package.json` has no Tailwind dependency and the portal uses plain CSS, so dropping this artifact into the repo today renders it completely unstyled.
- I did not run a screen reader, a browser, or any zoom/forced-colors test in this session. Findings A11Y-01/02/03/04/07/08 are determinable from source and are reported as such; the announced-string details in A11Y-10 and the focus-ring quality in A11Y-15 are inferences that need a real NVDA+Firefox / VoiceOver+Safari pass and a cross-browser focus screenshot matrix before anyone states them as fact.
- Who owns the evidence tier of a claim, and what happens when a tier is disputed? The validator enforces that a tier is *recorded* and internally consistent; it cannot judge whether a cited paper actually supports the sentence. That requires a named reviewer and a date — hence the proposed `Claim.review` field. Without a person attached, 'established' means 'someone typed established'.
- Is the briefing a public artifact or a tenant-scoped one? It currently statically generates at build time with no auth. AEOS has a hardened multi-tenant model with row-level security; a document containing MCPS pilot details, financial projections and named partner universities may not belong on an unauthenticated static route. That decision changes the routing design (static vs. server-rendered with session) and should be settled before the route structure is generalised.
- Does the 'focus mode' promised at artifact L122 and L553 mean this briefing's reading mode, or the student app's sensory-reduction accommodation? They are different products with different requirements. If the latter, nothing in this briefing refactor delivers it, and the claim should be tiered as `hypothesis` until the student app exists.
- Target-size (SC 2.5.8) and reflow (SC 1.4.10) currently pass in the artifact — tab buttons compute to ~28px tall and the body grids collapse at `md:`. Both are accidents of the current markup, not properties anyone chose. The proposed tests (ADD-05) would make them guarantees; without them, the first design iteration can silently lose both.

