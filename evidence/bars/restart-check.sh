#!/usr/bin/env bash
# C30: run after restarting the hosted deployment. Reads the restart fixture
# that run.sh left behind (a task C21 does not delete) and checks it survived
# with its content intact.
set -uo pipefail
cd "$(dirname "$0")"
source ./env.sh
source ./lib.sh

FAILED=0
fixture=checks/restart-fixture.json
[[ -s "$fixture" ]] || { echo "No restart fixture. Run run.sh first." >&2; exit 2; }
RUN_ID=$(jq -r '.run_id' "$fixture")
task=$(jq -r '.task_id' "$fixture")
want_title=$(jq -r '.title' "$fixture")
run_base=$(jq -r '.base // empty' checks/run.json 2>/dev/null || true)
[[ -z "$run_base" || "$run_base" == "$BASE" ]] \
  || { echo "REFUSING: BASE ($BASE) differs from the run's BASE ($run_base)." >&2; exit 2; }

JAR="$TMP/restart.jar"
http POST /api/auth/signin "$JAR" "$(creds_json "$TESTER_A_EMAIL" "$TESTER_A_PIN")"
[[ "$HTTP_STATUS" == 200 ]] || { echo "sign-in after restart failed ($HTTP_STATUS)" >&2; exit 3; }
http GET "/api/tasks/$task" "$JAR"
got_title=$(jq -r '.title // empty' "$HTTP_BODY" 2>/dev/null || true)
if   [[ "$HTTP_STATUS" != 200 ]];        then actual="$HTTP_STATUS"
elif [[ "$got_title" != "$want_title" ]]; then actual="200-content-changed"
else                                          actual=200; fi
record C30 "records survive app restart" R21 GET /api/tasks/:id A 200 "$actual" "$HTTP_MS"
exit $(( FAILED > 0 ? 1 : 0 ))
