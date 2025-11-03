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
import plotly.graph_objects as go

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

# ===== KRW 환율 (USDT 기준) =====
@st.cache_data(ttl=60)
def fetch_usdt_krw() -> float | None:
    try:
        res = requests.get("https://api.upbit.com/v1/ticker", params={"markets": "USDT-BTC,KRW-BTC"}, timeout=5)
        data = res.json()

        btc_usdt = next((d["trade_price"] for d in data if d["market"] == "USDT-BTC"), None)
        btc_krw = next((d["trade_price"] for d in data if d["market"] == "KRW-BTC"), None)

        if btc_usdt and btc_krw:
            return float(btc_krw) / float(btc_usdt)
        return None
    except Exception:
        return None

USDT_KRW = fetch_usdt_krw()

def krw_line(amount_usd: float, color: str | None = None) -> str:
    if not USDT_KRW:
        return ""
    won = amount_usd * USDT_KRW
    style_color = f"color:{color};" if color else f"color:{TEXT_SUB};"
    return f"<div style='font-size:0.70rem;{style_color}margin-top:0px;'>≈ ₩{won:,.0f}</div>"

# ================= SESSION STATE (차트 선택 심볼) =================
if "selected_symbol" not in st.session_state:
    # 기본 심볼: BTCUSDT
    st.session_state.selected_symbol = "BTCUSDT"


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
    캔들/빌링 등은 'BTCUSDT'만 오는 경우도 있음.
    => '_' 이후를 자르고 대문자화해서 통일.
    """
    if not sym:
        return ""
    return sym.split("_")[0].upper()


# ================= PUBLIC FETCHERS (차트용) =================
def fetch_kline_spot(symbol="BTCUSDT", granularity="1h", limit=100):
    params = {
        "symbol": symbol,
        "granularity": granularity,  # '1m','5m','1h','4h','1d' 등
        "limit": str(limit),
    }
    res = requests.get(f"{BASE_URL}/api/v2/spot/market/candles", params=params).json()
    if res.get("code") != "00000":
        return pd.DataFrame()

    data = res.get("data", [])
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(
        data,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "vol_base",
            "vol_usdt",
            "vol_quote",
        ],
    )

    # 타입 변환
    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(float), unit="ms")
    df = df.astype({
        "open": float,
        "high": float,
        "low": float,
        "close": float,
    })

    # Bitget은 최신 -> 과거 순서로 줄 때도 있으니까 시간순으로 정렬
    df = df.sort_values("timestamp")
    return df

def render_chart(symbol_display: str, granularity="1h"):
    df = fetch_kline_spot(symbol_display, granularity=granularity, limit=100)
    
    if df.empty:
        st.warning(f"{symbol} 차트를 불러올 수 없습니다.")
        return

    fig = go.Figure(
        data=[go.Candlestick(
            x=df["timestamp"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            increasing_line_color="#22c55e",
            decreasing_line_color="#ef4444",
        )]
    )

    fig.update_layout(
        title=f"{symbol_display} / {granularity}",
        height=320,
        margin=dict(l=0, r=0, t=30, b=0),
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
    )

    st.plotly_chart(fig, use_container_width=True)


# ================= BITGET PRIVATE FETCHERS =================
def fetch_positions():
    params = {"productType": PRODUCT_TYPE, "marginCoin": MARGIN_COIN}
    res = _private_get("/api/v2/mix/position/all-position", params)
    if res.get("code") == "00000":
        return (res.get("data") or [], res)
    else:
        return ([], res)

def fetch_account():
    params = {"productType": PRODUCT_TYPE, "marginCoin": MARGIN_COIN}
    res = _private_get("/api/v2/mix/account/accounts", params)
    if res.get("code") != "00000":
        return None, res
    arr = res.get("data") or []
    acct = next((a for a in arr if a.get("marginCoin") == MARGIN_COIN), None)
    return acct, res

def fetch_account_bills(limit=100):
    """
    펀딩비 내역 등 Billing (최근 90일)
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

    cumu_sum = defaultdict(float)  # 누적 펀딩비 합계
    last_amt = {}
    last_ts = {}
    seen_types = set()

    for b in bills:
        raw_sym = b.get("symbol", "")
        sym = normalize_symbol(raw_sym)
        bt_raw = b.get("businessType", "")
        bt_clean = (bt_raw or "").strip().lower()
        amt = fnum(b.get("amount", 0.0))
        ts_raw = b.get("cTime")

        seen_types.add(bt_clean)

        # settle_fee / funding 등만 집계
        if ("settle_fee" in bt_clean) or ("funding" in bt_clean):
            cumu_sum[sym] += amt
            # 최근값 추적 (디버그용)
            if sym not in last_ts or (ts_raw and ts_raw > last_ts[sym]):
                last_ts[sym] = ts_raw
                last_amt[sym] = amt

    result = {}
    for sym in cumu_sum:
        result[sym] = {
            "cumulative": cumu_sum[sym],
            "last": last_amt.get(sym, 0.0),
        }

    return {
        "_debug_seen_types": list(seen_types),
        "_debug_raw_result": dict(result),
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
funding_data = funding_map.get("_debug_raw_result", {})

# ================= METRICS 계산 =================
available = fnum(account.get("available")) if account else 0.0
locked = fnum(account.get("locked")) if account else 0.0
margin_size_acct = fnum(account.get("marginSize")) if account else 0.0

# 총자산
total_equity = (
    fnum(account.get("usdtEquity"))
    if (account and account.get("usdtEquity") is not None)
    else (available + locked + margin_size_acct)
)

withdrawable_pct = (available / total_equity * 100.0) if total_equity > 0 else 0.0

total_position_value = 0.0
unrealized_total_pnl = 0.0

for p in positions:
    lev = fnum(p.get("leverage", 0.0))
    mg = fnum(p.get("marginSize", 0.0))

    # 명목규모 (증거금 * 레버리지)
    notional_est = mg * lev
    total_position_value += notional_est

    # 전체 미실현 PnL 누적
    unrealized_total_pnl += fnum(p.get("unrealizedPL", 0.0))

# 계좌 차원의 추정 레버리지
est_leverage = (total_position_value / total_equity) if total_equity > 0 else 0.0

# 전체 PnL 색/ROE
pnl_color = "#4ade80" if unrealized_total_pnl >= 0 else "#f87171"
roe_pct = (unrealized_total_pnl / total_equity * 100.0) if total_equity > 0 else 0.0


# ================= STYLE =================
CARD_BG, TEXT_SUB, TEXT_MAIN = "#1e2538", "#94a3b8", "#f8fafc"
BORDER, SHADOW = "rgba(148,163,184,0.2)", "0 24px 48px rgba(0,0,0,0.6)"
FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif"

# 글로벌 폰트 주입
st.markdown("""
<style>
@font-face {
    font-family: 'Everett Mono';
    src: url('https://cdn.jsdelivr.net/gh/jaywcjlove/fonts@main/fonts/Everett-Mono-Regular.woff2') format('woff2');
    font-weight: 400;
    font-style: normal;
}
@font-face {
    font-family: 'Everett Mono';
    src: url('https://cdn.jsdelivr.net/gh/jaywcjlove/fonts@main/fonts/Everett-Mono-Bold.woff2') format('woff2');
    font-weight: 700;
    font-style: normal;
}

/* 기본 */
html, body, [class*="css"] {
    font-family: 'Inter', 'Everett Mono', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    color: #f8fafc;
    font-size: 1.4rem;
}

/* 숫자/코드 느낌 */
.value, .price, .metric, .number, code, pre {
    font-family: 'Everett Mono', monospace;
    font-weight: 500;
    font-size: 1.2rem;
    letter-spacing: -0.02rem;
}

.toolbar {
  display:flex; align-items:center; justify-content:space-between;
  gap:16px; padding:8px 12px; border:1px solid rgba(148,163,184,.15);
  background:#0f172a; border-radius:10px; margin:4px 0 10px 0;
  box-shadow: 0 12px 32px rgba(0,0,0,.35);
}

/* title */
.toolbar .title {
  display:flex; align-items:center; gap:10px; color:#e2e8f0; font-weight:700;
  letter-spacing:-0.02rem;
}
.toolbar .title .sub { color:#94a3b8; font-weight:500; }

/* ===== Radio -> Pill 화 ===== */
div[role="radiogroup"] {
  display:flex; flex-wrap:wrap; gap:8px;
}
div[role="radiogroup"] > label {
  margin:0 !important; padding:6px 12px; border-radius:999px;
  border:1px solid rgba(148,163,184,.25);
  background:#111827; color:#e5e7eb; transition:all .15s ease;
  font-size:.85rem; cursor:pointer;
}
div[role="radiogroup"] > label:hover {
  background:#1f2937; transform:translateY(-1px);
}
div[role="radiogroup"] > label[data-checked="true"] {
  background:#1e293b; border-color:#60a5fa; box-shadow:0 0 0 1px #60a5fa inset;
  color:#f8fafc; font-weight:700;
}

/* 라벨 숨김(공간 최소화) */
.small-label .stRadio > label, .small-label .stRadio > div > label { display:none; }

/* 심볼 라디오를 칩처럼 */
.symbols { margin-top:6px; }
</style>
""", unsafe_allow_html=True)


# ================= BADGE (롱/숏 칩) =================
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


# ================= TOP CARD BLOCK HTML =================
pnl_block_html = f"""
<div style='color:{TEXT_SUB};'>
  <div style='font-size:0.75rem;'>미실현 손익</div>
  <div style='font-weight:600;font-size:1rem;color:{pnl_color};'>
    ${unrealized_total_pnl:,.2f}
    <span style='font-size:0.7rem;color:{pnl_color};'>({roe_pct:.2f}%)</span>
  </div>
  {krw_line(unrealized_total_pnl, color=pnl_color)}
</div>
"""

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
<div style='display:flex;flex-wrap:wrap;row-gap:1px;column-gap:32px;'>

<div style='color:{TEXT_SUB};'>
  <div style='font-size:0.75rem;'>총자산</div>
  <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${total_equity:,.2f}</div>
  {krw_line(total_equity)}
</div>

<div style='color:{TEXT_SUB};'>
  <div style='font-size:0.75rem;'>출금 가능
    <span style='color:#4ade80;'>{withdrawable_pct:.2f}%</span>
  </div>
  <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${available:,.2f}</div>
  {krw_line(available)}
</div>

<div style='color:{TEXT_SUB};'>
  <div style='font-size:0.75rem;'>레버리지
    <span style='background:#7f1d1d;color:#fff;padding:2px 6px;border-radius:6px;
    font-size:0.7rem;font-weight:600;'>{est_leverage:.2f}x</span>
  </div>
  <div style='color:{TEXT_MAIN};font-weight:600;font-size:1rem;'>${total_position_value:,.2f}</div>
  {krw_line(total_position_value)}
</div>

{pnl_block_html}

</div>
</div>"""

# ================== GRANULARITY SELECT ==================
granularity_map = {
    "1분": "1min",
    "5분": "5min",
    "15분": "15min",
    "1시간": "1h",
    "4시간": "4h",
    "1일": "1day",
}

granularity_labels = list(granularity_map.keys())
default_granularity_index = 2  # 15분

# 현재 보유 포지션 기준 심볼 목록 (없으면 BTC/ETH fallback)
pos_symbols = [normalize_symbol(p.get("symbol","")) for p in positions] if positions else []
pos_symbols = [s for s in pos_symbols if s] or ["BTCUSDT","ETHUSDT"]

# 현재 선택 심볼이 목록에 없으면 넣기
if st.session_state.selected_symbol not in pos_symbols:
    pos_symbols = [st.session_state.selected_symbol] + [s for s in pos_symbols if s != st.session_state.selected_symbol]

# ===== Toolbar (타이틀 + 간격칩) =====
left, right = st.columns([0.52, 0.48], vertical_alignment="center")
with left:
    st.markdown(
        f"""
        <div class="toolbar">
          <div class="title">
            <span>📈</span>
            <div>
              <div style="font-size:1.05rem;">{st.session_state.selected_symbol} <span class="sub">가격</span></div>
              <div class="sub">{st.session_state.selected_symbol} / {granularity_labels[default_granularity_index]}</div>
            </div>
          </div>
          <div></div>
        </div>
        """, unsafe_allow_html=True
    )

with right:
    st.container()  # 자리 맞추기용

# ===== 간격 선택(칩) - 라벨 숨김, 가로 나열 =====
with st.container():
    st.markdown('<div class="small-label">', unsafe_allow_html=True)
    selected_granularity_label = st.radio(
        "차트 간격",
        granularity_labels,
        horizontal=True,
        index=default_granularity_index,
        key="granularity_radio",
    )
    st.markdown('</div>', unsafe_allow_html=True)

selected_granularity = granularity_map[selected_granularity_label]

# ================== LAYOUT: CHART + CARD ==================
st.markdown(
    f"#### 📈 {st.session_state.selected_symbol} 가격 ({selected_granularity_label})"
)
render_chart(
    st.session_state.selected_symbol,
    granularity=selected_granularity
)

# 그 다음 상단 카드
render_html(top_card_html)

# ================= POSITIONS TABLE =================
st.markdown(
    "<div style='font-size:0.8rem;color:#94a3b8;margin-top:4px;'>심볼 변경:</div>",
    unsafe_allow_html=True
)
sym_cols = st.columns(len(positions) if positions else 1)
for idx, p in enumerate(positions):
    symbol_norm = normalize_symbol(p.get("symbol", ""))
    with sym_cols[idx]:
        if st.button(symbol_norm, key=f"symbtn_{symbol_norm}"):
           st.session_state.selected_symbol = symbol_norm
           st.rerun()

# 실제 상세 테이블
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
margin-top:8px;
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
<div>펀딩비</div>
</div>
"""

for p in positions:
    raw_symbol = p.get("symbol", "")
    symbol = normalize_symbol(raw_symbol)

    side_raw = (p.get("holdSide") or "").upper()
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
    funding_display = f"${funding_total_val:,.2f}"

    badge_html = format_side_badge(side_raw)

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
KST = timezone(timedelta(hours=9))
now_kst = datetime.now(KST)

footer_html = f"""<div style='font-size:0.7rem;color:{TEXT_SUB};
margin-top:8px;
margin-bottom:12px;'>
마지막 갱신: {now_kst.strftime('%H:%M:%S')} (KST) · {REFRESH_INTERVAL_SEC}초 주기 자동 새로고침
</div>"""
render_html(footer_html)

# ================= AUTO REFRESH =================
time.sleep(REFRESH_INTERVAL_SEC)
st.rerun()






















