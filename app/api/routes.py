"""
FastAPI Main Route Registry (Person 4 Ownership)
Exposes REST endpoints for health checks and API integration.
"""

from fastapi import FastAPI
from app.schemas.response import HealthResponseSchema
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Adaptive AI Security Awareness Trainer API"
)


@app.get("/health", response_model=HealthResponseSchema)
def health_check():
    """Health check endpoint confirming repository and module status."""
    return HealthResponseSchema(
        status="ok",
        app_name=settings.app_name,
        version="0.1.0",
        modules={
            "person1_scenarios": "ready",
            "person2_ai_coach": "ready",
            "person3_risk_engine": "ready",
            "person4_dashboard": "ready"
        }
    )
