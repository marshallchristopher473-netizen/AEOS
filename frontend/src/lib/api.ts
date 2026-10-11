const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || '/api').replace(/\/$/, '');

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;

  return localStorage.getItem('aeos_access_token');
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAccessToken();

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
    if (res.status === 401) throw new Error('Please sign in again to continue.');
    const errorBody = await res.json().catch(() => null);
    const detail = errorBody?.detail;
    if (typeof detail === 'string' && res.status < 500) throw new Error(detail);
    if (res.status === 422) throw new Error('Please check the values and try again.');
    throw new Error(`Request failed with status ${res.status}. Please try again.`);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}
