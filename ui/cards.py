# ui/cards.py
import streamlit as st
from utils.format import render_html

def render_top_bar(total_equity, available, leverage, next_refresh="20s"):
    """이미지 상단의 가로형 스탯 바"""
    html = f"""
    <div class="top-metric-container">
        <div class="metric-box">
            <div class="text-label">Total Value <span style="background:#1e1e1e; padding:2px 6px; border-radius:4px; font-size:0.7rem; margin-left:4px;">Combined</span></div>
            <div class="text-value" style="font-size:1.4rem;">${total_equity:,.2f}</div>
        </div>
        
        <div class="metric-box">
            <div class="text-label">Withdrawable <span style="color:var(--text-tertiary); font-size:0.75rem;">74.50%</span></div>
            <div class="text-value" style="font-size:1.4rem;">${available:,.2f}</div>
            <div style="font-size:0.75rem; color:var(--text-secondary);">Free margin available</div>
        </div>
        
        <div class="metric-box">
            <div class="text-label">Leverage <span class="metric-badge">{leverage:.2f}x</span></div>
            <div class="text-value" style="font-size:1.4rem;">${(total_equity * leverage):,.2f}</div>
            <div style="font-size:0.75rem; color:var(--text-secondary);">Total position value</div>
        </div>

        <div style="flex-grow:1; text-align:right;">
             <div style="font-size:0.8rem; color:var(--text-secondary);">Next refresh in {next_refresh}</div>
             <div style="color:var(--color-up); font-size:0.85rem; cursor:pointer;">Support us</div>
        </div>
    </div>
    """
    render_html(st, html)

def render_left_summary(perp_equity, margin_usage, unrealized_pnl, roe_pct, positions):
    """이미지 좌측의 요약 패널 (Perp Equity, Bias, Dist, PnL)"""
    
    # 롱/숏 비율 계산
    long_size = sum(p['marginSize'] * p['leverage'] for p in positions if p['holdSide']=='LONG')
    short_size = sum(p['marginSize'] * p['leverage'] for p in positions if p['holdSide']=='SHORT')
    total_size = long_size + short_size
    
    long_pct = (long_size / total_size * 100) if total_size else 0
    short_pct = (short_size / total_size * 100) if total_size else 0
    
    bias_text = "NEUTRAL"
    bias_color = "var(--text-secondary)"
    if long_pct > 60: bias_text, bias_color = "LONG", "var(--color-up)"
    elif short_pct > 60: bias_text, bias_color = "SHORT", "var(--color-down)"

    pnl_color = "text-up" if unrealized_pnl >= 0 else "text-down"
    
    html = f"""
    <div class="dashboard-card" style="height: 420px; display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div class="text-label">Perp Equity</div>
            <div class="text-xl" style="margin-bottom:4px;">${perp_equity:,.2f}</div>
            
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                <span class="text-label">Margin Usage</span>
                <span class="text-mono" style="font-size:0.9rem;">{margin_usage:.2f}%</span>
            </div>
            <div style="width:100%; height:4px; background:#1e1e1e; margin-top:4px;">
                <div style="width:{min(margin_usage,100)}%; height:100%; background:var(--color-up);"></div>
            </div>
        </div>
        
        <div style="margin-top:24px;">
            <div style="display:flex; justify-content:space-between;">
                <span class="text-label">Direction Bias</span>
                <span style="color:{bias_color}; font-weight:bold; font-size:0.9rem;">{bias_text}</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:4px;">
                <span class="text-label">Long Exposure</span>
                <span class="text-mono" style="font-size:0.9rem; color:var(--color-up);">{long_pct:.1f}%</span>
            </div>
            
            <div style="margin-top:16px;">
                 <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin-bottom:4px;">
                    <span style="color:var(--color-up);">● {long_pct:.1f}%</span>
                    <span style="color:var(--color-down);">● {short_pct:.1f}%</span>
                 </div>
                 <div class="progress-bg">
                    <div style="width:{long_pct}%; background:var(--color-up);"></div>
                    <div style="width:{short_pct}%; background:var(--color-down);"></div>
                 </div>
                 <div style="display:flex; justify-content:space-between; margin-top:8px;">
                    <div style="background:#0f1814; color:var(--color-up); padding:4px 12px; border-radius:4px; font-size:0.9rem;">{long_size/1000:.1f}k</div>
                    <div style="background:#2b1010; color:var(--color-down); padding:4px 12px; border-radius:4px; font-size:0.9rem;">{short_size/1000:.1f}k</div>
                 </div>
            </div>
        </div>
        
        <div style="margin-top:24px;">
            <div style="display:flex; justify-content:space-between; align-items:baseline;">
                <span class="text-label">Unrealized PnL</span>
                <span class="{pnl_color}" style="font-size:0.9rem;">{roe_pct:+.2f}% ROE</span>
            </div>
            <div class="text-xl {pnl_color}" style="margin-top:4px;">${unrealized_pnl:+,.2f}</div>
        </div>
    </div>
    """
    render_html(st, html)
