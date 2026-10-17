'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getAccessToken } from '@/lib/api';
import { Assessment, listAssessments } from '@/lib/assessments';

export default function AssessmentsPage() {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    const loadAssessments = async () => {
      try {
        const token = getAccessToken();
        if (!token) {
          setError('Please sign in to view assessments.');
          setLoading(false);
          return;
        }

        const data = await listAssessments(controller.signal);
        if (!controller.signal.aborted) setAssessments(data);
      } catch (err) {
        if (!controller.signal.aborted) setError(err instanceof Error ? err.message : 'Unable to load assessments.');
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    };

    loadAssessments();
    return () => controller.abort();
  }, []);

  return (
    <main className="page-shell">
      <div className="topbar">
        <h1>Assessments</h1>
        <div className="button-row">
          <Link href="/assessments/new" className="primary-btn">+ New intake</Link>
        </div>
      </div>

      {error ? <div role="alert" className="error">{error}</div> : null}

      <div className="card">
        {loading ? (
          <p>Loading assessments…</p>
        ) : error ? <p>Assessments could not be loaded.</p> : assessments.length === 0 ? (
          <div className="empty-state">No assessments found.</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Type</th>
                <th>Status</th>
                <th>Student</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {assessments.map((assessment) => (
                <tr key={assessment.id}>
                  <td>{assessment.title}</td>
                  <td>{assessment.assessment_type}</td>
                  <td>{assessment.status}</td>
                  <td>{assessment.student_id}</td>
                  <td>
                    <Link href={`/assessments/${assessment.id}`} className="ghost-btn">Review</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </main>
  );
}
