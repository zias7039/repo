# ui/styles.py
def inject(st):
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg-app: #0b0e11;
  --bg-card: #151a21;
  --bg-card-hover: #1b2129;
  --border-color: #2b313a;
  --text-primary: #eaecef;
  --text-secondary: #848e9c;
  --text-tertiary: #5e6673;
  --color-up: #2ebd85;
  --color-down: #f6465d;
  --color-accent: #fcd535;
  --layout-max-width: 1400px;
  --radius-md: 8px;
}

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    color: var(--text-primary);
}
.stApp { background-color: var(--bg-app); }
.block-container {
    max-width: var(--layout-max-width) !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* ---------------- Table & Layout ---------------- */
.trade-table-container {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px 8px 0 0; /* 위쪽만 둥글게 */
    margin-top: 12px;
}
.trade-header {
    display: grid;
    /* 헤더 그리드 비율 (st.columns 비율과 유사하게 시각적 조정) */
    grid-template-columns: 1.1fr 0.7fr 1.5fr 1.3fr 1fr 1fr 1fr 1fr 1.1fr;
    gap: 1rem; /* st.columns 기본 갭과 맞춤 */
    padding: 12px 0; /* 좌우 패딩 제거 (Streamlit 컬럼 정렬 맞춤) */
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-secondary);
}

/* 데이터 행 사이의 구분선 */
.table-row-divider {
    border-top: 1px solid var(--border-color);
    margin: 4px 0;
}

/* ---------------- Badges ---------------- */
.badge {
    padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;
    display: inline-block;
}
.badge-long { background: rgba(46, 189, 133, 0.15); color: var(--color-up); }
.badge-short { background: rgba(246, 70, 93, 0.15); color: var(--color-down); }

/* ---------------- Buttons (Symbol Click) ---------------- */
/* 테이블 내부 버튼 스타일 커스텀 */
div[data-testid="stVerticalBlock"] button {
    width: 100%;
    border: none !important;
    background: transparent !important;
    color: var(--text-primary) !important;
    text-align: left !important;
    padding: 0 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    line-height: 1.2 !important;
    transition: color 0.2s;
}
div[data-testid="stVerticalBlock"] button:hover {
    color: var(--color-accent) !important;
}
div[data-testid="stVerticalBlock"] button p {
    font-size: 0.9rem;
}

/* ---------------- Other UI ---------------- */
/* 상단 카드 */
.stat-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 16px;
}

/* 입력창 및 기타 버튼 */
.stTextInput input {
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
}
/* 차트 스크롤 숨김 */
div[data-testid="stPlotlyChart"] > div { overflow-y: hidden !important; }
</style>
""", unsafe_allow_html=True)
