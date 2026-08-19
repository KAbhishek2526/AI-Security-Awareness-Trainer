"""
Core constants and enumeration types for AI Security Awareness Trainer.
All team members MUST import and use these enums to ensure consistency across modules.
"""

from enum import Enum, IntEnum
from typing import Set


class ThreatCategory(str, Enum):
    """Standardized threat categories across all scenarios and risk scoring."""
    PHISHING = "phishing"
    SOCIAL_ENGINEERING = "social_engineering"
    PASSWORD_SECURITY = "password_security"
    MFA_SECURITY = "mfa_security"
    DATA_PROTECTION = "data_protection"
    AI_SECURITY = "ai_security"


class RiskLevel(str, Enum):
    """Standardized risk classifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DifficultyLevel(IntEnum):
    """Standardized scenario difficulty levels."""
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3


# Controlled security weaknesses vocabulary (Person 2 requirement)
CONTROLLED_WEAKNESSES: Set[str] = {
    "urgency_bias",
    "authority_trust",
    "sender_not_verified",
    "domain_not_verified",
    "link_not_verified",
    "attachment_not_verified",
    "credential_sharing",
    "password_sharing",
    "password_reuse",
    "weak_password_practice",
    "mfa_fatigue",
    "mfa_push_approval",
    "otp_sharing",
    "tailgating_acceptance",
    "physical_security_awareness",
    "sensitive_data_sharing",
    "unsafe_data_transfer",
    "pii_handling",
    "public_ai_data_upload",
    "confidential_data_to_ai",
    "ai_output_overtrust",
    "secret_exposure",
    "hardcoded_secret",
    "lack_of_verification",
    "social_engineering_susceptibility",
    "other",
}


def normalize_weakness(weakness_str: str) -> str:
    """
    Normalize an arbitrary string from LLM output to the closest valid controlled weakness label.
    If no match exists in CONTROLLED_WEAKNESSES, returns 'other'.
    """
    if not weakness_str:
        return "other"
    
    cleaned = weakness_str.strip().lower().replace("-", "_").replace(" ", "_")
    if cleaned in CONTROLLED_WEAKNESSES:
        return cleaned

    # Substring matching heuristics
    if "urgent" in cleaned or "urgency" in cleaned:
        return "urgency_bias"
    if "authority" in cleaned or "ceo" in cleaned:
        return "authority_trust"
    if "domain" in cleaned:
        return "domain_not_verified"
    if "sender" in cleaned:
        return "sender_not_verified"
    if "link" in cleaned:
        return "link_not_verified"
    if "attachment" in cleaned:
        return "attachment_not_verified"
    if "otp" in cleaned:
        return "otp_sharing"
    if "mfa" in cleaned or "push" in cleaned:
        return "mfa_fatigue"
    if "tailgat" in cleaned or "door" in cleaned:
        return "tailgating_acceptance"
    if "password_share" in cleaned or "spreadsheet" in cleaned:
        return "password_sharing"
    if "password_reuse" in cleaned:
        return "password_reuse"
    if "weak_pass" in cleaned:
        return "weak_password_practice"
    if "credential" in cleaned or "pass" in cleaned:
        return "credential_sharing"
    if "ai" in cleaned and ("public" in cleaned or "upload" in cleaned or "chat" in cleaned):
        return "public_ai_data_upload"
    if "secret" in cleaned or "api_key" in cleaned or "key" in cleaned:
        return "hardcoded_secret"
    if "pii" in cleaned or "customer" in cleaned or "sensitive" in cleaned:
        return "sensitive_data_sharing"
    if "verif" in cleaned:
        return "lack_of_verification"
    if "social" in cleaned or "vish" in cleaned:
        return "social_engineering_susceptibility"

    return "other"


# Helper mappings and validation sets
VALID_THREAT_CATEGORIES = {category.value for category in ThreatCategory}
VALID_RISK_LEVELS = {level.value for level in RiskLevel}
VALID_DIFFICULTY_LEVELS = {diff.value for diff in DifficultyLevel}
