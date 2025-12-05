# ui/styles.py
def inject(st):
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg-app: #0b0e11;
  --bg-card: #151a21;
  --border-color: #2b313a;
  --text-primary: #eaecef;
  --text-secondary: #848e9c;
  --text-tertiary: #5e6673;
  --color-up: #2ebd85;
  --color-down: #f6465d;
  --color-accent: #fcd535; /* 강조색 (Gold) */
  --radius-md: 8px;
}

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    color: var(--text-primary);
}
.stApp { background-color: var(--bg-app); }
.block-container {
    max-width: 1400px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* ---------------- Timeframe Selector Design ---------------- */
/* 라디오 버튼 컨테이너를 우측 정렬 */
.timeframe-selector {
    display: flex;
    justify-content: flex-end;
}

/* Streamlit 라디오 버튼 커스텀 */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    background-color: transparent;
    gap: 4px; /* 버튼 사이 간격 */
}

/* 라디오 버튼 항목 (라벨) */
div[data-testid="stRadio"] label {
    background-color: transparent !important;
    border: none !important;
    padding: 4px 8px !important;
    border-radius: 4px !important;
    cursor: pointer;
    transition: all 0.2s ease;
}

/* 라디오 버튼 안의 '동그라미' 숨기기 (핵심) */
div[data-testid="stRadio"] label > div:first-child {
    display: none;
}

/* 텍스트 스타일 (기본: 회색) */
div[data-testid="stRadio"] label p {
    color: var(--text-secondary);
    font-size: 0.9rem;
    font-weight: 600;
    margin: 0;
}

/* 마우스 올렸을 때 (Hover) */
div[data-testid="stRadio"] label:hover p {
    color: var(--text-primary);
}

/* 선택되었을 때 (Active) - 텍스트 색상 변경 및 배경 */
div[data-testid="stRadio"] label[data-checked="true"] p {
    color: var(--color-accent) !important; /* 노란색 텍스트 */
}
div[data-testid="stRadio"] label[data-checked="true"] {
    background-color: rgba(252, 213, 53, 0.1) !important; /* 노란색 배경(연하게) */
}

/* ---------------- Table & Layout ---------------- */
.trade-table-container {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px 8px 0 0;
    margin-top: 12px;
}
.trade-header {
    display: grid;
    grid-template-columns: 1.2fr 0.7fr 1.5fr 1.3fr 1fr 1fr 1fr 1fr 1fr;
    gap: 1rem;
    padding: 12px 16px;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-secondary);
}
.table-row-divider {
    border-top: 1px solid var(--border-color);
    margin: 4px 0;
}

/* ---------------- Buttons & Cards ---------------- */
/* 투명 버튼 (심볼 클릭용) */
div[data-testid="stVerticalBlock"] button {
    border: none !important;
    background: transparent !important;
    color: var(--text-primary) !important;
    text-align: left !important;
    padding: 0 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    line-height: 1.2 !important;
}
div[data-testid="stVerticalBlock"] button:hover {
    color: var(--color-accent) !important;
}

.stat-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 16px;
}
.stTextInput input {
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
}

/* 차트 스크롤 숨김 */
div[data-testid="stPlotlyChart"] { overflow: hidden !important; }
div[data-testid="stPlotlyChart"] > div { overflow: hidden !important; }
</style>
""", unsafe_allow_html=True)
