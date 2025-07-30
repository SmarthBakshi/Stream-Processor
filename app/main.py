"""
Main entry point for the ML-powered Football Analytics Dashboard.

This module sets up the Streamlit app, navigation, and page configuration.
It provides access to the Overview, Match Analysis, and Model Insights pages.

Functions
---------
- main: Launches the Streamlit dashboard and handles page navigation.
"""

import streamlit as st

from webpages.overview import overview_page
from webpages.match_analysis import match_analysis_page
from webpages.model_insights import model_insights


def main():
    """
    Launch the Football Analytics Dashboard with navigation.

    Sets up the Streamlit page configuration and sidebar navigation
    for Overview, Match Analysis, and Model Insights pages.

    :return: None
    """
    st.set_page_config(page_title="Football Analytics Dashboard", layout="wide")

    page = st.sidebar.radio(
        "Navigation",
        ["Overview", "Match Analysis", "Model Insights"]
    )

    if page == "Overview":
        overview_page()
    elif page == "Match Analysis":
        match_analysis_page()
    elif page == "Model Insights":
        model_insights()


if __name__ == "__main__":
    main()