import os
import mlflow
import mlflow.sklearn
import optuna
import pandas as pd
from joblib import dump, load
from mlflow.tracking import MlflowClient

from model import get_model
from utils import save_model
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

from data_preparation import load_and_prepare_data
from football_stream_processor.config import (
    MODEL_NAME,
    MODEL_SAVE_PATH,
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_TRACKING_URI
)
from evaluation import print_classification_report, print_roc_auc, plot_confusion_matrix


def create_preprocessor():
    categorical_features = ["length_bucket", "minute_bucket"]
    numerical_features = ["start_x", "start_y", "end_x", "end_y", "distance", "angle", "abs_angle"]
    binary_features = ["is_forward", "progressive", "start_in_final_third", "end_in_penalty_area"]

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(drop="first"))
    ])
    numerical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler())
    ])
    binary_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent"))
    ])

    return ColumnTransformer(transformers=[
        ("num", numerical_transformer, numerical_features),
        ("cat", categorical_transformer, categorical_features),
        ("bin", binary_transformer, binary_features)
    ])


def objective(trial):
    xgb_params = {
        "n_estimators": trial.suggest_int("n_estimators", 50, 600),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "random_state": 42,
        "eval_metric": "logloss"
    }

    X_train, X_test, y_train, y_test = load_and_prepare_data()
    preprocessor = create_preprocessor()

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", get_model(MODEL_NAME, **xgb_params))
    ])

    with mlflow.start_run(nested=True) as run:
        mlflow.log_params(xgb_params)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_probs = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_probs)

        mlflow.log_metrics({
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "roc_auc": roc_auc
        })

        plot_path = "resources/plots/confusion_matrix.png"
        plot_confusion_matrix(y_test, y_pred, save_path=plot_path)
        mlflow.log_artifact(plot_path)

        # Save the run_id in the trial's user_attrs for later retrieval
        trial.set_user_attr("mlflow_run_id", run.info.run_id)

    print_classification_report(y_test, y_pred)
    print_roc_auc(y_test, y_probs)

    return roc_auc


def get_latest_registered_model():
    """Fetch latest version of the registered model from MLflow."""
    client = MlflowClient()
    try:
        versions = client.get_latest_versions(MODEL_NAME, stages=["None", "Staging", "Production"])
        if not versions:
            return None

        # Pick the most recent version
        latest_version = sorted(versions, key=lambda v: int(v.version), reverse=True)[0]
        print(f"📦 Found registered model {MODEL_NAME}, version {latest_version.version}.")

        # Download the model
        local_path = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}/{latest_version.version}")
        return local_path
    except Exception as e:
        print(f"⚠️ Could not fetch registered model: {e}")
        return None


def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    # Check MLflow registry for a model
    model = get_latest_registered_model()
    if model is not None:
        print("✅ Using the latest registered model from MLflow. Skipping hyperparameter tuning.")
        return

    # If no model exists, run Optuna optimization
    print("🚀 No registered model found. Running hyperparameter optimization...")
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=5, n_jobs=1)

    print("Best trial:")
    print(f"  ROC AUC: {study.best_value}")
    print(f"  Params: {study.best_params}")

    best_trial = study.best_trial
    best_params = best_trial.params
    best_params.update({"random_state": 42, "eval_metric": "logloss"})

    X_train, X_test, y_train, y_test = load_and_prepare_data()
    preprocessor = create_preprocessor()
    best_model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", get_model(MODEL_NAME, **best_params))
    ])
    best_model.fit(X_train, y_train)

    # Save locally
    save_model(best_model, MODEL_SAVE_PATH)
    print(f"Best model saved to {MODEL_SAVE_PATH}")

    # Reuse the best trial's MLflow run for registration
    best_run_id = best_trial.user_attrs["mlflow_run_id"]
    with mlflow.start_run(run_id=best_run_id):
        mlflow.sklearn.log_model(
            best_model,
            artifact_path="model",
            registered_model_name=MODEL_NAME,
            input_example=X_train.head(5)
        )
        print(f"Model registered to MLflow as '{MODEL_NAME}' in run {best_run_id}.")


if __name__ == "__main__":
    main()