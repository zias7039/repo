# ui/chart.py
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

def render_chart(history_df, current_equity):
    """
    Daily History Chart
    """
    # 카드 높이를 좌측 패널과 맞추기 위해 스타일 조정 (overflow hidden)
    st.markdown('<div class="dashboard-card" style="padding:15px; height:100%; min-height:420px; overflow:hidden;">', unsafe_allow_html=True)

    if history_df is None or history_df.empty:
        df = pd.DataFrame({'date': [pd.Timestamp.now().strftime('%Y-%m-%d')], 'equity': [current_equity]})
    else:
        df = history_df.copy()
        last_date = str(df['date'].iloc[-1])
        today_str = pd.Timestamp.now().strftime('%Y-%m-%d')
        if last_date != today_str:
            new_row = pd.DataFrame({'date': [today_str], 'equity': [current_equity]})
            df = pd.concat([df, new_row], ignore_index=True)

    # Date Parsing (문자열 -> datetime)
    df['date'] = pd.to_datetime(df['date'])

    start_val = df['equity'].iloc[0]
    end_val = df['equity'].iloc[-1]
    is_profit = end_val >= start_val
    
    color_line = "#3dd995" if is_profit else "#ff4d4d"
    # 그라데이션 느낌을 위해 투명도 조절
    color_fill = "rgba(61, 217, 149, 0.15)" if is_profit else "rgba(255, 77, 77, 0.15)"
    
    pnl_diff = end_val - start_val
    pnl_sign = "+" if pnl_diff >= 0 else ""

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['equity'],
        mode='lines',  # 점(markers) 제거하여 더 깔끔하게
        line=dict(color=color_line, width=3), # 라인 두께 증가
        fill='tozeroy',
        fillcolor=color_fill,
        hoverinfo='y+x'
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        height=350, # 차트 영역 높이 설정
        xaxis=dict(
            showgrid=False, 
            showticklabels=True,
            tickformat="%m-%d",  # 날짜 포맷 단축 (월-일)
            nticks=6,            # 라벨 개수 제한
            tickfont=dict(size=10, color="#666")
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor="#1a1a1a", 
            showticklabels=False
        ),
        hovermode="x unified"
    )

    # 상단 헤더
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; margin-bottom:15px; align-items:center;">
        <div style="display:flex; gap:8px;">
            <span style="background:#222; padding:4px 10px; border-radius:4px; font-size:0.75rem; color:#fff; font-weight:600;">History</span>
        </div>
        <div style="text-align:right;">
            <div class="label" style="margin-bottom:0;">PnL (Recorded)</div>
            <div style="color:{color_line}; font-family:var(--font-mono); font-weight:700; font-size:1.1rem;">{pnl_sign}${pnl_diff:,.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
