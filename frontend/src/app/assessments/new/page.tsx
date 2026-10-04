'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';
import { getAccessToken } from '@/lib/api';
import { createAssessment } from '@/lib/assessments';

export default function NewAssessmentPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError('');

    const form = new FormData(event.currentTarget);
    const payload = {
      student_id: String(form.get('student_id') || '').trim(),
      title: String(form.get('title') || '').trim(),
      assessment_type: String(form.get('assessment_type') || '').trim(),
      status: String(form.get('status') || 'draft').trim(),
      notes: String(form.get('notes') || '').trim() || null,
    };

    try {
      const token = getAccessToken();
      if (!token) {
        throw new Error('Please sign in before creating an assessment.');
      }

      const assessment = await createAssessment(payload);
      router.push(`/assessments/${assessment.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create assessment.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page-shell">
      <div className="topbar">
        <h1>New Assessment Intake</h1>
        <div className="button-row">
          <Link href="/assessments" className="secondary-btn">Back to assessments</Link>
        </div>
      </div>

      {error ? <div role="alert" className="error">{error}</div> : null}

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="field">
              <label htmlFor="student_id">Student ID</label>
              <input id="student_id" name="student_id" required />
            </div>
            <div className="field">
              <label htmlFor="title">Title</label>
              <input id="title" name="title" required />
            </div>
            <div className="field">
              <label htmlFor="assessment_type">Assessment type</label>
              <input id="assessment_type" name="assessment_type" required />
            </div>
            <div className="field">
              <label htmlFor="status">Status</label>
              <select id="status" name="status" defaultValue="draft">
                <option value="draft">Draft</option>
                <option value="submitted">Submitted</option>
                <option value="in_review">In review</option>
                <option value="complete">Complete</option>
              </select>
            </div>
            <div className="field" style={{ gridColumn: '1 / -1' }}>
              <label htmlFor="notes">Notes</label>
              <input id="notes" name="notes" />
            </div>
          </div>

          <div className="button-row" style={{ marginTop: 20 }}>
            <button type="submit" className="primary-btn" disabled={isSubmitting}>
              {isSubmitting ? 'Saving…' : 'Create assessment'}
            </button>
            <Link href="/assessments" className="ghost-btn">Cancel</Link>
          </div>
        </form>
      </div>
    </main>
  );
}
