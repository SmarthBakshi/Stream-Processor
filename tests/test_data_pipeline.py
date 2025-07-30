import pytest
import pandas as pd
from pathlib import Path
from football_stream_processor.models.xg_model import data_pipeline


@pytest.fixture
def sample_event():
    return {
        "type": {"name": "Pass"},
        "location": [50.0, 34.0],
        "pass": {
            "end_location": [80.0, 36.0],
            "outcome": None
        },
        "minute": 23
    }


def test_is_pass(sample_event):
    assert data_pipeline.is_pass(sample_event) is True


def test_calculate_distance():
    dist = data_pipeline.calculate_distance(0, 0, 3, 4)
    assert dist == 5.0


def test_calculate_angle():
    angle = data_pipeline.calculate_angle(0, 0, 1, 1)
    assert round(angle, 2) == 0.79  # ~ pi/4


def test_extract_pass_features_valid(sample_event):
    features = data_pipeline.extract_pass_features(sample_event)
    assert features["start_x"] == 50.0
    assert features["end_x"] == 80.0
    assert features["pass_outcome"] == 1
    assert features["minute"] == 23


def test_extract_pass_features_missing():
    bad_event = {"type": {"name": "Pass"}}
    assert data_pipeline.extract_pass_features(bad_event) is None


def test_filter_pass_events():
    events = [
        {"type": {"name": "Pass"}},
        {"type": {"name": "Shot"}}
    ]
    result = data_pipeline.filter_pass_events(events)
    assert len(result) == 1
    assert result[0]["type"]["name"] == "Pass"


def test_build_all_passes_dataset_creates_pickle(tmp_path):
    # Simulate empty event dir with a single file
    events_dir = tmp_path / "events"
    events_dir.mkdir()
    sample_file = events_dir / "12345.json"
    sample_file.write_text('[{"type": {"name": "Pass"}, "location": [1,1], "pass": {"end_location": [2,2]}, "minute": 1}]')

    cache_path = tmp_path / "pass_data.pkl"
    df = data_pipeline.build_all_passes_dataset(events_dir, cache_path=cache_path, limit=1)
    assert isinstance(df, pd.DataFrame)
    assert cache_path.exists()
