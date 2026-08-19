"""SQLite database persistence layer for Module 3."""

import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

# Constants for database initialization
INITIAL_CATEGORY_SCORE: int = 70


def _classify_risk(score: int) -> str:
    """Internal helper to classify risk without circular imports."""
    if score >= 71:
        return "low"
    elif score >= 41:
        return "medium"
    return "high"


class Database:
    """SQLite Database manager for user awareness profiles and scenario attempts."""

    def __init__(self, db_path: str = "data/firewall.db"):
        self.db_path = db_path
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Return the database connection with row factory enabled."""
        return self._conn

    def init_db(self) -> None:
        """Initialize database schema tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Profiles table (stores baseline and current scores per category)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id TEXT PRIMARY KEY,
                    phishing_score INTEGER DEFAULT 70,
                    social_engineering_score INTEGER DEFAULT 70,
                    mfa_otp_score INTEGER DEFAULT 70,
                    password_security_score INTEGER DEFAULT 70,
                    data_protection_score INTEGER DEFAULT 70,
                    ai_security_score INTEGER DEFAULT 70,
                    overall_score INTEGER DEFAULT 70,
                    risk_level TEXT DEFAULT 'medium',
                    baseline_score INTEGER DEFAULT 70,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)

            # Attempts history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    scenario_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    difficulty INTEGER NOT NULL,
                    user_answer TEXT,
                    correct BOOLEAN NOT NULL,
                    scenario_risk TEXT,
                    ai_weaknesses TEXT,
                    ai_explanation TEXT,
                    ai_recommendation TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def get_or_create_user(self, user_id: str) -> Dict[str, Any]:
        """Fetch existing user profile or initialize a new user profile with baseline score 70."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)

            # Insert new user
            cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            
            # Insert initial profile
            initial_risk = _classify_risk(INITIAL_CATEGORY_SCORE)
            cursor.execute("""
                INSERT INTO profiles (
                    user_id,
                    phishing_score,
                    social_engineering_score,
                    mfa_otp_score,
                    password_security_score,
                    data_protection_score,
                    ai_security_score,
                    overall_score,
                    risk_level,
                    baseline_score,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                user_id,
                INITIAL_CATEGORY_SCORE,
                INITIAL_CATEGORY_SCORE,
                INITIAL_CATEGORY_SCORE,
                INITIAL_CATEGORY_SCORE,
                INITIAL_CATEGORY_SCORE,
                INITIAL_CATEGORY_SCORE,
                INITIAL_CATEGORY_SCORE,
                initial_risk,
                INITIAL_CATEGORY_SCORE,
            ))
            conn.commit()

            cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
            return dict(cursor.fetchone())

    def update_profile_scores(
        self,
        user_id: str,
        category_scores: Dict[str, int],
        overall_score: int,
        risk_level: str,
    ) -> Dict[str, Any]:
        """Update current category and overall scores for a user while preserving the baseline score."""
        self.get_or_create_user(user_id)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE profiles
                SET phishing_score = ?,
                    social_engineering_score = ?,
                    mfa_otp_score = ?,
                    password_security_score = ?,
                    data_protection_score = ?,
                    ai_security_score = ?,
                    overall_score = ?,
                    risk_level = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (
                category_scores.get("phishing", INITIAL_CATEGORY_SCORE),
                category_scores.get("social_engineering", INITIAL_CATEGORY_SCORE),
                category_scores.get("mfa_otp", INITIAL_CATEGORY_SCORE),
                category_scores.get("password_security", INITIAL_CATEGORY_SCORE),
                category_scores.get("data_protection", INITIAL_CATEGORY_SCORE),
                category_scores.get("ai_security", INITIAL_CATEGORY_SCORE),
                overall_score,
                risk_level,
                user_id,
            ))
            conn.commit()
            cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
            return dict(cursor.fetchone())

    def record_attempt(
        self,
        user_id: str,
        scenario_id: str,
        category: str,
        difficulty: int,
        user_answer: Optional[str],
        correct: bool,
        scenario_risk: Optional[str] = None,
        ai_weaknesses: Optional[List[str]] = None,
        ai_explanation: Optional[str] = None,
        ai_recommendation: Optional[str] = None,
    ) -> int:
        """Insert a scenario attempt record."""
        self.get_or_create_user(user_id)
        weaknesses_json = json.dumps(ai_weaknesses or [])
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO attempts (
                    user_id,
                    scenario_id,
                    category,
                    difficulty,
                    user_answer,
                    correct,
                    scenario_risk,
                    ai_weaknesses,
                    ai_explanation,
                    ai_recommendation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                scenario_id,
                category,
                difficulty,
                user_answer,
                1 if correct else 0,
                scenario_risk,
                weaknesses_json,
                ai_explanation,
                ai_recommendation,
            ))
            conn.commit()
            return cursor.lastrowid

    def get_attempts(self, user_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve attempt history for a specific user, optionally filtered by category."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute(
                    "SELECT * FROM attempts WHERE user_id = ? AND category = ? ORDER BY id ASC",
                    (user_id, category),
                )
            else:
                cursor.execute(
                    "SELECT * FROM attempts WHERE user_id = ? ORDER BY id ASC",
                    (user_id,),
                )
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                if item.get("ai_weaknesses"):
                    try:
                        item["ai_weaknesses"] = json.loads(item["ai_weaknesses"])
                    except Exception:
                        item["ai_weaknesses"] = []
                else:
                    item["ai_weaknesses"] = []
                item["correct"] = bool(item["correct"])
                results.append(item)
            return results

    def get_attempt_counts(self, user_id: str) -> Dict[str, int]:
        """Get total, correct, and incorrect attempt counts for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) as correct_count,
                    SUM(CASE WHEN correct = 0 THEN 1 ELSE 0 END) as incorrect_count
                FROM attempts
                WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            total = row["total"] or 0
            correct = row["correct_count"] or 0
            incorrect = row["incorrect_count"] or 0
            return {
                "attempts": total,
                "correct_attempts": correct,
                "incorrect_attempts": incorrect,
            }

    def get_all_profiles(self) -> List[Dict[str, Any]]:
        """Retrieve all user profiles for enterprise aggregation."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles ORDER BY user_id ASC")
            return [dict(r) for r in cursor.fetchall()]

    def reset_database(self) -> None:
        """Clear all data for testing or reset."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attempts")
            cursor.execute("DELETE FROM profiles")
            cursor.execute("DELETE FROM users")
            conn.commit()


# Default singleton instance
_default_db: Optional[Database] = None


def get_db(db_path: Optional[str] = None) -> Database:
    """Get or create the Database instance."""
    global _default_db
    if db_path:
        return Database(db_path)
    if _default_db is None:
        _default_db = Database()
    return _default_db
