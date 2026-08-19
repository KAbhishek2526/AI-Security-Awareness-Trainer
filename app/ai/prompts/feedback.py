"""Feedback prompt template for structured personalized explanations."""

FEEDBACK_PROMPT = """Generate concise, structured security feedback for the user attempt:

Scenario ID: {scenario_id}
User Choice: {user_answer}
Correct Choice: {correct_answer}
Reasoning: {user_reasoning}
Weaknesses: {weaknesses}
Risk Level: {risk_signal}

Generate a concise feedback object with 4 elements:
- what_happened: 1 sentence summarizing user choice.
- why_risky: 1-2 sentences explaining why this choice/reasoning creates risk or what attackers exploit.
- safer_behavior: 1 sentence stating exact safe action to take instead.
- learning_point: 1 memorable key takeaway sentence.

Output JSON:
{{
  "what_happened": "string",
  "why_risky": "string",
  "safer_behavior": "string",
  "learning_point": "string"
}}
"""
