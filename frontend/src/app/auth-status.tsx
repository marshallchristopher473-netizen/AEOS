'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { getSupabaseBrowserClient } from '@/lib/supabase';

export default function AuthStatus() {
  const router = useRouter();
  const [email, setEmail] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let supabase;
    try {
      supabase = getSupabaseBrowserClient();
    } catch {
      // Not configured: stay hidden; the login page reports the problem.
      return;
    }

    supabase.auth.getSession().then(({ data }) => {
      setEmail(data.session?.user.email ?? null);
      setReady(true);
    });

    const { data } = supabase.auth.onAuthStateChange((_event, session) => {
      setEmail(session?.user.email ?? null);
    });

    return () => data.subscription.unsubscribe();
  }, []);

  async function handleSignOut() {
    await getSupabaseBrowserClient().auth.signOut();
    router.replace('/login');
  }

  if (!ready) return null;

  return (
    <header className="auth-bar">
      {email ? (
        <>
          <span>Signed in as {email}</span>
          <button type="button" className="ghost-btn" onClick={handleSignOut}>
            Sign out
          </button>
        </>
      ) : (
        <Link href="/login" className="ghost-btn">Sign in</Link>
      )}
    </header>
  );
}
