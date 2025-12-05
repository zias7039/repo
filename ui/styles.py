# ui/styles.py
def inject(st):
    st.markdown("""
<style>
:root{
  --layout-max: 1200px;
  --bg-dark: #0f172a;
  --bg-card: #1e293b;
  --text-main: #f1f5f9;
  --text-sub: #94a3b8;
  --accent: #3b82f6;
}

.block-container{
  max-width: var(--layout-max) !important;
  padding-top: 2rem !important;
  padding-bottom: 4rem !important;
}

/* 툴바 스타일 */
.stTextInput > div > div > input {
    background-color: var(--bg-card);
    color: var(--text-main);
    border: 1px solid #334155;
}

/* 테이블 컨테이너: 가로 스크롤 허용 */
div[data-testid="stVerticalBlock"] > div {
    overflow-x: auto;
}

/* Plotly 차트 여백 제거 */
.js-plotly-plot .plotly .main-svg {
    background: transparent !important;
}

/* 새로고침 버튼 스타일 */
.stButton button {
    background-color: var(--bg-card);
    color: var(--text-sub);
    border: 1px solid #334155;
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
}
.stButton button:hover {
    border-color: var(--text-sub);
    color: var(--text-main);
}
</style>
""", unsafe_allow_html=True)
