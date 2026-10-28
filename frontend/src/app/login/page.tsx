'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useEffect, useState } from 'react';

import {
  clearAccessToken,
  getSupabaseClient,
  isSupabaseConfigured,
  readAccessToken,
  storeAccessToken,
} from '@/lib/supabaseClient';

export default function LoginPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [signedInEmail, setSignedInEmail] = useState<string | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);

  // Supabase access tokens are short-lived. On load, re-read the live session
  // so a stale token left in storage is replaced rather than presented to the
  // API and rejected.
  useEffect(() => {
    let active = true;

    const syncSession = async () => {
      if (!isSupabaseConfigured()) {
        if (active) setCheckingSession(false);
        return;
      }

      try {
        const { data } = await getSupabaseClient().auth.getSession();
        if (!active) return;

        if (data.session?.access_token) {
          storeAccessToken(data.session.access_token);
          setSignedInEmail(data.session.user?.email ?? 'Signed in');
        } else if (readAccessToken()) {
          clearAccessToken();
        }
      } catch {
        // A session lookup failure must not strand the user on a blank page;
        // fall through and show the sign-in form.
      } finally {
        if (active) setCheckingSession(false);
      }
    };

    syncSession();

    return () => {
      active = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError('');

    const form = new FormData(event.currentTarget);
    const email = String(form.get('email') || '').trim();
    const password = String(form.get('password') || '');

    try {
      if (!isSupabaseConfigured()) {
        throw new Error(
          'Authentication is not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.',
        );
      }

      const { data, error: signInError } = await getSupabaseClient().auth.signInWithPassword({
        email,
        password,
      });

      if (signInError) {
        throw new Error(signInError.message);
      }

      const accessToken = data.session?.access_token;
      if (!accessToken) {
        throw new Error('Sign-in succeeded but no session token was returned.');
      }

      storeAccessToken(accessToken);
      router.push('/students');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign in.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleSignOut() {
    setError('');

    try {
      if (isSupabaseConfigured()) {
        await getSupabaseClient().auth.signOut();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign out cleanly.');
    } finally {
      clearAccessToken();
      setSignedInEmail(null);
    }
  }

  return (
    <main className="page-shell">
      <div className="topbar">
        <h1>Sign in</h1>
      </div>

      {error ? <div className="error">{error}</div> : null}

      <div className="card">
        {checkingSession ? (
          <p>Checking session…</p>
        ) : signedInEmail ? (
          <>
            <p>
              Signed in as <strong>{signedInEmail}</strong>.
            </p>
            <div className="button-row" style={{ marginTop: 20 }}>
              <Link href="/students" className="primary-btn">
                Go to students
              </Link>
              <button type="button" className="ghost-btn" onClick={handleSignOut}>
                Sign out
              </button>
            </div>
          </>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="email">Email</label>
                <input id="email" name="email" type="email" autoComplete="username" required />
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
        )}
      </div>
    </main>
  );
}
