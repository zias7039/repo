import time
import hmac
import hashlib
import base64
import requests
import streamlit as st
import pandas as pd
from urllib.parse import urlencode
from datetime import datetime
from textwrap import dedent

# =============== CONFIG ===============
st.set_page_config(page_title="Perp Dashboard", page_icon="📈", layout="wide")

PRODUCT_TYPE = "USDT-FUTURES"
MARGIN_COIN = "USDT"

API_KEY = st.secrets["bitget"]["api_key"]
API_SECRET = st.secrets["bitget"]["api_secret"]
PASSPHRASE = st.secrets["bitget"]["passphrase"]

BASE_URL = "https://api.bitget.com"
REFRESH_INTERVAL_SEC = 15

# =============== HELPERS ===============
def _timestamp_ms() -> str:
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

    mac = hmac.new(secret_key.encode("utf-8"), sign_target.encode("utf-8"), digestmod=hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()

def _private_get(path, params=None):
    ts = _timestamp_ms()
    signature = _sign(ts, "GET", path, params, "", API_SECRET)

    if params:
        q = urlencode(params)
        url = f"{BASE_URL}{path}?{q}"
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
    r = requests.get(url, headers=headers)
    return r.json()


def fetch_positions():
    params = {"productType": PRODUCT_TYPE, "marginCoin": MARGIN_COIN}
    res = _private_get("/api/v2/mix/position/all-position", params)
    if res.get("code") != "00000":
        return [], res
    data = res.get("data") or []
    return data, res


def fetch_account():
    params = {"productType": PRODUCT_TYPE, "marginCoin": MARGIN_COIN}
    res = _private_get("/api/v2/mix/account/accounts", params)
    if res.get("code") != "00000":
        return None, res
    arr = res.get("data") or []
    acct = next((a for a in arr if a.get("marginCoin") == MARGIN_COIN), None)
    return acct, res

# =============== FETCH DATA ===============
positions, _raw_pos = fetch_positions()
account, _raw_acct = fetch_account()

def fnum(v):
    try:
        return float(v)
    except:
        return 0.0

available   = fnum(account.get("available")) if account else 0.0
locked      = fnum(account.get("locked")) if account else 0.0
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
    mg  = fnum(p.get("marginSize", 0.0))
    notional_est = mg * lev
    total_position_value += notional_est

    side = (p.get("holdSide", "") or "").lower()
    if side == "long":
        long_value += notional_est
    elif side == "short":
        short_value += notional_est

    unrealized_total_pnl += fnum(p.get("unrealizedPL", 0.0))

    mark_price = fnum(p.get("markPrice"))
    liq_price  = fnum(p.get("liquidationPrice"))
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
roe_pct = (unrealized_total_pnl / total_equity * 100.0) if total_equity > 0 else 0.0

if nearest_liq_pct is None:
    liq_text = "n/a"
    liq_color = "#94a3b8"
else:
    liq_text  = f"{nearest_liq_pct:.2f}%"
    liq_color = "#4ade80" if nearest_liq_pct > 30 else "#f87171"

positions_count = len(positions)

if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = []

st.session_state.pnl_history.append({
    "ts": datetime.now().strftime("%H:%M:%S"),
    "pnl": unrealized_total_pnl,
})

st.session_state.pnl_history = st.session_state.pnl_history[-200:]
chart_df = pd.DataFrame(st.session_state.pnl_history)

# =============== STYLE CONSTS ===============
CARD_BG     = "#1e2538"
TEXT_SUB    = "#94a3b8"
TEXT_MAIN   = "#f8fafc"
BORDER      = "rgba(148,163,184,0.2)"
SHADOW      = "0 24px 48px rgba(0,0,0,0.6)"
FONT_FAMILY = "-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif"

# key helper: ALWAYS use this instead of st.markdown directly for HTML blocks

def render_html(html: str):
    st.markdown(html, unsafe_allow_html=True)

# =============== TOP CARD ===============

top_card_html = dedent(f"""
<div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;
            padding:12px 16px;margin-bottom:8px;box-shadow:{SHADOW};
            font-family:{FONT_FAMILY};font-size:0.8rem;display:flex;
            align-items:flex-start;justify-content:space-between;'>

    <div style='display:flex;flex-wrap:wrap;row-gap:8px;column-gap:32px;'>
        <div style='color:{TEXT_SUB};'>
            <div style='font-size:0.75rem;'>Total Value</div>
            <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>
                ${total_equity:,.2f}
            </div>
            <div style='font-size:0.7rem;color:{TEXT_SUB};'>Perp ${total_equity:,.2f}</div>
        </div>

        <div style='color:{TEXT_SUB};'>
            <div style='font-size:0.75rem;'>
                Withdrawable
                <span style='color:#4ade80;'>{withdrawable_pct:.2f}%</span>
            </div>
            <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>
                ${available:,.2f}
            </div>
        </div>

        <div style='color:{TEXT_SUB};'>
            <div style='font-size:0.75rem;'>
                Leverage
                <span style='background:#7f1d1d;color:#fff;padding:2px 6px;
                             border-radius:6px;font-size:0.7rem;font-weight:600;'>
                    {est_leverage:.2f}x
                </span>
            </div>
            <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>
                ${total_position_value:,.2f}
            </div>
        </div>
    </div>

    <div style='font-size:0.7rem;color:{TEXT_SUB};white-space:nowrap;'>
        Manual refresh • {REFRESH_INTERVAL_SEC}s
    </div>
</div>
""")

render_html(top_card_html)

# =============== MID SECTION ===============

col_left, col_right = st.columns([0.4, 0.6])

with col_left:
    mid_left_html = dedent(f"""
    <div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;
                padding:16px;box-shadow:{SHADOW};font-family:{FONT_FAMILY};
                margin-bottom:12px;font-size:0.8rem;color:{TEXT_SUB};'>

        <div style='font-size:0.8rem;color:{TEXT_SUB};'>Perp Equity</div>
        <div style='color:{TEXT_MAIN};font-weight:600;font-size:1.4rem;
                    margin-bottom:12px;'>
            ${total_equity:,.2f}
        </div>

        <div style='font-size:0.75rem;color:{TEXT_SUB};'>Direction Bias</div>
        <div style='font-weight:600;font-size:0.9rem;color:{bias_color};
                    margin-bottom:12px;'>
            {bias_label}
        </div>

        <div style='font-size:0.75rem;color:{TEXT_SUB};'>Unrealized PnL</div>
        <div style='font-size:1rem;font-weight:600;color:{pnl_color};'>
            ${unrealized_total_pnl:,.2f}
        </div>
        <div style='font-size:0.7rem;color:{TEXT_SUB};margin-bottom:12px;'>
            {roe_pct:.2f}% ROE
        </div>

        <div style='display:flex;gap:8px;flex-wrap:wrap;font-size:0.7rem;'>
            <div style='background:#0f3;color:#000;font-weight:600;
                        border-radius:6px;padding:4px 8px;'>
                24H
            </div>
            <div style='background:{CARD_BG};border:1px solid #334155;
                        border-radius:6px;padding:4px 8px;color:{TEXT_SUB};'>
                1W
            </div>
        </div>
    </div>
    """)
    render_html(mid_left_html)

with col_right:
    st.line_chart(chart_df, x="ts", y="pnl", height=220)

# =============== POSITIONS ===============

positions_header_html = dedent(f"""
<div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;
            padding:12px 16px;margin-bottom:12px;box-shadow:{SHADOW};
            font-family:{FONT_FAMILY};font-size:0.8rem;color:{TEXT_SUB};'>
    Positions: {len(positions)} | Total: ${total_position_value:,.2f}
</div>
""")
render_html(positions_header_html)

rows = []
for p in positions:
    lev = fnum(p.get("leverage", 0.0))
    mg  = fnum(p.get("marginSize", 0.0))
    mark_price = fnum(p.get("markPrice"))
    liq_price  = fnum(p.get("liquidationPrice"))

    if liq_price:
        dist_pct = abs((mark_price - liq_price) / liq_price) * 100.0
        liq_dist = f"{dist_pct:.2f}%"
    else:
        liq_dist = "n/a"

    rows.append({
        "Asset": p.get("symbol"),
        "Type": (p.get("holdSide", "") or "").upper(),
        "Lev": f"{lev:.1f}x",
        "Value": f"{mg * lev:,.2f}",
        "PnL": f"{fnum(p.get('unrealizedPL', 0.0)):.2f}",
        "Liq Dist": liq_dist,
    })

st.dataframe(rows, use_container_width=True)

render_html(
    dedent(f"""
    <div style='font-size:0.7rem;color:{TEXT_SUB};margin-top:8px;font-family:{FONT_FAMILY};'>
        Last update: {datetime.now().strftime("%H:%M:%S")} • refresh every {REFRESH_INTERVAL_SEC}s
    </div>
    """)
)
