# ui/cards.py
import streamlit as st
from utils.format import render_html

def render_header(now_kst, nav, nav_change, total_units, next_rebalance="09:00:00", user_initials="JS"):
    """상단 고정 헤더바"""
    color_class = "text-up" if nav_change >= 0 else "text-down"
    sign = "+" if nav_change >= 0 else ""
    
    html = f"""
    <div class="header-container">
        <div style="display:flex; align-items:center;">
            <div class="app-title">
                QUANTUM FUND <span class="badge-master">MASTER</span>
            </div>
            <div style="width: 1px; height: 24px; background: var(--border-color); margin: 0 24px;"></div>
            
            <div style="display:flex; flex-direction:column; justify-content:center;">
                <span class="text-label" style="line-height:1;">NAV</span>
                <div style="display:flex; align-items:baseline; gap:8px; margin-top:2px;">
                    <span class="text-mono" style="font-size:1.1rem; font-weight:700;">{nav:.4f}</span>
                    <span class="{color_class} text-mono" style="font-size:0.8rem;">{sign}{nav_change:.2f}%</span>
                </div>
            </div>

            <div style="margin-left: 32px; display:flex; flex-direction:column; justify-content:center;">
                <span class="text-label" style="line-height:1;">TOTAL UNITS</span>
                <span class="text-mono" style="font-size:1.1rem; font-weight:700; margin-top:2px; color:var(--text-primary);">{total_units:,.2f}</span>
            </div>
        </div>

        <div style="display:flex; align-items:center; gap:12px;">
            <div style="text-align:right; margin-right:12px;">
                <div class="text-label">Next Rebalance</div>
                <div class="text-mono" style="color:var(--text-primary);">{next_rebalance}</div>
            </div>
            <button class="btn-primary">Mint</button>
            <button class="btn-outline">Redeem</button>
            <div style="width:32px; height:32px; background:#2b313a; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#fff; font-size:0.8rem; font-weight:bold;">
                {user_initials}
            </div>
        </div>
    </div>
    """
    render_html(st, html)

def render_side_stats(total_equity, unrealized_total_pnl, roe_pct, usdt_krw):
    """우측 사이드바: 자산 카드"""
    pnl_class = "text-up" if unrealized_total_pnl >= 0 else "text-down"
    krw_equity = total_equity * (usdt_krw or 1400)
    
    html = f"""
    <div class="dashboard-card">
        <div class="text-label" style="margin-bottom:4px;">Total Equity (USDT)</div>
        <div class="text-mono text-xl">${total_equity:,.2f}</div>
        <div class="text-mono text-secondary" style="font-size:0.9rem; margin-top:2px;">≈ ₩{krw_equity:,.0f}</div>
        
        <div style="margin-top:20px; padding-top:16px; border-top:1px solid var(--border-color); display:flex; justify-content:space-between;">
            <div>
                <div class="text-label">Unrealized PnL</div>
                <div class="text-mono {pnl_class}" style="font-size:1.0rem; font-weight:600; margin-top:4px;">
                    ${unrealized_total_pnl:+.2f}
                </div>
            </div>
            <div style="text-align:right;">
                <div class="text-label">ROE%</div>
                <div class="text-mono {pnl_class}" style="font-size:1.0rem; font-weight:600; margin-top:4px;">
                    {roe_pct:+.2f}%
                </div>
            </div>
        </div>
        
         <div style="margin-top:16px; padding-top:16px; border-top:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center;">
             <div class="text-label">USDT Price (Upbit)</div>
             <div class="text-mono" style="color:var(--color-yellow);">₩{usdt_krw:,.0f}</div>
         </div>
    </div>
    """
    render_html(st, html)

def render_investor_breakdown(investors, current_nav, usdt_krw):
    """투자자 리스트 카드"""
    rows_html = ""
    sorted_inv = sorted(investors.items(), key=lambda x: x[1], reverse=True)
    total_units = sum(investors.values()) or 1

    for name, units in sorted_inv:
        pct = (units / total_units) * 100
        val_usd = units * current_nav
        
        rows_html += f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <div>
                <div style="font-size:0.9rem; font-weight:600; color:var(--text-primary);">{name}</div>
                <div class="text-mono text-label">{units:,.0f} Units ({pct:.1f}%)</div>
            </div>
            <div class="text-mono" style="text-align:right; font-size:0.9rem;">
                ${val_usd:,.0f}
            </div>
        </div>
        """
        
    html = f"""
    <div class="dashboard-card">
        <div class="text-label" style="margin-bottom:12px;">Investors</div>
        {rows_html}
    </div>
    """
    render_html(st, html)

def render_system_logs(logs):
    """로그 카드"""
    log_rows = ""
    for log in logs[:5]:
        color = "#2ebd85" if "Buy" in log['msg'] or "synced" in log['msg'] else "#848e9c"
        log_rows += f"""
        <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:6px;">
            <div style="display:flex; gap:8px;">
                <span style="color:{color}; font-weight:700;">[{log['type']}]</span>
                <span style="color:var(--text-secondary);">{log['msg']}</span>
            </div>
            <span class="text-mono" style="color:var(--text-tertiary);">{log['time']}</span>
        </div>
        """
    
    html = f"""
    <div class="dashboard-card" style="min-height:150px;">
        <div class="text-label" style="margin-bottom:10px;">System Logs</div>
        {log_rows}
    </div>
    """
    render_html(st, html)
