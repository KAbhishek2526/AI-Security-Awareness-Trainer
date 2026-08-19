"""
Reusable Streamlit UI & Chart Visualization Components (Person 4 Ownership).
Contains chart builders, metric cards, risk badges, weakness pills, and coaching blocks.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
from app.schemas.risk import RiskProfileSchema, CategoryScoreSchema


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
    level = (risk_level or "").lower()
    if level == "high":
        st.error("🚨 HIGH RISK LEVEL: Immediate Security Retraining Required")
    elif level == "medium":
        st.warning("⚠️ MEDIUM RISK LEVEL: Moderate Vulnerability Detected")
    else:
        st.success("🛡️ LOW RISK LEVEL: High Security Awareness Demonstrated")


def render_weakness_tags(weaknesses: List[str]):
    """Render weakness tag pills."""
    if not weaknesses:
        st.caption("No active security weaknesses detected.")
        return
    
    html_tags = " ".join([
        f"<span style='background-color:#ffebe9; color:#cf222e; padding:4px 8px; border-radius:12px; font-weight:600; font-size:13px; margin-right:4px;'>⚠️ {w}</span>"
        for w in weaknesses
    ])
    st.markdown(html_tags, unsafe_allow_html=True)


def render_category_score_radar(category_scores: Dict[str, CategoryScoreSchema]):
    """Render Plotly radar chart showing awareness scores across threat categories."""
    if not category_scores:
        return
    
    categories = []
    scores = []
    
    for cat_key, cat_obj in category_scores.items():
        cat_name = cat_key.replace("_", " ").title()
        categories.append(cat_name)
        score_val = cat_obj.score if hasattr(cat_obj, 'score') else cat_obj.get('score', 100.0)
        scores.append(score_val)
        
    df = pd.DataFrame(dict(r=scores, theta=categories))
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Awareness Score',
        line_color='#0969da',
        fillcolor='rgba(9, 105, 218, 0.25)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        height=320
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_manager_risk_distribution(users_profiles: List[RiskProfileSchema]):
    """Render Plotly donut chart showing org-wide risk level distribution."""
    risk_counts = {"low": 0, "medium": 0, "high": 0}
    for p in users_profiles:
        lvl = p.risk_level.value.lower() if hasattr(p.risk_level, 'value') else str(p.risk_level).lower()
        if lvl in risk_counts:
            risk_counts[lvl] += 1
        else:
            risk_counts["low"] += 1
            
    fig = px.pie(
        names=["Low Risk (High Awareness)", "Medium Risk", "High Risk (Vulnerable)"],
        values=[risk_counts["low"], risk_counts["medium"], risk_counts["high"]],
        color=["Low Risk (High Awareness)", "Medium Risk", "High Risk (Vulnerable)"],
        color_discrete_map={
            "Low Risk (High Awareness)": "#2da44e",
            "Medium Risk": "#d97706",
            "High Risk (Vulnerable)": "#cf222e"
        },
        hole=0.4,
        title="Organization Human Risk Distribution"
    )
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=300)
    st.plotly_chart(fig, use_container_width=True)
