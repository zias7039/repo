import time
import hmac
import hashlib
import base64
import requests
import streamlit as st
import pandas as pd
from urllib.parse import urlencode
from datetime import datetime

# ======================================
# CONFIG
# ======================================
st.set_page_config(page_title="Perp Dashboard", page_icon="📈", layout="wide")

PRODUCT_TYPE = "USDT-FUTURES"
MARGIN_COIN = "USDT"

API_KEY = st.secrets["bitget"]["api_key"]
API_SECRET = st.secrets["bitget"]["api_secret"]
PASSPHRASE = st.secrets["bitget"]["passphrase"]

BASE_URL = "https://api.bitget.com"
REFRESH_INTERVAL_SEC = 15

# ======================================
# API helpers
# ======================================
def _timestamp_ms():
    return str(int(time.time() * 1000))


def _sign(timestamp_ms, method, path, query_params, body, secret_key):
    if body is None:
        body = ""
    method_up = method.upper()
    if query_params:
        query_str = urlencode(query_params)
        sign_target = f"{timestamp_ms}{method_up}{path}?{query_str}{body}"
    else:
        sign_target = f"{timestamp_ms}{method_up}{path}{body}"
    mac = hmac.new(secret_key.encode("utf-8"), sign_target.encode("utf-8"), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()


def _private_get(path, params=None):
    ts = _timestamp_ms()
    signature = _sign(ts, "GET", path, params, "", API_SECRET)
    if params:
        query_str = urlencode(params)
        url = f"{BASE_URL}{path}?{query_str}"
    else:
        url = f"{BASE_URL}{path}"
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "ACCESS-TIMESTAMP": ts,
        "locale": "en-US",
        "Content-Type": "application/json",
    }
    return requests.get(url, headers=headers).json()


def fetch_positions():
    params = {"productType": PRODUCT_TYPE, "marginCoin": MARGIN_COIN}
    res = _private_get("/api/v2/mix/position/all-position", params)
    if res.get("code") != "00000":
        return [], res
    return res.get("data") or [], res


def fetch_account():
    params = {"productType": PRODUCT_TYPE, "marginCoin": MARGIN_COIN}
    res = _private_get("/api/v2/mix/account/accounts", params)
    if res.get("code") != "00000":
        return None, res
    arr = res.get("data") or []
    acct = next((a for a in arr if a.get("marginCoin") == MARGIN_COIN), None)
    return acct, res

# ======================================
# FETCH DATA & METRICS
# ======================================
positions, _ = fetch_positions()
account, _ = fetch_account()


def fnum(v):
    try:
        return float(v)
    except:
        return 0.0

available = fnum(account.get("available")) if account else 0.0
locked = fnum(account.get("locked")) if account else 0.0
margin_size = fnum(account.get("marginSize")) if account else 0.0

if account and "usdtEquity" in account:
    total_equity = fnum(account["usdtEquity"])
elif account and "equity" in account:
    total_equity = fnum(account["equity"])
else:
    total_equity = available + locked + margin_size

withdrawable_pct = (available / total_equity * 100.0) if total_equity > 0 else 0.0

total_position_value = 0.0
long_value = 0.0
short_value = 0.0
unrealized_total_pnl = 0.0
nearest_liq_pct = None

for p in positions:
    lev = fnum(p.get("leverage", 0.0))
    mg = fnum(p.get("marginSize", 0.0))
    pos_val = mg * lev
    total_position_value += pos_val

    side = (p.get("holdSide", "") or "").lower()
    if side == "long":
        long_value += pos_val
    elif side == "short":
        short_value += pos_val

    unrealized_total_pnl += fnum(p.get("unrealizedPL", 0.0))

    mark_price = fnum(p.get("markPrice"))
    liq_price = fnum(p.get("liquidationPrice"))
    if liq_price != 0:
        dist_pct = abs((mark_price - liq_price) / liq_price) * 100.0
        if nearest_liq_pct is None or dist_pct < nearest_liq_pct:
            nearest_liq_pct = dist_pct

est_leverage = (total_position_value / total_equity) if total_equity > 0 else 0.0

if long_value > short_value:
    bias_label = "LONG"
    bias_color = "#4ade80"
elif short_value > long_value:
    bias_label = "SHORT"
    bias_color = "#f87171"
else:
    bias_label = "FLAT"
    bias_color = "#94a3b8"

pnl_color = "#4ade80" if unrealized_total_pnl >= 0 else "#f87171"

if nearest_liq_pct is None:
    liq_text = "n/a"
    liq_color = "#94a3b8"
else:
    liq_text = f"{nearest_liq_pct:.2f}%"
    liq_color = "#4ade80" if nearest_liq_pct > 30 else "#f87171"

positions_count = len(positions)
if positions_count > 0:
    longs = sum(1 for p in positions if (p.get("holdSide", "") or "").lower() == "long")
    shorts = sum(1 for p in positions if (p.get("holdSide", "") or "").lower() == "short")
    pos_long_pct = (longs / positions_count) * 100.0
    pos_short_pct = (shorts / positions_count) * 100.0
else:
    pos_long_pct = 0.0
    pos_short_pct = 0.0

roe_pct = (unrealized_total_pnl / total_equity * 100.0) if total_equity > 0 else 0.0

# ======================================
# SESSION STATE FOR CHART HISTORY
# ======================================
if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = []

st.session_state.pnl_history.append({
    "ts": datetime.now().strftime("%H:%M:%S"),
    "pnl": unrealized_total_pnl,
})
# keep last 200 points
st.session_state.pnl_history = st.session_state.pnl_history[-200:]
chart_df = pd.DataFrame(st.session_state.pnl_history)

