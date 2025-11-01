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

# --- Secrets (streamlit cloud에 저장된 값 사용)
API_KEY = st.secrets["bitget"]["api_key"]
API_SECRET = st.secrets["bitget"]["api_secret"]
PASSPHRASE = st.secrets["bitget"]["passphrase"]

BASE_URL = "https://api.bitget.com"

REFRESH_INTERVAL_SEC = 15  # manual refresh target interval

# ======================================
# Bitget API helpers
# ======================================
def _timestamp_ms():
    return str(int(time.time() * 1000))

def _sign(timestamp_ms, method, path, query_params, body, secret_key):
    method_up = method.upper()
    if body is None:
        body = ""
    if query_params:
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
    ts = _timestamp_ms()
    method = "GET"
    body = ""

    signature = _sign(ts, method, path, params, body, API_SECRET)

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
    r = requests.get(url, headers=headers)
    return r.json()

def fetch_positions():
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
    params = {
        "productType": PRODUCT_TYPE,
        "marginCoin": MARGIN_COIN,
    }
    res = _private_get("/api/v2/mix/account/accounts", params)
    if res.get("code") != "00000":
        return None, res
    arr = res.get("data") or []
    acct = None
    for a in arr:
        if a.get("marginCoin") == MARGIN_COIN:
            acct = a
            break
    return acct, res

# ======================================
# Fetch + derive dashboard metrics
# ======================================
positions, raw_pos = fetch_positions()
account, raw_acct = fetch_account()

def fnum(v):
    try:
        return float(v)
    except:
        return 0.0

# account metrics
available     = fnum(account.get("available")) if account else 0.0
locked        = fnum(account.get("locked")) if account else 0.0
margin_size   = fnum(account.get("marginSize")) if account else 0.0

# total_equity 추정
if account and "usdtEquity" in account:
    total_equity = fnum(account.get("usdtEquity"))
elif account and "equity" in account:
    total_equity = fnum(account.get("equity"))
else:
    total_equity = available + locked + margin_size

withdrawable_pct = (available / total_equity * 100.0) if total_equity > 0 else 0.0

total_position_value = 0.0
long_value = 0.0
short_value = 0.0
unrealized_total_pnl = 0.0
nearest_liq_pct = None  # % distance to nearest liq

for p in positions:
    lev = fnum(p.get("leverage", 0.0))
    mg  = fnum(p.get("marginSize", 0.0))

    # notionals ~= marginSize * leverage
    pos_val = mg * lev
    total_position_value += pos_val

    side = (p.get("holdSide","") or "").lower()
    if side == "long":
        long_value += pos_val
    elif side == "short":
        short_value += pos_val

    upnl = fnum(p.get("unrealizedPL",0.0))
    unrealized_total_pnl += upnl

    mark_price = fnum(p.get("markPrice"))
    liq_price  = fnum(p.get("liquidationPrice"))
    if liq_price != 0:
        dist_pct = abs((mark_price - liq_price) / liq_price) * 100.0
        if nearest_liq_pct is None or dist_pct < nearest_liq_pct:
            nearest_liq_pct = dist_pct

# est leverage
est_leverage = (total_position_value / total_equity) if total_equity > 0 else 0.0

# Bias
if long_value > short_value:
    bias_label = "LONG"
    bias_color = "#4ade80"
elif short_value > long_value:
    bias_label = "SHORT"
    bias_color = "#f87171"
else:
    bias_label = "FLAT"
    bias_color = "#94a3b8"

# PnL color
pnl_color = "#4ade80" if unrealized_total_pnl >= 0 else "#f87171"

# Liq buffer text/color
if nearest_liq_pct is None:
    liq_text = "n/a"
    liq_color = "#94a3b8"
else:
    liq_text = f"{nearest_liq_pct:.2f}% to nearest liq"
    liq_color = "#4ade80" if nearest_liq_pct > 30 else "#f87171"

# pos counts
positions_count = len(positions)
if positions_count > 0:
    longs  = sum(1 for p in positions if (p.get("holdSide","") or "").lower()=="long")
    shorts = sum(1 for p in positions if (p.get("holdSide","") or "").lower()=="short")
    pos_long_pct = (longs/positions_count)*100.0
    pos_short_pct = (shorts/positions_count)*100.0
