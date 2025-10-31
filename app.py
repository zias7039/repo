import time
import hmac
import hashlib
import base64
import requests
import streamlit as st
from urllib.parse import urlencode
from datetime import datetime

API_KEY = st.secrets["bitget"]["api_key"]
API_SECRET = st.secrets["bitget"]["api_secret"]
PASSPHRASE = st.secrets["bitget"]["passphrase"]

BASE_URL = "https://api.bitget.com"
PRODUCT_TYPE = "USDT-FUTURES"


# ==========================
# 공통 유틸 / 사인 / 요청
# ==========================
def get_timestamp_ms():
    return str(int(time.time() * 1000))

def make_signature(ts_ms: str, method: str, request_path: str, query_params: dict | None, body: str, secret_key: str) -> str:
    method_up = method.upper()
    if body is None:
        body = ""
    if query_params:
        query_str = urlencode(query_params)
        sign_target = f"{ts_ms}{method_up}{request_path}?{query_str}{body}"
    else:
        sign_target = f"{ts_ms}{method_up}{request_path}{body}"

    mac = hmac.new(
        secret_key.encode("utf-8"),
        sign_target.encode("utf-8"),
        digestmod=hashlib.sha256
    )
    return base64.b64encode(mac.digest()).decode()

def private_get(path: str, params: dict | None = None):
    ts_ms = get_timestamp_ms()
    method = "GET"
    body = ""

    sign = make_signature(ts_ms, method, path, params, body, API_SECRET)

    if params:
        query_str = urlencode(params)
        full_path = f"{path}?{query_str}"
        url = f"{BASE_URL}{full_path}"
    else:
        full_path = path
        url = f"{BASE_URL}{path}"

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": sign,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "ACCESS-TIMESTAMP": ts_ms,
        "locale": "en-US",
        "Content-Type": "application/json",
    }

    resp = requests.get(url, headers=headers)
    return resp.json()


# ==========================
# 비즈니스 로직
# ==========================
def get_positions(product_type: str):
    params = {
        "productType": product_type,
        "marginCoin": "USDT",
    }
    res = private_get("/api/v2/mix/position/all-position", params)

    if res.get("code") != "00000":
        return [], res
    return res.get("data") or [], res

def get_balance_usdt(product_type: str):
    params = {
        "productType": product_type,
        "marginCoin": "USDT",
    }
    res = private_get("/api/v2/mix/account/accounts", params)

    if res.get("code") != "00000":
        return 0.0, res

    accounts = res.get("data") or []
    for acc in accounts:
        if acc.get("marginCoin") == "USDT":
            try:
                return float(acc.get("available", 0.0)), res
            except:
                return 0.0, res
    return 0.0, res

def summarize_positions(positions: list[dict]):
    total_pnl = 0.0
    for p in positions:
        try:
            total_pnl += float(p.get("unrealizedPL", 0))
        except:
            pass

    return {
        "total_cnt": len(positions),
        "total_pnl": total_pnl,
    }

def positions_to_table_rows(positions: list[dict], public_mode: bool):
    """
    public_mode = True면 민감 데이터(수량, 청산가 등) 숨겨서 가볍게 보여주기
    """
    rows = []
    for p in positions:
        base = {
            "심볼": p.get("symbol"),
            "방향": p.get("holdSide"),
            "레버리지": f"{p.get('leverage')}x",
            "진입가": p.get("openPriceAvg") or p.get("averageOpenPrice"),
            "현재가(마크)": p.get("markPrice"),
            "미실현PnL": p.get("unrealizedPL"),
        }
        if not public_mode:
            # 풀 정보 모드에서만 보여줄 항목
            base.update({
                "수량": p.get("total"),
                "청산가": p.get("liquidationPrice"),
                "마진비율": p.get("marginRatio"),
            })
        rows.append(base)
    return rows


# ==========================
# Streamlit 화면 구성
# ==========================
st.set_page_config(
    page_title="My Futures Monitor",
    layout="wide",
    page_icon="📈",
)

# ----- Custom CSS (카드 형태, 색상 등) -----
st.markdown(
    """
    <style>
    /* 전체 배경 조금 어둡고 카드 떠 있는 느낌 */
    body {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    .main {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    /* metric 카드 직접 꾸미기 위해 container div 만들 거라 그 스타일 */
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148,163,184,0.2);
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 600;
        color: #f8fafc;
        line-height: 1.2;
    }
    .metric-value.positive {
        color: #4ade80;
    }
    .metric-value.negative {
        color: #f87171;
    }
    .section-header {
        font-size: 1rem;
        font-weight: 600;
        color: #f8fafc;
        display: flex;
        align-items: baseline;
        gap: 0.5rem;
    }
    .section-sub {
        font-size: 0.75rem;
        font-weight: 400;
        color: #94a3b8;
    }
    /* 표 텍스트 색 */
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        color: #e2e8f0 !important;
        background-color: #1e2538 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----- 사이드바 컨트롤 -----
st.sidebar.title("⚙ Control")
refresh = st.sidebar.button("↻ 새로고침")
public_mode = st.sidebar.checkbox("공개용 뷰 (민감정보 숨김)", value=False)

st.sidebar.markdown("---")
st.sidebar.write("마켓 타입:", PRODUCT_TYPE)
st.sidebar.caption("※ 공개용 뷰 켜면 수량/청산가/마진비율 숨김")

# ----- 데이터 로드 -----
positions, raw_pos_res = get_positions(PRODUCT_TYPE)
balance_usdt, raw_bal_res = get_balance_usdt(PRODUCT_TYPE)
summary = summarize_positions(positions)

last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ----- KPI 영역 (3컬럼) -----
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">오픈 포지션 개수</div>
            <div class="metric-value">{summary["total_cnt"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

pnl_class = "positive" if summary["total_pnl"] >= 0 else "negative"

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">총 미실현 PnL (USDT)</div>
            <div class="metric-value {pnl_class}">{summary["total_pnl"]:.4f} USDT</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">가용 USDT 잔액</div>
            <div class="metric-value">{balance_usdt:,.4f} USDT</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ----- 섹션 헤더 (포지션 테이블) -----
st.markdown(
    f"""
    <div class="section-header">
        <div>현재 포지션</div>
        <div class="section-sub">updated {last_updated}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

table_rows = positions_to_table_rows(positions, public_mode=public_mode)

if len(positions) == 0:
    st.info("현재 오픈 포지션이 없습니다.")
else:
    st.dataframe(table_rows, use_container_width=True)

st.markdown("---")

# ----- Debug 섹션 (사이드바에서만 켤 수도 있는데 지금은 본문에 둠)
with st.expander("RAW API Response (positions)"):
    st.write(raw_pos_res)

with st.expander("RAW API Response (balance)"):
    st.write(raw_bal_res)

st.caption("⚠ API Key 하드코딩 상태에서 URL 공유 = 계좌 노출. 배포 전에는 secrets 처리 필수.")
