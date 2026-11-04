type Point = { n: number; qwk: number | null; at: string };

/**
 * Cumulative-QWK sparkline. Inline SVG so the pilot needs no chart dependency.
 * The kill threshold is drawn as a dashed rule so "below the line" is visible
 * without reading the axis.
 */
export function QwkTrend({ points, threshold }: { points: Point[]; threshold: number }) {
  const usable = points.filter((p): p is Point & { qwk: number } => p.qwk !== null);

  if (usable.length < 2) {
    return (
      <p className="text-sm text-slate-500">
        Not enough decisions yet to plot a trend ({usable.length} point
        {usable.length === 1 ? '' : 's'}). At least 2 are needed.
      </p>
    );
  }

  const width = 640;
  const height = 140;
  const pad = { top: 10, right: 10, bottom: 20, left: 32 };
  const innerW = width - pad.left - pad.right;
  const innerH = height - pad.top - pad.bottom;

  // QWK ranges -1..1; clamp the drawn domain to the data plus the threshold.
  const values = usable.map((p) => p.qwk);
  const lo = Math.min(-0.1, Math.min(...values), threshold - 0.1);
  const hi = Math.max(1, Math.max(...values));

  const x = (i: number) => pad.left + (i / (usable.length - 1)) * innerW;
  const y = (v: number) => pad.top + (1 - (v - lo) / (hi - lo)) * innerH;

  const path = usable.map((p, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(p.qwk).toFixed(1)}`).join(' ');
  const thresholdY = y(threshold);

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="h-auto w-full"
      role="img"
      aria-label={`Cumulative QWK across ${usable.length} decisions, ending at ${usable[usable.length - 1]?.qwk.toFixed(2)}`}
    >
      <line
        x1={pad.left}
        x2={width - pad.right}
        y1={thresholdY}
        y2={thresholdY}
        stroke="#b91c1c"
        strokeDasharray="4 3"
        strokeWidth={1}
      />
      <text x={pad.left} y={thresholdY - 4} fontSize={10} fill="#b91c1c">
        kill threshold {threshold}
      </text>

      <line
        x1={pad.left}
        x2={pad.left}
        y1={pad.top}
        y2={height - pad.bottom}
        stroke="#cbd5e1"
        strokeWidth={1}
      />
      <text x={4} y={y(hi) + 4} fontSize={10} fill="#64748b">
        {hi.toFixed(1)}
      </text>
      <text x={4} y={y(lo) + 4} fontSize={10} fill="#64748b">
        {lo.toFixed(1)}
      </text>

      <path d={path} fill="none" stroke="#1d4ed8" strokeWidth={2} />
      {usable.map((p, i) => (
        <circle key={p.n} cx={x(i)} cy={y(p.qwk)} r={2.5} fill="#1d4ed8">
          <title>{`after ${p.n} decision${p.n === 1 ? '' : 's'}: QWK ${p.qwk.toFixed(3)}`}</title>
        </circle>
      ))}
      <text x={pad.left} y={height - 6} fontSize={10} fill="#64748b">
        decisions →
      </text>
    </svg>
  );
}
