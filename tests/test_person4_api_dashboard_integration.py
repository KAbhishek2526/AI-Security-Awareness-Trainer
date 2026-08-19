"""
Person 4 FastAPI & Streamlit Dashboard End-to-End Integration Test.
Verifies the complete 10-step flow:
Scenario -> ScenarioAttempt -> AIService (Gemini 3.6 Flash) -> AIAnalysisSchema -> Risk Engine -> RiskProfile -> Personalization -> FastAPI -> Streamlit Dashboard
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.core.config import settings
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel
from app.api.routes import app
from app.schemas.attempt import ScenarioAttemptSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.schemas.risk import RiskProfileSchema
from app.schemas.scenario import ScenarioSchema
from app.services.scenario_service import ScenarioService
from app.services.ai_service import AIService
from app.services.risk_service import RiskService
from app.services.personalization_service import PersonalizationService
from app.ai.provider import GeminiLLMProvider, get_llm_provider


HAS_GEMINI_KEY = bool(settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here")


def test_fastapi_rest_endpoints_contract():
    """Verify FastAPI routes /health, /scenarios, /coach/analyze, /risk/profile/{id}, /risk/update."""
    client = TestClient(app)

    # 1. Health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    data_health = res_health.json()
    assert data_health["status"] == "ok"
    assert data_health["modules"]["person4_dashboard"] == "active"

    # 2. List scenarios via API
    res_sc = client.get("/api/v1/scenarios/")
    assert res_sc.status_code == 200
    scenarios_list = res_sc.json()
    assert isinstance(scenarios_list, list)
    assert len(scenarios_list) >= 12
    scenario_ids = [s["scenario_id"] for s in scenarios_list]
    assert "PHISH001" in scenario_ids

    # 3. Get user risk profile via API
    user_id = "USER_API_TEST_01"
    res_profile = client.get(f"/api/v1/risk/profile/{user_id}")
    assert res_profile.status_code == 200
    prof_data = res_profile.json()
    assert prof_data["user_id"] == user_id
    assert prof_data["overall_score"] == 100.0
    assert prof_data["risk_level"] == "low"

    # 4. Analyze scenario attempt via API
    attempt_data = {
        "user_id": user_id,
        "scenario_id": "PHISH001",
        "category": "phishing",
        "difficulty": 1,
        "scenario": "Phishing test",
        "options": ["Click link", "Verify sender"],
        "user_answer": "Click link",
        "correct_answer": "Verify sender",
        "user_reasoning": "It looked urgent and came from IT support so I wanted to fix it quickly."
    }
    res_coach = client.post("/api/v1/coach/analyze", json=attempt_data)
    assert res_coach.status_code == 200
    analysis_res = res_coach.json()
    assert analysis_res["user_id"] == user_id
    assert analysis_res["decision"]["correct"] is False
    assert analysis_res["decision"]["risk_signal"] in ["medium", "high"]
    assert len(analysis_res["security_analysis"]["weaknesses"]) > 0

    # 5. Update user risk profile via API using AI analysis
    res_update = client.post("/api/v1/risk/update", json=analysis_res)
    assert res_update.status_code == 200
    updated_prof_data = res_update.json()
    assert updated_prof_data["total_attempts"] == 1
    assert updated_prof_data["overall_score"] < 100.0
    assert updated_prof_data["risk_level"] == "high"


@pytest.mark.skipif(not HAS_GEMINI_KEY, reason="GEMINI_API_KEY is not configured in environment or .env")
def test_full_e2e_gemini_to_api_and_dashboard_flow():
    """Verify complete 10-step E2E flow: Scenario -> Attempt -> AIService (Gemini 3.6 Flash) -> AIAnalysis -> Risk Engine -> RiskProfile -> Personalization -> FastAPI -> Dashboard."""
    client = TestClient(app)
    user_id = "USER_GEMINI_E2E_DASHBOARD"

    # Step 1: Load real scenario PHISH001 from ScenarioService
    scenario_service = ScenarioService()
    phish001: ScenarioSchema = scenario_service.get_scenario("PHISH001")
    assert phish001.scenario_id == "PHISH001"

    # Step 2: Construct ScenarioAttempt
    attempt_payload = ScenarioAttemptSchema(
        user_id=user_id,
        scenario_id=phish001.scenario_id,
        category=phish001.category,
        difficulty=phish001.difficulty,
        scenario=phish001.description,
        options=phish001.options,
        user_answer="Click the link immediately and update your password",
        correct_answer=phish001.correct_answer,
        user_reasoning="It looked urgent so I wanted to fix it quickly."
    )

    # Step 3 & 4 & 5: AIService using live Gemini 3.6 Flash provider produces AIAnalysisSchema
    gemini_provider = get_llm_provider("gemini")
    ai_service = AIService(provider=gemini_provider)
    ai_analysis: AIAnalysisSchema = ai_service.analyze_user_attempt(attempt_payload)

    assert isinstance(ai_analysis, AIAnalysisSchema)
    assert ai_analysis.decision.correct is False

    # Step 6 & 7 & 8: Post AIAnalysis payload to FastAPI /api/v1/risk/update endpoint
    response_update = client.post("/api/v1/risk/update", json=ai_analysis.model_dump(mode="json"))
    assert response_update.status_code == 200

    # Step 9: Retrieve updated RiskProfile through REST API GET /api/v1/risk/profile/{user_id}
    response_get = client.get(f"/api/v1/risk/profile/{user_id}")
    assert response_get.status_code == 200
    dashboard_profile_data = response_get.json()

    # Step 10: Verify dashboard-facing JSON response fields match Person 3 risk calculations
    assert dashboard_profile_data["user_id"] == user_id
    assert dashboard_profile_data["total_attempts"] == 1
    assert dashboard_profile_data["overall_score"] == 0.0
    assert dashboard_profile_data["risk_level"] == "high"
    assert len(dashboard_profile_data["top_weaknesses"]) > 0
    assert dashboard_profile_data["recommended_next_category"] == "phishing"


    print("\n" + "=" * 60)
    print("✅ E2E Flow: Scenario -> Gemini 3.6 Flash -> Risk -> API -> Dashboard Verified!")
    print(f"   User ID             : {dashboard_profile_data['user_id']}")
    print(f"   API Response Status : HTTP {response_get.status_code} OK")
    print(f"   Dashboard Score     : {dashboard_profile_data['overall_score']}%")
    print(f"   Dashboard Risk      : {dashboard_profile_data['risk_level'].upper()}")
    print(f"   Top Weaknesses      : {dashboard_profile_data['top_weaknesses']}")
    print(f"   Next Recommended    : {dashboard_profile_data['recommended_next_category']}")
    print("=" * 60)
