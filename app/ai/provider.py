"""
LLM Provider Abstraction Layer (Person 2 Ownership)
Provides unified interface for OpenAI / Gemini / Mock LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from app.core.config import settings
from app.schemas.attempt import ScenarioAttemptSchema


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def analyze_attempt(self, attempt: ScenarioAttemptSchema) -> Dict[str, Any]:
        """Analyze a user scenario attempt and return structured analysis dict."""
        pass


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM Provider for rapid offline testing and fallback."""

    def analyze_attempt(self, attempt: ScenarioAttemptSchema) -> Dict[str, Any]:
        is_correct = attempt.user_answer.strip().lower() == attempt.correct_answer.strip().lower()
        risk = "low" if is_correct else ("high" if attempt.difficulty >= 2 else "medium")
        weaknesses = [] if is_correct else ["urgency_bias", "sender_not_verified"]
        
        return {
            "user_id": attempt.user_id,
            "scenario_id": attempt.scenario_id,
            "category": attempt.category.value,
            "analysis": {
                "correct": is_correct,
                "risk": risk,
                "weaknesses": weaknesses
            },
            "feedback": {
                "explanation": (
                    "Excellent decision! You correctly identified suspicious elements." 
                    if is_correct else 
                    "Caution: The scenario contained artificial urgency designed to rush your decision."
                ),
                "learning_points": [
                    "Always verify external domains independently.",
                    "Do not trust urgent password change prompts."
                ]
            },
            "personalization": {
                "recommended_topic": attempt.category.value,
                "recommended_difficulty": attempt.difficulty.value,
                "reason": "Reinforce scenario analysis under pressure."
            }
        }


def get_llm_provider() -> BaseLLMProvider:
    """Factory function returning active LLM provider instance."""
    # Extensible for OpenAI / Gemini providers based on settings.llm_provider
    return MockLLMProvider()
