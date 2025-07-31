"""
Simulate real-time playback of StatsBomb events.

This script loads event data and prints each event with a simulated real-time delay.
"""

import json
import time
from datetime import datetime

# Load the JSON file
with open("../../../open-data/data/events/22912.json") as f:
    events = json.load(f)

def parse_timestamp(t):
    """
    Convert StatsBomb timestamp string to datetime.

    :param t: Timestamp string in the format "%H:%M:%S.%f"
    :type t: str
    :return: Corresponding datetime object
    :rtype: datetime
    """
    return datetime.strptime(t, "%H:%M:%S.%f")

# Initialize base time (simulate from zero)
start_time = parse_timestamp(events[0]["timestamp"])

def simulate_events(events):
    """
    Simulate real-time playback of events, printing each event with a delay.

    :param events: List of event dictionaries
    :type events: list[dict]
    """
    for i in range(len(events)):
        event = events[i]
        current_time = parse_timestamp(event["timestamp"])
        
        if i > 0:
            prev_time = parse_timestamp(events[i-1]["timestamp"])
            gap = (current_time - prev_time).total_seconds()
            time.sleep(gap)  # Simulate real-time delay

        # Simulate sending this event (e.g., to a function or API)
        print(f"[{event['timestamp']}] {event['type']['name']} by {event['player']['name'] if 'player' in event else 'N/A'}")

if __name__ == "__main__":
    simulate_events(events)