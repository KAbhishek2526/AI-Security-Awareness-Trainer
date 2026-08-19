"""Socratic coaching prompt template."""

SOCRATIC_COACHING_PROMPT = """Generate a Socratic coaching question based on scenario {scenario_id} and detected weaknesses {weaknesses}:

Goal: Ask a targeted question that encourages the user to uncover the security flaw in their thinking without giving away the direct answer upfront.

Output JSON:
{{
  "question": "string"
}}
"""
