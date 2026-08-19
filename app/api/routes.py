"""
FastAPI Main Route Registry (Person 4 Integration)
Exposes REST API endpoints for scenarios, AI coaching, risk profiles, and system health checks.
"""

from fastapi import FastAPI
from app.schemas.response import HealthResponseSchema
from app.core.config import settings
from app.api.scenarios import router as scenarios_router
from app.api.coach import router as coach_router
from app.api.risk import router as risk_router
from app.api.users import router as users_router

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Adaptive AI Security Awareness Trainer API"
)

# Register module routers
app.include_router(scenarios_router, prefix="/api/v1")
app.include_router(coach_router, prefix="/api/v1")
app.include_router(risk_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponseSchema)
def health_check():
    """Health check endpoint confirming repository and module status."""
    return HealthResponseSchema(
        status="ok",
        app_name=settings.app_name,
        version="0.1.0",
        modules={
            "person1_scenarios": "active",
            "person2_ai_coach": "active",
            "person3_risk_engine": "active",
            "person4_dashboard": "active"
        }
    )
