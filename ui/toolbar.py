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
    # ---- 심볼 소스 구성
    normalized_default = normalize_symbol(default_symbol)
    pos_symbols = [normalize_symbol(p.get("symbol", "")) for p in (positions or [])]
    pos_symbols = [s for s in pos_symbols if s]

    merged_symbols = []
    for sym in [normalized_default, *DEFAULT_SYMBOLS, *pos_symbols]:
        if sym and sym not in merged_symbols:
            merged_symbols.append(sym)

    # ---- 상태 기본값
    if "selected_symbol" not in st.session_state or not st.session_state.selected_symbol:
        st.session_state.selected_symbol = normalized_default

    # ---- on_change 핸들러: 텍스트 입력 → 선택 심볼로 반영
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
            left, right = st.columns([1, 1], vertical_alignment="center")

            # --- 왼쪽: 검색창 (타이핑)
            with left:
                # 검색창을 보기 좋게 감싸는 div (아이콘/스타일은 CSS로)
                st.markdown("<div class='symbol-search'>", unsafe_allow_html=True)
                st.text_input(
                    label="심볼, ISIN 또는 CUSIP",
                    value=st.session_state.selected_symbol,
                    key="symbol_input",
                    placeholder="심볼, ISIN 또는 CUSIP",
                    label_visibility="collapsed",
                    on_change=_on_symbol_input_change,
                )
                st.markdown("</div>", unsafe_allow_html=True)

                # (선택) 빠른 선택용 추천 pill들
                with st.container():
                    cols = st.columns(min(4, max(1, len(merged_symbols))))
                    for i, sym in enumerate(merged_symbols[:8]):  # 너무 많으면 8개까지만
                        if cols[i % len(cols)].button(sym, use_container_width=True, key=f"sym_btn_{sym}"):
                            st.session_state.selected_symbol = sym
                            st.session_state["_symbol_changed"] = True

            # --- 오른쪽: 차트 간격 라디오 유지
            with right:
                selected_gran_label = st.radio(
                    "차트 간격",
                    list(GRANULARITY_MAP.keys()),
                    horizontal=True,
                    index=list(GRANULARITY_MAP.keys()).index(default_gran_label)
                          if default_gran_label in GRANULARITY_MAP else 0,
                    key="granularity_radio",
                )

        st.markdown("</div>", unsafe_allow_html=True)

    # ---- 입력/버튼으로 심볼이 바뀌었으면 즉시 리런
    if st.session_state.get("_symbol_changed"):
        st.session_state["_symbol_changed"] = False
        st.rerun()

    return st.session_state.selected_symbol, GRANULARITY_MAP[selected_gran_label]
