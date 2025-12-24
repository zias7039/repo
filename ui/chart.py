# ui/chart.py
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

def render_chart(history_df, current_equity):
    """
    Daily History Chart
    일별 자산 기록(history.csv)을 시각화합니다.
    """
    st.markdown('<div class="dashboard-card" style="padding:10px; overflow:hidden;">', unsafe_allow_html=True)

    # 1. 데이터 준비: 실제 기록 데이터만 사용
    if history_df is None or history_df.empty:
        # 데이터가 아예 없을 경우 현재 자산으로 점 하나만 찍음
        df = pd.DataFrame({'date': [pd.Timestamp.now().strftime('%Y-%m-%d')], 'equity': [current_equity]})
    else:
        df = history_df.copy()
        # 오늘 자산이 기록되지 않았다면 차트 꼬리에 현재가 추가 (실시간성 반영)
        last_date = str(df['date'].iloc[-1])
        today_str = pd.Timestamp.now().strftime('%Y-%m-%d')
        if last_date != today_str:
            new_row = pd.DataFrame({'date': [today_str], 'equity': [current_equity]})
            df = pd.concat([df, new_row], ignore_index=True)

    # 2. 색상 및 수익률 계산
    start_val = df['equity'].iloc[0]
    end_val = df['equity'].iloc[-1]
    is_profit = end_val >= start_val
    
    color_line = "#3dd995" if is_profit else "#ff4d4d"
    color_fill = "rgba(61, 217, 149, 0.1)" if is_profit else "rgba(255, 77, 77, 0.1)"
    
    pnl_diff = end_val - start_val
    pnl_sign = "+" if pnl_diff >= 0 else ""

    # 3. 차트 그리기
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['equity'],
        mode='lines+markers', # 데이터가 적을 수 있으므로 마커 표시
        marker=dict(size=6, color=color_line),
        line=dict(color=color_line, width=2),
        fill='tozeroy',
        fillcolor=color_fill,
        hoverinfo='y+x'
    ))

    # 4. 레이아웃
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        height=450,
        xaxis=dict(
            showgrid=False, 
            showticklabels=True, 
            type='category' # 날짜가 띄엄띄엄 있을 수 있으므로 카테고리형 추천
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor="#1a1a1a", 
            showticklabels=False # 값은 숨기고 추세만 확인
        ),
        hovermode="x unified"
    )

    # 상단 헤더 (Total PnL 표시)
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; padding:0 10px; margin-bottom:10px;">
        <div style="display:flex; gap:10px;">
            <span style="background:#161616; padding:4px 12px; border-radius:4px; font-size:0.8rem; color:#fff;">History</span>
        </div>
        <div style="text-align:right;">
            <div class="label">Total PnL (Recorded)</div>
            <div style="color:{color_line}; font-family:var(--font-mono); font-weight:600;">{pnl_sign}${pnl_diff:,.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
