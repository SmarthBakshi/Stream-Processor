import mlflow
from mlflow.tracking import MlflowClient

def get_best_run():
    try:
        client = MlflowClient()

        experiment = client.get_experiment_by_name("football-pass-prediction")
        if experiment is None:
            raise ValueError("No experiment found with name: football-pass-prediction")

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["metrics.accuracy DESC"],
            max_results=1
        )

        return runs[0] if runs else None

    except Exception as e:
        print(f"[MLFlow Error] {e}")
        return None
