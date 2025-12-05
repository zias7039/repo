# ui/table.py
from utils.format import render_html, normalize_symbol, fnum, safe_pct

def side_badge(side: str):
    side = (side or "").upper()
    if side == "LONG":
        return '<span class="badge badge-long">Long</span>'
    elif side == "SHORT":
        return '<span class="badge badge-short">Short</span>'
    return f'<span class="badge" style="background:#333;">{side}</span>'

def positions_table(st, positions, funding_data):
    # 헤더 정의
    table_html = """
    <div class="trade-table-container">
        <div class="trade-row trade-header">
            <div>Symbol</div>
            <div>Side</div>
            <div style="text-align:right;">Size / Value</div>
            <div style="text-align:right;">PNL (ROE)</div>
            <div style="text-align:right;">Entry Price</div>
            <div style="text-align:right;">Mark Price</div>
            <div style="text-align:right;">Liq. Price</div>
            <div style="text-align:right;">Margin</div>
            <div style="text-align:right;">Funding</div>
        </div>
    """

    if not positions:
        table_html += """<div style="padding:32px; text-align:center; color:var(--text-secondary);">
            보유 중인 포지션이 없습니다.
        </div></div>"""
        render_html(st, table_html)
        return

    for p in positions:
        symbol = normalize_symbol(p.get("symbol", ""))
        side = p.get("holdSide", "")
        lev = fnum(p.get("leverage", 0))
        mg = fnum(p.get("marginSize", 0))
        qty = fnum(p.get("total", 0))
        entry = fnum(p.get("averageOpenPrice", 0))
        mark = fnum(p.get("markPrice", 0))
        liq = fnum(p.get("liquidationPrice", 0))
        upl = fnum(p.get("unrealizedPL", 0))
        
        notional = mg * lev
        roe = safe_pct(upl, mg)
        
        # PNL Color
        pnl_cls = "var(--color-up)" if upl >= 0 else "var(--color-down)"
        
        # Funding
        fund_info = funding_data.get(symbol, {"cumulative": 0.0})
        fund_val = fund_info.get("cumulative", 0.0)
        fund_color = "var(--color-up)" if fund_val >= 0 else "var(--text-secondary)"

        table_html += f"""
        <div class="trade-row trade-item">
            <div>
                <div style="font-weight:600; color:var(--text-primary);">{symbol}</div>
                <div style="font-size:0.75rem; color:var(--color-accent);">{lev:.0f}x</div>
            </div>
            
            <div>{side_badge(side)}</div>
            
            <div style="text-align:right;">
                <div style="color:var(--text-primary);">${notional:,.0f}</div>
                <div style="font-size:0.75rem; color:var(--text-secondary);">{qty:,.3f}</div>
            </div>
            
            <div style="text-align:right;">
                <div style="font-weight:600; color:{pnl_cls};">${upl:,.2f}</div>
                <div style="font-size:0.75rem; color:{pnl_cls};">{roe:+.2f}%</div>
            </div>
            
            <div style="text-align:right; color:var(--text-primary);">${entry:,.2f}</div>
            <div style="text-align:right; color:var(--text-tertiary);">${mark:,.2f}</div>
            <div style="text-align:right; color:var(--color-down);">${liq:,.2f}</div>
            
            <div style="text-align:right; color:var(--text-primary);">${mg:,.2f}</div>
            
            <div style="text-align:right; color:{fund_color}; font-size:0.8rem;">
                ${fund_val:,.2f}
            </div>
        </div>
        """

    table_html += "</div>"
    render_html(st, table_html)
