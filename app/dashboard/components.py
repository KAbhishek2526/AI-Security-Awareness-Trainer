"""
Reusable Streamlit UI components (Person 4 Ownership).
Contains chart builders, metric cards, and health badges.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Any


def render_header(title: str, subtitle: str):
    """Render standardized enterprise page header."""
    st.title(title)
    st.caption(subtitle)
    st.markdown("---")


def render_metric_card(label: str, value: str, delta: str = None, help_text: str = None):
    """Render enterprise metric indicator card."""
    st.metric(label=label, value=value, delta=delta, help=help_text)


def render_risk_badge(risk_level: str):
    """Render color-coded risk badge."""
    level = risk_level.lower()
    if level == "high":
        st.error("RED RISK LEVEL: HIGH VULNERABILITY")
    elif level == "medium":
        st.warning("AMBER RISK LEVEL: MODERATE RISK")
    else:
        st.success("GREEN RISK LEVEL: HIGH AWARENESS")
