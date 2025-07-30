import pytest
from datetime import datetime
from unittest.mock import patch
from io import StringIO
import sys

from football_stream_processor.match.simulate import parse_timestamp, simulate_events

# Sample event data for testing
mock_events = [
    {
        "timestamp": "00:00:05.000",
        "type": {"name": "Pass"},
        "player": {"name": "Player A"}
    },
    {
        "timestamp": "00:00:07.500",
        "type": {"name": "Shot"},
        "player": {"name": "Player B"}
    }
]

def test_parse_timestamp():
    ts = "00:01:30.250"
    result = parse_timestamp(ts)
    assert isinstance(result, datetime)
    assert result.minute == 1 and result.second == 30 and result.microsecond == 250000

@patch("time.sleep", return_value=None)
def test_simulate_events(mock_sleep):
    # Capture printed output
    captured_output = StringIO()
    sys.stdout = captured_output

    simulate_events(mock_events)

    sys.stdout = sys.__stdout__  # Reset stdout

    output = captured_output.getvalue()
    assert "[00:00:05.000] Pass by Player A" in output
    assert "[00:00:07.500] Shot by Player B" in output
    assert mock_sleep.call_count == 1  # Only one delay between two events