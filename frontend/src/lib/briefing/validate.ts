/**
 * Integrity checks for evidence-graded briefings.
 *
 * These run in a test (see validate.test.ts) so a briefing that overclaims fails the build
 * instead of reaching a reader. The checks are deliberately mechanical: they cannot judge
 * whether a citation genuinely supports a claim, only whether the author did the work of
 * recording one. That is still the difference between a document that can be audited and
 * one that cannot.
 */

import {
  type Briefing,
  type Claim,
  type EvidenceTier,
  MARKETABLE_TIERS,
  allClaims,
} from './types';

export type ValidationIssue = {
  severity: 'error' | 'warning';
  claimId: string;
  sectionSlug: string;
  message: string;
};

/** Tiers that must name at least one source. A hypothesis is ours and cites nobody. */
const TIERS_REQUIRING_SOURCES: ReadonlySet<EvidenceTier> = new Set<EvidenceTier>([
  'established',
  'emerging',
  'expert-opinion',
  'inference',
  'retracted',
]);

/**
 * Source kinds that can carry an `established` claim. An `established` tier asserts
 * replicated or statutory backing, so a single primary study or a trade book cannot
 * support it on its own.
 */
const ESTABLISHED_SOURCE_KINDS = new Set([
  'meta-analysis',
  'systematic-review',
  'practice-guide',
  'statute',
  'regulation',
  'agency-data',
]);

/**
 * Numerals that imply a measured quantity. A claim whose text contains one of these but
 * carries no `magnitude` record is asserting precision it has not documented — which is
 * exactly how "raises achievement (ES: 0.8)" gets into a document with no study behind it.
 */
const QUANTITY_PATTERN = /(\d+(?:\.\d+)?\s*(?:%|×|x\b)|\bES[:=]|\bd\s*=|\bg\s*=|\$\s?\d)/i;

/** Words that assert proven benefit. Only a marketable tier may use them unqualified. */
const EFFICACY_PATTERN =
  /\b(proven|guarantees?|guaranteed|clinically validated|evidence[- ]based results|cures?|eliminates?)\b/i;

/**
 * Negations that flip an efficacy word into a disclaimer — "a guarantee that cannot be met"
 * is the opposite of a marketing claim.
 *
 * This is a heuristic, and a blunt one: it looks in a window around the match rather than
 * parsing the sentence. It will occasionally miss a negation phrased unusually, in which
 * case the check fires and the author has to either raise the tier or reword. Erring toward
 * the false positive is the correct direction for a check whose job is to stop overclaiming.
 */
const NEGATION_PATTERN = /\b(no|not|never|cannot|can't|without|nor|neither|un(?:proven|able))\b/i;
const NEGATION_WINDOW = 48;

function assertsEfficacy(text: string): boolean {
  const match = EFFICACY_PATTERN.exec(text);
  if (!match) return false;

  const start = Math.max(0, match.index - NEGATION_WINDOW);
  const end = Math.min(text.length, match.index + match[0].length + NEGATION_WINDOW);
  return !NEGATION_PATTERN.test(text.slice(start, end));
}

export function validateBriefing(briefing: Briefing): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const sourceIds = new Set(briefing.sources.map((source) => source.id));
  const seenClaimIds = new Set<string>();
  const seenSectionSlugs = new Set<string>();

  for (const section of briefing.sections) {
    if (seenSectionSlugs.has(section.slug)) {
      issues.push({
        severity: 'error',
        claimId: '—',
        sectionSlug: section.slug,
        message: `Duplicate section slug "${section.slug}". Slugs are URLs and must be unique.`,
      });
    }
    seenSectionSlugs.add(section.slug);
  }

  for (const { claim, section } of allClaims(briefing)) {
    const at = (severity: ValidationIssue['severity'], message: string) =>
      issues.push({ severity, claimId: claim.id, sectionSlug: section.slug, message });

    if (seenClaimIds.has(claim.id)) {
      at('error', `Duplicate claim id "${claim.id}".`);
    }
    seenClaimIds.add(claim.id);

    if (TIERS_REQUIRING_SOURCES.has(claim.tier) && claim.sources.length === 0) {
      at('error', `Tier "${claim.tier}" requires at least one source; none given.`);
    }

    if (claim.tier === 'hypothesis' && claim.sources.length > 0) {
      at(
        'warning',
        'A hypothesis cites sources. If the sources support it, raise the tier; if they only ' +
          'inspired it, say so in `note` instead of citing them.',
      );
    }

    for (const sourceId of claim.sources) {
      if (!sourceIds.has(sourceId)) {
        at('error', `Cites unknown source "${sourceId}".`);
      }
    }

    if (claim.tier === 'established') {
      const kinds = claim.sources
        .map((id) => briefing.sources.find((source) => source.id === id)?.kind)
        .filter((kind): kind is NonNullable<typeof kind> => kind !== undefined);
      if (kinds.length > 0 && !kinds.some((kind) => ESTABLISHED_SOURCE_KINDS.has(kind))) {
        at(
          'error',
          'Tier "established" needs a meta-analysis, systematic review, practice guide, or ' +
            `legal/agency source. Cited kinds: ${kinds.join(', ')}.`,
        );
      }
    }

    if (QUANTITY_PATTERN.test(claim.text) && !claim.magnitude) {
      at(
        'error',
        'Claim text states a quantity but carries no `magnitude` record naming the metric and ' +
          'population. Move the number into `magnitude`.',
      );
    }

    if (claim.magnitude && claim.tier === 'hypothesis') {
      at('error', 'A hypothesis cannot carry a magnitude — there is no measurement behind it.');
    }

    if (assertsEfficacy(claim.text) && !MARKETABLE_TIERS.has(claim.tier)) {
      at(
        'error',
        `Claim asserts proven benefit at tier "${claim.tier}". Only established or emerging ` +
          'claims may use that language.',
      );
    }

    if (claim.tier === 'retracted' && !claim.note) {
      at('error', 'A retracted claim must record what was previously asserted in `note`.');
    }
  }

  for (const source of briefing.sources) {
    const cited = allClaims(briefing).some(({ claim }) => claim.sources.includes(source.id));
    if (!cited) {
      issues.push({
        severity: 'warning',
        claimId: '—',
        sectionSlug: '—',
        message: `Source "${source.id}" is defined but never cited.`,
      });
    }
  }

  return issues;
}

/**
 * The check a release gate calls. Warnings are surfaced but do not block; errors do.
 */
export function assertBriefingValid(briefing: Briefing): void {
  const issues = validateBriefing(briefing);
  const errors = issues.filter((issue) => issue.severity === 'error');
  if (errors.length > 0) {
    const detail = errors
      .map((issue) => `  [${issue.sectionSlug}/${issue.claimId}] ${issue.message}`)
      .join('\n');
    throw new Error(`Briefing "${briefing.slug}" has ${errors.length} integrity error(s):\n${detail}`);
  }
}

/**
 * Claims a marketing or sales surface is allowed to repeat without a qualifier.
 * Everything else needs the tier shown alongside it.
 */
export function marketableClaims(briefing: Briefing): Claim[] {
  return allClaims(briefing)
    .map(({ claim }) => claim)
    .filter((claim) => MARKETABLE_TIERS.has(claim.tier));
}
