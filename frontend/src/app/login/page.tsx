'use client';

import { useRouter } from 'next/navigation';
import { FormEvent, useEffect, useState } from 'react';

import { getSupabaseBrowserClient } from '@/lib/supabase';

export default function LoginPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const redirectIfSignedIn = async () => {
      try {
        const { data } = await getSupabaseBrowserClient().auth.getSession();
        if (data.session) router.replace('/students');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Sign-in is unavailable.');
      }
    };

    redirectIfSignedIn();
  }, [router]);

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
        // One message for every failure, so the form does not reveal which
        // email addresses have accounts.
        throw new Error('Sign-in failed. Check your email and password.');
      }

      router.replace('/students');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign-in failed.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="page-shell">
      <div className="topbar">
        <h1>Sign in</h1>
      </div>

      {error ? <div className="error">{error}</div> : null}

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
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
          </div>

          <div className="button-row" style={{ marginTop: 20 }}>
            <button type="submit" className="primary-btn" disabled={isSubmitting}>
              {isSubmitting ? 'Signing in…' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
