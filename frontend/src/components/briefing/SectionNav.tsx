import Link from 'next/link';
import type { Briefing } from '@/lib/briefing/types';

/**
 * Section navigation.
 *
 * The original document used ten buttons holding client state. That had four consequences:
 * no section could be linked or bookmarked, the browser back button did nothing, screen
 * readers were given plain buttons with no indication of which was current, and all ten
 * section trees were constructed on every render.
 *
 * Links to real routes fix all four at once. `aria-current="page"` carries the selected
 * state, and the list is a real list inside a labelled nav landmark, so a screen reader
 * user can jump straight to it.
 */
export function SectionNav({
  briefing,
  activeSlug,
}: {
  briefing: Briefing;
  activeSlug: string;
}) {
  return (
    <nav aria-label="Briefing sections" className="briefing-nav">
      <ol>
        {briefing.sections.map((section, index) => {
          const isActive = section.slug === activeSlug;
          return (
            <li key={section.slug}>
              <Link
                aria-current={isActive ? 'page' : undefined}
                className={`briefing-nav__link${isActive ? ' briefing-nav__link--active' : ''}`}
                href={`/briefings/${briefing.slug}/${section.slug}`}
              >
                <span aria-hidden="true" className="briefing-nav__index">
                  {index + 1}
                </span>
                <span className="briefing-nav__title">{section.title}</span>
              </Link>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
