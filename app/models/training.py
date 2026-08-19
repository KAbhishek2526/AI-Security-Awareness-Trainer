"""
Training Domain Model
Tracks training recommendations, sessions, and baseline vs current progress.
"""

from typing import List
from dataclasses import dataclass, field
from datetime import datetime
from app.core.constants import ThreatCategory, DifficultyLevel


@dataclass
class TrainingRecommendationModel:
    """Internal training recommendation entity model."""
    recommendation_id: str
    user_id: str
    target_category: ThreatCategory
    target_difficulty: DifficultyLevel
    reason: str
    created_at: datetime = datetime.utcnow()
    completed: bool = False
