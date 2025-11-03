# ui/table.py
from utils.format import render_html, normalize_symbol, fnum, safe_pct

def side_badge(side: str):
    side_up = (side or "").upper()
    if side_up == "LONG":
        bg,border,color = "#14532d","#22c55e","#22c55e"
        label = "롱"
    elif side_up == "SHORT":
        bg,border,color = "#450a0a","#f87171","#f87171"
        label = "숏"
    else:
        bg,border,color = "#1e2538","#94a3b8","#94a3b8"
        label = side_up
    return f"""<span style="background:{bg};color:{color};border:1px solid {border};
font-size:0.7rem;font-weight:600;border-radius:4px;padding:2px 6px;line-height:1;display:inline-block;min-width:44px;text-align:center;">{label}</span>"""

def positions_table(st, positions, funding_data, *, border="rgba(148,163,184,0.2)",
                    text_sub="#94a3b8", text_main="#f8fafc", shadow="0 24px 48px rgba(0,0,0,0.6)"):
    table_html = f"""<div style="background:#0f172a;border:1px solid {border};border-radius:8px;
box-shadow:{shadow};font-size:0.8rem;color:{text_sub};min-width:1200px;margin-top:8px;">
<div style="display:grid;grid-template-columns:100px 70px 160px 150px 110px 120px 120px 110px 140px;column-gap:16px;
padding:12px 16px;border-bottom:1px solid rgba(148,163,184,0.15);font-size:0.9rem;color:{text_sub};font-weight:500;">
<div>자산</div><div>방향</div><div>포지션 가치 / 수량</div><div>미실현 손익</div>
<div>진입가</div><div>현재가</div><div>청산가</div><div>사용 마진</div><div>펀딩비</div></div>"""

    for p in positions:
        symbol = normalize_symbol(p.get("symbol",""))
        side = (p.get("holdSide") or "").upper()
        lev = fnum(p.get("leverage",0.0)); mg = fnum(p.get("marginSize",0.0))
        qty = fnum(p.get("total",0.0)); entry = fnum(p.get("averageOpenPrice",0.0))
        mark = fnum(p.get("markPrice",0.0)); liq = fnum(p.get("liquidationPrice",0.0))
        upl = fnum(p.get("unrealizedPL",0.0))
        notional = mg*lev
        roe_each = safe_pct(upl, mg)
        pnl_color = "#4ade80" if upl>=0 else "#f87171"
        fund_info = funding_data.get(symbol, {"cumulative":0.0})
        funding_display = f"${fund_info.get('cumulative',0.0):,.2f}"

        table_html += f"""<div style="display:grid;grid-template-columns:100px 70px 160px 150px 110px 120px 120px 110px 140px;column-gap:16px;
padding:16px;border-bottom:1px solid rgba(148,163,184,0.08);color:{text_main};font-size:0.8rem;line-height:1.4;">
<div><div style="font-weight:600;">{symbol}</div><div style="font-size:0.7rem;color:{text_sub};">{lev:.0f}x</div></div>
<div style="display:flex;align-items:flex-start;padding-top:2px;">{side_badge(side)}</div>
<div><div>${notional:,.2f}</div><div style="font-size:0.7rem;color:{text_sub};">{qty:,.4f} {symbol.replace("USDT","")}</div></div>
<div><div style="color:{pnl_color};">${upl:,.2f}</div><div style="color:{pnl_color};font-size:0.7rem;">{roe_each:.2f}%</div></div>
<div>${entry:,.2f}</div><div>${mark:,.2f}</div><div>${liq:,.2f}</div><div>${mg:,.2f}</div>
<div style="color:#4ade80;font-weight:500;">{funding_display}</div>
</div>"""

    table_html += "</div>"
    render_html(st, table_html)
