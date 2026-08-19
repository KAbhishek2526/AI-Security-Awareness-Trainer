"""
Comprehensive Person 4 Integration Verification Test.
Executes exact 18-step user flow:
Dashboard load -> Scenario retrieval -> PHISH001 -> Unsafe decision & reasoning ->
AI Coach invocation -> Structured feedback & weakness detection -> Socratic question ->
Person 3 Risk Profile update -> Recommendation -> Next scenario -> Manager Dashboard aggregation ->
Secrets exposure audit.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from app.schemas.attempt import ScenarioAttemptSchema
from app.schemas.scenario import ScenarioSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.schemas.risk import RiskProfileSchema
from app.services.scenario_service import ScenarioService
from app.services.ai_service import AIService
from app.services.risk_service import RiskService
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel


def test_complete_person4_18_step_integration_flow():
    """Execute complete 18-step Person 4 end-to-end integration verification."""

    # 1. Fresh Application State Initialization
    scenario_service = ScenarioService()
    ai_service = AIService()
    risk_service = RiskService()

    user_id = "USER001"

    # 2. Load User Dashboard Profile
    initial_profile: RiskProfileSchema = risk_service.get_user_risk_profile(user_id)
    assert initial_profile.user_id == user_id
    assert initial_profile.overall_score == 100.0
    assert initial_profile.risk_level == RiskLevel.LOW

    # 3. Retrieve Available Scenarios
    available_scenarios = scenario_service.get_all()
    assert len(available_scenarios) >= 12
    scenario_ids = [s.scenario_id for s in available_scenarios]
    assert "PHISH001" in scenario_ids
    assert "AI001" in scenario_ids

    # 4. Open PHISH001
    phish001: ScenarioSchema = scenario_service.get_scenario("PHISH001")
    assert phish001.scenario_id == "PHISH001"
    assert phish001.category == ThreatCategory.PHISHING

    # 5. Display Scenario Data
    assert "IT-Support" in phish001.description
    assert len(phish001.options) == 4

    # 6. Submit Unsafe Decision
    unsafe_choice = "Click the link immediately and update your password"
    assert unsafe_choice in phish001.options

    # 7. Submit User Reasoning
    user_reasoning = "It looked urgent and came from IT support so I wanted to fix it quickly."

    # 8. Invoke Person 2 AI Coach
    attempt = ScenarioAttemptSchema(
        user_id=user_id,
        scenario_id=phish001.scenario_id,
        category=phish001.category,
        difficulty=phish001.difficulty,
        scenario=phish001.description,
        options=phish001.options,
        user_answer=unsafe_choice,
        correct_answer=phish001.correct_answer,
        user_reasoning=user_reasoning
    )

    ai_analysis: AIAnalysisSchema = ai_service.analyze_user_attempt(attempt)
    assert ai_analysis.decision.correct is False
    assert ai_analysis.decision.risk_signal in [RiskLevel.MEDIUM, RiskLevel.HIGH]

    # 9. Display Structured Feedback
    assert ai_analysis.feedback.what_happened != ""
    assert ai_analysis.feedback.why_risky != ""
    assert ai_analysis.feedback.safer_behavior != ""
    assert ai_analysis.feedback.learning_point != ""

    # 10. Display Detected Weaknesses
    weaknesses = ai_analysis.security_analysis.weaknesses
    assert len(weaknesses) > 0
    assert "urgency_bias" in weaknesses

    # 11. Display Coaching Question
    assert len(ai_analysis.coaching.question) > 10
    assert "?" in ai_analysis.coaching.question

    # 12. Update/Retrieve Person 3 Risk Profile
    updated_profile: RiskProfileSchema = risk_service.record_analysis_and_update_risk(ai_analysis)

    # 13. Display Updated Risk Information
    assert updated_profile.total_attempts == 1
    assert updated_profile.overall_score < 100.0
    assert updated_profile.risk_level == RiskLevel.HIGH
    assert "urgency_bias" in updated_profile.top_weaknesses

    # 14. Display Personalized Recommendation
    assert updated_profile.recommended_next_category == ThreatCategory.PHISHING
    assert updated_profile.recommended_next_difficulty in [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE]

    # 15. Start Another Scenario (AI001)
    ai001: ScenarioSchema = scenario_service.get_scenario("AI001")
    assert ai001.scenario_id == "AI001"

    attempt_ai = ScenarioAttemptSchema(
        user_id=user_id,
        scenario_id=ai001.scenario_id,
        category=ai001.category,
        difficulty=ai001.difficulty,
        scenario=ai001.description,
        options=ai001.options,
        user_answer="It is completely safe because public AI models delete data immediately",
        correct_answer=ai001.correct_answer,
        user_reasoning="I pasted customer data because the AI can debug faster."
    )
    analysis_ai = ai_service.analyze_user_attempt(attempt_ai)
    risk_service.record_analysis_and_update_risk(analysis_ai)

    # 16. Open Manager Dashboard & Aggregate Multi-User Profiles
    user2_profile = risk_service.get_user_risk_profile("USER002")
    user3_profile = risk_service.get_user_risk_profile("USER003")
    all_profiles = [risk_service.get_user_risk_profile(u) for u in ["USER001", "USER002", "USER003"]]

    # 17. Verify Aggregated Manager Metrics
    total_users = len(all_profiles)
    assert total_users == 3
    avg_score = sum(p.overall_score for p in all_profiles) / total_users
    assert avg_score < 100.0

    high_risk_users = [p for p in all_profiles if p.risk_level == RiskLevel.HIGH]
    assert len(high_risk_users) >= 1

    # 18. Verify No Raw Secrets or Sensitive Information Exposed
    all_payload_str = str(ai_analysis.model_dump()) + str(updated_profile.model_dump())
    assert "sk-" not in all_payload_str
    assert "api_key" not in all_payload_str.lower() or "hardcoded" in all_payload_str.lower()
    assert "password123" not in all_payload_str.lower()
