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

st.set_page_config(
    page_title="Perp Dashboard",
    page_icon="📈",
    layout="wide",
)

PRODUCT_TYPE = "USDT-FUTURES"
MARGIN_COIN = "USDT"

# Bitget API keys are expected in .streamlit/secrets.toml or Streamlit Cloud secrets
API_KEY = st.secrets["bitget"]["api_key"]
API_SECRET = st.secrets["bitget"]["api_secret"]
PASSPHRASE = st.secrets["bitget"]["passphrase"]

BASE_URL = "https://api.bitget.com"
REFRESH_INTERVAL_SEC = 15  # just used for the UI label


# ======================================
# Bitget API helpers
# ======================================

def _timestamp_ms() -> str:
    """Return current epoch milliseconds as string (Bitget wants ms precision)."""
    return str(int(time.time() * 1000))


def _sign(timestamp_ms, method, path, query_params, body, secret_key):
    """
    Bitget signature format:
    sign_target = timestamp + method + path + (optional '?query') + body
    HMAC-SHA256 -> base64
    """
    if body is None:
        body = ""
    method_up = method.upper()

    if query_params:
        # urlencode dict to query string like "a=1&b=2"
        query_str = urlencode(query_params)
        sign_target = f"{timestamp_ms}{method_up}{path}?{query_str}{body}"
    else:
        sign_target = f"{timestamp_ms}{method_up}{path}{body}"

    mac = hmac.new(
        secret_key.encode("utf-8"),
        sign_target.encode("utf-8"),
        digestmod=hashlib.sha256,
    )
    return base64.b64encode(mac.digest()).decode()


def _private_get(path, params=None):
    """Signed GET request to Bitget private endpoints."""
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
    """
    Returns:
        (positions_list, raw_response)
    Bitget returns list of open positions for productType/marginCoin.
    """
    params = {
        "productType": PRODUCT_TYPE,
        "marginCoin": MARGIN_COIN,
    }
    res = _private_get("/api/v2/mix/position/all-position", params)
    if res.get("code") != "00000":
        return [], res
    data = res.get("data") or []
    return data, res


def fetch_account():
    """
    Returns:
        (account_info_for_marginCoin, raw_response)

    Bitget returns multiple accounts (one per marginCoin).
    We pick the one that matches our MARGIN_COIN (USDT).
    """
    params = {
        "productType": PRODUCT_TYPE,
        "marginCoin": MARGIN_COIN,
    }
    res = _private_get("/api/v2/mix/account/accounts", params)
    if res.get("code") != "00000":
        return None, res

    arr = res.get("data") or []
    acct = next((a for a in arr if a.get("marginCoin") == MARGIN_COIN), None)
    return acct, res


# ======================================
# FETCH DATA & DERIVED METRICS
# ======================================

positions, _raw_pos = fetch_positions()
account, _raw_acct = fetch_account()

def fnum(v):
    """safe float() with fallback 0.0"""
    try:
        return float(v)
    except:
        return 0.0

# pull account-level numbers
available   = fnum(account.get("available")) if account else 0.0
locked      = fnum(account.get("locked")) if account else 0.0
margin_size = fnum(account.get("marginSize")) if account else 0.0

# total_equity (USDT equity, fallback)
if account and "usdtEquity" in account:
    total_equity = fnum(account["usdtEquity"])
elif account and "equity" in account:
    total_equity = fnum(account["equity"])
else:
    total_equity = available + locked + margin_size

withdrawable_pct = (available / total_equity * 100.0) if total_equity > 0 else 0.0

# walk positions to compute agg metrics
total_position_value = 0.0
long_value = 0.0
short_value = 0.0
unrealized_total_pnl = 0.0
nearest_liq_pct = None  # closest liquidation distance %

for p in positions:
    lev = fnum(p.get("leverage", 0.0))
    mg  = fnum(p.get("marginSize", 0.0))
    notional_est = mg * lev  # approx pos size ~= margin * leverage
    total_position_value += notional_est

    side = (p.get("holdSide", "") or "").lower()
    if side == "long":
        long_value += notional_est
    elif side == "short":
        short_value += notional_est

    unrealized_total_pnl += fnum(p.get("unrealizedPL", 0.0))

    # compute nearest liq % distance (mark vs liq)
    mark_price = fnum(p.get("markPrice"))
    liq_price  = fnum(p.get("liquidationPrice"))
    if liq_price != 0:
        dist_pct = abs((mark_price - liq_price) / liq_price) * 100.0
        if nearest_liq_pct is None or dist_pct < nearest_liq_pct:
            nearest_liq_pct = dist_pct

# est leverage = total position notional / equity
est_leverage = (total_position_value / total_equity) if total_equity > 0 else 0.0

# Bias coloring
if long_value > short_value:
    bias_label = "LONG"
    bias_color = "#4ade80"  # green
elif short_value > long_value:
    bias_label = "SHORT"
    bias_color = "#f87171"  # red
else:
    bias_label = "FLAT"
    bias_color = "#94a3b8"

# PnL color
pnl_color = "#4ade80" if unrealized_total_pnl >= 0 else "#f87171"

