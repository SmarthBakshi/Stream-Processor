import os
import pandas as pd

from .utils import load_model
from .feature_engineering import add_engineered_features

def predict_pass_outcome(model_path: str, input_df: pd.DataFrame):
    model = load_model(model_path)
    df = add_engineered_features(input_df)
    
    features = [
        "start_x", "start_y", "end_x", "end_y",
        "distance", "angle", "is_forward", "progressive",
        "start_in_final_third", "end_in_penalty_area",
        "length_bucket", "minute_bucket", "abs_angle"
    ]
    
    X = df[features].fillna(0)
    preds = model.predict_proba(X)[:, 1]  # Probability of success
    return preds

def main():
    model_path = os.path.expanduser("~/models/linear_model.pkl")
    # Example input CSV with same features except target
    input_path = os.path.expanduser("~/data/pass_new.csv")
    
    df = pd.read_csv(input_path)
    preds = predict_pass_outcome(model_path, df)
    df["pass_success_prob"] = preds
    print(df[["start_x", "start_y", "end_x", "end_y", "pass_success_prob"]].head())

if __name__ == "__main__":
    main()