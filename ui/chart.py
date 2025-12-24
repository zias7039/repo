# ui/chart.py
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from utils.format import render_html

def render_chart(history_df, current_equity):
    # 1. Data Preparation
    if history_df is None or history_df.empty:
        df = pd.DataFrame({'date': [pd.Timestamp.now().strftime('%Y-%m-%d')], 'equity': [current_equity]})
    else:
        df = history_df.copy()
        last_date = str(df['date'].iloc[-1])
        today_str = pd.Timestamp.now().strftime('%Y-%m-%d')
        if last_date != today_str:
            new_row = pd.DataFrame({'date': [today_str], 'equity': [current_equity]})
            df = pd.concat([df, new_row], ignore_index=True)
    df['date'] = pd.to_datetime(df['date'])

    # 2. Color & PnL Logic
    start_val = df['equity'].iloc[0]
    end_val = df['equity'].iloc[-1]
    is_profit = end_val >= start_val
    
    color_line = "#3dd995" if is_profit else "#ff4d4d"
    color_fill = "rgba(61, 217, 149, 0.1)" if is_profit else "rgba(255, 77, 77, 0.1)"
    pnl_diff = end_val - start_val
    pnl_sign = "+" if pnl_diff >= 0 else ""

    # 3. Header HTML (Seamless integration)
    # 하단 보더를 제거하고 배경색을 카드와 통일
    header_html = f"""
    <div class="dashboard-card" style="border-bottom:none; border-bottom-left-radius:0; border-bottom-right-radius:0; padding:16px 20px 0 20px;">
        <div class="flex-between">
            <div style="display:flex; gap:8px; align-items:center;">
                <span class="label" style="font-weight:600; color:var(--text-primary);">PNL HISTORY</span>
                <span class="badge badge-neutral">30D</span>
            </div>
            <div style="text-align:right;">
                <div class="label">RECORDED PNL</div>
                <div class="text-mono" style="color:{color_line}; font-weight:700; font-size:1.1rem;">
                    {pnl_sign}${pnl_diff:,.2f}
                </div>
            </div>
        </div>
    </div>
    """
    render_html(st, header_html)

    # 4. Plotly Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['equity'],
        mode='lines', line=dict(color=color_line, width=2),
        fill='tozeroy', fillcolor=color_fill,
        hoverinfo='y+x'
    ))

    # 레이아웃: 마진을 완전히 제거하여 헤더와 밀착
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='#111111', # var(--bg-card)와 동일
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        height=345, # 좌측 패널 높이(400px) - 헤더 높이 고려
        xaxis=dict(
            showgrid=False, showticklabels=True,
            tickformat="%m-%d", nticks=5,
            tickfont=dict(size=10, color="#555", family="JetBrains Mono")
        ),
        yaxis=dict(showgrid=False, showticklabels=False), # Y축 완전히 숨김
        hovermode="x unified"
    )

    # 차트 렌더링 (컨테이너 없이)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # 마감선 (선택적)
    st.markdown('<div style="height:1px; background:#1f1f1f; margin-top:-1px;"></div>', unsafe_allow_html=True)
