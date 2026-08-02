#!/bin/bash
set -e

echo "Setting up AEOS FastAPI backend..."

mkdir -p backend/app backend/tests
cd backend

if [ ! -f requirements.txt ]; then
  cat > requirements.txt <<'EOF'
fastapi==0.115.0
uvicorn[standard]==0.30.0
pydantic==2.8.3
python-dotenv==1.0.1
httpx==0.27.0
supabase==2.5.0
EOF
fi

mkdir -p app/api app/core app/models app/services

cat > app/main.py <<'EOF'
from fastapi import FastAPI

app = FastAPI(title="AEOS API", version="0.1.0")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "aeos-backend"}
EOF

cat > app/api/__init__.py <<'EOF'
EOF

cat > app/core/__init__.py <<'EOF'
EOF

cat > app/models/__init__.py <<'EOF'
EOF

cat > app/services/__init__.py <<'EOF'
EOF

cat > .env.example <<'EOF'
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
EOF

cat > README.md <<'EOF'
# AEOS Backend

FastAPI backend for the AEOS MVP.

## Run locally

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOF

echo "Backend scaffold created."
echo "Install dependencies with: pip install -r backend/requirements.txt"
docs: expand .env.example with security notes and future frontend vars