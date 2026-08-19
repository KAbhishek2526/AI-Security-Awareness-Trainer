"""
AI Service Interface (Person 2 Ownership)
Business service integrating LLM provider, prompt generation, guardrails, and output validation.
"""

from typing import Optional
from app.schemas.attempt import ScenarioAttemptSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.ai.provider import get_llm_provider, BaseLLMProvider
from app.ai.guardrails import LLMGuardrails


class AIService:
    """Service for AI analysis and coaching feedback."""

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        self.provider = provider or get_llm_provider()
        self.guardrails = LLMGuardrails()

    def analyze_user_attempt(self, attempt: ScenarioAttemptSchema) -> AIAnalysisSchema:
        """Analyze a user's attempt payload and return validated AIAnalysisSchema."""
        # Sanitize reasoning input
        if attempt.user_reasoning:
            attempt.user_reasoning = self.guardrails.sanitize_input(attempt.user_reasoning)
        
        # Invoke LLM provider
        raw_output = self.provider.analyze_attempt(attempt)
        
        # Validate schema contract
        return AIAnalysisSchema(**raw_output)
