"""
Data pipeline for extracting and processing pass features from StatsBomb event data.

This module provides functions to load event data, filter for passes, extract relevant features,
and build a pandas DataFrame suitable for modeling or analysis.

"""

import json
import math
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional


def load_events(json_path: str) -> List[Dict[str, Any]]:
    """
    Load events from a StatsBomb JSON file.

    :param json_path: Path to the StatsBomb events JSON file.
    :type json_path: str
    :return: List of event dictionaries.
    :rtype: list[dict]
    """
    with open(json_path, 'r') as f:
        events = json.load(f)
    return events


def is_pass(event: Dict[str, Any]) -> bool:
    """
    Check if the event is a pass.

    :param event: Event dictionary.
    :type event: dict
    :return: True if the event is a pass, False otherwise.
    :rtype: bool
    """
    return event.get('type', {}).get('name') == 'Pass'


def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate Euclidean distance between two points.

    :param x1: X-coordinate of the first point.
    :type x1: float
    :param y1: Y-coordinate of the first point.
    :type y1: float
    :param x2: X-coordinate of the second point.
    :type x2: float
    :param y2: Y-coordinate of the second point.
    :type y2: float
    :return: Euclidean distance.
    :rtype: float
    """
    return math.hypot(x2 - x1, y2 - y1)


def calculate_angle(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate the angle (in radians) of the vector from (x1, y1) to (x2, y2).

    :param x1: X-coordinate of the start point.
    :type x1: float
    :param y1: Y-coordinate of the start point.
    :type y1: float
    :param x2: X-coordinate of the end point.
    :type x2: float
    :param y2: Y-coordinate of the end point.
    :type y2: float
    :return: Angle in radians.
    :rtype: float
    """
    return math.atan2(y2 - y1, x2 - x1)


def extract_pass_features(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract relevant features from a pass event.

    :param event: Pass event dictionary.
    :type event: dict
    :return: Dictionary of extracted features, or None if data is missing.
    :rtype: dict or None
    """
    start_pos = event.get('location')
    end_pos = event.get('pass', {}).get('end_location')

    if not start_pos or not end_pos or None in end_pos:
        return None

    x1, y1 = start_pos
    x2, y2 = end_pos

    distance = calculate_distance(x1, y1, x2, y2)
    angle = calculate_angle(x1, y1, x2, y2)

    outcome = event.get('pass', {}).get('outcome')
    # outcome == None means success, else failed with outcome['name']
    success = 1 if outcome is None else 0

    minute = event.get('minute')

    return {
        'start_x': x1,
        'start_y': y1,
        'end_x': x2,
        'end_y': y2,
        'distance': distance,
        'angle': angle,
        'success': success,
        'minute': minute
    }


def filter_pass_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter a list of events to only include passes.

    :param events: List of event dictionaries.
    :type events: list[dict]
    :return: List of pass event dictionaries.
    :rtype: list[dict]
    """
    return [e for e in events if is_pass(e)]


def build_pass_dataset(json_path: str) -> pd.DataFrame:
    """
    Load JSON events, filter passes, extract features, and return a DataFrame.

    :param json_path: Path to the StatsBomb events JSON file.
    :type json_path: str
    :return: DataFrame of pass features.
    :rtype: pandas.DataFrame
    """
    events = load_events(json_path)
    pass_events = filter_pass_events(events)
    features = [extract_pass_features(e) for e in pass_events]
    # Remove None entries (incomplete data)
    features = [f for f in features if f is not None]
    df = pd.DataFrame(features)
    return df


def main():
    """
    Example usage: Build and print a DataFrame of pass features from a sample file.
    """
    data_path = Path(__file__).parents[2] / 'open-data' / 'data' / 'events' / '22912.json'
    df = build_pass_dataset(str(data_path))
    print(df)


if __name__ == '__main__':
    main()