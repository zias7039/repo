# ui/toolbar.py
import streamlit as st
from utils.format import normalize_symbol

DEFAULT_SYMBOLS = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BNBUSDT"]

GRANULARITY_MAP = {
    "1분": "1min",
    "5분": "5min",
    "15분": "15min",
    "1시간": "1h",
    "4시간": "4h",
    "1일": "1day"
}

def render_toolbar(positions, default_symbol="BTCUSDT", default_gran_label="1분"):
    # ✅ 심볼 목록 구성 (포지션 기반 + 기본값 + XRPUSDT/BNBUSDT 추가)
    normalized_default = normalize_symbol(default_symbol)
    pos_symbols = [normalize_symbol(p.get("symbol", "")) for p in (positions or [])]
    pos_symbols = [s for s in pos_symbols if s]

    # 항상 기본 심볼이 가장 먼저 나타나도록 + 기본 제공 심볼 추가
    merged_symbols = []
    for sym in [normalized_default, *DEFAULT_SYMBOLS, *pos_symbols]:
        if sym and sym not in merged_symbols:
            merged_symbols.append(sym)

    # 선택 상태 유지
    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = normalized_default

    with st.container():
        st.markdown("<div class='layout-boundary toolbar-row'>", unsafe_allow_html=True)

        boundary = st.container()
        with boundary:
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
