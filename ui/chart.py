# ui/chart.py
import plotly.graph_objects as go
import streamlit as st

def render_chart(df, title):
    if df is None or df.empty:
        st.warning("차트를 불러올 수 없습니다.")
        return
    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color="#22c55e", decreasing_line_color="#ef4444",
    )])
    fig.update_layout(title=title, height=320, margin=dict(l=0,r=0,t=30,b=0),
                      template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
