"""
Hackathon End-to-End Demo Script for Person 2 AI Security Coach.
Demonstrates 5 core hackathon demo flows: PHISH001, PHISH003, MFA001, AI001, AI002.
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


def run_person2_demo():
    print("=" * 75)
    print(" AI HUMAN FIREWALL -- PERSON 2: AI SECURITY COACH DEMO")
    print("=" * 75)

    scenario_service = ScenarioService()
    ai_service = AIService()
    risk_service = RiskService()

    demo_cases = [
        {
            "demo_id": "DEMO 1 -- PHISH001 (Urgency Bias)",
            "scenario_id": "PHISH001",
            "user_answer": "Click the link immediately and update your password",
            "reasoning": "I would click the link because my password is expiring and I need to fix it immediately."
        },
        {
            "demo_id": "DEMO 2 -- PHISH003 (CEO Fraud & Authority Trust)",
            "scenario_id": "PHISH003",
            "user_answer": "Execute the wire transfer immediately because it is marked urgent and confidential by the CEO",
            "reasoning": "I would send the transfer because the email is from the CEO."
        },
        {
            "demo_id": "DEMO 3 -- MFA001 (MFA Fatigue)",
            "scenario_id": "MFA001",
            "user_answer": "Approve the push request to make the notification disappear",
            "reasoning": "I would approve the MFA request because it keeps appearing."
        },
        {
            "demo_id": "DEMO 4 -- AI001 (Public AI Data Upload - KEY DEMO)",
            "scenario_id": "AI001",
            "user_answer": "It is completely safe because public AI models delete data immediately",
            "reasoning": "I would paste the customer data because the AI can debug the issue faster."
        },
        {
            "demo_id": "DEMO 5 -- AI002 (Hardcoded Secret in AI Code)",
            "scenario_id": "AI002",
            "user_answer": "Commit the code directly to Git because the AI assistant generated it",
            "reasoning": "I would use the code because the AI generated it."
        }
    ]

    for case in demo_cases:
        print(f"\n---------------------------------------------------------------------------")
        print(f"[*] {case['demo_id']}")
        print(f"---------------------------------------------------------------------------")

        scenario = scenario_service.get_scenario(case["scenario_id"])
        print(f"Scenario Context: {scenario.description[:90]}...")
        print(f"User Selected Choice: {case['user_answer']}")
        print(f"User Stated Reasoning: \"{case['reasoning']}\"")

        attempt = ScenarioAttemptSchema(
            user_id="DEMO_USER_01",
            scenario_id=scenario.scenario_id,
            category=scenario.category,
            difficulty=scenario.difficulty,
            scenario=scenario.description,
            options=scenario.options,
            user_answer=case["user_answer"],
            correct_answer=scenario.correct_answer,
            user_reasoning=case["reasoning"]
        )

        # Person 2 AI Coach Analysis
        analysis = ai_service.analyze_user_attempt(attempt)

        print("\n[AI Security Coach Output]:")
        print(f"  * Decision Correct:    {analysis.decision.correct}")
        print(f"  * Risk Signal:         {analysis.decision.risk_signal.value.upper()}")
        print(f"  * Weaknesses Detected: {analysis.security_analysis.weaknesses}")
        print(f"  * What Happened:       {analysis.feedback.what_happened}")
        print(f"  * Why Risky:           {analysis.feedback.why_risky}")
        print(f"  * Safer Behavior:      {analysis.feedback.safer_behavior}")
        print(f"  * Learning Takeaway:   {analysis.feedback.learning_point}")
        print(f"  * Socratic Question:   \"{analysis.coaching.question}\"")
        print(f"  * Learning Rec:        Topic: {analysis.recommendation.topic.value} (Diff: {analysis.recommendation.difficulty}) - {analysis.recommendation.reason}")

        # Person 3 Consumption Verification
        profile = risk_service.record_analysis_and_update_risk(analysis)
        print(f"\n[Person 3 Risk Profile Updated]: Score = {profile.overall_score}/100 | Risk Level = {profile.risk_level.value.upper()}")

    print("\n" + "=" * 75)
    print(" [+] PERSON 2 AI SECURITY COACH DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    run_person2_demo()
