import time
import hmac
import hashlib
import base64
import requests
import streamlit as st
import pandas as pd
from urllib.parse import urlencode
from datetime import datetime, timedelta, timezone
from textwrap import dedent
from collections import defaultdict

# ================= CONFIG =================
st.set_page_config(page_title="Perp Dashboard", page_icon="📈", layout="wide")

PRODUCT_TYPE = "USDT-FUTURES"
MARGIN_COIN = "USDT"

API_KEY = st.secrets["bitget"]["api_key"]
API_SECRET = st.secrets["bitget"]["api_secret"]
PASSPHRASE = st.secrets["bitget"]["passphrase"]

BASE_URL = "https://api.bitget.com"

# 새로고침 주기 (초)
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

def fnum(v):
    try:
        return float(v)
    except:
        return 0.0

def safe_pct(numerator, denominator):
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100.0

def render_html(block: str):
    clean = dedent(block).lstrip()
    st.markdown(clean, unsafe_allow_html=True)

# ================= BITGET FETCHERS =================
def fetch_positions():
    """
    전체 포지션 조회
    """
    params = {"productType": PRODUCT_TYPE, "marginCoin": MARGIN_COIN}
    res = _private_get("/api/v2/mix/position/all-position", params)
    if res.get("code") == "00000":
        return (res.get("data") or [], res)
    else:
        return ([], res)

def fetch_account():
    """
    계정 정보(총자산 등)
    """
    params = {"productType": PRODUCT_TYPE, "marginCoin": MARGIN_COIN}
    res = _private_get("/api/v2/mix/account/accounts", params)
    if res.get("code") != "00000":
        return None, res
    arr = res.get("data") or []
    acct = next((a for a in arr if a.get("marginCoin") == MARGIN_COIN), None)
    return acct, res

def fetch_account_bill(symbol=None, business_type=None, limit=200):
    """
    선물 계정 청구내역(원장)
    - symbol: "BTCUSDT" 등 특정 심볼만 보고 싶으면 지정
    - business_type: 펀딩만 보고 싶으면 지정 (ex: 'fundingFee'), 근데 아래에서 우린 전체 긁고 필터링할거라 안 씀
    - limit: 최근 N개
    """
    params = {
        "productType": PRODUCT_TYPE,
        "marginCoin": MARGIN_COIN,
        "limit": str(limit),
    }
    if symbol:
        params["symbol"] = symbol
    if business_type:
        params["businessType"] = business_type

    res = _private_get("/api/v2/mix/account/accountBill", params)
    if res.get("code") != "00000":
        return []
    return res.get("data") or []

def aggregate_funding_by_symbol_with_last():
    """
    accountBill에서 businessType이 '펀딩' 관련인 항목만 모아서
    심볼별 누적 펀딩비 / 가장 최근 펀딩비를 계산.
    """
    bills = fetch_account_bill(limit=200)

    # 누적 합 / 최근 1건
    cumu_sum = defaultdict(float)
    last_amt = {}
    last_ts = {}

    for b in bills:
        sym = b.get("symbol", "")  # ex. 'BTCUSDT'
        bt = b.get("businessType", "")  # ex. 'fundingFee', 'Funding Fee', etc.
        # Bitget 응답에서 실제 금액 필드 확인 필요:
        # 보통 'amount' 또는 'billAmount' 같은 키로 금액이 들어온다.
        amt = fnum(b.get("amount", 0.0)) or fnum(b.get("billAmount", 0.0))

        # timestamp / 정렬기준으로 쓰일 값. Bitget은 보통 'cTime'(ms) 같은거 준다.
        ts_raw = b.get("cTime") or b.get("ctime") or b.get("ts")

        # 펀딩 관련 라인만 잡기: businessType 안에 'fund' 라는 문자열이 있으면 펀딩으로 간주
        # (대소문자 무시)
        if "fund" in str(bt).lower():
            cumu_sum[sym] += amt

            # 최신 1건 추적
            if ts_raw is None:
                # timestamp 없으면 그냥 덮어쓰기만
                last_amt[sym] = amt
            else:
                # 더 최신인지 비교
                old_ts = last_ts.get(sym)
                if old_ts is None or (ts_raw > old_ts):
                    last_ts[sym] = ts_raw
                    last_amt[sym] = amt

    result = {}
    for sym in cumu_sum:
        result[sym] = {
            "cumulative": cumu_sum[sym],
            "last": last_amt.get(sym, 0.0),
        }
    return result

# ================= FETCH DATA (런타임) =================
positions, raw_pos_res = fetch_positions()
account, raw_acct_res = fetch_account()

if raw_pos_res.get("code") != "00000":
    st.error(f"포지션 조회 실패: {raw_pos_res.get('msg')}")
    positions = []

if raw_acct_res.get("code") != "00000":
    st.error(f"계정 조회 실패: {raw_acct_res.get('msg')}")
    account = {}

# 펀딩비 집계
funding_map = aggregate_funding_by_symbol_with_last()

