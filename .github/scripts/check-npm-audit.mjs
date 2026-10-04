#!/usr/bin/env node
// Runs the full `npm audit` (development dependencies included) and fails unless
// every reported advisory is covered by an unexpired entry in the exceptions file.
//
// Usage, from the package directory:
//   node ../.github/scripts/check-npm-audit.mjs audit-exceptions.json
//
// Exits 1 when:
//   - an advisory of severity low or above has no exception
//   - an exception names a different package than the one the advisory affects
//   - an exception's `expires` date (YYYY-MM-DD, UTC) is in the past
//   - npm audit does not return a usable report
// An exception that no longer matches any advisory only produces a warning.

import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';

const REPORTED_SEVERITIES = new Set(['low', 'moderate', 'high', 'critical']);
const ADVISORY_ID = /^GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}$/;
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

function fail(message) {
  console.error(`npm audit check failed: ${message}`);
  process.exit(1);
}

const exceptionsPath = process.argv[2];
if (!exceptionsPath) fail('usage: check-npm-audit.mjs <exceptions.json>');

let exceptions;
try {
  ({ exceptions } = JSON.parse(readFileSync(exceptionsPath, 'utf8')));
} catch (error) {
  fail(`cannot read ${exceptionsPath}: ${error.message}`);
}
if (!Array.isArray(exceptions)) fail(`${exceptionsPath} must contain an "exceptions" array`);

const today = new Date().toISOString().slice(0, 10);
const allowed = new Map();
for (const entry of exceptions) {
  const { advisory, package: pkg, expires } = entry ?? {};
  if (!ADVISORY_ID.test(advisory ?? '') || !pkg || !ISO_DATE.test(expires ?? '')) {
    fail(`malformed exception: ${JSON.stringify(entry)}`);
  }
  if (expires < today) {
    fail(`the exception for ${advisory} (${pkg}) expired on ${expires}; fix the dependency, or review the risk again and set a new date`);
  }
  allowed.set(advisory, entry);
}

const audit = spawnSync('npm', ['audit', '--json'], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
if (audit.error) fail(`could not run npm audit: ${audit.error.message}`);

let report;
try {
  report = JSON.parse(audit.stdout);
} catch {
  fail(`npm audit did not return JSON (exit ${audit.status}): ${audit.stderr.trim()}`);
}
if (!report || report.error || report.auditReportVersion !== 2 || typeof report.vulnerabilities !== 'object') {
  fail(`npm audit returned an unusable report: ${JSON.stringify(report?.error ?? report).slice(0, 500)}`);
}

// An advisory appears as an object in the `via` list of the package it affects.
// Packages that are vulnerable only through a dependency list that dependency's
// name as a string instead, so collecting the objects finds every advisory.
const covered = new Set();
const uncovered = new Set();
for (const vulnerability of Object.values(report.vulnerabilities)) {
  for (const via of vulnerability.via) {
    if (typeof via !== 'object' || !REPORTED_SEVERITIES.has(via.severity)) continue;
    const advisory = String(via.url ?? '').split('/').pop();
    if (allowed.get(advisory)?.package === via.name) {
      covered.add(advisory);
    } else {
      uncovered.add(`${via.severity} ${via.name}: ${via.title} (${via.url ?? via.source})`);
    }
  }
}

for (const advisory of covered) {
  const { package: pkg, expires } = allowed.get(advisory);
  console.log(`excepted until ${expires}: ${advisory} (${pkg})`);
}
for (const advisory of allowed.keys()) {
  if (!covered.has(advisory)) {
    console.warn(`warning: the exception for ${advisory} matched no advisory; remove it from ${exceptionsPath}`);
  }
}
if (uncovered.size > 0) {
  fail(`advisories without an exception:\n  ${[...uncovered].join('\n  ')}`);
}
console.log(`npm audit: ${covered.size} excepted advisory(ies), no others reported`);
