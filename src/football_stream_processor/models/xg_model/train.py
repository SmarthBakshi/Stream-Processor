import os
import mlflow
import mlflow.sklearn
import pandas as pd
from model import get_model
from utils import save_model

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import (
    accuracy_score, 
    precision_score,
    recall_score, 
    roc_auc_score
)

from data_preparation import load_and_prepare_data
from football_stream_processor.config import (
    MODEL_NAME,
    MODEL_SAVE_PATH,
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_RUN_NAME,
    MLFLOW_TRACKING_URI
)
from evaluation import (
    print_classification_report,
    print_roc_auc,
    plot_confusion_matrix,
)

def main():
    # Setup MLflow
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run(run_name=MLFLOW_RUN_NAME):
        mlflow.log_param("model_name", MODEL_NAME)

        # Load data
        X_train, X_test, y_train, y_test = load_and_prepare_data()

        # Feature groups
        categorical_features = ["length_bucket", "minute_bucket"]
        numerical_features = ["start_x", "start_y", "end_x", "end_y", "distance", "angle", "abs_angle"]
        binary_features = ["is_forward", "progressive", "start_in_final_third", "end_in_penalty_area"]

        # Preprocessing
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

        # Full pipeline with model
        model = Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", get_model(MODEL_NAME))
        ])

        # Train model
        model.fit(X_train, y_train)
        print("Model trained successfully.")

        # Predictions
        y_pred = model.predict(X_test)
        y_probs = model.predict_proba(X_test)[:, 1]

        # Evaluation (console + MLflow)
        print_classification_report(y_test, y_pred)
        print_roc_auc(y_test, y_probs)

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_probs)
        }
        mlflow.log_metrics(metrics)

        # Log model with schema inference
        mlflow.sklearn.log_model(
            model,
            name="model",
            registered_model_name=MODEL_NAME,
            input_example=X_test.head(5)  # Ensures schema is saved
        )

        # Save to local disk
        os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
        save_model(model, MODEL_SAVE_PATH)
        print(f"Model saved to {MODEL_SAVE_PATH}")

        # Log confusion matrix plot
        plot_path = "resources/plots/confusion_matrix.png"
        plot_confusion_matrix(y_test, y_pred, save_path=plot_path)
        mlflow.log_artifact(plot_path)

if __name__ == "__main__":
    main()