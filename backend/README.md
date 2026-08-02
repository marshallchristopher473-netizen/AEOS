# AEOS Backend

This directory contains the initial FastAPI backend scaffold for the AEOS Intervention Intelligence Platform MVP.

## Structure
- app/main.py: application entrypoint
- app/api/health.py: health endpoint
- app/api/assessments.py: assessment analysis endpoint placeholder
- app/core/config.py: environment configuration
- app/models/schemas.py: shared request/response schemas

## Run locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints
- GET /health
- POST /assessments/analyze
fix: add required-env validation to config.py
docs: add environment setup section to README