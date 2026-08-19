"""
Personalization Service Interface (Person 3 Ownership)
Determines next scenario recommendations based on user risk profiles and weakness trends.
"""

from typing import Tuple
from app.schemas.risk import RiskProfileSchema
from app.core.constants import ThreatCategory, DifficultyLevel


class PersonalizationService:
    """Service recommending adaptive learning pathways."""

    def get_next_recommended_training(
        self, profile: RiskProfileSchema
    ) -> Tuple[ThreatCategory, DifficultyLevel, str]:
        """Return (category, difficulty, rationale) for next training iteration."""
        category = profile.recommended_next_category
        difficulty = profile.recommended_next_difficulty
        reason = f"Adaptive retraining targeting {category.value} based on current risk level ({profile.risk_level.value})."
        return category, difficulty, reason
