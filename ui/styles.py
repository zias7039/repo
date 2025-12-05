# ui/styles.py
def inject(st):
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  /* ---------- Theme Variables ---------- */
  --bg-app: #0b0e11;          /* 더 깊은 검은색 배경 */
  --bg-card: #151a21;         /* 카드 배경 */
  --bg-card-hover: #1b2129;   /* 카드 호버/강조 */
  --border-color: #2b313a;    /* 은은한 테두리 */
  
  /* Text Colors */
  --text-primary: #eaecef;
  --text-secondary: #848e9c;
  --text-tertiary: #5e6673;

  /* Accent Colors */
  --color-up: #2ebd85;        /* 매수/수익 (Green) */
  --color-down: #f6465d;      /* 매도/손실 (Red) */
  --color-accent: #fcd535;    /* 포인트 (Yellow/Gold) */
  
  /* Layout */
  --layout-max-width: 1400px;
  --radius-md: 8px;
  --radius-sm: 4px;
}

/* 기본 설정 */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    color: var(--text-primary);
}

/* Streamlit 기본 배경 덮어쓰기 */
.stApp {
    background-color: var(--bg-app);
}

.block-container {
    max-width: var(--layout-max-width) !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* ---------------- Card Design ---------------- */
.stat-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 16px;
    transition: all 0.2s ease-in-out;
}
.stat-card:hover {
    border-color: #474d57;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

/* ---------------- Table Design ---------------- */
.trade-table-container {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    overflow: hidden;
    margin-top: 12px;
}

.trade-row {
    display: grid;
    grid-template-columns: 1fr 0.8fr 1.5fr 1.2fr 1fr 1fr 1fr 1fr 1.2fr;
    gap: 8px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    align-items: center;
    font-size: 0.9rem;
}

.trade-header {
    background-color: #1e2329;
    color: var(--text-secondary);
    font-size: 0.75rem;
    font-weight: 500;
    border-bottom: 1px solid var(--border-color);
}

.trade-item:last-child {
    border-bottom: none;
}
.trade-item:hover {
    background-color: var(--bg-card-hover);
}

/* ---------------- Badges ---------------- */
.badge {
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1.2;
    display: inline-block;
}
.badge-long { background: rgba(46, 189, 133, 0.15); color: var(--color-up); }
.badge-short { background: rgba(246, 70, 93, 0.15); color: var(--color-down); }

/* ---------------- Inputs & Buttons ---------------- */
/* 입력창 스타일 */
.stTextInput > div > div > input {
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-sm);
}
.stTextInput > div > div > input:focus {
    border-color: var(--color-accent) !important;
    box-shadow: none !important;
}

/* 라디오 버튼 (차트 간격) */
.stRadio [role="radiogroup"] {
    background-color: var(--bg-card);
    padding: 4px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-color);
}

/* 새로고침 버튼 */
.stButton button {
    background-color: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    font-weight: 500;
    transition: 0.2s;
}
.stButton button:hover {
    border-color: var(--text-secondary);
    background-color: var(--bg-card-hover);
    color: var(--color-accent);
}

/* 차트 영역 조정 */
div[data-testid="stPlotlyChart"] {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 8px;
}
</style>
""", unsafe_allow_html=True)
