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
    # 1. 헤더 (HTML) - CSS Grid와 비율을 맞춤
    header_html = """
    <div class="trade-table-container">
    <div class="trade-header">
        <div style="padding-left:4px;">Symbol</div>
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
        st.info("보유 중인 포지션이 없습니다.")
        return

    # 2. 데이터 행 (Streamlit Columns)
    # 헤더와 비율을 시각적으로 맞춤 (1.2, 0.7, 1.5, ...)
    cols_ratio = [1.2, 0.7, 1.5, 1.3, 1.0, 1.0, 1.0, 1.0, 1.0]

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

        # 행 사이 구분선
        st.markdown("""<div class="table-row-divider"></div>""", unsafe_allow_html=True)
        
        c = st.columns(cols_ratio, vertical_alignment="center")

        # [Col 1] 심볼 (투명 버튼 -> 클릭 시 차트 변경)
        with c[0]:
            if st.button(f"{symbol}\n{lev:.0f}x", key=f"btn_{i}"):
                st.session_state.selected_symbol = symbol
                st.rerun()

        # [Col 2] 방향
        with c[1]:
            st.markdown(side_badge(side), unsafe_allow_html=True)

        # [Col 3] Size
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
        
        # [Col 5~9] 나머지 숫자 데이터
        with c[4]: st.markdown(f"<div style='text-align:right;'>${entry:,.2f}</div>", unsafe_allow_html=True)
        with c[5]: st.markdown(f"<div style='text-align:right; color:var(--text-tertiary);'>${mark:,.2f}</div>", unsafe_allow_html=True)
        with c[6]: st.markdown(f"<div style='text-align:right; color:var(--color-down);'>${liq:,.2f}</div>", unsafe_allow_html=True)
        with c[7]: st.markdown(f"<div style='text-align:right;'>${mg:,.2f}</div>", unsafe_allow_html=True)
        with c[8]: st.markdown(f"<div style='text-align:right; color:{fund_color}; font-size:0.8rem;'>${fund_val:,.2f}</div>", unsafe_allow_html=True)
