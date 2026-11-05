import type { VerificationResult } from '@/lib/evidence';

type Status = VerificationResult['status'];

const EVIDENCE_STYLES: Record<Status, { className: string; label: string; title: string }> = {
  verified: {
    className: 'bg-green-100 text-green-900 ring-1 ring-green-700/30',
    label: '✓ verified',
    title: 'This quote appears verbatim in the student response.',
  },
  'case-insensitive': {
    className: 'bg-amber-100 text-amber-900 ring-1 ring-amber-700/30',
    label: '≈ case-insensitive',
    title: 'This quote appears only when letter case is ignored.',
  },
  not_found: {
    className: 'bg-red-100 text-red-900 ring-1 ring-red-700/40',
    label: '✕ not verified',
    title: 'This quote could NOT be found in the student response. Do not trust it.',
  },
};

export function EvidenceBadge({ status }: { status: Status }) {
  const s = EVIDENCE_STYLES[status];
  return (
    <span className={`badge ${s.className}`} title={s.title} data-evidence-status={status}>
      {s.label}
    </span>
  );
}

const CONFIDENCE_STYLES: Record<'low' | 'medium' | 'high', string> = {
  low: 'bg-slate-100 text-slate-700 ring-1 ring-slate-400/40',
  medium: 'bg-sky-100 text-sky-900 ring-1 ring-sky-700/30',
  high: 'bg-indigo-100 text-indigo-900 ring-1 ring-indigo-700/30',
};

export function ConfidenceBadge({ level }: { level: 'low' | 'medium' | 'high' }) {
  return (
    <span
      className={`badge ${CONFIDENCE_STYLES[level]}`}
      title="Model-reported confidence. Not a measure of accuracy."
    >
      confidence: {level}
    </span>
  );
}

const ACTION_STYLES: Record<string, string> = {
  accept: 'bg-green-100 text-green-900 ring-1 ring-green-700/30',
  revise: 'bg-amber-100 text-amber-900 ring-1 ring-amber-700/30',
  reject: 'bg-red-100 text-red-900 ring-1 ring-red-700/30',
  flag: 'bg-slate-200 text-slate-800 ring-1 ring-slate-500/30',
};

export function ActionBadge({ action }: { action: string }) {
  return <span className={`badge ${ACTION_STYLES[action] ?? ''}`}>{action}</span>;
}
