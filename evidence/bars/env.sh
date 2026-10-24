#!/usr/bin/env bash
# Prompt 3 preconditions. Sourced by run.sh and restart-check.sh.
# Deliberately sets no shell options: the caller owns `set`.
# Any unmet precondition exits 2 before anything is written to checks/.

refuse() { echo "REFUSING: $*" >&2; exit 2; }

for tool in curl jq; do
  command -v "$tool" >/dev/null 2>&1 || refuse "$tool is not installed."
done

[[ -n "${BASE:-}" ]]           || refuse "BASE must be set, e.g. https://aeos-bars.replit.app"
[[ -n "${TESTER_A_EMAIL:-}" ]] || refuse "TESTER_A_EMAIL must be set."
[[ -n "${TESTER_A_PIN:-}" ]]   || refuse "TESTER_A_PIN must be set."
[[ -n "${TESTER_B_EMAIL:-}" ]] || refuse "TESTER_B_EMAIL must be set."
[[ -n "${TESTER_B_PIN:-}" ]]   || refuse "TESTER_B_PIN must be set."

BASE="${BASE%/}"
[[ "$BASE" == https://* ]] || refuse "BASE must be an https:// hosted URL. Prompt 3 requires a hosted target."
_host="${BASE#https://}"; _host="${_host%%/*}"
case "$_host" in
  localhost|localhost:*|127.*|0.0.0.0|0.0.0.0:*|\[*|*.local|*.local:*)
    refuse "BASE points at a local address ($_host). Prompt 3 requires a hosted target." ;;
esac
unset _host

[[ "$(printf '%s' "$TESTER_A_EMAIL" | tr '[:upper:]' '[:lower:]')" != \
   "$(printf '%s' "$TESTER_B_EMAIL" | tr '[:upper:]' '[:lower:]')" ]] \
  || refuse "tester A and B must be distinct accounts."

EVID="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ATTEST="$EVID/environment.txt"
[[ -s "$ATTEST" ]] \
  || refuse "evidence/bars/environment.txt is missing or empty. Fill the R1 attestation (see environment.txt.example)."
grep -q '<[^>]*>' "$ATTEST" \
  && refuse "environment.txt still contains <placeholder> values. Replace every one."
grep -Eq '^database_is_shared_with_dev:[[:space:]]*no[[:space:]]*$' "$ATTEST" \
  || refuse "environment.txt must attest 'database_is_shared_with_dev: no' (Prompt 3 R1)."

mkdir -p "$EVID/checks"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HTTP_BODY="$TMP/body.json"
HTTP_STATUS=000
HTTP_MS=0

sha() {
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$1" | sha256sum | cut -d' ' -f1
  else
    printf '%s' "$1" | shasum -a 256 | cut -d' ' -f1
  fi
}
email_hash() { sha "$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"; }

new_uuid() {
  if [[ -r /proc/sys/kernel/random/uuid ]]; then
    cat /proc/sys/kernel/random/uuid
  elif command -v uuidgen >/dev/null 2>&1; then
    uuidgen | tr '[:upper:]' '[:lower:]'
  else
    echo "00000000-0000-4000-8000-$(date +%s%N | tail -c 13)"
  fi
}

# JSON sign-in body built by jq, so a PIN or email containing quotes is safe.
creds_json() { jq -nc --arg e "$1" --arg p "$2" '{email:$e,pin:$p}'; }
