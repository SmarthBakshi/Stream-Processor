import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from football_stream_processor.config import DATA_DIR
from mplsoccer import Pitch
import streamlit as st
import matplotlib.patches as mpatches


def render_shot_map(match_id):
    path = os.path.join(DATA_DIR, "events", f"{match_id}.json")
    with open(path, "r") as f:
        events = json.load(f)

    shots = []
    for e in events:
        if e.get("type", {}).get("name") == "Shot" and "location" in e:
            loc = e["location"]
            xg = e.get("shot", {}).get("statsbomb_xg", 0)
            outcome = e.get("shot", {}).get("outcome", {}).get("name", "Unknown")
            shots.append({
                "x": loc[0], "y": loc[1],
                "xg": float(xg),
                "outcome": outcome
            })

    if not shots:
        st.info("No shots found for this match.")
        return

    df = pd.DataFrame(shots)

    outcome_colors = {
        "Goal": "#d62728",      # red
        "Off T": "#ff7f0e",     # orange
        "Wayward": "#1f77b4",   # blue
        "Saved": "#17becf",     # cyan
        "Blocked": "#2ca02c",   # green
        "Unknown": "#999999"    # gray
    }
    df["color"] = df["outcome"].map(outcome_colors).fillna("#bbbbbb")

    # Setup pitch
    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color='#111',
        line_color='white',
        goal_type='box',  # ensures both goals are drawn
        line_zorder=1
    )

    fig, ax = pitch.draw(figsize=(7, 4.5))  # Smaller figure
    fig.patch.set_facecolor('#111')   # Match background to pitch color
    ax.set_facecolor('#111')          # Ensure axis area matches pitch

    pitch.scatter(
        df["x"], df["y"],
        s=df["xg"] * 1800,  # Slightly reduced size
        color=df["color"],
        ax=ax,
        edgecolors='white',
        linewidth=0.8,
        alpha=0.85,
        zorder=2
    )

    ax.set_title("Shot Map (circle size = xG)", color='white', fontsize=14, pad=15)

    # Legend below
    handles = [
        mpatches.Patch(color=color, label=label)
        for label, color in outcome_colors.items()
        if label in df['outcome'].unique()
    ]
    fig.legend(
        handles=handles,
        loc='lower center',
        ncol=5,
        frameon=False,
        fontsize=6,
        labelcolor='white',
        
        bbox_to_anchor=(0.5, -0.07)
    )

    st.pyplot(fig, use_container_width=True)  # Responsive to screen size

    st.markdown(
        "<div style='text-align:center; color:#ddd; font-size:16px; margin-top:10px;'>"
        "Each circle represents a shot. Color = shot outcome."
        "</div>",
        unsafe_allow_html=True
    )
