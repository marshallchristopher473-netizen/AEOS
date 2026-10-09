import assert from 'node:assert/strict';
import { readdir, readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { ESLint } from 'eslint';

// package.json overrides @next/eslint-plugin-next's fast-glob with tinyglobby
// (already installed through eslint-config-next) to remove the unpatched
// fast-glob → micromatch → braces chain (GHSA-vfj7-8cjw-p6xm). These tests pin
// the assumptions that make that substitution safe for this project.
const frontend = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const require = createRequire(path.join(frontend, 'package.json'));
const pluginDist = path.dirname(require.resolve('@next/eslint-plugin-next'));
const pluginRequire = createRequire(path.join(pluginDist, 'index.js'));

async function pluginGlobMembers() {
  const members = new Set();
  const files = (await readdir(pluginDist, { recursive: true })).filter((file) => file.endsWith('.js'));
  for (const file of files) {
    const source = await readFile(path.join(pluginDist, file), 'utf8');
    for (const [, binding] of source.matchAll(/var (\w+) = require\("fast-glob"\)/g)) {
      for (const [, member] of source.matchAll(new RegExp(`\\b${binding}\\.(\\w+)`, 'g'))) members.add(member);
    }
  }
  return [...members];
}

test('plugin resolves fast-glob to tinyglobby and only uses members it provides', async () => {
  assert.equal(pluginRequire('fast-glob/package.json').name, 'tinyglobby');
  const members = await pluginGlobMembers();
  assert.ok(
    members.length > 0,
    '@next/eslint-plugin-next no longer requires fast-glob; remove the package.json override',
  );
  const glob = pluginRequire('fast-glob');
  for (const member of members) assert.equal(typeof glob[member], 'function', `fast-glob.${member}`);
});

test('ESLint config leaves settings.next.rootDir unset for every linted file', async () => {
  // tinyglobby expands directory patterns that fast-glob would not, so the
  // override is only equivalent while the plugin globs nothing (rootDir unset).
  // Flat config can scope `settings` to a `files` glob, so check every file
  // `eslint .` lints (ESLint's own enumeration), not one sample file.
  const eslint = new ESLint({ cwd: frontend });
  const files = (await eslint.lintFiles(['.'])).map((result) => result.filePath);
  assert.ok(files.includes(path.join(frontend, 'src/app/assessments/page.tsx')), 'linted file discovery is broken');
  for (const file of files) {
    const config = await eslint.calculateConfigForFile(file);
    assert.equal(config.settings?.next?.rootDir, undefined, path.relative(frontend, file));
  }
});

test('no-html-link-for-pages still reports raw links to app routes', async () => {
  const eslint = new ESLint({ cwd: frontend });
  const [result] = await eslint.lintText(
    'export default function Page() {\n  return <a href="/students">Students</a>;\n}\n',
    { filePath: path.join(frontend, 'src/app/lint-probe/page.tsx') },
  );
  assert.deepEqual(
    result.messages.map((message) => message.ruleId),
    ['@next/next/no-html-link-for-pages'],
  );
});
