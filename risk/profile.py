"""User profile management, adaptive recommendations, and enterprise metrics."""

import json
import os
from typing import Any, Dict, List, Optional, Union

from data.database import Database, get_db
from risk.models import (
    CANONICAL_CATEGORIES,
    CATEGORY_MAX_DIFFICULTIES,
    EnterpriseMetrics,
    ImprovementMetrics,
    ScenarioAttemptInput,
    ScenarioDefinition,
    TrainingRecommendation,
    UserProfile,
)
from risk.scoring import (
    calculate_overall_score,
    classify_risk,
    create_initial_scores,
    get_weakest_category,
    update_category_score,
)

# Canonical fallback scenarios if scenarios.json is not found
FALLBACK_SCENARIOS: List[Dict[str, Any]] = [
    {"scenario_id": "PHISH001", "category": "phishing", "difficulty": 1, "scenario": "Urgent \"password expiring\" email from a lookalike IT domain."},
    {"scenario_id": "PHISH002", "category": "phishing", "difficulty": 2, "scenario": "Vendor invoice from a slightly altered email address, no urgency."},
    {"scenario_id": "PHISH003", "category": "phishing", "difficulty": 3, "scenario": "Verified CEO account requesting an urgent, confidential wire transfer."},
    {"scenario_id": "SOC001", "category": "social_engineering", "difficulty": 1, "scenario": "Caller claiming to be IT, asking for your password."},
    {"scenario_id": "SOC002", "category": "social_engineering", "difficulty": 2, "scenario": "Tailgating: someone with full hands asking you to hold the secure door."},
    {"scenario_id": "MFA001", "category": "mfa_otp", "difficulty": 1, "scenario": "Unexpected MFA push notification with no login attempt on your end."},
    {"scenario_id": "MFA002", "category": "mfa_otp", "difficulty": 2, "scenario": "\"Bank\" caller asking you to read out your OTP to verify identity."},
    {"scenario_id": "PWD001", "category": "password_security", "difficulty": 1, "scenario": "Choosing the strongest new work-account password practice."},
    {"scenario_id": "PWD002", "category": "password_security", "difficulty": 2, "scenario": "Discovering a team's shared spreadsheet with plaintext passwords."},
    {"scenario_id": "DATA001", "category": "data_protection", "difficulty": 1, "scenario": "Choosing a safe method to send a spreadsheet with customer PII."},
    {"scenario_id": "AI001", "category": "ai_security", "difficulty": 1, "scenario": "Pasting real customer data into a public AI chatbot to debug faster."},
    {"scenario_id": "AI002", "category": "ai_security", "difficulty": 2, "scenario": "AI coding assistant suggests a snippet with a hardcoded API key."},
]


