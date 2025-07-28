import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

def load_dummy_events():
    """Generate dummy events and xG progression for simulation."""
    events = [
        {"x": 10, "y": 30, "time": 0},
        {"x": 30, "y": 40, "time": 10},
        {"x": 50, "y": 20, "time": 20},
        {"x": 70, "y": 50, "time": 30},
        {"x": 90, "y": 40, "time": 40}
    ]
    times = [e["time"] for e in events]
    xg_team1 = np.cumsum(np.random.rand(len(events)) * 0.2)
    xg_team2 = np.cumsum(np.random.rand(len(events)) * 0.2)
    return events, xg_team1, xg_team2, times

def render_match_simulator(events, xg_team1, xg_team2, times):
    """Render the match simulator with pitch animation and xG progression."""
    # Initialize state
    if "frame" not in st.session_state:
        st.session_state.frame = 0
    if "playing" not in st.session_state:
        st.session_state.playing = False

    # Controls
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("▶️ Play"):
            st.session_state.playing = True
        if st.button("⏸ Pause"):
            st.session_state.playing = False

    with col2:
        st.session_state.frame = st.slider(
            "Timeline (seconds)",
            0,
            times[-1],
            st.session_state.frame
        )

    # Increment frame if playing
    if st.session_state.playing:
        if st.session_state.frame < times[-1]:
            st.session_state.frame += 1
        else:
            st.session_state.playing = False
        time.sleep(0.1)
        st.rerun()

    # Determine current ball position
    x_coords = [e["x"] for e in events]
    y_coords = [e["y"] for e in events]
    current_idx = min(range(len(times)), key=lambda i: abs(times[i] - st.session_state.frame))
    ball_x = x_coords[current_idx]
    ball_y = y_coords[current_idx]

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

    # Draw xG progression with timeline marker
    xg_fig = go.Figure()
    xg_fig.add_trace(go.Scatter(x=times, y=xg_team1, name="Team 1", line=dict(color="blue")))
    xg_fig.add_trace(go.Scatter(x=times, y=xg_team2, name="Team 2", line=dict(color="red")))
    xg_fig.add_vline(x=st.session_state.frame, line_dash="dash", line_color="gray")
    xg_fig.update_layout(title="xG Progression", xaxis_title="Time (s)", yaxis_title="xG")
    st.plotly_chart(xg_fig, use_container_width=True)
