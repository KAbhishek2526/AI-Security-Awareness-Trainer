"""
AI Analysis Schema (Person 2 Contract)
Defines the structured output returned by Person 2 AI Coach after evaluating a scenario attempt.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel


class DecisionSchema(BaseModel):
    """Decision outcome and semantic risk signal evaluated by AI."""
    correct: bool = Field(..., description="Whether user chose the correct answer")
    risk_signal: RiskLevel = Field(..., description="Evaluated risk signal: low, medium, high")


class SecurityAnalysisSchema(BaseModel):
    """Semantic breakdown of cognitive weaknesses and security reasoning."""
    weaknesses: List[str] = Field(default_factory=list, description="Identified cognitive/security weaknesses from controlled vocabulary")
    reasoning: str = Field(default="", description="Detailed semantic breakdown of user's reasoning")


class FeedbackDetailSchema(BaseModel):
    """Structured personalized feedback explaining the risk and safer alternatives."""
    what_happened: str = Field(default="", description="Summary of user's decision")
    why_risky: str = Field(default="", description="Why the choice poses a security risk")
    safer_behavior: str = Field(default="", description="Action to take instead")
    learning_point: str = Field(default="", description="One memorable key security takeaway")
    
    # Backwards compatibility fields for Person 3 & Person 4
    explanation: str = Field(default="", description="Full personalized explanation text")
    learning_points: List[str] = Field(default_factory=list, description="List of learning takeaways")


class SocraticCoachingSchema(BaseModel):
    """Socratic coaching question encouraging security reasoning."""
    question: str = Field(..., description="Guiding question promoting security critical thinking")


class RecommendationDetailSchema(BaseModel):
    """Next step recommendations passed to Person 3 Personalization Engine."""
    topic: ThreatCategory = Field(..., description="Target category for retraining")
    difficulty: DifficultyLevel = Field(..., description="Target difficulty for next scenario")
    reason: str = Field(..., description="Rationale for retraining recommendation")
    
    # Backwards compatibility fields
    recommended_topic: Optional[ThreatCategory] = None
    recommended_difficulty: Optional[DifficultyLevel] = None


class AnalysisDetailSchema(BaseModel):
    """Legacy backward-compatible analysis detail schema for Person 3."""
    correct: bool = Field(..., description="Whether user chose correct answer")
    risk: RiskLevel = Field(..., description="Evaluated risk level")
    weaknesses: List[str] = Field(default_factory=list, description="Identified weaknesses")


class PersonalizationRecommendationSchema(BaseModel):
    """Legacy backward-compatible recommendation schema for Person 3."""
    recommended_topic: ThreatCategory = Field(..., description="Target category")
    recommended_difficulty: DifficultyLevel = Field(..., description="Target difficulty")
    reason: str = Field(..., description="Rationale")


class AIAnalysisSchema(BaseModel):
    """Complete output contract from Person 2 AI Coach."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "USER001",
                "scenario_id": "PHISH001",
                "category": "phishing",
                "decision": {
                    "correct": False,
                    "risk_signal": "high"
                },
                "security_analysis": {
                    "weaknesses": ["urgency_bias", "domain_not_verified"],
                    "reasoning": "User succumbed to artificial urgency without checking sender domain."
                },
                "feedback": {
                    "what_happened": "You clicked the password reset link immediately.",
                    "why_risky": "The link points to a lookalike phishing domain designed to steal credentials.",
                    "safer_behavior": "Verify the sender address and log in directly through official IT portals.",
                    "learning_point": "Never allow artificial urgency to bypass domain verification.",
                    "explanation": "You clicked the password reset link immediately because of artificial urgency. The link points to a lookalike phishing domain.",
                    "learning_points": ["Never allow artificial urgency to bypass domain verification."]
                },
                "coaching": {
                    "question": "What could you independently verify before clicking a password-reset link?"
                },
                "recommendation": {
                    "topic": "phishing",
                    "difficulty": 1,
                    "reason": "User needs reinforcement on domain verification under artificial urgency."
                }
            }
        }
    )

    user_id: str = Field(..., description="User ID")
    scenario_id: str = Field(..., description="Scenario ID")
    category: ThreatCategory = Field(..., description="Threat category")
    
    decision: DecisionSchema = Field(..., description="Core decision and risk signal")
    security_analysis: SecurityAnalysisSchema = Field(..., description="Semantic weaknesses and reasoning breakdown")
    feedback: FeedbackDetailSchema = Field(..., description="Structured personalized feedback")
    coaching: SocraticCoachingSchema = Field(..., description="Socratic question encouraging security thinking")
    recommendation: RecommendationDetailSchema = Field(..., description="Learning pathway recommendation")
    
    # Optional/populated backward-compatible fields for Person 3 & Person 4
    analysis: Optional[AnalysisDetailSchema] = None
    personalization: Optional[PersonalizationRecommendationSchema] = None

    @model_validator(mode="after")
    def populate_backwards_compatible_fields(self):
        """Ensure legacy fields (analysis, personalization, feedback.explanation) are populated."""
        if not self.analysis:
            self.analysis = AnalysisDetailSchema(
                correct=self.decision.correct,
                risk=self.decision.risk_signal,
                weaknesses=self.security_analysis.weaknesses
            )
        if not self.personalization:
            self.personalization = PersonalizationRecommendationSchema(
                recommended_topic=self.recommendation.topic,
                recommended_difficulty=self.recommendation.difficulty,
                reason=self.recommendation.reason
            )
        if not self.feedback.explanation:
            self.feedback.explanation = f"{self.feedback.what_happened} {self.feedback.why_risky} {self.feedback.safer_behavior}".strip()
        if not self.feedback.learning_points and self.feedback.learning_point:
            self.feedback.learning_points = [self.feedback.learning_point]
        return self
