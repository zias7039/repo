import time  # 시간 관련 기능
import hmac  # HMAC 서명 생성
import hashlib  # 해시 알고리즘
import base64  # Base64 인코딩
import requests  # HTTP 요청 전송
import streamlit as st  # Streamlit UI 구성
import pandas as pd  # 데이터프레임 처리
from urllib.parse import urlencode  # URL 파라미터 인코딩
from datetime import datetime  # 현재 시간 사용

# ======================================
# CONFIGURATION (환경 설정)
# ======================================
st.set_page_config(page_title="Perp Dashboard", page_icon="📈", layout="wide")

# Bitget API 기본 설정
PRODUCT_TYPE = "USDT-FUTURES"  # 선물 상품 타입
MARGIN_COIN = "USDT"  # 증거금 단위

# Streamlit secrets에 저장된 API 키 정보 로드
API_KEY = st.secrets["bitget"]["api_key"]
API_SECRET = st.secrets["bitget"]["api_secret"]
PASSPHRASE = st.secrets["bitget"]["passphrase"]

BASE_URL = "https://api.bitget.com"  # Bitget 기본 URL
REFRESH_INTERVAL_SEC = 15  # 새로고침 주기 (초)

# ======================================
# Bitget API 헬퍼 함수
# ======================================
def _timestamp_ms():
    return str(int(time.time() * 1000))  # 현재 시간(밀리초) 반환


