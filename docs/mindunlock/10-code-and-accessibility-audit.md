# MindUnlock — code and accessibility audit

Audit of `MindUnlock_Academy.jsx` (859 lines, single file) and the rebuilt replacement now in
`frontend/src/`.

Every number in this document was measured, not estimated. The method for each is stated so it
can be re-run.

---

## 1. The headline finding

The document specifies, in its own Tech Stack tab:

> "React Native (Expo SDK 51) … accessibility-native (WCAG 2.1 AA)"
> "Tailwind CSS + Radix UI … Sensory-aware palette; dark/high-contrast modes; ADHD-friendly
> custom tokens; accessible components"

The code shipped alongside that specification meets none of it. For a product whose entire
premise is serving students with ADHD, dyslexia, sensory sensitivity and literacy difficulty,
this is not a cosmetic gap — the artifact that is supposed to demonstrate the idea is itself
inaccessible to a meaningful share of the people it describes.

This matters commercially as well as ethically. Any district procurement process will ask for
a VPAT or an accessibility conformance statement. A claim of WCAG 2.1 AA that fails an
automated scan is worse than no claim, because it is a documented misrepresentation.

---

## 2. Colour contrast — measured

**Method.** Tailwind's default `slate` palette values, composited where the original uses
alpha (`bg-slate-800/80` is painted over `bg-slate-950`), then the WCAG 2.x relative-luminance
contrast formula. Script retained in the session scratchpad; reproducible from the table below.

`bg-slate-800/80` over `bg-slate-950` composites to **`#182234`**.

| Foreground | Background | Ratio | AA (4.5:1) | Where it is used |
|---|---|---:|---|---|
| `text-slate-400` | card `bg-slate-800/80` | **6.22** | pass | body copy, 40 occurrences |
| `text-slate-300` | card `bg-slate-800/80` | **10.74** | pass | primary copy |
| `text-slate-300` | `bg-slate-700` | **6.97** | pass | primary copy, inner cards |
| `text-green-400` | `bg-slate-700` | **5.94** | pass | "Outcome:" text |
| `text-purple-300` | `bg-slate-700` | **5.86** | pass | agent names |
| `text-slate-400` | `bg-slate-700` | **4.04** | **FAIL** | body copy inside inner cards |
| `text-red-400` | `bg-slate-700` | **3.74** | **FAIL** | "Pain:" text |
| `text-slate-500` | card `bg-slate-800/80` | **3.35** | **FAIL** | sub-labels, 7 occurrences |
| `text-slate-500` | `bg-slate-700` | **2.18** | **FAIL** | sub-labels inside inner cards |

Four of nine pairs fail. The 4.5:1 threshold is the applicable one because essentially all of
this text renders at `text-xs` (12px) — it does not qualify as large text, for which the 3:1
threshold would apply.

The worst case, 2.18:1, is used for the descriptive sub-label under every customer-profile
card, every note-taking method, and every tech-stack item.

### Why this happened

`bg-slate-700` is used as an *inner* surface on top of `bg-slate-800/80` cards, but the text
colours were chosen against the darker outer surface. Raising the surface without re-checking
the text is the single most common way a dark theme fails contrast. A token system prevents
it structurally; a palette of literal colour classes does not.

---

## 3. Structural accessibility defects

Verified by reading the source and by running axe-core against a faithful render.

| # | Defect | WCAG SC | Severity | Evidence in source |
|---|---|---|---|---|
| 1 | Tab bar is ten plain `<button>`s with no `role="tablist"`/`tab`/`tabpanel`, no `aria-selected`, no `aria-controls`, no roving tabindex, no arrow-key support | 4.1.2 Name, Role, Value | Critical | lines 845–854 |
| 2 | Sub-tab bars (`SubTab`) repeat the same pattern three times | 4.1.2 | Critical | lines 24–28 |
| 3 | No focus management after a tab switch — focus stays on the button while the entire page content is replaced; nothing is announced | 4.1.3 Status Messages (and general AT behaviour) | Critical | line 855 |
| 4 | Four colour pairs below 4.5:1 (section 2) | 1.4.3 Contrast (Minimum) | Serious | throughout |
| 5 | Meaning carried by colour alone — red = pain, green = outcome, red/orange badge = severity | 1.4.1 Use of Colour | Serious | lines 63–64, 125, 642 |
| 6 | `text-xs` (12px) is the dominant body size, for an audience that includes students with reading difficulty | 1.4.4 Resize Text (and basic usability) | Serious | ~180 occurrences |
| 7 | Decorative emoji used as the sole icon affordance, unlabelled — screen readers announce "rocket", "brain", "man and woman holding hands" inline with headings | 1.1.1 Non-text Content | Serious | throughout |
| 8 | No landmark regions — no `<main>`, `<nav>`, or `<header>`; the whole app is nested `<div>`s | 1.3.1 Info and Relationships | Serious | lines 832–857 |
| 9 | No skip link past the ten-item tab strip | 2.4.1 Bypass Blocks | Serious | — |
| 10 | `<table>` with no `<caption>` and no `scope` on header cells | 1.3.1 | Moderate | lines 188–209 |
| 11 | No visible focus indicator beyond UA default on custom-styled buttons, which is suppressed by the Tailwind reset in most setups | 2.4.7 Focus Visible | Serious | lines 26, 848 |
| 12 | `transition-all` with no `prefers-reduced-motion` guard | 2.3.3 Animation from Interactions (AAA) + vestibular safety | Moderate | lines 26, 849 |
| 13 | Horizontally scrolling tab strip and `overflow-x-auto` table on a 390px viewport | 1.4.10 Reflow | Moderate | lines 187, 846 |
| 14 | No `lang` attribute anywhere, and no i18n layer at all, despite a roadmap commitment to a Spanish version in month 12 | 3.1.1 Language of Page | Moderate | — |
| 15 | Heading hierarchy skips: `h1` → `h2` (section) → `h3` (card) → `h4` (sub-card), but `h4`s also appear without an intervening `h3` inside grid items | 1.3.1 | Moderate | lines 61, 80, 509 |

