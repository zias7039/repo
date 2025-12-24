# ui/table.py
import streamlit as st
from utils.format import render_html, normalize_symbol, fnum, safe_pct

def render_bottom_section(st, positions, nav_data):
    st.markdown('<div style="margin-top:24px;"></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["POSITIONS", "INVESTORS", "ORDERS"])
    
    with tab1: _render_positions(positions)
    with tab2: _render_investors(nav_data)
    with tab3: st.info("No open orders.")

def _render_positions(positions):
    header = """
    <div class="dashboard-card" style="padding:0; overflow:hidden; min-height:200px;">
        <div class="table-header">
            <div style="flex:1;">Asset</div>
            <div style="flex:0.6; text-align:center;">Side</div>
            <div style="flex:1.4; text-align:right;">Size / Value</div>
            <div style="flex:1.4; text-align:right;">Unrealized PnL</div>
            <div style="flex:1.1; text-align:right;">Entry</div>
            <div style="flex:1.1; text-align:right;">Mark</div>
            <div style="flex:1.1; text-align:right;">Liq.</div>
        </div>
    """
    rows = ""
    if not positions: rows = "<div style='padding:40px; text-align:center; color:#444; font-size:0.8rem;'>No open positions</div>"
    
    for p in positions:
        sym = normalize_symbol(p.get("symbol"))
        side = str(p.get("holdSide", "")).upper()
        lev = fnum(p.get("leverage"))
        upl = fnum(p.get("unrealizedPL"))
        margin = fnum(p.get("marginSize"))
        entry = fnum(p.get("averageOpenPrice"))
        mark = fnum(p.get("markPrice"))
        liq = fnum(p.get("liquidationPrice"))
        val = margin * lev
        roe = safe_pct(upl, margin)
        pnl_cls = "text-up" if upl >= 0 else "text-down"
        badge = "badge-up" if side != "SHORT" else "badge-down"
        side_text = side if side else "LONG"

        rows += f"""
        <div class="table-row">
            <div style="flex:1;">
                <div style="font-weight:600; font-size:0.9rem;">{sym}</div>
                <div class="label" style="margin-top:2px;">{lev:.0f}x</div>
            </div>
            <div style="flex:0.6; text-align:center;">
                <span class="badge {badge}">{side_text}</span>
            </div>
            <div style="flex:1.4; text-align:right;">
                <div class="value">${val:,.0f}</div>
            </div>
            <div style="flex:1.4; text-align:right;">
                <div class="value {pnl_cls}">${upl:+,.2f}</div>
                <div class="{pnl_cls} text-mono" style="font-size:0.75rem; margin-top:2px;">{roe:+.2f}%</div>
            </div>
            <div style="flex:1.1; text-align:right;"><span class="value">${entry:,.1f}</span></div>
            <div style="flex:1.1; text-align:right;"><span class="value">${mark:,.1f}</span></div>
            <div style="flex:1.1; text-align:right;"><span class="value" style="color:#e0a040;">${liq:,.1f}</span></div>
        </div>
        """
    render_html(st, header + rows + "</div>")

def _render_investors(nav_data):
    investors = nav_data.get("investors", {})
    current_nav = nav_data.get("nav", 1.0)
    total_units = nav_data.get("total_units", 1.0)
    
    header = """
    <div class="dashboard-card" style="padding:0; overflow:hidden; min-height:200px;">
        <div class="table-header">
            <div style="flex:1.5;">Investor</div>
            <div style="flex:1.2; text-align:right;">Units</div>
            <div style="flex:1.2; text-align:right;">Share</div>
            <div style="flex:1.5; text-align:right;">Valuation (USDT)</div>
        </div>
    """
    rows = ""
    for name, units in sorted(investors.items(), key=lambda x: x[1], reverse=True):
        pct = (units / total_units * 100) if total_units else 0
        val_usd = units * current_nav
        initial = name.split()[-1][0] if " " in name else name[0]
        
        rows += f"""
        <div class="table-row">
            <div style="flex:1.5; display:flex; align-items:center; gap:10px;">
                <div style="width:22px; height:22px; background:#222; border:1px solid #333; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:600; color:#fff;">{initial}</div>
                <div style="font-weight:600; font-size:0.9rem;">{name}</div>
            </div>
            <div style="flex:1.2; text-align:right;"><span class="value" style="color:var(--text-secondary);">{units:,.2f}</span></div>
            <div style="flex:1.2; text-align:right;"><span class="value text-up">{pct:.1f}%</span></div>
            <div style="flex:1.5; text-align:right;"><span class="value" style="font-weight:700;">${val_usd:,.2f}</span></div>
        </div>
        """
    footer = f"""<div style="padding:10px 16px; background:#0f0f0f; border-top:1px solid var(--border-color); text-align:right; font-size:0.75rem; color:var(--text-tertiary);">NAV: <span class="text-mono" style="color:#fff;">${current_nav:,.4f}</span></div></div>"""
    render_html(st, header + rows + footer)
