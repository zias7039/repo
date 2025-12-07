# app/app.py
import time
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from utils.format import fnum
from services.upbit import fetch_usdt_krw
from services.bitget import fetch_positions, fetch_account, fetch_account_bills, fetch_kline_futures
from services.history import try_record_snapshot, load_history
from services.fund import get_nav_metrics  # [추가됨] NAV 및 투자자 데이터 관리
from ui.styles import inject as inject_styles
from ui.toolbar import render_toolbar
from ui.chart import render_chart
from ui.cards import render_header, render_side_stats, render_system_logs, render_investor_breakdown
from ui.table import positions_table

# ============ CONFIG ============
st.set_page_config(page_title="Quantum Fund", page_icon="📊", layout="wide")
PRODUCT_TYPE = "USDT-FUTURES"
MARGIN_COIN = "USDT"

if "bitget" not in st.secrets:
    st.error("Secrets에 'bitget' 설정이 없습니다.")
    st.stop()

API_KEY = st.secrets["bitget"]["api_key"]
API_SECRET = st.secrets["bitget"]["api_secret"]
PASSPHRASE = st.secrets["bitget"]["passphrase"]
REFRESH_INTERVAL_SEC = 10

# ============ LOGIC HELPERS ============
def load_data():
    pos_data, pos_res = fetch_positions(API_KEY, API_SECRET, PASSPHRASE, PRODUCT_TYPE, MARGIN_COIN)
    acct_data, acct_res = fetch_account(API_KEY, API_SECRET, PASSPHRASE, PRODUCT_TYPE, MARGIN_COIN)
    bills_data = fetch_account_bills(API_KEY, API_SECRET, PASSPHRASE, PRODUCT_TYPE, limit=100)
    usdt_krw = fetch_usdt_krw()
    
    return {
        "positions": pos_data,
        "account": acct_data,
        "bills": bills_data,
        "usdt_krw": usdt_krw,
        "errors": [
            f"포지션: {pos_res.get('msg')}" if pos_res.get("code") != "00000" else None,
            f"계정: {acct_res.get('msg')}" if acct_res.get("code") != "00000" else None,
        ]
    }

def process_funding(bills):
    funding_sum = defaultdict(float)
    for b in bills:
        bt = (b.get("businessType","") or "").lower()
        if ("settle_fee" in bt) or ("funding" in bt):
            sym = (b.get("symbol","") or "").split("_")[0].upper()
            funding_sum[sym] += fnum(b.get("amount", 0.0))
    return {k: {"cumulative": v} for k,v in funding_sum.items()}

def calculate_metrics(account, positions):
    available = fnum(account.get("available")) if account else 0.0
    locked    = fnum(account.get("locked")) if account else 0.0
    marg_acct = fnum(account.get("marginSize")) if account else 0.0
    
    if account and account.get("usdtEquity") is not None:
        total_equity = fnum(account.get("usdtEquity"))
    else:
        total_equity = available + locked + marg_acct

    total_position_value = 0.0
    unrealized_total_pnl = 0.0
    
    for p in positions:
        lev = fnum(p.get("leverage", 0.0))
        mg = fnum(p.get("marginSize", 0.0))
        total_position_value += (mg * lev)
        unrealized_total_pnl += fnum(p.get("unrealizedPL", 0.0))
        
    roe_pct = (unrealized_total_pnl / total_equity * 100) if total_equity > 0 else 0.0
    
    return {
        "total_equity": total_equity,
        "unrealized_total_pnl": unrealized_total_pnl,
        "roe_pct": roe_pct
    }