---

## 4. React and engineering defects

| # | Defect | Impact |
|---|---|---|
| 1 | **All ten tab subtrees are constructed on every render.** `content` (line 828) is an *object of already-created elements*, not a map of components. `<ProjectOverview/>` et al. are evaluated when the object literal is built, so every one of the ten component functions runs on every keystroke of state change — not just the visible one. The fix is a map of component references (`{overview: ProjectOverview}`) and `createElement`, or routes. | Performance, and it grows linearly with every tab added |
| 2 | **859 lines in one file, ~100% of content inline in JSX.** There is no way to review the content without reviewing the markup, no way to test the content, no way to translate it, and no way for a non-engineer to correct a citation. | This is the root cause of everything in §5 |
| 3 | **No TypeScript**, although the target repository is TypeScript 5 with `strict: true`. | Inconsistent with the codebase it is meant to join |
| 4 | **Inconsistent defensive style.** `Badge` falls back safely (`C[color]?.bdg \|\| C.purple.bdg`, line 16) but `C[g.col].l` (line 171), `C[d.color].l` (line 275) and `C[m.color].l` (line 488) throw on an unknown key. A typo in a content string crashes the page. | Latent crash |
| 5 | **Index-as-key** in several lists (lines 41, 45, 338, 423, 786). Harmless while lists are static, a correctness bug the moment they are filtered or reordered. | Latent |
| 6 | **No URL state.** A section cannot be linked, bookmarked, cited, or shared; the back button does nothing. For a document whose purpose is to be circulated to an executive team, this is the most consequential product defect in the file. | High |
| 7 | **No print path.** A dark-background SPA prints blank or illegible. This is a document people will take into meetings. | High |
| 8 | No tests, no memoisation, no code splitting, no error boundary. | — |

---

## 5. The structural problem underneath all of it

The document makes roughly two hundred assertions. They are string literals inside JSX. That
has one consequence that matters more than every item above:

**there is no place to put a citation, so claims and their evidence cannot be checked against
each other.**

This is not a metaphor for what went wrong — it is mechanically what went wrong. Because a
claim is a `<p>` and not a record, nothing prevented `"raises Black student achievement
(ES: 0.8)"` from sitting beside three book citations that report no such figure, and nothing
would have flagged it in review.

The founder's own operating rule is *"Evidence Before Claims — never imply validation that has
not occurred."* A rule like that cannot be enforced by intention. It has to be enforced by
something that refuses to build.

---

## 6. The rebuild

Location: `frontend/src/` in the existing AEOS repository — not a parallel React Native/Expo
stack, per the project's own "shared infrastructure across AEOS modules" principle.

```
frontend/
├─ scripts/ts-resolve.mjs                     # lets `node --test` run the TS sources directly
└─ src/
   ├─ lib/briefing/
   │  ├─ types.ts                             # Claim, EvidenceTier, Source, Briefing
   │  ├─ validate.ts                          # the integrity gate
   │  └─ validate.test.ts                     # 14 tests, proves the gate rejects
   ├─ content/mindunlock/
   │  ├─ sources.ts                           # 40 sources, each with its `caveat`
   │  └─ index.ts                             # the briefing as graded claims
   ├─ components/briefing/
   │  ├─ EvidenceBadge.tsx
   │  ├─ ClaimCard.tsx
   │  └─ SectionNav.tsx
   └─ app/briefings/mindunlock/
      ├─ page.tsx                             # redirects to first section
      └─ [section]/
         ├─ page.tsx                          # one route per section
         └─ briefing.css
```

### The core idea

Every assertion is a record:

