// Route rules shared by the proxy and the login page.
//
// This file must stay dependency-free plain TypeScript: it is unit tested
// directly with `node --test` (see tests/redirect.test.mjs).

export const LOGIN_PATH = '/login';
export const DEFAULT_SIGNED_IN_PATH = '/students';

// Pages reachable without a session. Everything else requires sign-in.
const PUBLIC_PATHS = new Set<string>([LOGIN_PATH]);

export function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.has(pathname);
}

// Only same-origin absolute paths are accepted as post-login destinations.
// Rejects protocol-relative URLs (`//evil.example`), backslash variants that
// browsers normalise to `//`, and any whitespace or control character, which
// browsers strip from URLs and could otherwise turn `/\t/evil.example` into
// `//evil.example`.
const SAFE_PATH = /^\/(?![/\\])[^\\\s\u0000-\u001f\u007f]*$/;

export function safeRedirectPath(candidate: string | null | undefined): string {
  if (!candidate || !SAFE_PATH.test(candidate)) {
    return DEFAULT_SIGNED_IN_PATH;
  }

  const pathname = candidate.split(/[?#]/, 1)[0];
  if (isPublicPath(pathname)) {
    return DEFAULT_SIGNED_IN_PATH;
  }

  return candidate;
}
