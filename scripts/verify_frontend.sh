#!/usr/bin/env bash
# Runs the frontend verification steps that are actually possible headlessly
# today. See the NOTE below for a known gap.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT/frontend"

echo "== npm ci =="
npm ci

echo "== npm run build =="
npm run build

# NOTE (verified in a live audit): `npm run lint` (next lint) cannot run
# non-interactively today. No .eslintrc*/eslint.config.* exists in
# frontend/, so `next lint` drops into an interactive "How would you like
# to configure ESLint?" prompt and hangs in CI/scripted contexts. Until an
# ESLint config is committed to frontend/, this script intentionally does
# not call `npm run lint` rather than silently skip a check that would
# otherwise look green. Fixing this (committing a non-interactive ESLint
# config) is tracked as an open backend/frontend CI gap, not solved here.
echo "== npm run lint: SKIPPED (no committed ESLint config; next lint requires interactive setup) =="

echo "== Frontend verification complete (build only; lint gap noted above) =="
