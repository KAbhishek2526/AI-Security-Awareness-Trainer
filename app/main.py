"""
AI HUMAN FIREWALL — Adaptive AI Security Awareness Trainer
Main Entrypoint (Streamlit Dashboard & Interactive Simulator).

Owned by Person 4 (Enterprise Dashboard & Integration).
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.dashboard.user_dashboard import render_user_dashboard
from app.dashboard.manager_dashboard import render_manager_dashboard

st.set_page_config(
    page_title="AI Human Firewall",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    st.sidebar.title("🛡️ AI Human Firewall")
    st.sidebar.caption("Adaptive AI Security Awareness Trainer")

    # User Profile Switcher in Sidebar
    active_user_id = st.sidebar.selectbox(
        "Active User Account:",
        ["USER001", "USER002", "USER003"],
        index=0
    )

    view_mode = st.sidebar.radio(
        "Navigation",
        [
            "🎯 User Security Hub & Simulator",
            "📊 Enterprise Manager Dashboard",
            "🔍 System Architecture & Health"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Module Architecture")
    st.sidebar.markdown("""
    - **Person 1**: Threat Scenarios (`app/scenarios/`)
    - **Person 2**: AI Security Coach (`app/ai/`)
    - **Person 3**: Adaptive Risk Engine (`app/risk/`)
    - **Person 4**: Dashboard & Integration (`app/dashboard/`, `app/main.py`)
    """)

    if view_mode == "🎯 User Security Hub & Simulator":
        render_user_dashboard(user_id=active_user_id)
    elif view_mode == "📊 Enterprise Manager Dashboard":
        render_manager_dashboard()
    elif view_mode == "🔍 System Architecture & Health":
        st.title("🛡️ AI Human Firewall -- System Health & Architecture")
        st.subheader("System Initialized & Integrated Successfully.")
        st.success("Repository foundation, 4 module boundaries, Pydantic schemas, and environment configuration are active.")

        st.markdown("### Active Module Status")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Person 1: Scenarios", "Active", help="app/scenarios/")
        with col2:
            st.metric("Person 2: AI Coach", "Active", help="app/ai/")
        with col3:
            st.metric("Person 3: Risk Engine", "Active", help="app/risk/")
        with col4:
            st.metric("Person 4: Dashboard", "Active", help="app/dashboard/")

        st.markdown("---")
        st.markdown("### Environment Configuration")
        st.json({
            "App Name": settings.app_name,
            "Environment": settings.app_env,
            "LLM Provider": settings.llm_provider,
            "Database URL": settings.database_url,
            "Status": "Healthy"
        })


if __name__ == "__main__":
    main()
