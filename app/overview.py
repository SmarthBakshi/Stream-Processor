import streamlit as st
from components.pass_network import render_pass_network
from components.shot_map import render_shot_map
from components.player_performace import render_player_performance
from utils.simulate_utils import load_match_events
from utils.mlflow_utils import fetch_xgboost_runs
from utils.ui_helpers import kpi_card


def overview_page():
    st.title("⚽ ML-powered Football Analytics Dashboard")
    st.markdown("Explore football match insights using machine learning:")

    # ---------------------
    # Match Visualizations Preview (Top)
    # ---------------------
    st.divider()
    st.subheader("🔍 Match Visualizations")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🥅 Shot Map")
        render_shot_map(match_id=3764230)

    with col2:
        st.subheader("🔥 Player Performance Heatmap")
        render_player_performance(match_id=3764230)

    # ---------------------
    # Best Model Metrics with KPI Cards
    # ---------------------
    st.divider()
    st.subheader("🏆 Best Pass Prediction Model Performance")

    df_runs, best_run = fetch_xgboost_runs()
    if best_run is not None:
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(kpi_card("Accuracy", f"{best_run['Accuracy']:.3f}"), unsafe_allow_html=True)
        col2.markdown(kpi_card("Precision", f"{best_run['Precision']:.3f}"), unsafe_allow_html=True)
        col3.markdown(kpi_card("Recall", f"{best_run['Recall']:.3f}"), unsafe_allow_html=True)
        col4.markdown(kpi_card("ROC AUC", f"{best_run['ROC AUC']:.3f}"), unsafe_allow_html=True)
    else:
        st.info("No best model found in MLflow.")

    # ---------------------
    # Leaderboard & Pass Network
    # ---------------------
    st.divider()
    st.subheader("📊 Model Leaderboard  &  🔁 Pass Network")

    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Leaderboard")
        if not df_runs.empty:
            top_models = df_runs.sort_values("Accuracy", ascending=False).head(20)[
                ["Run ID", "Accuracy", "ROC AUC"]
            ]
            st.dataframe(top_models, use_container_width=True)
        else:
            st.warning("No MLflow runs found.")

    with col6:
        st.subheader("Pass Network Snapshot")
        st.caption("Top passing patterns in a match")
        render_pass_network(match_id=3764230)

    st.divider()
    st.markdown("📎 **View full code on [GitHub](https://github.com/SmarthBakshi/Stream-Processor)**")
