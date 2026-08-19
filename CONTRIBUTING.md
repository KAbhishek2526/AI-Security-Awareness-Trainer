# Contributing & Developer Guidelines

Welcome to the **AI HUMAN FIREWALL** collaborative project. To ensure all 4 team members can develop simultaneously during the hackathon without code collisions or merge conflicts, please follow these guidelines strictly.

---

## 👥 Module Ownership Boundaries

Each developer has exclusive ownership over their designated directories and files:

### Person 1: Threat Scenario & Cybersecurity Simulator
- **Primary Directories**: `app/scenarios/`
- **Primary Files**: `app/models/scenario.py`, `app/schemas/scenario.py`, `app/services/scenario_service.py`, `app/scenarios/data/scenarios.json`
- **Rule**: Do NOT edit `app/ai/` or `app/risk/` code directly. Expose interfaces via `app/schemas/scenario.py`.

### Person 2: AI Security Coach
- **Primary Directories**: `app/ai/`
- **Primary Files**: `app/services/ai_service.py`, `app/models/analysis.py`, `app/schemas/ai_analysis.py`, `app/ai/provider.py`, `app/ai/guardrails.py`
- **Rule**: Consume `ScenarioAttemptSchema` from Person 1; produce `AIAnalysisSchema` for Person 3.

### Person 3: Adaptive Risk Engine
- **Primary Directories**: `app/risk/`
- **Primary Files**: `app/services/risk_service.py`, `app/services/personalization_service.py`, `app/services/training_service.py`, `app/models/user_profile.py`, `app/schemas/risk.py`
- **Rule**: Maintain deterministic scoring in Python (`app/risk/scoring.py`). Do not hardcode risk scores in the LLM.

### Person 4: Enterprise Dashboard & Integration
- **Primary Directories**: `app/dashboard/`, `app/api/`
- **Primary Files**: `app/main.py`, `app/dashboard/user_dashboard.py`, `app/dashboard/manager_dashboard.py`, `app/api/routes.py`
- **Rule**: Import service layers from Persons 1, 2, and 3 to assemble UI views and API endpoints.

---

## 🌿 Git Branching Strategy

Never commit directly to `main` or `develop`. Work on your assigned branch:

- `person1-scenarios`
- `person2-ai-coach`
- `person3-risk-personalization`
- `person4-dashboard-integration`

### Branch Workflow
1. Switch to your feature branch:
   ```bash
   git checkout person1-scenarios
   ```
2. Pull latest changes from `develop`:
   ```bash
   git pull origin develop
   ```
3. Commit your changes locally with clear messages.
4. Push to your remote branch:
   ```bash
   git push origin person1-scenarios
   ```
5. Open a Pull Request from your branch into `develop`.

---

## 📝 Commit Conventions

Use concise, descriptive commit messages prefixed with your module tag:

- `[Person-1]` feat: add MFA fatigue scenario catalog
- `[Person-2]` feat: add socratic evaluation prompt and guardrails
- `[Person-3]` feat: implement deterministic overall risk scoring
- `[Person-4]` feat: add risk radar chart to user dashboard
- `[Docs]` docs: update integration contracts in INTEGRATION.md

---

## 🛡️ Avoiding Merge Conflicts

1. **Do not modify files owned by another developer.**
2. If shared core files (`app/core/constants.py`, `app/core/config.py`) require updates, coordinate with the team first.
3. Keep shared imports at the interface level using Pydantic schemas in `app/schemas/`.
