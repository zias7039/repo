# ui/chart.py
import plotly.graph_objects as go
import streamlit as st

def render_chart(df, title):
    st.markdown(f'<div class="dashboard-card" style="height:420px; padding:10px;">', unsafe_allow_html=True)
    
    if df is None or df.empty:
        st.write("No Data")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # EMA
    df["EMA20"] = df["close"].ewm(span=20).mean()

    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"],
        open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color="#3dd995", decreasing_line_color="#ff4d4d",
        name="Price"
    )])
    
    # EMA 라인 (은은하게)
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["EMA20"], line=dict(color='#3b82f6', width=1.5), name='EMA20'))

    # 스타일: 극도로 미니멀하게 (이미지 참조)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=50, t=30, b=0),
        height=400,
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False), # 세로 그리드 제거
        yaxis=dict(
            side="right", showgrid=True, gridcolor="#1a1a1a", zeroline=False,
            tickfont=dict(color="#666", family="JetBrains Mono")
        ),
        hovermode='x unified'
    )
    
    # 툴바 커스텀
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
