# ui/chart.py
import plotly.graph_objects as go
import streamlit as st

def render_chart(df, title):
    if df is None or df.empty:
        st.warning("차트를 불러올 수 없습니다.")
        return

    # ✅ 차트 제목은 Streamlit에서 출력 (Plotly title 아님)
    st.markdown(f"<p class='chart-title'>{title}</p>", unsafe_allow_html=True)

    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing_line_color="#22c55e",
        decreasing_line_color="#ef4444",
    )])

    # ✅ Plotly 내부 제목과 여백 최소화
    fig.update_layout(
        title=None,
        height=320,
        margin=dict(l=0, r=0, t=12, b=0),
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
    )

    # ✅ 차트 렌더
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
