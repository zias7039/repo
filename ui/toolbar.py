import streamlit as st
from utils.format import normalize_symbol

GRANULARITY_MAP = {"1분":"1min","5분":"5min","15분":"15min","1시간":"1h","4시간":"4h","1일":"1day"}

def render_toolbar(positions, default_symbol="BTCUSDT", default_gran_label="15분"):
    # 심볼 후보
    pos_symbols = [normalize_symbol(p.get("symbol","")) for p in (positions or [])]
    pos_symbols = [s for s in pos_symbols if s] or ["BTCUSDT","ETHUSDT"]

    # 세션 기본값
    st.session_state.setdefault("selected_symbol", default_symbol)

    left, spacer, right = st.columns([0.45, 0.10, 0.45], vertical_alignment="center")

    with left:
        st.markdown('<div class="symbol-wrap">', unsafe_allow_html=True)
        sym = st.radio(
            label='',
            options=pos_symbols,
            horizontal=True,
            index=pos_symbols.index(st.session_state.selected_symbol) if st.session_state.selected_symbol in pos_symbols else 0,
            key="symbol_radio",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="gran-wrap">', unsafe_allow_html=True)
        gran_label = st.radio(
            label='',
            options=list(GRANULARITY_MAP.keys()),
            horizontal=True,
            index=list(GRANULARITY_MAP.keys()).index(default_gran_label),
            key="granularity_radio",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # 상태 반영
    if sym != st.session_state.selected_symbol:
        st.session_state.selected_symbol = sym
        st.rerun()

    return sym, GRANULARITY_MAP[gran_label]
