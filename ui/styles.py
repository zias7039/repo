# ui/styles.py
def inject(st):
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg-app: #0b0e11;
  --bg-card: #151a21;
  --bg-hover: #2b313a;
  --border-color: #2b313a;
  --text-primary: #eaecef;
  --text-secondary: #848e9c;
  --color-accent: #fcd535;
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

/* ---------------- Toolbar Area ---------------- */
/* 툴바 전체 영역에 하단 테두리를 주어 구분감 형성 */
.toolbar-container {
    display: flex;
    align-items: center;
    padding-bottom: 12px;
    margin-bottom: 12px;
    border-bottom: 1px solid var(--border-color);
}

/* ---------------- Timeframe Selector (Segmented Control) ---------------- */
/* 라디오 버튼 그룹 전체를 감싸는 박스 스타일 */
div[role="radiogroup"] {
    background-color: #1e2329; /* 아주 어두운 회색 배경 */
    padding: 4px;
    border-radius: 8px;
    display: inline-flex;
    gap: 0px !important; /* 버튼 사이 간격 제거 */
    border: 1px solid var(--border-color);
}

/* 개별 라디오 버튼 라벨 */
div[data-testid="stRadio"] label {
    margin: 0 !important;
    padding: 4px 12px !important;
    border-radius: 6px !important;
    transition: all 0.2s ease;
    border: none !important;
    background: transparent !important;
}

/* 라디오 버튼 내부 동그라미 숨김 */
div[data-testid="stRadio"] label > div:first-child { display: none; }

/* 텍스트 스타일 */
div[data-testid="stRadio"] label p {
    color: var(--text-secondary);
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0;
}

/* 마우스 호버 */
div[data-testid="stRadio"] label:hover {
    background-color: var(--bg-hover) !important;
}
div[data-testid="stRadio"] label:hover p {
    color: var(--text-primary);
}

/* 선택된 상태 (Active) */
div[data-testid="stRadio"] label[data-checked="true"] {
    background-color: #2b313a !important; /* 활성 배경색 */
    box-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
div[data-testid="stRadio"] label[data-checked="true"] p {
    color: var(--color-accent) !important; /* 활성 텍스트 색상 */
}

/* ---------------- Others ---------------- */
/* 차트 스크롤 숨김 */
div[data-testid="stPlotlyChart"] { overflow: hidden !important; }
div[data-testid="stPlotlyChart"] > div { overflow: hidden !important; }

/* 테이블 및 카드 등 기존 스타일 유지 */
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
.table-row-divider { border-top: 1px solid var(--border-color); margin: 4px 0; }

.stat-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 16px;
}
.badge {
    padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; display: inline-block;
}
.badge-long { background: rgba(46, 189, 133, 0.15); color: #2ebd85; }
.badge-short { background: rgba(246, 70, 93, 0.15); color: #f6465d; }

/* 버튼 텍스트화 */
div[data-testid="stVerticalBlock"] button {
    border: none !important; background: transparent !important; color: var(--text-primary) !important;
    text-align: left !important; padding: 0 !important; font-weight: 600 !important; font-size: 0.9rem !important;
}
div[data-testid="stVerticalBlock"] button:hover { color: var(--color-accent) !important; }
</style>
""", unsafe_allow_html=True)
