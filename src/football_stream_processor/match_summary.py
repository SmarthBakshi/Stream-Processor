
import json
from collections import defaultdict

def analyze_match_metrics(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)

    pass_attempts = defaultdict(int)
    pass_completions = defaultdict(int)
    carry_counts = defaultdict(int)
    dribble_attempts = defaultdict(int)
    dribble_successes = defaultdict(int)
    total_xg = defaultdict(float)
    turnovers = defaultdict(int)
    recoveries = defaultdict(int)
    pressures = defaultdict(int)
    successful_pressures = defaultdict(int)

    for event in data:
        team = event.get("team", {}).get("name")
        if not team:
            continue
        event_type = event.get("type", {}).get("name")

        if event_type == "Pass":
            pass_attempts[team] += 1
            if "outcome" not in event.get("pass", {}):
                pass_completions[team] += 1
        elif event_type == "Carry":
            carry_counts[team] += 1
        elif event_type == "Dribble":
            dribble_attempts[team] += 1
            if event.get("dribble", {}).get("outcome", {}).get("name") == "Complete":
                dribble_successes[team] += 1
        elif event_type == "Shot":
            total_xg[team] += event.get("shot", {}).get("statsbomb_xg", 0.0)
        elif event_type in {"Miscontrol", "Dispossessed"}:
            turnovers[team] += 1
        elif event_type == "Ball Recovery":
            recoveries[team] += 1
        elif event_type == "Pressure":
            pressures[team] += 1
            related_ids = event.get("related_events", [])
            for rel_event in data:
                if rel_event["id"] in related_ids:
                    rel_type = rel_event.get("type", {}).get("name")
                    if rel_type in {"Miscontrol", "Dispossessed", "Incomplete Pass"}:
                        successful_pressures[team] += 1
                        break

    pass_accuracy = {team: (pass_completions[team] / pass_attempts[team]) * 100 if pass_attempts[team] else 0 for team in pass_attempts}
    pressure_success_rate = {team: (successful_pressures[team] / pressures[team]) * 100 if pressures[team] else 0 for team in pressures}

    summary_metrics = {
        "Pass Accuracy (%)": pass_accuracy,
        "Carries": dict(carry_counts),
        "Successful Dribbles": dict(dribble_successes),
        "Dribble Success Rate (%)": {team: (dribble_successes[team] / dribble_attempts[team]) * 100 if dribble_attempts[team] else 0 for team in dribble_attempts},
        "Total xG": dict(total_xg),
        "Turnovers": dict(turnovers),
        "Ball Recoveries": dict(recoveries),
        "Pressures Applied": dict(pressures),
        "Pressure Success Rate (%)": pressure_success_rate
    }

    return summary_metrics

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python match_summary.py <path_to_json>")
    else:
        metrics = analyze_match_metrics(sys.argv[1])
        for key, value in metrics.items():
            print(f"\n{key}:")
            for team, val in value.items():
                print(f"  {team}: {val:.2f}" if isinstance(val, float) else f"  {team}: {val}")
