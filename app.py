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

REFRESH_INTERVAL_SEC = 15  # 우리가 목표로 하는 새로고침 주기 (수동 rerun 기준)

# ======================================
# STYLE
# ======================================
st.markdown(
    """
    <style>
    body, .main {
        background-color: #0f172a;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    }

    .kpi-bar {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        background-color: #1e2538;
        border: 1px solid rgba(148,163,184,0.2);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 24px 48px rgba(0,0,0,0.6);
    }

    .kpi-left {
        display: flex;
        flex-wrap: wrap;
        gap: 24px;
    }

    .kpi-block {
        display: flex;
        flex-direction: column;
        font-size: 0.8rem;
        color: #94a3b8;
        min-width: 140px;
    }

    .kpi-label {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-bottom: 2px;
    }
    .kpi-value {
        font-size: 1rem;
        line-height: 1.3;
        color: #f8fafc;
        font-weight: 600;
    }
    .kpi-sub {
        font-size: 0.7rem;
        color: #94a3b8;
    }

    .kpi-right {
        text-align: right;
        font-size: 0.7rem;
        color: #94a3b8;
        min-width: 150px;
    }
    .kpi-next-refresh {
        font-size: 0.7rem;
        color: #94a3b8;
    }
    .kpi-support {
        font-size: 0.75rem;
        color: #10b981;
        font-weight: 500;
    }

    .panel-wrapper {
        background-color: #1e2538;
        border: 1px solid rgba(148,163,184,0.2);
        border-radius: 12px;
        box-shadow: 0 24px 48px rgba(0,0,0,0.6);
        padding: 16px 20px;
        margin-bottom: 16px;
    }

    .equity-block {
        min-width: 260px;
        color: #f8fafc;
        font-size: 1rem;
        font-weight: 600;
        background-color: #1e2538;
        border: 1px solid rgba(148,163,184,0.2);
        border-radius: 12px;
        box-shadow: 0 24px 48px rgba(0,0,0,0.6);
        padding: 16px 20px;
        margin-bottom: 16px;
    }
    .equity-title {
        font-size: 0.8rem;
        font-weight: 500;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .equity-value {
        font-size: 1.4rem;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 8px;
    }

    .metric-bar-label {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .metric-bar-value {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-bar-bg {
        width: 160px;
        height: 6px;
        background-color: #334155;
        border-radius: 999px;
        overflow: hidden;
        margin-bottom: 8px;
    }
    .metric-bar-fill {
        height: 100%;
        background: linear-gradient(90deg,#10b981,#059669);
    }

    .risk-label {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .risk-value-number {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .risk-sub {
        font-size: 0.7rem;
        color: #94a3b8;
        margin-bottom: 8px;
    }

    .positions-header-bar {
        background-color: #1e2538;
        border: 1px solid rgba(148,163,184,0.2);
        border-radius: 12px 12px 0 0;
        border-bottom: 0;
        padding: 12px 20px;
        font-size: 0.8rem;
        color: #94a3b8;
    }
    .positions-header-topline {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        row-gap: 4px;
        color: #94a3b8;
    }
    .positions-header-topline span {
        color: #f8fafc;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .positions-body {
        background-color: #1e2538;
        border: 1px solid rgba(148,163,184,0.2);
        border-radius: 0 0 12px 12px;
        border-top: 0;
        padding: 12px 20px 20px;
        box-shadow: 0 24px 48px rgba(0,0,0,0.6);
    }

    /* Streamlit dataframe override */
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        color: #e2e8f0 !important;
        background-color: #1e2538 !important;
        border-color: #334155 !important;
        font-size: 0.8rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
# Derive dashboard metrics
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

# total equity
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

# For liq distance calc
nearest_liq_pct = None  # % distance to nearest liq (lower is scarier)

for p in positions:
    lev = fnum(p.get("leverage", 0.0))
    mg  = fnum(p.get("marginSize", 0.0))
    pos_val = mg * lev  # 명목 포지션 가치 근사
    total_position_value += pos_val

    side = (p.get("holdSide","") or "").lower()
    if side == "long":
        long_value += pos_val
    elif side == "short":
        short_value += pos_val

    upnl = fnum(p.get("unrealizedPL",0.0))
    unrealized_total_pnl += upnl

    # liquidation distance 계산
    mark_price = fnum(p.get("markPrice"))
    liq_price  = fnum(p.get("liquidationPrice"))
    if liq_price != 0:
        dist_pct = abs((mark_price - liq_price) / liq_price) * 100.0
        if nearest_liq_pct is None or dist_pct < nearest_liq_pct:
            nearest_liq_pct = dist_pct

# est leverage
est_leverage = (total_position_value / total_equity) if total_equity > 0 else 0.0

# Bias 계산
if long_value > short_value:
    bias_label = "LONG"
    bias_color = "#4ade80"
elif short_value > long_value:
    bias_label = "SHORT"
    bias_color = "#f87171"
else:
    bias_label = "FLAT"
    bias_color = "#94a3b8"

# PnL 색
pnl_color = "#4ade80" if unrealized_total_pnl >= 0 else "#f87171"

# long/short 포지션 개수 비중
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

# 너무 길어지는 거 방지
MAX_POINTS = 200
st.session_state.pnl_history = st.session_state.pnl_history[-MAX_POINTS:]

chart_x = [pt["ts"] for pt in st.session_state.pnl_history]
chart_y = [pt["pnl"] for pt in st.session_state.pnl_history]

# ======================================
# RENDER: KPI BAR (상단)
# ======================================
st.markdown(
    f"""
<div class="kpi-bar">
<div class="kpi-left">

<div class="kpi-block">
<div class="kpi-label">Total Value</div>
<div class="kpi-value">${total_equity:,.2f}</div>
<div class="kpi-sub">Perp ${total_equity:,.2f} • Spot n/a</div>
</div>

<div class="kpi-block">
<div class="kpi-label">Withdrawable <span style="color:#4ade80;">{withdrawable_pct:.2f}%</span></div>
<div class="kpi-value">${available:,.2f}</div>
<div class="kpi-sub">Free margin available</div>
</div>

<div class="kpi-block">
<div class="kpi-label">
Leverage
<span style="background:#7f1d1d;color:#fff;padding:2px 6px;border-radius:6px;font-size:0.7rem;font-weight:600;">
{est_leverage:.2f}x
</span>
</div>
<div class="kpi-value">${total_position_value:,.2f}</div>
<div class="kpi-sub">Total position value</div>
</div>

</div>

<div class="kpi-right">
<div class="kpi-next-refresh">Manual refresh • target {REFRESH_INTERVAL_SEC}s interval</div>
<div class="kpi-support">Support us</div>
</div>
</div>
    """,
    unsafe_allow_html=True
)

# ======================================
# RENDER MAIN PANEL (좌: 계좌상태 / 우: 차트)
# ======================================
col_main_left, col_main_right = st.columns([0.4,0.6])

with col_main_left:
    liq_text = "n/a"
    if nearest_liq_pct is not None:
        liq_text = f"{nearest_liq_pct:.2f}% to nearest liq"

st.markdown(
f"""
<div class="equity-block">

<div class="equity-title">Perp Equity</div>
<div class="equity-value">${total_equity:,.2f}</div>

<div class="metric-bar-label">Leverage Utilization</div>
<div class="metric-bar-bg">
<div class="metric-bar-fill" style="width:{min(est_leverage*10,100)}%;"></div>
</div>
<div class="risk-sub" style="margin-bottom:12px;">
est. leverage {est_leverage:.2f}x
</div>

<div class="metric-bar-label">Direction Bias</div>
<div class="metric-bar-value" style="color:{bias_color};">{bias_label}</div>

<div class="risk-label" style="margin-top:12px;">Unrealized PnL</div>
<div class="risk-value-number" style="color:{pnl_color};">
${unrealized_total_pnl:,.2f}
</div>
<div class="risk-sub">
{roe_pct:.2f}% ROE
</div>

<div class="risk-label">Liq buffer</div>
<div class="risk-value-number" style="color:#94a3b8;">
{liq_text}
</div>
<div class="risk-sub">
nearest distance to forced close
</div>

</div>
""",
unsafe_allow_html=True
    )

with col_main_right:
    st.markdown(
        """
        <div class="panel-wrapper">
            <div style="display:flex;justify-content:space-between;flex-wrap:wrap;margin-bottom:8px;">
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

    chart_df = pd.DataFrame({
        "time": chart_x,
        "PnL": chart_y,
    })

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
        </div>
        """,
        unsafe_allow_html=True
    )

# ======================================
# POSITIONS TABLE
# ======================================
st.markdown(
    f"""
    <div class="positions-header-bar">
        <div class="positions-header-topline">
            <div>Positions <span>{positions_count}</span></div>
            <div>Total <span>${total_position_value:,.0f}</span></div>
            <div>Long <span>{pos_long_pct:.1f}%</span></div>
            <div>Short <span>{pos_short_pct:.1f}%</span></div>
            <div>U PnL <span>${unrealized_total_pnl:,.2f}</span></div>
        </div>
        <div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:12px;font-size:0.7rem;">
            <div style="background:#10b9811a;border:1px solid #10b98133;padding:4px 8px;border-radius:6px;color:#10b981;font-weight:500;">Asset Positions</div>
            <div style="background:#1e2538;border:1px solid #334155;padding:4px 8px;border-radius:6px;color:#94a3b8;">Open Orders</div>
            <div style="background:#1e2538;border:1px solid #334155;padding:4px 8px;border-radius:6px;color:#94a3b8;">Recent Fills</div>
            <div style="background:#1e2538;border:1px solid #334155;padding:4px 8px;border-radius:6px;color:#94a3b8;">Completed Trades</div>
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

st.markdown('<div class="positions-body">', unsafe_allow_html=True)
st.dataframe(table_rows, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# footer
st.caption(
    f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  •  Manual refresh • target {REFRESH_INTERVAL_SEC}s interval"
)



