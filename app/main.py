"""
AI HUMAN FIREWALL — Adaptive AI Security Awareness Trainer
Main Entrypoint (Streamlit Dashboard & Health Verification Screen).

Owned by Person 4 (Enterprise Dashboard & Integration).
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.dashboard.user_dashboard import render_user_dashboard_placeholder
from app.dashboard.manager_dashboard import render_manager_dashboard_placeholder

st.set_page_config(
    page_title="AI Human Firewall",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.sidebar.title("🛡️ AI Human Firewall")
    st.sidebar.caption("Adaptive AI Security Awareness Trainer")
    
    view_mode = st.sidebar.radio(
        "Navigation / Role",
        ["System Health Status", "User Dashboard (Person 4)", "Manager Dashboard (Person 4)"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Team Ownership")
    st.sidebar.markdown("""
    - **Person 1**: Threat Scenarios (`app/scenarios/`)
    - **Person 2**: AI Coach (`app/ai/`)
    - **Person 3**: Risk Engine (`app/risk/`)
    - **Person 4**: Dashboard & Integration (`app/dashboard/`, `app/main.py`)
    """)
    
    if view_mode == "System Health Status":
        st.title("🛡️ AI Human Firewall")
        st.subheader("System Initialized Successfully.")
        st.success("Repository foundation, module boundaries, integration schemas, and environment configuration are active.")
        
        st.markdown("### Active Module Readiness")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Person 1: Scenarios", "Ready", help="app/scenarios/")
        with col2:
            st.metric("Person 2: AI Coach", "Ready", help="app/ai/")
        with col3:
            st.metric("Person 3: Risk Engine", "Ready", help="app/risk/")
        with col4:
            st.metric("Person 4: Dashboard", "Ready", help="app/dashboard/")
            
        st.markdown("---")
        st.markdown("### Environment Configuration")
        st.json({
            "App Name": settings.app_name,
            "Environment": settings.app_env,
            "LLM Provider": settings.llm_provider,
            "Database URL": settings.database_url,
            "Status": "Healthy"
        })
        
    elif view_mode == "User Dashboard (Person 4)":
        render_user_dashboard_placeholder()
    elif view_mode == "Manager Dashboard (Person 4)":
        render_manager_dashboard_placeholder()


if __name__ == "__main__":
    main()
