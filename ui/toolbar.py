# ui/toolbar.py
import streamlit as st
from utils.format import normalize_symbol

GRANULARITY_MAP = {
    "1분": "1m",
    "5분": "5m",
    "15분": "15m",
    "1시간": "1H",
    "4시간": "4H",
    "1일": "1D"
}

def render_toolbar(positions=None, default_symbol="BTCUSDT", default_gran_label="1분"):
    # 세션 상태 초기화
    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = normalize_symbol(default_symbol)

    # 검색창 로직 제거됨 (_on_symbol_input_change 등 삭제)

    with st.container():
        # 레이아웃 컨테이너
        st.markdown("<div class='layout-boundary toolbar-row'>", unsafe_allow_html=True)
        
        # [수정됨] 검색창 대신 현재 심볼 이름과 차트 간격(Radio) 배치
        c1, c2 = st.columns([0.6, 0.4], vertical_alignment="bottom")

        with c1:
            # 현재 선택된 종목명 표시 (검색창 대체)
            sym = st.session_state.selected_symbol
            st.markdown(f"<h2 style='margin:0; padding:0; color:var(--text-primary);'>{sym}</h2>", unsafe_allow_html=True)

        with c2:
            # 차트 간격 선택 (오른쪽 정렬)
            st.markdown("<div style='display:flex; justify-content:flex-end;'>", unsafe_allow_html=True)
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

        st.markdown("</div>", unsafe_allow_html=True)

    return st.session_state.selected_symbol, GRANULARITY_MAP[selected_gran_label]
