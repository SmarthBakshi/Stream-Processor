import pandas as pd
from sklearn.model_selection import train_test_split
from scripts.eda import PassDataEDA, basic_checks
from feature_engineering import add_engineered_features

def load_and_prepare_data(filepath: str):
    
    df = basic_checks()
    
    features = [
        "start_x", "start_y", "end_x", "end_y",
        "distance", "angle", "is_forward", "progressive",
        "start_in_final_third", "end_in_penalty_area",
        "length_bucket", "minute_bucket", "abs_angle"
    ]
    
    # Target
    target = "pass_outcome"
    
    X = df[features]
    y = df[target]
    
    # Handle missing values or convert categorical if needed
    X = X.fillna(0)
    
    # Split train-test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    
    return X_train, X_test, y_train, y_test