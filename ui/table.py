# ui/table.py
import streamlit as st
from utils.format import render_html, normalize_symbol, fnum, safe_pct

def positions_table(st, positions):
    # 헤더
    header_html = """
    <div style="margin-top:20px;">
    <div class="dashboard-card" style="padding:0; overflow:hidden;">
        <div class="table-header">
            <div style="flex:1;">Asset</div>
            <div style="flex:0.6; text-align:center;">Type</div>
            <div style="flex:1.4; text-align:right;">Position Value / Size</div>
            <div style="flex:1.4; text-align:right;">Unrealized PnL</div>
            <div style="flex:1.1; text-align:right;">Entry Price</div>
            <div style="flex:1.1; text-align:right;">Current Price</div>
            <div style="flex:1.1; text-align:right;">Liq. Price</div>
            <div style="flex:1.1; text-align:right;">Margin Used</div>
            <div style="flex:1.1; text-align:right;">Funding</div>
        </div>
    """
    
    rows_html = ""
    
    if not positions:
        rows_html = "<div style='padding:40px; text-align:center; color:#555;'>No open positions</div>"
    
    for p in positions:
        sym = normalize_symbol(p.get("symbol", ""))
        side = p.get("holdSide", "").upper()
        lev = fnum(p.get("leverage", 0))
        size = fnum(p.get("total", 0))
        entry = fnum(p.get("averageOpenPrice", 0))
        mark = fnum(p.get("markPrice", 0))
        liq = fnum(p.get("liquidationPrice", 0))
        upl = fnum(p.get("unrealizedPL", 0))
        margin = fnum(p.get("marginSize", 0))
        
        val = margin * lev
        roe = safe_pct(upl, margin)
        
        pnl_cls = "text-up" if upl >= 0 else "text-down"
        
        # 뱃지 스타일
        badge_style = "background:#2b1010; color:#ff4d4d;" if side == "SHORT" else "background:#0f1814; color:#3dd995;"
        
        rows_html += f"""
        <div class="table-row">
            <div style="flex:1;">
                <div style="font-weight:700; font-size:0.9rem; color:var(--text-primary);">{sym}</div>
                <div style="font-size:0.7rem; color:var(--text-tertiary);">{lev:.0f}x</div>
            </div>
            <div style="flex:0.6; text-align:center;">
                <span style="{badge_style} padding:3px 8px; border-radius:4px; font-size:0.7rem; font-weight:600;">{side}</span>
            </div>
            <div style="flex:1.4; text-align:right;">
                <div class="value" style="font-size:0.95rem;">${val:,.2f}</div>
                <div style="font-size:0.75rem; color:var(--text-tertiary);">{size:.3f} {sym}</div>
            </div>
            <div style="flex:1.4; text-align:right;">
                <div class="{pnl_cls} value" style="font-size:0.95rem;">${upl:+,.2f}</div>
                <div class="{pnl_cls}" style="font-size:0.75rem;">{roe:+.2f}%</div>
            </div>
            <div style="flex:1.1; text-align:right;" class="value" style="font-size:0.9rem;">${entry:,.2f}</div>
            <div style="flex:1.1; text-align:right;" class="value" style="font-size:0.9rem;">${mark:,.2f}</div>
            <div style="flex:1.1; text-align:right;" class="value" style="font-size:0.9rem; color:#e0a040;">${liq:,.2f}</div>
            <div style="flex:1.1; text-align:right;" class="value" style="font-size:0.9rem;">${margin:,.2f}</div>
            <div style="flex:1.1; text-align:right;" class="text-up" style="font-size:0.85rem;">$0.00</div>
        </div>
        """

    footer = "</div></div>" # 카드 닫기
    render_html(st, header_html + rows_html + footer)
