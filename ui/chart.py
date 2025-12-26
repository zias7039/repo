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
        
        if last_date != today_str:
            new_row = pd.DataFrame({'date': [today_str], 'equity': [current_equity]})
            df = pd.concat([df, new_row], ignore_index=True)
            
    df['date'] = pd.to_datetime(df['date'])

    # 2. PnL 및 Y축 범위 계산
    start_val = df['equity'].iloc[0]
    end_val = df['equity'].iloc[-1]
    is_profit = end_val >= start_val
    
    min_y = df['equity'].min()
    max_y = df['equity'].max()
    
    # 위아래 여백 15%
    padding = (max_y - min_y) * 0.15
    if padding == 0: padding = max_y * 0.05
    y_range = [min_y - padding, max_y + padding]
    
    color_line = "#3dd995" if is_profit else "#ff4d4d"
    color_fill = "rgba(61, 217, 149, 0.1)" if is_profit else "rgba(255, 77, 77, 0.1)"
    
    pnl_diff = end_val - start_val
    pnl_sign = "+" if pnl_diff >= 0 else ""

    # 3. Header HTML (Grid Layout 적용 + 강제 여백)
    # [해결책] display: grid를 사용하여 좌우 공간을 물리적으로 분할
    # margin-right: 4px를 추가하여 텍스트가 카드 끝에 닿지 않도록 강제함
    header_html = f"""
    <div class="dashboard-card" style="
        border-bottom:none; 
        border-bottom-left-radius:0; 
        border-bottom-right-radius:0; 
        padding: 20px 24px 0 24px; 
        background: var(--bg-card); 
        width: 100%; 
        box-sizing: border-box;
    ">
        <div style="
            display: grid; 
            grid-template-columns: 1fr auto; 
            width: 100%; 
            align-items: start;
        ">
            <div style="display:flex; gap:8px; align-items:center;">
                <span style="font-size:0.95rem; font-weight:600; color:#f5f5f5;">PnL History</span>
                <span style="background:#262626; color:#737373; padding:2px 8px; border-radius:12px; font-size:0.7rem; font-weight:600;">30D</span>
            </div>
            
            <div style="text-align:right; margin-right: 4px;">
                <div style="font-size:0.75rem; color:#737373; margin-bottom:2px; font-weight:500;">Recorded PnL</div>
                <div class="text-mono" style="color:{color_line}; font-weight:700; font-size:1.1rem; letter-spacing:-0.5px;">
                    {pnl_sign}${pnl_diff:,.2f}
                </div>
            </div>
        </div>
    </div>
    """
    render_html(st, header_html)

    # 4. Plotly Chart 설정 (부드러운 곡선)
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['equity'],
        mode='lines', 
        line=dict(color=color_line, width=2, shape='spline', smoothing=1.3),
        fill='tozeroy', 
        fillcolor=color_fill,
        hoverinfo='y+x',
        hovertemplate='%{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='#141414',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=20),
        height=320,
        xaxis=dict(
            showgrid=False, 
            showline=False,
            showticklabels=True,
            tickformat="%-m-%d",
            tickfont=dict(size=11, color="#525252", family="JetBrains Mono"),
            ticks="",
            nticks=5,
            fixedrange=True
        ),
        yaxis=dict(
            showgrid=False, 
            showline=False,
            showticklabels=False,
            zeroline=False,
            range=y_range,
            fixedrange=True
        ),
        hovermode="x unified",
        showlegend=False
    )

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
