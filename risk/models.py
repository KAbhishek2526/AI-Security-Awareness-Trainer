"""Data models and type definitions for Module 3 (Adaptive Risk & Personalization Engine)."""

from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator

# Canonical categories (ordered for deterministic tie-breaking)
CANONICAL_CATEGORIES = (
    "phishing",
    "social_engineering",
    "mfa_otp",
    "password_security",
    "data_protection",
    "ai_security",
)

CategoryType = Literal[
    "phishing",
    "social_engineering",
    "mfa_otp",
    "password_security",
    "data_protection",
    "ai_security",
]

RiskLevelType = Literal["low", "medium", "high"]

# Maximum available difficulty per category based on scenario inventory
CATEGORY_MAX_DIFFICULTIES: Dict[str, int] = {
    "phishing": 3,
    "social_engineering": 2,
    "mfa_otp": 2,
    "password_security": 2,
    "data_protection": 1,
    "ai_security": 2,
}

# Initial score for all categories
INITIAL_CATEGORY_SCORE: int = 70


class AIAnalysisInput(BaseModel):
    """Supporting AI analysis data from Module 2 (AI Security Coach)."""
    risk: Optional[str] = None
    weaknesses: List[str] = Field(default_factory=list)
    explanation: Optional[str] = None
    recommendation: Optional[str] = None
    next_category: Optional[str] = None


class ScenarioAttemptInput(BaseModel):
    """Input payload representing an attempt on a scenario from Module 1 / Module 2."""
    user_id: str
    scenario_id: str
    category: str
    difficulty: int
    user_answer: Optional[str] = None
    correct: bool
    scenario_risk: Optional[str] = None
    ai_analysis: Optional[Union[AIAnalysisInput, Dict]] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        v_clean = v.strip().lower()
        if v_clean not in CANONICAL_CATEGORIES:
            raise ValueError(f"Category '{v}' is not one of canonical categories: {CANONICAL_CATEGORIES}")
        return v_clean


class ScenarioDefinition(BaseModel):
    """Definition of a cybersecurity scenario."""
    scenario_id: str
    category: str
    difficulty: int
    scenario: str


class TrainingRecommendation(BaseModel):
    """Adaptive recommendation for the user's next training scenario."""
    category: str
    difficulty: int
    reason: str
    scenario_id: str


class ImprovementMetrics(BaseModel):
    """Improvement metrics comparing baseline to current score."""
    baseline_score: int
    current_score: int
    improvement: int


class UserProfile(BaseModel):
    """Comprehensive user profile structure consumed by Module 4 (Dashboard)."""
    user_id: str
    scores: Dict[str, int]
    overall_score: int
    risk_level: RiskLevelType
    attempts: int = 0
    correct_attempts: int = 0
    incorrect_attempts: int = 0
    weakest_category: str
    recommended_category: str
    recommended_difficulty: int
    baseline_score: int = INITIAL_CATEGORY_SCORE
    improvement: int = 0


class EnterpriseMetrics(BaseModel):
    """Aggregated organization-level awareness and risk metrics for Module 4."""
    total_users: int
    risk_distribution: Dict[str, int]  # e.g., {"high": 3, "medium": 8, "low": 14}
    average_score: int
    category_weaknesses: Dict[str, int]  # average score per category across all users
    most_common_weakness: str
    average_improvement: int
