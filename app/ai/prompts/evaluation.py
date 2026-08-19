"""Evaluation prompt templates for scenario analysis."""

EVALUATION_PROMPT = """Evaluate the following user response to a cybersecurity threat scenario:

Scenario Context: {scenario}
Category: {category}
User Answer: {user_answer}
Correct Answer: {correct_answer}
User Reasoning: {user_reasoning}

Analyze:
1. Is the answer correct?
2. What is the assessed risk level (low, medium, high)?
3. What cognitive biases or weaknesses were exhibited (e.g. urgency_bias, authority_trust, sender_not_verified)?

Output formatted JSON:
{{
    "correct": bool,
    "risk": "low" | "medium" | "high",
    "weaknesses": ["string"]
}}
"""
