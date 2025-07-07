import os
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from model import get_model
from utils import save_model
from data_preparation import load_and_prepare_data
from football_stream_processor.config import MODEL_NAME, MODEL_SAVE_PATH
from evaluation import print_classification_report, print_roc_auc, plot_confusion_matrix

def main():
    
    X_train, X_test, y_train, y_test = load_and_prepare_data()

    categorical_features = ["length_bucket", "minute_bucket"]
    numerical_features = [
        "start_x", "start_y", "end_x", "end_y",
        "distance", "angle", "abs_angle"
    ]
    binary_features = [
        "is_forward", "progressive",
        "start_in_final_third", "end_in_penalty_area"
    ]

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(drop="first"))
    ])

    numerical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler())
    ])

    binary_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, numerical_features),
            ("cat", categorical_transformer, categorical_features),
            ("bin", binary_transformer, binary_features)
        ]
    )

    model = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", get_model(MODEL_NAME))
    ])

    model.fit(X_train, y_train)
    print("Model trained successfully.")
    y_pred = model.predict(X_test)
    y_probs = model.predict_proba(X_test)[:, 1]
    
    print_classification_report(y_test, y_pred)
    print_roc_auc(y_test, y_probs)
    plot_confusion_matrix(y_test, y_pred)
    
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    save_model(model, MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    main()