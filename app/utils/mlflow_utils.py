import mlflow
from mlflow.tracking import MlflowClient
from src.football_stream_processor.config import MLFLOW_EXPERIMENT_NAME

def get_best_run():
    try:
        client = MlflowClient()

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
        print(f"[MLFlow Error] {e}")
        return None
