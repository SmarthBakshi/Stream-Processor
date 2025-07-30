import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from app.utils import mlflow_utils


@patch("app.utils.mlflow_utils.mlflow")
@patch("app.utils.mlflow_utils.MlflowClient")
def test_fetch_xgboost_runs_returns_dataframe(mock_client_cls, mock_mlflow):
    # Mock experiment
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_experiment = MagicMock(experiment_id="123")
    mock_client.get_experiment_by_name.return_value = mock_experiment

    # Mock run
    mock_run = MagicMock()
    mock_run.info.run_id = "abc123"
    mock_run.data.metrics = {
        "accuracy": 0.92,
        "roc_auc": 0.85,
        "precision": 0.90,
        "recall": 0.88
    }
    mock_run.data.params = {
        "max_depth": "5",
        "learning_rate": "0.1",
        "n_estimators": "100"
    }
    mock_client.search_runs.return_value = [mock_run]

    df, best_run = mlflow_utils.fetch_xgboost_runs()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert best_run is not None
    assert best_run["Accuracy"] == 0.92
    assert best_run["Run ID"] == "abc123"


@patch("app.utils.mlflow_utils.mlflow")
@patch("app.utils.mlflow_utils.MlflowClient")
def test_get_best_run_returns_run(mock_client_cls, mock_mlflow):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_experiment = MagicMock(experiment_id="456")
    mock_client.get_experiment_by_name.return_value = mock_experiment

    mock_run = MagicMock()
    mock_client.search_runs.return_value = [mock_run]

    best_run = mlflow_utils.get_best_run()
    assert best_run is not None
