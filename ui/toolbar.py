# ui/toolbar.py
import streamlit as st
from utils.format import normalize_symbol

# ✅ Bitget API 형식에 맞게 값 수정 (1min -> 1m, 1h -> 1H 등)
GRANULARITY_MAP = {
    "1분": "1m",
    "5분": "5m",
    "15분": "15m",
    "1시간": "1H",
    "4시간": "4H",
    "1일": "1D"
}

def render_toolbar(positions=None, default_symbol="BTCUSDT", default_gran_label="1분"):
    normalized_default = normalize_symbol(default_symbol)

    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = normalized_default

    def _on_symbol_input_change():
        raw = st.session_state.get("symbol_input", "")
        sym = normalize_symbol(raw or "")
        if sym:
            st.session_state.selected_symbol = sym
            st.session_state["_symbol_changed"] = True

    with st.container():
        st.markdown("<div class='layout-boundary toolbar-row'>", unsafe_allow_html=True)
        boundary = st.container()
        with boundary:
            left, right = st.columns([0.4, 0.6], vertical_alignment="center")

            with left:
                st.markdown("<div class='symbol-search'>", unsafe_allow_html=True)
                st.text_input(
                    label="심볼 검색",
                    value=st.session_state.selected_symbol,
                    key="symbol_input",
                    placeholder="BTCUSDT",
                    label_visibility="collapsed",
                    on_change=_on_symbol_input_change,
                )
                st.markdown("</div>", unsafe_allow_html=True)

            with right:
                selected_gran_label = st.radio(
                    "차트 간격",
                    list(GRANULARITY_MAP.keys()),
                    horizontal=True,
                    index=list(GRANULARITY_MAP.keys()).index(default_gran_label)
                          if default_gran_label in GRANULARITY_MAP else 0,
                    key="granularity_radio",
                    label_visibility="collapsed", 
                )

        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("_symbol_changed"):
        st.session_state["_symbol_changed"] = False
        st.rerun()

    return st.session_state.selected_symbol, GRANULARITY_MAP[selected_gran_label]