else:
    pos_long_pct = 0.0
    pos_short_pct = 0.0

roe_pct = (unrealized_total_pnl / total_equity * 100.0) if total_equity > 0 else 0.0

# ======================================
# Session State -> PnL history
# ======================================
if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = []

st.session_state.pnl_history.append({
    "ts": datetime.now().strftime("%H:%M:%S"),
    "pnl": unrealized_total_pnl
})

MAX_POINTS = 200
st.session_state.pnl_history = st.session_state.pnl_history[-MAX_POINTS:]

chart_x = [pt["ts"] for pt in st.session_state.pnl_history]
chart_y = [pt["pnl"] for pt in st.session_state.pnl_history]

chart_df = pd.DataFrame({
    "time": chart_x,
    "PnL": chart_y,
})

# ======================================
# RENDER: KPI BAR (inline style로 margin/padding 포함)
# ======================================
st.markdown(
    f"""
<div style="
    display:flex;
    flex-wrap:wrap;
    justify-content:space-between;
    background-color:#1e2538;
    border:1px solid rgba(148,163,184,0.2);
    border-radius:12px;
    padding:16px 20px;
    margin-bottom:16px;
    box-shadow:0 24px 48px rgba(0,0,0,0.6);
    font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
    font-size:0.8rem;
    color:#94a3b8;
">
    <div style="display:flex;flex-wrap:wrap;gap:24px;">

        <div class="kpi-block" style="display:flex;flex-direction:column;min-width:140px;">
            <div class="kpi-label" style="font-size:0.75rem;color:#94a3b8;margin-bottom:2px;">Total Value</div>
            <div class="kpi-value" style="font-size:1rem;line-height:1.3;color:#f8fafc;font-weight:600;">
                ${total_equity:,.2f}
            </div>
            <div class="kpi-sub" style="font-size:0.7rem;color:#94a3b8;">
                Perp ${total_equity:,.2f} • Spot n/a
            </div>
        </div>

        <div class="kpi-block" style="display:flex;flex-direction:column;min-width:140px;">
            <div class="kpi-label" style="font-size:0.75rem;color:#94a3b8;margin-bottom:2px;">
                Withdrawable
                <span style="color:#4ade80;">{withdrawable_pct:.2f}%</span>
            </div>
            <div class="kpi-value" style="font-size:1rem;line-height:1.3;color:#f8fafc;font-weight:600;">
                ${available:,.2f}
            </div>
            <div class="kpi-sub" style="font-size:0.7rem;color:#94a3b8;">Free margin available</div>
        </div>

        <div class="kpi-block" style="display:flex;flex-direction:column;min-width:140px;">
            <div class="kpi-label" style="font-size:0.75rem;color:#94a3b8;margin-bottom:2px;">
                Leverage
                <span style="background:#7f1d1d;color:#fff;padding:2px 6px;border-radius:6px;font-size:0.7rem;font-weight:600;">
                    {est_leverage:.2f}x
                </span>
            </div>
            <div class="kpi-value" style="font-size:1rem;line-height:1.3;color:#f8fafc;font-weight:600;">
                ${total_position_value:,.2f}
            </div>
            <div class="kpi-sub" style="font-size:0.7rem;color:#94a3b8;">Total position value</div>
        </div>

    </div>

    <div style="text-align:right;font-size:0.7rem;color:#94a3b8;min-width:150px;">
        <div style="font-size:0.7rem;color:#94a3b8;">Manual refresh • target {REFRESH_INTERVAL_SEC}s interval</div>
        <div style="font-size:0.75rem;color:#10b981;font-weight:500;">Support us</div>
    </div>
</div>
    """,
    unsafe_allow_html=True
)

