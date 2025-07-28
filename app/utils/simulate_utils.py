import os
import json
import time
import numpy as np
import pandas as pd
import streamlit as st
from football_stream_processor.config import DATA_DIR
import plotly.graph_objects as go

MAJOR_COMPS = {"English Premier League", "La Liga", "Champions League"}

@st.cache_data
def load_matches():
    """Load and cache all matches from StatsBomb open-data into a DataFrame."""
    matches = []
    matches_dir = os.path.join(DATA_DIR, "matches")

    for comp in os.listdir(matches_dir):
        comp_path = os.path.join(matches_dir, comp)
        for season_file in os.listdir(comp_path):
            season_path = os.path.join(comp_path, season_file)
            if not season_path.endswith(".json"):
                continue

            with open(season_path, "r") as f:
                data = json.load(f)
                for m in data:
                    comp_name = m["competition"]["competition_name"]
                    if comp_name not in MAJOR_COMPS:
                        continue
                    matches.append({
                        "match_id": m["match_id"],
                        "home_team": m["home_team"]["home_team_name"],
                        "away_team": m["away_team"]["away_team_name"],
                        "competition": comp_name,
                        "season": m["season"]["season_name"],
                        "date": m["match_date"]
                    })
    df = pd.DataFrame(matches)
    return df.sort_values(["competition", "season", "date"])


@st.cache_data
def load_match_events(match_id):
    """Load events for a given match and extract passes & shots."""
    path = os.path.join(DATA_DIR, "events", f"{match_id}.json")
    with open(path, "r") as f:
        events = json.load(f)

    passes = []
    xg_team1, xg_team2, times = [], [], []
    home_name = events[0]["team"]["name"] if events else "Home"

    for e in events:
        if e["type"]["name"] == "Pass" and "location" in e and e["location"]:
            x, y = e["location"]
            passes.append({
                "x": x / 1.2,  # Rescale 120 -> 100
                "y": y / 1.33, # Rescale 80 -> 60
                "time": int(e.get("minute", 0) * 60 + e.get("second", 0))
            })
        if e["type"]["name"] == "Shot":
            team = e["team"]["name"]
            xg = float(e.get("shot", {}).get("statsbomb_xg", 0))
            t = int(e.get("minute", 0) * 60 + e.get("second", 0))
            if team == home_name:
                xg_team1.append(xg)
                xg_team2.append(0)
            else:
                xg_team2.append(xg)
                xg_team1.append(0)
            times.append(t)

    # Ensure same length arrays for plotting
    times = sorted(times) if times else [0]
    xg_team1 = np.cumsum(xg_team1) if xg_team1 else np.zeros(len(times))
    xg_team2 = np.cumsum(xg_team2) if xg_team2 else np.zeros(len(times))

    return passes, xg_team1, xg_team2, times


def render_match_simulator(passes, xg_team1, xg_team2, times):
    """Render the match simulator with pitch animation and xG progression."""
    if not passes:
        st.warning("No passes found for this match.")
        return

    if "frame" not in st.session_state:
        st.session_state.frame = 0
    if "playing" not in st.session_state:
        st.session_state.playing = False

    # Controls
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("▶️ Play"):
            st.session_state.playing = True
        if st.button("⏸ Pause"):
            st.session_state.playing = False
    with col3:
        speed = st.selectbox("Speed (x)", [0.5, 1, 2], index=1)

    with col2:
        st.session_state.frame = st.slider(
            "Timeline (seconds)",
            0,
            times[-1] if times else 0,
            st.session_state.frame
        )

    # Increment frame if playing
    if st.session_state.playing:
        if st.session_state.frame < (times[-1] if times else 0):
            st.session_state.frame += speed
        else:
            st.session_state.playing = False
        time.sleep(0.1)
        st.rerun()

    # Current ball position
    x_coords = [p["x"] for p in passes]
    y_coords = [p["y"] for p in passes]
    idx = min(range(len(passes)), key=lambda i: abs(passes[i]["time"] - st.session_state.frame))
    ball_x = x_coords[idx]
    ball_y = y_coords[idx]

    # Draw pitch
    pitch = go.Figure()
    pitch.add_shape(type="rect", x0=0, y0=0, x1=100, y1=60,
                    line=dict(color="white"), fillcolor="green")
    pitch.add_trace(go.Scatter(x=x_coords, y=y_coords, mode="lines+markers",
                               line=dict(color="orange"), name="Pass Path"))
    pitch.add_trace(go.Scatter(x=[ball_x], y=[ball_y], mode="markers",
                               marker=dict(color="red", size=12), name="Ball"))
    pitch.update_layout(
        title="Pass Sequence Simulation",
        xaxis=dict(range=[0, 100], visible=False),
        yaxis=dict(range=[0, 60], visible=False),
        plot_bgcolor="green",
        height=400
    )
    st.plotly_chart(pitch, use_container_width=True)

    # Draw xG progression
    xg_fig = go.Figure()
    xg_fig.add_trace(go.Scatter(x=times, y=xg_team1, name="Home Team", line=dict(color="blue")))
    xg_fig.add_trace(go.Scatter(x=times, y=xg_team2, name="Away Team", line=dict(color="red")))
    xg_fig.add_vline(x=st.session_state.frame, line_dash="dash", line_color="gray")
    xg_fig.update_layout(title="xG Progression", xaxis_title="Time (s)", yaxis_title="xG")
    st.plotly_chart(xg_fig, use_container_width=True)
