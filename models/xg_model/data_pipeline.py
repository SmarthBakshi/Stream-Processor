import json
import math
import pandas as pd
from pathlib import Path

def load_events(json_path: str) -> list:
    """Load events from a StatsBomb JSON file."""
    with open(json_path, 'r') as f:
        events = json.load(f)
    return events

def is_pass(event: dict) -> bool:
    """Check if the event is a pass."""
    return event.get('type', {}).get('name') == 'Pass'

def calculate_distance(x1, y1, x2, y2) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calculate_angle(x1, y1, x2, y2) -> float:
    """Calculate the angle (in radians) of the pass vector."""
    return math.atan2(y2 - y1, x2 - x1)

def extract_pass_features(event: dict) -> dict:
    """Extract relevant features from a pass event."""
    start_pos = event['location']
    end_pos = event.get('pass', {}).get('end_location', [None, None])

    x1, y1 = start_pos
    x2, y2 = end_pos if None not in end_pos else (None, None)

    distance = calculate_distance(x1, y1, x2, y2) if x2 is not None else None
    angle = calculate_angle(x1, y1, x2, y2) if x2 is not None else None

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

def build_pass_dataset(json_path: str) -> pd.DataFrame:
    """Load JSON events, filter passes, extract features, return DataFrame."""
    events = load_events(json_path)
    pass_events = [e for e in events if is_pass(e)]

    features = [extract_pass_features(e) for e in pass_events]

    df = pd.DataFrame(features)
    # Optionally drop rows with missing data
    df.dropna(inplace=True)
    return df


if __name__ == '__main__':
    # Example usage:
    data_path = Path(__file__).parents[2] / 'open-data' / 'data' / 'events' / '22912.json'
    df = build_pass_dataset(str(data_path))
    print(df)