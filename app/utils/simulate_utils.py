"""
Simulation utilities for the Football Analytics Dashboard.

This module provides functions for loading match data, extracting pass and shot events,
aggregating pass networks, and rendering interactive match simulations with Streamlit.

Functions
---------
- load_matches: Load and cache all matches from StatsBomb open-data into a DataFrame.
- load_match_events: Load events for a given match and extract passes & shots.
- get_pass_network_data: Aggregate pass events into a pass network DataFrame.
"""

import os
import json
import numpy as np
import pandas as pd
import streamlit as st
from football_stream_processor.config import DATA_DIR


@st.cache_data
def load_matches():
    """
    Load and cache all matches from StatsBomb open-data into a DataFrame.

    :return: DataFrame of matches with columns [match_id, home_team, away_team, competition, season, date].
    :rtype: pd.DataFrame
    """
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
    """
    Load events for a given match and extract passes & shots.

    :param match_id: Match identifier.
    :type match_id: int or str
    :return: Tuple (passes, xg_team1, xg_team2, times)
    :rtype: (list, np.ndarray, np.ndarray, list)
    """
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


def get_pass_network_data(match_id):
    """
    Parse pass events from StatsBomb event data for a given match and aggregate 
    the number of passes between each passer-receiver pair within the same team.

    :param match_id: Match identifier.
    :type match_id: int or str
    :return: DataFrame with columns ['passer', 'receiver', 'count', 'team'].
    :rtype: pd.DataFrame
    """
    path = os.path.join(DATA_DIR, "events", f"{match_id}.json")
    with open(path, "r", encoding="utf-8") as f:
        events = json.load(f)

    data = []
    for e in events:
        if (
            e.get("type", {}).get("name") == "Pass"
            and "pass" in e
            and "recipient" in e["pass"]
            and "location" in e
        ):
            passer = e["player"]["name"]
            receiver = e["pass"]["recipient"]["name"]
            team = e["team"]["name"]
            data.append({"passer": passer, "receiver": receiver, "team": team})

    df = pd.DataFrame(data)
    if df.empty:
        return df

    # Count number of passes from each passer to each receiver
    df = df.groupby(["passer", "receiver", "team"]).size().reset_index(name="count")

    return df
