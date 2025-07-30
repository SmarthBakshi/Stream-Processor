"""
Match Analysis page for the ML-powered Football Analytics Dashboard.

This module provides interactive match-level visualizations and KPIs,
including shot maps, player performance, pass networks, and xG timelines.

Functions
---------
- get_match_kpis: Compute key match-level KPIs (total shots, passes, xG, pass accuracy).
- render_xg_timeline: Plot cumulative xG over time for both teams.
- match_analysis_page: Renders the match analysis dashboard page.
"""

import os
import json
import streamlit as st
import plotly.graph_objects as go

from utils.simulate_utils import load_matches, load_match_events
from utils.ui_helpers import kpi_card

from football_stream_processor.config import DATA_DIR

from components.shot_map import render_shot_map
from components.player_performace import render_player_performance
from components.pass_network import render_pass_network


def get_match_kpis(match_id):
    """
    Compute key match-level KPIs (total shots, passes, xG, pass accuracy).

    :param match_id: Match identifier.
    :type match_id: int or str
    :return: Dictionary of KPIs.
    :rtype: dict
    """
    path = os.path.join(DATA_DIR, "events", f"{match_id}.json")
    with open(path, "r") as f:
        events = json.load(f)

    total_shots = sum(1 for e in events if e.get("type", {}).get("name") == "Shot")
    total_passes = sum(1 for e in events if e.get("type", {}).get("name") == "Pass")
    completed_passes = sum(
        1 for e in events
        if e.get("type", {}).get("name") == "Pass" and e.get("pass", {}).get("outcome") is None
    )
    total_xg = sum(float(e.get("shot", {}).get("statsbomb_xg", 0)) for e in events)
    pass_acc = (completed_passes / total_passes * 100) if total_passes else 0

    return {
        "shots": total_shots,
        "passes": total_passes,
        "pass_accuracy": pass_acc,
        "total_xg": total_xg,
    }


def render_xg_timeline(xg_team1, xg_team2, times, team1_name, team2_name):
    """
    Plot cumulative xG over time for both teams.

    :param xg_team1: List of cumulative xG values for team 1.
    :param xg_team2: List of cumulative xG values for team 2.
    :param times: List of time points.
    :param team1_name: Name of team 1.
    :param team2_name: Name of team 2.
    :return: Plotly Figure object.
    :rtype: plotly.graph_objects.Figure
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=xg_team1, name=team1_name,
                             line=dict(color="#1f77b4", width=3)))
    fig.add_trace(go.Scatter(x=times, y=xg_team2, name=team2_name,
                             line=dict(color="#d62728", width=3)))

    fig.update_layout(
        template="plotly_dark",
        title="<b>xG Accumulation Over Time</b>",
        title_font=dict(size=22),
        xaxis=dict(title="Match Time (Seconds)", gridcolor="#333", zerolinecolor="#444"),
        yaxis=dict(title="Cumulative xG", gridcolor="#333", zerolinecolor="#444"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        plot_bgcolor="#111",
        paper_bgcolor="#111",
        font=dict(color="white")
    )
    return fig


def match_analysis_page():
    """
    Render the Match Analysis Dashboard page.

    Displays:
    - Match KPIs (shots, passes, pass accuracy, xG)
    - Shot map, player performance, pass network, and xG timeline visualizations

    :return: None
    """
    # Global Dark Style
    st.markdown(
        """
        <style>
            body {
                background-color: #111;
                color: white;
            }
            .stApp {
                background-color: #111;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h1 style='color:white;text-align:center;'>⚽ Match Analysis Dashboard</h1>", unsafe_allow_html=True)

    # Match selector
    matches_df = load_matches()
    match_id = st.selectbox(
        "Select a Match",
        matches_df["match_id"].tolist(),
        format_func=lambda mid: (
            f"{matches_df.loc[matches_df['match_id']==mid, 'home_team'].values[0]} vs "
            f"{matches_df.loc[matches_df['match_id']==mid, 'away_team'].values[0]} "
            f"({matches_df.loc[matches_df['match_id']==mid, 'date'].values[0]})"
        )
    )

    # Load KPIs & Events
    passes, xg_team1, xg_team2, times = load_match_events(match_id)
    home_team = matches_df.loc[matches_df['match_id'] == match_id, 'home_team'].values[0]
    away_team = matches_df.loc[matches_df['match_id'] == match_id, 'away_team'].values[0]
    kpis = get_match_kpis(match_id)

    # KPI Cards
    st.markdown("<h3 style='color:#ccc;'>Match KPIs</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(kpi_card("Total Shots", kpis["shots"]), unsafe_allow_html=True)
    col2.markdown(kpi_card("Total Passes", kpis["passes"]), unsafe_allow_html=True)
    col3.markdown(kpi_card("Pass Accuracy", f"{kpis['pass_accuracy']:.1f}%"), unsafe_allow_html=True)
    col4.markdown(kpi_card("Total xG", f"{kpis['total_xg']:.2f}"), unsafe_allow_html=True)

    st.markdown("---")

    # Detailed Analysis Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Shot Map", "Player Performance", "Pass Network", "xG Timeline"])
    with tab1:
        render_shot_map(match_id)
    with tab2:
        render_player_performance(match_id)
    with tab3:
        render_pass_network(match_id)
    with tab4:
        fig_xg = render_xg_timeline(xg_team1, xg_team2, times, home_team, away_team)
        st.plotly_chart(fig_xg, use_container_width=True)
    return