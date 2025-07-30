import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.patches import Circle
from datetime import datetime
import argparse
import os

def parse_time(timestamp):
    """
    Convert StatsBomb timestamp string to datetime.

    :param timestamp: Timestamp string in the format "%H:%M:%S.%f"
    :type timestamp: str
    :return: Corresponding datetime object
    :rtype: datetime
    """
    return datetime.strptime(timestamp, "%H:%M:%S.%f")

def load_events(filepath):
    """
    Load and parse StatsBomb event JSON for passes, carries, and shots.

    :param filepath: Path to the StatsBomb events JSON file
    :type filepath: str
    :return: List of action dictionaries sorted by time
    :rtype: list[dict]
    :raises ValueError: If no valid actions are found in the file
    """
    with open(filepath) as f:
        events = json.load(f)
    actions = []
    for e in events:
        # Passes
        if (
            e.get("type", {}).get("name") == "Pass"
            and "location" in e
            and "end_location" in e.get("pass", {})
        ):
            actions.append({
                "type": "pass",
                "timestamp": e["timestamp"],
                "start": e["location"],
                "end": e["pass"]["end_location"]
            })
        # Carries
        elif (
            e.get("type", {}).get("name") == "Carry"
            and "location" in e
            and "carry" in e
            and "end_location" in e["carry"]
        ):
            actions.append({
                "type": "carry",
                "timestamp": e["timestamp"],
                "start": e["location"],
                "end": e["carry"]["end_location"]
            })
        # Shots
        elif (
            e.get("type", {}).get("name") == "Shot"
            and "location" in e
            and "shot" in e
            and "end_location" in e["shot"]
        ):
            actions.append({
                "type": "shot",
                "timestamp": e["timestamp"],
                "start": e["location"],
                "end": e["shot"]["end_location"][:2]
            })
    if not actions:
        raise ValueError("No valid passes, carries, or shots found in the provided JSON file.")

    base_time = parse_time(actions[0]["timestamp"])
    for action in actions:
        action["time_sec"] = (parse_time(action["timestamp"]) - base_time).total_seconds()
    return sorted(actions, key=lambda x: x["time_sec"])

def draw_pitch(ax, pitch_color="green"):
    """
    Draw a full football pitch on the given Axes.

    :param ax: Matplotlib Axes object to draw the pitch on
    :type ax: matplotlib.axes.Axes
    :param pitch_color: Background color of the pitch
    :type pitch_color: str
    """
    ax.set_facecolor(pitch_color)
    ax.plot([0, 0, 120, 120, 0], [0, 80, 80, 0, 0], color="black")
    ax.plot([60, 60], [0, 80], color="black", linestyle="--")
    center_circle = Circle((60, 40), 9.15, color='black', fill=False)
    ax.add_patch(center_circle)
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
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("off")

def animate_events(actions, speed=1.0, interval_ms=100, save=False):
    """
    Create an animation of passes, carries, and shots and optionally save as video.

    :param actions: List of action dictionaries to animate
    :type actions: list[dict]
    :param speed: Playback speed multiplier
    :type speed: float
    :param interval_ms: Interval between animation frames in milliseconds
    :type interval_ms: int
    :param save: Whether to save the animation as a video file
    :type save: bool
    :raises ValueError: If no actions are provided
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title("Passes, Carries, and Shots Animation")
    draw_pitch(ax)

    actions = sorted(actions, key=lambda a: a["time_sec"])
    actions_queue = actions.copy()
    arrows = []
    ball = None  # Will hold the ball patch

    def update(frame):
        """
        Update function for each animation frame.

        :param frame: Current frame number
        :type frame: int
        """
        nonlocal ball
        current_time = (frame / 10.0) * speed
        # Remove previous ball
        if ball is not None:
            ball.remove()
            ball = None
        # Find the latest action up to current_time
        latest_action = None
        for a in actions:
            if a["time_sec"] <= current_time:
                latest_action = a
            else:
                break
        # Draw the ball at the end of the latest action
        if latest_action is not None:
            ball_pos = latest_action["end"]
            ball = plt.Circle((ball_pos[0], ball_pos[1]), 1.2, color="white", ec="black", zorder=10)
            ax.add_patch(ball)
        # Draw new arrows for actions up to current_time
        while actions_queue and actions_queue[0]["time_sec"] <= current_time:
            a = actions_queue.pop(0)
            start = a["start"]
            end = a["end"]
            if a["type"] == "pass":
                color = "blue"
                alpha = 0.6
            elif a["type"] == "carry":
                color = "green"
                alpha = 0.7
            else:  # shot
                color = "red"
                alpha = 0.7
            arrow = ax.arrow(
                start[0], start[1],
                end[0] - start[0], end[1] - start[1],
                head_width=1, length_includes_head=True,
                alpha=alpha, color=color
            )
            arrows.append(arrow)

    if not actions:
        raise ValueError("No passes, carries, or shots to animate.")

    total_time = int(max(a["time_sec"] for a in actions)) + 5
    total_frames = int(total_time * 10 / speed)

    anim = FuncAnimation(fig, update, frames=range(total_frames), interval=interval_ms)

    if save:
        output_path = "../resources/animation_all_events.mp4"
        os.makedirs("../resources", exist_ok=True)
        print(f"🎞️  Exporting video to {output_path} ...")
        writer = FFMpegWriter(fps=10)
        anim.save(output_path, writer=writer)
        print("✅ Video saved.")
    else:
        plt.show()

def main():
    """
    Main function to parse arguments and run the animation.

    :return: None
    """
    parser = argparse.ArgumentParser(description="Animate StatsBomb passes, carries, and shots.")
    parser.add_argument("--file", required=True, help="Path to StatsBomb events JSON file")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier")
    parser.add_argument("--save", action="store_true", help="Save animation to resources/animation_all_events.mp4")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"❌ File not found: {args.file}")
        return

    try:
        actions = load_events(args.file)
        print(f"✅ Loaded {len(actions)} passes/carries/shots.")
        animate_events(actions, speed=args.speed, save=args.save)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()