# AI HUMAN FIREWALL — Adaptive AI Security Awareness Trainer

> **TCS Cybersecurity Hackathon Project**  
> An enterprise-grade, adaptive AI-powered security awareness trainer designed to transform human security culture from the weakest link into an active defense firewall.

---

## 🎯 Problem Statement

Traditional security awareness training is static, generic, and unengaging:
- Annual compliance videos fail to change real-world employee behavior.
- Users memorize answers to pass multiple-choice quizzes without understanding security reasoning.
- Organizations lack real-time visibility into **human risk indicators** and cognitive vulnerabilities (e.g., urgency bias, authority trust).

## 💡 Our Solution: AI Human Firewall

**AI Human Firewall** puts employees inside realistic, safe simulated cybersecurity scenarios (phishing, MFA fatigue, social engineering, password security, data protection, AI security) and uses an **AI Security Coach** to analyze both their actions and their reasoning.

### Core Learning Loop
$$\text{ASSESS} \longrightarrow \text{ANALYZE} \longrightarrow \text{IDENTIFY WEAKNESS} \longrightarrow \text{PERSONALIZE} \longrightarrow \text{RETRAIN} \longrightarrow \text{MEASURE IMPROVEMENT}$$

---

## 🏛️ System Architecture & 4-Layer Separation

The system strictly decouples AI semantic intelligence from authoritative enterprise risk scoring:

```
┌─────────────────────────────────────────────────────────┐
│              Presentation & Integration                 │ (Person 4)
│         Streamlit Dashboard / FastAPI Routes            │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│             Adaptive Risk & Personalization             │ (Person 3)
│           Deterministic Scoring & User Profile          │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                    AI Security Coach                    │ (Person 2)
│             LLM Analysis & Socratic Coaching            │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│          Threat Scenario & Security Simulator           │ (Person 1)
│             Scenario Catalog & Data Schemas             │
└─────────────────────────────────────────────────────────┘
```

- **LLM Responsibilities**: Semantic analysis, reasoning evaluation, cognitive weakness detection, personalized explanations, Socratic coaching.
- **Application Responsibilities**: Input validation, state management, SQLite database persistence, **deterministic risk scoring**, risk thresholds, workflow execution, security controls.

---

## 👥 4-Person Team Ownership Boundaries

| Role | Module Owner | Primary Directories / Files | Responsibilities |
|---|---|---|---|
| **Person 1** | Threat Scenario & Simulator | `app/scenarios/`, `app/models/scenario.py`, `app/schemas/scenario.py` | Safe threat scenarios, phishing, MFA/OTP, passwords, data, AI security scenarios, difficulty levels, interaction data |
| **Person 2** | AI Security Coach | `app/ai/`, `app/services/ai_service.py`, `app/models/analysis.py`, `app/schemas/ai_analysis.py` | LLM provider integration, answer & reasoning analysis, weakness detection, personalized feedback, Socratic prompts, guardrails |
| **Person 3** | Adaptive Risk Engine | `app/risk/`, `app/services/risk_service.py`, `app/services/personalization_service.py`, `app/models/user_profile.py`, `app/schemas/risk.py` | User risk profiles, category scores, deterministic risk level classification, weakness tracking, adaptive next scenario selection |
| **Person 4** | Enterprise Dashboard & Integration | `app/dashboard/`, `app/api/`, `app/main.py`, integration pipelines | Streamlit UI dashboards, user risk visualizer, manager compliance hub, REST API endpoints, app integration |

---

## 🛠️ Technology Stack

- **Language**: Python 3.9+
- **Frontend / Rapid UI**: Streamlit
- **API Framework**: FastAPI & Uvicorn
- **Data Validation & Schemas**: Pydantic v2
- **Database**: SQLite (via standard library / repository pattern)
- **Data & Charts**: Pandas, Plotly
- **Testing**: Pytest
- **AI Abstraction**: Support for OpenAI / Gemini / Azure / Mock providers

---

## 🚀 Quick Start & Local Setup

### 1. Clone Repository & Navigate
```bash
git clone https://github.com/Pheonix-web-sna/AI-Security-Awareness-Trainer.git
cd AI-Security-Awareness-Trainer
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Key environment variables:
```ini
LLM_PROVIDER=mock
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./security_awareness.db
```

### 4. Run the Streamlit Application
```bash
streamlit run app/main.py
```

### 5. Run FastAPI Backend Server (Optional)
```bash
uvicorn app.api.routes:app --reload --port 8000
```

---

## 🌿 Git Branch Strategy & Workflow

To prevent merge conflicts, each developer works exclusively in their dedicated branch:

- `main`: Stable release branch
- `develop`: Shared integration branch
- `person1-scenarios`: Person 1 feature branch
- `person2-ai-coach`: Person 2 feature branch
- `person3-risk-personalization`: Person 3 feature branch
- `person4-dashboard-integration`: Person 4 feature branch

```
main
  ↑
develop
  ↑
feature / person branches
```

---

## 🧪 Running Tests & Verifying Integration

Run unit test suite:
```bash
pytest
```

Run end-to-end integration demo script:
```bash
python scripts/run_demo.py
```