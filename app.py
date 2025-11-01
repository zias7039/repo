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

# ================= CONFIG =================
st.set_page_config(page_title="Perp Dashboard", page_icon="📈", layout="wide")

PRODUCT_TYPE = "USDT-FUTURES"
MARGIN_COIN = "USDT"

API_KEY = st.secrets["bitget"]["api_key"]
API_SECRET = st.secrets["bitget"]["api_secret"]
PASSPHRASE = st.secrets["bitget"]["passphrase"]

BASE_URL = "https://api.bitget.com"
REFRESH_INTERVAL_SEC = 15

# ================= HELPERS =================
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
    url = f"{BASE_URL}{path}?{urlencode(params)}" if params else f"{BASE_URL}{path}"
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
    return (res.get("data") or [], res) if res.get("code") == "00000" else ([], res)

def fetch_account():
    params = {"productType": PRODUCT_TYPE, "marginCoin": MARGIN_COIN}
    res = _private_get("/api/v2/mix/account/accounts", params)
    if res.get("code") != "00000":
        return None, res
    arr = res.get("data") or []
    return next((a for a in arr if a.get("marginCoin") == MARGIN_COIN), None), res

# ================= FETCH DATA =================
positions, _ = fetch_positions()
account, _ = fetch_account()

def fnum(v):
    try:
        return float(v)
    except:
        return 0.0

available   = fnum(account.get("available")) if account else 0.0
locked      = fnum(account.get("locked")) if account else 0.0
margin_size = fnum(account.get("marginSize")) if account else 0.0

# equity
if account and account.get("usdtEquity"):
    total_equity = fnum(account.get("usdtEquity"))
elif account and account.get("equity"):
    total_equity = fnum(account.get("equity"))
else:
    total_equity = available + locked + margin_size

withdrawable_pct = (available / total_equity * 100.0) if total_equity > 0 else 0.0
margin_usage_pct = (margin_size / total_equity * 100.0) if total_equity > 0 else 0.0

# aggregate pos metrics
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
    if liq_price:
        dist_pct = abs((mark_price - liq_price) / liq_price) * 100.0
        if nearest_liq_pct is None or dist_pct < nearest_liq_pct:
            nearest_liq_pct = dist_pct

# derived display numbers
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

long_exposure_pct  = (long_value  / total_position_value * 100.0) if total_position_value > 0 else 0.0
short_exposure_pct = (short_value / total_position_value * 100.0) if total_position_value > 0 else 0.0

unrealized_is_profit = unrealized_total_pnl >= 0
pnl_color = "#4ade80" if unrealized_is_profit else "#f87171"
roe_pct = (unrealized_total_pnl / total_equity * 100.0) if total_equity > 0 else 0.0
roe_color = "#4ade80" if roe_pct >= 0 else "#f87171"
arrow_icon = "↑" if unrealized_is_profit else "↓"

positions_count = len(positions)

# ================= PNL HISTORY (CHART) =================
if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = []

st.session_state.pnl_history.append({
    "ts": datetime.now().strftime("%H:%M:%S"),
    "pnl": unrealized_total_pnl,
})

st.session_state.pnl_history = st.session_state.pnl_history[-200:]
chart_df = pd.DataFrame(st.session_state.pnl_history)

# ================= STYLE =================
CARD_BG      = "#1a1f27"        # darker card background
CARD_BORDER  = "#2a303a"
BAR_BG       = "#2f343b"
TEXT_MAIN    = "#f8fafc"
TEXT_SUB     = "#9ca3af"
GOOD_COLOR   = "#4ade80"
BAD_COLOR    = "#f87171"
FONT_FAMILY  = "-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif"
RADIUS       = "10px"
SHADOW       = "0 20px 40px rgba(0,0,0,0.8)"

# helper to render safe HTML
def render_html(block: str):
    clean = dedent(block).lstrip()
    st.markdown(clean, unsafe_allow_html=True)

# ================= KPI TOP BAR =================
# compact summary card above main card

top_card_html = f"""
<div style='background:{CARD_BG};border:1px solid {CARD_BORDER};border-radius:{RADIUS};
            padding:12px 16px;margin-bottom:12px;box-shadow:{SHADOW};
            font-family:{FONT_FAMILY};font-size:0.8rem;display:flex;
            align-items:flex-start;justify-content:space-between;'>

    <div style='display:flex;flex-wrap:wrap;row-gap:12px;column-gap:32px;'>
        <div style='color:{TEXT_SUB};min-width:120px;'>
            <div style='font-size:0.75rem;'>Total Value</div>
            <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${total_equity:,.2f}</div>
            <div style='font-size:0.7rem;color:{TEXT_SUB};'>Perp ${total_equity:,.2f}</div>
        </div>

        <div style='color:{TEXT_SUB};min-width:120px;'>
            <div style='font-size:0.75rem;'>Withdrawable
                <span style='color:{GOOD_COLOR};'>{withdrawable_pct:.2f}%</span>
            </div>
            <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${available:,.2f}</div>
        </div>

        <div style='color:{TEXT_SUB};min-width:120px;'>
            <div style='font-size:0.75rem;'>Leverage
                <span style='background:#7f1d1d;color:#fff;padding:2px 6px;border-radius:6px;
                             font-size:0.7rem;font-weight:600;'>{est_leverage:.2f}x</span>
            </div>
            <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${total_position_value:,.2f}</div>
        </div>
    </div>

    <div style='font-size:0.7rem;color:{TEXT_SUB};white-space:nowrap;'>Manual refresh • {REFRESH_INTERVAL_SEC}s</div>
</div>
"""
render_html(top_card_html)

