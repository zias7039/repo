# ui/cards.py
import streamlit as st
from utils.format import render_html

def render_top_bar(total_equity, available, leverage, next_refresh="20s"):
    html = f"""
    <div style="display:flex; gap:40px; margin-bottom:16px; align-items:flex-start;">
        <div>
            <span class="label">Total Value <span style="background:#222; padding:1px 4px; border-radius:3px; font-size:0.6rem;">Combined</span></span>
            <div class="value-xl">${total_equity:,.2f}</div>
        </div>
        <div>
            <span class="label">Withdrawable <span style="color:#666;">74.5%</span></span>
            <div class="value-xl">${available:,.2f}</div>
            <div style="font-size:0.65rem; color:#444; margin-top:2px;">Free margin available</div>
        </div>
        <div>
            <span class="label">Leverage <span style="background:rgba(61,217,149,0.1); color:var(--color-up); padding:1px 4px; border-radius:3px; font-size:0.7rem;">{leverage:.2f}x</span></span>
            <div class="value-xl">${(total_equity * leverage):,.2f}</div>
            <div style="font-size:0.65rem; color:#444; margin-top:2px;">Total position value</div>
        </div>
        <div style="flex-grow:1; text-align:right; padding-top:4px;">
             <div style="font-size:0.75rem; color:#666;">Next refresh in {next_refresh}</div>
             <div style="color:var(--color-up); font-size:0.8rem; cursor:pointer;">Support us</div>
        </div>
    </div>
    """
    render_html(st, html)

def render_left_summary(perp_equity, margin_usage, unrealized_pnl, roe_pct, positions):
    # 1. Delta Exposure 계산 (Dollar Delta)
    # USDT 선물 기준: Notional Value (Size * Price) 자체가 Dollar Delta입니다.
    # 레버리지를 포함한 포지션 총액을 계산합니다.
    long_delta = sum(p['marginSize'] * p['leverage'] for p in positions if p.get('holdSide')=='LONG')
    short_delta = sum(p['marginSize'] * p['leverage'] for p in positions if p.get('holdSide')=='SHORT')
    
    net_delta = long_delta - short_delta
    total_exposure = long_delta + short_delta
    
    # 2. Bias 판단 (자산 대비 Net Delta 비중이 5% 이상이면 방향성이 있다고 판단)
    # perp_equity가 0일 경우 방어 로직 추가
    equity_base = perp_equity if perp_equity > 0 else 1.0
    delta_ratio = net_delta / equity_base

    if delta_ratio > 0.05:
        bias_text, bias_color = "LONG", "var(--color-up)"
    elif delta_ratio < -0.05:
        bias_text, bias_color = "SHORT", "var(--color-down)"
    else:
        bias_text, bias_color = "NEUTRAL", "#888"

    # 3. 비중 계산 (시각화용)
    if total_exposure > 0:
        long_pct = (long_delta / total_exposure) * 100
        short_pct = (short_delta / total_exposure) * 100
    else:
        long_pct, short_pct = 0, 0

    pnl_color = "var(--color-up)" if unrealized_pnl >= 0 else "var(--color-down)"
    pnl_sign = "+" if unrealized_pnl >= 0 else ""

    # 4. HTML 렌더링
    html = f"""
    <div class="dashboard-card" style="min-height:450px; display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div class="label">Perp Equity</div>
            <div class="value-xl" style="font-size:1.6rem;">${perp_equity:,.2f}</div>
            
            <div style="display:flex; justify-content:space-between; margin-top:12px;">
                <span class="label">Margin Usage</span>
                <span style="font-family:var(--font-mono); font-size:0.8rem;">{margin_usage:.2f}%</span>
            </div>
            <div class="progress-bg">
                <div class="progress-fill" style="width:{min(margin_usage,100)}%; background:var(--color-up);"></div>
            </div>
        </div>
        
        <div style="border-top:1px solid #222; padding-top:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="label">Direction Bias (Delta)</span>
                <span style="color:{bias_color}; font-weight:700; font-size:0.85rem;">{bias_text}</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:4px;">
                <span class="label">Net Exposure</span>
                <span style="font-family:var(--font-mono); color:{bias_color}; font-size:0.85rem;">{(delta_ratio*100):+.2f}%</span>
            </div>
            
            <div style="margin-top:10px;">
                <div style="display:flex; justify-content:space-between; font-size:0.7rem; margin-bottom:4px;">
                    <span style="color:var(--color-up);">L: ${long_delta/1000:.1f}k</span>
                    <span style="color:var(--color-down);">S: ${short_delta/1000:.1f}k</span>
                </div>
                <div class="progress-bg" style="display:flex; background:#2b1d1d;">
                    <div style="width:{long_pct}%; background:var(--color-up); height:100%;"></div>
                    <div style="width:{short_pct}%; background:var(--color-down); height:100%;"></div>
                </div>
            </div>
        </div>
        
        <div style="border-top:1px solid #222; padding-top:16px;">
            <div style="display:flex; justify-content:space-between; align-items:baseline;">
                <span class="label">Unrealized PnL</span>
                <span style="color:{pnl_color}; font-weight:600; font-size:0.9rem;">{pnl_sign}{roe_pct:.2f}% ROE</span>
            </div>
            <div style="font-family:var(--font-mono); font-size:1.5rem; font-weight:700; color:{pnl_color}; margin-top:4px;">
                {pnl_sign}${unrealized_pnl:,.2f}
            </div>
        </div>
    </div>
    """
    render_html(st, html)
