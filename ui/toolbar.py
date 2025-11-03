import streamlit as st
from utils.format import normalize_symbol

GRANULARITY_MAP = {"1분":"1min","5분":"5min","15분":"15min","1시간":"1h","4시간":"4h","1일":"1day"}

def render_toolbar(positions, default_symbol="BTCUSDT", default_gran_label="15분"):
    # 심볼 목록
    pos_symbols = [normalize_symbol(p.get("symbol","")) for p in (positions or [])]
    pos_symbols = [s for s in pos_symbols if s] or ["BTCUSDT","ETHUSDT"]

    # 선택 유지
    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = default_symbol

    # ❌ spacer 제거 → ⭕ 두 칼럼만 사용
    left, right = st.columns([1, 1], vertical_alignment="center")

    with left:
        st.markdown('<div class="symbol-wrap">', unsafe_allow_html=True)
        selected_symbol = st.radio(
            "심볼",
            pos_symbols,
            horizontal=True,
            index=pos_symbols.index(st.session_state.selected_symbol) if st.session_state.selected_symbol in pos_symbols else 0,
            key="symbol_radio",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        # 오른쪽 칼럼 전체를 우측 정렬할 래퍼
        st.markdown('<div class="gran-wrap">', unsafe_allow_html=True)
        selected_gran_label = st.radio(
            "차트 간격",
            list(GRANULARITY_MAP.keys()),
            horizontal=True,
            index=list(GRANULARITY_MAP.keys()).index(default_gran_label),
            key="granularity_radio",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # 상태 반영
    if selected_symbol != st.session_state.selected_symbol:
        st.session_state.selected_symbol = selected_symbol
        st.rerun()

    return selected_symbol, GRANULARITY_MAP[selected_gran_label]
