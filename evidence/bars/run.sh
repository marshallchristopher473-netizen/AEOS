#!/usr/bin/env bash
# Prompt 3 hosted evidence run: checks C01..C30 against a hosted BARS deployment.
# Exit codes: 0 no FAIL · 1 one or more FAIL · 2 precondition unmet
#             3 fixture setup failed (sign-in/create/edit) · 4 credential found in evidence
set -uo pipefail
cd "$(dirname "$0")"
source ./env.sh
source ./lib.sh

FAILED=0
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-$(new_uuid | cut -c1-8)"
JAR_A="$TMP/a.jar"; JAR_B="$TMP/b.jar"; JAR_ANON="$TMP/anon.jar"
JAR_A_FRESH="$TMP/a-fresh.jar"; JAR_B_REVOKED="$TMP/b-revoked.jar"
A_HASH="$(email_hash "$TESTER_A_EMAIL")"; B_HASH="$(email_hash "$TESTER_B_EMAIL")"

# Evidence is bound to one run: clear every record from earlier runs first.
rm -f checks/C[0-9][0-9].json checks/C[0-9][0-9].body.json checks/run.json checks/restart-fixture.json

write_run_meta() {
  jq -n --arg run_id "$RUN_ID" --arg base "$BASE" --arg started "$STARTED" \
        --arg finished "${1:-}" --arg a "${A_HASH:0:16}" --arg b "${B_HASH:0:16}" \
        --argjson failed "$FAILED" \
        '{run_id:$run_id,base:$base,started_at:$started,finished_at:$finished,
          tester_a_sha256_prefix:$a,tester_b_sha256_prefix:$b,failed:$failed}' > checks/run.json
}
fatal() { echo "FATAL: $*" >&2; write_run_meta "aborted: $*"; exit 3; }

STARTED="$(date -u +%FT%TZ)"
write_run_meta

echo "== Prompt 3 hosted evidence run =="
echo "RUN_ID=$RUN_ID"
echo "BASE=$BASE"
echo "A=${A_HASH:0:16}  B=${B_HASH:0:16}"
echo

# --- sign-in both testers -------------------------------------------------
http POST /api/auth/signin "$JAR_A" "$(creds_json "$TESTER_A_EMAIL" "$TESTER_A_PIN")"
[[ "$HTTP_STATUS" == 200 ]] || fatal "tester A cannot sign in ($HTTP_STATUS)"
http POST /api/auth/signin "$JAR_B" "$(creds_json "$TESTER_B_EMAIL" "$TESTER_B_PIN")"
[[ "$HTTP_STATUS" == 200 ]] || fatal "tester B cannot sign in ($HTTP_STATUS)"
echo "sign-in: A ok, B ok"
echo

# --- R3 authenticate every protected request ------------------------------
http GET  /api/tasks     "$JAR_ANON"; record C01 "anonymous list tasks"   R3 GET  /api/tasks     anonymous 401 "$HTTP_STATUS" "$HTTP_MS"
http GET  /api/tasks/abc "$JAR_ANON"; record C02 "anonymous read task"    R3 GET  /api/tasks/:id anonymous 401 "$HTTP_STATUS" "$HTTP_MS"
http POST /api/tasks     "$JAR_ANON" '{"title":"x","output":"y"}'
                                      record C03 "anonymous create task"  R3 POST /api/tasks     anonymous 401 "$HTTP_STATUS" "$HTTP_MS"

# --- R2 restrict enrollment ----------------------------------------------
http POST /api/auth/signin "$JAR_ANON" "$(creds_json "nobody-$RUN_ID@example.test" "000000")"
record C04 "unknown email rejected" R2 POST /api/auth/signin anonymous 401 "$HTTP_STATUS" "$HTTP_MS"
WRONG_PIN="000000"; [[ "$TESTER_A_PIN" == "$WRONG_PIN" ]] && WRONG_PIN="999999"
http POST /api/auth/signin "$JAR_ANON" "$(creds_json "$TESTER_A_EMAIL" "$WRONG_PIN")"
record C05 "wrong PIN rejected"     R2 POST /api/auth/signin anonymous 401 "$HTTP_STATUS" "$HTTP_MS"

# --- A creates the fixture ------------------------------------------------
http POST /api/tasks "$JAR_A" '{"title":"Prompt3 fixture","output":"a one-page opener outline"}'
[[ "$HTTP_STATUS" == 201 ]] || fatal "A cannot create task ($HTTP_STATUS)"
A_TASK=$(jq -r '.id // empty' "$HTTP_BODY")
A_VER=$(jq -r '.version // empty' "$HTTP_BODY")
[[ -n "$A_TASK" && "$A_VER" =~ ^[0-9]+$ ]] || fatal "create response lacks id or integer version"
echo "fixture: A task = $A_TASK (v$A_VER)"
echo

