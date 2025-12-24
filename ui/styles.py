# ui/styles.py
def inject(st):
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg-app: #080808;       /* 더 깊은 블랙 */
    --bg-card: #111111;      /* 카드 배경 */
    --bg-hover: #181818;     /* 호버 효과 */
    --border-color: #1f1f1f; /* 아주 은은한 테두리 */
    
    --text-primary: #ffffff;
    --text-secondary: #888888;
    --text-tertiary: #555555;
    
    --color-up: #3dd995;   /* 네온 민트 */
    --color-down: #ff4d4d; /* 네온 레드 */
    
    --font-base: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

html, body, .stApp {
    background-color: var(--bg-app) !important;
    font-family: var(--font-base);
    color: var(--text-primary);
    letter-spacing: -0.02em; /* 텍스트를 약간 더 조임 */
}

/* [핵심] 폭 X1278 고정 및 중앙 정렬 */
.main .block-container {
    max-width: 1278px !important;
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
    margin: auto;
}

/* Streamlit 기본 요소 숨김 및 간격 제거 */
header[data-testid="stHeader"] { display: none; }
div[data-testid="stVerticalBlock"] { gap: 0rem; }
div[data-testid="stBlock"] { gap: 0rem; }

/* 공통 카드 스타일 (더 플랫하게) */
.dashboard-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 4px; /* 라운드 줄임 */
}

/* 유틸리티 클래스 */
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.text-mono { font-family: var(--font-mono); }
.label { font-size: 0.75rem; color: var(--text-secondary); font-weight: 500; letter-spacing: 0.02em; }
.value-xl { font-family: var(--font-mono); font-size: 1.75rem; font-weight: 700; color: #fff; letter-spacing: -0.05em; line-height: 1.1; }
.text-up { color: var(--color-up) !important; }
.text-down { color: var(--color-down) !important; }

/* 뱃지 스타일 */
.badge {
    padding: 2px 6px; border-radius: 3px; font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
}
.badge-neutral { background: #222; color: #999; }
.badge-up { background: rgba(61, 217, 149, 0.15); color: var(--color-up); }
.badge-down { background: rgba(255, 77, 77, 0.15); color: var(--color-down); }

/* 프로그레스 바 */
.progress-bg {
    width: 100%; height: 4px; background: #1a1a1a; border-radius: 2px; overflow: hidden; margin-top: 6px;
}
.progress-fill { height: 100%; }

/* 테이블 스타일 (더 타이트하게) */
.table-header {
    display: flex; padding: 10px 16px; border-bottom: 1px solid var(--border-color);
    font-size: 0.7rem; color: var(--text-tertiary); font-weight: 600; text-transform: uppercase;
}
.table-row {
    display: flex; padding: 12px 16px; align-items: center; 
    border-bottom: 1px solid var(--bg-hover); transition: background 0.1s;
}
.table-row:hover { background-color: var(--bg-hover); }
.table-row .value { font-family: var(--font-mono); font-size: 0.9rem; font-weight: 500; }

/* 탭 스타일 (미니멀) */
div[data-testid="stTabs"] { gap: 0px; }
div[data-testid="stTabs"] button {
    font-size: 0.8rem; color: var(--text-secondary); background: transparent; border: none; padding: 8px 16px; font-weight: 500;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--text-primary) !important;
    border-bottom: 2px solid var(--color-up) !important;
}
</style>
""", unsafe_allow_html=True)
