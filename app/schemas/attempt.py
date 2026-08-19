"""
Scenario Attempt Schema (Input Contract for Person 2 AI Coach)
Defines the submission data from Person 1 UI to Person 2 AI analysis engine.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.core.constants import ThreatCategory, DifficultyLevel


class ScenarioAttemptSchema(BaseModel):
    """User attempt payload passed to Person 2 AI Coach."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "USER001",
                "scenario_id": "SC001",
                "category": "phishing",
                "difficulty": 2,
                "scenario": "You receive an email from IT-support@company-verify.com claiming your password expires in 15 minutes.",
                "options": [
                    "Click the link immediately",
                    "Verify the sender address and contact internal IT support directly"
                ],
                "user_answer": "Click the link immediately",
                "correct_answer": "Verify the sender address and contact internal IT support directly",
                "user_reasoning": "It looked urgent and came from IT support so I wanted to fix it quickly."
            }
        }
    )

    user_id: str = Field(..., description="Unique user identifier e.g., USER001")
    scenario_id: str = Field(..., description="Unique scenario identifier e.g., SC001")
    category: ThreatCategory = Field(..., description="Threat category enum")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level 1-3")
    scenario: str = Field(..., description="Scenario context text")
    options: List[str] = Field(..., description="Available options presented")
    user_answer: str = Field(..., description="Option selected by user")
    correct_answer: str = Field(..., description="Correct option")
    user_reasoning: Optional[str] = Field(default="", description="User's explanation of why they chose this answer")