# ============ MAIN APP ============
def main():
    inject_styles(st)
    
    # 1. 데이터 로드
    data = load_data()
    for err in data["errors"]:
        if err: st.error(err)
        
    positions = data["positions"]
    account = data["account"]
    bills = data["bills"]
    
    metrics = calculate_metrics(account, positions)
    funding_data = process_funding(bills)
    
    # 2. 자산 기록 (History) 및 NAV 계산
    history_df, is_recorded_now = try_record_snapshot(metrics["total_equity"])
    if is_recorded_now:
        st.toast("✅ Daily Equity Snapshot Recorded!")
    
    # NAV 및 투자자 데이터 계산
    nav_data = get_nav_metrics(metrics["total_equity"], history_df)
    
    # KST 시간 설정
    KST = timezone(timedelta(hours=9))
    now_kst = datetime.now(KST)

    # 3. UI: Header (NAV 정보 표시)
    render_header(
        now_kst, 
        nav=nav_data["nav"], 
        nav_change=nav_data["change_pct"], 
        total_units=nav_data["total_units"]
    )

    # 4. UI: Main Grid (3:1 비율)
    col_main, col_side = st.columns([3, 1])

    # [좌측] 메인 차트 및 포지션 테이블
    with col_main:
        selected_symbol, selected_gran = render_toolbar(positions)
        
        # 캔들 차트
        df = fetch_kline_futures(symbol=selected_symbol, granularity=selected_gran, product_type=PRODUCT_TYPE, limit=100)
        render_chart(df, f"{selected_symbol}")
        
        # 탭 (포지션 / 대기주문 / 내역)
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs([f"Positions ({len(positions)})", "Open Orders (0)", "Order History"])
        
        with tab1:
            positions_table(st, positions, funding_data)
        with tab2:
            st.info("No open orders.")
        with tab3:
            st.info("History feature coming soon.")

    # [우측] 사이드바 정보 (자산, 투자자, NAV차트, 로그)
    with col_side:
        # (1) 자산 현황 카드
        render_side_stats(
            total_equity=metrics["total_equity"],
            unrealized_total_pnl=metrics["unrealized_total_pnl"],
            roe_pct=metrics["roe_pct"],
            usdt_krw=data["usdt_krw"]
        )

        # (2) 투자자별 현황 카드 (New)
        render_investor_breakdown(
            investors=nav_data["investors"],
            current_nav=nav_data["nav"],
            usdt_krw=data["usdt_krw"]
        )

        # (3) NAV 퍼포먼스 차트
        st.markdown("""<div class="side-card"><div class="stat-label">NAV Performance</div>""", unsafe_allow_html=True)
        
        if history_df.empty:
            chart_df = pd.DataFrame({"date": [now_kst.strftime("%Y-%m-%d")], "equity": [metrics["total_equity"]]})
        else:
            chart_df = history_df.copy()
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=chart_df["date"], 
            y=chart_df["equity"],
            mode='lines',
            line=dict(color='#2ebd85', width=2),
            fill='tozeroy',
            fillcolor='rgba(46, 189, 133, 0.1)'
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=200,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=True, gridcolor="#2b313a", showticklabels=True, tickfont=dict(size=10)),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        # (4) 시스템 로그 (예시 데이터)
        logs = [
            {"type": "INFO", "msg": "Rebalance check complete", "time": "12:30:05"},
            {"type": "NAV", "msg": "Settlement updated", "time": "12:00:00"},
            {"type": "INFO", "msg": "System online", "time": "11:59:59"}
        ]
        render_system_logs(logs)
    # [디버깅용] 사이드바에 강제 저장 버튼 추가
    with st.sidebar:
        st.markdown("---")
        st.write("🔧 관리자 메뉴")
        if st.button("💾 자산 데이터 강제 저장"):
            # force=True로 호출
            _, saved = try_record_snapshot(metrics["total_equity"], force=True)
            if saved:
                st.toast(f"✅ 현재 자산(${metrics['total_equity']:,.2f})이 강제 저장되었습니다!")
                time.sleep(1)
                st.rerun() # 새로고침하여 차트 즉시 반영

    time.sleep(REFRESH_INTERVAL_SEC)
    st.rerun()

if __name__ == "__main__":
    main()

