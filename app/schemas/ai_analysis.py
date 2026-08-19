"""
AI Analysis Schema (Person 2 Contract)
Defines the output structure returned by Person 2 AI Coach after evaluating a scenario attempt.
"""

from typing import List
from pydantic import BaseModel, Field, ConfigDict
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel


class AnalysisDetailSchema(BaseModel):
    """Detailed breakdown of user's answer and reasoning."""
    correct: bool = Field(..., description="Whether user chose the correct answer")
    risk: RiskLevel = Field(..., description="Evaluated risk level: low, medium, high")
    weaknesses: List[str] = Field(default_factory=list, description="Identified cognitive/security weaknesses e.g., ['urgency_bias']")


class FeedbackDetailSchema(BaseModel):
    """Personalized feedback provided to the user."""
    explanation: str = Field(..., description="Detailed personalized explanation of why the choice was safe or unsafe")
    learning_points: List[str] = Field(default_factory=list, description="Actionable takeaways for future scenarios")


class PersonalizationRecommendationSchema(BaseModel):
    """Next step recommendations passed to Person 3 Personalization Engine."""
    recommended_topic: ThreatCategory = Field(..., description="Target category for retraining")
    recommended_difficulty: DifficultyLevel = Field(..., description="Target difficulty for next scenario")
    reason: str = Field(..., description="Rationale for retraining recommendation")


class AIAnalysisSchema(BaseModel):
    """Complete output contract from Person 2 AI Coach."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "USER001",
                "scenario_id": "SC001",
                "category": "phishing",
                "analysis": {
                    "correct": False,
                    "risk": "high",
                    "weaknesses": [
                        "urgency_bias",
                        "sender_not_verified"
                    ]
                },
                "feedback": {
                    "explanation": "You fell for the artificial urgency. Attackers create fake deadlines to bypass your critical thinking.",
                    "learning_points": [
                        "Always inspect email sender domains carefully.",
                        "Never log in through links sent in urgent unexpected emails."
                    ]
                },
                "personalization": {
                    "recommended_topic": "phishing",
                    "recommended_difficulty": 2,
                    "reason": "Reinforce phishing domain verification under artificial urgency."
                }
            }
        }
    )

    user_id: str = Field(..., description="User ID")
    scenario_id: str = Field(..., description="Scenario ID")
    category: ThreatCategory = Field(..., description="Threat category")
    analysis: AnalysisDetailSchema = Field(..., description="Core risk & weakness analysis")
    feedback: FeedbackDetailSchema = Field(..., description="Personalized feedback text & learning points")
    personalization: PersonalizationRecommendationSchema = Field(..., description="Next step recommendations")
