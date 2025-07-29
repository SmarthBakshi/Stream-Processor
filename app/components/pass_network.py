from pyvis.network import Network
import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
from utils.simulate_utils import get_pass_network_data
import tempfile


def render_pass_network(match_id):
    df = get_pass_network_data(match_id)

    if df.empty:
        st.warning("No pass data available for this match.")
        return

    # Filter out low-frequency passes and unknowns
    df = df[df['count'] >= 3]
    df = df[~df['passer'].isin(['Unknown']) & ~df['receiver'].isin(['Unknown'])]

    # Build player-to-team mapping
    player_teams = {}
    for _, row in df.iterrows():
        player_teams[row['passer']] = row['team']
        player_teams[row['receiver']] = player_teams.get(row['receiver'], row['team'])

    teams = list(df['team'].unique())

    # Create PyVis network
    net = Network(height="650px", width="100%", bgcolor="#111", font_color="white", directed=True)
    net.toggle_physics(False)  # Static layout

    # Add nodes
    players = set(df['passer']).union(set(df['receiver']))
    for player in players:
        total_passes = df[(df['passer'] == player) | (df['receiver'] == player)]['count'].sum()
        team = player_teams.get(player, "Unknown")
        color = "#1f77b4" if team == teams[0] else "#d62728"
        size = min(10 + total_passes * 0.5, 40)

        net.add_node(
            player,
            label=player,
            size=size,
            color=color,
            title=f"{player}<br>Total Passes: {total_passes}"
        )

    # Add edges
    for _, row in df.iterrows():
        net.add_edge(
            row['passer'],
            row['receiver'],
            value=row['count'],
            color="#aaa",
            title=f"{row['count']} passes"
        )

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        net.save_graph(tmp_file.name)

        with open(tmp_file.name, "r", encoding="utf-8") as f:
            html = f.read()

    # Inject custom CSS into HTML head
    html = html.replace(
        "<head>",
        """<head>
        <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #111 !important;
        }
        iframe, .network {
            border: none !important;
            box-shadow: none !important;
            margin: 0 !important;
            padding: 0 !important;
            background-color: transparent !important;
        }
        </style>
        """
    )

    # Render the PyVis graph inside Streamlit
    components.html(html, height=650, scrolling=False)
