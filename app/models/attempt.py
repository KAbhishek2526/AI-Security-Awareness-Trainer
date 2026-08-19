"""
Scenario Attempt Domain Model
Used to store historical user responses for scoring and telemetry.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from app.core.constants import ThreatCategory, DifficultyLevel


@dataclass
class ScenarioAttemptModel:
    """Internal user attempt entity model."""
    attempt_id: str
    user_id: str
    scenario_id: str
    category: ThreatCategory
    difficulty: DifficultyLevel
    user_answer: str
    correct_answer: str
    is_correct: bool
    user_reasoning: Optional[str] = ""
    timestamp: datetime = datetime.utcnow()