# --- R4/R5/R8 IDOR: B cannot read/change/delete A's task ------------------
# Positive control for C06-C11 is C15: A can still read the task, unchanged.
http GET    "/api/tasks/$A_TASK" "$JAR_B"
record C06 "B reads A's task by id"          R4 GET    /api/tasks/:id B 404 "$HTTP_STATUS" "$HTTP_MS"
http PATCH  "/api/tasks/$A_TASK" "$JAR_B" "$(jq -nc --argjson v "$A_VER" '{title:"pwn",expectedVersion:$v}')"
record C07 "B edits A's task by id"          R5 PATCH  /api/tasks/:id B 404 "$HTTP_STATUS" "$HTTP_MS"
http DELETE "/api/tasks/$A_TASK" "$JAR_B"
record C08 "B deletes A's task by id"        R8 DELETE /api/tasks/:id B 404 "$HTTP_STATUS" "$HTTP_MS"
http POST   "/api/tasks/$A_TASK/focus/start"  "$JAR_B"
record C09 "B starts focus on A's task"      R5 POST   /focus/start   B 404 "$HTTP_STATUS" "$HTTP_MS"
http POST   "/api/tasks/$A_TASK/focus/finish" "$JAR_B"
record C10 "B finishes focus on A's task"    R5 POST   /focus/finish  B 404 "$HTTP_STATUS" "$HTTP_MS"
http POST   "/api/tasks/$A_TASK/reflection"   "$JAR_B" '{"body":"injected"}'
record C11 "B writes reflection on A's task" R5 POST   /reflection    B 404 "$HTTP_STATUS" "$HTTP_MS"

# --- R6 list isolation, with a positive control ---------------------------
# "absent" requires: B's list is a real array without A's task, AND A's own
# list contains it. An endpoint that always returns [] cannot pass.
http GET /api/tasks "$JAR_A"
a_has=$(jq -r --arg id "$A_TASK" 'if type=="array" then (map(.id) | index($id) != null) else "unparseable" end' "$HTTP_BODY" 2>/dev/null || echo unparseable)
http GET /api/tasks "$JAR_B"
b_has=$(jq -r --arg id "$A_TASK" 'if type=="array" then (map(.id) | index($id) != null) else "unparseable" end' "$HTTP_BODY" 2>/dev/null || echo unparseable)
if   [[ "$HTTP_STATUS" != 200 ]];   then actual="status-$HTTP_STATUS"
elif [[ "$b_has" == unparseable ]]; then actual="unparseable"
elif [[ "$b_has" == true ]];        then actual="present"
elif [[ "$a_has" != true ]];        then actual="control-failed"
else                                     actual="absent"; fi
record C12 "B list excludes A's task (A list includes it)" R6 GET /api/tasks B absent "$actual" "$HTTP_MS"

# --- random UUID probe ----------------------------------------------------
http GET "/api/tasks/$(new_uuid)" "$JAR_B"
record C13 "B reads nonexistent UUID" R4 GET /api/tasks/:id B 404 "$HTTP_STATUS" "$HTTP_MS"

# --- R9 browser-supplied owner is not authorization -----------------------
# B submits A's tester id as the owner. PASS requires the new task to belong to
# B: B can read it, A cannot.
http GET /api/me "$JAR_A"
A_ID=$(jq -r '.id // .tester.id // .user.id // empty' "$HTTP_BODY" 2>/dev/null || true)
if [[ "$HTTP_STATUS" != 200 || -z "$A_ID" ]]; then
  record_blocked C14 "spoofed owner id ignored" \
    "GET /api/me returned $HTTP_STATUS without an id, so A's tester id is unknown. Expose it or supply it, then rerun." R9
else
  http POST /api/tasks "$JAR_B" "$(jq -nc --arg o "$A_ID" '{title:"spoof",output:"x",testerId:$o,tester_id:$o,ownerId:$o}')"
  create_status=$HTTP_STATUS
  SPOOF_ID=$(jq -r '.id // empty' "$HTTP_BODY" 2>/dev/null || true)
  if [[ "$create_status" != 201 || -z "$SPOOF_ID" ]]; then
    actual="create-$create_status"
  else
    http GET "/api/tasks/$SPOOF_ID" "$JAR_A"; a_sees=$HTTP_STATUS
    http GET "/api/tasks/$SPOOF_ID" "$JAR_B"; b_sees=$HTTP_STATUS
    if   [[ "$a_sees" == 404 && "$b_sees" == 200 ]]; then actual="owner=B"
    elif [[ "$a_sees" == 200 ]];                     then actual="owner=A"
    else actual="a=$a_sees,b=$b_sees"; fi
  fi
  record C14 "spoofed owner id ignored" R9 POST /api/tasks B owner=B "$actual" "$HTTP_MS"
