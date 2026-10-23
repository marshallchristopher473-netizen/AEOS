'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { FormEvent, Suspense, useState } from 'react';

import { safeRedirectPath } from '@/lib/auth/redirect';
import { getSupabaseBrowserClient } from '@/lib/supabase/client';

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError('');

    const form = new FormData(event.currentTarget);
    const email = String(form.get('email') || '').trim();
    const password = String(form.get('password') || '');

    try {
      const { error: signInError } = await getSupabaseBrowserClient().auth.signInWithPassword({
        email,
        password,
      });

      if (signInError) {
        // Same message for unknown email and wrong password.
        throw new Error('Incorrect email or password.');
      }

      router.replace(safeRedirectPath(searchParams.get('next')));
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign in.');
      setIsSubmitting(false);
    }
  }

  return (
    <form className="form-grid" onSubmit={handleSubmit}>
      {error ? <div className="error">{error}</div> : null}

      <div className="field">
        <label htmlFor="email">Email</label>
        <input id="email" name="email" type="email" autoComplete="email" required />
      </div>

      <div className="field">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
        />
      </div>

      <div className="button-row">
        <button type="submit" className="primary-btn" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in…' : 'Sign in'}
        </button>
      </div>
    </form>
  );
}

export default function LoginPage() {
  return (
    <main className="page-shell auth-shell">
      <div className="card">
        <h1>Sign in to AEOS</h1>
        <Suspense fallback={<p>Loading…</p>}>
          <LoginForm />
        </Suspense>
      </div>
    </main>
  );
}
