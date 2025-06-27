import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from datetime import datetime

# === Load events ===
with open("../open-data/data/events/22912.json") as f:
    events = json.load(f)

# === Filter passes with required data ===
passes = [
    e for e in events
    if e.get("type", {}).get("name") == "Pass" and "location" in e and "end_location" in e.get("pass", {})
]

print(f"Total passes found: {len(passes)}")

# === Parse timestamps ===
def parse_time(t):
    return datetime.strptime(t, "%H:%M:%S.%f")

# Add relative time in seconds to each pass
start_time = parse_time(passes[0]["timestamp"])
for p in passes:
    p["time_sec"] = (parse_time(p["timestamp"]) - start_time).total_seconds()

# === Set up plot ===
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 120)
ax.set_ylim(0, 80)
ax.axis("off")
ax.set_title("Pass Animation")

# === Draw pitch ===
def draw_pitch():
    ax.set_facecolor("#00E700")  # green field

    # Pitch boundaries
    ax.plot([0, 0, 120, 120, 0], [0, 80, 80, 0, 0], color="black")
    ax.plot([60, 60], [0, 80], color="black", linestyle="--")  # halfway line

    # Center circle & spot
    center_circle = plt.Circle((60, 40), 9.15, color='black', fill=False)
    ax.add_patch(center_circle)
    ax.plot(60, 40, 'ko')

    # Left penalty area
    ax.plot([18, 18], [21.1, 58.9], color="black")
    ax.plot([0, 18], [21.1, 21.1], color="black")
    ax.plot([0, 18], [58.9, 58.9], color="black")

    # Right penalty area
    ax.plot([102, 120], [21.1, 21.1], color="black")
    ax.plot([102, 102], [21.1, 58.9], color="black")
    ax.plot([102, 120], [58.9, 58.9], color="black")

    # Goals
    ax.plot([0, 0], [36, 44], color="red", linewidth=2)
    ax.plot([120, 120], [36, 44], color="red", linewidth=2)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("off")

draw_pitch()

# === Animation function ===
arrows = []

def update(frame):
    t = frame  # 0.1s per frame
    while passes and passes[0]["time_sec"] <= t:
        p = passes.pop(0)
        start = p["location"]
        end = p["pass"]["end_location"]
        arrow = ax.arrow(
            start[0], start[1],
            end[0] - start[0], end[1] - start[1],
            head_width=1, length_includes_head=True,
            alpha=0.6, color="blue"
        )
        arrows.append(arrow)

# === Dynamically calculate frame count ===
max_time = int(max(p["time_sec"] for p in passes)) + 5  # buffer
total_frames = max_time * 10  # 10 frames per second

ani = FuncAnimation(fig, update, frames=range(total_frames), interval=100)

plt.show()
