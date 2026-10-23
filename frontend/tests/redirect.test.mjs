// Unit tests for the post-login redirect guard and public-route rules.
// Runs with Node's built-in test runner (Node >= 22.18 strips TypeScript
// types natively): `npm test`.

import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
  DEFAULT_SIGNED_IN_PATH,
  LOGIN_PATH,
  isPublicPath,
  safeRedirectPath,
} from '../src/lib/auth/redirect.ts';

test('only /login is public', () => {
  assert.equal(isPublicPath(LOGIN_PATH), true);
  for (const path of ['/', '/students', '/students/new', '/assessments', '/login/extra']) {
    assert.equal(isPublicPath(path), false, path);
  }
});

test('same-origin paths are kept, including query strings', () => {
  for (const path of ['/students', '/students/abc-123', '/assessments?status=draft', '/']) {
    assert.equal(safeRedirectPath(path), path);
  }
});

test('missing destination falls back to the default page', () => {
  assert.equal(safeRedirectPath(null), DEFAULT_SIGNED_IN_PATH);
  assert.equal(safeRedirectPath(undefined), DEFAULT_SIGNED_IN_PATH);
  assert.equal(safeRedirectPath(''), DEFAULT_SIGNED_IN_PATH);
});

test('off-site and malformed destinations are rejected', () => {
  const attacks = [
    'https://evil.example',
    'http://evil.example/students',
    '//evil.example',
    '/\\evil.example',
    '\\\\evil.example',
    '/\t/evil.example',
    '/\n/evil.example',
    '/students\\..\\evil',
    'javascript:alert(1)',
    'students',
    ' /students',
  ];
  for (const attack of attacks) {
    assert.equal(safeRedirectPath(attack), DEFAULT_SIGNED_IN_PATH, JSON.stringify(attack));
  }
});

test('redirecting back to the login page is not allowed', () => {
  assert.equal(safeRedirectPath('/login'), DEFAULT_SIGNED_IN_PATH);
  assert.equal(safeRedirectPath('/login?next=/students'), DEFAULT_SIGNED_IN_PATH);
  assert.equal(safeRedirectPath('/login#top'), DEFAULT_SIGNED_IN_PATH);
});
