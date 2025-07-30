# tests/conftest.py

import os
import sys
import pytest 

from app.utils.simulate_utils import load_matches, load_match_events


# Add the 'src' directory to sys.path so 'from app...' works correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

@pytest.fixture(scope="session")
def matches_df():
    """Fixture to provide the loaded matches DataFrame once per test session."""
    return load_matches()

@pytest.fixture(scope="session")
def match_events():
    """Fixture to provide match events for a specific match."""
    match_id = 3749052  # Example match ID
    return load_match_events(match_id)
    
