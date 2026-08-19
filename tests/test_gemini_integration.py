"""
Integration Test for AI Security Coach with Real Gemini Provider (gemini-3.6-flash).
Verifies the complete flow:
Scenario -> ScenarioAttemptSchema -> AIService -> GeminiLLMProvider -> Gemini 3.6 Flash -> AIAnalysisSchema
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.core.config import settings
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel
from app.schemas.attempt import ScenarioAttemptSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.services.scenario_service import ScenarioService
from app.services.ai_service import AIService
from app.ai.provider import GeminiLLMProvider, get_llm_provider


# Skip test if GEMINI_API_KEY is not set or placeholder
HAS_GEMINI_KEY = bool(settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here")


@pytest.mark.skipif(not HAS_GEMINI_KEY, reason="GEMINI_API_KEY is not configured in environment or .env")
def test_gemini_ai_service_integration_flow():
    """Verify end-to-end AIService execution using real Gemini 3.6 Flash provider."""

    # 1. Initialize Gemini Provider and AIService
    gemini_provider = get_llm_provider("gemini")
    assert isinstance(gemini_provider, GeminiLLMProvider)
    assert gemini_provider.model_name == "gemini-3.6-flash"

    ai_service = AIService(provider=gemini_provider)
    assert isinstance(ai_service.provider, GeminiLLMProvider)
    assert ai_service.provider.model_name == "gemini-3.6-flash"

    # 2. Retrieve PHISH001 Scenario
    scenario_service = ScenarioService()
    scenario_data = scenario_service.get_scenario("PHISH001")
    assert scenario_data.scenario_id == "PHISH001"
    assert scenario_data.category == ThreatCategory.PHISHING

    # 3. Construct Unsafe ScenarioAttempt
    user_id = "USER_GEMINI_TEST"
    unsafe_choice = "Click the link immediately and update your password"
    user_reasoning = "It looked urgent and came from IT support so I wanted to fix it quickly."

    attempt = ScenarioAttemptSchema(
        user_id=user_id,
        scenario_id=scenario_data.scenario_id,
        category=scenario_data.category,
        difficulty=scenario_data.difficulty,
        scenario=scenario_data.description,
        options=scenario_data.options,
        user_answer=unsafe_choice,
        correct_answer=scenario_data.correct_answer,
        user_reasoning=user_reasoning
    )

    # 4. Execute AIService.analyze_user_attempt (calls Gemini 3.6 Flash via GeminiLLMProvider)
    analysis: AIAnalysisSchema = ai_service.analyze_user_attempt(attempt)

    # 5. Verify Output Schema Contract & Decision Results
    assert isinstance(analysis, AIAnalysisSchema)
    assert analysis.user_id == user_id
    assert analysis.scenario_id == "PHISH001"
    assert analysis.category == ThreatCategory.PHISHING

    # Decision evaluation check
    assert analysis.decision.correct is False
    assert analysis.decision.risk_signal in [RiskLevel.MEDIUM, RiskLevel.HIGH]

    # Weaknesses check (normalized vocabulary check)
    assert isinstance(analysis.security_analysis.weaknesses, list)
    assert len(analysis.security_analysis.weaknesses) > 0

    # Structured feedback check
    assert analysis.feedback.what_happened != ""
    assert analysis.feedback.why_risky != ""
    assert analysis.feedback.safer_behavior != ""
    assert analysis.feedback.learning_point != ""

    # Coaching Socratic question check
    assert len(analysis.coaching.question) > 5

    # Retraining recommendation check
    assert analysis.recommendation.topic == ThreatCategory.PHISHING
    assert analysis.recommendation.difficulty in [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED]

    print("\n" + "=" * 60)
    print("✅ Gemini AIService Integration Test Completed Successfully!")
    print(f"   Provider Used : {type(ai_service.provider).__name__}")
    print(f"   Model Used    : {ai_service.provider.model_name}")
    print(f"   Decision      : Correct={analysis.decision.correct}, RiskSignal={analysis.decision.risk_signal.value}")
    print(f"   Weaknesses    : {analysis.security_analysis.weaknesses}")
    print(f"   Feedback      : {analysis.feedback.why_risky}")
    print(f"   Coaching Q    : {analysis.coaching.question}")
    print("=" * 60)
