import type { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ClaimCard } from '@/components/briefing/ClaimCard';
import { SectionNav } from '@/components/briefing/SectionNav';
import { MINDUNLOCK_BRIEFING } from '@/content/mindunlock';
import { findSection } from '@/lib/briefing/types';
import { assertBriefingValid } from '@/lib/briefing/validate';
import './briefing.css';

/**
 * Evaluated at module load, which during `next build` means the build fails rather than
 * publishing a briefing whose claims are not backed at the tier they assert. This is the
 * enforcement point for "evidence before claims" — a rule nobody remembers under deadline
 * unless something refuses to compile.
 */
assertBriefingValid(MINDUNLOCK_BRIEFING);

type PageProps = { params: Promise<{ section: string }> };

export function generateStaticParams() {
  return MINDUNLOCK_BRIEFING.sections.map((section) => ({ section: section.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { section: slug } = await params;
  const section = findSection(MINDUNLOCK_BRIEFING, slug);

  if (!section) {
    return { title: 'Section not found' };
  }

  return {
    title: `${section.title} — ${MINDUNLOCK_BRIEFING.title}`,
    description: section.summary,
  };
}

export default async function BriefingSectionPage({ params }: PageProps) {
  const { section: slug } = await params;
  const section = findSection(MINDUNLOCK_BRIEFING, slug);

  if (!section) {
    notFound();
  }

  const index = MINDUNLOCK_BRIEFING.sections.indexOf(section);
  const previous = MINDUNLOCK_BRIEFING.sections[index - 1];
  const next = MINDUNLOCK_BRIEFING.sections[index + 1];

  return (
    <div className="briefing" data-tone={section.tone}>
      <a className="skip-link" href="#briefing-main">
        Skip to section content
      </a>

      <header className="briefing__masthead">
        <p className="briefing__eyebrow">AEOS module briefing</p>
        <h1>{MINDUNLOCK_BRIEFING.title}</h1>
        <p className="briefing__subtitle">{MINDUNLOCK_BRIEFING.subtitle}</p>
        <p className="briefing__scope">{MINDUNLOCK_BRIEFING.scope}</p>
        <p className="briefing__revised">
          Revised <time dateTime={MINDUNLOCK_BRIEFING.revised}>{MINDUNLOCK_BRIEFING.revised}</time>
        </p>
      </header>

      <SectionNav activeSlug={section.slug} briefing={MINDUNLOCK_BRIEFING} />

      <main className="briefing__main" id="briefing-main" tabIndex={-1}>
        <h2 className="briefing__section-title">{section.title}</h2>
        <p className="briefing__section-summary">{section.summary}</p>

        {section.groups.map((group) => (
          <section aria-labelledby={`${group.id}-heading`} className="claim-group" key={group.id}>
            <h3 id={`${group.id}-heading`}>{group.heading}</h3>
            {group.intro ? <p className="claim-group__intro">{group.intro}</p> : null}
            <div className="claim-group__claims">
              {group.claims.map((claim) => (
                <ClaimCard briefing={MINDUNLOCK_BRIEFING} claim={claim} key={claim.id} />
              ))}
            </div>
          </section>
        ))}

        <nav aria-label="Previous and next section" className="briefing__pager">
          {previous ? (
            <Link href={`/briefings/${MINDUNLOCK_BRIEFING.slug}/${previous.slug}`}>
              <span aria-hidden="true">←</span> {previous.title}
            </Link>
          ) : (
            <span />
          )}
          {next ? (
            <Link href={`/briefings/${MINDUNLOCK_BRIEFING.slug}/${next.slug}`}>
              {next.title} <span aria-hidden="true">→</span>
            </Link>
          ) : (
            <span />
          )}
        </nav>
      </main>
    </div>
  );
}
