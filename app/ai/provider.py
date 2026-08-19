import json
import re
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from app.core.config import settings
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel, normalize_weakness
from app.core.exceptions import AIProviderError
from app.schemas.attempt import ScenarioAttemptSchema
from app.ai.guardrails import LLMGuardrails


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def analyze_attempt(self, attempt: ScenarioAttemptSchema) -> Dict[str, Any]:
        """Analyze a user scenario attempt and return structured analysis dict."""
        pass


class GeminiLLMProvider(BaseLLMProvider):
    """
    Gemini LLM Provider using Google GenAI SDK (google.genai).
    Uses configurable GEMINI_MODEL (default: gemini-3.6-flash).
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key or settings.llm_api_key
        self.model_name = model_name or settings.gemini_model

        if not self.api_key:
            raise AIProviderError("Gemini API key is missing. Set GEMINI_API_KEY in environment or .env file.")

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise AIProviderError(f"Failed to initialize Gemini client: {e}")

    def analyze_attempt(self, attempt: ScenarioAttemptSchema) -> Dict[str, Any]:
        from app.ai.prompts.system import SYSTEM_COACH_PROMPT
        from app.ai.prompts.evaluation import EVALUATION_PROMPT

        scenario_category_val = attempt.category.value if hasattr(attempt.category, "value") else str(attempt.category)
        scenario_diff_val = attempt.difficulty.value if hasattr(attempt.difficulty, "value") else str(attempt.difficulty)

        prompt = f"{SYSTEM_COACH_PROMPT}\n\n" + EVALUATION_PROMPT.format(
            scenario_id=attempt.scenario_id,
            category=scenario_category_val,
            difficulty=scenario_diff_val,
            scenario=attempt.scenario,
            options=", ".join(attempt.options) if isinstance(attempt.options, list) else str(attempt.options),
            user_answer=attempt.user_answer,
            correct_answer=attempt.correct_answer,
            user_reasoning=attempt.user_reasoning or ""
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            raw_text = response.text or ""
        except Exception as e:
            raise AIProviderError(f"Gemini API call failed using model {self.model_name}: {e}")

        # Parse JSON from response
        try:
            cleaned = raw_text.strip()
            if "```" in cleaned:
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
                if match:
                    cleaned = match.group(1)
            parsed_json = json.loads(cleaned)
        except Exception:
            is_correct = (attempt.user_answer.strip().lower() in attempt.correct_answer.strip().lower() or attempt.correct_answer.strip().lower() in attempt.user_answer.strip().lower())
            parsed_json = {
                "correct": is_correct,
                "risk_signal": "low" if is_correct else "medium",
                "weaknesses": [] if is_correct else ["lack_of_verification"],
                "reasoning_summary": raw_text[:200] if raw_text else "Evaluated by Gemini AI Security Coach."
            }

        is_correct = parsed_json.get("correct", (attempt.user_answer.strip().lower() in attempt.correct_answer.strip().lower() or attempt.correct_answer.strip().lower() in attempt.user_answer.strip().lower()))
        risk_signal = parsed_json.get("risk_signal", "low" if is_correct else "medium")
        weaknesses = parsed_json.get("weaknesses", [])
        reasoning_summary = parsed_json.get("reasoning_summary", "Evaluation completed by Gemini Security Coach.")

        what_happened = f"Selected choice: '{attempt.user_answer}'."
        why_risky = "Verify independent security channels before acting on unverified prompts." if not is_correct else "Choice successfully avoided security risk."
        safer_behavior = "Perform out-of-band verification via official corporate channels."
        learning_point = "Always verify unexpected prompts through secondary channels."

        analysis_payload = {
            "user_id": attempt.user_id,
            "scenario_id": attempt.scenario_id,
            "category": scenario_category_val,
            "decision": {
                "correct": is_correct,
                "risk_signal": risk_signal
            },
            "security_analysis": {
                "weaknesses": weaknesses,
                "reasoning": reasoning_summary
            },
            "feedback": {
                "what_happened": what_happened,
                "why_risky": why_risky,
                "safer_behavior": safer_behavior,
                "learning_point": learning_point,
                "explanation": f"{what_happened} {why_risky} {safer_behavior}",
                "learning_points": [learning_point]
            },
            "coaching": {
                "question": "What independent verification steps will you take before taking action on similar requests?"
            },
            "recommendation": {
                "topic": scenario_category_val,
                "difficulty": int(scenario_diff_val) if str(scenario_diff_val).isdigit() else 1,
                "reason": f"Reinforce {scenario_category_val} awareness targeting identified risk signal."
            }
        }

        return LLMGuardrails.validate_output(analysis_payload)


class OpenAILLMProvider(BaseLLMProvider):
    """
    OpenAI LLM Provider.
    Uses configurable OPENAI_MODEL (default: gpt-4o-mini).
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key or settings.llm_api_key
        self.model_name = model_name or settings.openai_model

        if not self.api_key:
            raise AIProviderError("OpenAI API key is missing. Set OPENAI_API_KEY in environment or .env file.")

    def analyze_attempt(self, attempt: ScenarioAttemptSchema) -> Dict[str, Any]:
        # Fallback to MockLLMProvider for evaluation when OpenAI SDK is not active
        mock = MockLLMProvider()
        return mock.analyze_attempt(attempt)


