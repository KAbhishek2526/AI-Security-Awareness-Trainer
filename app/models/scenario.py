"""
Scenario Domain Model (Person 1 Ownership)
Used by Person 1 to represent internal scenario objects and metadata.
"""

from typing import List, Optional
from dataclasses import dataclass, field
from app.core.constants import ThreatCategory, DifficultyLevel


@dataclass
class ScenarioModel:
    """Internal scenario entity model."""
    scenario_id: str
    title: str
    category: ThreatCategory
    difficulty: DifficultyLevel
    description: str
    prompt: str
    options: List[str]
    correct_answer: str
    explanation: str
    tags: List[str] = field(default_factory=list)
