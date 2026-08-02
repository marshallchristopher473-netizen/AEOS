'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

type Student = {
  id: string;
  first_name: string;
  last_name: string;
  student_number?: string | null;
  grade_level?: string | null;
  iep_status?: boolean;
  birth_date?: string | null;
  organization_id?: string;
  created_at?: string | null;
  updated_at?: string | null;
};

export default function StudentDetailPage() {
  const params = useParams<{ id: string }>();
  const [student, setStudent] = useState<Student | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadStudent = async () => {
      try {
        const token = localStorage.getItem('aeos_access_token');
        if (!token) {
          setError('Please sign in to view this student.');
          setLoading(false);
          return;
        }

        const res = await fetch(`http://127.0.0.1:8000/students/${params.id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) {
          throw new Error(await res.text());
        }

        setStudent(await res.json());
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load student details.');
      } finally {
        setLoading(false);
      }
    };

    if (params?.id) {
      loadStudent();
    }
  }, [params?.id]);

  if (loading) {
    return <main className="page-shell"><p>Loading student…</p></main>;
  }

  if (error) {
    return (
      <main className="page-shell">
        <div className="error">{error}</div>
        <Link href="/students" className="secondary-btn">Back to students</Link>
      </main>
    );
  }

  if (!student) {
    return <main className="page-shell">Student not found.</main>;
  }

  return (
    <main className="page-shell">
      <div className="topbar">
        <h1>{student.first_name} {student.last_name}</h1>
        <div className="button-row">
          <Link href="/students" className="secondary-btn">Back to students</Link>
        </div>
      </div>

      <div className="card">
        <div className="detail-grid">
          <div className="meta-box"><strong>Student #</strong><br />{student.student_number || '—'}</div>
          <div className="meta-box"><strong>Grade</strong><br />{student.grade_level || '—'}</div>
          <div className="meta-box"><strong>IEP</strong><br />{student.iep_status ? 'Yes' : 'No'}</div>
          <div className="meta-box"><strong>Birth date</strong><br />{student.birth_date || '—'}</div>
        </div>
      </div>
    </main>
  );
}
