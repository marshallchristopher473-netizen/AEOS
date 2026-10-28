/**
 * Evidence-graded briefing model.
 *
 * AEOS operating rule: "Evidence Before Claims — never imply validation that has not occurred."
 *
 * This module makes that rule structural rather than aspirational. Every assertion that
 * appears in a briefing is a `Claim` record carrying an explicit evidence tier and a
 * provenance record. `validateBriefing` (see ./validate) refuses a briefing whose claims
 * are not backed at the level their tier asserts, and the build fails rather than shipping
 * a document that overclaims.
 */

/**
 * How much weight a claim is entitled to.
 *
 * The ordering is deliberate: `TIER_RANK` below depends on it, and marketing copy may
 * never assert a tier higher than the claim it rests on.
 */
export type EvidenceTier =
  /** Replicated meta-analytic or systematic-review evidence, or the text of a law. */
  | 'established'
  /** Real empirical support that is thin, contested, or not yet replicated. */
  | 'emerging'
  /** A credible authority's position that is not empirically settled. */
  | 'expert-opinion'
  /** Our own reasoning from the tiers above. Defensible, but ours. */
  | 'inference'
  /** A design bet we have not tested. Must be labelled as such everywhere it appears. */
  | 'hypothesis'
  /** A claim previously made that the evidence does not support. Kept visible on purpose. */
  | 'retracted';

export const TIER_RANK: Record<EvidenceTier, number> = {
  established: 5,
  emerging: 4,
  'expert-opinion': 3,
  inference: 2,
  hypothesis: 1,
  retracted: 0,
};

/** Tiers that may be repeated in anything a customer sees without a qualifier. */
export const MARKETABLE_TIERS: ReadonlySet<EvidenceTier> = new Set<EvidenceTier>([
  'established',
  'emerging',
]);

export type SourceKind =
  | 'meta-analysis'
  | 'systematic-review'
  | 'primary-study'
  | 'practice-guide'
  | 'statute'
  | 'regulation'
  | 'agency-data'
  | 'book'
  | 'internal-pilot';

export type Source = {
  /** Stable key so several claims can cite one source without repeating it. */
  id: string;
  kind: SourceKind;
  /** "Dunlosky, Rawson, Marsh, Nathan & Willingham" — not "Dunlosky et al." */
  authors: string;
  year: number;
  title: string;
  /** Journal, publisher, agency, or the citation of a statute. */
  venue?: string;
  /** DOI preferred; a stable public URL otherwise. */
  locator?: string;
  /**
   * What this source does NOT support. Recording the limit next to the citation is the
   * cheapest guard against a claim drifting past its evidence over successive edits.
   */
  caveat?: string;
};

export type Claim = {
  id: string;
  /** The assertion itself, written so it can be quoted verbatim without a surrounding sentence. */
  text: string;
  tier: EvidenceTier;
  /** Source ids. Required for every tier except `hypothesis`. */
  sources: string[];
  /**
   * For `retracted`: what we used to say, so the correction stays legible.
   * For every other tier: optional context on why this wording and not a stronger one.
   */
  note?: string;
  /** Effect sizes, percentages and currency only belong here, never inline in `text`. */
  magnitude?: {
    value: string;
    /** The exact metric, e.g. "Hedges' g, immediate post-test" — not "improvement". */
    metric: string;
    /** Population and setting the number came from. Numbers travel badly without it. */
    population: string;
  };
};

export type ClaimGroup = {
  id: string;
  heading: string;
  /** Plain-language framing. Must not itself make a gradeable assertion. */
  intro?: string;
  claims: Claim[];
};

export type SectionTone = 'neutral' | 'risk' | 'correction' | 'opportunity';

export type Section = {
  /** URL segment. Lowercase, hyphenated, stable — these get linked and cited. */
  slug: string;
  title: string;
  /** One sentence, shown under the title and in the section index. */
  summary: string;
  tone: SectionTone;
  groups: ClaimGroup[];
};

export type Briefing = {
  slug: string;
  title: string;
  subtitle: string;
  /** ISO date. Readers need to know how stale this is. */
  revised: string;
  /** What this document is for and what it deliberately does not do. */
  scope: string;
  sources: Source[];
  sections: Section[];
};

export function tierLabel(tier: EvidenceTier): string {
  switch (tier) {
    case 'established':
      return 'Established';
    case 'emerging':
      return 'Emerging';
    case 'expert-opinion':
      return 'Expert opinion';
    case 'inference':
      return 'Our inference';
    case 'hypothesis':
      return 'Untested hypothesis';
    case 'retracted':
      return 'Retracted';
  }
}

/**
 * Tier descriptions are rendered as the accessible name of the tier badge, so a screen
 * reader user hears what the badge means rather than a bare word.
 */
export function tierDescription(tier: EvidenceTier): string {
  switch (tier) {
    case 'established':
      return 'Replicated meta-analytic evidence or the text of a law.';
    case 'emerging':
      return 'Real empirical support, but thin, contested, or not yet replicated.';
    case 'expert-opinion':
      return 'A credible authority holds this; it is not empirically settled.';
    case 'inference':
      return 'Our own reasoning from the evidence above, not a finding.';
    case 'hypothesis':
      return 'A design bet we have not tested. Do not repeat this as fact.';
    case 'retracted':
      return 'We said this and the evidence does not support it. Kept visible as a correction.';
  }
}

export function findSection(briefing: Briefing, slug: string): Section | undefined {
  return briefing.sections.find((section) => section.slug === slug);
}

export function sourcesFor(briefing: Briefing, claim: Claim): Source[] {
  return claim.sources
    .map((id) => briefing.sources.find((source) => source.id === id))
    .filter((source): source is Source => source !== undefined);
}

/** Every claim in the briefing, flattened, with the section and group it came from. */
export function allClaims(
  briefing: Briefing,
): Array<{ claim: Claim; section: Section; group: ClaimGroup }> {
  return briefing.sections.flatMap((section) =>
    section.groups.flatMap((group) => group.claims.map((claim) => ({ claim, section, group }))),
  );
}
