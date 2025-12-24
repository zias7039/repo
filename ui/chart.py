# ui/cards.py
import streamlit as st
from utils.format import render_html

def render_top_bar(total_equity, available, leverage, next_refresh_sec=20):
    """상단 가로형 스탯 바"""
    html = f"""
    <div class="top-bar">
        <div class="stat-box">
            <div class="label">Total Value <span style="background:#1c1c1c; color:#777; padding:1px 4px; border-radius:3px; font-size:0.6rem;">Combined</span></div>
            <div class="value-xl">${total_equity:,.2f}</div>
        </div>
        
        <div class="stat-box">
            <div class="label">Withdrawable <span style="color:#555; font-size:0.7rem;">74.5%</span></div>
            <div class="value-xl">${available:,.2f}</div>
            <div style="font-size:0.7rem; color:var(--text-tertiary);">Free margin available</div>
        </div>
        
        <div class="stat-box">
            <div class="label">Leverage <span class="tag">{leverage:.2f}x</span></div>
            <div class="value-xl">${(total_equity * leverage):,.2f}</div>
            <div style="font-size:0.7rem; color:var(--text-tertiary);">Total position value</div>
        </div>

        <div style="flex-grow:1; text-align:right;">
             <div style="font-size:0.75rem; color:var(--text-secondary);">Next refresh in {next_refresh_sec}s</div>
             <div style="color:var(--color-up); font-size:0.8rem; cursor:pointer; margin-top:2px;">Support us</div>
        </div>
    </div>
    """
    render_html(st, html)

def render_left_summary(perp_equity, margin_usage_pct, unrealized_pnl, roe_pct, positions):
    """좌측 패널: 자산 상세 요약"""
    # 롱/숏 비중 계산
    long_vol = sum(p['marginSize'] * p['leverage'] for p in positions if p['holdSide']=='LONG')
    short_vol = sum(p['marginSize'] * p['leverage'] for p in positions if p['holdSide']=='SHORT')
    total_vol = long_vol + short_vol
    
    long_pct = (long_vol / total_vol * 100) if total_vol else 0
    short_pct = (short_vol / total_vol * 100) if total_vol else 0
    
    # 방향성 바이어스
    bias = "NEUTRAL"
    bias_color = "#777"
    if long_pct > 60: bias, bias_color = "LONG", "var(--color-up)"
    elif short_pct > 60: bias, bias_color = "SHORT", "var(--color-down)"

    pnl_cls = "text-up" if unrealized_pnl >= 0 else "text-down"
    
    html = f"""
    <div class="dashboard-card" style="height: 420px; display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div class="label">Perp Equity</div>
            <div class="value-xl" style="font-size:1.8rem;">${perp_equity:,.2f}</div>
            
            <div style="display:flex; justify-content:space-between; margin-top:12px; font-size:0.75rem; color:var(--text-secondary);">
                <span>Margin Usage</span>
                <span>{margin_usage_pct:.2f}%</span>
            </div>
            <div class="progress-container">
                <div class="progress-fill" style="width:{min(margin_usage_pct, 100)}%;"></div>
            </div>
        </div>
        
        <div style="border-top:1px solid #222; padding-top:16px;">
            <div style="display:flex; justify-content:space-between;">
                <span class="label">Direction Bias</span>
                <span style="color:{bias_color}; font-weight:700; font-size:0.85rem;">{bias}</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:4px;">
                <span class="label">Long Exposure</span>
                <span class="value" style="font-size:0.9rem; color:var(--color-up);">{long_pct:.1f}%</span>
            </div>
            
            <div style="margin-top:10px;">
                 <div style="display:flex; justify-content:space-between; font-size:0.7rem; margin-bottom:4px;">
                    <span style="color:var(--color-up);">● {long_pct:.0f}%</span>
                    <span style="color:var(--color-down);">● {short_pct:.0f}%</span>
                 </div>
                 <div class="progress-container" style="display:flex; background:#2b1d1d;">
                    <div style="width:{long_pct}%; background:var(--color-up); height:100%;"></div>
                    <div style="width:{short_pct}%; background:var(--color-down); height:100%;"></div>
                 </div>
                 
                 <div style="display:flex; gap:8px; margin-top:8px;">
                    <div style="background:#0f1814; color:var(--color-up); padding:4px 8px; border-radius:4px; font-size:0.8rem; flex:1; text-align:center;">
                        {long_vol/1000:.1f}k
                    </div>
                    <div style="background:#2b1010; color:var(--color-down); padding:4px 8px; border-radius:4px; font-size:0.8rem; flex:1; text-align:center;">
                        {short_vol/1000:.1f}k
                    </div>
                 </div>
            </div>
        </div>
        
        <div style="border-top:1px solid #222; padding-top:16px;">
            <div style="display:flex; justify-content:space-between; align-items:baseline;">
                <span class="label">Unrealized PnL</span>
                <span class="{pnl_cls}" style="font-weight:600; font-size:0.9rem;">{roe_pct:+.2f}% ROE</span>
            </div>
            <div class="{pnl_cls}" style="font-family:var(--font-mono); font-size:1.6rem; font-weight:700; margin-top:4px;">
                ${unrealized_pnl:+,.2f}
            </div>
        </div>
    </div>
    """
    render_html(st, html)
