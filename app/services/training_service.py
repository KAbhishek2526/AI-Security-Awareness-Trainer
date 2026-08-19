"""
Training Service Interface (Person 3 Ownership)
Manages training session progression and baseline metrics.
"""

from typing import Dict, Any


class TrainingService:
    """Service tracking training sessions and completion metrics."""

    def calculate_improvement(self, baseline_score: float, current_score: float) -> float:
        """Calculate score improvement percentage."""
        if baseline_score == 0:
            return 0.0
        return round(((current_score - baseline_score) / baseline_score) * 100.0, 1)