fi

# --- R11/R21 persistence --------------------------------------------------
http GET "/api/tasks/$A_TASK" "$JAR_A"
title_now=$(jq -r '.title // empty' "$HTTP_BODY" 2>/dev/null || true)
if [[ "$HTTP_STATUS" == 200 && "$title_now" == "Prompt3 fixture" ]]; then actual=200
elif [[ "$HTTP_STATUS" == 200 ]]; then actual="200-but-modified"
else actual="$HTTP_STATUS"; fi
record C15 "A reads own task, unchanged by B" R11 GET /api/tasks/:id A 200 "$actual" "$HTTP_MS"

# Sign A out, then in with a fresh cookie jar: the server must derive identity
# from the new session and still find the record.
http POST /api/auth/signout "$JAR_A"
http POST /api/auth/signin "$JAR_A_FRESH" "$(creds_json "$TESTER_A_EMAIL" "$TESTER_A_PIN")"
[[ "$HTTP_STATUS" == 200 ]] || fatal "A cannot sign back in ($HTTP_STATUS)"
http GET "/api/tasks/$A_TASK" "$JAR_A_FRESH"
record C16 "A's task survives sign-out/in" R21 GET /api/tasks/:id A 200 "$HTTP_STATUS" "$HTTP_MS"

# Server-confirmed round-trip: PATCH then GET must reflect the write and return
# a higher version (the API counterpart of the UI "Saved" badge).
http PATCH "/api/tasks/$A_TASK" "$JAR_A_FRESH" \
  "$(jq -nc --argjson v "$A_VER" '{title:"Prompt3 fixture (edited)",expectedVersion:$v}')"
[[ "$HTTP_STATUS" == 200 ]] || fatal "A cannot edit own task ($HTTP_STATUS)"
A_VER2=$(jq -r '.version // empty' "$HTTP_BODY")
http GET "/api/tasks/$A_TASK" "$JAR_A_FRESH"
server_title=$(jq -r '.title // empty' "$HTTP_BODY" 2>/dev/null || true)
if [[ "$server_title" == "Prompt3 fixture (edited)" && "$A_VER2" =~ ^[0-9]+$ ]] && (( A_VER2 > A_VER )); then
  actual="roundtrip-ok"
else
  actual="roundtrip-bad"
fi
record C17 "server-confirmed PATCH round-trip" R13 PATCH /api/tasks/:id A roundtrip-ok "$actual" "$HTTP_MS"

# --- R17 stale-tab detection ---------------------------------------------
http PATCH "/api/tasks/$A_TASK" "$JAR_A_FRESH" \
  "$(jq -nc --argjson v "$A_VER" '{title:"stale",expectedVersion:$v}')"
record C18 "stale version rejected 409" R17 PATCH /api/tasks/:id A 409 "$HTTP_STATUS" "$HTTP_MS"

# --- R20 revoked access ---------------------------------------------------
cp "$JAR_B" "$JAR_B_REVOKED"
http POST /api/auth/signout "$JAR_B"
http GET /api/tasks "$JAR_B_REVOKED"
record C19 "revoked session cookie rejected" R20 GET /api/tasks B-revoked 401 "$HTTP_STATUS" "$HTTP_MS"

# --- R16 duplicate submission --------------------------------------------
# Five parallel POSTs carrying the SAME body and the SAME Idempotency-Key, as a
# double-clicking client would send. Exactly one record may result.
http GET /api/tasks "$JAR_A_FRESH"; before=$(body_array_len)
IDEM_KEY="$(new_uuid)"
DUP_BODY="$TMP/dup-body.json"
jq -nc --arg t "dup-$RUN_ID" '{title:$t,output:"dup"}' > "$DUP_BODY"
: > "$TMP/dup.status"
for i in 1 2 3 4 5; do
  cp "$JAR_A_FRESH" "$TMP/jar.$i"
  ( curl -sS -o /dev/null -w '%{http_code}\n' --max-time 30 -X POST \
      -b "$TMP/jar.$i" -c "$TMP/jar.$i" \
      -H 'Content-Type: application/json' -H "Idempotency-Key: $IDEM_KEY" \
      --data-binary "@$DUP_BODY" "$BASE/api/tasks" >> "$TMP/dup.status" ) &
