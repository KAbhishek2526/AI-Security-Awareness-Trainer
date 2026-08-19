"""
Risk Profile & Scoring Schema (Person 3 Contract)
Defines user security profile, risk scores, and weakness tracking.
"""

from typing import List, Dict
from pydantic import BaseModel, Field, ConfigDict
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel


class CategoryScoreSchema(BaseModel):
    """Security awareness score for a single threat category."""
    category: ThreatCategory = Field(..., description="Threat category")
    score: float = Field(..., ge=0.0, le=100.0, description="Awareness score (0-100)")
    attempts_count: int = Field(default=0, ge=0, description="Total attempts in this category")
    correct_count: int = Field(default=0, ge=0, description="Correct attempts count")


class RiskProfileSchema(BaseModel):
    """Deterministic security profile and risk classification for a user."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "USER001",
                "overall_score": 65.5,
                "risk_level": "medium",
                "category_scores": {
                    "phishing": {
                        "category": "phishing",
                        "score": 50.0,
                        "attempts_count": 4,
                        "correct_count": 2
                    },
                    "password_security": {
                        "category": "password_security",
                        "score": 80.0,
                        "attempts_count": 5,
                        "correct_count": 4
                    }
                },
                "top_weaknesses": ["urgency_bias", "mfa_fatigue"],
                "recommended_next_category": "phishing",
                "recommended_next_difficulty": 2,
                "total_attempts": 9,
                "improvement_rate": 15.5
            }
        }
    )

    user_id: str = Field(..., description="User ID")
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall security awareness score (0-100)")
    risk_level: RiskLevel = Field(..., description="Deterministic risk classification: low, medium, high")
    category_scores: Dict[str, CategoryScoreSchema] = Field(..., description="Map of category names to category scores")
    top_weaknesses: List[str] = Field(default_factory=list, description="Top identified user weaknesses across all attempts")
    recommended_next_category: ThreatCategory = Field(..., description="Category recommended for next training session")
    recommended_next_difficulty: DifficultyLevel = Field(..., description="Difficulty level recommended for next session")
    total_attempts: int = Field(default=0, ge=0, description="Total completed scenarios")
    improvement_rate: float = Field(default=0.0, description="Percentage improvement over baseline score")
