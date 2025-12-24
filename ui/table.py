# ui/table.py
import streamlit as st
from utils.format import render_html, normalize_symbol, fnum, safe_pct

def positions_table(st, positions):
    # 헤더 정의
    header_html = """
    <div style="margin-top:20px; background:var(--bg-card); border-radius:8px; padding:0 24px 24px 24px;">
        <div class="table-header">
            <div style="flex:1;">Asset</div>
            <div style="flex:0.8; text-align:center;">Type</div>
            <div style="flex:1.5; text-align:right;">Position Value / Size</div>
            <div style="flex:1.5; text-align:right;">Unrealized PnL</div>
            <div style="flex:1.2; text-align:right;">Entry Price</div>
            <div style="flex:1.2; text-align:right;">Current Price</div>
            <div style="flex:1.2; text-align:right;">Liq. Price</div>
            <div style="flex:1.2; text-align:right;">Margin Used</div>
            <div style="flex:1.2; text-align:right;">Funding</div>
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
        type_badge = "background:#2b1010; color:#ff4d4d;" if side == "SHORT" else "background:#0f1814; color:#3dd995;"
        
        rows_html += f"""
        <div class="table-row">
            <div style="flex:1;">
                <div style="font-weight:700; font-size:0.95rem;">{sym}</div>
                <div style="font-size:0.75rem; color:var(--text-secondary);">{lev:.0f}x</div>
            </div>
            <div style="flex:0.8; text-align:center;">
                <span style="{type_badge} padding:4px 8px; border-radius:4px; font-size:0.75rem; font-weight:600;">{side}</span>
            </div>
            <div style="flex:1.5; text-align:right;">
                <div class="text-mono" style="font-size:1rem;">${val:,.2f}</div>
                <div class="text-mono" style="font-size:0.8rem; color:var(--text-secondary);">{size:.3f} {sym}</div>
            </div>
            <div style="flex:1.5; text-align:right;">
                <div class="text-mono {pnl_cls}" style="font-size:1rem;">${upl:+,.2f}</div>
                <div class="text-mono {pnl_cls}" style="font-size:0.8rem;">{roe:+.2f}%</div>
            </div>
            <div style="flex:1.2; text-align:right;" class="text-mono">${entry:,.2f}</div>
            <div style="flex:1.2; text-align:right;" class="text-mono">${mark:,.2f}</div>
            <div style="flex:1.2; text-align:right;" class="text-mono" style="color:#dba442;">${liq:,.2f}</div>
            <div style="flex:1.2; text-align:right;" class="text-mono">${margin:,.2f}</div>
            <div style="flex:1.2; text-align:right;" class="text-mono text-up">$0.00</div>
        </div>
        """

    footer = "</div>"
    render_html(st, header_html + rows_html + footer)
