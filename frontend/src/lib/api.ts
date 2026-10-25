import { getSupabaseBrowserClient } from '@/lib/supabase/client';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || '/api').replace(/\/$/, '');

// Errors whose body is the backend's sanitized `{ code, message }` shape keep
// the code so callers can react to it. The message is a fixed server string.
export class ApiError extends Error {
  status: number;
  code: string | null;

  constructor(message: string, status: number, code: string | null = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

// The bearer token comes from the signed-in Supabase session, which
// @supabase/ssr keeps in cookies; application code never stores tokens.
// getSession() refreshes an expired access token before returning it.
export async function getAccessToken(): Promise<string | null> {
  if (typeof window === 'undefined') return null;

  const { data } = await getSupabaseBrowserClient().auth.getSession();
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
    if (res.status === 401) throw new ApiError('Please sign in again to continue.', 401);
    const errorBody = await res.json().catch(() => null);
    const detail = errorBody?.detail;
    if (detail && typeof detail === 'object' && !Array.isArray(detail)
        && typeof detail.code === 'string' && typeof detail.message === 'string') {
      throw new ApiError(detail.message, res.status, detail.code);
    }
    if (typeof detail === 'string' && res.status < 500) throw new ApiError(detail, res.status);
    if (res.status === 422) throw new ApiError('Please check the values and try again.', 422);
    throw new ApiError(`Request failed with status ${res.status}. Please try again.`, res.status);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}
