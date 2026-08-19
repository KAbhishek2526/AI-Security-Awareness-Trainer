"""
LLM Safety Guardrails (Person 2 Ownership)
Validates inputs, redirects offensive requests, and enforces controlled weakness output schemas.
"""

from typing import Dict, Any, List
from app.core.exceptions import AISafetyViolationError
from app.core.constants import CONTROLLED_WEAKNESSES, normalize_weakness


class LLMGuardrails:
    """Guardrail validator for LLM prompts and output text."""

    OFFENSIVE_KEYWORDS = [
        "generate malware", "create ransomware", "harvest credentials", 
        "steal password", "bypass mfa", "spoof email", "exploit vulnerability",
        "how to hack", "phishing template", "crack password"
    ]

    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input before sending to LLM."""
        if not text:
            return ""
        # Remove potential instruction override delimiters
        sanitized = text.replace("system:", "").replace("user:", "").replace("assistant:", "")
        sanitized = sanitized.replace("<|im_start|>", "").replace("<|im_end|>", "")
        return sanitized.strip()

    @classmethod
    def check_offensive_redirection(cls, text: str) -> bool:
        """Check if user input contains offensive attack requests requiring redirection."""
        if not text:
            return False
        lower_text = text.lower()
        return any(keyword in lower_text for keyword in cls.OFFENSIVE_KEYWORDS)

    @staticmethod
    def normalize_weaknesses_list(weaknesses: List[str]) -> List[str]:
        """Normalize a list of raw weakness strings to controlled vocabulary."""
        normalized = []
        for w in weaknesses:
            norm_w = normalize_weakness(w)
            if norm_w not in normalized:
                normalized.append(norm_w)
        return normalized

    @classmethod
    def validate_output(cls, analysis_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Verify LLM output JSON contains required schema keys and valid weakness labels."""
        required_root_keys = {"user_id", "scenario_id", "category", "decision", "security_analysis", "feedback", "coaching", "recommendation"}
        
        # Check root structure
        if not required_root_keys.issubset(analysis_dict.keys()):
            missing = required_root_keys - analysis_dict.keys()
            raise AISafetyViolationError(f"LLM output missing required root fields: {missing}")

        # Normalize weaknesses
        raw_weaknesses = analysis_dict.get("security_analysis", {}).get("weaknesses", [])
        analysis_dict["security_analysis"]["weaknesses"] = cls.normalize_weaknesses_list(raw_weaknesses)

        return analysis_dict
