'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState } from 'react';

import { LOGIN_PATH, isPublicPath } from '@/lib/auth/redirect';
import { getSupabaseBrowserClient } from '@/lib/supabase/client';

export default function AppHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [error, setError] = useState('');

  if (isPublicPath(pathname)) {
    return null;
  }

  async function handleSignOut() {
    setIsSigningOut(true);
    setError('');

    const { error: signOutError } = await getSupabaseBrowserClient().auth.signOut();
    if (signOutError) {
      setError('Sign-out failed. Please try again.');
      setIsSigningOut(false);
      return;
    }

    router.replace(LOGIN_PATH);
    router.refresh();
  }

  return (
    <header className="app-header">
      <nav className="button-row">
        <Link href="/students">Students</Link>
        <Link href="/assessments">Assessments</Link>
      </nav>
      <div className="button-row">
        {error ? <span className="error-inline">{error}</span> : null}
        <button
          type="button"
          className="secondary-btn"
          onClick={handleSignOut}
          disabled={isSigningOut}
        >
          {isSigningOut ? 'Signing out…' : 'Sign out'}
        </button>
      </div>
    </header>
  );
}
