# ui/table.py
import streamlit as st
from utils.format import render_html, normalize_symbol, fnum, safe_pct

def side_badge(side: str):
    side = (side or "").upper()
    if side == "LONG":
        return '<span class="badge badge-long">Long</span>'
    elif side == "SHORT":
        return '<span class="badge badge-short">Short</span>'
    return f'<span class="badge" style="background:#333;">{side}</span>'

def positions_table(st, positions, funding_data):
    # 1. 테이블 헤더 (HTML 유지)
    header_html = """
    <div class="trade-table-container">
    <div class="trade-row trade-header">
        <div style="padding-left:4px;">Symbol (Click to View)</div>
        <div>Side</div>
        <div style="text-align:right;">Size / Value</div>
        <div style="text-align:right;">PNL (ROE)</div>
        <div style="text-align:right;">Entry</div>
        <div style="text-align:right;">Mark</div>
        <div style="text-align:right;">Liq.</div>
        <div style="text-align:right;">Margin</div>
        <div style="text-align:right;">Funding</div>
    </div>
    </div>
    """
    render_html(st, header_html)

    if not positions:
        render_html(st, """<div style="padding:32px; text-align:center; color:var(--text-secondary); background:var(--bg-card); border:1px solid var(--border-color); border-top:none; border-radius:0 0 8px 8px;">보유 중인 포지션이 없습니다.</div>""")
        return

    # 2. 데이터 행 (Streamlit Columns + Button 사용)
    # 기존 Grid 비율에 맞춰 컬럼 비율 조정
    # Grid: 1fr 0.8fr 1.5fr 1.2fr 1fr 1fr 1fr 1fr 1.2fr
    cols_ratio = [1.1, 0.7, 1.5, 1.3, 1.0, 1.0, 1.0, 1.0, 1.1]

    for i, p in enumerate(positions):
        symbol = normalize_symbol(p.get("symbol", ""))
        side = p.get("holdSide", "")
        lev = fnum(p.get("leverage", 0))
        mg = fnum(p.get("marginSize", 0))
        qty = fnum(p.get("total", 0))
        entry = fnum(p.get("averageOpenPrice", 0))
        mark = fnum(p.get("markPrice", 0))
        liq = fnum(p.get("liquidationPrice", 0))
        upl = fnum(p.get("unrealizedPL", 0))
        
        notional = mg * lev
        roe = safe_pct(upl, mg)
        pnl_cls = "var(--color-up)" if upl >= 0 else "var(--color-down)"
        
        fund_info = funding_data.get(symbol, {"cumulative": 0.0})
        fund_val = fund_info.get("cumulative", 0.0)
        fund_color = "var(--color-up)" if fund_val >= 0 else "var(--text-secondary)"

        # CSS로 만든 테이블과 유사하게 보이도록 컨테이너 구성
        with st.container():
            st.markdown("""<div class="table-row-divider"></div>""", unsafe_allow_html=True)
            c = st.columns(cols_ratio, vertical_alignment="center")

            # [Col 1] 심볼 (버튼으로 구현)
            with c[0]:
                # 버튼 클릭 시 세션 상태 업데이트 후 리런
                if st.button(f"{symbol}\n{lev:.0f}x", key=f"pos_btn_{i}"):
                    st.session_state.selected_symbol = symbol
                    st.rerun()

            # [Col 2] 방향
            with c[1]:
                st.markdown(side_badge(side), unsafe_allow_html=True)

            # [Col 3] Size / Value
            with c[2]:
                st.markdown(f"""<div style="text-align:right; line-height:1.2;">
                    <div style="color:var(--text-primary);">${notional:,.0f}</div>
                    <div style="font-size:0.75rem; color:var(--text-secondary);">{qty:,.3f}</div>
                </div>""", unsafe_allow_html=True)

            # [Col 4] PNL
            with c[3]:
                st.markdown(f"""<div style="text-align:right; line-height:1.2;">
                    <div style="font-weight:600; color:{pnl_cls};">${upl:,.2f}</div>
                    <div style="font-size:0.75rem; color:{pnl_cls};">{roe:+.2f}%</div>
                </div>""", unsafe_allow_html=True)
            
            # [Col 5~9] 나머지 데이터
            with c[4]: st.markdown(f"<div style='text-align:right;'>${entry:,.2f}</div>", unsafe_allow_html=True)
            with c[5]: st.markdown(f"<div style='text-align:right; color:var(--text-tertiary);'>${mark:,.2f}</div>", unsafe_allow_html=True)
            with c[6]: st.markdown(f"<div style='text-align:right; color:var(--color-down);'>${liq:,.2f}</div>", unsafe_allow_html=True)
            with c[7]: st.markdown(f"<div style='text-align:right;'>${mg:,.2f}</div>", unsafe_allow_html=True)
            with c[8]: st.markdown(f"<div style='text-align:right; color:{fund_color}; font-size:0.8rem;'>${fund_val:,.2f}</div>", unsafe_allow_html=True)
