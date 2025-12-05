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
        
        fund_info = funding_data.get(symbol, {"cumulative": 0.0})
        fund_val = fund_info.get("cumulative", 0.0)
        
        # ROE 계산
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
            "ROE": roe / 100,
            "Funding": fund_val
        })

    df = pd.DataFrame(rows)

    # 2. 스타일링 함수 (안전한 문법으로 변경)
    def highlight_pnl(val):
        color = '#2ebd85' if val >= 0 else '#f6465d'
        return f'color: {color}'
    
    def highlight_side(val):
        if val == "LONG": return 'color: #2ebd85'
        if val == "SHORT": return 'color: #f6465d'
        return ''

    # Pandas Styler 적용
    styled_df = df.style.map(highlight_pnl, subset=['PNL', 'ROE', 'Funding'])
    styled_df = styled_df.map(highlight_side, subset=['Side'])

    # 3. Streamlit 데이터프레임 렌더링
    st.markdown("##### ⚡ Positions (Click row to chart)")
    
    event = st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",           # 선택 시 리런
        selection_mode="single-row", # 한 줄만 선택 가능
        column_order=["Symbol", "Side", "Lev", "Size", "Entry", "Mark", "Liq.", "Margin", "PNL", "ROE", "Funding"],
        column_config={
            "Symbol": st.column_config.TextColumn("Symbol", width="medium"),
            "Side": st.column_config.TextColumn("Side", width="small"),
            "Lev": st.column_config.TextColumn("Lev", width="small"),
            "Size": st.column_config.NumberColumn("Size", format="%.4f"),
            "Entry": st.column_config.NumberColumn("Entry", format="$%.2f"),
            "Mark": st.column_config.NumberColumn("Mark", format="$%.2f"),
            "Liq.": st.column_config.NumberColumn("Liq.", format="$%.2f"),
            "Margin": st.column_config.NumberColumn("Margin", format="$%.2f"),
            "PNL": st.column_config.NumberColumn("PNL (USDT)", format="$%.2f"),
            "ROE": st.column_config.NumberColumn("ROE", format="%.2f%%"),
            "Funding": st.column_config.NumberColumn("Funding", format="$%.2f"),
        }
    )

    # 4. 선택된 행이 있으면 차트 심볼 변경
    if event.selection.rows:
        selected_index = event.selection.rows[0]
        selected_symbol = df.iloc[selected_index]["Symbol"]
        
        # 현재 선택된 심볼과 다를 경우에만 업데이트
        if st.session_state.selected_symbol != selected_symbol:
            st.session_state.selected_symbol = selected_symbol
            st.rerun()
