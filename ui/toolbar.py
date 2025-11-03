# ui/toolbar.py
import streamlit as st
from utils.format import normalize_symbol

GRANULARITY_MAP = {
    "1분": "1min",
    "5분": "5min",
    "15분": "15min",
    "1시간": "1h",
    "4시간": "4h",
    "1일": "1day"
}

def render_toolbar(positions, default_symbol="BTCUSDT", default_gran_label="1분"):
    # ✅ 심볼 목록 구성 (포지션 기반 + 기본값 + XRPUSDT 추가)
    pos_symbols = [normalize_symbol(p.get("symbol", "")) for p in (positions or [])]
    pos_symbols = [s for s in pos_symbols if s]

    # 항상 기본 3개 포함하도록
    default_symbols = ["BTCUSDT", "ETHUSDT", "XRPUSDT"]

    # 중복 없이 병합
    merged_symbols = []
    for sym in default_symbols + pos_symbols:
        if sym not in merged_symbols:
            merged_symbols.append(sym)

    # 선택 상태 유지
    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = default_symbol

    # 좌 / 우 분할
    left, right = st.columns([1, 1], vertical_alignment="center")

    with left:
        selected_symbol = st.radio(
            "심볼",
            merged_symbols,
            horizontal=True,
            index=merged_symbols.index(st.session_state.selected_symbol)
                  if st.session_state.selected_symbol in merged_symbols else 0,
            key="symbol_radio",
        )

    with right:
        selected_gran_label = st.radio(
            "차트 간격",
            list(GRANULARITY_MAP.keys()),
            horizontal=True,
            index=list(GRANULARITY_MAP.keys()).index(default_gran_label),
            key="granularity_radio",
        )

    # 상태 반영
    if selected_symbol != st.session_state.selected_symbol:
        st.session_state.selected_symbol = selected_symbol
        st.rerun()

    return selected_symbol, GRANULARITY_MAP[selected_gran_label]