# ======================================
# STYLE HELPERS
# ======================================
CARD_BG = "#1e2538"
TEXT_SUB = "#94a3b8"
TEXT_MAIN = "#f8fafc"
BORDER = "rgba(148,163,184,0.2)"
SHADOW = "0 24px 48px rgba(0,0,0,0.6)"
FONT_FAMILY = "-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif"

# ======================================
# TOP BAR (KPI BAR) - FIXED: NO LEADING NEWLINE
# ======================================
st.markdown(
    f"""<div style='display:flex;align-items:flex-start;justify-content:space-between;background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;padding:12px 16px;margin-bottom:8px;box-shadow:{SHADOW};font-family:{FONT_FAMILY};'>
<div style='display:flex;flex-wrap:wrap;row-gap:8px;column-gap:32px;font-size:0.8rem;'>
    <div style='color:{TEXT_SUB};'>
        <div style='font-size:0.75rem;'>Total Value</div>
        <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${total_equity:,.2f}</div>
        <div style='font-size:0.7rem;color:{TEXT_SUB};'>Perp ${total_equity:,.2f}</div>
    </div>
    <div style='color:{TEXT_SUB};'>
        <div style='font-size:0.75rem;'>Withdrawable <span style='color:#4ade80;'>{withdrawable_pct:.2f}%</span></div>
        <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${available:,.2f}</div>
    </div>
    <div style='color:{TEXT_SUB};'>
        <div style='font-size:0.75rem;'>Leverage <span style='background:#7f1d1d;color:#fff;padding:2px 6px;border-radius:6px;font-size:0.7rem;font-weight:600;'>{est_leverage:.2f}x</span></div>
        <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${total_position_value:,.2f}</div>
    </div>
</div>
<div style='font-size:0.7rem;color:{TEXT_SUB};white-space:nowrap;'>Manual refresh • {REFRESH_INTERVAL_SEC}s</div>
</div>""",
    unsafe_allow_html=True,
)

# ======================================
# MID CARD (EQUITY + CHART) - FIXED: NO LEADING NEWLINE
# ======================================
st.markdown(
    f"""<div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;padding:16px;margin-bottom:12px;box-shadow:{SHADOW};font-family:{FONT_FAMILY};'>""",
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([0.5, 0.5])
with left_col:
    st.markdown(
        f"""<div style='color:{TEXT_SUB};font-size:0.8rem;'>
<div style='font-size:0.8rem;color:{TEXT_SUB};'>Perp Equity</div>
<div style='color:{TEXT_MAIN};font-weight:600;font-size:1.4rem;margin-bottom:12px;'>${total_equity:,.2f}</div>
<div style='font-size:0.75rem;color:{TEXT_SUB};'>Direction Bias</div>
<div style='font-weight:600;font-size:0.9rem;color:{bias_color};margin-bottom:12px;'>{bias_label}</div>
<div style='font-size:0.75rem;color:{TEXT_SUB};'>Unrealized PnL</div>
<div style='font-size:1rem;font-weight:600;color:{pnl_color};'>${unrealized_total_pnl:,.2f}</div>
<div style='font-size:0.7rem;color:{TEXT_SUB};margin-bottom:12px;'>{roe_pct:.2f}% ROE</div>
</div>""",
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown(
        f"""<div style='display:flex;gap:8px;justify-content:flex-start;flex-wrap:wrap;margin-bottom:8px;font-size:0.7rem'>
<div style='background:#0f3;color:#000;font-weight:600;border-radius:6px;padding:4px 8px;'>24H</div>
<div style='background:{CARD_BG};border:1px solid #334155;border-radius:6px;padding:4px 8px;color:{TEXT_SUB};'>1W</div>
</div>""",
        unsafe_allow_html=True,
    )

# 차트도 같은 카드 안에서 바로 출력
st.line_chart(chart_df, x="ts", y="pnl", height=220)

# 카드 닫기
st.markdown("</div>", unsafe_allow_html=True)

# ======================================
# POSITIONS CARD - FIXED: NO LEADING NEWLINE
# ======================================
st.markdown(
    f"""<div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;padding:12px 16px;margin-bottom:12px;box-shadow:{SHADOW};font-family:{FONT_FAMILY};'>
<div style='font-size:0.8rem;color:{TEXT_SUB};margin-bottom:8px;'>Positions: {positions_count} | Total: ${total_position_value:,.2f}</div>""",
    unsafe_allow_html=True,
)

rows = []
for p in positions:
    lev = fnum(p.get("leverage", 0.0))
    mg = fnum(p.get("marginSize", 0.0))
    mark_price = fnum(p.get("markPrice"))
    liq_price = fnum(p.get("liquidationPrice"))
    if liq_price:
        dist_pct = abs((mark_price - liq_price) / liq_price) * 100.0
        liq_dist = f"{dist_pct:.2f}%"
    else:
        liq_dist = "n/a"

    rows.append(
        {
            "Asset": p.get("symbol"),
            "Type": (p.get("holdSide", "") or "").upper(),
            "Lev": f"{lev:.1f}x",
            "Value": f"{mg * lev:,.2f}",
            "PnL": f"{fnum(p.get('unrealizedPL', 0.0)):.2f}",
            "Liq Dist": liq_dist,
        }
    )

st.dataframe(rows, use_container_width=True)

st.markdown(
    f"""<div style='font-size:0.7rem;color:{TEXT_SUB};margin-top:8px;'>Last update: {datetime.now().strftime('%H:%M:%S')} • refresh every {REFRESH_INTERVAL_SEC}s</div></div>""",
    unsafe_allow_html=True,
)
