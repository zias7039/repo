# app/app.py

# ... (임포트) ...
from services.fund import get_nav_metrics
# ui/cards.py에서 render_investor_breakdown 추가 임포트
from ui.cards import render_header, render_side_stats, render_system_logs, render_investor_breakdown

# ... (기존 설정 및 main 함수 앞부분 동일) ...

def main():
    inject_styles(st)
    
    # 1. 데이터 로드
    data = load_data()
    # ... (에러 처리) ...
    
    positions = data["positions"]
    account = data["account"]
    bills = data["bills"]
    
    metrics = calculate_metrics(account, positions)
    funding_data = process_funding(bills)
    
    # History 기록
    history_df, is_recorded_now = try_record_snapshot(metrics["total_equity"])
    if is_recorded_now:
        st.toast("✅ Daily Equity Snapshot Recorded!")
    
    # NAV 및 투자자 데이터 계산
    nav_data = get_nav_metrics(metrics["total_equity"], history_df)
    
    KST = timezone(timedelta(hours=9))
    now_kst = datetime.now(KST)

    # 2. UI: Header
    render_header(
        now_kst, 
        nav=nav_data["nav"], 
        nav_change=nav_data["change_pct"], 
        total_units=nav_data["total_units"]
    )

    # 3. UI: Main Grid
    col_main, col_side = st.columns([3, 1])

    with col_main:
        # ... (차트 및 테이블 코드 기존과 동일) ...
        selected_symbol, selected_gran = render_toolbar(positions)
        df = fetch_kline_futures(symbol=selected_symbol, granularity=selected_gran, product_type=PRODUCT_TYPE, limit=100)
        render_chart(df, f"{selected_symbol}")
        
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs([f"Positions ({len(positions)})", "Open Orders (0)", "Order History"])
        with tab1:
            positions_table(st, positions, funding_data)
        with tab2:
            st.info("No open orders.")
        with tab3:
            st.info("History feature coming soon.")

    with col_side:
        # [1] 자산 현황
        render_side_stats(
            total_equity=metrics["total_equity"],
            unrealized_total_pnl=metrics["unrealized_total_pnl"],
            roe_pct=metrics["roe_pct"],
            usdt_krw=data["usdt_krw"]
        )

        # [2] 투자자별 현황 (신규 추가)
        render_investor_breakdown(
            investors=nav_data["investors"],
            current_nav=nav_data["nav"],
            usdt_krw=data["usdt_krw"]
        )

        # [3] NAV 차트
        st.markdown("""<div class="side-card"><div class="stat-label">NAV Performance</div>""", unsafe_allow_html=True)
        # ... (차트 그리는 코드 기존과 동일) ...
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

        # [4] 로그
        render_system_logs([
            {"type": "INFO", "msg": "Rebalance check complete", "time": "12:30:05"},
            {"type": "NAV", "msg": "Settlement updated", "time": "12:00:00"},
            {"type": "INFO", "msg": "System online", "time": "11:59:59"}
        ])

    time.sleep(REFRESH_INTERVAL_SEC)
    st.rerun()

if __name__ == "__main__":
    main()