# ======================================
# RENDER: MAIN PANEL (equity stats + chart in one flex card)
# ======================================
st.markdown(
    """
<div style="
    background-color:#1e2538;
    border:1px solid rgba(148,163,184,0.2);
    border-radius:12px;
    box-shadow:0 24px 48px rgba(0,0,0,0.6);
    padding:16px 20px;
    margin-bottom:16px;
    display:flex;
    flex-wrap:wrap;
    justify-content:space-between;
    gap:20px;
    align-items:flex-start;
    font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
    color:#f8fafc;
">
    """,
    unsafe_allow_html=True
)

# LEFT: equity / risk info
st.markdown(
    f"""
    <div style="flex:0.35;min-width:260px;">
        <div style="font-size:0.8rem;font-weight:500;color:#94a3b8;margin-bottom:4px;">Perp Equity</div>
        <div style="font-size:1.4rem;font-weight:600;color:#f8fafc;margin-bottom:12px;">${total_equity:,.2f}</div>

        <div style="font-size:0.75rem;color:#94a3b8;margin-bottom:6px;">Leverage Utilization</div>
        <div style="width:160px;height:6px;background-color:#334155;border-radius:999px;overflow:hidden;margin-bottom:8px;">
            <div style="height:100%;background:linear-gradient(90deg,#10b981,#059669);width:{min(est_leverage*10,100)}%;"></div>
        </div>
        <div style="font-size:0.7rem;color:#94a3b8;margin-bottom:16px;">est. leverage {est_leverage:.2f}x</div>

        <div style="font-size:0.75rem;color:#94a3b8;margin-bottom:4px;">Direction Bias</div>
        <div style="font-size:0.9rem;font-weight:600;color:{bias_color};margin-bottom:16px;">{bias_label}</div>

        <div style="font-size:0.75rem;color:#94a3b8;margin-bottom:4px;">Unrealized PnL</div>
        <div style="font-size:1rem;font-weight:600;color:{pnl_color};margin-bottom:4px;">${unrealized_total_pnl:,.2f}</div>
        <div style="font-size:0.7rem;color:#94a3b8;margin-bottom:16px;">{roe_pct:.2f}% ROE</div>

        <div style="font-size:0.75rem;color:#94a3b8;margin-bottom:4px;">Liq buffer</div>
        <div style="font-size:1rem;font-weight:600;color:{liq_color};margin-bottom:4px;">{liq_text}</div>
        <div style="font-size:0.7rem;color:#94a3b8;margin-bottom:0;">nearest distance to forced close</div>
    </div>
    """,
    unsafe_allow_html=True
)

# RIGHT: chart + tabs UI
st.markdown(
    """
    <div style="flex:0.6;min-width:400px;">
        <div style="display:flex;justify-content:space-between;flex-wrap:wrap;margin-bottom:8px;font-size:0.7rem;">
            <div style="display:flex;gap:8px;flex-wrap:wrap;font-size:0.7rem;">
                <div style="background:#0f3;padding:4px 8px;border-radius:6px;color:#000;font-weight:600;">24H</div>
                <div style="background:#1e2538;border:1px solid #334155;padding:4px 8px;border-radius:6px;color:#94a3b8;">1W</div>
                <div style="background:#1e2538;border:1px solid #334155;padding:4px 8px;border-radius:6px;color:#94a3b8;">1M</div>
                <div style="background:#1e2538;border:1px solid #334155;padding:4px 8px;border-radius:6px;color:#94a3b8;">All</div>
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;font-size:0.7rem;">
                <div style="background:#0f3;padding:4px 8px;border-radius:6px;color:#000;font-weight:600;">Combined</div>
                <div style="background:#1e2538;border:1px solid #334155;padding:4px 8px;border-radius:6px;color:#94a3b8;">Perp Only</div>
                <div style="background:#1e2538;border:1px solid #334155;padding:4px 8px;border-radius:6px;color:#94a3b8;">PnL</div>
                <div style="background:#1e2538;border:1px solid #334155;padding:4px 8px;border-radius:6px;color:#94a3b8;">Account Value</div>
            </div>
        </div>
    """,
    unsafe_allow_html=True
)

st.line_chart(
    data=chart_df,
    x="time",
    y="PnL",
    height=220,
)

