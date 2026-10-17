import { getSupabaseBrowserClient } from './supabase';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// The access token of the current Supabase session, refreshed by supabase-js
// when it is near expiry. The AEOS API verifies it independently, so nothing
// here is trusted for authorization.
export async function getAccessToken(): Promise<string | null> {
  if (typeof window === 'undefined') return null;

  const { data, error } = await getSupabaseBrowserClient().auth.getSession();
  if (error) return null;

  return data.session?.access_token ?? null;
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = await getAccessToken();

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
    cache: 'no-store',
  });

  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(errorBody || `Request failed with status ${res.status}`);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}
