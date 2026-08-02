'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';

export default function NewStudentPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError('');

    const form = new FormData(event.currentTarget);
    const payload = {
      first_name: String(form.get('first_name') || '').trim(),
      last_name: String(form.get('last_name') || '').trim(),
      student_number: String(form.get('student_number') || '').trim() || null,
      grade_level: String(form.get('grade_level') || '').trim() || null,
      iep_status: form.get('iep_status') === 'on',
      birth_date: String(form.get('birth_date') || '').trim() || null,
    };

    try {
      const token = localStorage.getItem('aeos_access_token');
      if (!token) {
        throw new Error('Please sign in before creating a student.');
      }

      const response = await fetch('http://127.0.0.1:8000/students/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || 'Unable to create student.');
      }

      router.push('/students');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create student.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page-shell">
      <div className="topbar">
        <h1>Add Student</h1>
        <div className="button-row">
          <Link href="/students" className="secondary-btn">Back to students</Link>
        </div>
      </div>

      {error ? <div className="error">{error}</div> : null}

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="field">
              <label htmlFor="first_name">First name</label>
              <input id="first_name" name="first_name" required />
            </div>

            <div className="field">
              <label htmlFor="last_name">Last name</label>
              <input id="last_name" name="last_name" required />
            </div>

            <div className="field">
              <label htmlFor="student_number">Student number</label>
              <input id="student_number" name="student_number" />
            </div>

            <div className="field">
              <label htmlFor="grade_level">Grade level</label>
              <input id="grade_level" name="grade_level" />
            </div>

            <div className="field">
              <label htmlFor="birth_date">Birth date</label>
              <input id="birth_date" name="birth_date" type="date" />
            </div>

            <div className="field checkbox-row">
              <input id="iep_status" name="iep_status" type="checkbox" />
              <label htmlFor="iep_status">IEP status</label>
            </div>
          </div>

          <div className="button-row" style={{ marginTop: 20 }}>
            <button type="submit" className="primary-btn" disabled={isSubmitting}>
              {isSubmitting ? 'Saving…' : 'Save student'}
            </button>
            <Link href="/students" className="ghost-btn">Cancel</Link>
          </div>
        </form>
      </div>
    </main>
  );
}
