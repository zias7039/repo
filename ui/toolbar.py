# ui/toolbar.py
import streamlit as st
from utils.format import normalize_symbol

GRANULARITY_MAP = {"1분":"1min","5분":"5min","15분":"15min","1시간":"1h","4시간":"4h","1일":"1day"}

def render_toolbar(positions, default_symbol="BTCUSDT", default_gran_label="15분"):
    # 심볼 후보
    pos_symbols = [normalize_symbol(p.get("symbol","")) for p in (positions or [])]
    pos_symbols = [s for s in pos_symbols if s] or ["BTCUSDT", "ETHUSDT"]

    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = default_symbol

    # 🔹 flex row 시작
    st.markdown('<div class="toolbar-row">', unsafe_allow_html=True)

    # 왼쪽: 심볼
    st.markdown('<div class="toolbar-left">', unsafe_allow_html=True)
    selected_symbol = st.radio(
        "심볼",
        pos_symbols,
        horizontal=True,
        index=pos_symbols.index(st.session_state.selected_symbol) if st.session_state.selected_symbol in pos_symbols else 0,
        key="symbol_radio",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # 오른쪽: 차트 간격
    st.markdown('<div class="toolbar-right">', unsafe_allow_html=True)
    selected_gran_label = st.radio(
        "차트 간격",
        list(GRANULARITY_MAP.keys()),
        horizontal=True,
        index=list(GRANULARITY_MAP.keys()).index(default_gran_label),
        key="granularity_radio",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # flex row 끝
    st.markdown('</div>', unsafe_allow_html=True)

    # 상태 반영
    if selected_symbol != st.session_state.selected_symbol:
        st.session_state.selected_symbol = selected_symbol
        st.rerun()

    return selected_symbol, GRANULARITY_MAP[selected_gran_label]
