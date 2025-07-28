import os
from datetime import datetime
from pathlib import Path

# Model training
MODEL_NAME = "xgboost"
RANDOM_SEED = 42
TEST_SIZE = 0.2

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = "models"
MODEL_FILENAME_TEMPLATE = "{model_name}_model.pkl"
MODEL_SAVE_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME_TEMPLATE.format(model_name=MODEL_NAME))
PLOT_DIR = "resources/plots"
PICKLE_DIR = ".pickle"
RESOURCES_DIR = "resources"
DATA_DIR = "open-data/data"
MLFLOW_DIR = ROOT_DIR / "mlflow"
MLFLOW_RUNS = MLFLOW_DIR / "mlruns"
MLFLOW_ARTIFACTS = MLFLOW_DIR / "mlartifacts"

# MLflow Configuration
MLFLOW_TRACKING_URI = f"file://{MLFLOW_RUNS}"
MLFLOW_REGISTRY_URI = f"file://{MLFLOW_ARTIFACTS}"
MLFLOW_EXPERIMENT_NAME = "football-pass-prediction"
MLFLOW_RUN_NAME = f"{MODEL_NAME}-run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
MLFLOW_ARTIFACT_PATH = "mlruns"
MLFLOW_AUTOLOG = True