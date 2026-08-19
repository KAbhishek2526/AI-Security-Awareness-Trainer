"""Module 3: Adaptive Risk & Personalization Engine for AI Human Firewall."""

from risk.models import (
    AIAnalysisInput,
    CANONICAL_CATEGORIES,
    CATEGORY_MAX_DIFFICULTIES,
    CategoryType,
    EnterpriseMetrics,
    ImprovementMetrics,
    INITIAL_CATEGORY_SCORE,
    RiskLevelType,
    ScenarioAttemptInput,
    ScenarioDefinition,
    TrainingRecommendation,
    UserProfile,
)
from risk.profile import (
    get_enterprise_metrics,
    get_improvement,
    get_user_profile,
    load_scenarios,
    recommend_next_training,
    record_attempt,
)
from risk.scoring import (
    calculate_overall_score,
    classify_risk,
    clamp_score,
    create_initial_scores,
    get_weakest_category,
    update_category_score,
)

__all__ = [
    # Core API for Module 1, 2, 4
    "record_attempt",
    "get_user_profile",
    "get_weakest_category",
    "recommend_next_training",
    "get_improvement",
    "get_enterprise_metrics",
    # Scoring & Math helpers
    "classify_risk",
    "calculate_overall_score",
    "update_category_score",
    "clamp_score",
    "create_initial_scores",
    "load_scenarios",
    # Data Models & Constants
    "UserProfile",
    "ScenarioAttemptInput",
    "AIAnalysisInput",
    "TrainingRecommendation",
    "ImprovementMetrics",
    "EnterpriseMetrics",
    "ScenarioDefinition",
    "CANONICAL_CATEGORIES",
    "CATEGORY_MAX_DIFFICULTIES",
    "INITIAL_CATEGORY_SCORE",
    "CategoryType",
    "RiskLevelType",
]
