# ui/toolbar.py
import streamlit as st
from utils.format import normalize_symbol

GRANULARITY_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1H",
    "4h": "4H",
    "1d": "1D"
}

def render_toolbar(positions=None, default_symbol="BTCUSDT", default_gran_label="1m"):
    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = normalize_symbol(default_symbol)

    with st.container():
        # CSS 클래스 'toolbar-container' 적용을 위한 div (styles.py 참조)
        st.markdown("<div class='toolbar-container'></div>", unsafe_allow_html=True)
        
        # [수정됨] vertical_alignment="center"로 수직 중앙 정렬 맞춤
        c1, c2 = st.columns([0.4, 0.6], vertical_alignment="center")

        with c1:
            sym = st.session_state.selected_symbol
            # 폰트 사이즈와 두께 조정하여 타이틀처럼 보이게 함
            st.markdown(f"""
            <div style='display:flex; align-items:center; gap:8px;'>
                <h2 style='margin:0; padding:0; font-size:1.5rem; color:#eaecef; letter-spacing:-0.5px;'>{sym}</h2>
                <span style='background:#2b313a; color:#848e9c; padding:2px 6px; border-radius:4px; font-size:0.75rem;'>Perp</span>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            # 우측 정렬된 컨테이너 안에 라디오 버튼 배치
            st.markdown("<div style='display:flex; justify-content:flex-end;'>", unsafe_allow_html=True)
            
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

        # 툴바와 차트 사이 간격 살짝 띄우기
        st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    return st.session_state.selected_symbol, GRANULARITY_MAP[selected_label]
