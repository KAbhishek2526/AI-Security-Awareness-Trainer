"""
Database connection and session initialization logic.
Uses SQLite for zero-dependency local development during the hackathon.
"""

import sqlite3
from typing import Optional
from app.core.config import settings


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    target_path = db_path or settings.database_url.replace("sqlite:///", "")
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database tables if they do not exist."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Simple schema initialization
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attempts (
        attempt_id TEXT PRIMARY KEY,
        user_id TEXT,
        scenario_id TEXT,
        category TEXT,
        difficulty INTEGER,
        user_answer TEXT,
        is_correct INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    conn.commit()
    conn.close()
