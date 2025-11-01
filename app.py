diff --git a/app.py b/app.py
index 3be02723efddc985a854b340adbff75014e83088..993c87aeff664315e240dc14e413e870241cbfbd 100644
--- a/app.py
+++ b/app.py
@@ -1,62 +1,85 @@
 import time
 import hmac
 import hashlib
 import base64
-import requests
-import streamlit as st
-import pandas as pd
+import requests
+import streamlit as st
+import pandas as pd
+from textwrap import dedent
 from urllib.parse import urlencode
 from datetime import datetime
 
 # ======================================
 # CONFIG
 # ======================================
-st.set_page_config(
-    page_title="Perp Dashboard",
-    page_icon="📈",
-    layout="wide",
-)
-
-PRODUCT_TYPE = "USDT-FUTURES"
-MARGIN_COIN = "USDT"
-
-# --- Secrets (streamlit cloud에 저장된 값 사용)
-API_KEY = st.secrets["bitget"]["api_key"]
-API_SECRET = st.secrets["bitget"]["api_secret"]
-PASSPHRASE = st.secrets["bitget"]["passphrase"]
+st.set_page_config(
+    page_title="Perp Dashboard",
+    page_icon="📈",
+    layout="wide",
+)
+
+PRODUCT_TYPE = "USDT-FUTURES"
+MARGIN_COIN = "USDT"
+
+# --- Secrets (streamlit cloud에 저장된 값 사용)
+bitget_conf = st.secrets.get("bitget")
+if not bitget_conf:
+    st.error(
+        "Bitget API credentials가 설정되지 않았습니다. Streamlit secrets에 bitget 섹션을 추가해 주세요."
+    )
+    st.stop()
+
+missing_secret_keys = [
+    key for key in ("api_key", "api_secret", "passphrase") if key not in bitget_conf
+]
+if missing_secret_keys:
+    st.error(
+        "Bitget API credentials에 누락된 키가 있습니다: "
+        + ", ".join(missing_secret_keys)
+    )
+    st.stop()
+
+API_KEY = bitget_conf["api_key"]
+API_SECRET = bitget_conf["api_secret"]
+PASSPHRASE = bitget_conf["passphrase"]
 
 BASE_URL = "https://api.bitget.com"
 
 REFRESH_INTERVAL_SEC = 15  # 화면에 "Next refresh in Ns"로 보여줄 값
 
 
 # ======================================
 # STYLE: 다크 UI와 카드 스타일
 # ======================================
