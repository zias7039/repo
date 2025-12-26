# ui/cards.py
import streamlit as st
from utils.format import render_html, fnum

def render_top_bar(total_equity, available, leverage, next_refresh="20s", usdt_rate=None):
    # KRW 환산 헬퍼
    def to_krw(val):
        return f"<span style='font-size:0.9rem; color:#737373; margin-left:6px; font-weight:500;'>≈₩{val*usdt_rate:,.0f}</span>" if usdt_rate else ""

    # 환율 표시 HTML
    rate_display = f"<div style='font-size:0.8rem; color:#f5f5f5; font-weight:600; margin-bottom:4px;'>1 USDT ≈ {usdt_rate:,.0f} KRW</div>" if usdt_rate else ""

    html = f"""
    <div style="display:flex; gap:40px; margin-bottom:24px; align-items:flex-start; padding: 0 4px;">
        <div>
            <div class="label" style="margin-bottom:4px;">Total Value <span class="badge badge-neutral" style="margin-left:4px;">Combined</span></div>
            <div class="value-xl">${total_equity:,.2f}{to_krw(total_equity)}</div>
        </div>
        <div>
            <div class="label" style="margin-bottom:4px;">Withdrawable</div>
            <div class="value-xl">${available:,.2f}{to_krw(available)}</div>
            <div style="font-size:0.7rem; color:var(--text-tertiary); margin-top:2px;">74.5% Free Margin</div>
        </div>
        <div>
            <div class="label" style="margin-bottom:4px;">Leverage</div>
            <div class="value-xl" style="display:flex; align-items:center; gap:8px;">
                {leverage:.2f}x <span class="badge badge-up">Active</span>
            </div>
            <div style="font-size:0.7rem; color:var(--text-tertiary); margin-top:2px;">Notional: ${(total_equity * leverage):,.2f}</div>
        </div>
        <div style="flex-grow:1; text-align:right; padding-top:4px;">
             {rate_display}
             <div style="font-size:0.75rem; color:var(--text-secondary);">Auto-refresh in {next_refresh}</div>
             <div style="color:var(--color-up); font-size:0.8rem; font-weight:500; cursor:pointer; margin-top:4px;">System Online</div>
        </div>
    </div>
    """
    render_html(st, html)

def render_left_summary(perp_equity, margin_usage, unrealized_pnl, roe_pct, positions, usdt_rate=None):
    # Delta Logic
    long_delta = sum(fnum(p.get('marginSize', 0)) * fnum(p.get('leverage', 0)) for p in positions if str(p.get('holdSide')).upper() == 'LONG')
    short_delta = sum(fnum(p.get('marginSize', 0)) * fnum(p.get('leverage', 0)) for p in positions if str(p.get('holdSide')).upper() == 'SHORT')
    net_delta = long_delta - short_delta
    total_exposure = long_delta + short_delta
    
    equity_base = perp_equity if perp_equity > 0 else 1.0
    delta_ratio = net_delta / equity_base

    if delta_ratio > 0.05: bias_text, bias_color, bias_badge = "LONG", "var(--color-up)", "badge-up"
    elif delta_ratio < -0.05: bias_text, bias_color, bias_badge = "SHORT", "var(--color-down)", "badge-down"
    else: bias_text, bias_color, bias_badge = "NEUTRAL", "var(--text-secondary)", "badge-neutral"

    long_pct = (long_delta / total_exposure * 100) if total_exposure > 0 else 0
    short_pct = (short_delta / total_exposure * 100) if total_exposure > 0 else 0
    pnl_cls = "text-up" if unrealized_pnl >= 0 else "text-down"
    pnl_sign = "+" if unrealized_pnl >= 0 else ""

    # [수정] KRW 문자열 생성
    krw_equity = f"<span style='font-size:0.9rem; color:#737373; margin-left:6px; font-weight:500;'>≈₩{perp_equity*usdt_rate:,.0f}</span>" if usdt_rate else ""
    krw_pnl = ""
    if usdt_rate:
        val = abs(unrealized_pnl * usdt_rate)
        s_sign = "+" if unrealized_pnl >= 0 else "-"
        krw_pnl = f"<div style='font-size:0.8rem; color:#737373; margin-top:2px;'>≈{s_sign}₩{val:,.0f}</div>"

    html = f"""
    <div class="dashboard-card" style="height:400px; padding:24px; display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div class="label">Perp Equity</div>
            <div class="value-xl">${perp_equity:,.2f}{krw_equity}</div>
            
            <div class="flex-between" style="margin-top:16px;">
                <span class="label">Margin Usage</span>
                <span class="text-mono" style="font-size:0.85rem; color:var(--text-primary);">{margin_usage:.2f}%</span>
            </div>
            <div class="progress-bg">
                <div class="progress-fill" style="width:{min(margin_usage,100)}%; background:var(--color-up);"></div>
            </div>
        </div>
        
        <div style="border-top:1px solid var(--border-color); padding-top:20px;">
            <div class="flex-between">
                <span class="label">Direction Bias</span>
                <span class="badge {bias_badge}">{bias_text}</span>
            </div>
            <div class="flex-between" style="margin-top:8px;">
                <span class="label">Net Exposure</span>
                <span class="text-mono" style="color:{bias_color}; font-size:0.9rem; font-weight:600;">{(delta_ratio*100):+.2f}%</span>
            </div>
            <div class="progress-bg" style="display:flex; background:#1a1a1a; height:6px; margin-top:10px;">
                <div style="width:{long_pct}%; background:var(--color-up);"></div>
                <div style="width:{short_pct}%; background:var(--color-down);"></div>
            </div>
            <div class="flex-between" style="margin-top:6px; font-size:0.75rem;">
                <span style="color:var(--color-up); font-weight:500;">${long_delta/1000:.0f}k</span>
                <span style="color:var(--color-down); font-weight:500;">${short_delta/1000:.0f}k</span>
            </div>
        </div>
        
        <div style="border-top:1px solid var(--border-color); padding-top:20px;">
            <div class="flex-between">
                <span class="label">Unrealized PnL</span>
                <span class="{pnl_cls} text-mono" style="font-size:0.9rem; font-weight:600;">{pnl_sign}{roe_pct:.2f}% ROE</span>
            </div>
            <div class="value-xl {pnl_cls}" style="margin-top:4px;">
                {pnl_sign}${unrealized_pnl:,.2f}
            </div>
            {krw_pnl}
        </div>
    </div>
    """
    render_html(st, html)
