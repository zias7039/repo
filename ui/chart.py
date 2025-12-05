# ui/chart.py
import plotly.graph_objects as go
import streamlit as st

def render_chart(df, title):
    if df is None or df.empty:
        st.warning("차트 데이터가 없습니다.")
        return

    # 캔들스틱 차트 생성
    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing_line_color="#2ebd85", # 테마 Green
        decreasing_line_color="#f6465d", # 테마 Red
        name=title
    )])

    # 레이아웃 스타일링 (Dark Theme 최적화)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', # 투명 배경
        plot_bgcolor='rgba(0,0,0,0)',  # 투명 배경
        margin=dict(l=0, r=40, t=30, b=0),
        height=380,
        title=dict(
            text=title, 
            font=dict(size=14, color="#848e9c"),
            x=0.02, y=0.95
        ),
        xaxis=dict(
            rangeslider_visible=False,
            showgrid=True,
            gridcolor="#2b313a", # 은은한 그리드
            zeroline=False,
            showticklabels=True,
        ),
        yaxis=dict(
            side="right", # 가격축을 오른쪽으로 (TradingView 스타일)
            showgrid=True,
            gridcolor="#2b313a",
            zeroline=False,
            tickformat=",.1f"
        ),
        hovermode='x unified',
    )
    
    # 모드바(줌, 이동 버튼 등) 최소화
    st.plotly_chart(fig, use_container_width=True, config={
        "displayModeBar": True, 
        "modeBarButtonsToRemove": ['select2d', 'lasso2d'],
        "displaylogo": False
    })