-st.markdown(
-    """
+def render_html(markup: str) -> None:
+    """Render raw HTML markup without leading indentation artifacts."""
+    st.markdown(dedent(markup), unsafe_allow_html=True)
+
+
+render_html(
+    """
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
 
@@ -200,135 +223,162 @@ st.markdown(
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
-    </style>
-    """,
-    unsafe_allow_html=True
-)
+    </style>
+    """
+)
 
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
 
-def _private_get(path, params=None):
-    ts = _timestamp_ms()
-    method = "GET"
-    body = ""
-
-    signature = _sign(ts, method, path, params, body, API_SECRET)
-
-    if params:
-        query_str = urlencode(params)
-        url = f"{BASE_URL}{path}?{query_str}"
-    else:
-        url = f"{BASE_URL}{path}"
-
-    headers = {
-        "ACCESS-KEY": API_KEY,
-        "ACCESS-SIGN": signature,
-        "ACCESS-PASSPHRASE": PASSPHRASE,
-        "ACCESS-TIMESTAMP": ts,
-        "locale": "en-US",
-        "Content-Type": "application/json",
-    }
-    r = requests.get(url, headers=headers)
-    return r.json()
-
-def fetch_positions():
-    params = {
-        "productType": PRODUCT_TYPE,
-        "marginCoin": MARGIN_COIN,
-    }
-    res = _private_get("/api/v2/mix/position/all-position", params)
-    if res.get("code") != "00000":
-        return [], res
-    data = res.get("data") or []
-    return data, res
-
-def fetch_account():
-    params = {
-        "productType": PRODUCT_TYPE,
-        "marginCoin": MARGIN_COIN,
-    }
+def _private_get(path, params=None):
+    ts = _timestamp_ms()
+    method = "GET"
+    body = ""
+
+    signature = _sign(ts, method, path, params, body, API_SECRET)
+
+    if params:
+        query_str = urlencode(params)
+        url = f"{BASE_URL}{path}?{query_str}"
+    else:
+        url = f"{BASE_URL}{path}"
+
+    headers = {
+        "ACCESS-KEY": API_KEY,
+        "ACCESS-SIGN": signature,
+        "ACCESS-PASSPHRASE": PASSPHRASE,
+        "ACCESS-TIMESTAMP": ts,
+        "locale": "en-US",
+        "Content-Type": "application/json",
+    }
+
+    try:
+        response = requests.get(url, headers=headers, timeout=10)
+        response.raise_for_status()
+    except requests.RequestException as exc:
+        return {
+            "code": "HTTP_ERROR",
+            "msg": f"Bitget API request failed: {exc}",
+            "data": None,
+        }
+
+    try:
+        return response.json()
+    except ValueError:
+        return {
+            "code": "INVALID_RESPONSE",
+            "msg": "Bitget API에서 JSON이 아닌 응답을 반환했습니다.",
+            "data": None,
+        }
+
+@st.cache_data(ttl=REFRESH_INTERVAL_SEC)
+def fetch_positions():
+    params = {
+        "productType": PRODUCT_TYPE,
+        "marginCoin": MARGIN_COIN,
+    }
+    res = _private_get("/api/v2/mix/position/all-position", params)
+    if res.get("code") != "00000":
+        return [], res
+    data = res.get("data") or []
+    return data, res
+
+@st.cache_data(ttl=REFRESH_INTERVAL_SEC)
+def fetch_account():
+    params = {
+        "productType": PRODUCT_TYPE,
+        "marginCoin": MARGIN_COIN,
+    }
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
-positions, raw_pos = fetch_positions()
-account, raw_acct = fetch_account()
+positions, raw_pos = fetch_positions()
+raw_pos = raw_pos or {}
+if raw_pos.get("code") != "00000":
+    st.error(raw_pos.get("msg", "Bitget 포지션 정보를 불러오지 못했습니다."))
+    positions = []
+
+account, raw_acct = fetch_account()
+raw_acct = raw_acct or {}
+if raw_acct.get("code") != "00000":
+    st.error(raw_acct.get("msg", "Bitget 계정 정보를 불러오지 못했습니다."))
+    account = None
 
 # 안전 파싱 함수
 def fnum(v):
     try:
         return float(v)
     except:
         return 0.0
 
 # account 쪽 수치 추출
 available = fnum(account.get("available")) if account else 0.0
 locked = fnum(account.get("locked")) if account else 0.0
 margin_size = fnum(account.get("marginSize")) if account else 0.0
 
 # 총 잔액(우리가 dashboard 상단에서 Total Value로 쓰는 값)
 # Bitget 계정마다 필드가 다를 수 있어서 우선순위로 가져옴
 if account and "usdtEquity" in account:
     total_equity = fnum(account.get("usdtEquity"))
 elif account and "equity" in account:
     total_equity = fnum(account.get("equity"))
 else:
     total_equity = available + locked + margin_size
 
 # "Withdrawable" = available 비슷하게 노출
 withdrawable_pct = 0.0
 if total_equity > 0:
@@ -359,225 +409,222 @@ long_ratio_pct = 0.0
 if (long_value + short_value) > 0:
     long_ratio_pct = (long_value / (long_value+short_value))*100.0
 
 # 포지션 합계 표시에 쓸 문자열들
 positions_count = len(positions)
 pos_long_pct = 0.0
 pos_short_pct = 0.0
 if positions_count > 0:
     # 단순히 보유 포지션 중 long/short 비중
     longs = sum(1 for p in positions if p.get("holdSide","").lower()=="long")
     shorts = sum(1 for p in positions if p.get("holdSide","").lower()=="short")
     pos_long_pct = (longs/positions_count)*100.0
     pos_short_pct = (shorts/positions_count)*100.0
 
 # ROE 비슷한 값: unrealized_total_pnl / total_equity
 roe_pct = 0.0
 if total_equity > 0:
     roe_pct = (unrealized_total_pnl / total_equity) * 100.0
 
 # ======================================
 # Session State로 PnL 히스토리 쌓아서 라인차트 흉내
 # ======================================
 if "pnl_history" not in st.session_state:
     st.session_state.pnl_history = []
 
-st.session_state.pnl_history.append({
-    "ts": datetime.now().strftime("%H:%M:%S"),
-    "pnl": unrealized_total_pnl
-})
+st.session_state.pnl_history.append({
+    "ts": datetime.now().strftime("%H:%M:%S"),
+    "pnl": unrealized_total_pnl
+})
+
+st.session_state.pnl_history = st.session_state.pnl_history[-200:]
 
 chart_x = [pt["ts"] for pt in st.session_state.pnl_history]
 chart_y = [pt["pnl"] for pt in st.session_state.pnl_history]
 
 
 # ======================================
 # RENDER: KPI BAR (상단)
 # ======================================
-st.markdown(
-    f"""
+render_html(
+    f"""
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
                 <div class="kpi-label">Leverage <span style="background:#7f1d1d;color:#fff;padding:2px 6px;border-radius:6px;font-size:0.7rem;font-weight:600;">{est_leverage:.2f}x</span></div>
                 <div class="kpi-value">${total_position_value:,.2f}</div>
                 <div class="kpi-sub">Total position value</div>
             </div>
         </div>
 
         <div class="kpi-right">
             <div class="kpi-next-refresh">Next refresh in {REFRESH_INTERVAL_SEC}s</div>
             <div class="kpi-support">Support us</div>
         </div>
     </div>
-    """,
-    unsafe_allow_html=True
-)
+    """
+)
 
 # ======================================
 # RENDER: MAIN PANEL (Equity / Bias / PnL / Chart)
 # ======================================
 col_main_left, col_main_right = st.columns([0.4,0.6])
 
 with col_main_left:
-    st.markdown(
-        f"""
+    render_html(
+        f"""
         <div class="panel-wrapper">
             <div class="panel-top">
 
                 <div class="equity-block">
                     <div class="equity-title">Perp Equity</div>
                     <div class="equity-value">${total_equity:,.2f}</div>
                     <div class="metric-bar-label">
                         Margin Usage
                     </div>
                     <div class="metric-bar-bg">
                         <div class="metric-bar-fill" style="width:{min(est_leverage*10,100)}%;"></div>
                     </div>
                     <div class="section-sub" style="font-size:0.7rem;color:#94a3b8;">
                         est. leverage {est_leverage:.2f}x
                     </div>
                     <br/>
 
                     <div class="metric-bar-block">
                         <div class="metric-bar-label">Direction Bias</div>
                         <div class="metric-bar-value" style="color:#4ade80;">LONG</div>
                         <div class="metric-bar-bg">
                             <div class="metric-bar-fill" style="width:{long_ratio_pct:.2f}%;"></div>
                         </div>
                         <div class="section-sub" style="font-size:0.7rem;color:#94a3b8;">
                             Long Exposure {long_ratio_pct:.2f}%
                         </div>
                     </div>
 
                     <br/>
                     <div class="metric-bar-block">
                         <div class="metric-bar-label">Position Distribution</div>
                         <div class="metric-bar-value" style="color:#4ade80;">${total_position_value:,.0f}</div>
                         <div class="section-sub" style="font-size:0.7rem;color:#94a3b8;">
                             {positions_count} positions
                         </div>
                     </div>
 
                     <br/>
                     <div class="risk-block">
                         <div class="risk-label">Unrealized PnL</div>
                         <div class="risk-value-loss">${unrealized_total_pnl:,.2f}</div>
                         <div class="risk-sub">{roe_pct:.2f}% ROE</div>
                     </div>
 
                 </div>
 
             </div>
         </div>
-        """,
-        unsafe_allow_html=True
-    )
+        """
+    )
 
 with col_main_right:
-    st.markdown(
-        f"""
+    render_html(
+        f"""
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
-        """,
-        unsafe_allow_html=True
-    )
+        """
+    )
 
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
 
-    st.markdown(
-        f"""
+    render_html(
+        f"""
         <div style="display:flex;justify-content:space-between;flex-wrap:wrap;margin-top:4px;font-size:0.8rem;color:#4ade80;">
             <div>24H PnL (Session)</div>
             <div style="font-weight:600;">${unrealized_total_pnl:,.2f}</div>
         </div>
         </div>
-        """,
-        unsafe_allow_html=True
-    )
+        """
+    )
 
 
 # ======================================
 # RENDER: POSITIONS TABLE SECTION
 # ======================================
 
 # positions header summary bar
-st.markdown(
-    f"""
+render_html(
+    f"""
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
-    """,
-    unsafe_allow_html=True
-)
+    """
+)
 
 # 포지션 rows -> 테이블용으로 가공
 table_rows = []
 for p in positions:
     table_rows.append({
         "Asset": p.get("symbol"),
         "Type": p.get("holdSide","").upper(),
         "Lev": f'{p.get("leverage","")}x',
         "Position Value": f'{fnum(p.get("marginSize",0.0))*fnum(p.get("leverage",0.0)):,.2f}',
         "Unrealized PnL": f'{fnum(p.get("unrealizedPL",0.0)):,.2f}',
         "Entry Price": p.get("openPriceAvg") or p.get("averageOpenPrice"),
         "Current Price": p.get("markPrice"),
         "Liq. Price": p.get("liquidationPrice"),
         "Margin Used": p.get("marginSize"),
     })
 
 st.markdown('<div class="positions-body">', unsafe_allow_html=True)
 st.dataframe(table_rows, use_container_width=True)
 st.markdown('</div>', unsafe_allow_html=True)
 
 # footer-ish
 st.caption(
     f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  •  Auto refresh hint: every {REFRESH_INTERVAL_SEC}s (manually rerun for now)"
 )
 
