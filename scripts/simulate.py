import json
import time
from datetime import datetime

# Load the JSON file
with open("/Users/smarthbakshi/projects/football_stream_processor/open-data/data/events/22912.json") as f:
    events = json.load(f)

def parse_timestamp(t):
    return datetime.strptime(t, "%H:%M:%S.%f")

# Initialize base time (simulate from zero)
start_time = parse_timestamp(events[0]["timestamp"])

def simulate_events(events):
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