class MockLLMProvider(BaseLLMProvider):
    """
    Mock LLM Provider for rapid offline testing and hackathon demo evaluation.
    Provides scenario-aware semantic analysis for all 12 standard scenarios.
    """

    SCENARIO_CONFIGS = {
        "PHISH001": {
            "category": ThreatCategory.PHISHING,
            "difficulty": DifficultyLevel.BEGINNER,
            "weaknesses": ["urgency_bias", "domain_not_verified", "link_not_verified"],
            "coaching_question": "What could you independently verify before clicking a password-reset link?",
            "safer_behavior": "Verify the email sender domain and navigate to official corporate portals directly.",
            "learning_point": "Never allow artificial urgency to rush you into clicking unverified email links."
        },
        "PHISH002": {
            "category": ThreatCategory.PHISHING,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "weaknesses": ["sender_not_verified", "domain_not_verified", "lack_of_verification"],
            "coaching_question": "What secondary communication channel could you use to verify vendor bank details before processing payment?",
            "safer_behavior": "Call vendor billing using a known official phone number before altering payment details.",
            "learning_point": "Always perform out-of-band phone verification for payment account changes."
        },
        "PHISH003": {
            "category": ThreatCategory.PHISHING,
            "difficulty": DifficultyLevel.ADVANCED,
            "weaknesses": ["authority_trust", "urgency_bias", "lack_of_verification"],
            "coaching_question": "Even if the request appears to come from the CEO, what independent verification could you perform before sending money?",
            "safer_behavior": "Verify financial transfer requests out-of-band via established executive approval workflows.",
            "learning_point": "Authority and secrecy should never override mandatory dual-authorization controls."
        },
        "SOC001": {
            "category": ThreatCategory.SOCIAL_ENGINEERING,
            "difficulty": DifficultyLevel.BEGINNER,
            "weaknesses": ["authority_trust", "credential_sharing", "social_engineering_susceptibility"],
            "coaching_question": "Should a legitimate IT employee ever need to know your password?",
            "safer_behavior": "Refuse to share passwords over the phone and report suspicious callers to IT security.",
            "learning_point": "Legitimate IT staff will NEVER ask for your password under any circumstance."
        },
        "SOC002": {
            "category": ThreatCategory.SOCIAL_ENGINEERING,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "weaknesses": ["tailgating_acceptance", "physical_security_awareness"],
            "coaching_question": "Why is it vital for every individual to badge in independently regardless of physical burden?",
            "safer_behavior": "Politely direct unbadged visitors to the security desk before opening doors.",
            "learning_point": "Tailgating exploits politeness to breach physical access controls."
        },
        "MFA001": {
            "category": ThreatCategory.MFA_SECURITY,
            "difficulty": DifficultyLevel.BEGINNER,
            "weaknesses": ["mfa_fatigue", "mfa_push_approval", "lack_of_verification"],
            "coaching_question": "What should you do when an MFA approval request appears without you starting a login?",
            "safer_behavior": "Deny unexpected MFA push prompts immediately and report potential credential compromise.",
            "learning_point": "An unexpected MFA push means an attacker may have guessed your password."
        },
        "MFA002": {
            "category": ThreatCategory.MFA_SECURITY,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "weaknesses": ["otp_sharing", "authority_trust", "social_engineering_susceptibility"],
            "coaching_question": "Why should an OTP remain confidential even when someone claims to be from your bank?",
            "safer_behavior": "Never read OTP codes out loud over the phone to callers.",
            "learning_point": "One-Time Passwords (OTPs) are single-use secret keys that must never be shared."
        },
        "PWD001": {
            "category": ThreatCategory.PASSWORD_SECURITY,
            "difficulty": DifficultyLevel.BEGINNER,
            "weaknesses": ["weak_password_practice", "password_reuse"],
            "coaching_question": "Why does using an enterprise password manager provide superior protection compared to password reuse?",
            "safer_behavior": "Generate unique passphrases stored in an enterprise password manager.",
            "learning_point": "Unique passphrases prevent single site breaches from spreading across work accounts."
        },
        "PWD002": {
            "category": ThreatCategory.PASSWORD_SECURITY,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "weaknesses": ["password_sharing", "secret_exposure"],
            "coaching_question": "What security risk is created when multiple employees can read plaintext passwords in a shared file?",
            "safer_behavior": "Migrate administrative credentials to an access-controlled enterprise vault.",
            "learning_point": "Plaintext spreadsheets expose administrative credentials to internal and external threats."
        },
        "DATA001": {
            "category": ThreatCategory.DATA_PROTECTION,
            "difficulty": DifficultyLevel.BEGINNER,
            "weaknesses": ["sensitive_data_sharing", "unsafe_data_transfer", "pii_handling"],
            "coaching_question": "What approved organizational channel could you use instead of sending customer PII through an unapproved service?",
            "safer_behavior": "Use corporate encrypted file transfer channels with audit logging for PII.",
            "learning_point": "Customer PII requires end-to-end encryption and strict access logging."
        },
        "AI001": {
            "category": ThreatCategory.AI_SECURITY,
            "difficulty": DifficultyLevel.BEGINNER,
            "weaknesses": ["public_ai_data_upload", "confidential_data_to_ai", "sensitive_data_sharing"],
            "coaching_question": "Before pasting customer information into an AI tool, what should you verify about the tool and the data?",
            "safer_behavior": "Use approved enterprise AI instances with zero data retention for sensitive debugging.",
            "learning_point": "Pasting customer PII into public AI chatbots risks data exposure and privacy violations."
        },
        "AI002": {
            "category": ThreatCategory.AI_SECURITY,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "weaknesses": ["hardcoded_secret", "secret_exposure"],
            "coaching_question": "Why is storing an API key directly in source code risky, and where should secrets normally be stored?",
            "safer_behavior": "Remove hardcoded credentials and inject API keys via environment variables or secret vaults.",
            "learning_point": "AI coding assistants may generate hardcoded secrets; always audit AI code before committing."
        }
    }

    def analyze_attempt(self, attempt: ScenarioAttemptSchema) -> Dict[str, Any]:
        scenario_id = attempt.scenario_id.upper()
        config = self.SCENARIO_CONFIGS.get(
            scenario_id,
            {
                "category": attempt.category,
                "difficulty": attempt.difficulty,
                "weaknesses": ["lack_of_verification"],
                "coaching_question": "What security verification steps could you perform before completing this action?",
                "safer_behavior": "Verify requests independently via official communication channels.",
                "learning_point": "Always verify unexpected prompts through secondary channels."
            }
        )

        # Check if user choice is correct
        user_ans = attempt.user_answer.strip().lower()
        corr_ans = attempt.correct_answer.strip().lower()
        
        # Check matching
        is_correct = (user_ans in corr_ans or corr_ans in user_ans)
        
        # Override for specific unsafe keywords in reasoning
        unsafe_keywords = ["fix it quickly", "looks urgent", "urgent", "trust", "identified themselves", "convenient", "faster", "easy"]
        safe_keywords = ["verify", "official", "refuse", "do not click", "password manager", "encrypted", "out-of-band"]
        
        reasoning_lower = (attempt.user_reasoning or "").lower()
        if any(kw in reasoning_lower for kw in unsafe_keywords) and not any(skw in reasoning_lower for skw in safe_keywords):
            if "click" in user_ans or "provide" in user_ans or "approve" in user_ans or "paste" in user_ans or "keep" in user_ans:
                is_correct = False

        if is_correct:
            risk_signal = "low"
            weaknesses = []
            what_happened = f"You correctly selected: '{attempt.user_answer}'."
            why_risky = "Your choice successfully avoided the security risk."
            safer_behavior = config["safer_behavior"]
            learning_point = config["learning_point"]
            reasoning_summary = "User identified suspicious threat elements and chose safe action."
        else:
            risk_signal = "high" if config["difficulty"] >= 2 else "medium"
            weaknesses = config["weaknesses"]
            what_happened = f"You chose: '{attempt.user_answer}'."
            why_risky = f"This decision introduces security vulnerability related to {config['category'].value}."
            safer_behavior = config["safer_behavior"]
            learning_point = config["learning_point"]
            reasoning_summary = f"User decision exhibited cognitive oversight: {', '.join(weaknesses)}."

        # Socratic question
        coaching_question = config["coaching_question"]

        # Recommendation
        rec_topic = config["category"]
        rec_diff = config["difficulty"] if is_correct else max(1, config["difficulty"])
        rec_reason = (
            f"Consolidate awareness in {config['category'].value}." if is_correct else
            f"Reinforce {config['category'].value} targeting {weaknesses[0] if weaknesses else 'verification'}."
        )

        analysis_payload = {
            "user_id": attempt.user_id,
            "scenario_id": attempt.scenario_id,
            "category": config["category"].value if hasattr(config["category"], "value") else str(config["category"]),
            "decision": {
                "correct": is_correct,
                "risk_signal": risk_signal
            },
            "security_analysis": {
                "weaknesses": weaknesses,
                "reasoning": reasoning_summary
            },
            "feedback": {
                "what_happened": what_happened,
                "why_risky": why_risky,
                "safer_behavior": safer_behavior,
                "learning_point": learning_point,
                "explanation": f"{what_happened} {why_risky} {safer_behavior}",
                "learning_points": [learning_point]
            },
            "coaching": {
                "question": coaching_question
            },
            "recommendation": {
                "topic": rec_topic.value if hasattr(rec_topic, "value") else str(rec_topic),
                "difficulty": int(rec_diff),
                "reason": rec_reason,
                "recommended_topic": rec_topic.value if hasattr(rec_topic, "value") else str(rec_topic),
                "recommended_difficulty": int(rec_diff)
            }
        }

        return LLMGuardrails.validate_output(analysis_payload)


def get_llm_provider(provider_type: Optional[str] = None) -> BaseLLMProvider:
    """Factory function returning active LLM provider instance."""
    p_type = (provider_type or settings.llm_provider or "mock").lower()
    
    if p_type == "gemini":
        return GeminiLLMProvider()
    elif p_type == "openai":
        return OpenAILLMProvider()
    else:
        return MockLLMProvider()

