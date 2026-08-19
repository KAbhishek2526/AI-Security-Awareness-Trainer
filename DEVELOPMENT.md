# Development Guide

This guide covers setup commands, running the application, testing, and git operations.

---

## 🛠️ Environment Setup

### Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12 installed
- Git installed

### Quick Setup Commands

#### Windows (PowerShell):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

#### macOS / Linux (Bash):
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Running the Project

### Running Streamlit UI
```bash
streamlit run app/main.py
```

### Running Integration Demo Script
```bash
python scripts/run_demo.py
```

### Running Seed Script
```bash
python scripts/seed_data.py
```

---

## 🧪 Running Tests

Run unit test suite:
```bash
pytest
```

Run test suite with detailed output:
```bash
pytest -v
```

---

## 🌿 Git Commands Cheat Sheet

```bash
# Check status
git status

# Create and switch to person branch
git checkout -b person1-scenarios

# Commit changes
git add .
git commit -m "[Person-1] feat: add initial phishing scenarios"

# Push branch to remote
git push origin person1-scenarios
```
