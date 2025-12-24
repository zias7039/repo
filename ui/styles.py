# ui/styles.py
def inject(st):
    st.markdown("""
<style>
/* 폰트 로드 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
  /* Color Palette */
  --bg-app: #121418;       /* 더 깊은 배경색 */
  --bg-card: #1b1f26;      /* 카드 배경 */
  --bg-hover: #262b34;
  --border-color: #2b313a;
  
  --text-primary: #eaecef;
  --text-secondary: #848e9c;
  --text-tertiary: #5e6673;
  
  --color-up: #2ebd85;     /* 상승색 (초록) */
  --color-down: #f6465d;   /* 하락색 (빨강) */
  --color-accent: #3b82f6; /* 강조색 (파랑) */
  --color-yellow: #fcd535;
  
  --radius-sm: 4px;
  --radius-md: 8px;
  --shadow-card: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
}

/* 기본 설정 */
html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: var(--bg-app) !important;
    color: var(--text-primary);
}

/* Streamlit 기본 여백 제거 및 패딩 조정 */
.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 1;
}

/* 공통 카드 스타일 */
.dashboard-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-card);
}

/* 헤더 스타일 */
.header-container {
    display: flex; justify-content: space-between; align-items: center;
    background-color: var(--bg-card);
    border-bottom: 1px solid var(--border-color);
    padding: 16px 24px;
    margin: -3.5rem -2rem 20px -2rem; /* 화면 꽉 차게 */
}
.app-title { font-size: 1.1rem; font-weight: 800; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px; }
.badge-master { background: #fcd535; color: #000; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; font-weight: 700; }

/* 텍스트 유틸리티 */
.text-mono { font-family: 'JetBrains Mono', monospace; }
.text-up { color: var(--color-up) !important; }
.text-down { color: var(--color-down) !important; }
.text-label { font-size: 0.8rem; color: var(--text-secondary); }
.text-value { font-size: 1.0rem; color: var(--text-primary); font-weight: 600; }
.text-xl { font-size: 1.5rem; font-weight: 700; }

/* 테이블 (Positions) 스타일 */
.trade-table-header {
    display: flex;
    padding: 12px 16px;
    background: #232830;
    border-top-left-radius: var(--radius-md);
    border-top-right-radius: var(--radius-md);
    border-bottom: 1px solid var(--border-color);
    font-size: 0.75rem; color: var(--text-secondary); font-weight: 600;
}
.trade-row {
    display: flex;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    align-items: center;
    transition: background 0.2s;
}
.trade-row:hover { background-color: var(--bg-hover); }
.trade-row:last-child { border-bottom: none; }

/* 버튼 스타일 */
.btn-primary {
    background-color: var(--color-accent); color: white;
    padding: 6px 16px; border-radius: 6px; font-size: 0.85rem; font-weight: 600;
    cursor: pointer; text-align: center; border: none;
}
.btn-outline {
    background: transparent; color: var(--text-primary);
    padding: 5px 15px; border-radius: 6px; font-size: 0.85rem;
    border: 1px solid var(--border-color); cursor: pointer;
}

/* 탭 스타일 커스텀 */
div[data-testid="stTabs"] button {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: var(--text-secondary);
    padding: 0px 16px 10px 16px;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--color-accent) !important;
    border-bottom-color: var(--color-accent) !important;
}
</style>
""", unsafe_allow_html=True)
