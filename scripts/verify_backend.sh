#!/usr/bin/env bash
# Runs the same backend verification steps as .github/workflows/backend.yml,
# locally. Mirrors the existing .github/workflows/p0-backend-tests.yml gate.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT/backend"

if [ -d "../.venv" ]; then
  # shellcheck disable=SC1091
  source ../.venv/bin/activate
fi

echo "== Static compilation check =="
python -m compileall -q app tests

echo "== Verify backend import =="
python -c "from app.main import app; print('backend OK')"

echo "== Verify schemas import =="
python -c "from app.models.schemas import AssessmentCreateRequest, AssessmentResponse, AuthenticatedActor; print('schemas OK')"

echo "== Verify dependencies import =="
python -c "from app.core.dependencies import get_db_user, get_current_actor; print('dependencies OK')"

echo "== Run backend test suite =="
python -m pytest tests/ -v

echo "== Backend verification complete =="
