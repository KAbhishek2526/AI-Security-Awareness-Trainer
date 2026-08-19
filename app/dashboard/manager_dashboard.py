"""
Enterprise Manager Dashboard (Person 4 Ownership)
Displays organization-wide risk overview, team weaknesses, and compliance metrics.
"""

import streamlit as st
from app.dashboard.components import render_header, render_metric_card


def render_manager_dashboard_placeholder():
    """Placeholder view for Person 4 manager dashboard."""
    render_header(
        "Enterprise Human Risk Management",
        "Organization-wide human vulnerability metrics, high-risk departments, and training compliance."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Org Avg Score", "85.4 / 100", "+4.2%", "Average across all employees")
    with col2:
        render_metric_card("High Risk Users", "2 Employees", "-1", "Employees requiring priority retraining")
    with col3:
        render_metric_card("Training Completion Rate", "94%", "+2%", "Quarterly compliance target")

    st.success("Manager Dashboard framework initialized.")
