import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import mlflow
from utils.mlflow_utils import fetch_xgboost_runs
from utils.simulate_utils import load_dummy_events, render_match_simulator
from mlflow.tracking import MlflowClient
from football_stream_processor.config import MLFLOW_TRACKING_URI

st.set_page_config(page_title="Football Analytics Dashboard", layout="wide")

page = st.sidebar.radio("Navigation", ["Overview", "Pass Analysis", "Model Insights", "Match Simulator"])

teams = ["Barcelona", "Real Madrid"]
players = ["Messi", "Modric", "Benzema"]

if page == "Overview":
    st.title("ML-powered Football Analytics Dashboard")
    st.markdown("""
    Explore football match insights using machine learning:
    - Interactive pitch visualizations for passes.
    - Model performance from MLflow + Optuna.
    - Live match simulator with xG tracking.
    """)
    st.markdown("**View Code on [GitHub](https://github.com/)**")

elif page == "Pass Analysis":
    st.header("Pass Analysis")
    col1, col2, col3 = st.columns(3)
    team = col1.selectbox("Select Team", teams)
    player = col2.selectbox("Select Player", players)
    time_range = col3.slider("Select Time Range (min)", 0, 90, (0, 45))
    fig_pitch = go.Figure()
    fig_pitch.add_trace(go.Scatter(x=[20, 50], y=[30, 60], mode="lines+markers", line=dict(color="red")))
    fig_pitch.update_layout(title="Pass Map", xaxis=dict(visible=False), yaxis=dict(visible=False), plot_bgcolor="green")
    st.plotly_chart(fig_pitch, use_container_width=True)
    time = np.linspace(0, 90, 10)
    xg_A, xg_B = np.cumsum(np.random.rand(10)), np.cumsum(np.random.rand(10))
    fig_xg = go.Figure()
    fig_xg.add_trace(go.Scatter(x=time, y=xg_A, name=teams[0], line=dict(color="blue")))
    fig_xg.add_trace(go.Scatter(x=time, y=xg_B, name=teams[1], line=dict(color="red")))
    fig_xg.update_layout(title="xG Over Time", xaxis_title="Minutes", yaxis_title="xG")
    st.plotly_chart(fig_xg, use_container_width=True)

elif page == "Model Insights":
    st.header("Model Insights")
    st.write("Fetching all Optuna trials for XGBoost from MLflow...")
    df_runs, best_run = fetch_xgboost_runs()
    if not df_runs.empty:
        st.subheader("All XGBoost Trial Runs")
        st.dataframe(df_runs, use_container_width=True)

        st.subheader("Compare Models")
        selected_runs = st.multiselect(
            "Select Runs to Compare",
            df_runs["Run ID"].tolist(),
            default=df_runs["Run ID"].head(2).tolist()
        )

        # Let user select which metrics to compare
        metrics_options = ["Accuracy", "ROC AUC", "Precision", "Recall"]
        selected_metrics = st.multiselect(
            "Select Metrics to Compare",
            metrics_options,
            default=["Accuracy", "ROC AUC"]
        )

        if selected_runs and selected_metrics:
            compare_df = df_runs[df_runs["Run ID"].isin(selected_runs)]
            st.write("Selected Models Comparison:")
            st.dataframe(compare_df, use_container_width=True)

            # Build dynamic bar chart
            fig_bar = go.Figure()
            colors = {
                "Accuracy": "blue",
                "ROC AUC": "green",
                "Precision": "orange",
                "Recall": "red"
            }
            for metric in selected_metrics:
                fig_bar.add_trace(go.Bar(
                    x=compare_df["Run ID"],
                    y=compare_df[metric],
                    name=metric,
                    marker_color=colors.get(metric, "gray")
                ))
            fig_bar.update_layout(
                barmode='group',
                title="Model Performance Comparison",
                xaxis_title="Run ID",
                yaxis_title="Score"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Best model summary
        if best_run is not None:
            acc = best_run['Accuracy'] if pd.notnull(best_run['Accuracy']) else 0.0
            roc = best_run['ROC AUC'] if pd.notnull(best_run['ROC AUC']) else 0.0
            precision = best_run['Precision'] if pd.notnull(best_run['Precision']) else 0.0
            recall = best_run['Recall'] if pd.notnull(best_run['Recall']) else 0.0

            st.subheader("Best Model Summary")
            st.markdown(f"""
            **Run ID:** {best_run['Run ID']}  
            **Accuracy:** {acc:.3f}  
            **ROC AUC:** {roc:.3f}  
            **Precision:** {precision:.3f}  
            **Recall:** {recall:.3f}  
            **Parameters:** max_depth={best_run['max_depth']}, learning_rate={best_run['learning_rate']}, n_estimators={best_run['n_estimators']}
            """)
    else:
        st.warning("No runs found in MLflow for the specified experiment.")


elif page == "Match Simulator":
    st.header("Match Simulator")
    match = st.selectbox("Select Match", ["Barcelona vs Real Madrid", "Team C vs Team D"])

    # Load dummy events for now (replace with real StatsBomb later)
    events, xg_team1, xg_team2, times = load_dummy_events()

    # Render the simulator
    render_match_simulator(events, xg_team1, xg_team2, times)
