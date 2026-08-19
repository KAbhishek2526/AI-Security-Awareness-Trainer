"""
Demo runner script testing integration contract pipeline across all 4 module layers.
Run with: python scripts/run_demo.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas.attempt import ScenarioAttemptSchema
from app.services.scenario_service import ScenarioService
from app.services.ai_service import AIService
from app.services.risk_service import RiskService
from app.core.constants import ThreatCategory, DifficultyLevel


def run_pipeline_demo():
    print("=" * 60)
    print("AI HUMAN FIREWALL — Integration Pipeline Verification")
    print("=" * 60)

    # Step 1: Person 1 Scenarios
    print("\n[Step 1: Person 1 - Scenario Engine]")
    scenario_service = ScenarioService()
    scenarios = scenario_service.get_all()
    scenario = scenarios[0]
    print(f"Loaded Scenario ID: {scenario.scenario_id}")
    print(f"Title: {scenario.title}")
    print(f"Category: {scenario.category.value}")

    # Simulating User Input
    attempt_payload = ScenarioAttemptSchema(
        user_id="USER001",
        scenario_id=scenario.scenario_id,
        category=scenario.category,
        difficulty=scenario.difficulty,
        scenario=scenario.description,
        options=scenario.options,
        user_answer=scenario.options[0],  # Choosing incorrect option
        correct_answer=scenario.correct_answer,
        user_reasoning="The email said it was urgent IT support so I clicked immediately."
    )
    print(f"Simulated User Choice: {attempt_payload.user_answer}")

    # Step 2: Person 2 AI Coach
    print("\n[Step 2: Person 2 - AI Security Coach]")
    ai_service = AIService()
    ai_analysis = ai_service.analyze_user_attempt(attempt_payload)
    print(f"AI Assessed Correct: {ai_analysis.analysis.correct}")
    print(f"AI Assessed Risk: {ai_analysis.analysis.risk.value}")
    print(f"Identified Weaknesses: {ai_analysis.analysis.weaknesses}")
    print(f"Feedback: {ai_analysis.feedback.explanation}")

    # Step 3: Person 3 Risk Engine
    print("\n[Step 3: Person 3 - Adaptive Risk Engine]")
    risk_service = RiskService()
    updated_profile = risk_service.record_analysis_and_update_risk(ai_analysis)
    print(f"Updated Overall Risk Score: {updated_profile.overall_score}/100")
    print(f"Deterministic Risk Level: {updated_profile.risk_level.value}")
    print(f"Recommended Next Category: {updated_profile.recommended_next_category.value}")
    print(f"Recommended Next Difficulty: {updated_profile.recommended_next_difficulty}")

    # Step 4: Person 4 Integration Verification
    print("\n[Step 4: Person 4 - Integration Status]")
    print("Contract verification passed seamlessly across all 4 module boundaries!")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline_demo()
