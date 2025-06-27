import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.patches import Circle
from datetime import datetime
import argparse
import os


def load_events(filepath):
    """Load StatsBomb event JSON and return pass events with team info."""
    with open(filepath) as f:
        events = json.load(f)

    passes = [
        e for e in events
        if e.get("type", {}).get("name") == "Pass"
        and "location" in e
        and "end_location" in e.get("pass", {})
        and "team" in e
    ]

    if not passes:
        raise ValueError("No valid passes found in the file.")

    base_time = parse_time(passes[0]["timestamp"])
    for e in passes:
        e["time_sec"] = (parse_time(e["timestamp"]) - base_time).total_seconds()

    return passes


def parse_time(t):
    return datetime.strptime(t, "%H:%M:%S.%f")


def draw_pitch(ax, pitch_color="#00E700"):
    ax.set_facecolor(pitch_color)

    # Pitch outline and center line
    ax.plot([0, 0, 120, 120, 0], [0, 80, 80, 0, 0], color="black")
    ax.plot([60, 60], [0, 80], color="black", linestyle="--")

    # Center circle and spot
    ax.add_patch(Circle((60, 40), 9.15, color='black', fill=False))
    ax.plot(60, 40, 'ko')

    # Penalty areas
    ax.plot([0, 18], [21.1, 21.1], color="black")
    ax.plot([18, 18], [21.1, 58.9], color="black")
    ax.plot([0, 18], [58.9, 58.9], color="black")

    ax.plot([102, 120], [21.1, 21.1], color="black")
    ax.plot([102, 102], [21.1, 58.9], color="black")
    ax.plot([102, 120], [58.9, 58.9], color="black")

    # Goals
    ax.plot([0, 0], [36, 44], color="red", linewidth=2)
    ax.plot([120, 120], [36, 44], color="red", linewidth=2)

    ax.set_xlim(0, 120)
    ax.set_ylim(0, 80)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("off")


def animate_passes(passes, speed=1.0, interval_ms=100, save_path=None):
    """Animate passes and optionally export to video."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title("Pass Animation")
    draw_pitch(ax)

    # DO NOT modify original pass list
    passes_sorted = sorted(passes, key=lambda p: p["time_sec"])
    passes_queue = passes_sorted.copy()  # this we will pop from
    team_colors = assign_team_colors(passes_sorted)
    arrows = []

    def update(frame):
        t = (frame / 10.0) * speed  # ✅ speed adjustment FIXED
        while passes_queue and passes_queue[0]["time_sec"] <= t:
            p = passes_queue.pop(0)
            start = p["location"]
            end = p["pass"]["end_location"]
            team = p["team"]["name"]
            color = team_colors.get(team, "blue")
            arrow = ax.arrow(
                start[0], start[1],
                end[0] - start[0], end[1] - start[1],
                head_width=1, length_includes_head=True,
                alpha=0.6, color=color
            )
            arrows.append(arrow)

    total_time = int(max(p["time_sec"] for p in passes_sorted)) + 5
    total_frames = int(total_time * 10 / speed)

    anim = FuncAnimation(fig, update, frames=range(total_frames), interval=interval_ms)

    if save_path:
        print(f"🎞️  Exporting video to {save_path}...")
        writer = FFMpegWriter(fps=10)
        anim.save(save_path, writer=writer)
        print("✅ Video export complete.")
    else:
        plt.show()


def assign_team_colors(passes):
    """Assign two distinct colors to teams in the dataset."""
    teams = list({p["team"]["name"] for p in passes})
    colors = ["blue", "orange"]  # Extend if needed
    return {team: colors[i % len(colors)] for i, team in enumerate(teams)}


def main():
    parser = argparse.ArgumentParser(description="Animate StatsBomb passes with team colors.")
    parser.add_argument("--file", required=True, help="Path to StatsBomb events JSON file")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier")
    parser.add_argument("--save", type=str, help="Path to export video (e.g. out.mp4)")

    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"❌ File not found: {args.file}")
        return

    try:
        passes = load_events(args.file)
        print(f"✅ Loaded {len(passes)} passes from {args.file}")
        animate_passes(passes, speed=args.speed, save_path=args.save)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
