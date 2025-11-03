# ui/cards.py
from utils.format import render_html, fnum

def krw_line(amount_usd: float, usdt_krw: float, color: str | None = None) -> str:
    if not usdt_krw: return ""
    won = amount_usd * usdt_krw
    style = f"color:{color};" if color else "color:#94a3b8;"
    return f"<div style='font-size:0.70rem;{style}margin-top:0px;'>≈ ₩{won:,.0f}</div>"

def top_card(st, *, total_equity, available, withdrawable_pct, est_leverage,
             total_position_value, unrealized_total_pnl, roe_pct, usdt_krw, text_sub="#94a3b8",
             text_main="#f8fafc", card_bg="#1e2538", border="rgba(148,163,184,0.2)", shadow="0 24px 48px rgba(0,0,0,0.6)"):
    pnl_color = "#4ade80" if unrealized_total_pnl >= 0 else "#f87171"
    pnl_block_html = f"""
<div style='color:{text_sub};'>
  <div style='font-size:0.75rem;'>미실현 손익</div>
  <div style='font-weight:600;font-size:1rem;color:{pnl_color};'>
    ${unrealized_total_pnl:,.2f}
    <span style='font-size:0.7rem;color:{pnl_color};'>({roe_pct:.2f}%)</span>
  </div>
  {krw_line(unrealized_total_pnl, usdt_krw, color=pnl_color)}
</div>"""

    html = f"""<div style='background:{card_bg};border:1px solid {border};border-radius:8px;
padding:12px 16px;margin-bottom:8px;box-shadow:{shadow};font-size:0.8rem;display:flex;justify-content:space-between;'>
<div style='display:flex;flex-wrap:wrap;row-gap:1px;column-gap:32px;'>

<div style='color:{text_sub};'>
  <div style='font-size:0.75rem;'>총자산</div>
  <div style='color:{text_main};font-weight:600;font-size:1rem;'>${total_equity:,.2f}</div>
  {krw_line(total_equity, usdt_krw)}
</div>

<div style='color:{text_sub};'>
  <div style='font-size:0.75rem;'>출금 가능 <span style='color:#4ade80;'>{withdrawable_pct:.2f}%</span></div>
  <div style='color:{text_main};font-weight:600;font-size:1rem;'>${available:,.2f}</div>
  {krw_line(available, usdt_krw)}
</div>

<div style='color:{text_sub};'>
  <div style='font-size:0.75rem;'>레버리지
    <span style='background:#7f1d1d;color:#fff;padding:2px 6px;border-radius:6px;font-size:0.7rem;font-weight:600;'>
      {est_leverage:.2f}x
    </span>
  </div>
  <div style='color:{text_main};font-weight:600;font-size:1rem;'>${total_position_value:,.2f}</div>
  {krw_line(total_position_value, usdt_krw)}
</div>

{pnl_block_html}

</div></div>"""
    render_html(st, html)
