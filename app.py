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

def calculate_realized_pnl(bills):
    """
    최근 내역(bills)에서 '포지션 종료(close)'로 인한 실현 손익 합산
    """
    realized_sum = 0.0
    history_list = []
    
    # KST 기준 오늘 날짜 확인 (00:00 이후만 합산하려면 날짜 필터 추가 가능)
    # 여기서는 가져온 bills(최근 100개) 전체를 대상으로 합산
    
    for b in bills:
        bt = (b.get("businessType", "") or "").lower()
        amount = fnum(b.get("amount", 0.0))
        
        # 실현 손익 관련 타입 필터링 (close_long, close_short 등)
        if "close" in bt:
            realized_sum += amount
            
            # 히스토리 표시용 데이터 저장
            ts = int(b.get("cTime", 0))
            dt = datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')
            symbol = b.get("symbol", "").split("_")[0]
            history_list.append({
                "Time": dt,
                "Symbol": symbol,
                "Type": bt,
                "Amount (USDT)": amount
            })
            
    return realized_sum, history_list

# ============ MAIN APP ============
def main():
    inject_styles(st)
    
    c1, c2 = st.columns([0.8, 0.2])
    with c2:
        if st.button("🔄 새로고침", use_container_width=True):
            st.rerun()

    data = load_data()
    for err in data["errors"]:
        if err: st.error(err)
        
    positions = data["positions"]
    account = data["account"]
    bills = data["bills"]
    
    metrics = calculate_metrics(account, positions)
    funding_data = process_funding(bills)
    
    # [추가됨] 실현 손익 계산
    realized_pnl, realized_history = calculate_realized_pnl(bills)
    
    # UI: 툴바
    selected_symbol, selected_gran = render_toolbar(positions)

    # UI: 차트 (MA 지표 포함)
    df = fetch_kline_futures(symbol=selected_symbol, granularity=selected_gran, product_type=PRODUCT_TYPE, limit=100)
    render_chart(df, f"{selected_symbol} ({selected_gran})")

    # UI: 상단 요약 카드 (실현손익 전달)
    top_card(
        st,
        total_equity=metrics["total_equity"],
        available=metrics["available"],
        withdrawable_pct=metrics["withdrawable_pct"],
        est_leverage=metrics["est_leverage"],
        total_position_value=metrics["total_position_value"],
        unrealized_total_pnl=metrics["unrealized_total_pnl"],
        roe_pct=metrics["roe_pct"],
        realized_pnl=realized_pnl,  # 추가됨
        usdt_krw=data["usdt_krw"],
    )

    # UI: 포지션 테이블
    positions_table(st, positions, funding_data)
    
    # [추가됨] 실현 손익 상세 내역 (아코디언)
    if realized_history:
        with st.expander("📝 최근 실현 손익 내역 (Recent Realized PnL)", expanded=False):
            hf = pd.DataFrame(realized_history)
            st.dataframe(hf, use_container_width=True, hide_index=True)

    # Footer
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
