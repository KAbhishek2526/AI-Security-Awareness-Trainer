"""
User Security Dashboard & Interactive Simulator (Person 4 Ownership)
Integrates Person 1 Scenario Engine, Person 2 AI Security Coach, and Person 3 Adaptive Risk Engine.
"""

import streamlit as st
from typing import Optional
from app.schemas.attempt import ScenarioAttemptSchema
from app.schemas.scenario import ScenarioSchema
from app.schemas.risk import RiskProfileSchema
from app.services.scenario_service import ScenarioService
from app.services.ai_service import AIService
from app.services.risk_service import RiskService
from app.core.constants import ThreatCategory, RiskLevel, DifficultyLevel
from app.dashboard.components import (
    render_header, render_metric_card, render_risk_badge, 
    render_weakness_tags, render_category_score_radar
)


def render_user_dashboard(
    user_id: str = "USER001",
    scenario_service: Optional[ScenarioService] = None,
    ai_service: Optional[AIService] = None,
    risk_service: Optional[RiskService] = None
):
    """Render full interactive user security hub, scenario simulator, and risk breakdown."""
    sc_service = scenario_service or ScenarioService()
    coach_service = ai_service or AIService()
    rk_service = risk_service or RiskService()

    # Fetch user risk profile
    profile: RiskProfileSchema = rk_service.get_user_risk_profile(user_id)

    render_header(
        f"🛡️ Security Awareness Hub — {user_id}",
        "Safe simulated threat scenarios, instant AI coaching, and adaptive risk tracking."
    )

    # 1. Top Metrics Header
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            "Overall Awareness Score", 
            f"{profile.overall_score:.1f} / 100", 
            f"{profile.improvement_rate:+.1f}%", 
            "Deterministic awareness score calculated in Python"
        )
    with col2:
        render_risk_badge(profile.risk_level.value if hasattr(profile.risk_level, 'value') else str(profile.risk_level))
    with col3:
        render_metric_card("Scenarios Completed", str(profile.total_attempts), help_text="Total completed scenarios")
    with col4:
        rec_cat = profile.recommended_next_category.value if hasattr(profile.recommended_next_category, 'value') else str(profile.recommended_next_category)
        render_metric_card("Recommended Topic", rec_cat.replace("_", " ").title(), help_text="Target category for next retraining")

    st.markdown("---")

    # Navigation Tabs
    tab_sim, tab_analytics = st.tabs(["🎯 Threat Scenario Simulator", "📊 Personal Risk Analytics"])

    with tab_sim:
        st.subheader("1. Select a Cybersecurity Threat Scenario")
        
        all_scenarios = sc_service.get_all()
        scenario_options = {f"[{s.scenario_id}] {s.title} ({s.category.value.title()})": s for s in all_scenarios}
        
        # Check if recommended scenario requested
        default_index = 0
        if "selected_scenario_id" in st.session_state:
            for idx, (label, sc) in enumerate(scenario_options.items()):
                if sc.scenario_id == st.session_state["selected_scenario_id"]:
                    default_index = idx
                    break

        selected_label = st.selectbox("Choose Threat Scenario:", list(scenario_options.keys()), index=default_index)
        selected_scenario: ScenarioSchema = scenario_options[selected_label]

        # Display Scenario Card
        st.markdown("---")
        col_sc1, col_sc2 = st.columns([3, 1])
        with col_sc1:
            st.markdown(f"### 📋 Scenario [{selected_scenario.scenario_id}]: {selected_scenario.title}")
        with col_sc2:
            st.markdown(f"**Category:** `{selected_scenario.category.value}` | **Difficulty:** `{selected_scenario.difficulty.value if hasattr(selected_scenario.difficulty, 'value') else selected_scenario.difficulty}`")

        st.info(f"**Context:** {selected_scenario.description}")
        st.markdown(f"**Prompt Question:** {selected_scenario.prompt}")

        # Submission Form
        with st.form(key=f"scenario_form_{selected_scenario.scenario_id}"):
            user_choice = st.radio(
                "Select your decision:",
                selected_scenario.options,
                key=f"choice_{selected_scenario.scenario_id}"
            )
            
            user_reasoning = st.text_area(
                "Explain your security reasoning (Why did you make this decision?):",
                placeholder="e.g., The request looked urgent and came from IT support so I wanted to fix it quickly...",
                key=f"reasoning_{selected_scenario.scenario_id}"
            )
            
            submit_btn = st.form_submit_button("🚀 Submit Decision & Analyze with AI Security Coach", use_container_width=True)

        if submit_btn:
            if not user_reasoning.strip():
                st.warning("Please provide your security reasoning to help the AI Coach evaluate your decision.")
            else:
                with st.spinner("AI Security Coach analyzing decision & reasoning..."):
                    # Construct Attempt Contract
                    attempt_payload = ScenarioAttemptSchema(
                        user_id=user_id,
                        scenario_id=selected_scenario.scenario_id,
                        category=selected_scenario.category,
                        difficulty=selected_scenario.difficulty,
                        scenario=selected_scenario.description,
                        options=selected_scenario.options,
                        user_answer=user_choice,
                        correct_answer=selected_scenario.correct_answer,
                        user_reasoning=user_reasoning
                    )

                    # Step 1: Person 2 AI Coach Analysis
                    ai_analysis = coach_service.analyze_user_attempt(attempt_payload)
                    
                    # Step 2: Person 3 Risk Profile Update
                    updated_profile = rk_service.record_analysis_and_update_risk(ai_analysis)

                    # Store in Session State
                    st.session_state["latest_analysis"] = ai_analysis
                    st.session_state["latest_profile"] = updated_profile

        # Display AI Analysis Results if available
        if "latest_analysis" in st.session_state and st.session_state["latest_analysis"].scenario_id == selected_scenario.scenario_id:
            analysis = st.session_state["latest_analysis"]
            
            st.markdown("---")
            st.subheader("🤖 Person 2: AI Security Coach Feedback")

            # Decision Badge
            is_correct = analysis.decision.correct
            if is_correct:
                st.success("✅ SAFE DECISION: You correctly identified the safe action!")
            else:
                st.error("🚨 UNSAFE DECISION DETECTED: This action exposes the organization to security risk.")

            col_fb1, col_fb2 = st.columns(2)
            with col_fb1:
                st.markdown(f"**Evaluated Risk Signal:** `{analysis.decision.risk_signal.value.upper()}`")
                st.markdown("**Identified Cognitive Weaknesses:**")
                render_weakness_tags(analysis.security_analysis.weaknesses)
            with col_fb2:
                st.markdown(f"**Target Category:** `{analysis.category.value}`")
                st.markdown(f"**Next Recommendation:** `{analysis.recommendation.topic.value}` (Difficulty {analysis.recommendation.difficulty})")

            st.markdown("#### Structured Feedback")
            st.write(f"• **What Happened:** {analysis.feedback.what_happened}")
            st.write(f"• **Why Risky:** {analysis.feedback.why_risky}")
            st.write(f"• **Safer Alternative:** {analysis.feedback.safer_behavior}")
            st.write(f"• **Key Takeaway:** {analysis.feedback.learning_point}")

            # Socratic Coaching Question Block
            st.markdown("#### ❓ Socratic Coaching Question")
            st.info(f"👉 **Coach Question:** \"{analysis.coaching.question}\"")

            # Person 3 Updated Profile Banner
            st.markdown("#### 📈 Person 3: Updated Deterministic Risk Profile")
            up_prof = st.session_state["latest_profile"]
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.metric("New Overall Score", f"{up_prof.overall_score:.1f} / 100")
            with col_p2:
                st.metric("New Risk Classification", up_prof.risk_level.value.upper())
            with col_p3:
                rec_sc_id = "PHISH002" if up_prof.recommended_next_category.value == "phishing" else "AI001"
                if st.button("▶️ Start Next Recommended Scenario"):
                    st.session_state["selected_scenario_id"] = rec_sc_id
                    st.rerun()

    with tab_analytics:
        st.subheader("📊 Category Awareness Radar & Weakness Analysis")
        col_an1, col_an2 = st.columns(2)
        with col_an1:
            st.markdown("#### Category Score Radar (0-100%)")
            render_category_score_radar(profile.category_scores)
        with col_an2:
            st.markdown("#### Top Identified User Weaknesses")
            render_weakness_tags(profile.top_weaknesses)
            st.markdown("#### Rationale & Training Pathway")
            st.write(f"• Total Attempted Scenarios: **{profile.total_attempts}**")
            st.write(f"• Recommended Next Topic: **{profile.recommended_next_category.value.title()}**")
            st.write(f"• Recommended Difficulty: **Level {profile.recommended_next_difficulty}**")
