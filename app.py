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

available = fnum(account.get("available")) if account else 0.0
locked = fnum(account.get("locked")) if account else 0.0
margin_size = fnum(account.get("marginSize")) if account else 0.0

total_equity = fnum(account.get("usdtEquity")) if account and account.get("usdtEquity") else available + locked + margin_size
withdrawable_pct = (available / total_equity * 100.0) if total_equity > 0 else 0.0

total_position_value = 0.0
long_value = 0.0
short_value = 0.0
unrealized_total_pnl = 0.0
nearest_liq_pct = None

for p in positions:
    lev = fnum(p.get("leverage", 0.0))
    mg = fnum(p.get("marginSize", 0.0))
    notional_est = mg * lev
    total_position_value += notional_est

    side = (p.get("holdSide", "") or "").lower()
    if side == "long":
        long_value += notional_est
    elif side == "short":
        short_value += notional_est

    unrealized_total_pnl += fnum(p.get("unrealizedPL", 0.0))

    mark_price = fnum(p.get("markPrice"))
    liq_price = fnum(p.get("liquidationPrice"))
    if liq_price:
        dist_pct = abs((mark_price - liq_price) / liq_price) * 100.0
        if nearest_liq_pct is None or dist_pct < nearest_liq_pct:
            nearest_liq_pct = dist_pct

est_leverage = (total_position_value / total_equity) if total_equity > 0 else 0.0
bias_label, bias_color = ("LONG", "#4ade80") if long_value > short_value else ("SHORT", "#f87171") if short_value > long_value else ("FLAT", "#94a3b8")
pnl_color = "#4ade80" if unrealized_total_pnl >= 0 else "#f87171"
roe_pct = (unrealized_total_pnl / total_equity * 100.0) if total_equity > 0 else 0.0

positions_count = len(positions)

# ================= STYLE =================
CARD_BG, TEXT_SUB, TEXT_MAIN = "#1e2538", "#94a3b8", "#f8fafc"
BORDER, SHADOW = "rgba(148,163,184,0.2)", "0 24px 48px rgba(0,0,0,0.6)"
FONT_FAMILY = "-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif"

def render_html(block: str):
    clean = dedent(block).lstrip()
    st.markdown(clean, unsafe_allow_html=True)

# ================= TOP CARD =================
top_card_html = f"""<div style='background:{CARD_BG};border:1px solid {BORDER};border-radius:8px;padding:12px 16px;margin-bottom:8px;box-shadow:{SHADOW};font-family:{FONT_FAMILY};font-size:0.8rem;display:flex;align-items:flex-start;justify-content:space-between;'>
<div style='display:flex;flex-wrap:wrap;row-gap:8px;column-gap:32px;'>
<div style='color:{TEXT_SUB};'><div style='font-size:0.75rem;'>Total Value</div><div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${total_equity:,.2f}</div><div style='font-size:0.7rem;color:{TEXT_SUB};'>Perp ${total_equity:,.2f}</div></div>
<div style='color:{TEXT_SUB};'><div style='font-size:0.75rem;'>Withdrawable <span style='color:#4ade80;'>{withdrawable_pct:.2f}%</span></div><div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${available:,.2f}</div></div>
<div style='color:{TEXT_SUB};'><div style='font-size:0.75rem;'>Leverage <span style='background:#7f1d1d;color:#fff;padding:2px 6px;border-radius:6px;font-size:0.7rem;font-weight:600;'>{est_leverage:.2f}x</span></div><div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${total_position_value:,.2f}</div></div>
</div><div style='font-size:0.7rem;color:{TEXT_SUB};white-space:nowrap;'>Manual refresh • {REFRESH_INTERVAL_SEC}s</div></div>"""
render_html(top_card_html)

# ================= POSITIONS =================
def format_side_badge(hold_side: str):
    side_up = (hold_side or "").upper()
    if side_up == "LONG":
        bg = "#14532d"
        border = "#22c55e"
        color = "#22c55e"
    elif side_up == "SHORT":
        bg = "#450a0a"
        border = "#f87171"
        color = "#f87171"
    else:
        bg = "#1e2538"
        border = "#94a3b8"
        color = "#94a3b8"
    return f"""
        <span style="
            background:{bg};
            color:{color};
            border:1px solid {border};
            font-size:0.7rem;
            font-weight:600;
            border-radius:4px;
            padding:2px 6px;
            line-height:1;
            display:inline-block;
            min-width:44px;
            text-align:center;
        ">{side_up}</span>
    """

def safe_pct(numerator, denominator):
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100.0

# 테이블 헤더 렌더
table_html = f"""
<div style="
    background:#0f172a;
    border:1px solid {BORDER};
    border-radius:8px;
    box-shadow:{SHADOW};
    font-family:{FONT_FAMILY};
    font-size:0.8rem;
    color:{TEXT_SUB};
    overflow:hidden;
    ">
<div style="
        display:grid;
        grid-template-columns:
            120px   /* Asset */
            80px    /* Type */
            180px   /* Position Value / Size */
            160px   /* Unrealized PnL */
            110px   /* Entry Price */
            110px   /* Current Price */
            110px   /* Liq. Price */
            130px   /* Margin Used */
            110px   /* Funding */
        ;
        column-gap:16px;
        padding:12px 16px;
        border-bottom:1px solid rgba(148,163,184,0.15);
        font-size:0.75rem;
        color:{TEXT_SUB};
        font-weight:500;
    ">
<div>Asset</div>
<div>Type</div>
<div>Position Value / Size <span style="color:#4ade80;">↓</span></div>
<div>Unrealized PnL</div>
<div>Entry Price</div>
<div>Current Price</div>
<div>Liq. Price</div>
<div>Margin Used</div>
<div>Funding</div>
</div>
"""

