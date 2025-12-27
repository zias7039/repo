# ui/table.py
import streamlit as st
from utils.format import render_html, normalize_symbol, fnum, safe_pct

def render_bottom_section(st, positions, nav_data, usdt_rate=None):
    st.markdown('<div style="margin-top:24px;"></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["보유 포지션", "투자자 현황", "주문 내역"])
    
    with tab1: _render_positions(positions)
    # [수정] usdt_rate 전달
    with tab2: _render_investors(nav_data, usdt_rate)
    with tab3: st.info("대기 중인 주문이 없습니다.")

def _render_positions(positions):
    header = """
    <div class="dashboard-card" style="padding:0; overflow:hidden; min-height:200px;">
        <div class="table-header">
            <div style="flex:1;">자산</div>
            <div style="flex:0.6; text-align:center;">포지션</div>
            <div style="flex:1.4; text-align:right;">수량 / 가치</div>
            <div style="flex:1.4; text-align:right;">미실현 손익</div>
            <div style="flex:1.1; text-align:right;">진입가</div>
            <div style="flex:1.1; text-align:right;">시장가</div>
            <div style="flex:1.1; text-align:right;">청산</div>
        </div>
    """
    rows = ""
    if not positions: rows = "<div style='padding:40px; text-align:center; color:#525252; font-size:0.85rem;'>No open positions</div>"
    
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
                <div style="font-weight:600; font-size:0.9rem; color:var(--text-primary);">{sym}</div>
                <div class="label" style="margin-top:2px;">{lev:.0f}x</div>
            </div>
            <div style="flex:0.6; text-align:center;">
                <span class="badge {badge}">{side_text}</span>
            </div>
            <div style="flex:1.4; text-align:right;">
                <div class="text-mono" style="color:var(--text-primary);">${val:,.0f}</div>
            </div>
            <div style="flex:1.4; text-align:right;">
                <div class="text-mono {pnl_cls}">${upl:+,.2f}</div>
                <div class="{pnl_cls} text-mono" style="font-size:0.75rem; margin-top:2px;">{roe:+.2f}%</div>
            </div>
            <div style="flex:1.1; text-align:right;"><span class="text-mono" style="font-size:0.9rem;">${entry:,.1f}</span></div>
            <div style="flex:1.1; text-align:right;"><span class="text-mono" style="font-size:0.9rem;">${mark:,.1f}</span></div>
            <div style="flex:1.1; text-align:right;"><span class="text-mono" style="color:#e0a040; font-size:0.9rem;">${liq:,.1f}</span></div>
        </div>
        """
    render_html(st, header + rows + "</div>")

def _render_investors(nav_data, usdt_rate=None):
    investors = nav_data.get("investors", {})
    current_nav = nav_data.get("nav", 1.0)
    total_units = nav_data.get("total_units", 1.0)
    
    header = """
    <div class="dashboard-card" style="padding:0; overflow:hidden; min-height:200px;">
        <div class="table-header">
            <div style="flex:1.5;">투자자</div>
            <div style="flex:1.2; text-align:right;">보유 좌수</div>
            <div style="flex:1.2; text-align:right;">지분율</div>
            <div style="flex:1.5; text-align:right;">평가액 (USDT)</div>
        </div>
    """
    rows = ""
    for name, units in sorted(investors.items(), key=lambda x: x[1], reverse=True):
        pct = (units / total_units * 100) if total_units else 0
        val_usd = units * current_nav
        initial = name.split()[-1][0] if " " in name else name[0]
        
        # [추가] KRW 표시
        krw_html = ""
        if usdt_rate:
            val_krw = val_usd * usdt_rate
            krw_html = f"<div style='font-size:0.75rem; color:#525252; margin-top:2px;'>≈₩{val_krw:,.0f}</div>"
        
        rows += f"""
        <div class="table-row">
            <div style="flex:1.5; display:flex; align-items:center; gap:12px;">
                <div style="width:24px; height:24px; background:#1f1f1f; border:1px solid #333; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:600; color:#fff;">{initial}</div>
                <div style="font-weight:500; font-size:0.9rem; color:var(--text-primary);">{name}</div>
            </div>
            <div style="flex:1.2; text-align:right;"><span class="text-mono" style="color:var(--text-secondary);">{units:,.2f}</span></div>
            <div style="flex:1.2; text-align:right;"><span class="text-mono text-up">{pct:.1f}%</span></div>
            <div style="flex:1.5; text-align:right;">
                <div class="text-mono" style="font-weight:600; color:var(--text-primary);">${val_usd:,.2f}</div>
                {krw_html}
            </div>
        </div>
        """
    footer = f"""<div style="padding:12px 20px; background:#141414; border-top:1px solid var(--border-color); text-align:right; font-size:0.75rem; color:var(--text-tertiary);">현재 NAV: <span class="text-mono" style="color:#fff;">${current_nav:,.4f}</span></div></div>"""
    render_html(st, header + rows + footer)
