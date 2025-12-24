# ui/styles.py
def inject(st):
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
  /* Hyperdash Palette */
  --bg-app: #0b0b0b;        /* 메인 배경 (Deep Dark) */
  --bg-card: #131313;       /* 카드 배경 */
  --bg-hover: #1e1e1e;
  --border-color: #252525;
  
  --text-primary: #ffffff;
  --text-secondary: #888888;
  --text-tertiary: #444444;
  
  --color-up: #3dd995;      /* 네온 그린 */
  --color-down: #ff4d4d;    /* 네온 레드 */
  --color-accent: #3dd995;
  --color-label: #a0a0a0;
  
  --radius-md: 8px;
}

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-app) !important;
    color: var(--text-primary);
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 100% !important;
}

header[data-testid="stHeader"] { background: transparent !important; }

/* 커스텀 카드 스타일 */
.dashboard-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 24px;
    margin-bottom: 16px;
}

/* 텍스트 스타일 */
.text-label { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 4px; }
.text-value { font-size: 1.1rem; font-weight: 600; color: var(--text-primary); font-family: 'JetBrains Mono', monospace; }
.text-xl { font-size: 1.8rem; font-weight: 700; letter-spacing: -0.5px; font-family: 'JetBrains Mono', monospace; }
.text-mono { font-family: 'JetBrains Mono', monospace; }

.text-up { color: var(--color-up) !important; }
.text-down { color: var(--color-down) !important; }

/* 상단 메트릭 바 */
.top-metric-container {
    display: flex; gap: 40px; margin-bottom: 20px;
}
.metric-box { display: flex; flex-direction: column; }
.metric-badge {
    background: #1c2229; color: var(--color-up);
    padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin-left: 8px;
}

/* 프로그레스 바 (Long/Short) */
.progress-bg {
    width: 100%; height: 6px; background: #2b1d1d; border-radius: 3px; overflow: hidden; margin-top: 8px; display: flex;
}
.progress-fill-long { height: 100%; background: var(--color-up); }
.progress-fill-short { height: 100%; background: var(--color-down); }

/* 테이블 스타일 */
.table-header {
    display: flex; padding: 12px 0; border-bottom: 1px solid var(--border-color);
    font-size: 0.8rem; color: var(--text-secondary);
}
.table-row {
    display: flex; padding: 16px 0; border-bottom: 1px solid #1a1a1a; align-items: center;
    transition: background 0.2s;
}
.table-row:hover { background-color: var(--bg-hover); }

/* 탭 스타일 */
div[data-testid="stTabs"] button {
    background: transparent; border: none; color: var(--text-secondary); font-size: 0.9rem;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--color-accent) !important;
    background: #132f25 !important;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)
