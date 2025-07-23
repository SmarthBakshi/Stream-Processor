import os
import mlflow
import mlflow.sklearn
import optuna
import pandas as pd

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

    preprocessor = ColumnTransformer(transformers=[
        ("num", numerical_transformer, numerical_features),
        ("cat", categorical_transformer, categorical_features),
        ("bin", binary_transformer, binary_features)
    ])

    return preprocessor


def objective(trial):
    # Define hyperparameter search space
    xgb_params = {
        "n_estimators": trial.suggest_int("n_estimators", 50, 600),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "random_state": 42,
        "use_label_encoder": False,
        "eval_metric": "logloss"
    }

    # Load data
    X_train, X_test, y_train, y_test = load_and_prepare_data()

    preprocessor = create_preprocessor()

    # Build pipeline
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", get_model(MODEL_NAME, **xgb_params))
    ])

    # Start MLflow run for this trial
    with mlflow.start_run(nested=True):  # nested=True allows multiple runs inside one experiment
        mlflow.log_params(xgb_params)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_probs = model.predict_proba(X_test)[:, 1]

        # Metrics
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

        # Optional: log confusion matrix plot
        plot_path = "resources/plots/confusion_matrix.png"
        plot_confusion_matrix(y_test, y_pred, save_path=plot_path)
        mlflow.log_artifact(plot_path)

        # Log model with input example to save schema
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            registered_model_name=MODEL_NAME,
            input_example=X_train.head(5)
        )

    # Print classification report and ROC AUC on console (optional)
    print_classification_report(y_test, y_pred)
    print_roc_auc(y_test, y_probs)

    # Return the metric to optimize
    return roc_auc


def main():
    # Setup MLflow tracking and experiment
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    # Create Optuna study
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=50, n_jobs=1)  # adjust n_trials as needed

    print("Best trial:")
    print(f"  ROC AUC: {study.best_value}")
    print(f"  Params: {study.best_params}")

    # Optionally, retrain best model and save locally
    best_params = study.best_params
    best_params["random_state"] = 42
    best_params["use_label_encoder"] = False
    best_params["eval_metric"] = "logloss"

    X_train, X_test, y_train, y_test = load_and_prepare_data()
    preprocessor = create_preprocessor()
    best_model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", get_model(MODEL_NAME, **best_params))
    ])
    best_model.fit(X_train, y_train)
    save_model(best_model, MODEL_SAVE_PATH)
    print(f"Best model saved to {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    main()