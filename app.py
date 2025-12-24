# app/app.py
import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# Services & Utils
from utils.format import fnum
from services.upbit import fetch_usdt_krw
from services.bitget import fetch_positions, fetch_account, fetch_account_bills, fetch_kline_futures
from services.history import try_record_snapshot
from services.fund import get_nav_metrics
from ui.styles import inject as inject_styles
from ui.toolbar import render_toolbar
from ui.chart import render_chart
from ui.cards import render_header, render_side_stats, render_system_logs, render_investor_breakdown
from ui.table import positions_table

# ============ CONSTANTS & CONFIG ============
PRODUCT_TYPE = "USDT-FUTURES"
MARGIN_COIN = "USDT"
REFRESH_INTERVAL_SEC = 10
KST = timezone(timedelta(hours=9))

# ============ LOGIC HELPERS ============
def get_bitget_secrets():
    """Secrets에서 키 가져오기"""
    if "bitget" not in st.secrets:
        st.error("Secrets에 'bitget' 설정이 필요합니다.")
        st.stop()
    return st.secrets["bitget"]["api_key"], st.secrets["bitget"]["api_secret"], st.secrets["bitget"]["passphrase"]

def load_exchange_data(api_key, api_secret, passphrase):
    """거래소 데이터 일괄 조회"""
    pos_data, pos_res = fetch_positions(api_key, api_secret, passphrase, PRODUCT_TYPE, MARGIN_COIN)
    acct_data, acct_res = fetch_account(api_key, api_secret, passphrase, PRODUCT_TYPE, MARGIN_COIN)
    bills_data = fetch_account_bills(api_key, api_secret, passphrase, PRODUCT_TYPE, limit=100)
    usdt_krw = fetch_usdt_krw()
    
    errors = []
    if pos_res.get("code") != "00000": errors.append(f"Position Error: {pos_res.get('msg')}")
    if acct_res.get("code") != "00000": errors.append(f"Account Error: {acct_res.get('msg')}")
    
    return {
        "positions": pos_data,
        "account": acct_data,
        "bills": bills_data,
        "usdt_krw": usdt_krw,
        "errors": errors
    }

def process_metrics(account, positions):
    """자산 및 PNL 지표 계산"""
    available = fnum(account.get("available")) if account else 0.0
    locked    = fnum(account.get("locked")) if account else 0.0
    marg_acct = fnum(account.get("marginSize")) if account else 0.0
    
    # 총 자산 계산 (USDT Equity 우선, 없으면 계산)
    if account and account.get("usdtEquity") is not None:
        total_equity = fnum(account.get("usdtEquity"))
    else:
        total_equity = available + locked + marg_acct

    unrealized_total_pnl = sum(fnum(p.get("unrealizedPL", 0.0)) for p in positions)
    roe_pct = (unrealized_total_pnl / total_equity * 100) if total_equity > 0 else 0.0
    
    return {
        "total_equity": total_equity,
        "unrealized_total_pnl": unrealized_total_pnl,
        "roe_pct": roe_pct
    }

def process_funding_data(bills):
    """펀딩비 누적 합계 계산"""
    funding_sum = defaultdict(float)
    for b in bills:
        bt = (b.get("businessType", "") or "").lower()
        if "settle_fee" in bt or "funding" in bt:
            sym = (b.get("symbol", "") or "").split("_")[0].upper()
            funding_sum[sym] += fnum(b.get("amount", 0.0))
    return {k: {"cumulative": v} for k, v in funding_sum.items()}

def render_nav_chart(history_df, current_equity):
    """NAV 퍼포먼스 미니 차트 렌더링"""
    st.markdown("""<div class="side-card"><div class="stat-label">NAV Performance</div>""", unsafe_allow_html=True)
    
    # 데이터 준비
    if history_df.empty:
        chart_df = pd.DataFrame({"date": [datetime.now(KST).strftime("%Y-%m-%d")], "equity": [current_equity]})
    else:
        chart_df = history_df.copy()
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=chart_df["date"], 
        y=chart_df["equity"],
        mode='lines+markers',
        marker=dict(size=4, color='#2ebd85'),
        line=dict(color='#2ebd85', width=2),
        hoverinfo='y+x'
    ))
    
    # Y축 마진 설정
    min_val, max_val = chart_df['equity'].min(), chart_df['equity'].max()
    margin = (max_val - min_val) * 0.1 if max_val != min_val else max_val * 0.01
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=200,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=True, gridcolor="#2b313a", showticklabels=True, tickfont=dict(size=10), range=[min_val - margin, max_val + margin]),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)


# ============ MAIN APP ============
def main():
    st.set_page_config(page_title="Quantum Fund", page_icon="📊", layout="wide")
    inject_styles(st)
    
    # 1. Init & Auth
    api_key, api_secret, passphrase = get_bitget_secrets()
    
    # 2. Data Fetching
    data = load_exchange_data(api_key, api_secret, passphrase)
    for err in data["errors"]:
        st.error(err)
        
    positions = data["positions"]
    metrics = process_metrics(data["account"], positions)
    funding_data = process_funding_data(data["bills"])
    
    # 3. History & NAV Calculation
    history_df, is_recorded_now = try_record_snapshot(metrics["total_equity"])
    if is_recorded_now:
        st.toast("✅ Daily Equity Snapshot Recorded!")
        
    nav_data = get_nav_metrics(metrics["total_equity"], history_df)
    now_kst = datetime.now(KST)

    # 4. Render UI
    # [Top] Header
    render_header(
        now_kst, 
        nav=nav_data["nav"], 
        nav_change=nav_data["change_pct"], 
        total_units=nav_data["total_units"]
    )

    # [Main] Grid Layout (3:1)
    col_main, col_side = st.columns([3, 1])

    with col_main:
        # Chart & Toolbar
        selected_symbol, selected_gran = render_toolbar(positions)
        chart_df = fetch_kline_futures(symbol=selected_symbol, granularity=selected_gran, product_type=PRODUCT_TYPE)
        render_chart(chart_df, f"{selected_symbol}")
        
        # Tabs
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs([f"Positions ({len(positions)})", "Open Orders (0)", "Order History"])
        
        with tab1:
            positions_table(st, positions, funding_data)
        with tab2:
            st.info("No open orders.")
        with tab3:
            st.info("History feature coming soon.")

    with col_side:
        # Side Stats
        render_side_stats(
            total_equity=metrics["total_equity"],
            unrealized_total_pnl=metrics["unrealized_total_pnl"],
            roe_pct=metrics["roe_pct"],
            usdt_krw=data["usdt_krw"]
        )
        
        # Investor Breakdown
        render_investor_breakdown(
            investors=nav_data["investors"],
            current_nav=nav_data["nav"],
            usdt_krw=data["usdt_krw"]
        )
        
        # NAV Chart
        render_nav_chart(history_df, metrics["total_equity"])

        # Logs (Dummy)
        logs = [
            {"type": "INFO", "msg": "System synced", "time": now_kst.strftime("%H:%M:%S")},
        ]
        render_system_logs(logs)

    time.sleep(REFRESH_INTERVAL_SEC)
    st.rerun()

if __name__ == "__main__":
    main()
