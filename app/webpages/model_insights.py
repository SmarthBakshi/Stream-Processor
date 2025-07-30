import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from utils.mlflow_utils import fetch_xgboost_runs
from utils.ui_helpers import kpi_card  # Make sure this exists

def model_insights():
    """
    Render the Model Insights page for the Football Analytics Dashboard.

    Displays:
    - Best model metrics as KPI cards
    - All XGBoost trial runs from MLflow
    - Interactive comparison of selected runs and metrics
    :return: None
    """
    # Centered Title
    st.markdown("<h1 style='text-align:center;'>📈 Model Insights</h1>", unsafe_allow_html=True)

    # Load MLflow runs
    st.markdown("<div style='text-align:center;'><em>Fetching all Optuna trials for XGBoost from MLflow...</em></div>", unsafe_allow_html=True)
    df_runs, best_run = fetch_xgboost_runs()

    # ---------------------
    # KPI Cards for Best Model (TOP)
    # ---------------------
    if best_run is not None:
        st.markdown("### Best Model Performance", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(kpi_card("Accuracy", f"{best_run['Accuracy']:.3f}"), unsafe_allow_html=True)
        col2.markdown(kpi_card("Precision", f"{best_run['Precision']:.3f}"), unsafe_allow_html=True)
        col3.markdown(kpi_card("Recall", f"{best_run['Recall']:.3f}"), unsafe_allow_html=True)
        col4.markdown(kpi_card("ROC AUC", f"{best_run['ROC AUC']:.3f}"), unsafe_allow_html=True)
    else:
        st.info("No best model found in MLflow.")

    st.divider()

    # ---------------------
    # Trial Table + Compare
    # ---------------------
    if not df_runs.empty:
        st.subheader("All XGBoost Trial Runs")
        st.dataframe(df_runs, use_container_width=True)

        st.subheader("Compare Models")
        selected_runs = st.multiselect(
            "Select Runs to Compare",
            df_runs["Run ID"].tolist(),
            default=df_runs["Run ID"].head(2).tolist()
        )

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

            # Dynamic bar chart for selected metrics
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

        # Best model parameters
        if best_run is not None:
            st.subheader("Best Model Summary")
            st.markdown(f"""
            **Run ID:** {best_run['Run ID']}  
            **Parameters:**  
            - `max_depth`: {best_run['max_depth']}  
            - `learning_rate`: {best_run['learning_rate']}  
            - `n_estimators`: {best_run['n_estimators']}  
            """)
    else:
        st.warning("No runs found in MLflow for the specified experiment.")
    
    return
