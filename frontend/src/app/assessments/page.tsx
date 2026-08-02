'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';

type Assessment = {
  id: string;
  title: string;
  assessment_type: string;
  status: string;
  student_id: string;
  created_at?: string | null;
};

export default function AssessmentsPage() {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadAssessments = async () => {
      try {
        const token = localStorage.getItem('aeos_access_token');
        if (!token) {
          setError('Please sign in to view assessments.');
          setLoading(false);
          return;
        }

        const response = await fetch('http://127.0.0.1:8000/assessments', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(await response.text());
        }

        const data = await response.json();
        setAssessments(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load assessments.');
      } finally {
        setLoading(false);
      }
    };

    loadAssessments();
  }, []);

  return (
    <main className="page-shell">
      <div className="topbar">
        <h1>Assessments</h1>
        <div className="button-row">
          <Link href="/assessments/new" className="primary-btn">+ New intake</Link>
        </div>
      </div>

      {error ? <div className="error">{error}</div> : null}

      <div className="card">
        {loading ? (
          <p>Loading assessments…</p>
        ) : assessments.length === 0 ? (
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
                    <Link href={`/assessments/${assessment.id}`} className="ghost-btn">View</Link>
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
