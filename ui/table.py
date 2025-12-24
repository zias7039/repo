# ui/table.py
import streamlit as st
from utils.format import render_html, normalize_symbol, fnum, safe_pct

def render_bottom_section(st, positions, nav_data):
    st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
    
    # [탭 메뉴] Investors 탭 추가
    tab1, tab2, tab3 = st.tabs(["Asset Positions", "Fund Investors", "Open Orders"])
    
    # --- Tab 1: Positions ---
    with tab1:
        _render_positions(positions)

    # --- Tab 2: Investors (New) ---
    with tab2:
        _render_investors(nav_data)
        
    with tab3:
        st.info("No open orders.")

def _render_positions(positions):
    """기존 포지션 테이블 렌더링"""
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
        </div>
    """
    
    rows = ""
    if not positions:
        rows = "<div style='padding:50px; text-align:center; color:#444;'>No open positions</div>"
    
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
        
        if side == "SHORT":
            badge = "background:rgba(255, 77, 77, 0.2); color:#ff6666;"
        else:
            badge = "background:rgba(61, 217, 149, 0.2); color:#3dd995;"
        
        side_text = side if side else "LONG"

        rows += f"""
        <div class="table-row">
            <div style="flex:1;">
                <div style="color:#fff; font-weight:700; font-size:0.9rem;">{sym}</div>
                <div style="color:#555; font-size:0.75rem;">{lev:.0f}x</div>
            </div>
            <div style="flex:0.6; text-align:center;">
                <span style="{badge} padding:3px 8px; border-radius:4px; font-size:0.7rem; font-weight:700;">{side_text}</span>
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
        </div>
        """
    render_html(st, header + rows + "</div>")

def _render_investors(nav_data):
    """[추가] 투자자 현황 테이블"""
    investors = nav_data.get("investors", {})
    current_nav = nav_data.get("nav", 1.0)
    total_units = nav_data.get("total_units", 1.0)
    
    header = """
    <div class="dashboard-card" style="padding:0; overflow:hidden; min-height:200px;">
        <div class="table-header">
            <div style="flex:1.5;">Investor Name</div>
            <div style="flex:1.5; text-align:right;">Units Held</div>
            <div style="flex:1.5; text-align:right;">Share (%)</div>
            <div style="flex:2; text-align:right;">Valuation (USDT)</div>
            <div style="flex:2; text-align:right;">Valuation (KRW) <span style="font-weight:400; font-size:0.7rem;">@1440</span></div>
        </div>
    """
    
    rows = ""
    sorted_inv = sorted(investors.items(), key=lambda x: x[1], reverse=True)
    
    for name, units in sorted_inv:
        pct = (units / total_units * 100) if total_units else 0
        val_usd = units * current_nav
        val_krw = val_usd * 1440 # 임시 환율
        
        # 이름별 아바타 색상
        avatar_bg = "#3b82f6" if "A" in name else "#8b5cf6"
        initial = name.split()[-1][0] if " " in name else name[0]
        
        rows += f"""
        <div class="table-row">
            <div style="flex:1.5; display:flex; align-items:center; gap:10px;">
                <div style="width:24px; height:24px; background:{avatar_bg}; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:bold; color:#fff;">{initial}</div>
                <div style="font-weight:600; font-size:0.9rem;">{name}</div>
            </div>
            <div style="flex:1.5; text-align:right;">
                <div style="font-family:var(--font-mono); font-size:0.95rem; color:#ddd;">{units:,.2f}</div>
            </div>
            <div style="flex:1.5; text-align:right;">
                <div style="font-family:var(--font-mono); font-size:0.95rem; color:var(--color-up);">{pct:.1f}%</div>
            </div>
            <div style="flex:2; text-align:right;">
                <div style="font-family:var(--font-mono); font-size:1rem; font-weight:600;">${val_usd:,.2f}</div>
            </div>
            <div style="flex:2; text-align:right;">
                <div style="font-family:var(--font-mono); font-size:0.95rem; color:#888;">₩{val_krw:,.0f}</div>
            </div>
        </div>
        """
        
    footer = f"""
    <div style="padding:12px 16px; background:#161616; border-top:1px solid #222; text-align:right; font-size:0.8rem; color:#666;">
        Current NAV: <span style="color:#fff; font-family:var(--font-mono);">${current_nav:,.4f}</span>
    </div>
    </div>
    """
    render_html(st, header + rows + footer)
