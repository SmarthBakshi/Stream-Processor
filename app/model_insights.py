import pandas as pd
import streamlit as st
from football_stream_processor.config import DATA_DIR
from utils.simulate_utils import load_matches, load_match_events
from utils.mlflow_utils import fetch_xgboost_runs
import plotly.graph_objects as go


def model_insights():
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
  
  return
