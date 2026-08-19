"""
Adaptive Risk Engine (Person 3 Ownership)
Coordinates scoring, risk classification, and profile history.
"""

from typing import Dict, Optional
from app.schemas.risk import RiskProfileSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.risk.profile import UserProfileManager


class AdaptiveRiskEngine:
    """Core risk engine owned by Person 3."""

    def __init__(self):
        self._profiles: Dict[str, RiskProfileSchema] = {}

    def get_or_create_profile(self, user_id: str) -> RiskProfileSchema:
        """Get existing profile or initialize new default profile."""
        if user_id not in self._profiles:
            self._profiles[user_id] = UserProfileManager.create_default_profile(user_id)
        return self._profiles[user_id]

    def process_ai_analysis(self, analysis: AIAnalysisSchema) -> RiskProfileSchema:
        """Incorporate AI analysis into deterministic user risk profile."""
        profile = self.get_or_create_profile(analysis.user_id)
        updated_profile = UserProfileManager.update_profile_with_analysis(profile, analysis)
        self._profiles[analysis.user_id] = updated_profile
        return updated_profile
