"""Evaluation prompt template for evaluating user answer decision and reasoning."""

EVALUATION_PROMPT = """Evaluate the following user response to a cybersecurity scenario:

Scenario ID: {scenario_id}
Category: {category}
Difficulty: {difficulty}
Scenario Context: {scenario}
Presented Options: {options}
User Selected Choice: {user_answer}
Correct Choice: {correct_answer}
User Stated Reasoning: {user_reasoning}

Analyze the user's decision AND reasoning:
1. Decision Evaluation: Did the user choose the safe action or an unsafe action?
2. Semantic Reasoning Analysis: Why did the user choose this? Was there cognitive bias (urgency, authority, fatigue, convenience)?
3. Risk Signal: Rate as 'low' (safe choice with solid reasoning), 'medium' (partially safe or minor oversight), or 'high' (unsafe action or dangerous misconception).
4. Detected Weaknesses: Select 1-3 weakness labels from the controlled list:
   [urgency_bias, authority_trust, sender_not_verified, domain_not_verified, link_not_verified, attachment_not_verified, credential_sharing, password_sharing, password_reuse, weak_password_practice, mfa_fatigue, mfa_push_approval, otp_sharing, tailgating_acceptance, physical_security_awareness, sensitive_data_sharing, unsafe_data_transfer, pii_handling, public_ai_data_upload, confidential_data_to_ai, ai_output_overtrust, secret_exposure, hardcoded_secret, lack_of_verification, social_engineering_susceptibility]

Format output as JSON:
{{
  "correct": bool,
  "risk_signal": "low" | "medium" | "high",
  "weaknesses": ["string"],
  "reasoning_summary": "string"
}}
"""
