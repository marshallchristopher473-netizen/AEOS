#!/usr/bin/env bash
# End-to-end stack for the tenant-isolation harness (P0-01 / P0-02).
#
#   stack.sh fetch : download PostgREST into the work dir (checksum-verified)
#   stack.sh init  : new local-only keys + fresh database (destroys the previous one)
#   stack.sh up    : start PostgREST, the gateway, and the AEOS FastAPI app
#   stack.sh down  : stop those three processes (database keeps its data)
#
# Requires a disposable PostgreSQL 16 reachable at AEOS_TEST_DATABASE_URL.
# Never point this at a real or shared database: `init` drops and recreates
# the database named by AEOS_E2E_DB.
set -euo pipefail
H="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$(cd "$H/../.." && pwd)"
WORK="${AEOS_E2E_WORKDIR:-$H/.work}"
DB="${AEOS_E2E_DB:-aeos_e2e}"
PG_ADMIN="${AEOS_TEST_DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/postgres}"
PG_HOSTPORT="$(python3 -c 'import sys,urllib.parse as u; p=u.urlparse(sys.argv[1]); print("%s:%s" % (p.hostname or "localhost", p.port or 5432))' "$PG_ADMIN")"
AUTH_PW=e2e-local-only
PGRST_VERSION=v12.2.3
PGRST_SHA256=9f71269e61ac3a940281e93ff415760f5957e430e475ba4c3889f3ede7d5527c
mkdir -p "$WORK"

case "$1" in
fetch)
  if [ ! -x "$WORK/postgrest" ]; then
    curl -sSL -o "$WORK/postgrest.tar.xz" \
      "https://github.com/PostgREST/postgrest/releases/download/$PGRST_VERSION/postgrest-$PGRST_VERSION-linux-static-x64.tar.xz"
    echo "$PGRST_SHA256  $WORK/postgrest.tar.xz" | sha256sum -c -
    tar -xf "$WORK/postgrest.tar.xz" -C "$WORK"
  fi
  "$WORK/postgrest" --version
  ;;
init)
  python3 "$H/keys.py" "$WORK"
  AEOS_TEST_DATABASE_URL="$PG_ADMIN" python3 "$H/setup_db.py" "$BACKEND" "$DB" "$AUTH_PW"
  ;;
up)
  source "$WORK/env.sh"
  cat > "$WORK/postgrest.conf" <<EOF
db-uri = "postgresql://authenticator:$AUTH_PW@$PG_HOSTPORT/$DB"
db-schemas = "public"
db-anon-role = "anon"
jwt-secret = "$PGRST_JWT_SECRET"
server-host = "127.0.0.1"
server-port = 3001
EOF
  "$WORK/postgrest" "$WORK/postgrest.conf" > "$WORK/postgrest.log" 2>&1 & echo $! > "$WORK/postgrest.pid"
  python3 "$H/gateway.py" 54321 http://127.0.0.1:3001 "$WORK/jwks.json" > "$WORK/gateway.log" 2>&1 & echo $! > "$WORK/gateway.pid"
  ( cd "$BACKEND" && SUPABASE_URL=http://127.0.0.1:54321 SUPABASE_JWT_AUDIENCE=authenticated \
      exec python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > "$WORK/app.log" 2>&1 ) & echo $! > "$WORK/app.pid"
  for i in $(seq 1 40); do
    curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1 && curl -sf http://127.0.0.1:3001/ >/dev/null 2>&1 && break
    sleep 0.5
  done
  HEALTH="$(curl -s http://127.0.0.1:8000/health || true)"
  echo "health: $HEALTH"
  [ "$HEALTH" = '{"status":"ok","database":"connected"}' ] || { echo "stack not healthy" >&2; exit 1; }
  ;;
down)
  for p in app gateway postgrest; do
    [ -f "$WORK/$p.pid" ] && kill "$(cat "$WORK/$p.pid")" 2>/dev/null || true
    rm -f "$WORK/$p.pid"
  done
  # Fail loudly if anything still holds a stack port: a stale process would
  # silently serve the next run with old keys.
  for i in $(seq 1 20); do
    curl -s -o /dev/null http://127.0.0.1:8000/health || curl -s -o /dev/null http://127.0.0.1:3001/ || break
    sleep 0.5
  done
  if curl -s -o /dev/null http://127.0.0.1:8000/health || curl -s -o /dev/null http://127.0.0.1:3001/; then
    echo "stack ports still in use after down" >&2; exit 1
  fi
  ;;
*)
  echo "usage: $0 fetch|init|up|down" >&2; exit 2
  ;;
esac
