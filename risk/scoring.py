"""Deterministic scoring and risk classification engine for Module 3."""

from typing import Dict
from risk.models import (
    CANONICAL_CATEGORIES,
    INITIAL_CATEGORY_SCORE,
    RiskLevelType,
)

# Deterministic score adjustment deltas based on difficulty
CORRECT_DELTAS: Dict[int, int] = {
    1: 5,
    2: 7,
    3: 9,
}

INCORRECT_DELTAS: Dict[int, int] = {
    1: -7,
    2: -10,
    3: -13,
}


def clamp_score(score: int) -> int:
    """Clamp score strictly between 0 and 100."""
    return max(0, min(100, score))


def update_category_score(current_score: int, correct: bool, difficulty: int) -> int:
    """Calculate the new category score deterministically based on correctness and difficulty.
    
    Difficulty weights:
      - Correct: diff 1 (+5), diff 2 (+7), diff 3 (+9)
      - Incorrect: diff 1 (-7), diff 2 (-10), diff 3 (-13)
    Clamped to 0..100.
    """
    diff_key = difficulty if difficulty in (1, 2, 3) else max(1, min(3, difficulty))
    if correct:
        delta = CORRECT_DELTAS.get(diff_key, 5)
    else:
        delta = INCORRECT_DELTAS.get(diff_key, -7)
    
    new_score = current_score + delta
    return clamp_score(new_score)


def calculate_overall_score(category_scores: Dict[str, int]) -> int:
    """Calculate the overall user score as the arithmetic average of all 6 canonical categories.
    
    Ensures all 6 categories are present (defaults to INITIAL_CATEGORY_SCORE if missing).
    Rounds to the nearest integer.
    """
    total = 0
    for cat in CANONICAL_CATEGORIES:
        total += category_scores.get(cat, INITIAL_CATEGORY_SCORE)
    
    avg = total / len(CANONICAL_CATEGORIES)
    return int(round(avg))


def classify_risk(score: int) -> RiskLevelType:
    """Classify risk level based on exact deterministic score thresholds.
    
    Thresholds:
      - 71 to 100 -> 'low'
      - 41 to 70  -> 'medium'
      - 0 to 40   -> 'high'
    """
    clamped = clamp_score(score)
    if clamped >= 71:
        return "low"
    elif clamped >= 41:
        return "medium"
    else:
        return "high"


def get_weakest_category(category_scores: Dict[str, int]) -> str:
    """Identify the weakest category (lowest score) with deterministic tie-breaking.
    
    If two or more categories tie for the lowest score, ties are broken using
    the canonical category sequence order.
    """
    # Build list of (score, canonical_index, category_name)
    candidates = []
    for idx, cat in enumerate(CANONICAL_CATEGORIES):
        score = category_scores.get(cat, INITIAL_CATEGORY_SCORE)
        candidates.append((score, idx, cat))
    
    # Sort primarily by lowest score, secondarily by canonical index
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[0][2]


def create_initial_scores() -> Dict[str, int]:
    """Return a dictionary of all canonical categories initialized to 70."""
    return {cat: INITIAL_CATEGORY_SCORE for cat in CANONICAL_CATEGORIES}
