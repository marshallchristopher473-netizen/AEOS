// Public Supabase settings for the browser and the Next.js proxy.
//
// Only the anon (public) key belongs here. The service-role key bypasses
// row-level security and must never be exposed to the frontend.
//
// The NEXT_PUBLIC_* names are referenced literally so Next.js can inline
// them at build time.

export type SupabasePublicConfig = {
  url: string;
  anonKey: string;
};

export function readSupabasePublicConfig(): SupabasePublicConfig | null {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !anonKey) {
    return null;
  }

  return { url, anonKey };
}

export const MISSING_SUPABASE_CONFIG_MESSAGE =
  'Sign-in is not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in frontend/.env.local.';
