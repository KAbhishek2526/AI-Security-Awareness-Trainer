"""
Standard API & Health Response Schemas.
"""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class HealthResponseSchema(BaseModel):
    """System health response model."""
    status: str = Field(default="ok", description="Health status e.g., ok")
    app_name: str = Field(..., description="Application name")
    version: str = Field(default="0.1.0", description="App version")
    modules: Dict[str, str] = Field(
        default_factory=lambda: {
            "person1_scenarios": "ready",
            "person2_ai_coach": "ready",
            "person3_risk_engine": "ready",
            "person4_dashboard": "ready"
        },
        description="Status of individual system modules"
    )


class APIResponseSchema(BaseModel):
    """Generic API wrapper response model."""
    success: bool = Field(..., description="Success flag")
    message: str = Field(..., description="Status or error message")
    data: Optional[Any] = Field(default=None, description="Payload data")
