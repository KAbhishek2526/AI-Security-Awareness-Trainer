"""
Seed Script for initializing sample database records.
Run with: python scripts/seed_data.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.database import init_db


def main():
    print("[+] Initializing database schema...")
    init_db()
    print("[+] Database initialized successfully.")


if __name__ == "__main__":
    main()
