#!/usr/bin/env bash
# AEOS P0 security gate.
#
# This script is deliberately honest rather than aspirational: it runs what
# can actually be verified today, and prints a plain PASS/PENDING status per
# control so nobody mistakes "the script ran" for "P0 is complete." It exits
# non-zero only when something that IS implemented actually fails — never
# to punish a control that legitimately hasn't been built yet. Update the
# CONTROL CHECKS section as each control lands; do not delete a check
# because it currently reads PENDING.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT/backend"

if [ -d "../.venv" ]; then
  # shellcheck disable=SC1091
  source ../.venv/bin/activate
fi

FAIL=0

echo "== Running backend auth/actor unit tests =="
AUTH_TEST_TARGETS="tests/test_auth.py"
if [ -f "tests/test_dependencies.py" ]; then
  AUTH_TEST_TARGETS="$AUTH_TEST_TARGETS tests/test_dependencies.py"
fi
# shellcheck disable=SC2086
if python -m pytest $AUTH_TEST_TARGETS -v; then
  echo "auth/actor unit tests: PASS"
else
  echo "auth/actor unit tests: FAIL"
  FAIL=1
fi

echo
echo "== P0 control status (static checks) =="

check() {
  local label="$1" grep_expr="$2" file="$3" expect_present="$4"
  if grep -qE "$grep_expr" "$file" 2>/dev/null; then
    found=1
  else
    found=0
  fi
  if [ "$found" = "$expect_present" ]; then
    echo "PASS    - $label"
  else
    echo "PENDING - $label"
  fi
}

check "JWT audience verification enabled"  'verify_aud.: True' app/core/auth.py 1
check "JWT issuer verification enabled"    'verify_iss.: True' app/core/auth.py 1
check "get_current_actor exists"           'def get_current_actor' app/core/dependencies.py 1
check "students route requires auth"       'Depends\(get_current_actor\)' app/api/students.py 1
check "assessments route requires auth"    'Depends\(get_current_actor\)' app/api/assessments.py 1
check "intervention-plans route requires auth" 'Depends\(get_current_actor\)' app/api/intervention_plans.py 1

echo
echo "== Known gaps (informational — not a pass/fail check) =="
for f in app/api/students.py app/api/assessments.py app/api/intervention_plans.py; do
  if grep -q "get_supabase_admin_client" "$f" 2>/dev/null; then
    echo "  - $f still uses the service-role admin client for ordinary request handling"
  fi
done

echo
echo "== RLS status: NOT checked by this script =="
echo "RLS enablement/policy state can only be verified against a live Supabase"
echo "project (see backend/supabase/migrations/ for the versioned source of"
echo "truth, and reconcile against the live project before trusting either)."
echo "This script does not have network access to a live database by default."

echo
if [ "$FAIL" = "1" ]; then
  echo "== P0 security gate: FAIL (an implemented check actually failed) =="
  exit 1
fi
echo "== P0 security gate: ran cleanly. See PENDING items above — P0 is NOT complete until none remain. =="
