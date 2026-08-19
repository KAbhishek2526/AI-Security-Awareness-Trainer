"""
Integration Test for Person 2 (AI Security Coach) to Person 3 (Adaptive Risk Engine & Personalization).
Verifies the complete flow:
ScenarioAttemptSchema -> AIService -> AIAnalysisSchema -> RiskService/AdaptiveRiskEngine -> RiskProfileSchema -> PersonalizationService
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.core.config import settings
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel
from app.schemas.attempt import ScenarioAttemptSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.schemas.risk import RiskProfileSchema
from app.services.scenario_service import ScenarioService
from app.services.ai_service import AIService
from app.services.risk_service import RiskService
from app.services.personalization_service import PersonalizationService
from app.risk.scoring import DeterministicRiskScorer
from app.ai.provider import GeminiLLMProvider, get_llm_provider


HAS_GEMINI_KEY = bool(settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here")


def test_initial_profile_creation_and_ai_analysis_integration():
    """Verify that a new user gets a default profile, which updates deterministically upon receiving AI analysis."""
    user_id = "USER_RISK_TEST_01"
    risk_service = RiskService()
    ai_service = AIService() # Uses default provider (MockLLMProvider for unit determinism)

    # 1. Start with user who has no existing profile
    initial_profile = risk_service.get_user_risk_profile(user_id)
    assert initial_profile.user_id == user_id
    assert initial_profile.total_attempts == 0
    assert initial_profile.overall_score == 100.0
    assert initial_profile.risk_level == RiskLevel.LOW
    assert len(initial_profile.top_weaknesses) == 0

    # 2. Submit an unsafe scenario attempt for PHISH001
    attempt = ScenarioAttemptSchema(
        user_id=user_id,
        scenario_id="PHISH001",
        category=ThreatCategory.PHISHING,
        difficulty=DifficultyLevel.BEGINNER,
        scenario="Phishing test scenario",
        options=["Click link", "Verify sender"],
        user_answer="Click link",
        correct_answer="Verify sender",
        user_reasoning="It looked urgent so I wanted to fix it quickly."
    )

    # 3. AIService generates AIAnalysisSchema
    analysis: AIAnalysisSchema = ai_service.analyze_user_attempt(attempt)
    assert isinstance(analysis, AIAnalysisSchema)
    assert analysis.decision.correct is False

    # 4. Process AI analysis via RiskService
    updated_profile: RiskProfileSchema = risk_service.record_analysis_and_update_risk(analysis)

    # 5. Verify Profile Creation & Deterministic Update
    assert updated_profile.user_id == user_id
    assert updated_profile.total_attempts == 1
    assert "phishing" in updated_profile.category_scores

    phish_score_obj = updated_profile.category_scores["phishing"]
    assert phish_score_obj.attempts_count == 1
    assert phish_score_obj.correct_count == 0
    assert phish_score_obj.score == 0.0

    # Overall score calculated deterministically by Python code (0.0% for 0/1)
    assert updated_profile.overall_score == 0.0
    assert updated_profile.risk_level == RiskLevel.HIGH # < 60.0 => HIGH

    # Weaknesses tracking
    assert len(updated_profile.top_weaknesses) > 0
    assert "urgency_bias" in updated_profile.top_weaknesses


def test_repeated_attempts_and_deterministic_scoring_accuracy():
    """Verify deterministic scoring calculations over repeated attempts for the same user profile."""
    user_id = "USER_REPEATED_TEST"
    risk_service = RiskService()
    ai_service = AIService()

    safe_choice = "Verify the sender address domain and navigate to official IT portal directly"
    unsafe_choice = "Click the link immediately and update your password"

    # Attempt 10 scenarios in PHISHING category: 8 correct, 2 incorrect
    for i in range(10):
        is_correct = (i < 8) # First 8 correct, last 2 incorrect
        attempt = ScenarioAttemptSchema(
            user_id=user_id,
            scenario_id="PHISH001",
            category=ThreatCategory.PHISHING,
            difficulty=DifficultyLevel.BEGINNER,
            scenario="Phishing test",
            options=[safe_choice, unsafe_choice],
            user_answer=safe_choice if is_correct else unsafe_choice,
            correct_answer=safe_choice,
            user_reasoning="Verified out-of-band." if is_correct else "Clicked urgently."
        )
        analysis = ai_service.analyze_user_attempt(attempt)
        profile = risk_service.record_analysis_and_update_risk(analysis)

    # Verify 8 out of 10 correct => 80.0% score
    assert profile.total_attempts == 10
    phish_cat = profile.category_scores["phishing"]
    assert phish_cat.attempts_count == 10
    assert phish_cat.correct_count == 8
    assert phish_cat.score == 80.0

    # Deterministic risk classification: 80.0 >= 80.0 => LOW
    assert profile.overall_score == 80.0
    assert profile.risk_level == RiskLevel.LOW

    safe_pwd = "Generate a unique passphrase stored in an enterprise password manager"
    unsafe_pwd = "Reuse your personal email password"

    # Attempt 10 scenarios in PASSWORD_SECURITY category: 5 correct, 5 incorrect
    for i in range(10):
        is_correct = (i < 5) # 5 correct, 5 incorrect
        attempt = ScenarioAttemptSchema(
            user_id=user_id,
            scenario_id="PWD001",
            category=ThreatCategory.PASSWORD_SECURITY,
            difficulty=DifficultyLevel.BEGINNER,
            scenario="Password test",
            options=[safe_pwd, unsafe_pwd],
            user_answer=safe_pwd if is_correct else unsafe_pwd,
            correct_answer=safe_pwd,
            user_reasoning="Used password manager." if is_correct else "Reused password."
        )
        analysis = ai_service.analyze_user_attempt(attempt)
        profile = risk_service.record_analysis_and_update_risk(analysis)

    # Verify Password Security category score = 50.0%
    pwd_cat = profile.category_scores["password_security"]
    assert pwd_cat.attempts_count == 10
    assert pwd_cat.correct_count == 5
    assert pwd_cat.score == 50.0

    # Overall score = unweighted mean of active categories: (80.0 + 50.0) / 2 = 65.0%
    assert profile.overall_score == 65.0
    # Deterministic risk level: 60.0 <= 65.0 < 80.0 => MEDIUM
    assert profile.risk_level == RiskLevel.MEDIUM



def test_personalization_recommendation_flow():
    """Verify PersonalizationService returns appropriate retraining recommendation from risk profile."""
    user_id = "USER_PERSONALIZATION_TEST"
    risk_service = RiskService()
    ai_service = AIService()
    personalization_service = PersonalizationService()

    # Submit incorrect attempt for MFA_SECURITY scenario
    attempt = ScenarioAttemptSchema(
        user_id=user_id,
        scenario_id="MFA001",
        category=ThreatCategory.MFA_SECURITY,
        difficulty=DifficultyLevel.INTERMEDIATE,
        scenario="MFA push fatigue",
        options=["Approve push", "Deny push"],
        user_answer="Approve push",
        correct_answer="Deny push",
        user_reasoning="Notifications kept popping up."
    )
    analysis = ai_service.analyze_user_attempt(attempt)
    profile = risk_service.record_analysis_and_update_risk(analysis)

    # Get next recommended training iteration
    category, difficulty, reason = personalization_service.get_next_recommended_training(profile)

    assert isinstance(category, ThreatCategory)
    assert isinstance(difficulty, DifficultyLevel)
    assert len(reason) > 5
    assert category == profile.recommended_next_category
    assert difficulty == profile.recommended_next_difficulty


@pytest.mark.skipif(not HAS_GEMINI_KEY, reason="GEMINI_API_KEY is not configured in environment or .env")
def test_gemini_to_risk_end_to_end_integration():
    """Verify full pipeline: ScenarioAttempt -> AIService -> Gemini 3.6 Flash -> AIAnalysisSchema -> Risk Engine -> Personalization."""
    user_id = "USER_GEMINI_RISK_E2E"
    scenario_service = ScenarioService()
    gemini_provider = get_llm_provider("gemini")
    ai_service = AIService(provider=gemini_provider)
    risk_service = RiskService()
    personalization_service = PersonalizationService()

    # 1. Retrieve real scenario
    phish_scenario = scenario_service.get_scenario("PHISH001")

    # 2. Build unsafe attempt
    attempt = ScenarioAttemptSchema(
        user_id=user_id,
        scenario_id=phish_scenario.scenario_id,
        category=phish_scenario.category,
        difficulty=phish_scenario.difficulty,
        scenario=phish_scenario.description,
        options=phish_scenario.options,
        user_answer="Click the link immediately and update your password",
        correct_answer=phish_scenario.correct_answer,
        user_reasoning="It looked urgent so I wanted to fix it quickly."
    )

    # 3. Call AIService (uses Gemini 3.6 Flash live)
    analysis: AIAnalysisSchema = ai_service.analyze_user_attempt(attempt)
    assert isinstance(analysis, AIAnalysisSchema)
    assert analysis.decision.correct is False

    # 4. Pass analysis into Risk Engine
    profile: RiskProfileSchema = risk_service.record_analysis_and_update_risk(analysis)
    assert profile.user_id == user_id
    assert profile.total_attempts == 1
    assert profile.overall_score == 0.0
    assert profile.risk_level == RiskLevel.HIGH
    assert len(profile.top_weaknesses) > 0

    # 5. Query Personalization
    cat, diff, reason = personalization_service.get_next_recommended_training(profile)
    assert cat == ThreatCategory.PHISHING
    assert "retraining" in reason.lower() or "risk level" in reason.lower()

    print("\n" + "=" * 60)
    print("✅ Gemini 3.6 Flash → Risk Engine → Personalization E2E Integration Successful!")
    print(f"   User ID             : {profile.user_id}")
    print(f"   Overall Score       : {profile.overall_score}%")
    print(f"   Risk Level          : {profile.risk_level.value}")
    print(f"   Top Weaknesses      : {profile.top_weaknesses}")
    print(f"   Next Recommendation : {cat.value} (Difficulty {diff.value})")
    print("=" * 60)
