# ui/toolbar.py
import streamlit as st
from utils.format import normalize_symbol

# 표시용 라벨(Key) : API 전송용 값(Value)
GRANULARITY_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1H",  # API는 1H를 원함 (소문자 h 표기용)
    "4h": "4H",
    "1d": "1D"
}

def render_toolbar(positions=None, default_symbol="BTCUSDT", default_gran_label="1m"):
    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = normalize_symbol(default_symbol)

    with st.container():
        st.markdown("<div class='layout-boundary toolbar-row'>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([0.5, 0.5], vertical_alignment="bottom")

        with c1:
            # 현재 선택된 종목명 (헤드라인 스타일)
            sym = st.session_state.selected_symbol
            st.markdown(f"<h2 style='margin:0; padding:0; line-height:1; color:var(--text-primary); letter-spacing:-0.5px;'>{sym}</h2>", unsafe_allow_html=True)

        with c2:
            # 차트 간격 선택 (오른쪽 정렬)
            st.markdown("<div class='timeframe-selector'>", unsafe_allow_html=True)
            
            # 기본값 선택 인덱스 찾기
            keys = list(GRANULARITY_MAP.keys())
            try:
                idx = keys.index(default_gran_label)
            except ValueError:
                idx = 0

            selected_label = st.radio(
                "Timeframe",
                options=keys,
                index=idx,
                horizontal=True,
                key="granularity_radio",
                label_visibility="collapsed", 
            )
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    return st.session_state.selected_symbol, GRANULARITY_MAP[selected_label]
