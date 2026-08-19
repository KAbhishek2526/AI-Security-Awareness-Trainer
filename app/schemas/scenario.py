"""
Scenario Schema (Person 1 Contract)
Defines the schema for cybersecurity threat scenarios.
"""

from typing import List
from pydantic import BaseModel, Field, ConfigDict
from app.core.constants import ThreatCategory, DifficultyLevel


class ScenarioSchema(BaseModel):
    """Cybersecurity threat scenario definition."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scenario_id": "SC001",
                "title": "Urgent Password Reset Request",
                "category": "phishing",
                "difficulty": 2,
                "description": "You receive an email from IT-support@company-verify.com claiming your email password expires in 15 minutes.",
                "prompt": "What is the safest action to take?",
                "options": [
                    "Click the link immediately and update your password",
                    "Verify the sender address and contact internal IT support directly",
                    "Forward the email to all colleagues to warn them",
                    "Ignore it completely without reporting"
                ],
                "correct_answer": "Verify the sender address and contact internal IT support directly",
                "explanation": "Official IT departments do not use external domains or mandate immediate password changes via unverified links.",
                "tags": ["phishing", "email", "urgency"]
            }
        }
    )

    scenario_id: str = Field(..., description="Unique scenario identifier e.g., SC001")
    title: str = Field(..., description="Short descriptive title of the scenario")
    category: ThreatCategory = Field(..., description="Threat category enum")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level 1-3")
    description: str = Field(..., description="Background story or scenario context")
    prompt: str = Field(..., description="Specific question or decision presented to user")
    options: List[str] = Field(..., min_length=2, description="Available choice options")
    correct_answer: str = Field(..., description="The correct answer choice text or index")
    explanation: str = Field(..., description="Standard static explanation of the correct choice")
    tags: List[str] = Field(default_factory=list, description="Metadata tags e.g., ['email', 'urgency']")