# ROE-ish display
roe_pct = (unrealized_total_pnl / total_equity * 100.0) if total_equity > 0 else 0.0

# liquidation safety label
if nearest_liq_pct is None:
    liq_text = "n/a"
    liq_color = "#94a3b8"
else:
    liq_text  = f"{nearest_liq_pct:.2f}%"
    liq_color = "#4ade80" if nearest_liq_pct > 30 else "#f87171"

# positions summary
positions_count = len(positions)
total_long_pct = 0.0
total_short_pct = 0.0
if positions_count > 0:
    longs  = sum(1 for p in positions if (p.get("holdSide", "") or "").lower() == "long")
    shorts = sum(1 for p in positions if (p.get("holdSide", "") or "").lower() == "short")
    total_long_pct  = (longs / positions_count) * 100.0
    total_short_pct = (shorts / positions_count) * 100.0

# ======================================
# SESSION STATE HISTORY FOR CHART
# ======================================

if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = []

st.session_state.pnl_history.append({
    "ts": datetime.now().strftime("%H:%M:%S"),
    "pnl": unrealized_total_pnl,
})
# keep buffer small-ish
st.session_state.pnl_history = st.session_state.pnl_history[-200:]

chart_df = pd.DataFrame(st.session_state.pnl_history)

# ======================================
# STYLE CONSTANTS
# ======================================

CARD_BG     = "#1e2538"
TEXT_SUB    = "#94a3b8"
TEXT_MAIN   = "#f8fafc"
BORDER      = "rgba(148,163,184,0.2)"
SHADOW      = "0 24px 48px rgba(0,0,0,0.6)"
FONT_FAMILY = "-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif"

# ======================================
# TOP KPI BAR
# ======================================

st.markdown(
    f"""
<div style='display:flex;align-items:flex-start;justify-content:space-between;
            background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;
            padding:12px 16px;margin-bottom:8px;box-shadow:{SHADOW};
            font-family:{FONT_FAMILY};'>

    <div style='display:flex;flex-wrap:wrap;row-gap:8px;column-gap:32px;font-size:0.8rem;'>
        <div style='color:{TEXT_SUB};'>
            <div style='font-size:0.75rem;'>Total Value</div>
            <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>
                ${total_equity:,.2f}
            </div>
            <div style='font-size:0.7rem;color:{TEXT_SUB};'>
                Perp ${total_equity:,.2f}
            </div>
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
""",
    unsafe_allow_html=True,
)

# ======================================
# MID CARD (INFO LEFT + CHART RIGHT)
# single flex card layout
# ======================================

# We render one big <div> styled as a card, with flexbox:
# - left side: equity / bias / pnl text
# - right side: time range pills + (visually attached) chart
# Note: chart itself is a Streamlit block, so it's placed immediately after
# this card but visually belongs to the right side.

st.markdown(
    f"""
<div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;
            padding:16px;box-shadow:{SHADOW};font-family:{FONT_FAMILY};
            margin-bottom:0;  /* chart will come right after, so 0 gap here */'>

    <div style='display:flex;align-items:flex-start;justify-content:space-between;
                column-gap:24px;'>

        <!-- LEFT METRICS -->
        <div style='flex:0.35;color:{TEXT_SUB};font-size:0.8rem;'>
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
        </div>

        <!-- RIGHT HEADER (Time Range Pills) -->
        <div style='flex:0.65;display:flex;flex-direction:column;gap:8px;'>
            <div style='display:flex;gap:8px;justify-content:flex-start;
                        flex-wrap:wrap;font-size:0.7rem;'>
                <div style='background:#0f3;color:#000;font-weight:600;
                            border-radius:6px;padding:4px 8px;'>
                    24H
                </div>
                <div style='background:{CARD_BG};border:1px solid #334155;
                            border-radius:6px;padding:4px 8px;
                            color:{TEXT_SUB};'>
                    1W
                </div>
            </div>
        </div>

    </div> <!-- flex row end -->

</div> <!-- card end -->
""",
    unsafe_allow_html=True,
)

# Now we draw the chart directly under that card.
# Visually this reads as: card header + chart body.
st.line_chart(chart_df, x="ts", y="pnl", height=220)

# Add a tiny spacer after chart so next card isn't glued
st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

# ======================================
# POSITIONS CARD
# ======================================

st.markdown(
    f"""
<div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;
            padding:12px 16px;margin-bottom:12px;box-shadow:{SHADOW};
            font-family:{FONT_FAMILY};'>

    <div style='font-size:0.8rem;color:{TEXT_SUB};margin-bottom:8px;'>
        Positions: {positions_count} | Total: ${total_position_value:,.2f}
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# We'll render the dataframe AFTER that <div>, because st.dataframe is its own block.
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

st.markdown(
    f"""
<div style='font-size:0.7rem;color:{TEXT_SUB};margin-top:8px;'>
    Last update: {datetime.now().strftime("%H:%M:%S")}
    • refresh every {REFRESH_INTERVAL_SEC}s
</div>
""",
    unsafe_allow_html=True,
)
