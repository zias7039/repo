# app/app.py
import time
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from utils.format import fnum
from services.upbit import fetch_usdt_krw
from services.bitget import fetch_positions, fetch_account, fetch_account_bills, fetch_kline_futures
from ui.styles import inject as inject_styles
from ui.toolbar import render_toolbar
from ui.chart import render_chart
from ui.cards import top_card
from ui.table import positions_table

# ============ CONFIG ============
st.set_page_config(page_title="Perp Dashboard", page_icon="📈", layout="wide")
PRODUCT_TYPE = "USDT-FUTURES"
MARGIN_COIN = "USDT"

if "bitget" not in st.secrets:
    st.error("Secrets에 'bitget' 설정이 없습니다.")
    st.stop()

API_KEY = st.secrets["bitget"]["api_key"]
API_SECRET = st.secrets["bitget"]["api_secret"]
PASSPHRASE = st.secrets["bitget"]["passphrase"]
REFRESH_INTERVAL_SEC = 15

# ============ LOGIC HELPERS ============
def load_data():
    pos_data, pos_res = fetch_positions(API_KEY, API_SECRET, PASSPHRASE, PRODUCT_TYPE, MARGIN_COIN)
    acct_data, acct_res = fetch_account(API_KEY, API_SECRET, PASSPHRASE, PRODUCT_TYPE, MARGIN_COIN)
    # 펀딩비 계산용 bills (최소한의 호출 유지)
    bills_data = fetch_account_bills(API_KEY, API_SECRET, PASSPHRASE, PRODUCT_TYPE, limit=100)
    usdt_krw = fetch_usdt_krw()
    
    return {
        "positions": pos_data,
        "account": acct_data,
        "bills": bills_data,
        "usdt_krw": usdt_krw,
        "errors": [
            f"포지션: {pos_res.get('msg')}" if pos_res.get("code") != "00000" else None,
            f"계정: {acct_res.get('msg')}" if acct_res.get("code") != "00000" else None,
        ]
    }

def process_funding(bills):
    funding_sum = defaultdict(float)
    for b in bills:
        bt = (b.get("businessType","") or "").lower()
        if ("settle_fee" in bt) or ("funding" in bt):
            sym = (b.get("symbol","") or "").split("_")[0].upper()
            funding_sum[sym] += fnum(b.get("amount", 0.0))
    return {k: {"cumulative": v} for k,v in funding_sum.items()}

def calculate_metrics(account, positions):
    available = fnum(account.get("available")) if account else 0.0
    locked    = fnum(account.get("locked")) if account else 0.0
    marg_acct = fnum(account.get("marginSize")) if account else 0.0
    
    if account and account.get("usdtEquity") is not None:
        total_equity = fnum(account.get("usdtEquity"))
    else:
        total_equity = available + locked + marg_acct

    total_position_value = 0.0
    unrealized_total_pnl = 0.0
    
    for p in positions:
        lev = fnum(p.get("leverage", 0.0))
        mg = fnum(p.get("marginSize", 0.0))
        total_position_value += (mg * lev)
        unrealized_total_pnl += fnum(p.get("unrealizedPL", 0.0))
        
    est_leverage = (total_position_value / total_equity) if total_equity > 0 else 0.0
    withdrawable_pct = (available / total_equity * 100) if total_equity > 0 else 0.0
    roe_pct = (unrealized_total_pnl / total_equity * 100) if total_equity > 0 else 0.0
    
    return {
        "total_equity": total_equity,
        "available": available,
        "total_position_value": total_position_value,
        "unrealized_total_pnl": unrealized_total_pnl,
        "est_leverage": est_leverage,
        "withdrawable_pct": withdrawable_pct,
        "roe_pct": roe_pct
    }

# ============ MAIN APP ============
def main():
    inject_styles(st)
    
    # [제거됨] 새로고침 버튼 영역 삭제

    data = load_data()
    for err in data["errors"]:
        if err: st.error(err)
        
    positions = data["positions"]
    account = data["account"]
    bills = data["bills"]
    
    metrics = calculate_metrics(account, positions)
    funding_data = process_funding(bills)
    
    # UI: 툴바
    selected_symbol, selected_gran = render_toolbar(positions)

    # UI: 차트 (MA 지표 유지)
    df = fetch_kline_futures(symbol=selected_symbol, granularity=selected_gran, product_type=PRODUCT_TYPE, limit=100)
    render_chart(df, f"{selected_symbol} ({selected_gran})")

    # UI: 상단 요약 카드 (실현 손익 제거됨)
    top_card(
        st,
        total_equity=metrics["total_equity"],
        available=metrics["available"],
        withdrawable_pct=metrics["withdrawable_pct"],
        est_leverage=metrics["est_leverage"],
        total_position_value=metrics["total_position_value"],
        unrealized_total_pnl=metrics["unrealized_total_pnl"],
        roe_pct=metrics["roe_pct"],
        usdt_krw=data["usdt_krw"],
    )

    # UI: 포지션 테이블
    positions_table(st, positions, funding_data)
    
    # [제거됨] 실현 손익 내역 Expander 삭제

    # Footer & Auto Refresh
    KST = timezone(timedelta(hours=9))
    now_kst = datetime.now(KST)
    st.markdown(
        f"""<div style='text-align:right;font-size:0.8rem;color:#64748b;margin-top:20px;'>
        Last Update: {now_kst.strftime('%H:%M:%S')} (KST)
        </div>""", 
        unsafe_allow_html=True
    )

    time.sleep(REFRESH_INTERVAL_SEC)
    st.rerun()

if __name__ == "__main__":
    main()