# ================= MAIN CARD LEFT =================
# Large card matching first screenshot layout

col_left, col_right = st.columns([0.45, 0.55])

with col_left:
    long_pct_width  = f"{long_exposure_pct:.2f}%"
    short_pct_width = f"{short_exposure_pct:.2f}%"

    main_card_html = f"""
    <div style='background:{CARD_BG};border:1px solid {CARD_BORDER};border-radius:{RADIUS};
                box-shadow:{SHADOW};font-family:{FONT_FAMILY};padding:16px 20px;
                font-size:0.8rem;color:{TEXT_SUB};line-height:1.4;'>

        <!-- Perp Equity -->
        <div style='margin-bottom:16px;'>
            <div style='font-size:0.8rem;color:{TEXT_SUB};'>Perp Equity</div>
            <div style='color:{TEXT_MAIN};font-weight:600;font-size:1.4rem;'>${total_equity:,.2f}</div>
            <div style='display:flex;justify-content:space-between;font-size:0.7rem;color:{TEXT_SUB};margin-top:8px;'>
                <div>Margin Usage</div>
                <div>{margin_usage_pct:.2f}%</div>
            </div>
            <div style='width:100%;height:4px;border-radius:2px;background:{BAR_BG};margin-top:4px;'>
                <div style='width:{margin_usage_pct:.2f}%;height:4px;border-radius:2px;
                            background:{GOOD_COLOR};'></div>
            </div>
        </div>

        <!-- Direction Bias -->
        <div style='margin-bottom:16px;'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                <div style='font-size:0.8rem;color:{TEXT_SUB};'>Direction Bias</div>
                <div style='font-size:0.8rem;font-weight:600;color:{bias_color};
                            display:flex;align-items:center;gap:6px;'>
                    <span style='font-size:0.8rem;color:{bias_color};'>{'↗' if bias_label=='LONG' else '↘' if bias_label=='SHORT' else ''}</span>
                    <span>{bias_label}</span>
                </div>
            </div>

            <div style='display:flex;justify-content:space-between;font-size:0.7rem;margin-top:8px;'>
                <div style='color:{TEXT_SUB};'>Long Exposure</div>
                <div style='color:{GOOD_COLOR};'>{long_exposure_pct:.2f}%</div>
            </div>

            <div style='width:100%;height:4px;border-radius:2px;background:{BAR_BG};margin-top:4px;'>
                <div style='width:{long_exposure_pct:.2f}%;height:4px;border-radius:2px;
                            background:{GOOD_COLOR};'></div>
            </div>
        </div>

        <!-- Position Distribution -->
        <div style='margin-bottom:16px;'>
            <div style='display:flex;justify-content:space-between;font-size:0.7rem;margin-bottom:8px;'>
                <div style='display:flex;align-items:center;gap:6px;'>
                    <span style='width:6px;height:6px;border-radius:999px;background:{GOOD_COLOR};display:inline-block;'></span>
                    <span style='color:{TEXT_SUB};'>{long_exposure_pct:.2f}%</span>
                    <span style='width:6px;height:6px;border-radius:999px;background:{BAD_COLOR};display:inline-block;margin-left:12px;'></span>
                    <span style='color:{TEXT_SUB};'>{short_exposure_pct:.2f}%</span>
                </div>
                <div style='font-size:0.7rem;color:{TEXT_SUB};'>Position Distribution</div>
            </div>

            <div style='width:100%;display:flex;border-radius:6px;overflow:hidden;
                        background:linear-gradient(to right,#0f3a2e 0%,#3b1f2f 100%);
                        border:1px solid {CARD_BORDER};font-size:0.7rem;color:{TEXT_MAIN};'>
                <div style='flex:0 0 {long_pct_width};min-width:40px;background:rgba(16,83,60,0.6);
                            color:{GOOD_COLOR};text-align:center;padding:8px 4px;font-weight:600;'>
                    {long_exposure_pct:.2f}%
                </div>
                <div style='flex:1;background:rgba(83,16,32,0.4);text-align:center;padding:8px 4px;
                            font-weight:600;color:{BAD_COLOR};'>
                    {total_position_value:,.2f}
                </div>
            </div>
        </div>

        <!-- Unrealized PnL -->
        <div>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                <div style='font-size:0.8rem;color:{TEXT_SUB};'>Unrealized PnL</div>
                <div style='font-size:0.8rem;font-weight:600;color:{roe_color};'>
                    {narrow_icon} {roe_pct:.2f}% ROE
                </div>
            </div>
            <div style='color:{pnl_color};font-weight:600;font-size:1.1rem;margin-top:8px;'>
                ${unrealized_total_pnl:,.2f}
            </div>
        </div>
    </div>
    """
    render_html(main_card_html)

with col_right:
    st.line_chart(chart_df, x="ts", y="pnl", height=240)

# ================= POSITIONS TABLE =================
pos_card_html = f"""
<div style='background:{CARD_BG};border:1px solid {CARD_BORDER};border-radius:{RADIUS};
            box-shadow:{SHADOW};font-family:{FONT_FAMILY};padding:12px 16px;
            font-size:0.8rem;color:{TEXT_SUB};margin-top:16px;'>
    Positions: {positions_count} | Total: ${total_position_value:,.2f}
</div>
"""
render_html(pos_card_html)

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
    f"""
    <div style='font-size:0.7rem;color:{TEXT_SUB};margin-top:8px;font-family:{FONT_FAMILY};'>
        Last update: {datetime.now().strftime('%H:%M:%S')} • refresh every {REFRESH_INTERVAL_SEC}s
    </div>
    """
)
