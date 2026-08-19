"""
User Security Dashboard (Person 4 Ownership)
Displays user security awareness scores, progress metrics, and recommended scenarios.
"""

import streamlit as st
from app.dashboard.components import render_header, render_metric_card, render_risk_badge


def render_user_dashboard_placeholder():
    """Placeholder view for Person 4 user dashboard."""
    render_header(
        "User Security Awareness Hub",
        "Personalized risk score, weakness analysis, and adaptive training."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Overall Security Score", "100.0 / 100", "+0%", "Baseline Score")
    with col2:
        render_metric_card("Risk Level", "LOW", help_text="Current deterministic risk classification")
    with col3:
        render_metric_card("Scenarios Completed", "0", help_text="Total training scenarios completed")

    render_risk_badge("low")
    st.info("System Initialized Successfully. Scenario simulation UI ready for Person 1 integration.")
