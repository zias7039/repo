# ui/chart.py
import plotly.graph_objects as go
import streamlit as st

def render_chart(df, title):
    # 차트 영역을 카드 안에 넣기 위해 시작 div
    st.markdown('<div class="dashboard-card" style="padding:10px; height:450px;">', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.markdown('<div style="text-align:center; padding-top:180px; color:#555;">No Data Available</div></div>', unsafe_allow_html=True)
        return

    # EMA 계산
    df["EMA7"] = df["close"].ewm(span=7, adjust=False).mean()
    df["EMA25"] = df["close"].ewm(span=25, adjust=False).mean()
    df["EMA99"] = df["close"].ewm(span=99, adjust=False).mean()

    # 캔들스틱
    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"],
        open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color="#2ebd85", decreasing_line_color="#f6465d",
        name="Price"
    )])

    # EMA 라인 (얇게)
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["EMA7"], line=dict(color='#fcd535', width=1), name='EMA 7'))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["EMA25"], line=dict(color='#3b82f6', width=1), name='EMA 25'))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["EMA99"], line=dict(color='#8b5cf6', width=1), name='EMA 99'))

    # 레이아웃: 배경 투명, 그리드 최소화
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=60, t=10, b=0),
        height=420,
        showlegend=False,
        xaxis=dict(
            rangeslider_visible=False, 
            showgrid=True, 
            gridcolor="#2b313a", 
            gridwidth=1
        ),
        yaxis=dict(
            side="right", 
            showgrid=True, 
            gridcolor="#2b313a", 
            gridwidth=1,
            tickfont=dict(family='JetBrains Mono', size=11, color='#848e9c')
        ),
        hovermode='x unified'
    )
    
    # 툴바 제거 및 로고 숨김
    st.plotly_chart(fig, use_container_width=True, config={
        "displayModeBar": True, 
        "modeBarButtonsToRemove": ['select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d'], 
        "displaylogo": False
    })
    
    st.markdown('</div>', unsafe_allow_html=True)
