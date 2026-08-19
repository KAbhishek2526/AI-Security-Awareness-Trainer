# Integration Contracts Specification

This document defines the strict data exchange contracts between the 4 module boundaries.

---

## Data Pipeline Sequence

$$\text{Person 1 (Scenario + Attempt)} \longrightarrow \text{Person 2 (AI Analysis)} \longrightarrow \text{Person 3 (Risk Profile)} \longrightarrow \text{Person 4 (Dashboard)}$$

---

## 1. Input Contract (Person 1 $\to$ Person 2)

### Pydantic Schema: `ScenarioAttemptSchema` (`app/schemas/attempt.py`)

### Example JSON Payload:
```json
{
  "user_id": "USER001",
  "scenario_id": "SC001",
  "category": "phishing",
  "difficulty": 2,
  "scenario": "You receive an email from IT-support@company-verify.com claiming your password expires in 15 minutes.",
  "options": [
    "Click the link immediately and update your password",
    "Verify the sender address and contact internal IT support directly",
    "Forward the email to all colleagues",
    "Ignore it without reporting"
  ],
  "user_answer": "Click the link immediately and update your password",
  "correct_answer": "Verify the sender address and contact internal IT support directly",
  "user_reasoning": "It looked urgent and had IT support in the email sender name."
}
```

---

## 2. AI Analysis Contract (Person 2 $\to$ Person 3)

### Pydantic Schema: `AIAnalysisSchema` (`app/schemas/ai_analysis.py`)

### Example JSON Payload:
```json
{
  "user_id": "USER001",
  "scenario_id": "SC001",
  "category": "phishing",
  "analysis": {
    "correct": false,
    "risk": "high",
    "weaknesses": [
      "urgency_bias",
      "sender_not_verified"
    ]
  },
  "feedback": {
    "explanation": "You fell for the artificial urgency. Attackers create fake deadlines to bypass your critical thinking.",
    "learning_points": [
      "Always inspect email sender domains carefully.",
      "Never log in through links sent in urgent unexpected emails."
    ]
  },
  "personalization": {
    "recommended_topic": "phishing",
    "recommended_difficulty": 2,
    "reason": "Reinforce phishing domain verification under artificial urgency."
  }
}
```

---

## 3. Risk Profile Contract (Person 3 $\to$ Person 4)

### Pydantic Schema: `RiskProfileSchema` (`app/schemas/risk.py`)

### Example JSON Payload:
```json
{
  "user_id": "USER001",
  "overall_score": 65.5,
  "risk_level": "medium",
  "category_scores": {
    "phishing": {
      "category": "phishing",
      "score": 50.0,
      "attempts_count": 4,
      "correct_count": 2
    },
    "password_security": {
      "category": "password_security",
      "score": 80.0,
      "attempts_count": 5,
      "correct_count": 4
    }
  },
  "top_weaknesses": [
    "urgency_bias",
    "mfa_fatigue"
  ],
  "recommended_next_category": "phishing",
  "recommended_next_difficulty": 2,
  "total_attempts": 9,
  "improvement_rate": 15.5
}
```

---

## 4. Error Contracts

In case of error, all API endpoints return standard error payload:
```json
{
  "success": false,
  "message": "Scenario SC999 not found",
  "data": null
}
```
