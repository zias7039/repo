# ui/table.py
import streamlit as st
from utils.format import render_html, normalize_symbol, fnum, safe_pct

def positions_table(st, positions, funding_data):
    # 테이블 컨테이너 시작
    st.markdown('<div class="dashboard-card" style="padding:0; overflow:hidden;">', unsafe_allow_html=True)
    
    # 1. 헤더 (비율 조정: Symbol 넓게, 나머지 균등)
    # 비율: Sym(1.2) Side(0.6) Size(1.2) PNL(1.2) Entry(1) Mark(1) Liq(1) Margin(1)
    
    header_html = """
    <div class="trade-table-header">
        <div style="flex:1.2;">Symbol</div>
        <div style="flex:0.6; text-align:center;">Side</div>
        <div style="flex:1.2; text-align:right;">Size (USDT)</div>
        <div style="flex:1.2; text-align:right;">PNL (ROE)</div>
        <div style="flex:1; text-align:right;">Entry</div>
        <div style="flex:1; text-align:right;">Mark</div>
        <div style="flex:1; text-align:right;">Liq.</div>
        <div style="flex:1; text-align:right;">Margin</div>
    </div>
    """
    render_html(st, header_html)

    if not positions:
        st.markdown('<div style="padding:20px; text-align:center; color:#555;">No Active Positions</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True) # 카드 닫기
        return

    # 2. 데이터 행 렌더링
    for i, p in enumerate(positions):
        symbol = normalize_symbol(p.get("symbol", ""))
        side = p.get("holdSide", "").upper()
        lev = fnum(p.get("leverage", 0))
        mg = fnum(p.get("marginSize", 0))
        entry = fnum(p.get("averageOpenPrice", 0))
        mark = fnum(p.get("markPrice", 0))
        liq = fnum(p.get("liquidationPrice", 0))
        upl = fnum(p.get("unrealizedPL", 0))
        
        notional = mg * lev
        roe = safe_pct(upl, mg)
        
        pnl_color = "text-up" if upl >= 0 else "text-down"
        side_badge = f'<span style="color:var(--color-up); background:rgba(46,189,133,0.15); padding:2px 6px; border-radius:4px; font-size:0.7rem;">LONG</span>' if side == "LONG" else \
                     f'<span style="color:var(--color-down); background:rgba(246,70,93,0.15); padding:2px 6px; border-radius:4px; font-size:0.7rem;">SHORT</span>'

        row_html = f"""
        <div class="trade-row">
            <div style="flex:1.2; font-weight:600; color:var(--text-primary);">
                {symbol} <span style="color:var(--text-tertiary); font-size:0.75rem; font-weight:400; margin-left:4px;">{lev:.0f}x</span>
            </div>
            <div style="flex:0.6; text-align:center;">{side_badge}</div>
            <div style="flex:1.2; text-align:right;">
                <div class="text-mono" style="color:var(--text-primary);">${notional:,.0f}</div>
            </div>
            <div style="flex:1.2; text-align:right;">
                <div class="text-mono {pnl_color}">${upl:,.2f}</div>
                <div class="text-mono {pnl_color}" style="font-size:0.75rem;">{roe:+.2f}%</div>
            </div>
            <div style="flex:1; text-align:right;" class="text-mono text-label">${entry:,.1f}</div>
            <div style="flex:1; text-align:right;" class="text-mono text-label">${mark:,.1f}</div>
            <div style="flex:1; text-align:right;" class="text-mono" style="color:var(--color-yellow);">${liq:,.1f}</div>
            <div style="flex:1; text-align:right;" class="text-mono text-label">${mg:,.0f}</div>
        </div>
        """
        render_html(st, row_html)

    # 테이블 닫기
    st.markdown('</div>', unsafe_allow_html=True)
