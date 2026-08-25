#!/usr/bin/env bash
# Sets up (or re-verifies) the AEOS backend + frontend toolchain in a fresh
# Codespace / devcontainer. Idempotent: safe to re-run.
#
# This script only installs pinned dependencies from the repository's own
# manifests (backend/requirements-dev.txt, frontend/package-lock.json). It
# never invents or upgrades a dependency.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "== AEOS environment verification =="

echo "-- Python --"
python3 --version

if [ ! -d ".venv" ]; then
  echo "Creating backend virtualenv at .venv"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip --quiet
pip install -r backend/requirements-dev.txt --quiet
echo "Backend dependencies installed from backend/requirements-dev.txt"

echo "-- Node --"
node --version
npm --version

if [ -f "frontend/package-lock.json" ]; then
  (cd frontend && npm ci)
  echo "Frontend dependencies installed from frontend/package-lock.json"
else
  echo "frontend/package-lock.json not found; skipping frontend install" >&2
fi

if [ ! -f "backend/.env" ] && [ -f "backend/.env.example" ]; then
  echo "NOTE: backend/.env does not exist yet."
  echo "Copy backend/.env.example to backend/.env and fill in your own Supabase project values."
  echo "Never commit backend/.env."
fi

echo "== Environment verification complete =="