st.markdown(
    f"""
        <div style="display:flex;justify-content:space-between;flex-wrap:wrap;margin-top:4px;font-size:0.8rem;color:{pnl_color};">
            <div>24H PnL (Session)</div>
            <div style="font-weight:600;">${unrealized_total_pnl:,.2f}</div>
        </div>
    </div> <!-- right col -->
</div> <!-- main card flex wrapper -->
    """,
    unsafe_allow_html=True
)

# ======================================
# POSITIONS TABLE
# ======================================
st.markdown(
    f"""
    <div style="
        background-color:#1e2538;
        border:1px solid rgba(148,163,184,0.2);
        border-radius:12px 12px 0 0;
        border-bottom:0;
        padding:12px 20px;
        font-size:0.8rem;
        color:#94a3b8;
        box-shadow:0 24px 48px rgba(0,0,0,0.6);
    ">
        <div style=\"display:flex;flex-wrap:wrap;gap:16px;row-gap:4px;color:#94a3b8;\">
            <div>Positions <span style=\"color:#f8fafc;font-weight:600;font-size:0.8rem;\">{positions_count}</span></div>
            <div>Total <span style=\"color:#f8fafc;font-weight:600;font-size:0.8rem;\">${total_position_value:,.0f}</span></div>
            <div>Long <span style=\"color:#f8fafc;font-weight:600;font-size:0.8rem;\">{pos_long_pct:.1f}%</span></div>
            <div>Short <span style=\"color:#f8fafc;font-weight:600;font-size:0.8rem;\">{pos_short_pct:.1f}%</span></div>
            <div>U PnL <span style=\"color:#f8fafc;font-weight:600;font-size:0.8rem;\">${unrealized_total_pnl:,.2f}</span></div>
        </div>
        <div style=\"margin-top:8px;display:flex;flex-wrap:wrap;gap:12px;font-size:0.7rem;\">
            <div style=\"background:#10b9811a;border:1px solid #10b98133;padding:4px 8px;border-radius:6px;color:#10b981;font-weight:500;\">Asset Positions</div>
            <div style=\"background:#1e2538;border:1px solid #334155;padding:4px 8px;border-radius:6px;color:#94a3b8;\">Open Orders</div>
            <div style=\"background:#1e2538;border:1px solid #334155;padding:4px 8px;border-radius:6px;color:#94a3b8;\">Recent Fills</div>
            <div style=\"background:#1e2538;border:1px solid #334155;padding:4px 8px;border-radius:6px;color:#94a3b8;\">Completed Trades</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

table_rows = []
for p in positions:
    lev = fnum(p.get("leverage",0.0))
    mg  = fnum(p.get("marginSize",0.0))
    mark_price = fnum(p.get("markPrice"))
    liq_price  = fnum(p.get("liquidationPrice"))

    dist_to_liq = ""
    if liq_price != 0:
        dist_pct = abs((mark_price - liq_price) / liq_price) * 100.0
        dist_to_liq = f"{dist_pct:.2f}%"

    table_rows.append({
        "Asset": p.get("symbol"),
        "Type": (p.get("holdSide","") or "").upper(),
        "Lev": f"{lev}x",
        "Position Value": f"{mg*lev:,.2f}",
        "Unrealized PnL": f"{fnum(p.get('unrealizedPL',0.0)):,.2f}",
        "Entry Price": p.get("openPriceAvg") or p.get("averageOpenPrice"),
        "Current Price": p.get("markPrice"),
        "Liq. Price": p.get("liquidationPrice"),
        "Liq Buffer": dist_to_liq,
        "Margin Used": p.get("marginSize"),
    })

st.markdown(
    """
    <div style="
        background-color:#1e2538;
        border:1px solid rgba(148,163,184,0.2);
        border-radius:0 0 12px 12px;
        border-top:0;
        padding:12px 20px 20px;
        box-shadow:0 24px 48px rgba(0,0,0,0.6);
    ">
    """,
    unsafe_allow_html=True
)

st.dataframe(table_rows, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# footer
st.caption(
    f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  •  Manual refresh • target {REFRESH_INTERVAL_SEC}s interval"
)
