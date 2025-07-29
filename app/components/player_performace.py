import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from football_stream_processor.config import DATA_DIR


def plot_touch_heatmap_mpl(df_touches, player_name):

    fig, ax = plt.subplots(figsize=(8, 6))

    pitch = Pitch(pitch_type='statsbomb',
                  pitch_color='#0e1117',  # dark theme
                  line_color='white',
                  line_zorder=2)
    pitch.draw(ax=ax)

    # Create 2D histogram
    bin_statistic = pitch.bin_statistic(
        df_touches['x'], df_touches['y'],
        statistic='count', bins=(30, 20)
    )

    # Heatmap with better contrast
    pitch.heatmap(bin_statistic, ax=ax,
                  cmap='hot',
                  edgecolors='none',
                  zorder=1)

    # Optional: overlay actual touch dots
    pitch.scatter(df_touches['x'], df_touches['y'], ax=ax,
                  color='white', s=5, alpha=0.3, zorder=3)

    ax.set_title(f"{player_name} Touch Heatmap", color='white', fontsize=16, pad=10)
    return fig


def plot_shot_map_mpl(df_shots, player_name):
    fig, ax = plt.subplots(figsize=(6, 5))
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#111', line_color='white')
    pitch.draw(ax=ax)

    pitch.scatter(df_shots['x'], df_shots['y'], s=df_shots['xg'] * 2000, ax=ax,
                  alpha=0.8, edgecolors='black', linewidth=1, color='red')

    ax.set_title(f"Shot Map (xG-weighted)", color='white', fontsize=14, pad=10)
    return fig


def render_player_performance(match_id):
    path = os.path.join(DATA_DIR, "events", f"{match_id}.json")
    with open(path, "r") as f:
        events = json.load(f)

    players = sorted({e["player"]["name"] for e in events if "player" in e})
    selected_player = st.selectbox("Select Player", players)

    player_events = [e for e in events if e.get("player", {}).get("name") == selected_player]

    # KPIs
    total_passes = sum(1 for e in player_events if e.get("type", {}).get("name") == "Pass")
    completed_passes = sum(1 for e in player_events if e.get("type", {}).get("name") == "Pass" and e.get("pass", {}).get("outcome") is None)
    pass_acc = (completed_passes / total_passes * 100) if total_passes else 0

    total_shots = sum(1 for e in player_events if e.get("type", {}).get("name") == "Shot")
    xg_total = sum(float(e.get("shot", {}).get("statsbomb_xg", 0)) for e in player_events)

    # KPI Cards
    st.markdown(f"""
    <div style="display: flex; gap: 2rem; justify-content: center; margin-top: 1rem;">
        <div style="background: #222; padding: 1.5rem 2rem; border-radius: 12px; min-width: 180px; text-align:center;">
            <h3 style="color:#0cf; font-size: 2rem;">{pass_acc:.1f}%</h3>
            <div style="color:#aaa;">Pass Accuracy</div>
        </div>
        <div style="background: #222; padding: 1.5rem 2rem; border-radius: 12px; min-width: 180px; text-align:center;">
            <h3 style="color:#0cf; font-size: 2rem;">{total_shots}</h3>
            <div style="color:#aaa;">Total Shots</div>
        </div>
        <div style="background: #222; padding: 1.5rem 2rem; border-radius: 12px; min-width: 180px; text-align:center;">
            <h3 style="color:#0cf; font-size: 2rem;">{xg_total:.2f}</h3>
            <div style="color:#aaa;">Expected Goals (xG)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Plot side-by-side
    col1, col2 = st.columns(2)

    with col1:
        touches = [(e["location"][0], e["location"][1]) for e in player_events if "location" in e]
        if touches:
            df_touches = pd.DataFrame(touches, columns=["x", "y"])
            fig_touch = plot_touch_heatmap_mpl(df_touches, selected_player)
            st.pyplot(fig_touch)
            st.markdown(
                f"<div style='text-align:center; color:#fff; font-size:14px;'>"
                f"{selected_player}'s touch distribution across the pitch. Darker areas indicate more touches."
                f"</div>", unsafe_allow_html=True
            )
        else:
            st.info(f"No touches found for {selected_player}.")

    with col2:
        shot_events = [e for e in player_events if e.get("type", {}).get("name") == "Shot" and "location" in e]
        if shot_events:
            shot_locs = [(e["location"][0], e["location"][1], float(e.get("shot", {}).get("statsbomb_xg", 0))) for e in shot_events]
            df_shots = pd.DataFrame(shot_locs, columns=["x", "y", "xg"])
            fig_shots = plot_shot_map_mpl(df_shots, selected_player)
            st.pyplot(fig_shots)
            st.markdown(
                f"<div style='text-align:center; color:#fff; font-size:14px;'>"
                f"Each dot shows a shot by {selected_player}. Size and color reflect xG (expected goal probability)."
                f"</div>", unsafe_allow_html=True
            )

        else:
            st.info(f"No shots found for {selected_player}.")
