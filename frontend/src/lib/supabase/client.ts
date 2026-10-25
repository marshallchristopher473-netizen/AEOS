import { createBrowserClient } from '@supabase/ssr';
import type { SupabaseClient } from '@supabase/supabase-js';

import { MISSING_SUPABASE_CONFIG_MESSAGE, readSupabasePublicConfig } from './config';

let browserClient: SupabaseClient | null = null;

// Returns the shared browser client. The session is kept in cookies managed by
// @supabase/ssr so the Next.js proxy can read it on the server; application
// code never stores tokens itself.
//
// Created lazily so pages can be prerendered without Supabase settings.
export function getSupabaseBrowserClient(): SupabaseClient {
  if (browserClient) {
    return browserClient;
  }

  const config = readSupabasePublicConfig();
  if (!config) {
    throw new Error(MISSING_SUPABASE_CONFIG_MESSAGE);
  }

  browserClient = createBrowserClient(config.url, config.anonKey);
  return browserClient;
}
