import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# === Load the event data ===
with open("../open-data/data/events/22912.json") as f:
    events = json.load(f)

# === Filter pass events ===
passes = [event for event in events if event["type"]["name"] == "Pass"]

# === Plotting setup ===
def draw_pitch(ax):
    """Draw a half football pitch (StatsBomb style: 120x80)."""
    # Pitch Outline & Centre Line
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 80)
    ax.set_facecolor("#228B22")  # ForestGreen

    # Goals
    ax.plot([0, 0], [30, 50], color="black", linewidth=2)

    # Penalty Box
    ax.plot([18, 18], [21.1, 58.9], color="black")
    ax.plot([0, 18], [21.1, 21.1], color="black")
    ax.plot([0, 18], [58.9, 58.9], color="black")

    ax.set_xticks([])
    ax.set_yticks([])

# === Plot passes ===
fig, ax = plt.subplots(figsize=(12, 8))
draw_pitch(ax)

for p in passes:
    start = p.get("location", None)
    end = p.get("pass", {}).get("end_location", None)
    if start and end:
        ax.arrow(
            start[0], start[1],
            end[0] - start[0], end[1] - start[1],
            head_width=1, length_includes_head=True,
            color="blue", alpha=0.5
        )

plt.title("All Passes (from StatsBomb Data)")
plt.show()
