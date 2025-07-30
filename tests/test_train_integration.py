import tempfile
import mlflow
import os
from football_stream_processor.models.xg_model import train


def test_training_pipeline_runs():
    # Use a temporary MLflow directory to avoid conflicts
    with tempfile.TemporaryDirectory() as tmpdir:
        tracking_uri = f"file:{tmpdir}"
        os.environ["MLFLOW_TRACKING_URI"] = tracking_uri
        os.environ["MLFLOW_REGISTRY_URI"] = tracking_uri

        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_registry_uri(tracking_uri)
        mlflow.set_experiment("test_experiment")

        # Run the full training pipeline
        train.main()

        # If no exception, we assume success
        assert True
