"""Unit tests verifying Pydantic schema validation for module contracts."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.schemas.scenario import ScenarioSchema
from app.schemas.attempt import ScenarioAttemptSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.schemas.risk import RiskProfileSchema
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel
from app.risk.scoring import DeterministicRiskScorer


def test_scenario_schema_validation():
    """Verify ScenarioSchema validates correctly."""
    scenario = ScenarioSchema(
        scenario_id="SC001",
        title="Test Phishing Email",
        category=ThreatCategory.PHISHING,
        difficulty=DifficultyLevel.INTERMEDIATE,
        description="Test description",
        prompt="Test prompt",
        options=["Option A", "Option B"],
        correct_answer="Option B",
        explanation="Test explanation",
        tags=["test"]
    )
    assert scenario.scenario_id == "SC001"
    assert scenario.category == ThreatCategory.PHISHING
    assert scenario.difficulty == 2


def test_attempt_schema_validation():
    """Verify ScenarioAttemptSchema validates correctly."""
    attempt = ScenarioAttemptSchema(
        user_id="USER001",
        scenario_id="SC001",
        category=ThreatCategory.PHISHING,
        difficulty=DifficultyLevel.INTERMEDIATE,
        scenario="Test scenario context",
        options=["Option A", "Option B"],
        user_answer="Option A",
        correct_answer="Option B",
        user_reasoning="Felt urgent"
    )
    assert attempt.user_id == "USER001"
    assert attempt.category.value == "phishing"


def test_deterministic_scoring():
    """Verify RiskScorer calculates risk levels deterministically."""
    assert DeterministicRiskScorer.classify_risk_level(50.0) == RiskLevel.HIGH
    assert DeterministicRiskScorer.classify_risk_level(75.0) == RiskLevel.MEDIUM
    assert DeterministicRiskScorer.classify_risk_level(90.0) == RiskLevel.LOW
