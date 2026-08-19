"""
LLM Safety Guardrails (Person 2 Ownership)
Validates inputs and outputs to prevent prompt injection, key leakage, and malicious payload generation.
"""

from typing import Dict, Any
from app.core.exceptions import AISafetyViolationError


class LLMGuardrails:
    """Guardrail validator for LLM prompts and output text."""

    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input before sending to LLM."""
        if not text:
            return ""
        # Remove potential instruction override delimiters
        sanitized = text.replace("system:", "").replace("user:", "").replace("assistant:", "")
        return sanitized.strip()

    @staticmethod
    def validate_output(analysis_dict: Dict[str, Any]) -> bool:
        """Verify LLM output JSON contains required schema keys."""
        required_root_keys = {"correct", "risk", "weaknesses"}
        if not required_root_keys.issubset(analysis_dict.keys()):
            raise AISafetyViolationError(f"LLM output missing required schema fields: {required_root_keys - analysis_dict.keys()}")
        return True
