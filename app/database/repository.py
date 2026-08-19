"""
Data access repository pattern interface for scenarios, attempts, and profiles.
"""

from typing import List, Optional
from app.schemas.scenario import ScenarioSchema
from app.schemas.risk import RiskProfileSchema


class BaseRepository:
    """Base repository interface."""
    
    def get_user_profile(self, user_id: str) -> Optional[RiskProfileSchema]:
        """Fetch user risk profile."""
        return None
        
    def save_user_profile(self, profile: RiskProfileSchema) -> bool:
        """Save updated user profile."""
        return True
