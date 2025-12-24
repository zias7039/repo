# ui/cards.py
import streamlit as st
from utils.format import render_html, fnum

def render_top_bar(total_equity, available, leverage, next_refresh="20s"):
    html = f"""
    <div style="display:flex; gap:32px; margin-bottom:20px; align-items:flex-start; padding: 0 4px;">
        <div>
            <div class="label" style="margin-bottom:2px;">TOTAL VALUE <span class="badge badge-neutral" style="vertical-align:text-top;">COMBINED</span></div>
            <div class="value-xl">${total_equity:,.2f}</div>
        </div>
        <div>
            <div class="label" style="margin-bottom:2px;">WITHDRAWABLE</div>
            <div class="value-xl">${available:,.2f}</div>
            <div style="font-size:0.65rem; color:var(--text-tertiary); margin-top:2px;">Free margin: 74.5%</div>
        </div>
        <div>
            <div class="label" style="margin-bottom:2px;">LEVERAGE</div>
            <div class="value-xl" style="display:flex; align-items:center; gap:6px;">
                {leverage:.2f}x <span class="badge badge-up" style="font-size:0.7rem;">ACTIVE</span>
            </div>
            <div style="font-size:0.65rem; color:var(--text-tertiary); margin-top:2px;">Notional: ${(total_equity * leverage):,.2f}</div>
        </div>
        <div style="flex-grow:1; text-align:right; padding-top:4px;">
             <div style="font-size:0.7rem; color:var(--text-tertiary);">Auto-refresh in {next_refresh}</div>
        </div>
    </div>
    """
    render_html(st, html)

def render_left_summary(perp_equity, margin_usage, unrealized_pnl, roe_pct, positions):
    # Delta 계산
    long_delta = sum(fnum(p.get('marginSize', 0)) * fnum(p.get('leverage', 0)) for p in positions if str(p.get('holdSide')).upper() == 'LONG')
    short_delta = sum(fnum(p.get('marginSize', 0)) * fnum(p.get('leverage', 0)) for p in positions if str(p.get('holdSide')).upper() == 'SHORT')
    net_delta = long_delta - short_delta
    total_exposure = long_delta + short_delta
    
    # Bias 판단
    equity_base = perp_equity if perp_equity > 0 else 1.0
    delta_ratio = net_delta / equity_base
    if delta_ratio > 0.05: bias_text, bias_color, bias_badge = "LONG", "var(--color-up)", "badge-up"
    elif delta_ratio < -0.05: bias_text, bias_color, bias_badge = "SHORT", "var(--color-down)", "badge-down"
    else: bias_text, bias_color, bias_badge = "NEUTRAL", "var(--text-secondary)", "badge-neutral"

    long_pct = (long_delta / total_exposure * 100) if total_exposure > 0 else 0
    short_pct = (short_delta / total_exposure * 100) if total_exposure > 0 else 0
    pnl_cls = "text-up" if unrealized_pnl >= 0 else "text-down"
    pnl_sign = "+" if unrealized_pnl >= 0 else ""

    # HTML 렌더링 (고정 높이 및 flexbox 배분)
    html = f"""
    <div class="dashboard-card" style="height:400px; padding:20px; display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div class="label">PERP EQUITY</div>
            <div class="value-xl">${perp_equity:,.2f}</div>
            
            <div class="flex-between" style="margin-top:12px;">
                <span class="label">Margin Usage</span>
                <span class="text-mono" style="font-size:0.8rem; font-weight:600;">{margin_usage:.2f}%</span>
            </div>
            <div class="progress-bg">
                <div class="progress-fill" style="width:{min(margin_usage,100)}%; background:var(--color-up);"></div>
            </div>
        </div>
        
        <div style="border-top:1px solid var(--border-color); padding-top:16px;">
            <div class="flex-between">
                <span class="label">DIRECTION BIAS</span>
                <span class="badge {bias_badge}">{bias_text}</span>
            </div>
            <div class="flex-between" style="margin-top:6px;">
                <span class="label">Net Delta</span>
                <span class="text-mono" style="color:{bias_color}; font-size:0.85rem; font-weight:600;">{(delta_ratio*100):+.2f}%</span>
            </div>
            <div class="progress-bg" style="display:flex; background:#222; height:6px; margin-top:8px;">
                <div style="width:{long_pct}%; background:var(--color-up);"></div>
                <div style="width:{short_pct}%; background:var(--color-down);"></div>
            </div>
            <div class="flex-between" style="margin-top:6px; font-size:0.7rem;">
                <span style="color:var(--color-up);">${long_delta/1000:.0f}k</span>
                <span style="color:var(--color-down);">${short_delta/1000:.0f}k</span>
            </div>
        </div>
        
        <div style="border-top:1px solid var(--border-color); padding-top:16px;">
            <div class="flex-between">
                <span class="label">UNREALIZED PNL</span>
                <span class="{pnl_cls} text-mono" style="font-size:0.9rem; font-weight:600;">{pnl_sign}{roe_pct:.2f}% ROE</span>
            </div>
            <div class="value-xl {pnl_cls}" style="margin-top:4px;">
                {pnl_sign}${unrealized_pnl:,.2f}
            </div>
        </div>
    </div>
    """
    render_html(st, html)
