import numpy as np
from app.utils.simulate_utils import load_match_events

def test_load_matches_columns(matches_df):
    expected_cols = ["match_id", "home_team", "away_team", "competition", "season", "date"]
    for col in expected_cols:
        assert col in matches_df.columns

def test_load_matches_values(matches_df):
    assert matches_df["match_id"].nunique() > 0
    assert matches_df["home_team"].notnull().all()

def test_load_match_events_structure():
    match_id = 3749052  
    passes, xg_team1, xg_team2, times = load_match_events(match_id)

    # Passes structure
    assert isinstance(passes, list), "passes should be a list"
    if passes:
        assert all(isinstance(p, dict) for p in passes), "Each pass should be a dictionary"
        required_keys = {"x", "y", "time"}
        assert all(required_keys.issubset(p.keys()) for p in passes), "Each pass dict must contain x, y, time keys"

    # xG arrays and times
    assert isinstance(xg_team1, np.ndarray), "xg_team1 should be a numpy array"
    assert isinstance(xg_team2, np.ndarray), "xg_team2 should be a numpy array"
    assert isinstance(times, list), "times should be a list"

    # All must be same length
    assert len(xg_team1) == len(times), "xg_team1 and times should have the same length"
    assert len(xg_team2) == len(times), "xg_team2 and times should have the same length"

    # Sanity check: values should be non-negative
    assert np.all(xg_team1 >= 0), "xg_team1 contains negative values"
    assert np.all(xg_team2 >= 0), "xg_team2 contains negative values"
