# app/app.py
import streamlit as st
from utils.format import fnum
from services.upbit import fetch_usdt_krw
from services.bitget import fetch_positions, fetch_account, fetch_account_bills, fetch_kline_spot
from ui.styles import inject as inject_styles
from ui.toolbar import render_toolbar
from ui.chart import render_chart
from ui.cards import top_card
from ui.table import positions_table

# ============ CONFIG ============
st.set_page_config(page_title="Perp Dashboard", page_icon="📈", layout="wide")
PRODUCT_TYPE, MARGIN_COIN = "USDT-FUTURES", "USDT"
API_KEY = st.secrets["bitget"]["api_key"]
API_SECRET = st.secrets["bitget"]["api_secret"]
PASSPHRASE = st.secrets["bitget"]["passphrase"]
REFRESH_INTERVAL_SEC = 15

inject_styles(st)

# ============ DATA ============
positions, pos_res = fetch_positions(API_KEY, API_SECRET, PASSPHRASE, PRODUCT_TYPE, MARGIN_COIN)
account, acct_res  = fetch_account(API_KEY, API_SECRET, PASSPHRASE, PRODUCT_TYPE, MARGIN_COIN)

if pos_res.get("code") != "00000": st.error(f"포지션 조회 실패: {pos_res.get('msg')}")
if acct_res.get("code") != "00000": st.error(f"계정 조회 실패: {acct_res.get('msg')}")

bills = fetch_account_bills(API_KEY, API_SECRET, PASSPHRASE, PRODUCT_TYPE, limit=100)
# funding 집계(간단)
from collections import defaultdict
funding_sum = defaultdict(float)
for b in bills:
    bt = (b.get("businessType","") or "").lower()
    if ("settle_fee" in bt) or ("funding" in bt):
        sym = (b.get("symbol","") or "").split("_")[0].upper()
        funding_sum[sym] += fnum(b.get("amount",0.0))
funding_data = {k: {"cumulative": v} for k,v in funding_sum.items()}

# 계좌 메트릭
available = fnum(account.get("available")) if account else 0.0
locked    = fnum(account.get("locked")) if account else 0.0
marg_acct = fnum(account.get("marginSize")) if account else 0.0
total_equity = fnum(account.get("usdtEquity")) if (account and account.get("usdtEquity") is not None) else (available+locked+marg_acct)

total_position_value = 0.0
unrealized_total_pnl = 0.0
for p in positions:
    lev = fnum(p.get("leverage",0.0)); mg = fnum(p.get("marginSize",0.0))
    total_position_value += (mg*lev)
    unrealized_total_pnl += fnum(p.get("unrealizedPL",0.0))
est_leverage = (total_position_value/total_equity) if total_equity>0 else 0.0
withdrawable_pct = (available/total_equity*100) if total_equity>0 else 0.0
roe_pct = (unrealized_total_pnl/total_equity*100) if total_equity>0 else 0.0

USDT_KRW = fetch_usdt_krw()

# ============ UI: 컨트롤바 ============
selected_symbol, selected_gran = render_toolbar(positions)

# ============ Chart ============
df = fetch_kline_spot(symbol=selected_symbol, granularity=selected_gran, limit=100)
render_chart(df, f"{selected_symbol} / {selected_gran}")

# ============ Top Card ============
top_card(
    st,
    total_equity=total_equity,
    available=available,
    withdrawable_pct=withdrawable_pct,
    est_leverage=est_leverage,
    total_position_value=total_position_value,
    unrealized_total_pnl=unrealized_total_pnl,
    roe_pct=roe_pct,
    usdt_krw=USDT_KRW,
)

# ============ Positions ============
positions_table(st, positions, funding_data)

# ============ Footer & Auto refresh ============
from datetime import datetime, timedelta, timezone
KST = timezone(timedelta(hours=9))
now_kst = datetime.now(KST)
st.markdown(f"<div style='font-size:0.7rem;color:#94a3b8;margin:8px 0 12px;'>마지막 갱신: {now_kst.strftime('%H:%M:%S')} (KST) · {REFRESH_INTERVAL_SEC}초 주기 자동 새로고침</div>", unsafe_allow_html=True)

import time
time.sleep(REFRESH_INTERVAL_SEC)
st.rerun()
