# app/app.py
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from utils.format import fnum
from services.upbit import fetch_usdt_krw
from services.bitget import fetch_positions, fetch_account, fetch_account_bills, fetch_kline_futures
from services.history import try_record_snapshot, load_history
from services.fund import get_nav_metrics
from ui.styles import inject as inject_styles
from ui.chart import render_chart
from ui.cards import render_top_bar, render_left_summary
from ui.table import render_bottom_section

# Config
PRODUCT_TYPE = "USDT-FUTURES"
MARGIN_COIN = "USDT"

# [핵심 변경 1] 10초마다 이 함수 내부만 부분 새로고침 (전체 리로딩 X)
# 주의: Streamlit 1.37 이상 버전 필요 (requirements.txt 확인)
@st.fragment(run_every=10)
def run_dashboard(api_key, api_secret, passphrase):
    # ---------------------------
    # 1. Data Fetch
    # ---------------------------
    # API 호출이 실패해도 화면이 깨지지 않도록 예외처리 권장
    try:
        pos_data, _ = fetch_positions(api_key, api_secret, passphrase, PRODUCT_TYPE, MARGIN_COIN)
        acct_data, _ = fetch_account(api_key, api_secret, passphrase, PRODUCT_TYPE, MARGIN_COIN)
        usdt_rate = fetch_usdt_krw()
    except Exception as e:
        st.error(f"API Error: {e}")
        return

    # Metrics Calc
    available = fnum(acct_data.get("available")) if acct_data else 0.0
    equity = fnum(acct_data.get("usdtEquity")) if acct_data else available
    
    upl_pnl = sum(fnum(p.get("unrealizedPL",0)) for p in pos_data)
    margin_used = sum(fnum(p.get("marginSize",0)) for p in pos_data)
    
    roe = (upl_pnl / equity * 100) if equity > 0 else 0
    usage_pct = (margin_used / equity * 100) if equity > 0 else 0
    leverage = (sum(fnum(p.get("marginSize",0)) * fnum(p.get("leverage",0)) for p in pos_data) / equity) if equity > 0 else 0

    # History & NAV
    history_df, _ = try_record_snapshot(equity)
    nav_data = get_nav_metrics(equity, history_df)

    # ---------------------------
    # 2. Layout Render
    # ---------------------------
    render_top_bar(equity, available, leverage, usdt_rate=usdt_rate)
    
    c1, c2 = st.columns([1, 3])
    with c1:
        render_left_summary(equity, usage_pct, upl_pnl, roe, pos_data, usdt_rate=usdt_rate)
    with c2:
        render_chart(history_df, equity, usdt_rate=usdt_rate)

    render_bottom_section(st, pos_data, nav_data, usdt_rate=usdt_rate)
    
    # [핵심 변경 2] time.sleep() 및 st.rerun() 삭제됨

def main():
    st.set_page_config(page_title="Hyperdash", page_icon="⚡", layout="wide")
    inject_styles(st)
    
    if "bitget" not in st.secrets:
        st.error("Secrets required")
        st.stop()
        
    api_key = st.secrets["bitget"]["api_key"]
    api_secret = st.secrets["bitget"]["api_secret"]
    passphrase = st.secrets["bitget"]["passphrase"]
    
    # 대시보드 루프 실행
    run_dashboard(api_key, api_secret, passphrase)

if __name__ == "__main__":
    main()
