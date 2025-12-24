# ui/table.py
import streamlit as st
from utils.format import render_html, normalize_symbol, fnum, safe_pct

def positions_table(st, positions):
    st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
    
    # 탭 메뉴
    st.markdown("""
    <div style="display:flex; gap:20px; border-bottom:1px solid #222; padding-bottom:10px; margin-bottom:10px;">
        <span style="color:#3dd995; font-weight:600; font-size:0.9rem; border-bottom:2px solid #3dd995; padding-bottom:8px;">Asset Positions</span>
        <span style="color:#666; font-size:0.9rem; cursor:pointer;">Open Orders</span>
        <span style="color:#666; font-size:0.9rem; cursor:pointer;">Recent Fills</span>
    </div>
    """, unsafe_allow_html=True)

    header = """
    <div class="dashboard-card" style="padding:0; overflow:hidden; min-height:200px;">
        <div class="table-header">
            <div style="flex:1;">Asset</div>
            <div style="flex:0.6; text-align:center;">Type</div>
            <div style="flex:1.4; text-align:right;">Size / Value</div>
            <div style="flex:1.4; text-align:right;">Unrealized PnL</div>
            <div style="flex:1.1; text-align:right;">Entry</div>
            <div style="flex:1.1; text-align:right;">Mark</div>
            <div style="flex:1.1; text-align:right;">Liq.</div>
            <div style="flex:1.1; text-align:right;">Margin</div>
            <div style="flex:1.1; text-align:right;">Funding</div>
        </div>
    """
    
    rows = ""
    if not positions:
        rows = "<div style='padding:50px; text-align:center; color:#444;'>No open positions</div>"
    
    for p in positions:
        sym = normalize_symbol(p.get("symbol"))
        side = p.get("holdSide", "LONG")
        lev = fnum(p.get("leverage"))
        upl = fnum(p.get("unrealizedPL"))
        margin = fnum(p.get("marginSize"))
        entry = fnum(p.get("averageOpenPrice"))
        mark = fnum(p.get("markPrice"))
        liq = fnum(p.get("liquidationPrice"))
        
        val = margin * lev
        roe = safe_pct(upl, margin)
        pnl_cls = "text-up" if upl >= 0 else "text-down"
        badge = "background:rgba(255, 77, 77, 0.15); color:#ff4d4d;" if side=="SHORT" else "background:rgba(61, 217, 149, 0.15); color:#3dd995;"
        
        rows += f"""
        <div class="table-row">
            <div style="flex:1;">
                <div style="color:#fff; font-weight:700; font-size:0.9rem;">{sym}</div>
                <div style="color:#555; font-size:0.75rem;">{lev:.0f}x</div>
            </div>
            <div style="flex:0.6; text-align:center;">
                <span style="{badge} padding:2px 6px; border-radius:3px; font-size:0.7rem; font-weight:700;">{side}</span>
            </div>
            <div style="flex:1.4; text-align:right;">
                <div style="font-family:var(--font-mono); font-size:0.95rem;">${val:,.0f}</div>
            </div>
            <div style="flex:1.4; text-align:right;">
                <div class="{pnl_cls}" style="font-family:var(--font-mono); font-size:0.95rem;">${upl:+,.2f}</div>
                <div class="{pnl_cls}" style="font-size:0.75rem;">{roe:+.2f}%</div>
            </div>
            <div style="flex:1.1; text-align:right; font-family:var(--font-mono); font-size:0.9rem;">${entry:,.1f}</div>
            <div style="flex:1.1; text-align:right; font-family:var(--font-mono); font-size:0.9rem;">${mark:,.1f}</div>
            <div style="flex:1.1; text-align:right; font-family:var(--font-mono); font-size:0.9rem; color:#e0a040;">${liq:,.1f}</div>
            <div style="flex:1.1; text-align:right; font-family:var(--font-mono); font-size:0.9rem;">${margin:,.0f}</div>
            <div style="flex:1.1; text-align:right; font-family:var(--font-mono); font-size:0.9rem;" class="text-up">$0.00</div>
        </div>
        """
        
    render_html(st, header + rows + "</div>")
