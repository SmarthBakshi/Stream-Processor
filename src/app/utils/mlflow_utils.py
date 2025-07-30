"""
MLflow utilities for the Football Analytics Dashboard.

This module provides functions to fetch and summarize XGBoost model runs
from MLflow, including leaderboard data and best run retrieval.

Functions
---------
- fetch_xgboost_runs: Fetches and summarizes XGBoost runs from MLflow for leaderboard and comparison.
- get_best_run: Retrieves the best run (by accuracy) from MLflow for the configured experiment.
"""

import mlflow
import pandas as pd
from mlflow.tracking import MlflowClient
from football_stream_processor.config import MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME


def fetch_xgboost_runs(experiment_name="football-pass-prediction"):
    """
    Fetch and summarize XGBoost runs from MLflow for a given experiment.

    :param experiment_name: Name of the MLflow experiment to query.
    :type experiment_name: str
    :return: Tuple of (DataFrame of runs, best run as Series or None)
    :rtype: (pd.DataFrame, pd.Series or None)
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        return pd.DataFrame(), None
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.accuracy DESC"],
        max_results=50
    )
    records = []
    for r in runs:
        params = r.data.params
        metrics = r.data.metrics
        records.append({
            "Run ID": r.info.run_id,
            "Accuracy": metrics.get("accuracy"),
            "ROC AUC": metrics.get("roc_auc"),
            "Precision": metrics.get("precision"),
            "Recall": metrics.get("recall"),
            "max_depth": params.get("max_depth"),
            "learning_rate": params.get("learning_rate"),
            "n_estimators": params.get("n_estimators")
        })
    df = pd.DataFrame(records)
    best_run = df.iloc[0] if not df.empty else None
    return df, best_run


def get_best_run():
    """
    Retrieve the best run (by accuracy) from MLflow for the configured experiment.

    :return: The best MLflow run object or None if not found.
    :rtype: mlflow.entities.Run or None
    """
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

        experiment = client.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
        if experiment is None:
            raise ValueError(f"No experiment found with name: {MLFLOW_EXPERIMENT_NAME}")

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["metrics.accuracy DESC"],
            max_results=1
        )

        return runs[0] if runs else None

    except Exception as e:
        print(f"[MLflow Error] {e}")
        return None
