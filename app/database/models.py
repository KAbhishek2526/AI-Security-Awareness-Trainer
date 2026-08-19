"""
Database entities and schema representations for persistence.
"""

from typing import Optional
from pydantic import BaseModel


class UserEntity(BaseModel):
    user_id: str
    name: str
    email: str


class AttemptEntity(BaseModel):
    attempt_id: str
    user_id: str
    scenario_id: str
    category: str
    difficulty: int
    user_answer: str
    is_correct: bool
