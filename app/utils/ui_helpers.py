
def kpi_card(title, value, delta=None, color="#333"):
    """Return a styled KPI card as HTML for dark theme."""
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
