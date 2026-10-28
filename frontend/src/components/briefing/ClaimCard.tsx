import type { Briefing, Claim } from '@/lib/briefing/types';
import { sourcesFor } from '@/lib/briefing/types';
import { EvidenceBadge } from './EvidenceBadge';

/**
 * A single graded assertion with its provenance attached.
 *
 * The citation is not a footnote the reader has to chase — it sits under the claim, with
 * the caveat that bounds it. That placement is the whole point: a claim and the limit of
 * its evidence should be impossible to read separately.
 */
export function ClaimCard({ claim, briefing }: { claim: Claim; briefing: Briefing }) {
  const sources = sourcesFor(briefing, claim);
  const noteLabel = claim.tier === 'retracted' ? 'What the original document said' : 'Note';

  return (
    <article className={`claim claim--${claim.tier}`} aria-labelledby={`${claim.id}-text`}>
      <div className="claim__head">
        <EvidenceBadge tier={claim.tier} />
      </div>

      <p className="claim__text" id={`${claim.id}-text`}>
        {claim.text}
      </p>

      {claim.magnitude ? (
        <dl className="claim__magnitude">
          <div>
            <dt>Reported magnitude</dt>
            <dd>{claim.magnitude.value}</dd>
          </div>
          <div>
            <dt>Metric</dt>
            <dd>{claim.magnitude.metric}</dd>
          </div>
          <div>
            <dt>Population</dt>
            <dd>{claim.magnitude.population}</dd>
          </div>
        </dl>
      ) : null}

      {claim.note ? (
        <div className="claim__note">
          <p className="claim__note-label">{noteLabel}</p>
          <p>{claim.note}</p>
        </div>
      ) : null}

      {sources.length > 0 ? (
        <div className="claim__sources">
          <h4 className="claim__sources-heading">
            {sources.length === 1 ? 'Source' : 'Sources'}
          </h4>
          <ul>
            {sources.map((source) => (
              <li key={source.id}>
                <cite>
                  {source.authors} ({source.year}). {source.title}
                  {source.venue ? <>. {source.venue}</> : null}.
                </cite>{' '}
                <span className="claim__source-kind">{source.kind.replace(/-/g, ' ')}</span>
                {source.locator ? (
                  <>
                    {' '}
                    <a href={source.locator} rel="noreferrer noopener" target="_blank">
                      Open source
                      <span className="visually-hidden"> for {source.authors}, {source.year} (opens in a new tab)</span>
                    </a>
                  </>
                ) : null}
                {source.caveat ? <p className="claim__caveat">Limits: {source.caveat}</p> : null}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p className="claim__sources claim__sources--none">
          No source. This is our own untested position.
        </p>
      )}
    </article>
  );
}
