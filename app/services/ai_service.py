"""
AI Service Interface (Person 2 Ownership)
Business service integrating LLM provider, prompt generation, guardrails, and structured output validation.
"""

from typing import Optional, Dict, Any
from app.schemas.attempt import ScenarioAttemptSchema
from app.schemas.ai_analysis import AIAnalysisSchema
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel
from app.core.exceptions import AIProviderError, AISafetyViolationError
from app.ai.provider import get_llm_provider, BaseLLMProvider
from app.ai.guardrails import LLMGuardrails


class AIService:
    """Service for AI analysis, security weakness detection, and Socratic coaching feedback."""

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        self.provider = provider or get_llm_provider()
        self.guardrails = LLMGuardrails()

    def analyze_user_attempt(self, attempt: ScenarioAttemptSchema) -> AIAnalysisSchema:
        """
        Analyze a user's scenario attempt and return validated AIAnalysisSchema.
        Applies input sanitization, offensive redirection check, LLM provider execution,
        weakness normalization, and schema validation.
        """
        if not attempt:
            raise ValueError("Scenario attempt payload cannot be None")

        # 1. Sanitize user reasoning text
        reasoning_text = attempt.user_reasoning or ""
        sanitized_reasoning = self.guardrails.sanitize_input(reasoning_text)
        attempt.user_reasoning = sanitized_reasoning

        # 2. Check for offensive redirection attempts
        if self.guardrails.check_offensive_redirection(sanitized_reasoning):
            return self._build_defensive_redirection_response(attempt)

        # 3. Execute LLM Provider analysis
        try:
            raw_analysis = self.provider.analyze_attempt(attempt)
        except Exception as e:
            # Fallback to safe error payload on LLM failure
            raw_analysis = self._build_fallback_payload(attempt, str(e))

        # 4. Normalize weaknesses to controlled vocabulary
        raw_weaknesses = raw_analysis.get("security_analysis", {}).get("weaknesses", [])
        norm_weaknesses = self.guardrails.normalize_weaknesses_list(raw_weaknesses)
        raw_analysis["security_analysis"]["weaknesses"] = norm_weaknesses

        # 5. Return validated Pydantic contract schema
        return AIAnalysisSchema(**raw_analysis)

    def _build_defensive_redirection_response(self, attempt: ScenarioAttemptSchema) -> AIAnalysisSchema:
        """Return educational redirection payload when user submits offensive instructions."""
        payload = {
            "user_id": attempt.user_id,
            "scenario_id": attempt.scenario_id,
            "category": attempt.category.value,
            "decision": {
                "correct": False,
                "risk_signal": RiskLevel.HIGH.value
            },
            "security_analysis": {
                "weaknesses": ["social_engineering_susceptibility"],
                "reasoning": "User prompt requested offensive attack payload or credential harvesting instructions."
            },
            "feedback": {
                "what_happened": "Your input contained requests for offensive cyber exploitation.",
                "why_risky": "Our platform strictly provides defensive security awareness training.",
                "safer_behavior": "Focus on identifying threat indicators and protecting credentials.",
                "learning_point": "Cybersecurity awareness focuses on defense, verification, and threat mitigation.",
                "explanation": "Input contained offensive requests. Platform provides defensive awareness training.",
                "learning_points": ["Cybersecurity awareness focuses on defense and threat mitigation."]
            },
            "coaching": {
                "question": "How can you use defensive verification principles to protect your organization?"
            },
            "recommendation": {
                "topic": attempt.category.value,
                "difficulty": attempt.difficulty.value,
                "reason": "Redirected to defensive cybersecurity education."
            }
        }
        return AIAnalysisSchema(**payload)

    def _build_fallback_payload(self, attempt: ScenarioAttemptSchema, error_msg: str) -> Dict[str, Any]:
        """Fallback payload when LLM provider encounters error."""
        is_correct = (attempt.user_answer.strip().lower() == attempt.correct_answer.strip().lower())
        return {
            "user_id": attempt.user_id,
            "scenario_id": attempt.scenario_id,
            "category": attempt.category.value,
            "decision": {
                "correct": is_correct,
                "risk_signal": RiskLevel.LOW.value if is_correct else RiskLevel.MEDIUM.value
            },
            "security_analysis": {
                "weaknesses": [] if is_correct else ["lack_of_verification"],
                "reasoning": f"Fallback analysis (LLM provider note: {error_msg})."
            },
            "feedback": {
                "what_happened": f"Selected choice: '{attempt.user_answer}'.",
                "why_risky": "Verify independent channels before proceeding.",
                "safer_behavior": "Perform out-of-band verification.",
                "learning_point": "Always verify unexpected prompts.",
                "explanation": f"Selected choice: '{attempt.user_answer}'. Perform out-of-band verification.",
                "learning_points": ["Always verify unexpected prompts."]
            },
            "coaching": {
                "question": "What steps will you take to verify unexpected requests in the future?"
            },
            "recommendation": {
                "topic": attempt.category.value,
                "difficulty": attempt.difficulty.value,
                "reason": "Fallback training recommendation."
            }
        }
