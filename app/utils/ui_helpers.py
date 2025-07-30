"""
UI helper utilities for the Football Analytics Dashboard.

This module provides reusable UI components for Streamlit, such as styled KPI cards.

Functions
---------
- kpi_card: Return a styled KPI card as HTML for dark theme.
"""

def kpi_card(title, value, delta=None, color="#333"):
    """
    Return a styled KPI card as HTML for dark theme.

    :param title: Title of the KPI.
    :type title: str
    :param value: Value to display.
    :type value: str or number
    :param delta: Optional delta or change indicator.
    :type delta: str or number or None
    :param color: Background color for the card.
    :type color: str
    :return: HTML string for the KPI card.
    :rtype: str
    """
    delta_html = f"<span style='font-size:14px;color:#aaa'>{delta}</span>" if delta else ""
    return f"""
    <div style="
        background-color:{color};
        border-radius:15px;
        padding:20px;
        text-align:center;
        box-shadow:0 0 8px rgba(0,0,0,0.4);
        color:white;
        font-family:sans-serif;
        min-width:150px;
    ">
        <div style="font-size:16px; opacity:0.8;">{title}</div>
        <div style="font-size:32px; font-weight:bold;">{value}</div>
        {delta_html}
    </div>
    """
