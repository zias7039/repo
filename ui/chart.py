# ui/chart.py
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np

def render_chart(history_df, current_equity):
    """
    PnL History Area Chart (Filled)
    이미지와 같은 영역 그래프 렌더링
    """
    # 1. 데이터 준비 (데이터가 없으면 시각적 예시를 위해 더미 데이터 생성 가능)
    if history_df is None or history_df.empty:
        # PnL 차트 느낌을 내기 위해 최근 24시간 더미 데이터 생성 (시각화용)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=24, freq='H')
        base = current_equity if current_equity > 0 else 1000
        values = [base + (base * 0.02 * np.sin(i)) for i in range(24)]
        df = pd.DataFrame({'date': dates, 'equity': values})
    else:
        df = history_df.copy()
        df['date'] = pd.to_datetime(df['date'])

    # 2. 색상 결정 (시작점 대비 상승/하락)
    start_val = df['equity'].iloc[0]
    end_val = df['equity'].iloc[-1]
    is_profit = end_val >= start_val
    
    color_line = "#3dd995" if is_profit else "#ff4d4d"
    color_fill = "rgba(61, 217, 149, 0.1)" if is_profit else "rgba(255, 77, 77, 0.1)" # 투명도 적용

    # 3. 차트 그리기 (Scatter + Fill)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['equity'],
        mode='lines',
        fill='tozeroy',  # 영역 채우기
        line=dict(color=color_line, width=2),
        fillcolor=color_fill,
        hoverinfo='y+x'
    ))

    # 4. 레이아웃: 그리드 제거, 심플하게
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=0),
        height=450, # 카드 높이에 맞춤
        xaxis=dict(showgrid=False, showticklabels=True, tickformat="%H:%M"),
        yaxis=dict(showgrid=True, gridcolor="#1a1a1a", showticklabels=False), # 세로축 값 숨김(이미지 스타일)
        hovermode="x unified"
    )

    # 5. 렌더링 (카드 안에 가둠)
    st.markdown('<div class="dashboard-card" style="padding:10px; overflow:hidden;">', unsafe_allow_html=True)
    
    # 차트 헤더 (24H PnL 등)
    pnl_diff = end_val - start_val
    pnl_sign = "+" if pnl_diff >= 0 else ""
    
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; padding:0 10px; margin-bottom:10px;">
        <div style="display:flex; gap:10px;">
            <span style="background:#161616; padding:4px 12px; border-radius:4px; font-size:0.8rem; color:#fff; cursor:pointer;">24H</span>
            <span style="padding:4px 12px; font-size:0.8rem; color:#666; cursor:pointer;">1W</span>
            <span style="padding:4px 12px; font-size:0.8rem; color:#666; cursor:pointer;">1M</span>
        </div>
        <div style="text-align:right;">
            <div class="label">24H PnL</div>
            <div style="color:{color_line}; font-family:var(--font-mono); font-weight:600;">{pnl_sign}${pnl_diff:,.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
