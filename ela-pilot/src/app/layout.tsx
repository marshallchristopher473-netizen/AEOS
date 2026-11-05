import './globals.css';
import type { Metadata } from 'next';
import Link from 'next/link';
import { currentReviewer } from '@/lib/reviewer';

export const metadata: Metadata = {
  title: 'AEOS ELA Pilot',
  description: 'Auditable, teacher-in-the-loop rubric scoring',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const reviewer = currentReviewer();

  return (
    <html lang="en">
      <body>
        <header className="border-b border-slate-200 bg-white">
          <nav className="mx-auto flex max-w-6xl items-center gap-6 px-6 py-3 text-sm">
            <Link href="/" className="font-semibold text-slate-900">
              AEOS ELA Pilot
            </Link>
            <Link href="/" className="text-slate-600 hover:text-slate-900">
              Dashboard
            </Link>
            <Link href="/calibration" className="text-slate-600 hover:text-slate-900">
              Calibration
            </Link>
            <Link href="/rubrics" className="text-slate-600 hover:text-slate-900">
              Rubrics
            </Link>
            <span className="ml-auto text-slate-500">
              {reviewer ? (
                <>
                  Reviewer: <span className="font-medium text-slate-800">{reviewer}</span>
                </>
              ) : (
                <span className="text-red-700">No reviewer selected</span>
              )}
            </span>
          </nav>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-6">{children}</main>
        <footer className="mx-auto max-w-6xl px-6 pb-10 pt-4 text-xs text-slate-500">
          Pilot instance — synthetic data only. AI output is a draft for teacher review, never a
          final grade.
        </footer>
      </body>
    </html>
  );
}