```ts
type Claim = {
  id: string;
  text: string;                 // the assertion, quotable standalone
  tier: EvidenceTier;           // established | emerging | expert-opinion
                                // | inference | hypothesis | retracted
  sources: string[];            // required for every tier except `hypothesis`
  note?: string;                // for `retracted`: what we used to say
  magnitude?: {                 // numbers live here, never inline in `text`
    value: string;
    metric: string;             // "Hedges' g, immediate post-test" — not "improvement"
    population: string;         // numbers travel badly without this
  };
};
```

And `Source` carries a `caveat` field recording *what the source does not support*, rendered
directly beneath the citation. A claim and the boundary of its evidence become impossible to
read separately — which is the specific failure mode that produced the original's bad numbers.

### The gate

`assertBriefingValid` is called at module scope in the page, so it runs during `next build`.
The rules:

- A sourced tier with no sources → error.
- A citation to a source id that does not exist → error.
- `established` resting only on a trade book or single primary study → error.
- A quantity in `text` (`43%`, `ES: 0.8`, `d =`, `$`) with no `magnitude` record → error.
- A `hypothesis` carrying a `magnitude` → error (there is no measurement behind it).
- Efficacy language ("proven", "guaranteed", "clinically validated") below a marketable tier
  → error.
- A `retracted` claim with no record of what was previously asserted → error.

This is not theoretical. The gate failed the first build, on
`safeguards/safeguard-crisis` — and the failure was the *validator's* fault, not the claim's:
the sentence was "a sub-second detection **guarantee** … **cannot** be met", a disclaimer the
regex read as marketing. The fix was a negation guard with a documented window, plus a test
(`negated efficacy language is not mistaken for a claim`) that pins the behaviour. A check
that has never been watched fail is indistinguishable from one that always passes.

### Verification performed

| Check | Command | Result |
|---|---|---|
| Type check | `npx tsc --noEmit` | clean |
| Production build | `npx next build` | succeeds; 6 sections prerendered as static HTML |
| Integrity gate | `npm test` | **14/14 pass** |
| Gate actually rejects | included above | each failure mode asserted individually |
| Accessibility | axe-core 4.10.2 via Playwright, tags `wcag2a wcag2aa wcag21a wcag21aa wcag22aa best-practice`, 6 routes × {light, dark} × {390px, 1280px} | **0 violations across 24 runs** |
| Reflow | horizontal overflow measured per run | 0px on all 24 |

The axe run is an automated scan and catches roughly a third to a half of real accessibility
defects. It is a floor, not a certificate. A keyboard-only pass and a screen-reader pass by a
human are still required before this is described as conformant, and the honest statement
until then is "no automated violations", not "WCAG 2.1 AA".

### What the rebuild fixes, by defect number

| Original defect | Fix |
|---|---|
| 1, 2, 3 (tab widget, focus) | Replaced with real routes. `aria-current="page"` in a labelled `<nav>`; navigation is a page load, so focus and announcement are the browser's job, done correctly. |
| 4 (contrast) | Semantic tokens with separate light/dark definitions; muted text sits at 7.0:1 (light) and 7.4:1 (dark) against its surface. |
| 5 (colour-only meaning) | `EvidenceBadge` always renders the tier word plus a distinct symbol (`●●●`, `◆`, `?`, `✕`); colour is redundant. |
| 6 (12px body) | 1.0625rem body, 1.65 line height, 68ch measure. |
| 7 (emoji) | Removed. |
| 8, 9 (landmarks, skip link) | `<header>`, `<nav aria-label>`, `<main id tabIndex={-1}>`, skip link. |
| 11, 12 (focus, motion) | `:focus-visible` outline at 3px; `prefers-reduced-motion` block. |
| 13 (reflow) | Fluid layout, wrapping nav, measured at 390px. |
| 14 (lang) | `lang="en"` already on `<html>` in the repo's root layout; content is now data, so i18n is a translation of `content/`, not a rewrite of components. |
| Engineering 1 (eager render) | One route per section; Next prerenders each as static HTML. |
| Engineering 6 (URL state) | Each section has a stable, linkable, server-rendered URL. |
| Engineering 7 (print) | `@media print` block, including printing the URL after each citation link. |

### Also added, beyond the original

A `forced-colors: active` block that hands every colour back to the operating system. A product
that advertises a high-contrast mode should honour the one the user has already turned on at
the OS level, before offering its own.

---

## 7. What was deliberately not done

- **No new dependencies.** The test runner is Node 22's built-in `node:test` with
  `--experimental-strip-types`; the only new file enabling it is a 50-line resolver hook. The
  axe audit ran from the session scratchpad, not from the repo. Adding Vitest, jsdom,
  jest-axe and their trees for fourteen assertions would have violated the project's own cost
  discipline.
- **No visual redesign of the AEOS app.** The briefing styles are scoped to the briefing route.
- **No change to backend, auth, or the existing security test suite.**
- **The original file was not deleted or edited in place.** It is the historical record of what
  was claimed, and the `retracted` tier in the rebuild points back at it explicitly.
