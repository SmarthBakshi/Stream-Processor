"""
Feature engineering functions for pass-level StatsBomb data.

Adds tactical, spatial, and contextual derived features to the dataset.
"""

import pandas as pd

def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add engineered features to the pass dataframe.

    :param df: DataFrame containing raw pass features. Must include columns:
               ['start_x', 'start_y', 'end_x', 'end_y', 'distance', 'angle', 'minute']
    :type df: pd.DataFrame
    :return: DataFrame with additional engineered features.
    :rtype: pd.DataFrame

    Features added
    --------------
    - delta_x, delta_y: Direction deltas
    - is_forward: Forward pass indicator (toward opponent's goal)
    - progressive: Progressive pass indicator (moves ≥15 meters toward goal)
    - start_in_final_third: Pass starts in final third
    - end_in_penalty_area: Pass ends in penalty area
    - length_bucket: Categorical pass length
    - minute_bucket: Categorical match time
    - abs_angle: Absolute value of pass angle
    """
    # Direction deltas
    df["delta_x"] = df["end_x"] - df["start_x"]
    df["delta_y"] = df["end_y"] - df["start_y"]

    # Forward pass indicator (toward opponent's goal)
    df["is_forward"] = (df["delta_x"] > 0).astype(int)

    # Progressive pass (moves ≥15 meters toward goal)
    df["progressive"] = (df["delta_x"] > 15).astype(int)

    # Zone-based indicators
    df["start_in_final_third"] = (df["start_x"] > 80).astype(int)
    df["end_in_penalty_area"] = ((df["end_x"] > 102) & (df["end_y"].between(18, 62))).astype(int)

    # Pass length buckets
    df["length_bucket"] = pd.cut(
        df["distance"],
        bins=[0, 10, 20, 40, 60, 100],
        labels=["very_short", "short", "medium", "long", "very_long"]
    )

    # Match time buckets
    df["minute_bucket"] = pd.cut(
        df["minute"],
        bins=[0, 15, 30, 45, 60, 75, 90, 120],
        labels=["0-15", "16-30", "31-45", "46-60", "61-75", "76-90", "ET"]
    )

    # Absolute angle (for direction-agnostic passes)
    df["abs_angle"] = df["angle"].abs()

    return df
