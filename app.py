# app/app.py
import time
import streamlit as st
from utils.format import fnum
from services.bitget import fetch_positions, fetch_account
from services.history import try_record_snapshot
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
    
    # 1. API Auth
    if "bitget" not in st.secrets:
        st.error("Secrets required")
        st.stop()
    api_key = st.secrets["bitget"]["api_key"]
    api_secret = st.secrets["bitget"]["api_secret"]
    passphrase = st.secrets["bitget"]["passphrase"]
    
    # 2. Data Fetching
    pos_data, _ = fetch_positions(api_key, api_secret, passphrase, PRODUCT_TYPE, MARGIN_COIN)
    acct_data, _ = fetch_account(api_key, api_secret, passphrase, PRODUCT_TYPE, MARGIN_COIN)
    
    # 3. Metrics Calculation
    available = fnum(acct_data.get("available")) if acct_data else 0.0
    equity = fnum(acct_data.get("usdtEquity")) if acct_data else available
    
    upl_pnl = sum(fnum(p.get("unrealizedPL",0)) for p in pos_data)
    margin_used = sum(fnum(p.get("marginSize",0)) for p in pos_data)
    
    roe = (upl_pnl / equity * 100) if equity > 0 else 0
    usage_pct = (margin_used / equity * 100) if equity > 0 else 0
    leverage = (sum(fnum(p.get("marginSize",0)) * fnum(p.get("leverage",0)) for p in pos_data) / equity) if equity > 0 else 0

    # 4. Record Snapshot & Get History
    history_df, _ = try_record_snapshot(equity)

    # 5. Render Layout
    
    # [Top Bar]
    render_top_bar(equity, available, leverage)
    
    # [Main Content] Left: Summary, Right: PnL Chart
    c1, c2 = st.columns([1, 2.5]) # 비율 조정으로 배치 최적화
    
    with c1:
        # 좌측: Equity, Bias, Distribution, PnL 요약
        render_left_summary(equity, usage_pct, upl_pnl, roe, pos_data)
        
    with c2:
        # 우측: PnL Area Chart
        render_chart(history_df, equity)

    # [Bottom] Asset Positions Table
    positions_table(st, pos_data)
    
    time.sleep(10)
    st.rerun()

if __name__ == "__main__":
    main()
