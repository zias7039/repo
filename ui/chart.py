# ui/chart.py
import plotly.graph_objects as go
import streamlit as st

def render_chart(df, title):
    # 차트 데이터 없음 처리
    if df is None or df.empty:
        st.warning(f"⚠️ {title} 차트 데이터를 불러올 수 없습니다.")
        return

    # [수정됨] 스크롤바 숨김 CSS (전역 적용)
    st.markdown("""
        <style>
        div[data-testid="stPlotlyChart"] { overflow: hidden !important; }
        div[data-testid="stPlotlyChart"] > div { overflow: hidden !important; }
        </style>
    """, unsafe_allow_html=True)

    # 보조지표(MA) 계산
    df["MA7"] = df["close"].rolling(window=7).mean()
    df["MA25"] = df["close"].rolling(window=25).mean()
    df["MA99"] = df["close"].rolling(window=99).mean()

    # 캔들스틱 차트 생성
    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"],
        open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color="#2ebd85", decreasing_line_color="#f6465d", name="Price"
    )])

    # MA 선 추가
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["MA7"], line=dict(color='#fcd535', width=1), name='MA 7'))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["MA25"], line=dict(color='#3b82f6', width=1), name='MA 25'))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["MA99"], line=dict(color='#8b5cf6', width=1), name='MA 99'))

    # 레이아웃
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=50, t=30, b=0), height=400,
        title=dict(text=title, font=dict(size=14, color="#848e9c"), x=0.02, y=0.95),
        xaxis=dict(rangeslider_visible=False, showgrid=True, gridcolor="#2b313a"),
        yaxis=dict(side="right", showgrid=True, gridcolor="#2b313a", tickformat=",.1f"),
        hovermode='x unified',
        legend=dict(x=0, y=1, orientation="h", bgcolor='rgba(0,0,0,0)')
    )
    
    st.plotly_chart(fig, use_container_width=True, config={
        "displayModeBar": True, "modeBarButtonsToRemove": ['select2d', 'lasso2d'], "displaylogo": False
    })
