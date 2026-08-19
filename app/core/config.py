"""
Application settings configuration loader.
Reads environment variables with sensible defaults for local development.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env if present
load_dotenv()


class Settings(BaseModel):
    """Application configuration settings."""
    app_name: str = "AI HUMAN FIREWALL — Adaptive AI Security Awareness Trainer"
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Generic LLM Settings
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    llm_api_key: Optional[str] = os.getenv("LLM_API_KEY", None)
    llm_model: str = os.getenv("LLM_MODEL", "gemini-3.6-flash")

    # Gemini-Specific Settings
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY", os.getenv("LLM_API_KEY", None))
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    # OpenAI-Specific Settings
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", os.getenv("LLM_API_KEY", None))
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Database Settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./security_awareness.db")
    
    # Security Settings
    secret_key: str = os.getenv("SECRET_KEY", "dev_secret_key_32_chars_minimum_length")


settings = Settings()

