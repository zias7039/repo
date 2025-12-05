# ui/chart.py
import plotly.graph_objects as go
import streamlit as st

def render_chart(df, title):
    if df is None or df.empty:
        st.warning(f"⚠️ {title} 차트 데이터를 불러올 수 없습니다.")
        return

    # 스타일 유지 (스크롤바 숨김)
    st.markdown("""
        <style>
        div[data-testid="stPlotlyChart"] { overflow: hidden !important; }
        div[data-testid="stPlotlyChart"] > div { overflow: hidden !important; }
        </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # [수정됨] MA(단순) -> EMA(지수)로 변경
    # span=N : N일 지수이동평균에 해당하는 감쇠 계수 사용
    # ---------------------------------------------------------
    df["EMA5"] = df["close"].ewm(span=5, adjust=False).mean()
    df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["EMA40"] = df["close"].ewm(span=40, adjust=False).mean()

    # 캔들스틱 차트 생성
    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"],
        open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color="#2ebd85", decreasing_line_color="#f6465d", name="Price"
    )])

    # [수정됨] EMA 선 그리기 (변수명 및 라벨 변경)
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["EMA5"], line=dict(color='#fcd535', width=1), name='EMA 5'))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["EMA20"], line=dict(color='#3b82f6', width=1), name='EMA 20'))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["EMA40"], line=dict(color='#8b5cf6', width=1), name='EMA 40'))

    # 레이아웃 유지 (여백 최소화 등)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=50, t=5, b=0), 
        height=400,
        title=dict(text="", font=dict(size=1), x=0, y=0),
        xaxis=dict(rangeslider_visible=False, showgrid=True, gridcolor="#2b313a"),
        yaxis=dict(side="right", showgrid=True, gridcolor="#2b313a", tickformat=",.1f"),
        hovermode='x unified',
        legend=dict(x=0, y=1, orientation="h", bgcolor='rgba(0,0,0,0)')
    )
    
    st.plotly_chart(fig, use_container_width=True, config={
        "displayModeBar": True, "modeBarButtonsToRemove": ['select2d', 'lasso2d'], "displaylogo": False
    })
