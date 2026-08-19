"""
User Profile Domain Model (Person 3 Ownership)
Internal representation of user risk profile and training history.
"""

from typing import Dict, List
from dataclasses import dataclass, field
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel


@dataclass
class CategoryScoreModel:
    """Internal category score model."""
    category: ThreatCategory
    score: float
    attempts_count: int = 0
    correct_count: int = 0


@dataclass
class UserProfileModel:
    """Internal user risk profile model."""
    user_id: str
    overall_score: float = 100.0
    risk_level: RiskLevel = RiskLevel.LOW
    category_scores: Dict[str, CategoryScoreModel] = field(default_factory=dict)
    top_weaknesses: List[str] = field(default_factory=list)
    recommended_next_category: ThreatCategory = ThreatCategory.PHISHING
    recommended_next_difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    total_attempts: int = 0
    improvement_rate: float = 0.0
