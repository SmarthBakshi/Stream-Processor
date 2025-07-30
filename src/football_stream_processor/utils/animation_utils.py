import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import os

def parse_time(timestamp):
    return datetime.strptime(timestamp, "%H:%M:%S.%f")

def load_events(filepath):
    with open(filepath) as f:
        events = json.load(f)
    actions = []
    for e in events:
        if e.get("type", {}).get("name") == "Pass" and "location" in e and "end_location" in e.get("pass", {}):
            actions.append({
                "type": "pass",
                "timestamp": e["timestamp"],
                "start": e["location"],
                "end": e["pass"]["end_location"]
            })
        elif e.get("type", {}).get("name") == "Carry" and "location" in e and "carry" in e and "end_location" in e["carry"]:
            actions.append({
                "type": "carry",
                "timestamp": e["timestamp"],
                "start": e["location"],
                "end": e["carry"]["end_location"]
            })
        elif e.get("type", {}).get("name") == "Shot" and "location" in e and "shot" in e and "end_location" in e["shot"]:
            actions.append({
                "type": "shot",
                "timestamp": e["timestamp"],
                "start": e["location"],
                "end": e["shot"]["end_location"][:2]
            })
    if not actions:
        raise ValueError("No valid passes, carries, or shots found in the file.")

    base_time = parse_time(actions[0]["timestamp"])
    for action in actions:
        action["time_sec"] = (parse_time(action["timestamp"]) - base_time).total_seconds()
    return sorted(actions, key=lambda x: x["time_sec"])

def draw_pitch(ax):
    ax.set_facecolor("green")
    ax.plot([0, 0, 120, 120, 0], [0, 80, 80, 0, 0], color="black")
    ax.plot([60, 60], [0, 80], color="black", linestyle="--")
    ax.add_patch(plt.Circle((60, 40), 9.15, fill=False, color="black"))
    ax.plot(60, 40, 'ko')
    ax.plot([18, 18], [21.1, 58.9], color="black")
    ax.plot([0, 18], [21.1, 21.1], color="black")
    ax.plot([0, 18], [58.9, 58.9], color="black")
    ax.plot([102, 120], [21.1, 21.1], color="black")
    ax.plot([102, 102], [21.1, 58.9], color="black")
    ax.plot([102, 120], [58.9, 58.9], color="black")
    ax.plot([0, 0], [36, 44], color="red", linewidth=2)
    ax.plot([120, 120], [36, 44], color="red", linewidth=2)
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 80)
    ax.axis("off")

def render_frame(actions, current_time_sec):
    import matplotlib.pyplot as plt  # ensure imported if used externally
    fig, ax = plt.subplots(figsize=(12, 8))
    draw_pitch(ax)

    latest_action = None
    for action in actions:
        if action["time_sec"] <= current_time_sec:
            latest_action = action
        else:
            break

    for action in actions:
        if action["time_sec"] <= current_time_sec:
            start = action["start"]
            end = action["end"]
            color = {"pass": "blue", "carry": "green", "shot": "red"}.get(action["type"], "white")
            ax.arrow(
                start[0], start[1],
                end[0] - start[0], end[1] - start[1],
                length_includes_head=True,
                head_width=1.5,
                head_length=3,
                color=color,
                alpha=0.6
            )

    if latest_action:
        ball_x, ball_y = latest_action["end"]
        ax.plot(ball_x, ball_y, 'o', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=2)

    ax.set_title(f"Match Events Animation (Time: {current_time_sec:.1f} sec)")
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)
