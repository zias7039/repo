# ui/cards.py
import streamlit as st
from utils.format import render_html

def render_header(now_kst, nav, nav_change, total_units, next_rebalance="09:00:00", user_initials="JS"):
    """상단 헤더: 펀드 로고, NAV 현황, 시스템 상태 표시"""
    
    color = "#2ebd85" if nav_change >= 0 else "#f6465d"
    sign = "+" if nav_change >= 0 else ""
    
    # HTML 구조 유지
    html = f"""
    <div class="dashboard-header">
        <div style="display:flex; align-items:center;">
            <span class="header-title">QUANTUM FUND</span>
            <span class="header-badge">MASTER</span>
            
            <div style="margin-left: 24px; display:flex; align-items:baseline; gap:6px;">
                <span style="font-size:0.8rem; color:var(--text-secondary);">NAV</span>
                <span style="font-size:1.3rem; font-weight:700; color:{color}; font-family:'JetBrains Mono';">
                    {nav:.4f}
                </span>
                <span style="font-size:0.85rem; font-weight:600; color:{color}; background:{color}20; padding:2px 6px; border-radius:4px;">
                    {sign}{nav_change:.2f}%
                </span>
            </div>
            
            <div style="margin-left: 20px; font-size:0.8rem; color:var(--text-secondary);">
                TOTAL UNITS <span style="color:var(--text-primary); font-weight:bold; margin-left:4px;">{total_units:,.2f}</span>
            </div>
        </div>

        <div style="display:flex; align-items:center; gap:15px; font-size:0.8rem;">
            <div style="color:var(--text-secondary);">Next Rebalance <span style="color:var(--text-primary); font-weight:bold;">{next_rebalance}</span></div>
            <div style="background:#2ebd85; color:#000; font-weight:bold; padding:4px 12px; border-radius:4px; cursor:pointer;">Mint</div>
            <div style="background:#2b313a; color:#eaecef; padding:4px 12px; border-radius:4px; border:1px solid #444; cursor:pointer;">Redeem</div>
            <div style="width:30px; height:30px; background:#3b82f6; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; color:white;">{user_initials}</div>
        </div>
    </div>
    """
    render_html(st, html)

def render_side_stats(total_equity, unrealized_total_pnl, roe_pct, usdt_krw):
    """우측 사이드바: 자산 현황 카드"""
    upl_color = "var(--color-up)" if unrealized_total_pnl >= 0 else "var(--color-down)"
    krw_equity = total_equity * (usdt_krw or 0)
    
    html = f"""
    <div class="side-card">
        <div class="stat-label">총 자산 (Total Equity)</div>
        <div class="stat-value">${total_equity:,.2f}</div>
        <div class="stat-sub" style="color:var(--text-secondary);">≈ ₩{krw_equity:,.0f}</div>
        
        <div style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div style="background:var(--bg-app); padding:10px; border-radius:4px;">
                <div style="font-size:0.75rem; color:var(--text-secondary);">Unrealized PnL</div>
                <div style="font-size:1.1rem; font-weight:bold; color:{upl_color};">
                    ${unrealized_total_pnl:+.2f}
                </div>
                <div style="font-size:0.8rem; color:{upl_color};">{roe_pct:+.2f}%</div>
            </div>
            <div style="background:var(--bg-app); padding:10px; border-radius:4px;">
                <div style="font-size:0.75rem; color:var(--text-secondary);">USDT Price</div>
                <div style="font-size:1.1rem; font-weight:bold; color:var(--color-accent);">
                    ₩{usdt_krw:,.0f}
                </div>
                <div style="font-size:0.8rem; color:var(--text-secondary);">Upbit</div>
            </div>
        </div>
    </div>
    """
    render_html(st, html)

def render_investor_breakdown(investors, current_nav, usdt_krw):
    """우측 사이드바: 투자자별 지분 현황 리스트"""
    rows_html = ""
    sorted_investors = sorted(investors.items(), key=lambda item: item[1], reverse=True)
    total_units = sum(investors.values())
    
    for name, units in sorted_investors:
        valuation_usd = units * current_nav
        valuation_krw = valuation_usd * (usdt_krw if usdt_krw else 1400)
        share_pct = (units / total_units * 100) if total_units else 0
        
        rows_html += f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1px solid #2b313a; padding-bottom:8px;">
            <div>
                <div style="font-size:0.85rem; font-weight:600; color:var(--text-primary);">{name}</div>
                <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:2px;">
                    {units:,.2f} Units <span style="color:#2b313a; margin:0 4px;">|</span> {share_pct:.1f}%
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.9rem; font-weight:600; color:var(--text-primary);">${valuation_usd:,.2f}</div>
                <div style="font-size:0.75rem; color:var(--text-secondary);">₩{valuation_krw:,.0f}</div>
            </div>
        </div>
        """

    html = f"""
    <div class="side-card">
        <div class="stat-label" style="margin-bottom:12px;">Investors (Shareholders)</div>
        {rows_html}
        <div style="text-align:right; font-size:0.75rem; color:var(--text-secondary); margin-top:8px;">
            * Based on NAV ${current_nav:,.4f}
        </div>
    </div>
    """
    render_html(st, html)

def render_system_logs(logs):
    """우측 사이드바: 시스템 로그 표시"""
    log_html = ""
    for log in logs:
        msg = log.get('msg', '')
        color = "#2ebd85" if "Buy" in msg or "Mint" in msg else "#848e9c"
        if "Sell" in msg: color = "#f6465d"
        
        log_html += f"""
        <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:6px;">
            <span style="color:{color}; font-weight:600;">{log['type']}</span>
            <span style="color:var(--text-primary);">{msg}</span>
            <span style="color:var(--text-secondary);">{log['time']}</span>
        </div>
        """
    
    html = f"""
    <div class="side-card">
        <div class="stat-label" style="margin-bottom:10px;">System Logs</div>
        {log_html}
    </div>
    """
    render_html(st, html)
