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

def normalize_symbol(sym: str) -> str:
    """
    Bitget 포지션 심볼이 'BTCUSDT_UMCBL' 이런 식일 수 있음.
    청구내역 bill은 'BTCUSDT'처럼 뒤 suffix가 없을 수 있음.
    => '_' 이후를 자르고 대문자화해서 통일.
    """
    if not sym:
        return ""
    return sym.split("_")[0].upper()

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

def fetch_account_bills(limit=100):
    """
    Bitget 선물 계정 청구내역 (최근 90일)
    GET /api/v2/mix/account/bill

    response:
    {
        "code":"00000",
        "data":{
            "bills":[
                {
                    "billId":"1",
                    "symbol":"BTCUSDT",
                    "amount":"-0.004992",
                    "fee":"0",
                    "businessType":"contract_settle_fee",
                    "cTime":"1695715200654",
                    ...
                },
                ...
            ],
            "endId":"2"
        }
    }
    """
    params = {
        "productType": PRODUCT_TYPE,
        "limit": str(limit),
    }

    res = _private_get("/api/v2/mix/account/bill", params)
    if res.get("code") != "00000":
        return []

    data_obj = res.get("data", {})
    bills = data_obj.get("bills", [])
    return bills

def aggregate_funding_by_symbol_with_last():
    bills = fetch_account_bills(limit=100)

    cumu_sum = defaultdict(float)  # 심볼별 누적 펀딩비 합계
    last_amt = {}                  # 심볼별 가장 최근 펀딩비 금액
    last_ts = {}                   # 심볼별 가장 최근 타임스탬프(ms)
    seen_types = set()             # 디버깅: 어떤 businessType이 있었나 기록

    for b in bills:
        raw_sym = b.get("symbol", "")              # "BTCUSDT"
        sym = normalize_symbol(raw_sym)            # -> "BTCUSDT"
        bt_raw = b.get("businessType", "")
        bt_clean = (bt_raw or "").strip().lower()  # "contract_settle_fee"
        amt = fnum(b.get("amount", 0.0))           # "0.0126341" -> float
        ts_raw = b.get("cTime")                    # "1762041608855"

        seen_types.add(bt_clean)

        # 펀딩비만 카운트
        # 1) 정확히 contract_settle_fee
        # 2) 혹시 모르게 xxx_settle_fee / funding_fee 등 비슷한 변형도 있으면 포함
        if ("settle_fee" in bt_clean) or ("funding" in bt_clean):
            cumu_sum[sym] += amt

            # 최신값 갱신
            if sym not in last_ts or (ts_raw and ts_raw > last_ts[sym]):
                last_ts[sym] = ts_raw
                last_amt[sym] = amt

    # 결과 형태로 묶기
    result = {}
    for sym in cumu_sum:
        result[sym] = {
            "cumulative": cumu_sum[sym],
            "last": last_amt.get(sym, 0.0),
        }

    # 디버깅용으로 businessType 정보를 같이 돌려주자
    # Streamlit 쪽에서 보기 편하게 리턴에 얹는다
    return {
        "_debug_seen_types": list(seen_types),  # 우리가 실제로 본 businessType 종류들
        "_debug_raw_result": dict(result),      # 계산된 결과값
    }

# ================= FETCH DATA (런타임 실행) =================
positions, raw_pos_res = fetch_positions()
account, raw_acct_res = fetch_account()

if raw_pos_res.get("code") != "00000":
    st.error(f"포지션 조회 실패: {raw_pos_res.get('msg')}")
    positions = []

if raw_acct_res.get("code") != "00000":
    st.error(f"계정 조회 실패: {raw_acct_res.get('msg')}")
    account = {}

funding_map = aggregate_funding_by_symbol_with_last()
funding_data = funding_map.get("_debug_raw_result", {})  # 실제 펀딩 합계/최근 값 테이블용

# ================= METRICS 계산 =================
available = fnum(account.get("available")) if account else 0.0
locked = fnum(account.get("locked")) if account else 0.0
margin_size_acct = fnum(account.get("marginSize")) if account else 0.0

