import streamlit as st
from match_analysis_page import match_analysis_page
from model_insights import model_insights
from overview import overview_page


def main():
    st.set_page_config(page_title="Football Analytics Dashboard", layout="wide")

    page = st.sidebar.radio("Navigation", ["Overview", "Match Analysis", "Model Insights"])

    if page == "Overview":
        overview_page()

    elif page == "Match Analysis":
        match_analysis_page()

        
    elif page == "Model Insights":
        model_insights()

if __name__ == "__main__":
    main()