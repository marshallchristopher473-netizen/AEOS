import { type EvidenceTier, tierDescription, tierLabel } from '@/lib/briefing/types';

/**
 * The tier badge.
 *
 * Two rules it exists to enforce:
 *
 * 1. Tier is never carried by colour alone. The original document used coloured borders and
 *    red/green text as the only signal of severity, which is invisible to a reader who
 *    cannot distinguish them (WCAG 1.4.1). Here the word is always present, and the shape
 *    and symbol differ per tier as well.
 * 2. A screen reader hears what the tier means, not just its name. "Established" on its own
 *    tells a non-specialist nothing.
 */

const SYMBOL: Record<EvidenceTier, string> = {
  established: '●●●',
  emerging: '●●○',
  'expert-opinion': '●○○',
  inference: '◆',
  hypothesis: '?',
  retracted: '✕',
};

export function EvidenceBadge({ tier }: { tier: EvidenceTier }) {
  return (
    <span className={`evidence-badge evidence-badge--${tier}`}>
      <span aria-hidden="true" className="evidence-badge__symbol">
        {SYMBOL[tier]}
      </span>
      <span className="evidence-badge__label">{tierLabel(tier)}</span>
      <span className="visually-hidden"> — {tierDescription(tier)}</span>
    </span>
  );
}
