import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

import { DEFAULT_SIGNED_IN_PATH, LOGIN_PATH, isPublicPath } from '@/lib/auth/redirect';
import { readSupabasePublicConfig } from '@/lib/supabase/config';

// Redirects signed-out visitors to /login and refreshes the Supabase session
// cookie on each request.
//
// This is a navigation convenience, not the security boundary: the FastAPI
// backend verifies the bearer token and enforces tenant access on every API
// call regardless of what the proxy decides.
export async function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  let response = NextResponse.next({ request });

  const supabaseConfig = readSupabasePublicConfig();
  if (!supabaseConfig) {
    // Fail closed: without auth settings nobody can be signed in.
    return isPublicPath(pathname) ? response : redirectTo(request, LOGIN_PATH, response);
  }

  const supabase = createServerClient(supabaseConfig.url, supabaseConfig.anonKey, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet, headers) {
        cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
        response = NextResponse.next({ request });
        cookiesToSet.forEach(({ name, value, options }) =>
          response.cookies.set(name, value, options),
        );
        Object.entries(headers).forEach(([key, value]) => response.headers.set(key, value));
      },
    },
  });

  // getClaims() validates the session JWT rather than trusting the cookie.
  const { data, error } = await supabase.auth.getClaims();
  const isSignedIn = !error && Boolean(data?.claims?.sub);

  if (!isSignedIn && !isPublicPath(pathname)) {
    const loginUrl = new URL(LOGIN_PATH, request.url);
    loginUrl.searchParams.set('next', `${pathname}${search}`);
    return redirectTo(request, loginUrl, response);
  }

  if (isSignedIn && pathname === LOGIN_PATH) {
    return redirectTo(request, DEFAULT_SIGNED_IN_PATH, response);
  }

  return response;
}

// Redirects while keeping any refreshed session cookies and no-store headers
// that Supabase attached to the pass-through response.
function redirectTo(request: NextRequest, target: string | URL, from: NextResponse) {
  const redirect = NextResponse.redirect(new URL(target, request.url));
  from.cookies.getAll().forEach((cookie) => redirect.cookies.set(cookie));
  ['cache-control', 'expires', 'pragma'].forEach((header) => {
    const value = from.headers.get(header);
    if (value) redirect.headers.set(header, value);
  });
  return redirect;
}

export const config = {
  // Skip Next.js internals, static files and the same-origin /api rewrite to
  // FastAPI, which checks the bearer token itself and answers 401 as JSON.
  // Redirecting an API call to /login would hand the client an HTML page.
  matcher: ['/((?!api/|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)'],
};
