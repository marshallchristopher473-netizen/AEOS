import { getDb } from '@db/client';
import { listRubrics } from '@/lib/repo';
import { parseRubric } from '@/lib/rubric';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

/** Read-only for the pilot; editing is explicitly v2 (see brief, build step 13). */
export default function RubricsPage() {
  const db = getDb();
  const rubrics = listRubrics(db);

  if (rubrics.length === 0) {
    return (
      <div className="card">
        <h1 className="text-lg font-semibold">No rubrics</h1>
        <p className="mt-2 text-sm text-slate-600">
          Run <code className="rounded bg-slate-100 px-1">npm run seed</code> first.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-xl font-semibold">Rubrics</h1>
        <p className="mt-1 text-sm text-slate-600">
          Read-only in the pilot. Editing a rubric mid-pilot would change what the metrics mean, so
          it is deliberately out of scope.
        </p>
      </header>

      {rubrics.map((row) => {
        const rubric = parseRubric(row.definition_json);
        const totalWeight = rubric.criteria.reduce((sum, c) => sum + c.weight, 0);
        return (
          <section key={row.id} className="card">
            <h2 className="font-semibold">{rubric.name}</h2>
            <p className="text-xs text-slate-500">
              <code>{rubric.id}</code> · {rubric.criteria.length} criteria · total weight{' '}
              {totalWeight}
            </p>
            <table className="mt-3 w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500">
                  <th className="py-1">Criterion</th>
                  <th className="py-1">Scale</th>
                  <th className="py-1">Weight</th>
                  <th className="py-1">Description</th>
                </tr>
              </thead>
              <tbody>
                {rubric.criteria.map((c) => (
                  <tr key={c.id} className="border-t border-slate-100 align-top">
                    <td className="py-1">
                      <div className="font-medium">{c.label}</div>
                      <code className="text-xs text-slate-500">{c.id}</code>
                    </td>
                    <td className="py-1 tabular-nums">
                      {c.scale.min}–{c.scale.max}
                    </td>
                    <td className="py-1 tabular-nums">
                      {c.weight}{' '}
                      <span className="text-xs text-slate-400">
                        ({((c.weight / totalWeight) * 100).toFixed(0)}%)
                      </span>
                    </td>
                    <td className="py-1 text-slate-600">
                      {c.description}
                      {c.anchors?.length ? (
                        <ul className="mt-1 list-inside list-disc text-xs text-slate-500">
                          {c.anchors.map((a) => (
                            <li key={a.score}>
                              {a.score}: {a.exemplar}
                            </li>
                          ))}
                        </ul>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        );
      })}
    </div>
  );
}
