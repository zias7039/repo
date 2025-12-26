# ui/chart.py
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from datetime import timedelta
from utils.format import render_html

def render_chart(history_df, current_equity, usdt_rate=None):
    # ---------------------------
    # 1. 데이터 준비 및 기간 필터링
    # ---------------------------
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
    
    # [기간 필터 UI] - 차트 상단에 배치
    # Streamlit 1.40+ 에서는 st.pills 사용 가능, 하위 버전은 st.radio로 대체
    c_filter, c_empty = st.columns([0.4, 0.6])
    with c_filter:
        timeframe = st.radio(
            "Select Timeframe",
            ["1W", "1M", "All"],
            index=0,
            horizontal=True,
            label_visibility="collapsed",
            key="chart_tf"
        )

    # [필터 로직]
    cutoff_date = df['date'].min()
    if timeframe == "1W":
        cutoff_date = pd.Timestamp.now() - timedelta(weeks=1)
    elif timeframe == "1M":
        cutoff_date = pd.Timestamp.now() - timedelta(days=30)
    
    filtered_df = df[df['date'] >= cutoff_date]
    if filtered_df.empty:
        filtered_df = df.tail(1) # 데이터가 없으면 마지막 점이라도 표시

    # ---------------------------
    # 2. PnL 계산 (필터링된 기간 기준)
    # ---------------------------
    start_val = filtered_df['equity'].iloc[0]
    end_val = filtered_df['equity'].iloc[-1]
    pnl_diff = end_val - start_val
    pnl_sign = "+" if pnl_diff >= 0 else ""
    
    # 색상 테마 (이미지와 유사한 Teal/Mint 컬러)
    main_color = "#2EBD85" if pnl_diff >= 0 else "#F6465D" # 양수면 민트, 음수면 레드
    fill_color = "rgba(46, 189, 133, 0.15)" if pnl_diff >= 0 else "rgba(246, 70, 93, 0.15)"
    
    # KRW 변환
    krw_pnl_html = ""
    if usdt_rate:
        val_krw = abs(pnl_diff * usdt_rate)
        sign_krw = "+" if pnl_diff >= 0 else "-"
        krw_pnl_html = f"<span style='font-size:0.8rem; color:#848E9C; font-weight:400;'> (≈{sign_krw}₩{val_krw:,.0f})</span>"

    # ---------------------------
    # 3. Header HTML (오른쪽 상단 배치 스타일)
    # ---------------------------
    header_html = f"""
    <div style="
        position: relative;
        text-align: right;
        margin-bottom: -40px; 
        z-index: 10;
        padding-right: 10px;
        pointer-events: none; /* 차트 인터랙션 방해 금지 */
    ">
        <div style="font-size:0.8rem; color:#848E9C; font-weight:500; margin-bottom:4px;">
            {timeframe} PnL (Combined)
        </div>
        <div class="text-mono" style="
            color: {main_color}; 
            font-weight: 600; 
            font-size: 1.5rem; 
            letter-spacing: -0.5px;
            text-shadow: 0px 0px 10px {fill_color};
        ">
            {pnl_sign}${pnl_diff:,.2f}{krw_pnl_html}
        </div>
    </div>
    """
    render_html(st, header_html)

    # ---------------------------
    # 4. Plotly Chart 설정 (이미지 스타일 적용)
    # ---------------------------
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=filtered_df['date'], 
        y=filtered_df['equity'],
        mode='lines+markers', # 선과 마커(점) 모두 표시
        line=dict(
            color=main_color, 
            width=2, 
            shape='spline', # 부드러운 곡선
            smoothing=1.0
        ),
        marker=dict(
            size=4,
            color=main_color,
            symbol='circle'
        ),
        fill='tozeroy', 
        fillcolor=fill_color,
        hoverinfo='y+x',
        hovertemplate='<span style="color:#000">Date: %{x|%m-%d}<br>Equity: $%{y:,.2f}</span><extra></extra>'
    ))

    # Y축 범위 계산 (여백 추가)
    min_y = filtered_df['equity'].min()
    max_y = filtered_df['equity'].max()
    padding = (max_y - min_y) * 0.2 if max_y != min_y else max_y * 0.05
    y_range = [min_y - padding, max_y + padding]

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', # 배경 투명
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=20, t=50, b=30), # Header 공간(t=50) 확보
        height=350,
        xaxis=dict(
            showgrid=False, # X축 격자 숨김
            showline=False,
            showticklabels=True,
            tickformat="%-d %b", # 예: 21 Dec
            tickfont=dict(size=11, color="#848E9C", family="Inter"),
            fixedrange=True
        ),
        yaxis=dict(
            showgrid=True,       # Y축 격자 표시
            gridcolor='#2B3139', # 아주 어두운 회색 (Dotted Line 효과용)
            griddash='dot',      # 점선 스타일
            gridwidth=1,
            showline=False,
            showticklabels=True,
            tickfont=dict(size=11, color="#848E9C", family="Inter"),
            range=y_range,
            fixedrange=True,
            side='left'          # Y축 왼쪽 배치
        ),
        hovermode="x unified",
        showlegend=False,
        hoverlabel=dict(
            bgcolor="#1E2329",
            bordercolor=main_color,
            font=dict(color="#fff")
        )
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': False})