def load_scenarios(file_path: str = "scenarios/scenarios.json") -> List[ScenarioDefinition]:
    """Load scenario definitions from JSON file or fall back to canonical defaults."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [ScenarioDefinition(**item) for item in data]
        except Exception:
            pass
    return [ScenarioDefinition(**item) for item in FALLBACK_SCENARIOS]


def get_user_profile(user_id: str, db: Optional[Database] = None) -> UserProfile:
    """Retrieve the full user profile including scores, risk level, attempt counts, and adaptive recommendations."""
    database = db or get_db()
    row = database.get_or_create_user(user_id)
    
    scores = {
        "phishing": row["phishing_score"],
        "social_engineering": row["social_engineering_score"],
        "mfa_otp": row["mfa_otp_score"],
        "password_security": row["password_security_score"],
        "data_protection": row["data_protection_score"],
        "ai_security": row["ai_security_score"],
    }
    
    overall_score = row["overall_score"]
    risk_level = row["risk_level"]
    baseline_score = row["baseline_score"]
    improvement = overall_score - baseline_score
    
    counts = database.get_attempt_counts(user_id)
    weakest_cat = get_weakest_category(scores)
    
    # Calculate recommended training
    rec = recommend_next_training(user_id, db=database)
    
    return UserProfile(
        user_id=user_id,
        scores=scores,
        overall_score=overall_score,
        risk_level=risk_level,
        attempts=counts["attempts"],
        correct_attempts=counts["correct_attempts"],
        incorrect_attempts=counts["incorrect_attempts"],
        weakest_category=weakest_cat,
        recommended_category=rec.category,
        recommended_difficulty=rec.difficulty,
        baseline_score=baseline_score,
        improvement=improvement,
    )


def record_attempt(
    user_id: Optional[str] = None,
    scenario_id: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: Optional[int] = None,
    correct: Optional[bool] = None,
    user_answer: Optional[str] = None,
    scenario_risk: Optional[str] = None,
    ai_analysis: Optional[Union[Dict[str, Any], Any]] = None,
    attempt_input: Optional[ScenarioAttemptInput] = None,
    db: Optional[Database] = None,
) -> UserProfile:
    """Record a completed scenario attempt, deterministically update scores and profile, and store supporting AI analysis.
    
    Accepts either a ScenarioAttemptInput model or individual keyword arguments.
    """
    database = db or get_db()
    
    if attempt_input is not None:
        u_id = attempt_input.user_id
        s_id = attempt_input.scenario_id
        cat = attempt_input.category.strip().lower()
        diff = attempt_input.difficulty
        corr = attempt_input.correct
        ans = attempt_input.user_answer
        s_risk = attempt_input.scenario_risk
        ai_data = attempt_input.ai_analysis
    else:
        if not (user_id and scenario_id and category is not None and difficulty is not None and correct is not None):
            raise ValueError("user_id, scenario_id, category, difficulty, and correct are required")
        u_id = user_id
        s_id = scenario_id
        cat = category.strip().lower()
        diff = difficulty
        corr = correct
        ans = user_answer
        s_risk = scenario_risk
        ai_data = ai_analysis

    if cat not in CANONICAL_CATEGORIES:
        raise ValueError(f"Unknown category '{cat}'. Must be one of {CANONICAL_CATEGORIES}")

    # Extract AI supporting context if present
    weaknesses = []
    explanation = None
    recommendation = None
    if ai_data:
        if isinstance(ai_data, dict):
            weaknesses = ai_data.get("weaknesses", [])
            explanation = ai_data.get("explanation")
            recommendation = ai_data.get("recommendation")
        else:
            # Pydantic or object
            weaknesses = getattr(ai_data, "weaknesses", [])
            explanation = getattr(ai_data, "explanation", None)
            recommendation = getattr(ai_data, "recommendation", None)

    # 1. Fetch current profile
    profile_row = database.get_or_create_user(u_id)
    current_scores = {
        "phishing": profile_row["phishing_score"],
        "social_engineering": profile_row["social_engineering_score"],
        "mfa_otp": profile_row["mfa_otp_score"],
        "password_security": profile_row["password_security_score"],
        "data_protection": profile_row["data_protection_score"],
        "ai_security": profile_row["ai_security_score"],
    }

    # 2. Deterministic score calculation
    current_cat_score = current_scores.get(cat, 70)
    new_cat_score = update_category_score(current_cat_score, corr, diff)
    current_scores[cat] = new_cat_score

    # 3. Deterministic overall score and risk level
    new_overall_score = calculate_overall_score(current_scores)
    new_risk_level = classify_risk(new_overall_score)

    # 4. Persist attempt and updated profile
    database.record_attempt(
        user_id=u_id,
        scenario_id=s_id,
        category=cat,
        difficulty=diff,
        user_answer=ans,
        correct=corr,
        scenario_risk=s_risk,
        ai_weaknesses=weaknesses,
        ai_explanation=explanation,
        ai_recommendation=recommendation,
    )
    
    database.update_profile_scores(
        user_id=u_id,
        category_scores=current_scores,
        overall_score=new_overall_score,
        risk_level=new_risk_level,
    )

    # 5. Return fresh profile
    return get_user_profile(u_id, db=database)


def recommend_next_training(user_id: str, db: Optional[Database] = None) -> TrainingRecommendation:
    """Generate an adaptive training recommendation targeting the weakest category with adaptive difficulty."""
    database = db or get_db()
    row = database.get_or_create_user(user_id)
    
    scores = {
        "phishing": row["phishing_score"],
        "social_engineering": row["social_engineering_score"],
        "mfa_otp": row["mfa_otp_score"],
        "password_security": row["password_security_score"],
        "data_protection": row["data_protection_score"],
        "ai_security": row["ai_security_score"],
    }
    
    # 1. Target weakest category
    weakest_cat = get_weakest_category(scores)
    lowest_score = scores[weakest_cat]

    # 2. Determine adaptive difficulty based on recent performance in weakest category
    cat_attempts = database.get_attempts(user_id, category=weakest_cat)
    
    # Count consecutive successes from the most recent attempt backwards
    consecutive_correct = 0
    for att in reversed(cat_attempts):
        if att["correct"]:
            consecutive_correct += 1
        else:
            break
            
    if consecutive_correct >= 3:
        target_diff = 3
    elif consecutive_correct == 2:
        target_diff = 2
    else:
        target_diff = 1

    # Cap difficulty at maximum available for this category
    max_allowed = CATEGORY_MAX_DIFFICULTIES.get(weakest_cat, 1)
    target_diff = min(target_diff, max_allowed)

    # 3. Select appropriate scenario deterministically
    all_scenarios = load_scenarios()
    
    # Match candidate scenarios in category and target difficulty
    matching_scenarios = [
        s for s in all_scenarios
        if s.category == weakest_cat and s.difficulty == target_diff
    ]
    
    # Fallback to any scenario in that category if exact difficulty match is empty
    if not matching_scenarios:
        matching_scenarios = [s for s in all_scenarios if s.category == weakest_cat]
        # sort by closest difficulty
        matching_scenarios.sort(key=lambda s: abs(s.difficulty - target_diff))

    # Avoid immediately repeating the last completed scenario if alternatives exist
    last_completed_scenario_id = cat_attempts[-1]["scenario_id"] if cat_attempts else None
    
    selected_scenario: ScenarioDefinition
    if len(matching_scenarios) > 1 and last_completed_scenario_id:
        non_repeating = [s for s in matching_scenarios if s.scenario_id != last_completed_scenario_id]
        if non_repeating:
            selected_scenario = non_repeating[0]
        else:
            selected_scenario = matching_scenarios[0]
    else:
        selected_scenario = matching_scenarios[0]

    reason = f"Lowest category score: {weakest_cat} ({lowest_score}/100)"

    return TrainingRecommendation(
        category=weakest_cat,
        difficulty=selected_scenario.difficulty,
        reason=reason,
        scenario_id=selected_scenario.scenario_id,
    )


def get_improvement(user_id: str, db: Optional[Database] = None) -> ImprovementMetrics:
    """Calculate the baseline vs current score improvement for a user."""
    profile = get_user_profile(user_id, db=db)
    return ImprovementMetrics(
        baseline_score=profile.baseline_score,
        current_score=profile.overall_score,
        improvement=profile.improvement,
    )


def get_enterprise_metrics(db: Optional[Database] = None) -> EnterpriseMetrics:
    """Calculate aggregated organization-wide risk and awareness metrics for Module 4."""
    database = db or get_db()
    profiles = database.get_all_profiles()
    
    if not profiles:
        return EnterpriseMetrics(
            total_users=0,
            risk_distribution={"high": 0, "medium": 0, "low": 0},
            average_score=INITIAL_CATEGORY_SCORE,
            category_weaknesses=create_initial_scores(),
            most_common_weakness=CANONICAL_CATEGORIES[0],
            average_improvement=0,
        )

    total_users = len(profiles)
    risk_counts = {"high": 0, "medium": 0, "low": 0}
    total_overall_score = 0
    total_improvement = 0
    
    cat_totals = {cat: 0 for cat in CANONICAL_CATEGORIES}

    for p in profiles:
        overall = p["overall_score"]
        risk = p["risk_level"]
        baseline = p["baseline_score"]
        
        total_overall_score += overall
        total_improvement += (overall - baseline)
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        cat_totals["phishing"] += p["phishing_score"]
        cat_totals["social_engineering"] += p["social_engineering_score"]
        cat_totals["mfa_otp"] += p["mfa_otp_score"]
        cat_totals["password_security"] += p["password_security_score"]
        cat_totals["data_protection"] += p["data_protection_score"]
        cat_totals["ai_security"] += p["ai_security_score"]

    avg_overall = int(round(total_overall_score / total_users))
    avg_improvement = int(round(total_improvement / total_users))
    
    avg_cat_scores = {
        cat: int(round(cat_totals[cat] / total_users))
        for cat in CANONICAL_CATEGORIES
    }

    # Find most common weakness across the enterprise (lowest average category score)
    most_common_weakness = get_weakest_category(avg_cat_scores)

    return EnterpriseMetrics(
        total_users=total_users,
        risk_distribution=risk_counts,
        average_score=avg_overall,
        category_weaknesses=avg_cat_scores,
        most_common_weakness=most_common_weakness,
        average_improvement=avg_improvement,
    )
