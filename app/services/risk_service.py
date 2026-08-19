"""
Risk Service Interface (Person 3 Ownership)
Business service for accessing risk profiles and computing risk scores.
"""

from typing import Optional
from app.schemas.risk import RiskProfileSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.risk.risk_engine import AdaptiveRiskEngine


class RiskService:
    """Service interfacing with the Adaptive Risk Engine."""

    def __init__(self, engine: Optional[AdaptiveRiskEngine] = None):
        self.engine = engine or AdaptiveRiskEngine()

    def get_user_risk_profile(self, user_id: str) -> RiskProfileSchema:
        """Fetch or initialize risk profile for a user."""
        return self.engine.get_or_create_profile(user_id)

    def record_analysis_and_update_risk(self, analysis: AIAnalysisSchema) -> RiskProfileSchema:
        """Process AI analysis and return updated deterministic risk profile."""
        return self.engine.process_ai_analysis(analysis)
