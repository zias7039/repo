# ui/chart.py
import plotly.graph_objects as go
import streamlit as st

def render_chart(df, title):
    # 차트 영역 카드
    st.markdown(f'<div class="dashboard-card" style="height:420px; padding:10px;">', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.markdown('<div style="color:#555; text-align:center; padding-top:180px;">No Data</div></div>', unsafe_allow_html=True)
        return

    # EMA 계산
    df["EMA"] = df["close"].ewm(span=20).mean()

    # 차트 생성 (캔들스틱이지만 깔끔하게)
    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"],
        open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color="#3dd995", decreasing_line_color="#ff4d4d",
        name="Price"
    )])
    
    # EMA 라인 추가
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["EMA"], line=dict(color='#3b82f6', width=1.5), name='EMA', opacity=0.7))

    # 레이아웃: 이미지처럼 미니멀하게
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=50, t=20, b=0),
        height=400,
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=True),
        yaxis=dict(
            side="right", showgrid=True, gridcolor="#1a1a1a", zeroline=False,
            tickfont=dict(color="#666", family="JetBrains Mono", size=10)
        ),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