# 각 포지션 row 렌더
for p in positions:
    symbol = p.get("symbol", "")
    side = (p.get("holdSide") or "").upper()

    lev = fnum(p.get("leverage", 0.0))                 # 레버리지
    mg_usdt = fnum(p.get("marginSize", 0.0))           # 사용 마진 (USDT)
    qty = fnum(p.get("total", 0.0))                    # 보유 수량 (코인 단위: BTC 등)
    entry_price = fnum(p.get("averageOpenPrice", 0.0))
    mark_price = fnum(p.get("markPrice", 0.0))
    liq_price = fnum(p.get("liquidationPrice", 0.0))
    unreal_pl = fnum(p.get("unrealizedPL", 0.0))

    # 포지션 명목가치(대충 size * markPrice). Bitget 응답에 따라 다를 수 있어서
    # leverage * marginSize 로 추정했던 notional을 여기서도 씀
    notional_est = mg_usdt * lev

    # ROE% = PnL / margin (자기 돈 대비 수익률 관점)
    roe_pct = safe_pct(unreal_pl, mg_usdt)

    # 사이드 뱃지
    badge_html = format_side_badge(side)

    # PnL 색상
    if unreal_pl >= 0:
        pnl_color = "#4ade80"
    else:
        pnl_color = "#f87171"

    # Funding 컬럼은 아직 API 안 땡겨오니까 placeholder
    funding_display = "-"

    table_html += f"""
<div style="
        display:grid;
        grid-template-columns:
            120px
            80px
            180px
            160px
            110px
            110px
            110px
            130px
            110px
        ;
        column-gap:16px;
        padding:16px;
        border-bottom:1px solid rgba(148,163,184,0.08);
        color:{TEXT_MAIN};
        font-size:0.8rem;
        line-height:1.4;
        ">
        <!-- Asset -->
<div style="color:{TEXT_MAIN}; font-weight:600;">
<div style="font-size:0.8rem; line-height:1.2;">{symbol}</div>
<div style="font-size:0.7rem; color:{TEXT_SUB}; line-height:1.2;">{lev:.0f}x</div>
</div>

        <!-- Type -->
<div style="display:flex;align-items:flex-start;padding-top:2px;">
            {badge_html}
</div>

        <!-- Position Value / Size -->
<div style="color:{TEXT_MAIN}; font-weight:500;">
<div style="line-height:1.2;">${notional_est:,.2f}</div>
<div style="font-size:0.7rem; color:{TEXT_SUB}; line-height:1.2;">
                {qty:,.4f} {symbol.replace("USDT","")}
</div>
</div>

<!-- Unrealized PnL -->
<div style="font-weight:500;">
<div style="color:{pnl_color}; line-height:1.2;">
                ${unreal_pl:,.2f}
            </div>
<div style="color:{pnl_color}; font-size:0.7rem; line-height:1.2;">
                {roe_pct:.2f}%
            </div>
        </div>

        <!-- Entry Price -->
        <div style="color:{TEXT_MAIN}; font-weight:500;">
            <div style="line-height:1.2;">${entry_price:,.2f}</div>
        </div>

        <!-- Current Price -->
        <div style="color:{TEXT_MAIN}; font-weight:500;">
            <div style="line-height:1.2;">${mark_price:,.2f}</div>
        </div>

        <!-- Liq. Price -->
        <div style="color:{TEXT_MAIN}; font-weight:500;">
            <div style="line-height:1.2;">${liq_price:,.2f}</div>
        </div>

        <!-- Margin Used -->
        <div style="color:{TEXT_MAIN}; font-weight:500;">
            <div style="line-height:1.2;">${mg_usdt:,.2f}</div>
        </div>

        <!-- Funding -->
        <div style="color:#4ade80; font-weight:500;">
            <div style="line-height:1.2;">{funding_display}</div>
        </div>
    </div>
    """

table_html += "</div>"

# 상단 요약 헤더 (Positions: n개, Total 등) 유지하고 싶으면 그대로
pos_header_html = f"""
<div style='background:{CARD_BG};
    border:1px solid {BORDER};
    border-radius:8px;
    padding:12px 16px;
    margin:16px 0 8px 0;
    box-shadow:{SHADOW};
    font-family:{FONT_FAMILY};
    font-size:0.8rem;
    color:{TEXT_SUB};'>
    Positions: {positions_count} | Total: ${total_position_value:,.2f}
</div>
"""

render_html(pos_header_html)
render_html(table_html)

render_html(f"<div style='font-size:0.7rem;color:{TEXT_SUB};margin-top:8px;'>Last update: {datetime.now().strftime('%H:%M:%S')} • refresh every {REFRESH_INTERVAL_SEC}s</div>")




