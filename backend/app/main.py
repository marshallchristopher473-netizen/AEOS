from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ALLOWED_ORIGINS
from app.api.health import router as health_router
from app.api.assessments import router as assessments_router
from app.api.assessment_results import router as assessment_results_router
from app.api.students import router as students_router
from app.api.intervention_plans import router as intervention_plans_router

app = FastAPI(
    title="AEOS Intervention Intelligence Platform API",
    version="0.1.0",
    description="MVP backend for assessment review and intervention planning workflows",
)

# The teacher portal runs on a different origin and authenticates with a
# Supabase bearer token, so browsers need an explicit CORS grant. Credentials
# (cookies) are not allowed: the API never reads them, and refusing them keeps
# an allowed origin from riding an ambient session.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health_router)
app.include_router(assessments_router)
app.include_router(assessment_results_router)
app.include_router(students_router)
app.include_router(intervention_plans_router)
