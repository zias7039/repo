# ui/table.py
import pandas as pd
import streamlit as st
from utils.format import normalize_symbol, fnum

def positions_table(st, positions, funding_data):
    if not positions:
        st.info("보유 중인 포지션이 없습니다.")
        return

    # 1. 데이터 프레임 생성
    rows = []
    for p in positions:
        symbol = normalize_symbol(p.get("symbol", ""))
        side = (p.get("holdSide") or "").upper()
        lev = fnum(p.get("leverage", 0))
        qty = fnum(p.get("total", 0))
        entry = fnum(p.get("averageOpenPrice", 0))
        mark = fnum(p.get("markPrice", 0))
        liq = fnum(p.get("liquidationPrice", 0))
        upl = fnum(p.get("unrealizedPL", 0))
        mg = fnum(p.get("marginSize", 0))
        
        # 펀딩비
        fund_info = funding_data.get(symbol, {"cumulative": 0.0})
        fund_val = fund_info.get("cumulative", 0.0)
        
        # 수익률 (ROE)
        roe = (upl / mg * 100) if mg else 0.0

        rows.append({
            "Symbol": symbol,
            "Side": side,
            "Lev": f"{lev:.0f}x",
            "Size": qty,
            "Entry": entry,
            "Mark": mark,
            "Liq.": liq,
            "Margin": mg,
            "PNL": upl,
            "ROE": roe / 100, # 퍼센트 포맷을 위해 소수로 저장
            "Funding": fund_val
        })

    df = pd.DataFrame(rows)

    # 2. 스타일링 함수 (색상 적용)
    def highlight_pnl(val):
        color = '#2ebd85' if val >= 0 else '#f6465d' # Green / Red
        return f'color: {color}'
    
    def highlight_side(val):
        if val == "LONG": return 'color: #2ebd85'
        if val == "SHORT": return 'color: #f6465d'
        return ''

    # Pandas Styler 적용
    # PNL, ROE, Funding, Side 컬럼에 색상 입히기
    styled_df = df.style.map(highlight_pnl, subset=['PNL', 'ROE', 'Funding'])\
                        .map(highlight_side, subset=['Side'])

    # 3. Streamlit 데이터프레임 렌더링 (Select 기능 활성화)
    st.markdown("##### ⚡ Positions (Click row to chart)") # 소제목
    
    event = st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",          # [핵심] 선택 시 리런
        selection_mode="single-row", # 한 번에 한 줄만 선택
        column_order=["Symbol", "Side", "Lev", "Size", "Entry", "Mark", "Liq.", "Margin", "PNL", "ROE", "Funding"],
        column_config={
            "Symbol": st.column_config.TextColumn("Symbol", width="medium"),
            "Side": st.column_config.TextColumn("Side", width="small"),
            "Lev": st.column_config.TextColumn("Lev", width="small"),
            "Size": st.column_config.NumberColumn("Size", format="%.4f"),
            "Entry": st.column_config.NumberColumn("Entry", format="$%.2f"),
            "Mark": st.column_config.NumberColumn("Mark", format="$%.2
