#!/usr/bin/env bash
# Aggregate checks/C??.json into manifest.json and report.md.
# Needs no secrets: it reads only what run.sh recorded.
set -euo pipefail
cd "$(dirname "$0")"
command -v jq >/dev/null 2>&1 || { echo "jq is not installed." >&2; exit 2; }

shopt -s nullglob
records=(checks/C[0-9][0-9].json)
[[ ${#records[@]} -gt 0 && -s checks/run.json ]] || { echo "No check records. Run run.sh first." >&2; exit 2; }
[[ -s environment.txt ]] || { echo "environment.txt is missing." >&2; exit 2; }

checks_json=$(jq -s 'sort_by(.id)' "${records[@]}")
count() { jq --arg s "$1" '[.[] | select(.status == $s)] | length' <<<"$checks_json"; }
pass=$(count PASS); fail=$(count FAIL); blk=$(count BLOCKED); ntr=$(count "NOT RUN")

run_id=$(jq -r '.run_id' checks/run.json)
base=$(jq -r '.base' checks/run.json)
finished=$(jq -r '.finished_at' checks/run.json)
foreign=$(jq -r --arg r "$run_id" '[.[] | select(.run_id != $r) | .id] | join(", ")' <<<"$checks_json")
sha=$(grep -E '^deployed_git_sha:' environment.txt | cut -d: -f2- | xargs || true)
ts=$(date -u +%FT%TZ)

if   [[ -n "$foreign" ]];   then verdict="INVALID — records from another run: $foreign"
elif [[ "$finished" != 20* ]]; then verdict="INVALID — run did not complete ($finished)"
elif (( fail > 0 ));        then verdict="FAIL — pilot blocked"
elif (( blk > 0 ));         then verdict="BLOCKED — pilot blocked until closed"
elif (( ntr > 0 ));         then verdict="AUTOMATED PASS — $ntr manual item(s) still open"
else                             verdict="PASS"; fi

jq -n --arg base "$base" --arg env "$(cat environment.txt)" --arg sha "$sha" \
      --arg run_id "$run_id" --arg ts "$ts" --arg verdict "$verdict" \
      --argjson pass "$pass" --argjson fail "$fail" \
      --argjson blocked "$blk" --argjson notrun "$ntr" \
      --argjson checks "$checks_json" --slurpfile run checks/run.json \
  '{run_id:$run_id,base:$base,environment:$env,deployed_git_sha:$sha,
    report_generated_at:$ts,run:$run[0],verdict:$verdict,
    summary:{pass:$pass,fail:$fail,blocked:$blocked,not_run:$notrun},
    checks:$checks}' > manifest.json

{
  echo "# Prompt 3: hosted evidence report"
  echo
  echo "- Base: \`$base\`"
  echo "- Run ID: \`$run_id\`"
  echo "- Deployed SHA: \`${sha:-not recorded}\`"
  echo "- Report generated: $ts"
  echo "- **Verdict: $verdict**"
  echo "- **PASS $pass · FAIL $fail · BLOCKED $blk · NOT RUN $ntr**"
  echo
  echo "| ID | Req | Check | Status | Expected | Actual |"
  echo "| --- | --- | --- | --- | --- | --- |"
  jq -r '.[] | "| \(.id) | \(.requirement // "—") | \(.name) | \(.status) | \(.expected // "—") | \(.actual // .reason // "—") |"' <<<"$checks_json"
  echo
  echo "## Manual operator steps"
  echo
  echo "1. Restart the Replit deployment, then run \`evidence/bars/restart-check.sh\` and rerun this report (C30)."
  echo "2. In DevTools, confirm localStorage holds no task data (C27)."
  echo "3. In the UI, force a failed save (offline toggle) and confirm input is preserved (C28) and a retry is safe (C29)."
  echo "4. In Replit, confirm the tester account cannot open the project editor or Secrets (C26)."
} > report.md

echo "wrote manifest.json and report.md — $verdict"
