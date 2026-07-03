"""Network Monitor Dashboard (Streamlit).

Run with:  streamlit run app.py
Config via env vars: MONITOR_URL, REFRESH_INTERVAL, DASHBOARD_TITLE, CHART_HEIGHT.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import config
from data_parser import NetworkMonitorParser

st.set_page_config(page_title=config.DASHBOARD_TITLE, page_icon="📡", layout="wide")
st.title(config.DASHBOARD_TITLE)

url = st.sidebar.text_input("Monitor URL", value=config.MONITOR_URL)

parser = NetworkMonitorParser(url)


def line_figure(frame, y_title):
    """WebGL line chart from a wide frame (DateTime + one column per target)."""
    fig = go.Figure()
    for col in frame.columns:
        if col != "DateTime":
            fig.add_trace(go.Scattergl(x=frame["DateTime"], y=frame[col], mode="lines", name=col))
    fig.update_layout(
        height=config.CHART_HEIGHT,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis_title="Time",
        yaxis_title=y_title,
        hovermode="x unified",
        legend=dict(orientation="h"),
    )
    return fig


@st.fragment(run_every=config.REFRESH_INTERVAL)
def current_status():
    st.subheader("📊 Current Status")
    try:
        results = parser.parse_latest_results()
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return

    if not results:
        st.info("No current data available.")
        return

    # Wrap metrics 4-per-row.
    items = list(results.items())
    for row_start in range(0, len(items), 4):
        row = items[row_start : row_start + 4]
        for col, (target, data) in zip(st.columns(len(row)), row):
            loss = data.get("loss_percent", 0)
            icon = "🟢" if loss == 0 else "🟡" if loss < 25 else "🟠" if loss < 75 else "🔴"
            avg = data.get("avg_delay")
            col.metric(
                f"{icon} {target}",
                f"{avg:.1f} ms" if avg is not None else "—",
                delta=f"{loss}% loss",
                delta_color="inverse",
            )
            col.caption(f"📦 {data.get('received', 0)}/{data.get('transmitted', 0)}")


current_status()

st.subheader("📈 Historical Data")
try:
    files = parser.get_all_daily_files()
except Exception as e:
    files = []
    st.sidebar.error(f"❌ Error listing files: {e}")

selected = st.sidebar.selectbox(
    "Select a date", files, index=None, placeholder="Select a date to view historical data"
)

if selected:
    df = parser.parse_daily_csv(selected)
    if df.empty:
        st.info("📭 No data available for selected date.")
    else:
        active = parser.get_active_targets(df)
        ping = pd.DataFrame({"DateTime": df["DateTime"]})
        loss = pd.DataFrame({"DateTime": df["DateTime"]})
        for t in active:
            n, name = t["number"], t["name"]
            dcol, lcol = f"DelayAvg{n}", f"LossPct{n}"
            if t["has_delay_data"] and dcol in df.columns:
                ping[name] = df[dcol].where(df[dcol] > 0)  # drop invalid/zero delays
            if t["has_loss_data"] and lcol in df.columns:
                loss[name] = df[lcol]

        st.markdown("**📈 Ping Response Times (ms)**")
        if len(ping.columns) > 1:
            st.plotly_chart(line_figure(ping, "Response Time (ms)"), width="stretch")
        else:
            st.info("No delay data for selected date.")

        st.markdown("**📉 Packet Loss (%)**")
        if len(loss.columns) > 1:
            st.plotly_chart(line_figure(loss, "Packet Loss (%)"), width="stretch")
        else:
            st.info("No loss data for selected date.")
