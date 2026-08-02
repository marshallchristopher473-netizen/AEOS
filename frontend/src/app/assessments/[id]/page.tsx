'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

type Assessment = {
  id: string;
  organization_id: string;
  student_id: string;
  created_by: string;
  title: string;
  assessment_type: string;
  status: string;
  notes?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export default function AssessmentDetailPage() {
  const params = useParams<{ id: string }>();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadAssessment = async () => {
      try {
        const token = localStorage.getItem('aeos_access_token');
        if (!token) {
          setError('Please sign in to view this assessment.');
          setLoading(false);
          return;
        }

        const response = await fetch(`http://127.0.0.1:8000/assessments/${params.id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(await response.text());
        }

        setAssessment(await response.json());
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load assessment details.');
      } finally {
        setLoading(false);
      }
    };

    if (params?.id) {
      loadAssessment();
    }
  }, [params?.id]);

  if (loading) {
    return <main className="page-shell"><p>Loading assessment…</p></main>;
  }

  if (error) {
    return (
      <main className="page-shell">
        <div className="error">{error}</div>
        <Link href="/assessments" className="secondary-btn">Back to assessments</Link>
      </main>
    );
  }

  if (!assessment) {
    return <main className="page-shell">Assessment not found.</main>;
  }

  return (
    <main className="page-shell">
      <div className="topbar">
        <h1>{assessment.title}</h1>
        <div className="button-row">
          <Link href="/assessments" className="secondary-btn">Back to assessments</Link>
        </div>
      </div>

      <div className="card">
        <div className="detail-grid">
          <div className="meta-box"><strong>Type</strong><br />{assessment.assessment_type}</div>
          <div className="meta-box"><strong>Status</strong><br />{assessment.status}</div>
          <div className="meta-box"><strong>Student ID</strong><br />{assessment.student_id}</div>
          <div className="meta-box"><strong>Created by</strong><br />{assessment.created_by}</div>
          <div className="meta-box"><strong>Organization ID</strong><br />{assessment.organization_id}</div>
          <div className="meta-box"><strong>Notes</strong><br />{assessment.notes || '—'}</div>
        </div>
      </div>
    </main>
  );
}
