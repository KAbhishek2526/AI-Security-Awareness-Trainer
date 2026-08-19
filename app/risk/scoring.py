"""
Deterministic Risk Scoring Logic (Person 3 Ownership)
IMPORTANT ARCHITECTURE PRINCIPLE:
Scoring, risk level thresholds, and progress calculations MUST be calculated deterministically in python code,
NOT by trusting raw LLM text outputs as the authoritative score.
"""

from typing import Dict
from app.core.constants import RiskLevel, ThreatCategory


class DeterministicRiskScorer:
    """Calculates user risk levels and category scores deterministically."""

    @staticmethod
    def calculate_category_score(correct_count: int, total_attempts: int) -> float:
        """Calculate percentage accuracy score for a category (0.0 to 100.0)."""
        if total_attempts == 0:
            return 100.0
        return round((correct_count / total_attempts) * 100.0, 1)

    @staticmethod
    def calculate_overall_score(category_scores: Dict[str, float]) -> float:
        """Calculate unweighted mean score across active categories."""
        if not category_scores:
            return 100.0
        return round(sum(category_scores.values()) / len(category_scores), 1)

    @staticmethod
    def classify_risk_level(overall_score: float) -> RiskLevel:
        """
        Classify risk level according to deterministic enterprise thresholds:
        - overall_score < 60.0  => HIGH risk
        - 60.0 <= score < 80.0 => MEDIUM risk
        - overall_score >= 80.0 => LOW risk
        """
        if overall_score < 60.0:
            return RiskLevel.HIGH
        elif overall_score < 80.0:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
