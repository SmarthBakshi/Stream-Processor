import streamlit as st
from streamlit_autorefresh import st_autorefresh
import os
from football_stream_processor.utils.animation_utils import load_events, render_frame

def animation_page():
    st.title("StatsBomb Match Animation")

    uploaded_file = st.file_uploader("Upload StatsBomb events JSON", type=["json"])
    if not uploaded_file:
        st.info("Please upload a StatsBomb events JSON file.")
        return

    tmp_path = "./tmp_events.json"
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        actions = load_events(tmp_path)
    except Exception as e:
        st.error(f"Error loading events: {e}")
        return

    max_time = max(action["time_sec"] for action in actions)

    if "frame" not in st.session_state:
        st.session_state.frame = 0.0
    if "playing" not in st.session_state:
        st.session_state.playing = False
    if "speed" not in st.session_state:
        st.session_state.speed = 1.0

    col1, col2, col3 = st.columns([1, 2, 3])
    with col1:
        if st.button("▶ Play"):
            st.session_state.playing = True
        if st.button("⏸ Pause"):
            st.session_state.playing = False
    with col2:
        st.session_state.frame = st.slider("Timeline (seconds)", 0.0, max_time, st.session_state.frame, step=0.5)
    with col3:
        st.session_state.speed = st.slider("Playback Speed", 0.5, 3.0, st.session_state.speed, 0.5)

    if st.session_state.playing:
        st_autorefresh(interval=50, key="autorefresh")
        st.session_state.frame += 0.5 * st.session_state.speed
        if st.session_state.frame > max_time:
            st.session_state.frame = max_time
            st.session_state.playing = False

    render_frame(actions, st.session_state.frame)
