"""
Data pipeline for extracting and processing pass features from StatsBomb event data.

This module provides functions to load event data, filter for passes, extract relevant features,
and build a pandas DataFrame suitable for modeling or analysis.

"""

import json
import math
import pandas as pd
from pathlib import Path
import argparse
from tqdm import tqdm
from typing import Optional


def load_events(json_path: str) -> list[dict[str, any]]:
    """
    Load events from a StatsBomb JSON file.

    :param json_path: Path to the StatsBomb events JSON file.
    :type json_path: str
    :return: list of event dictionaries.
    :rtype: list[dict]
    """
    with open(json_path, 'r') as f:
        events = json.load(f)
    return events


def is_pass(event: dict[str, any]) -> bool:
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


def extract_pass_features(event: dict[str, any]) -> Optional[dict[str, any]]:
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


def filter_pass_events(events: list[dict[str, any]]) -> list[dict[str, any]]:
    """
    Filter a list of events to only include passes.

    :param events: list of event dictionaries.
    :type events: list[dict]
    :return: list of pass event dictionaries.
    :rtype: list[dict]
    """
    return [e for e in events if is_pass(e)]


def build_all_passes_dataset(events_dir: Path, cache_path: Path = Path("../../pickle/pass_data.pkl"), limit: int = 1000) -> pd.DataFrame:
    """
    Process up to `limit` event JSON files in a directory and extract pass features into a single DataFrame.
    Caches the result to a pickle file.

    :param events_dir: Path to the directory containing StatsBomb event JSON files.
    :param cache_path: Path to the pickle file for caching.
    :param limit: Maximum number of event files to process.
    :return: DataFrame of all pass features.
    """
    if cache_path.exists():
        print(f"[INFO] Loading cached data from {cache_path}")
        return pd.read_pickle(cache_path)

    print(f"[INFO] Processing up to {limit} event files in {events_dir}")
    all_features = []

    json_files = sorted(events_dir.glob("*.json"))[:limit]

    for json_file in tqdm(json_files, desc="Processing JSON files"):
        events = load_events(json_file)
        pass_events = filter_pass_events(events)
        features = [extract_pass_features(e) for e in pass_events if extract_pass_features(e) is not None]
        all_features.extend(features)

    df = pd.DataFrame(all_features)

    # Ensure .pickle directory exists
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_pickle(cache_path)
    print(f"[INFO] Cached pass dataset to {cache_path}")

    return df

def main():
    parser = argparse.ArgumentParser(description="Build pass dataset from StatsBomb event files.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of JSON files to process.")
    args = parser.parse_args()

    events_dir = Path(__file__).parents[2] / 'open-data' / 'data' / 'events'
    cache_path = Path("../../pickle/pass_data.pkl")

    df = build_all_passes_dataset(events_dir=events_dir, cache_path=cache_path, limit=args.limit)
    print(df)


if __name__ == "__main__":
    main()