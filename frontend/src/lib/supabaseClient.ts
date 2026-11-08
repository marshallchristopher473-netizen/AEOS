import { createClient, type SupabaseClient } from '@supabase/supabase-js';

/**
 * Browser-side Supabase client used only to obtain a user session.
 *
 * Only the publishable anon key is read here. The service-role key is a
 * server-only credential and must never reach client code: the FastAPI backend
 * holds it and is the sole component that bypasses RLS.
 */

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export const ACCESS_TOKEN_STORAGE_KEY = 'aeos_access_token';

let client: SupabaseClient | null = null;

export function isSupabaseConfigured(): boolean {
  return Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);
}

export function getSupabaseClient(): SupabaseClient {
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    throw new Error(
      'Authentication is not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.',
    );
  }

  if (!client) {
    client = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  }

  return client;
}

export function storeAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, token);
}

export function clearAccessToken(): void {
  localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
}

export function readAccessToken(): string | null {
  if (typeof window === 'undefined') return null;

  return localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
}