def _sign(timestamp_ms, method, path, query_params, body, secret_key):
    # 요청 서명을 생성 (Bitget HMAC-SHA256 방식)
    method_up = method.upper()
    if body is None:
        body = ""
    # 쿼리 파라미터 포함 시 URL 인코딩 처리
    if query_params:
        query_str = urlencode(query_params)
        sign_target = f"{timestamp_ms}{method_up}{path}?{query_str}{body}"
    else:
        sign_target = f"{timestamp_ms}{method_up}{path}{body}"
    # HMAC-SHA256 해싱 후 Base64 인코딩
    mac = hmac.new(secret_key.encode(), sign_target.encode(), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()


def _private_get(path, params=None):
    # 서명 포함된 인증 요청 수행
    ts = _timestamp_ms()
    signature = _sign(ts, "GET", path, params, "", API_SECRET)
    # URL 조합
    query_str = urlencode(params) if params else ""
    url = f"{BASE_URL}{path}?{query_str}" if params else f"{BASE_URL}{path}"
    # 인증 헤더 구성
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
    # 전체 포지션 정보 요청
    params = {"productType": PRODUCT_TYPE, "marginCoin": MARGIN_COIN}
    res = _private_get("/api/v2/mix/position/all-position", params)
    return (res.get("data") or [], res) if res.get("code") == "00000" else ([], res)


def fetch_account():
    # 계좌 정보 요청
    params = {"productType": PRODUCT_TYPE, "marginCoin": MARGIN_COIN}
    res = _private_get("/api/v2/mix/account/accounts", params)
    if res.get("code") != "00000":
        return None, res
    arr = res.get("data") or []
    acct = next((a for a in arr if a.get("marginCoin") == MARGIN_COIN), None)
    return acct, res

# ======================================
# 데이터 수집 및 계산
# ======================================
positions, _ = fetch_positions()
account, _ = fetch_account()

# 안전한 float 변환 함수
def fnum(v):
    try:
        return float(v)
    except:
        return 0.0

# 계좌 잔고 계산
available = fnum(account.get("available")) if account else 0.0
locked = fnum(account.get("locked")) if account else 0.0
margin_size = fnum(account.get("marginSize")) if account else 0.0

# 총 자산 계산
if account and "usdtEquity" in account:
    total_equity = fnum(account["usdtEquity"])
elif account and "equity" in account:
    total_equity = fnum(account["equity"])
else:
    total_equity = available + locked + margin_size

# 인출 가능 비율 계산
withdrawable_pct = (available / total_equity * 100) if total_equity > 0 else 0.0

# 포지션 기반 지표 초기화
total_position_value = 0.0
long_value, short_value, unrealized_total_pnl, nearest_liq_pct = 0.0, 0.0, 0.0, None

# 각 포지션 정보 순회하며 계산
for p in positions:
    lev = fnum(p.get("leverage"))
    mg = fnum(p.get("marginSize"))
    pos_val = mg * lev
    total_position_value += pos_val
    side = (p.get("holdSide", "").lower())
    if side == "long":
        long_value += pos_val
    elif side == "short":
        short_value += pos_val
    unrealized_total_pnl += fnum(p.get("unrealizedPL"))

    # 청산가까지 거리 계산 (가장 가까운 것 저장)
    mark_price, liq_price = fnum(p.get("markPrice")), fnum(p.get("liquidationPrice"))
    if liq_price:
        dist_pct = abs((mark_price - liq_price) / liq_price) * 100
        nearest_liq_pct = dist_pct if nearest_liq_pct is None else min(nearest_liq_pct, dist_pct)

# 레버리지, 방향성, 색상 지정
est_leverage = total_position_value / total_equity if total_equity else 0
bias_label, bias_color = ("LONG", "#4ade80") if long_value > short_value else ("SHORT", "#f87171") if short_value > long_value else ("FLAT", "#94a3b8")
pnl_color = "#4ade80" if unrealized_total_pnl >= 0 else "#f87171"

# 청산 버퍼 색상 및 텍스트
if nearest_liq_pct is None:
    liq_text, liq_color = "n/a", "#94a3b8"
else:
    liq_text = f"{nearest_liq_pct:.2f}% to nearest liq"
    liq_color = "#4ade80" if nearest_liq_pct > 30 else "#f87171"

# 포지션 수, 비율 계산
positions_count = len(positions)
if positions_count:
    longs = sum(1 for p in positions if (p.get("holdSide", "").lower()) == "long")
    shorts = sum(1 for p in positions if (p.get("holdSide", "").lower()) == "short")
    pos_long_pct, pos_short_pct = longs / positions_count * 100, shorts / positions_count * 100
else:
    pos_long_pct = pos_short_pct = 0.0

# ROE 계산
roe_pct = (unrealized_total_pnl / total_equity * 100) if total_equity else 0.0

# ======================================
# 세션 상태에 PnL 기록 저장 (차트용)
# ======================================
if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = []

st.session_state.pnl_history.append({"ts": datetime.now().strftime("%H:%M:%S"), "pnl": unrealized_total_pnl})
st.session_state.pnl_history = st.session_state.pnl_history[-200:]  # 최대 200개 유지

chart_df = pd.DataFrame(st.session_state.pnl_history)  # 차트용 데이터프레임

# ======================================
# KPI BAR 출력 (HTML 카드형)
# ======================================
st.markdown(
    f"""<div style="display:flex;flex-wrap:wrap;justify-content:space-between;background:#1e2538;border:1px solid rgba(148,163,184,0.2);border-radius:12px;padding:16px 20px;box-shadow:0 24px 48px rgba(0,0,0,0.6);">
    <div style='display:flex;flex-wrap:wrap;gap:24px;'>
        <div><div style='color:#94a3b8;font-size:0.75rem'>Total Value</div><div style='color:#f8fafc;font-weight:600'>${total_equity:,.2f}</div><div style='color:#94a3b8;font-size:0.7rem'>Perp ${total_equity:,.2f}</div></div>
        <div><div style='color:#94a3b8;font-size:0.75rem'>Withdrawable <span style='color:#4ade80'>{withdrawable_pct:.2f}%</span></div><div style='color:#f8fafc;font-weight:600'>${available:,.2f}</div></div>
        <div><div style='color:#94a3b8;font-size:0.75rem'>Leverage <span style='background:#7f1d1d;color:#fff;padding:2px 6px;border-radius:6px'>{est_leverage:.2f}x</span></div><div style='color:#f8fafc;font-weight:600'>${total_position_value:,.2f}</div></div>
    </div>
    <div style='text-align:right;color:#94a3b8;font-size:0.7rem'>Manual refresh • {REFRESH_INTERVAL_SEC}s</div>
</div>""", unsafe_allow_html=True)

# ======================================
# MAIN PANEL 카드 (왼쪽 지표 + 오른쪽 탭)
# ======================================
st.markdown(
    f"""<div style='display:flex;flex-wrap:wrap;justify-content:space-between;background:#1e2538;border:1px solid rgba(148,163,184,0.2);border-radius:12px;padding:16px 20px;box-shadow:0 24px 48px rgba(0,0,0,0.6);'>
        <div style='flex:0.35;'>
            <div style='color:#94a3b8;font-size:0.8rem'>Perp Equity</div>
            <div style='font-size:1.4rem;font-weight:600;color:#f8fafc'>${total_equity:,.2f}</div>
            <div style='color:#94a3b8;font-size:0.75rem'>Direction Bias</div>
            <div style='font-weight:600;color:{bias_color}'>{bias_label}</div>
            <div style='color:#94a3b8;font-size:0.75rem'>Unrealized PnL</div>
            <div style='font-weight:600;color:{pnl_color}'>${unrealized_total_pnl:,.2f}</div>
            <div style='font-size:0.7rem;color:#94a3b8'>{roe_pct:.2f}% ROE</div>
        </div>
        <div style='flex:0.6;'>
            <div style='display:flex;gap:8px;'>
                <div style='background:#0f3;color:#000;font-weight:600;border-radius:6px;padding:4px 8px;'>24H</div>
                <div style='border:1px solid #334155;border-radius:6px;padding:4px 8px;color:#94a3b8;'>1W</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

# 차트 출력
st.line_chart(chart_df, x="ts", y="pnl", height=220)

# ======================================
# POSITION TABLE + HEADER
# ======================================
st.markdown(f"<div style='background:#1e2538;padding:12px 20px;border-radius:12px 12px 0 0;color:#94a3b8'>Positions: {len(positions)} | Total: ${total_position_value:,.2f}</div>", unsafe_allow_html=True)

rows = []
for p in positions:
    lev = fnum(p.get("leverage"))
    mg = fnum(p.get("marginSize"))
    mark, liq = fnum(p.get("markPrice")), fnum(p.get("liquidationPrice"))
    dist = f"{abs((mark - liq) / liq) * 100:.2f}%" if liq else "n/a"
    rows.append({"Asset": p.get("symbol"), "Type": p.get("holdSide", "").upper(), "Lev": f"{lev}x", "Value": f"{mg*lev:,.2f}", "PnL": f"{fnum(p.get('unrealizedPL')):,.2f}", "Liq Dist": dist})

st.dataframe(rows, use_container_width=True)

st.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')} • refresh every {REFRESH_INTERVAL_SEC}s")
