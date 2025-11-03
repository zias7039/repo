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

def render_toolbar(positions, default_symbol="BTCUSDT", default_gran_label="15분"):
    pos_symbols = [normalize_symbol(p.get("symbol", "")) for p in (positions or [])]
    pos_symbols = [s for s in pos_symbols if s] or ["BTCUSDT", "ETHUSDT"]

    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = default_symbol

    left_ctrl, spacer, right_ctrl = st.columns([0.45, 0.1, 0.45], vertical_alignment="center")

    # ---- 심볼 선택 ----
    with left_ctrl:
        st.markdown('<div class="symbol-wrap">', unsafe_allow_html=True)
        selected_symbol = st.radio(
            label='',
            options=pos_symbols,
            horizontal=True,
            index=pos_symbols.index(st.session_state.selected_symbol)
            if st.session_state.selected_symbol in pos_symbols
            else 0,
            key="symbol_radio",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- 차트 간격 ----
    with right_ctrl:
        st.markdown('<div class="gran-wrap">', unsafe_allow_html=True)
        selected_gran_label = st.radio(
            label='',
            options=list(GRANULARITY_MAP.keys()),
            horizontal=True,
            index=list(GRANULARITY_MAP.keys()).index(default_gran_label),
            key="granularity_radio",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if selected_symbol != st.session_state.selected_symbol:
        st.session_state.selected_symbol = selected_symbol
        st.rerun()

    return selected_symbol, GRANULARITY_MAP[selected_gran_label]
