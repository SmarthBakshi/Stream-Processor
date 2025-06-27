import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.patches import Circle
from datetime import datetime
import argparse
import os


def load_events(filepath):
    """Load and parse StatsBomb event JSON."""
    with open(filepath) as f:
        events = json.load(f)
    passes = [
        e for e in events
        if e.get("type", {}).get("name") == "Pass"
        and "location" in e
        and "end_location" in e.get("pass", {})
    ]
    if not passes:
        raise ValueError("No valid passes found in the provided JSON file.")

    base_time = parse_time(passes[0]["timestamp"])
    for event in passes:
        event["time_sec"] = (parse_time(event["timestamp"]) - base_time).total_seconds()

    return passes


def parse_time(timestamp):
    """Convert StatsBomb timestamp string to datetime."""
    return datetime.strptime(timestamp, "%H:%M:%S.%f")


def draw_pitch(ax, pitch_color="#00E700"):
    """Draw a full football pitch on given Axes."""
    ax.set_facecolor(pitch_color)

    # Pitch outline & halves
    ax.plot([0, 0, 120, 120, 0], [0, 80, 80, 0, 0], color="black")
    ax.plot([60, 60], [0, 80], color="black", linestyle="--")

    # Center circle & spot
    center_circle = Circle((60, 40), 9.15, color='black', fill=False)
    ax.add_patch(center_circle)
    ax.plot(60, 40, 'ko')

    # Penalty areas
    ax.plot([18, 18], [21.1, 58.9], color="black")
    ax.plot([0, 18], [21.1, 21.1], color="black")
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


def animate_passes(passes, speed=1.0, interval_ms=100, save=False):
    """Create an animation of passes and optionally save as video."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title("Pass Animation")
    draw_pitch(ax)

    passes = sorted(passes, key=lambda p: p["time_sec"])
    passes_queue = passes.copy()
    arrows = []

    def update(frame):
        current_time = (frame / 10.0) * speed
        while passes_queue and passes_queue[0]["time_sec"] <= current_time:
            p = passes_queue.pop(0)
            start = p["location"]
            end = p["pass"]["end_location"]
            arrow = ax.arrow(
                start[0], start[1],
                end[0] - start[0], end[1] - start[1],
                head_width=1, length_includes_head=True,
                alpha=0.6, color="blue"
            )
            arrows.append(arrow)

    if not passes:
        raise ValueError("No passes to animate.")

    total_time = int(max(p["time_sec"] for p in passes)) + 5
    total_frames = int(total_time * 10 / speed)

    anim = FuncAnimation(fig, update, frames=range(total_frames), interval=interval_ms)

    if save:
        output_path = "../resources/animation_passes.mp4"
        os.makedirs("../resources", exist_ok=True)
        print(f"🎞️  Exporting video to {output_path} ...")
        writer = FFMpegWriter(fps=10)
        anim.save(output_path, writer=writer)
        print("✅ Video saved.")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="Animate StatsBomb passes.")
    parser.add_argument("--file", required=True, help="Path to StatsBomb events JSON file")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier")
    parser.add_argument("--save", action="store_true", help="Save animation to resources/animation_passes.mp4")

    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"❌ File not found: {args.file}")
        return

    try:
        passes = load_events(args.file)
        print(f"✅ Loaded {len(passes)} passes.")
        animate_passes(passes, speed=args.speed, save=args.save)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
