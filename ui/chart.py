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

    # 2. PnL 계산 및 색상 결정
    start_val = df['equity'].iloc[0]
    end_val = df['equity'].iloc[-1]
    is_profit = end_val >= start_val
    
    # 이미지와 유사한 Green / Red 색상
    color_line = "#3dd995" if is_profit else "#ff4d4d"
    # 하단 채우기는 매우 투명하게 처리
    color_fill = "rgba(61, 217, 149, 0.05)" if is_profit else "rgba(255, 77, 77, 0.05)"
    
    pnl_diff = end_val - start_val
    pnl_sign = "+" if pnl_diff >= 0 else ""

    # 3. Header HTML (이미지 디자인 적용)
    # - 좌측: 타이틀 + 30D 뱃지
    # - 우측: Recorded PnL 라벨 + 값
    header_html = f"""
    <div class="dashboard-card" style="border-bottom:none; border-bottom-left-radius:0; border-bottom-right-radius:0; padding:20px 24px 0 24px; background:var(--bg-card);">
        <div class="flex-between" style="align-items: flex-start;">
            <div style="display:flex; gap:8px; align-items:center;">
                <span style="font-size:0.95rem; font-weight:600; color:#f5f5f5;">PnL History</span>
                <span style="background:#262626; color:#737373; padding:2px 8px; border-radius:12px; font-size:0.7rem; font-weight:600;">30D</span>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem; color:#525252; margin-bottom:2px; font-weight:500;">Recorded PnL</div>
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
        hovertemplate='%{y:,.2f}<extra></extra>' # 깔끔한 툴팁
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='#141414', # var(--bg-card)와 일치
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=15, b=20), # 여백 최소화
        height=320, 
        xaxis=dict(
            showgrid=False, 
            showline=False,       # X축 선 제거
            showticklabels=True,  # 날짜는 표시
            tickformat="%-m-%d",  # 예: 12-07
            tickfont=dict(size=11, color="#404040", family="JetBrains Mono"), # 날짜 색상을 매우 어둡게(이미지처럼)
            ticks="",             # 눈금 제거
            nticks=5
        ),
        yaxis=dict(
            showgrid=False, 
            showline=False,
            showticklabels=False, # Y축 값 숨김 (이미지 스타일)
            zeroline=False
        ),
        hovermode="x unified",
        showlegend=False
    )

    # 마우스 오버 시 수직선 스타일 (점선, 어두운 색)
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="#1f1f1f",
            bordercolor="#333",
            font=dict(color="#fff", family="JetBrains Mono")
        )
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': False})
    
    # 5. 카드 하단 마감 (테두리 연결)
    st.markdown("""
        <div class="dashboard-card" style="border-top:none; border-top-left-radius:0; border-top-right-radius:0; height:1px; margin-top:-6px;"></div>
    """, unsafe_allow_html=True)
