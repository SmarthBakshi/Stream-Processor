import mlflow
import pandas as pd
from mlflow.tracking import MlflowClient
from football_stream_processor.config import MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME

def fetch_xgboost_runs(experiment_name="football-pass-prediction"):
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
