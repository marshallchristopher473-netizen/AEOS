import assert from 'node:assert/strict';
import { readdir, readFile } from 'node:fs/promises';
import test from 'node:test';

// getAccessToken() reads the Supabase session and is async. A call without
// `await` yields a Promise, which is always truthy, so a "please sign in"
// check written as `if (!getAccessToken())` can never fire. Neither `tsc`
// (strict) nor the lint config reports that, so this guard does.
const SRC = new URL('../src/', import.meta.url);

async function sourceFiles(dir) {
  const files = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const url = new URL(entry.name + (entry.isDirectory() ? '/' : ''), dir);
    if (entry.isDirectory()) files.push(...await sourceFiles(url));
    else if (/\.(ts|tsx)$/.test(entry.name)) files.push(url);
  }
  return files;
}

test('every getAccessToken() call is awaited', async () => {
  const unawaited = [];
  let calls = 0;
  for (const file of await sourceFiles(SRC)) {
    const lines = (await readFile(file, 'utf8')).split('\n');
    lines.forEach((line, index) => {
      for (const match of line.matchAll(/getAccessToken\(/g)) {
        const before = line.slice(0, match.index);
        if (/\bfunction\s+$/.test(before)) continue; // the declaration itself
        calls += 1;
        if (!/\bawait\s+$/.test(before)) {
          unawaited.push(`${file.pathname.split('/src/')[1]}:${index + 1}: ${line.trim()}`);
        }
      }
    });
  }
  assert.ok(calls > 0, 'expected at least one getAccessToken() call site');
  assert.deepEqual(unawaited, []);
});
