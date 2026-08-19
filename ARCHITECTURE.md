# System Architecture Document

## Overview

**AI HUMAN FIREWALL** is built on a 4-tier decoupled architecture separating presentation, risk intelligence, AI coaching, and scenario simulation.

```
                           +------------------------+
                           |  Presentation Layer    |
                           |   (Streamlit / API)    |
                           +-----------+------------+
                                       |
                                       v
                           +------------------------+
                           |   Adaptive Risk &      |
                           | Personalization Engine |
                           +-----------+------------+
                                       |
                                       v
                           +------------------------+
                           |    AI Security Coach   |
                           | (LLM + Guardrails)     |
                           +-----------+------------+
                                       |
                                       v
                           +------------------------+
                           |   Threat Scenario &    |
                           |  Simulator Engine      |
                           +------------------------+
```

---

## Key Architecture Principles

### 1. Separation of AI Intelligence & Deterministic Scoring
- **LLM Responsibility**: Reasoning analysis, cognitive vulnerability detection (e.g. urgency bias, authority bias), Socratic feedback generation, personalized explanation.
- **Application Responsibility**: Deterministic score calculation ($0-100\%$), risk classification thresholds (High $<60$, Medium $60-80$, Low $\ge 80$), progression tracking, SQLite database persistence, workflow routing.
- **Why**: LLMs can be nondeterministic and hallucinate scores. Enterprise compliance requires deterministic, audit-provable risk metrics.

### 2. Contract-Driven Module Communication
Modules communicate exclusively via Pydantic schema contracts defined in `app/schemas/`:
- `ScenarioSchema` (Person 1)
- `ScenarioAttemptSchema` (Input to Person 2)
- `AIAnalysisSchema` (Output of Person 2, Input to Person 3)
- `RiskProfileSchema` (Output of Person 3, Input to Person 4)

---

## Detailed Data Flows

### Flow 1: User Scenario Attempt
1. Person 4 UI displays scenario loaded from Person 1 `ScenarioEngine`.
2. User submits answer choice and reasoning.
3. Person 1 packs attempt data into `ScenarioAttemptSchema`.

### Flow 2: AI Coaching & Evaluation
1. `AIService` passes attempt through `LLMGuardrails.sanitize_input()`.
2. `BaseLLMProvider` generates structured evaluation and feedback.
3. `LLMGuardrails.validate_output()` ensures schema completeness.
4. Output returned as `AIAnalysisSchema`.

### Flow 3: Deterministic Risk Update & Personalization
1. `RiskService` passes `AIAnalysisSchema` to `DeterministicRiskScorer`.
2. Overall score and category scores updated deterministically.
3. `UserProfileManager` updates top weaknesses list.
4. `PersonalizationService` determines next recommended category and difficulty.

### Flow 4: Dashboard Visualization
1. Person 4 Streamlit dashboard fetches updated `RiskProfileSchema`.
2. Displays real-time risk gauges, improvement percentages, and weakness breakdown.
