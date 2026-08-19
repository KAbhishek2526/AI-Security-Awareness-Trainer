"""Feedback prompt templates for generating personalized explanations."""

FEEDBACK_PROMPT = """Provide constructive feedback for the user attempt:

Scenario: {scenario}
User Choice: {user_answer}
Correct Choice: {correct_answer}
Reasoning Given: {user_reasoning}

Generate a clear explanation of why their choice was safe/unsafe and list 2-3 key learning takeaways.
"""
