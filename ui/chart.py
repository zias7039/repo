# ui/chart.py
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from utils.format import render_html

def render_chart(history_df, current_equity):
    # 1. 데이터 준비
    if history_df is None or history_df.empty:
        df = pd.DataFrame({'date': [pd.Timestamp.now().strftime('%Y-%m-%d')], 'equity': [current_equity]})
    else:
        df = history_df.copy()
        last_date = str(df['date'].iloc[-1])
        today_str = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        # 오늘 날짜 데이터가 없으면 현재 equity로 임시 추가 (차트 표시용)
        if last_date != today_str:
            new_row = pd.DataFrame({'date': [today_str], 'equity': [current_equity]})
            df = pd.concat([df, new_row], ignore_index=True)
            
    df['date'] = pd.to_datetime(df['date'])

    # 2. PnL 계산 및 Y축 범위 설정 (핵심 수정)
    start_val = df['equity'].iloc[0]
    end_val = df['equity'].iloc[-1]
    is_profit = end_val >= start_val
    
    # [수정] 차트가 위로 붙지 않도록 데이터의 최소/최대값 기준으로 여유 공간 계산
    min_y = df['equity'].min()
    max_y = df['equity'].max()
    padding = (max_y - min_y) * 0.1 # 위아래 10% 여유
    if padding == 0: padding = max_y * 0.01 # 데이터가 1개일 경우 예외처리
    
    y_range = [min_y - padding, max_y + padding]
    
    color_line = "#3dd995" if is_profit else "#ff4d4d"
    # 그라데이션 효과를 흉내내기 위한 채우기 (투명도 조절)
    color_fill = "rgba(61, 217, 149, 0.1)" if is_profit else "rgba(255, 77, 77, 0.1)"
    
    pnl_diff = end_val - start_val
    pnl_sign = "+" if pnl_diff >= 0 else ""

    # 3. Header HTML (오른쪽 여백 확보 및 폰트 조정)
    header_html = f"""
    <div class="dashboard-card" style="border-bottom:none; border-bottom-left-radius:0; border-bottom-right-radius:0; padding:20px 24px 0 24px; background:var(--bg-card);">
        <div class="flex-between" style="align-items: flex-start;">
            <div style="display:flex; gap:8px; align-items:center;">
                <span style="font-size:0.95rem; font-weight:600; color:#f5f5f5;">PnL History</span>
                <span style="background:#262626; color:#737373; padding:2px 8px; border-radius:12px; font-size:0.7rem; font-weight:600;">30D</span>
            </div>
            <div style="text-align:right; min-width: 120px;"> <div style="font-size:0.75rem; color:#737373; margin-bottom:2px; font-weight:500;">Recorded PnL</div>
                <div class="text-mono" style="color:{color_line}; font-weight:700; font-size:1.1rem; letter-spacing:-0.5px;">
                    {pnl_sign}${pnl_diff:,.2f}
                </div>
            </div>
        </div>
    </div>
    """
    render_html(st, header_html)

    # 4. Plotly Chart 설정
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['equity'],
        mode='lines', 
        line=dict(color=color_line, width=2),
        fill='tozeroy', 
        fillcolor=color_fill,
        hoverinfo='y+x',
        hovertemplate='%{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='#141414',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=20), # 상하 여백 조정
        height=320,
        xaxis=dict(
            showgrid=False, 
            showline=False,
            showticklabels=True,
            tickformat="%-m-%d",
            tickfont=dict(size=11, color="#525252", family="JetBrains Mono"),
            ticks="",
            nticks=5,
            fixedrange=True # 줌 방지
        ),
        yaxis=dict(
            showgrid=False, 
            showline=False,
            showticklabels=False,
            zeroline=False,
            range=y_range, # [핵심] 계산된 범위 강제 적용
            fixedrange=True
        ),
        hovermode="x unified",
        showlegend=False
    )

    # 툴팁 스타일
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="#1f1f1f",
            bordercolor="#333",
            font=dict(color="#fff", family="JetBrains Mono")
        )
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': False})
    
    # 5. 하단 테두리 마감
    st.markdown("""
        <div class="dashboard-card" style="border-top:none; border-top-left-radius:0; border-top-right-radius:0; height:1px; margin-top:-6px;"></div>
    """, unsafe_allow_html=True)
