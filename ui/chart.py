# ui/chart.py
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from utils.format import render_html

def render_chart(history_df, current_equity):
    """
    Daily History Chart
    """
    # 1. 데이터 준비
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

    # 2. 색상 및 PnL 계산
    start_val = df['equity'].iloc[0]
    end_val = df['equity'].iloc[-1]
    is_profit = end_val >= start_val
    
    color_line = "#3dd995" if is_profit else "#ff4d4d"
    color_fill = "rgba(61, 217, 149, 0.15)" if is_profit else "rgba(255, 77, 77, 0.15)"
    
    pnl_diff = end_val - start_val
    pnl_sign = "+" if pnl_diff >= 0 else ""

    # 3. HTML 헤더 렌더링 (카드 상단부 역할)
    # 래퍼 div를 제거하고, 헤더 자체를 카드의 윗부분처럼 스타일링합니다.
    header_html = f"""
    <div style="
        background-color: #131313; 
        border: 1px solid #222; 
        border-bottom: none; 
        border-radius: 6px 6px 0 0; 
        padding: 16px 20px 0 20px;
    ">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="display:flex; gap:8px;">
                <span style="background:#222; padding:4px 10px; border-radius:4px; font-size:0.75rem; color:#fff; font-weight:600;">History</span>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.8rem; color:#888; margin-bottom:0;">PnL (Recorded)</div>
                <div style="color:{color_line}; font-family:'JetBrains Mono', monospace; font-weight:700; font-size:1.1rem;">
                    {pnl_sign}${pnl_diff:,.2f}
                </div>
            </div>
        </div>
    </div>
    """
    render_html(st, header_html)

    # 4. 차트 생성
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['equity'],
        mode='lines',
        line=dict(color=color_line, width=3),
        fill='tozeroy',
        fillcolor=color_fill,
        hoverinfo='y+x'
    ))

    # 5. 레이아웃 설정 (카드 하단부 역할)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='#131313', # 카드 배경색과 일치시킴
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10), # 여백 최소화
        height=380, # 높이 고정
        xaxis=dict(
            showgrid=False, 
            showticklabels=True,
            tickformat="%m-%d",
            nticks=5,
            tickfont=dict(size=11, color="#666")
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor="#1a1a1a", 
            showticklabels=False
        ),
        hovermode="x unified"
    )

    # 6. 차트 렌더링 (Streamlit 컨테이너 사용 X)
    # 차트 바로 아래에 border-bottom을 그려주기 위해 차트 자체는 테두리 없이 렌더링하고
    # CSS나 추가 HTML로 마감하지 않고, 배경색 일치로 시각적 통합을 유도합니다.
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # 카드 하단 마감선 (선택 사항, 깔끔한 마무리를 위함)
    st.markdown("""
        <div style="height:1px; background-color:#131313; border-top:1px solid #131313; border-radius:0 0 6px 6px; margin-top:-5px;"></div>
    """, unsafe_allow_html=True)
