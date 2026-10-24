#!/usr/bin/env bash
# HTTP and recording helpers. Requires env.sh to be sourced first.

# http METHOD PATH JAR [BODY_JSON] [EXTRA_HEADER]
# Runs in the current shell (never call it inside $(...)) and sets:
#   HTTP_STATUS  status code, or 000 on a transport failure
#   HTTP_MS      elapsed milliseconds
#   $HTTP_BODY   response body
# The request body goes through a temp file, so credentials never appear in argv.
http() {
  local method=$1 path=$2 jar=$3 body=${4:-} header=${5:-}
  local -a args=(-sS -o "$HTTP_BODY" -w '%{http_code}\t%{time_total}'
                 --max-time 30 -X "$method" -b "$jar" -c "$jar")
  if [[ -n "$body" ]]; then
    printf '%s' "$body" > "$TMP/req.json"
    args+=(-H 'Content-Type: application/json' --data-binary "@$TMP/req.json")
  fi
  [[ -n "$header" ]] && args+=(-H "$header")
  : > "$HTTP_BODY"
  touch "$jar"
  local out
  out="$(curl "${args[@]}" "$BASE$path")" || true
  rm -f "$TMP/req.json"
  HTTP_STATUS="${out%%$'\t'*}"
  [[ "$HTTP_STATUS" =~ ^[0-9]{3}$ ]] || HTTP_STATUS=000
  local secs=0
  [[ "$out" == *$'\t'* ]] && secs="${out##*$'\t'}"
  HTTP_MS=$(awk -v s="$secs" 'BEGIN{printf "%d", s*1000}')
}

# record ID NAME REQ METHOD PATH ACTOR EXPECTED ACTUAL MS
record() {
  local id=$1 name=$2 req=$3 method=$4 path=$5 actor=$6 expected=$7 actual=$8 ms=${9:-0}
  local status; [[ "$actual" == "$expected" ]] && status=PASS || status=FAIL
  jq -n --arg id "$id" --arg name "$name" --arg req "$req" \
        --arg method "$method" --arg path "$path" --arg actor "$actor" \
        --arg expected "$expected" --arg actual "$actual" --arg status "$status" \
        --argjson ms "$ms" --arg ts "$(date -u +%FT%TZ)" \
        --arg run_id "${RUN_ID:-}" --arg evidence "checks/$id.body.json" \
        '{id:$id,name:$name,requirement:$req,method:$method,path:$path,
          actor:$actor,expected:$expected,actual:$actual,elapsed_ms:$ms,
          status:$status,evidence:$evidence,run_id:$run_id,timestamp:$ts}' \
    > "$EVID/checks/$id.json"
  cp "$HTTP_BODY" "$EVID/checks/$id.body.json"
  printf '%-4s %-46s exp=%-12s got=%-12s %s\n' "$id" "$name" "$expected" "$actual" "$status"
  [[ "$status" == FAIL ]] && FAILED=$((FAILED+1))
  return 0
}

# _record_open ID NAME REQ STATUS REASON
_record_open() {
  jq -n --arg id "$1" --arg name "$2" --arg req "$3" --arg status "$4" \
        --arg reason "$5" --arg run_id "${RUN_ID:-}" --arg ts "$(date -u +%FT%TZ)" \
        '{id:$id,name:$name,requirement:$req,status:$status,reason:$reason,
          run_id:$run_id,timestamp:$ts,evidence:null,expected:null,actual:null}' \
    > "$EVID/checks/$1.json"
  printf '%-4s %-46s %-8s (%s)\n' "$1" "$2" "$4" "$5"
}

# record_blocked ID NAME REASON REQ
record_blocked() { _record_open "$1" "$2" "$4" BLOCKED "$3"; }
# record_notrun ID NAME REASON REQ
record_notrun()  { _record_open "$1" "$2" "$4" "NOT RUN" "$3"; }

# Count elements of the JSON array in $HTTP_BODY, or print "unparseable".
# A non-array is never treated as empty: that would turn a broken endpoint into a PASS.
body_array_len() {
  jq -e 'if type == "array" then length else error("not an array") end' "$HTTP_BODY" 2>/dev/null \
    || echo unparseable
}