# ================= CALCULATED METRICS =================
available = fnum(account.get("available")) if account else 0.0
locked = fnum(account.get("locked")) if account else 0.0
margin_size_acct = fnum(account.get("marginSize")) if account else 0.0

# usdtEquity가 있으면 그걸 총자산으로 쓰고, 없으면 available+locked+margin 추정
total_equity = fnum(account.get("usdtEquity")) if account and account.get("usdtEquity") else (available + locked + margin_size_acct)

withdrawable_pct = (available / total_equity * 100.0) if total_equity > 0 else 0.0

total_position_value = 0.0
long_value = 0.0
short_value = 0.0
unrealized_total_pnl = 0.0
nearest_liq_pct = None  # 청산가까지 거리 (%)

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

# Bias 라벨
bias_label_raw = "long" if long_value > short_value else "short" if short_value > long_value else "flat"
if bias_label_raw == "long":
    bias_label, bias_color = ("롱 우세", "#4ade80")
elif bias_label_raw == "short":
    bias_label, bias_color = ("숏 우세", "#f87171")
else:
    bias_label, bias_color = ("중립", "#94a3b8")

# 전체 PnL 색
pnl_color = "#4ade80" if unrealized_total_pnl >= 0 else "#f87171"
roe_pct = (unrealized_total_pnl / total_equity * 100.0) if total_equity > 0 else 0.0

positions_count = len(positions)

# ================= STYLE =================
CARD_BG, TEXT_SUB, TEXT_MAIN = "#1e2538", "#94a3b8", "#f8fafc"
BORDER, SHADOW = "rgba(148,163,184,0.2)", "0 24px 48px rgba(0,0,0,0.6)"
FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif"
MONO_FAMILY = "'Roboto Mono', monospace"

