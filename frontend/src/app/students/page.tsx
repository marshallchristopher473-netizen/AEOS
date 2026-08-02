'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';

type Student = {
  id: string;
  first_name: string;
  last_name: string;
  student_number?: string | null;
  grade_level?: string | null;
  iep_status?: boolean;
  created_at?: string | null;
};

export default function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadStudents = async () => {
      try {
        const token = localStorage.getItem('aeos_access_token');
        if (!token) {
          setError('Please sign in to view students.');
          setLoading(false);
          return;
        }

        const res = await fetch(`http://127.0.0.1:8000/students?search=${encodeURIComponent(search)}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) {
          throw new Error(await res.text());
        }

        const data = await res.json();
        setStudents(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load students.');
      } finally {
        setLoading(false);
      }
    };

    loadStudents();
  }, [search]);

  const filteredStudents = useMemo(() => {
    if (!search.trim()) return students;
    return students.filter((student) => {
      const combined = `${student.first_name} ${student.last_name} ${student.student_number ?? ''}`.toLowerCase();
      return combined.includes(search.toLowerCase());
    });
  }, [search, students]);

  return (
    <main className="page-shell">
      <div className="topbar">
        <h1>Students</h1>
        <div className="button-row">
          <Link href="/students/new" className="primary-btn">+ Add student</Link>
        </div>
      </div>

      {error ? <div className="error">{error}</div> : null}

      <div className="card">
        <div className="search-bar">
          <input
            type="text"
            value={search}
            placeholder="Search by student name or number"
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>

        {loading ? (
          <p>Loading students…</p>
        ) : filteredStudents.length === 0 ? (
          <div className="empty-state">No students found.</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Student #</th>
                <th>Grade</th>
                <th>IEP</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map((student) => (
                <tr key={student.id}>
                  <td>
                    <Link href={`/students/${student.id}`}>
                      {student.first_name} {student.last_name}
                    </Link>
                  </td>
                  <td>{student.student_number || '—'}</td>
                  <td>{student.grade_level || '—'}</td>
                  <td>{student.iep_status ? <span className="badge">IEP</span> : 'No'}</td>
                  <td>
                    <Link href={`/students/${student.id}`} className="ghost-btn">
                      View
                    </Link>
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
