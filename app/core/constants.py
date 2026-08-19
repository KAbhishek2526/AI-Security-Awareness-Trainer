"""
Core constants and enumeration types for AI Security Awareness Trainer.
All team members MUST import and use these enums to ensure consistency across modules.
"""

from enum import Enum, IntEnum


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


# Helper mappings and validation sets
VALID_THREAT_CATEGORIES = {category.value for category in ThreatCategory}
VALID_RISK_LEVELS = {level.value for level in RiskLevel}
VALID_DIFFICULTY_LEVELS = {diff.value for diff in DifficultyLevel}
