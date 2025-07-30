import pandas as pd
import pytest
from football_stream_processor.models.xg_model.feature_engineering import add_engineered_features

def test_add_engineered_features_structure():
    # Minimal valid input
    data = {
        "start_x": [50],
        "start_y": [30],
        "end_x": [70],
        "end_y": [35],
        "distance": [22.36],
        "angle": [0.25],
        "minute": [23],
    }
    df = pd.DataFrame(data)
    result = add_engineered_features(df)

    # Expected columns
    expected_cols = [
        "delta_x", "delta_y", "is_forward", "progressive",
        "start_in_final_third", "end_in_penalty_area",
        "length_bucket", "minute_bucket", "abs_angle"
    ]

    for col in expected_cols:
        assert col in result.columns, f"Missing column: {col}"

def test_bucket_assignments():
    data = {
        "start_x": [81],
        "start_y": [20],
        "end_x": [105],
        "end_y": [40],
        "distance": [35],
        "angle": [-0.5],
        "minute": [88],
    }
    df = pd.DataFrame(data)
    result = add_engineered_features(df).iloc[0]

    assert result["is_forward"] == 1
    assert result["progressive"] == 1
    assert result["start_in_final_third"] == 1
    assert result["end_in_penalty_area"] == 1
    assert result["length_bucket"] == "medium"
    assert result["minute_bucket"] == "76-90"
    assert result["abs_angle"] == 0.5
