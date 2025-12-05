# ui/cards.py
from utils.format import render_html

def krw_line(amount_usd: float, usdt_krw: float, color: str = "#848e9c") -> str:
    if not usdt_krw: return ""
    won = amount_usd * usdt_krw
    return f"<div style='font-size:0.8rem;color:{color};margin-top:2px;'>≈ ₩{won:,.0f}</div>"

def top_card(st, *, total_equity, available, withdrawable_pct, est_leverage,
             total_position_value, unrealized_total_pnl, roe_pct, realized_pnl, usdt_krw):
    
    # 미실현 PNL 색상
    upl_color = "var(--color-up)" if unrealized_total_pnl >= 0 else "var(--color-down)"
    upl_bg = "rgba(46, 189, 133, 0.1)" if unrealized_total_pnl >= 0 else "rgba(246, 70, 93, 0.1)"
    
    # [추가됨] 실현 PNL 색상
    rpl_color = "var(--color-up)" if realized_pnl >= 0 else "var(--color-down)"

    html = f"""
<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 16px;'>

<div class="stat-card">
    <div style="color:var(--text-secondary); font-size:0.85rem; margin-bottom:4px;">총 자산 (Equity)</div>
    <div style="font-size:1.4rem; font-weight:700; color:var(--text-primary);">${total_equity:,.2f}</div>
    {krw_line(total_equity, usdt_krw)}
</div>

<div class="stat-card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
        <div style="color:var(--text-secondary); font-size:0.85rem;">주문 가능</div>
        <div style="font-size:0.75rem; color:var(--color-up); background:rgba(46,189,133,0.1); padding:2px 6px; border-radius:4px;">{withdrawable_pct:.1f}%</div>
    </div>
    <div style="font-size:1.4rem; font-weight:700; color:var(--text-primary);">${available:,.2f}</div>
</div>

<div class="stat-card">
    <div style="color:var(--text-secondary); font-size:0.85rem; margin-bottom:4px;">오늘 실현 손익 (Realized)</div>
    <div style="font-size:1.4rem; font-weight:700; color:{rpl_color};">${realized_pnl:,.2f}</div>
    {krw_line(realized_pnl, usdt_krw, color=rpl_color)}
</div>

<div class="stat-card" style="border:1px solid {upl_color}; background: linear-gradient(145deg, var(--bg-card), {upl_bg});">
    <div style="color:var(--text-secondary); font-size:0.85rem; margin-bottom:4px;">미실현 손익 (Unrealized)</div>
    <div style="font-size:1.4rem; font-weight:700; color:{upl_color};">
        ${unrealized_total_pnl:,.2f}
        <span style="font-size:0.9rem; margin-left:4px;">({roe_pct:+.2f}%)</span>
    </div>
    {krw_line(unrealized_total_pnl, usdt_krw, color=upl_color)}
</div>

</div>
"""
    render_html(st, html)
