# ui/cards.py (아래 함수를 추가하세요)
from utils.format import render_html
import streamlit as st

# ... (기존 render_header, render_side_stats 등은 유지) ...

def render_investor_breakdown(investors, current_nav, usdt_krw):
    """우측 사이드바: 투자자별 지분 현황"""
    
    rows_html = ""
    # 지분율 높은 순으로 정렬
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
