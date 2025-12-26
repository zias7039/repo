# ui/chart.py
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from utils.format import render_html

def render_chart(history_df, current_equity, usdt_rate=None):
    # -----------------------------
    # 1) 데이터 준비
    # -----------------------------
    if history_df is None or history_df.empty:
        df = pd.DataFrame({
            "date": [pd.Timestamp.now().strftime("%Y-%m-%d")],
            "equity": [current_equity]
        })
    else:
        df = history_df.copy()

        # ✅ 날짜 비교 안정화 (Timestamp/문자열 섞여도 OK)
        last_date = pd.to_datetime(df["date"].iloc[-1]).strftime("%Y-%m-%d")
        today_str = pd.Timestamp.now().strftime("%Y-%m-%d")

        if last_date != today_str:
            new_row = pd.DataFrame({"date": [today_str], "equity": [current_equity]})
            df = pd.concat([df, new_row], ignore_index=True)

    df["date"] = pd.to_datetime(df["date"])

    # -----------------------------
    # 2) PnL / 축 범위
    # -----------------------------
    start_val = float(df["equity"].iloc[0])
    end_val = float(df["equity"].iloc[-1])
    pnl_diff = end_val - start_val
    is_profit = pnl_diff >= 0

    min_y = float(df["equity"].min())
    max_y = float(df["equity"].max())

    pad_y = (max_y - min_y) * 0.15
    if pad_y == 0:
        pad_y = max(1e-9, max_y * 0.05)
    y_range = [min_y - pad_y, max_y + pad_y]

    color_line = "#3dd995" if is_profit else "#ff4d4d"
    color_fill = "rgba(61, 217, 149, 0.10)" if is_profit else "rgba(255, 77, 77, 0.10)"
    pnl_sign = "+" if pnl_diff >= 0 else ""

    # ✅ 끝부분 ‘싹둑’ 느낌 방지: x축 패딩
    x_min, x_max = df["date"].min(), df["date"].max()
    x_pad = max(pd.Timedelta(hours=12), (x_max - x_min) * 0.02)
    x_range = [x_min - x_pad, x_max + x_pad]

    # KRW PnL
    krw_pnl_html = ""
    if usdt_rate:
        val_krw = abs(pnl_diff * usdt_rate)
        sign_krw = "+" if pnl_diff >= 0 else "-"
        krw_pnl_html = f"<span class='chart-krw'>≈{sign_krw}₩{val_krw:,.0f}</span>"

    # -----------------------------
    # 3) 카드(1장)로 묶기: 헤더 + 차트
    # -----------------------------
    st.markdown('<div class="dashboard-card chart-card">', unsafe_allow_html=True)

    header_html = f"""
    <div class="chart-head">
        <div class="chart-head-grid">
            <div class="chart-left">
                <span class="chart-title">PnL History</span>
                <span class="chart-badge">30D</span>
            </div>

            <div class="chart-right">
                <div class="chart-label">Recorded PnL</div>
                <div class="chart-pnl" style="color:{color_line};">
                    {pnl_sign}${pnl_diff:,.2f}{krw_pnl_html}
                </div>
            </div>
        </div>
    </div>
    """
    render_html(st, header_html)

    # -----------------------------
    # 4) Plotly
    # -----------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["equity"],
        mode="lines",
        line=dict(color=color_line, width=2, shape="spline", smoothing=1.2),
        fill="tozeroy",
        fillcolor=color_fill,
        hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.2f}<extra></extra>",
    ))

    fig.update_layout(
        template="plotly_dark",
        # ✅ 카드 배경이랑 겹겹이 안 보이게: 완전 투명
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        # ✅ 카드 안에서 여백은 CSS로 관리
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            tickformat="%m-%d",  # %-m은 환경 따라 깨질 수 있어 안전하게
            tickfont=dict(size=11, color="#525252", family="JetBrains Mono"),
            ticks="",
            nticks=5,
            fixedrange=True,
            range=x_range,
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            range=y_range,
            fixedrange=True,
        ),
        hovermode="x unified",
        showlegend=False,
        hoverlabel=dict(
            bgcolor="#1f1f1f",
            bordercolor="#333",
            font=dict(color="#fff", family="JetBrains Mono"),
        ),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("</div>", unsafe_allow_html=True)