# 총자산: usdtEquity가 있으면 그걸 쓰고, 없으면 available+locked+marginSize로 추정
total_equity = (
    fnum(account.get("usdtEquity"))
    if (account and account.get("usdtEquity") is not None)
    else (available + locked + margin_size_acct)
)

withdrawable_pct = (available / total_equity * 100.0) if total_equity > 0 else 0.0

total_position_value = 0.0
long_value = 0.0
short_value = 0.0
unrealized_total_pnl = 0.0
nearest_liq_pct = None  # 가장 가까운 청산까지 거리(%)

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

# 방향성 요약
bias_label_raw = "long" if long_value > short_value else "short" if short_value > long_value else "flat"
if bias_label_raw == "long":
    bias_label, bias_color = ("롱 우세", "#4ade80")
elif bias_label_raw == "short":
    bias_label, bias_color = ("숏 우세", "#f87171")
else:
    bias_label, bias_color = ("중립", "#94a3b8")

# 계좌 전체 PnL
pnl_color = "#4ade80" if unrealized_total_pnl >= 0 else "#f87171"
roe_pct = (unrealized_total_pnl / total_equity * 100.0) if total_equity > 0 else 0.0

positions_count = len(positions)

# ================= STYLE =================
CARD_BG, TEXT_SUB, TEXT_MAIN = "#1e2538", "#94a3b8", "#f8fafc"
BORDER, SHADOW = "rgba(148,163,184,0.2)", "0 24px 48px rgba(0,0,0,0.6)"
FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif"
MONO_FAMILY = "'Roboto Mono', monospace"

# 글로벌 폰트 주입
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Roboto+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    color: #f8fafc;
    font-size: 1rem;
}
.value, .price, .metric, .number {
    font-family: 'Roboto Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ================= BADGE =================
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
# 테이블 컨테이너 (overflow-x로 가로 스크롤 허용 / min-width 고정)
table_html = f"""<div style="
background:#0f172a;
border:1px solid {BORDER};
border-radius:8px;
box-shadow:{SHADOW};
font-family:{FONT_FAMILY};
font-size:0.8rem;
color:{TEXT_SUB};
overflow-x:auto;
min-width:1200px;
">
<!-- 헤더 -->
<div style="
display:grid;
grid-template-columns:100px 70px 160px 150px 110px 120px 120px 110px 140px;
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
    raw_symbol = p.get("symbol", "")
    symbol = normalize_symbol(raw_symbol)

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

    pnl_color_each = "#4ade80" if unreal_pl >= 0 else "#f87171"

    fund_info = funding_data.get(symbol, {"cumulative": 0.0, "last": 0.0})
    funding_total_val = fund_info.get("cumulative", 0.0)
    funding_last_val = fund_info.get("last", 0.0)
    funding_display = f"${funding_total_val:,.2f} / {funding_last_val:,.4f}"

    badge_html = format_side_badge(side)

    table_html += f"""<div style="
    display:grid;
    grid-template-columns:100px 70px 160px 150px 110px 120px 120px 110px 140px;
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

with st.expander("🧩 Debug Panel (펀딩비 확인용)"):
    st.write("### funding_map (full)")
    st.json(funding_map)

    st.write("### seen businessType values")
    st.json(funding_map.get("_debug_seen_types", []))

    st.write("### computed funding_data")
    st.json(funding_map.get("_debug_raw_result", {}))

    bills_debug = fetch_account_bills(limit=20)
    st.write("### sample bills_debug[:3]")
    st.json(bills_debug[:3])

    pos_syms_raw = [p.get("symbol","") for p in positions]
    pos_syms_norm = [normalize_symbol(p.get("symbol","")) for p in positions]
    st.write("### symbols raw   :", pos_syms_raw)
    st.write("### symbols norm  :", pos_syms_norm)


# ================= AUTO REFRESH =================
time.sleep(REFRESH_INTERVAL_SEC)
try:
    st.experimental_rerun()
except Exception:
    st.rerun()













