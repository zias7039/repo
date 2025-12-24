# app/app.py
import time
import streamlit as st
from datetime import datetime, timedelta, timezone

from utils.format import fnum
from services.bitget import fetch_positions, fetch_account, fetch_account_bills, fetch_kline_futures
from services.upbit import fetch_usdt_krw
from ui.styles import inject as inject_styles
from ui.cards import render_top_bar, render_left_summary
from ui.chart import render_chart
from ui.table import positions_table

# Config
PRODUCT_TYPE = "USDT-FUTURES"
MARGIN_COIN = "USDT"

def main():
    st.set_page_config(page_title="Hyperdash", page_icon="⚡", layout="wide")
    inject_styles(st)
    
    # 1. Init & Secrets
    if "bitget" not in st.secrets:
        st.error("Secrets required")
        st.stop()
    api_key = st.secrets["bitget"]["api_key"]
    api_secret = st.secrets["bitget"]["api_secret"]
    passphrase = st.secrets["bitget"]["passphrase"]
    
    # 2. Data Fetch
    pos_data, _ = fetch_positions(api_key, api_secret, passphrase, PRODUCT_TYPE, MARGIN_COIN)
    acct_data, _ = fetch_account(api_key, api_secret, passphrase, PRODUCT_TYPE, MARGIN_COIN)
    
    # Metrics Calc
    available = fnum(acct_data.get("available")) if acct_data else 0.0
    equity = fnum(acct_data.get("usdtEquity")) if acct_data else available
    
    upl_pnl = sum(fnum(p.get("unrealizedPL",0)) for p in pos_data)
    roe = (upl_pnl / equity * 100) if equity else 0
    margin_used = sum(fnum(p.get("marginSize",0)) for p in pos_data)
    usage_pct = (margin_used / equity * 100) if equity else 0
    leverage = (sum(fnum(p.get("marginSize",0)) * fnum(p.get("leverage",0)) for p in pos_data) / equity) if equity else 0

    # 3. Render Layout
    
    # [Row 1] Top Stats Bar (이미지 상단)
    render_top_bar(equity, available, leverage)
    
    # [Row 2] Main Split (Left: Summary / Right: Chart)
    c_left, c_right = st.columns([1, 3])
    
    with c_left:
        # 좌측 패널: Equity, Bias, PnL
        render_left_summary(equity, usage_pct, upl_pnl, roe, pos_data)
        
    with c_right:
        # 우측 패널: 차트 (탭 포함)
        tabs = st.tabs(["24H", "1W", "1M", "All"]) # 데코레이션용 탭
        
        # 차트 데이터 (BTCUSDT 기본)
        df = fetch_kline_futures("BTCUSDT", granularity="1h")
        render_chart(df, "PnL Chart")

    # [Row 3] Bottom Table (Asset Positions)
    # 탭 메뉴
    st.markdown("<br>", unsafe_allow_html=True)
    t1, t2, t3, t4, t5 = st.tabs(["Asset Positions", "Open Orders", "Recent Fills", "Completed Trades", "Transfers"])
    
    with t1:
        positions_table(st, pos_data)
    
    time.sleep(10)
    st.rerun()

if __name__ == "__main__":
    main()