done
wait
http GET /api/tasks "$JAR_A_FRESH"; after=$(body_array_len)
if [[ "$before" =~ ^[0-9]+$ && "$after" =~ ^[0-9]+$ ]]; then actual=$((after - before)); else actual="unparseable"; fi
dup_ms=$HTTP_MS
jq -n --arg before "$before" --arg after "$after" --rawfile st "$TMP/dup.status" \
  '{idempotency_key_sent:true,parallel_posts:5,
    post_statuses:($st | split("\n") | map(select(length>0))),
    list_length_before:$before,list_length_after:$after}' > "$HTTP_BODY"
record C20 "duplicate POSTs create one record" R16 POST /api/tasks A 1 "$actual" "$dup_ms"

# --- R21 restart fixture (kept; C21 deletes the other one) ----------------
RESTART_TITLE="Prompt3 restart fixture $RUN_ID"
http POST /api/tasks "$JAR_A_FRESH" "$(jq -nc --arg t "$RESTART_TITLE" '{title:$t,output:"must survive a restart"}')"
[[ "$HTTP_STATUS" == 201 ]] || fatal "A cannot create the restart fixture ($HTTP_STATUS)"
KEEP_TASK=$(jq -r '.id // empty' "$HTTP_BODY")
[[ -n "$KEEP_TASK" ]] || fatal "restart fixture response lacks id"
jq -n --arg run_id "$RUN_ID" --arg id "$KEEP_TASK" --arg title "$RESTART_TITLE" \
  '{run_id:$run_id,task_id:$id,title:$title}' > checks/restart-fixture.json

# --- R8 deletion ----------------------------------------------------------
http DELETE "/api/tasks/$A_TASK" "$JAR_A_FRESH"
record C21 "A deletes own task"   R8 DELETE /api/tasks/:id A 200 "$HTTP_STATUS" "$HTTP_MS"
http GET "/api/tasks/$A_TASK" "$JAR_A_FRESH"
record C22 "deleted task is gone" R8 GET    /api/tasks/:id A 404 "$HTTP_STATUS" "$HTTP_MS"

# --- R11 preference isolation, with a positive control --------------------
http PUT /api/preferences "$JAR_A_FRESH" '{"focusMinutes":40,"breakMinutes":7,"timezone":"America/New_York","reducedMotion":false}'
record C23 "A sets preferences" R11 PUT /api/preferences A 200 "$HTTP_STATUS" "$HTTP_MS"
http GET /api/preferences "$JAR_A_FRESH"; a_fm=$(jq -r '.focusMinutes // empty' "$HTTP_BODY" 2>/dev/null || true)
http POST /api/auth/signin "$JAR_B" "$(creds_json "$TESTER_B_EMAIL" "$TESTER_B_PIN")"
[[ "$HTTP_STATUS" == 200 ]] || fatal "B cannot sign back in ($HTTP_STATUS)"
http GET /api/preferences "$JAR_B"; b_fm=$(jq -r '.focusMinutes // empty' "$HTTP_BODY" 2>/dev/null || true)
if   [[ "$HTTP_STATUS" != 200 ]]; then actual="status-$HTTP_STATUS"
elif [[ "$a_fm" != 40 ]];         then actual="control-failed"
elif [[ "$b_fm" == 40 ]];         then actual="leaked"
else                                   actual="isolated"; fi
record C24 "B preferences not affected by A" R11 GET /api/preferences B isolated "$actual" "$HTTP_MS"

# --- items HTTP cannot prove ---------------------------------------------
record_notrun C25 "export ownership" \
  "No export endpoint exists in this build. If one is added, it must enforce tester_id." R7
record_notrun C26 "tester has no editor/secret access" \
  "Verify in the Replit dashboard, not over HTTP." R10
record_notrun C27 "browser storage not authoritative" \
  "Inspect localStorage in DevTools; it must hold no mirrored task state." R12
record_notrun C28 "unsaved input preserved on error" "Requires UI fault injection." R14
record_notrun C29 "safe retry after failed write"    "Requires UI fault injection." R15
record_blocked C30 "records survive app restart" \
  "Operator must restart the Replit deployment, then run restart-check.sh (fixture $KEEP_TASK)." R21

# --- the evidence must not contain credentials -----------------------------
leaks=$(grep -rlF -e "$TESTER_A_EMAIL" -e "$TESTER_B_EMAIL" checks/ 2>/dev/null; \
        grep -rlE '"pin"[[:space:]]*:' checks/ 2>/dev/null)
if [[ -n "$leaks" ]]; then
  echo "SANITIZATION FAILURE: tester email or PIN found in:" >&2
  echo "$leaks" | sort -u >&2
  echo "Do not share or commit checks/ from this run." >&2
  write_run_meta "sanitization-failure"
  exit 4
fi

write_run_meta "$(date -u +%FT%TZ)"
echo
echo "checks written to $EVID/checks/"
echo "FAILED=$FAILED"
exit $(( FAILED > 0 ? 1 : 0 ))
