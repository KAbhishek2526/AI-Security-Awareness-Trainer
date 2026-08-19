"""
User Security Profile Management (Person 3 Ownership)
Manages profile state updates, historical weakness tracking, and score adjustments.
"""

from typing import Dict, List, Optional
from app.schemas.risk import RiskProfileSchema, CategoryScoreSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel
from app.risk.scoring import DeterministicRiskScorer


class UserProfileManager:
    """Manages user security risk profiles and weakness progression."""

    @staticmethod
    def create_default_profile(user_id: str) -> RiskProfileSchema:
        """Create an initial default security profile for a new user."""
        categories = {
            cat.value: CategoryScoreSchema(
                category=cat,
                score=100.0,
                attempts_count=0,
                correct_count=0
            )
            for cat in ThreatCategory
        }
        
        return RiskProfileSchema(
            user_id=user_id,
            overall_score=100.0,
            risk_level=RiskLevel.LOW,
            category_scores=categories,
            top_weaknesses=[],
            recommended_next_category=ThreatCategory.PHISHING,
            recommended_next_difficulty=DifficultyLevel.BEGINNER,
            total_attempts=0,
            improvement_rate=0.0
        )

    @classmethod
    def update_profile_with_analysis(
        cls,
        existing_profile: RiskProfileSchema,
        analysis: AIAnalysisSchema
    ) -> RiskProfileSchema:
        """Update user profile deterministically based on new AI analysis output."""
        category_key = analysis.category.value
        cat_score_obj = existing_profile.category_scores.get(
            category_key,
            CategoryScoreSchema(category=analysis.category, score=100.0, attempts_count=0, correct_count=0)
        )
        
        # Update category counts
        cat_score_obj.attempts_count += 1
        if analysis.analysis.correct:
            cat_score_obj.correct_count += 1
            
        cat_score_obj.score = DeterministicRiskScorer.calculate_category_score(
            cat_score_obj.correct_count, cat_score_obj.attempts_count
        )
        existing_profile.category_scores[category_key] = cat_score_obj

        # Update overall score and risk level deterministically
        scores_map = {k: v.score for k, v in existing_profile.category_scores.items() if v.attempts_count > 0}
        new_overall = DeterministicRiskScorer.calculate_overall_score(scores_map)
        existing_profile.overall_score = new_overall
        existing_profile.risk_level = DeterministicRiskScorer.classify_risk_level(new_overall)
        
        # Track weaknesses
        for w in analysis.analysis.weaknesses:
            if w not in existing_profile.top_weaknesses:
                existing_profile.top_weaknesses.append(w)
                
        existing_profile.total_attempts += 1
        existing_profile.recommended_next_category = analysis.personalization.recommended_topic
        existing_profile.recommended_next_difficulty = analysis.personalization.recommended_difficulty

        return existing_profile
