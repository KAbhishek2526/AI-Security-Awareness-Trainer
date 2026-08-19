"""
AI Analysis Domain Model (Person 2 Ownership)
Internal representation of LLM analysis and feedback.
"""

from typing import List
from dataclasses import dataclass, field
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel


@dataclass
class AIAnalysisModel:
    """Internal AI evaluation entity model."""
    analysis_id: str
    attempt_id: str
    user_id: str
    scenario_id: str
    category: ThreatCategory
    is_correct: bool
    assessed_risk: RiskLevel
    identified_weaknesses: List[str] = field(default_factory=list)
    explanation: str = ""
    learning_points: List[str] = field(default_factory=list)
    recommended_topic: Optional[ThreatCategory] = None
    recommended_difficulty: Optional[DifficultyLevel] = None
    recommendation_reason: str = ""
