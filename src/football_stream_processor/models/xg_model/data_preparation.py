import pandas as pd
from sklearn.model_selection import train_test_split

from football_stream_processor.utils.eda_utils import basic_checks


def load_and_prepare_data():
    df = basic_checks()

    # Make this configurable, maybe one wants to try different sets of features in between runs
    features = [
        "start_x", "start_y", "end_x", "end_y",
        "distance", "angle", "is_forward", "progressive",
        "start_in_final_third", "end_in_penalty_area",
        "length_bucket", "minute_bucket", "abs_angle"
    ]
    target = "pass_outcome"

    X = df[features]
    y = df[target]

    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)