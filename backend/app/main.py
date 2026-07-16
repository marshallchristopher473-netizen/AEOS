from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.assessments import router as assessments_router
from app.api.students import router as students_router

app = FastAPI(
    title="AEOS Intervention Intelligence Platform API",
    version="0.1.0",
    description="MVP backend for assessment review and intervention planning workflows",
)

app.include_router(health_router)
app.include_router(assessments_router)
app.include_router(students_router)
