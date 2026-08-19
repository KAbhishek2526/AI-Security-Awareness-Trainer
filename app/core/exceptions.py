"""Custom exception hierarchy for the AI Security Awareness Trainer."""


class SecurityTrainerException(Exception):
    """Base exception for all application errors."""
    pass


class ScenarioNotFoundError(SecurityTrainerException):
    """Raised when a requested scenario cannot be found."""
    pass


class InvalidScenarioDataError(SecurityTrainerException):
    """Raised when scenario data fails validation."""
    pass


class AIProviderError(SecurityTrainerException):
    """Raised when calling the LLM provider fails."""
    pass


class AISafetyViolationError(SecurityTrainerException):
    """Raised when prompt or LLM response violates safety guardrails."""
    pass


class RiskScoringError(SecurityTrainerException):
    """Raised when risk score calculation encounters an error."""
    pass


class UserProfileNotFoundError(SecurityTrainerException):
    """Raised when a user security profile cannot be retrieved."""
    pass