# 웹폰트 주입
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Roboto+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    color: #f8fafc;
    font-size: 1.5rem; /* 기본 크기 크게 */
}
.value, .price, .metric, .number {
    font-family: 'Roboto Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ================= BADGE (LONG/SHORT → 롱/숏) =================
def format_side_badge(hold_side: str):
    side_up = (hold_side or "").upper()
    if side_up == "LONG":
        bg = "#14532d"
        border = "#22c55e"
        color = "#22c55e"
        label = "롱"
    elif side_up == "SHORT":
        bg = "#450a0a"
        border = "#f87171"
        color = "#f87171"
        label = "숏"
    else:
        bg = "#1e2538"
        border = "#94a3b8"
        color = "#94a3b8"
        label = side_up
    return f"""<span style="
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
">{label}</span>"""

# ================= RISK / PNL BLOCKS =================
margin_usage_pct = safe_pct(total_position_value, total_equity)

risk_color = (
    "#f87171" if margin_usage_pct > 70 or (nearest_liq_pct is not None and nearest_liq_pct < 3)
    else "#facc15" if margin_usage_pct > 40
    else "#4ade80"
)

risk_html = f"""
<div style='color:{TEXT_SUB};'>
  <div style='font-size:0.75rem;'>리스크</div>
  <div style='font-weight:600;font-size:1rem;color:{risk_color};'>
    마진 {margin_usage_pct:.1f}% 사용<br/>
    청산까지 {nearest_liq_pct:.2f}% 남음
  </div>
</div>
"""

pnl_block_html = f"""
<div style='color:{TEXT_SUB};'>
  <div style='font-size:0.75rem;'>미실현 손익</div>
  <div style='font-weight:600;font-size:1rem;color:{pnl_color};'>
    ${unrealized_total_pnl:,.2f}
    <span style='font-size:0.7rem;color:{pnl_color};'>({roe_pct:.2f}%)</span>
  </div>
</div>
"""

# ================= TOP CARD =================
top_card_html = f"""<div style='background:{CARD_BG};
border:1px solid {BORDER};
border-radius:8px;
padding:12px 16px;
margin-bottom:8px;
box-shadow:{SHADOW};
font-family:{FONT_FAMILY};
font-size:0.8rem;
display:flex;
align-items:flex-start;
justify-content:space-between;
'>
<div style='display:flex;flex-wrap:wrap;row-gap:8px;column-gap:32px;'>

<div style='color:{TEXT_SUB};'>
  <div style='font-size:0.75rem;'>총자산</div>
  <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${total_equity:,.2f}</div>
</div>

<div style='color:{TEXT_SUB};'>
  <div style='font-size:0.75rem;'>출금 가능
    <span style='color:#4ade80;'>{withdrawable_pct:.2f}%</span>
  </div>
  <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${available:,.2f}</div>
</div>

<div style='color:{TEXT_SUB};'>
  <div style='font-size:0.75rem;'>레버리지
    <span style='background:#7f1d1d;color:#fff;padding:2px 6px;border-radius:6px;
    font-size:0.7rem;font-weight:600;'>{est_leverage:.2f}x</span>
  </div>
  <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${total_position_value:,.2f}</div>
</div>

{risk_html}

{pnl_block_html}

</div>
</div>"""

render_html(top_card_html)

# ================= POSITIONS TABLE =================
table_html = f"""<div style="
background:#0f172a;
border:1px solid {BORDER};
border-radius:8px;
box-shadow:{SHADOW};
font-family:{FONT_FAMILY};
font-size:0.8rem;
color:{TEXT_SUB};
overflow:hidden;
">
<!-- 헤더 -->
<div style="
display:grid;
grid-template-columns:120px 80px 180px 160px 130px 140px 140px 130px 140px;
column-gap:16px;
padding:12px 16px;
border-bottom:1px solid rgba(148,163,184,0.15);
font-size:0.75rem;
color:{TEXT_SUB};
font-weight:500;
">
<div>자산</div>
<div>방향</div>
<div>포지션 가치 / 수량</div>
<div>미실현 손익</div>
<div>진입가</div>
<div>현재가</div>
<div>청산가</div>
<div>사용 마진</div>
<div>펀딩비 (누적 / 최근)</div>
</div>
"""

for p in positions:
    symbol = p.get("symbol", "")
    side = (p.get("holdSide") or "").upper()
    lev = fnum(p.get("leverage", 0.0))
    mg_usdt = fnum(p.get("marginSize", 0.0))
    qty = fnum(p.get("total", 0.0))
    entry_price = fnum(p.get("averageOpenPrice", 0.0))
    mark_price = fnum(p.get("markPrice", 0.0))
    liq_price = fnum(p.get("liquidationPrice", 0.0))
    unreal_pl = fnum(p.get("unrealizedPL", 0.0))

    notional_est = mg_usdt * lev
    roe_each_pct = safe_pct(unreal_pl, mg_usdt)

    # 색상
    pnl_color_each = "#4ade80" if unreal_pl >= 0 else "#f87171"

    # 펀딩비: funding_map에서 가져온다.
    fund_info = funding_map.get(symbol, {"cumulative": 0.0, "last": 0.0})
    funding_total_val = fund_info.get("cumulative", 0.0)
    funding_last_val = fund_info.get("last", 0.0)
    funding_display = f"${funding_total_val:,.2f} / {funding_last_val:,.4f}"

    badge_html = format_side_badge(side)

    table_html += f"""<div style="
    display:grid;
    grid-template-columns:120px 80px 180px 160px 130px 140px 140px 130px 140px;
    column-gap:16px;
    padding:16px;
    border-bottom:1px solid rgba(148,163,184,0.08);
    color:{TEXT_MAIN};
    font-size:0.8rem;
    line-height:1.4;
    ">

<!-- 자산 / 레버리지 -->
<div style="color:{TEXT_MAIN};font-weight:600;">
<div style="font-size:0.8rem;line-height:1.2;">{symbol}</div>
<div style="font-size:0.7rem;color:{TEXT_SUB};line-height:1.2;">{lev:.0f}x</div>
</div>

<!-- 방향 -->
<div style="display:flex;align-items:flex-start;padding-top:2px;">{badge_html}</div>

<!-- 포지션 가치 / 수량 -->
<div style="color:{TEXT_MAIN};font-weight:500;">
<div style="line-height:1.2;">${notional_est:,.2f}</div>
<div style="font-size:0.7rem;color:{TEXT_SUB};line-height:1.2;">{qty:,.4f} {symbol.replace("USDT","")}</div>
</div>

<!-- 미실현 손익 -->
<div style="font-weight:500;">
<div style="color:{pnl_color_each};line-height:1.2;">${unreal_pl:,.2f}</div>
<div style="color:{pnl_color_each};font-size:0.7rem;line-height:1.2;">{roe_each_pct:.2f}%</div>
</div>

<!-- 진입가 -->
<div style="color:{TEXT_MAIN};font-weight:500;white-space:nowrap;line-height:1.2;">
${entry_price:,.2f}
</div>

<!-- 현재가 -->
<div style="color:{TEXT_MAIN};font-weight:500;white-space:nowrap;line-height:1.2;">
${mark_price:,.2f}
</div>

<!-- 청산가 -->
<div style="color:{TEXT_MAIN};font-weight:500;white-space:nowrap;line-height:1.2;">
${liq_price:,.2f}
</div>

<!-- 사용 마진 -->
<div style="color:{TEXT_MAIN};font-weight:500;">
<div style="line-height:1.2;">${mg_usdt:,.2f}</div>
</div>

<!-- 펀딩비 -->
<div style="color:#4ade80;font-weight:500;">
<div style="line-height:1.2;">{funding_display}</div>
</div>

</div>"""

table_html += "</div>"

render_html(table_html)

# ================= FOOTER =================
KST = timezone(timedelta(hours=9))  # 한국 표준시
now_kst = datetime.now(KST)

footer_html = f"""<div style='font-size:0.7rem;color:{TEXT_SUB};margin-top:8px;'>
마지막 갱신: {now_kst.strftime('%H:%M:%S')} (KST) · {REFRESH_INTERVAL_SEC}초 주기 자동 새로고침
</div>"""
render_html(footer_html)

# ================= AUTO REFRESH =================
time.sleep(REFRESH_INTERVAL_SEC)
try:
    st.experimental_rerun()
except Exception:
    st.rerun()

