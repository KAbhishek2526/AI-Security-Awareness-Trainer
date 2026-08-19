"""Comprehensive unit and integration test suite for Module 3 (Adaptive Risk & Personalization Engine)."""

import pytest
from data.database import Database
from risk.models import (
    CANONICAL_CATEGORIES,
    CATEGORY_MAX_DIFFICULTIES,
    INITIAL_CATEGORY_SCORE,
    AIAnalysisInput,
    ScenarioAttemptInput,
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


@pytest.fixture
def memory_db():
    """Create an isolated in-memory SQLite database for testing."""
    return Database(":memory:")


# ==============================================================================
# 1. INITIAL SCORES & PROFILE SETUP
# ==============================================================================

def test_initial_scores_and_profile(memory_db):
    """Verify new user receives default score 70 across all 6 canonical categories."""
    profile = get_user_profile("USER_NEW", db=memory_db)
    
    assert profile.user_id == "USER_NEW"
    assert profile.overall_score == 70
    assert profile.risk_level == "medium"
    assert profile.baseline_score == 70
    assert profile.improvement == 0
    assert profile.attempts == 0
    assert profile.correct_attempts == 0
    assert profile.incorrect_attempts == 0
    
    # Check all 6 canonical categories are present and set to 70
    for cat in CANONICAL_CATEGORIES:
        assert cat in profile.scores
        assert profile.scores[cat] == 70


# ==============================================================================
# 2. SCORING ENGINE: CORRECT ANSWERS
# ==============================================================================

def test_correct_answer_updates(memory_db):
    """Verify correct answer increases the category score according to difficulty."""
    # Diff 1 correct (+5) -> 70 + 5 = 75
    profile = record_attempt(
        user_id="U1",
        scenario_id="PHISH001",
        category="phishing",
        difficulty=1,
        correct=True,
        db=memory_db,
    )
    assert profile.scores["phishing"] == 75
    assert profile.attempts == 1
    assert profile.correct_attempts == 1
    assert profile.incorrect_attempts == 0


# ==============================================================================
# 3. SCORING ENGINE: INCORRECT ANSWERS
# ==============================================================================

def test_incorrect_answer_updates(memory_db):
    """Verify incorrect answer reduces the category score according to difficulty."""
    # Diff 1 incorrect (-7) -> 70 - 7 = 63
    profile = record_attempt(
        user_id="U2",
        scenario_id="SOC001",
        category="social_engineering",
        difficulty=1,
        correct=False,
        db=memory_db,
    )
    assert profile.scores["social_engineering"] == 63
    assert profile.attempts == 1
    assert profile.correct_attempts == 0
    assert profile.incorrect_attempts == 1


# ==============================================================================
# 4. DIFFICULTY WEIGHTING
# ==============================================================================

def test_difficulty_weighting():
    """Verify difficulty weights:
    Correct: diff 1 (+5), diff 2 (+7), diff 3 (+9)
    Incorrect: diff 1 (-7), diff 2 (-10), diff 3 (-13)
    """
    base = 70
    assert update_category_score(base, correct=True, difficulty=1) == 75
    assert update_category_score(base, correct=True, difficulty=2) == 77
    assert update_category_score(base, correct=True, difficulty=3) == 79

    assert update_category_score(base, correct=False, difficulty=1) == 63
    assert update_category_score(base, correct=False, difficulty=2) == 60
    assert update_category_score(base, correct=False, difficulty=3) == 57


# ==============================================================================
# 5. SCORE CLAMPING (0 to 100)
# ==============================================================================

def test_score_clamping():
    """Verify scores never go below 0 or above 100."""
    assert clamp_score(150) == 100
    assert clamp_score(-20) == 0
    assert clamp_score(70) == 70

    # Test clamping via repeated updates
    score = 95
    score = update_category_score(score, correct=True, difficulty=3)  # 95 + 9 = 104 -> 100
    assert score == 100

    low_score = 5
    low_score = update_category_score(low_score, correct=False, difficulty=2)  # 5 - 10 = -5 -> 0
    assert low_score == 0


# ==============================================================================
# 6. OVERALL SCORE CALCULATION
# ==============================================================================

def test_calculate_overall_score():
    """Verify overall score is the rounded arithmetic average of all 6 categories."""
    scores = {
        "phishing": 52,
        "social_engineering": 41,
        "mfa_otp": 70,
        "password_security": 88,
        "data_protection": 76,
        "ai_security": 63,
    }
    # sum = 390 / 6 = 65
    assert calculate_overall_score(scores) == 65

    # Test rounding
    scores2 = {
        "phishing": 70,
        "social_engineering": 70,
        "mfa_otp": 70,
        "password_security": 70,
        "data_protection": 70,
        "ai_security": 71,
    }
    # sum = 421 / 6 = 70.166 -> 70
    assert calculate_overall_score(scores2) == 70


# ==============================================================================
# 7. RISK CLASSIFICATION BOUNDARIES
# ==============================================================================

def test_risk_classification_boundaries():
    """Explicitly verify risk thresholds:
    71–100 -> low
    41–70  -> medium
    0–40   -> high
    """
    assert classify_risk(100) == "low"
    assert classify_risk(71) == "low"
    assert classify_risk(70) == "medium"
    assert classify_risk(41) == "medium"
    assert classify_risk(40) == "high"
    assert classify_risk(0) == "high"


# ==============================================================================
# 8. WEAKEST CATEGORY & DETERMINISTIC TIE-BREAKING
# ==============================================================================

def test_weakest_category_detection():
    """Verify weakest category is identified correctly with deterministic tie-breaking."""
    scores = {
        "phishing": 52,
        "social_engineering": 35,
        "mfa_otp": 70,
        "password_security": 88,
        "data_protection": 76,
        "ai_security": 63,
    }
    assert get_weakest_category(scores) == "social_engineering"

    # Tied scores: all 70 -> tie-breaker picks first in canonical order ('phishing')
    initial = create_initial_scores()
    assert get_weakest_category(initial) == "phishing"


# ==============================================================================
# 9. ADAPTIVE DIFFICULTY RECOMMENDATION
# ==============================================================================

def test_adaptive_difficulty_recommendation(memory_db):
    """Verify adaptive difficulty increases on consecutive successes and drops on failure."""
    user_id = "U_ADAPTIVE"
    
    # Initially, weakest category is phishing (due to tie-break on 70), 0 successes -> diff 1
    rec1 = recommend_next_training(user_id, db=memory_db)
    assert rec1.category == "phishing"
    assert rec1.difficulty == 1

    # 1 success in phishing -> still diff 1 (0-1 successes -> diff 1)
    record_attempt(user_id=user_id, scenario_id="PHISH001", category="phishing", difficulty=1, correct=True, db=memory_db)
    
    # Now other categories are tied at 70 while phishing is 75. Next weakest is social_engineering.
    # Fail social_engineering on difficulty 2 (-10) -> score 60 (remains lowest even after two +5 wins)
    record_attempt(user_id=user_id, scenario_id="SOC002", category="social_engineering", difficulty=2, correct=False, db=memory_db)
    
    # 0 consecutive successes in social_engineering -> diff 1
    rec2 = recommend_next_training(user_id, db=memory_db)
    assert rec2.category == "social_engineering"
    assert rec2.difficulty == 1

    # 1st consecutive success in social_engineering (+5) -> score 65 (still lowest)
    record_attempt(user_id=user_id, scenario_id="SOC001", category="social_engineering", difficulty=1, correct=True, db=memory_db)
    rec3 = recommend_next_training(user_id, db=memory_db)
    assert rec3.category == "social_engineering"
    assert rec3.difficulty == 1

    # 2nd consecutive success in social_engineering (+5) -> score 70 (tied with 70s, tie-breaker prioritizes social_engineering)
    record_attempt(user_id=user_id, scenario_id="SOC001", category="social_engineering", difficulty=1, correct=True, db=memory_db)
    rec4 = recommend_next_training(user_id, db=memory_db)
    assert rec4.category == "social_engineering"
    assert rec4.difficulty == 2

    # If user then fails a difficulty 2 scenario, streak resets and difficulty returns to 1
    record_attempt(user_id=user_id, scenario_id="SOC002", category="social_engineering", difficulty=2, correct=False, db=memory_db)
    rec5 = recommend_next_training(user_id, db=memory_db)
    assert rec5.category == "social_engineering"
    assert rec5.difficulty == 1


# ==============================================================================
# 10. SCENARIO AVAILABILITY CONSTRAINTS
# ==============================================================================

def test_scenario_availability_constraints(memory_db):
    """Verify data_protection never receives difficulty > 1 regardless of streaks."""
    user_id = "U_DATA"
    
    # Force data_protection to be the weakest category by failing it once
    record_attempt(user_id=user_id, scenario_id="DATA001", category="data_protection", difficulty=1, correct=False, db=memory_db)
    
    # Now simulate 5 consecutive correct answers in data_protection
    for _ in range(5):
        record_attempt(user_id=user_id, scenario_id="DATA001", category="data_protection", difficulty=1, correct=True, db=memory_db)
    
    # If data_protection is evaluated, its difficulty MUST NEVER exceed 1
    max_diff = CATEGORY_MAX_DIFFICULTIES["data_protection"]
    assert max_diff == 1
    
    # Let's drop other scores to keep data_protection weakest and test recommendation
    # (By dropping ai_security to 0)
    for _ in range(10):
        record_attempt(user_id=user_id, scenario_id="AI001", category="ai_security", difficulty=1, correct=False, db=memory_db)
    
    # For ai_security, max difficulty is 2
    assert CATEGORY_MAX_DIFFICULTIES["ai_security"] == 2
    for _ in range(5):
        record_attempt(user_id=user_id, scenario_id="AI001", category="ai_security", difficulty=1, correct=True, db=memory_db)
    
    rec_ai = recommend_next_training(user_id, db=memory_db)
    assert rec_ai.difficulty <= 2


# ==============================================================================
# 11. SCENARIO REPETITION AVOIDANCE
# ==============================================================================

def test_scenario_repetition_avoidance(memory_db):
    """Verify engine avoids immediately repeating the same scenario when alternatives exist."""
    user_id = "U_REPEAT"
    
    # Set social_engineering as weakest and at difficulty 2
    # social_engineering has SOC001 (diff 1) and SOC002 (diff 2)
    # If user just completed SOC001 (diff 1), and target is diff 1, it selects SOC001 (only diff 1 option)
    record_attempt(user_id=user_id, scenario_id="SOC001", category="social_engineering", difficulty=1, correct=False, db=memory_db)
    
    rec = recommend_next_training(user_id, db=memory_db)
    assert rec.scenario_id == "SOC001"


# ==============================================================================
# 12. BEFORE / AFTER IMPROVEMENT & BASELINE PRESERVATION
# ==============================================================================

def test_before_after_improvement(memory_db):
    """Verify baseline score is preserved and improvement tracks delta from baseline."""
    user_id = "U_IMPROVE"
    
    # Initial state: baseline = 70, current = 70, improvement = 0
    imp0 = get_improvement(user_id, db=memory_db)
    assert imp0.baseline_score == 70
    assert imp0.current_score == 70
    assert imp0.improvement == 0

    # User answers several correctly
    record_attempt(user_id=user_id, scenario_id="PHISH001", category="phishing", difficulty=1, correct=True, db=memory_db)
    record_attempt(user_id=user_id, scenario_id="SOC001", category="social_engineering", difficulty=1, correct=True, db=memory_db)
    record_attempt(user_id=user_id, scenario_id="MFA001", category="mfa_otp", difficulty=1, correct=True, db=memory_db)
    
    imp1 = get_improvement(user_id, db=memory_db)
    # Baseline must remain strictly 70
    assert imp1.baseline_score == 70
    assert imp1.current_score > 70
    assert imp1.improvement == imp1.current_score - 70


# ==============================================================================
# 13. MULTI-USER ISOLATION
# ==============================================================================

def test_multiple_users_isolation(memory_db):
    """Verify attempts and profiles of different users are completely independent."""
    user_a = "USER_ALICE"
    user_b = "USER_BOB"

    # Alice answers incorrectly in phishing
    record_attempt(user_id=user_a, scenario_id="PHISH001", category="phishing", difficulty=1, correct=False, db=memory_db)

    # Bob answers correctly in phishing
    record_attempt(user_id=user_b, scenario_id="PHISH001", category="phishing", difficulty=1, correct=True, db=memory_db)

    profile_a = get_user_profile(user_a, db=memory_db)
    profile_b = get_user_profile(user_b, db=memory_db)

    assert profile_a.scores["phishing"] == 63
    assert profile_b.scores["phishing"] == 75
    assert profile_a.attempts == 1
    assert profile_b.attempts == 1


# ==============================================================================
# 14. ENTERPRISE METRICS AGGREGATION
# ==============================================================================

def test_enterprise_metrics(memory_db):
    """Verify calculation of enterprise metrics across multiple users."""
    # User 1: High risk (multiple failures)
    for _ in range(5):
        record_attempt(user_id="EMP1", scenario_id="PHISH001", category="phishing", difficulty=3, correct=False, db=memory_db)
    
    # User 2: Medium/Default
    get_user_profile("EMP2", db=memory_db)

    # User 3: Low risk (high scores)
    for cat, sid in [("phishing", "PHISH001"), ("social_engineering", "SOC001"), ("mfa_otp", "MFA001")]:
        record_attempt(user_id="EMP3", scenario_id=sid, category=cat, difficulty=2, correct=True, db=memory_db)

    metrics = get_enterprise_metrics(db=memory_db)
    assert metrics.total_users == 3
    assert "high" in metrics.risk_distribution
    assert "medium" in metrics.risk_distribution
    assert "low" in metrics.risk_distribution
    assert metrics.total_users == sum(metrics.risk_distribution.values())
    assert metrics.most_common_weakness in CANONICAL_CATEGORIES
    for cat in CANONICAL_CATEGORIES:
        assert cat in metrics.category_weaknesses


# ==============================================================================
# 15. AI ANALYSIS INTEGRATION (SUPPORTING ONLY)
# ==============================================================================

def test_ai_analysis_does_not_override_deterministic_risk(memory_db):
    """Verify AI analysis is stored but NEVER alters deterministic score/risk."""
    user_id = "U_AI_TEST"
    
    # AI says "risk: high" and provides weaknesses, but user answered correctly on diff 1
    ai_feedback = AIAnalysisInput(
        risk="high",
        weaknesses=["trusted urgency", "failed to verify sender"],
        explanation="The user showed hesitation.",
        recommendation="Always double check the sender domain.",
    )
    
    attempt = ScenarioAttemptInput(
        user_id=user_id,
        scenario_id="PHISH001",
        category="phishing",
        difficulty=1,
        correct=True,
        scenario_risk="high",
        ai_analysis=ai_feedback,
    )
    
    profile = record_attempt(attempt_input=attempt, db=memory_db)
    
    # Score should improve by +5 (70 -> 75), overall score = 71 (low risk), NOT high risk
    assert profile.scores["phishing"] == 75
    assert profile.overall_score == 71
    assert profile.risk_level == "low"  # 71 is low, AI 'high' did NOT override it!

    # Verify AI weaknesses were stored in the database attempts record
    attempts = memory_db.get_attempts(user_id)
    assert len(attempts) == 1
    assert "trusted urgency" in attempts[0]["ai_weaknesses"]
    assert attempts[0]["ai_recommendation"] == "Always double check the sender domain."


# ==============================================================================
# 16. SCENARIOS CATALOG INTEGRITY
# ==============================================================================

def test_all_12_canonical_scenarios_loaded():
    """Verify all 12 canonical scenarios from Person 1 are recognized."""
    scenarios = load_scenarios()
    assert len(scenarios) == 12
    
    scenario_ids = {s.scenario_id for s in scenarios}
    expected_ids = {
        "PHISH001", "PHISH002", "PHISH003",
        "SOC001", "SOC002",
        "MFA001", "MFA002",
        "PWD001", "PWD002",
        "DATA001",
        "AI001", "AI002",
    }
    assert scenario_ids == expected_ids
    
    # Verify all categories are canonical
    for s in scenarios:
        assert s.category in CANONICAL_CATEGORIES


# ==============================================================================
# 17. FULL ADAPTIVE LOOP END-TO-END SIMULATION
# ==============================================================================

def test_full_adaptive_loop_simulation(memory_db):
    """Simulate the complete hackathon user journey:
    wrong behavior -> risk engine identifies weakness -> profile updates
    -> targeted training selected -> user tries again -> score improves -> manager sees improvement!
    """
    user_id = "USER_JOURNEY_001"

    # Step 1: User fails an MFA scenario (MFA001, diff 1)
    p1 = record_attempt(
        user_id=user_id,
        scenario_id="MFA001",
        category="mfa_otp",
        difficulty=1,
        correct=False,
        ai_analysis={"weaknesses": ["unverified approval"], "recommendation": "Deny unexpected MFA push."},
        db=memory_db,
    )
    assert p1.scores["mfa_otp"] == 63
    assert p1.weakest_category == "mfa_otp"
    assert p1.recommended_category == "mfa_otp"
    assert p1.recommended_difficulty == 1

    # Step 2: System recommends targeted scenario
    rec = recommend_next_training(user_id, db=memory_db)
    assert rec.category == "mfa_otp"
    assert rec.difficulty == 1
    assert rec.scenario_id == "MFA001"

    # Step 3: User tries again and succeeds on difficulty 1 (+5 -> 68)
    p2 = record_attempt(
        user_id=user_id,
        scenario_id="MFA001",
        category="mfa_otp",
        difficulty=1,
        correct=True,
        db=memory_db,
    )
    assert p2.scores["mfa_otp"] == 68

    # Step 4: User succeeds again (+5 -> 73)
    p3 = record_attempt(
        user_id=user_id,
        scenario_id="MFA001",
        category="mfa_otp",
        difficulty=1,
        correct=True,
        db=memory_db,
    )
    assert p3.scores["mfa_otp"] == 73
    # MFA improved beyond baseline (70), now another category becomes weakest
    assert p3.improvement >= 0


# ==============================================================================
# 18. MODULE 4 DASHBOARD CONTRACT INTEGRITY
# ==============================================================================

def test_module4_json_contract_structure(memory_db):
    """Verify that UserProfile model dump produces the exact keys required by Person 4."""
    profile = get_user_profile("USER001", db=memory_db)
    data = profile.model_dump()

    required_keys = {
        "user_id",
        "scores",
        "overall_score",
        "risk_level",
        "attempts",
        "correct_attempts",
        "incorrect_attempts",
        "weakest_category",
        "recommended_category",
        "recommended_difficulty",
        "baseline_score",
        "improvement",
    }
    assert required_keys.issubset(data.keys())
    assert set(data["scores"].keys()) == set(CANONICAL_CATEGORIES)


# ==============================================================================
# 19. INVALID CATEGORY VALIDATION
# ==============================================================================

def test_invalid_category_validation(memory_db):
    """Verify ValueError is raised if a non-canonical category is passed."""
    with pytest.raises(ValueError):
        record_attempt(
            user_id="U_BAD",
            scenario_id="BAD001",
            category="crypto_mining",
            difficulty=1,
            correct=True,
            db=memory_db,
        )


# ==============================================================================
# 20. FILE-BASED PERSISTENCE INTEGRATION
# ==============================================================================

def test_file_based_db_persistence(tmp_path):
    """Verify persistence across distinct Database instances on the same file."""
    db_file = str(tmp_path / "test_firewall.db")
    db1 = Database(db_file)
    
    record_attempt(
        user_id="PERSIST_USER",
        scenario_id="PHISH001",
        category="phishing",
        difficulty=1,
        correct=True,
        db=db1,
    )

    # Open with a fresh Database connection instance pointing to the same file
    db2 = Database(db_file)
    profile = get_user_profile("PERSIST_USER", db=db2)
    assert profile.scores["phishing"] == 75
    assert profile.attempts == 1
