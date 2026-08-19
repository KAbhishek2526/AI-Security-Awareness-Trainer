"""
Pydantic schemas establishing integration contracts across module boundaries.
"""

from app.schemas.scenario import ScenarioSchema
from app.schemas.attempt import ScenarioAttemptSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.schemas.risk import RiskProfileSchema, CategoryScoreSchema
from app.schemas.response import HealthResponseSchema

__all__ = [
    "ScenarioSchema",
    "ScenarioAttemptSchema",
    "AIAnalysisSchema",
    "RiskProfileSchema",
    "CategoryScoreSchema",
    "HealthResponseSchema",
]
