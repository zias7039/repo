# ui/cards.py
from utils.format import render_html
import streamlit as st

def render_header(now_kst):
    """상단 로고 및 시스템 상태 바"""
    time_str = now_kst.strftime("%H:%M:%S")
    html = f"""
    <div class="dashboard-header">
        <div style="display:flex; align-items:center;">
            <span class="header-title">QUANTUM FUND</span>
            <span class="header-badge">MASTER</span>
            <div style="margin-left: 20px; font-size:0.8rem; color:var(--text-secondary);">
                NAV <span style="color:#2ebd85; font-weight:bold; margin-left:4px;">1.0000</span>
            </div>
        </div>
        <div style="display:flex; align-items:center; gap:15px; font-size:0.8rem;">
            <div style="color:var(--text-secondary);">Next Rebalance <span style="color:var(--text-primary); font-weight:bold;">04:00:00</span></div>
            <div style="background:#2ebd85; color:#000; font-weight:bold; padding:4px 12px; border-radius:4px; cursor:pointer;">Mint</div>
            <div style="background:#2b313a; color:#eaecef; padding:4px 12px; border-radius:4px; border:1px solid #444; cursor:pointer;">Redeem</div>
            <div style="width:30px; height:30px; background:#3b82f6; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold; color:white;">JS</div>
        </div>
    </div>
    """
    render_html(st, html)

def render_side_stats(total_equity, unrealized_total_pnl, roe_pct, usdt_krw):
    """우측 사이드바: 자산 현황 카드"""
    
    # 색상 로직
    upl_color = "var(--color-up)" if unrealized_total_pnl >= 0 else "var(--color-down)"
    krw_equity = total_equity * usdt_krw if usdt_krw else 0
    
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

def render_system_logs(logs):
    """우측 사이드바: 시스템 로그 (예시)"""
    log_html = ""
    for log in logs:
        color = "#2ebd85" if "Buy" in log['msg'] or "Mint" in log['msg'] else "#848e9c"
        if "Sell" in log['msg']: color = "#f6465d"
        
        log_html += f"""
        <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:6px;">
            <span style="color:{color}; font-weight:600;">{log['type']}</span>
            <span style="color:var(--text-primary);">{log['msg']}</span>
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
