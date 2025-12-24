# ui/styles.py
def inject(st):
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-app: #0b0b0b;
    --bg-card: #131313; /* 이미지와 유사한 어두운 카드색 */
    --bg-hover: #1c1c1c;
    --border-color: #222222;
    
    --text-primary: #ffffff;
    --text-secondary: #999999;
    --text-tertiary: #555555;
    
    --color-up: #3dd995;   /* 네온 민트 */
    --color-down: #ff4d4d; /* 네온 레드 */
    --color-accent: #3dd995;
    
    --font-base: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

html, body, .stApp {
    background-color: var(--bg-app) !important;
    font-family: var(--font-base);
    color: var(--text-primary);
}

/* Streamlit 기본 헤더 제거 */
header[data-testid="stHeader"] { display: none; }
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* 커스텀 카드 */
.dashboard-card {
    background-color: var(--bg-card);
    border-radius: 6px;
    padding: 20px;
    border: 1px solid var(--border-color);
}

/* 타이포그래피 */
.label { font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px; }
.value { font-family: var(--font-mono); font-size: 1.1rem; font-weight: 600; color: var(--text-primary); }
.value-xl { font-family: var(--font-mono); font-size: 1.6rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; }

.text-up { color: var(--color-up) !important; }
.text-down { color: var(--color-down) !important; }

/* 상단 스탯 바 */
.top-bar {
    display: flex; gap: 40px; margin-bottom: 20px; align-items: flex-start;
}
.stat-box { display: flex; flex-direction: column; }
.tag {
    font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; 
    background: #1e222d; color: var(--color-up); font-weight: 600; margin-left: 6px;
    vertical-align: middle;
}

/* 프로그레스 바 */
.progress-container {
    background: #1e1e1e; height: 6px; width: 100%; border-radius: 3px; overflow: hidden; margin-top: 8px;
}
.progress-fill { height: 100%; background-color: var(--color-up); }

/* 테이블 스타일 */
.table-header {
    display: flex; padding: 10px 16px; 
    font-size: 0.75rem; color: var(--text-secondary); font-weight: 600;
    border-bottom: 1px solid var(--border-color);
}
.table-row {
    display: flex; padding: 14px 16px; 
    align-items: center; border-bottom: 1px solid #161616;
    transition: background 0.2s;
}
.table-row:hover { background-color: var(--bg-hover); }

/* 탭 스타일 */
div[data-testid="stTabs"] button {
    font-family: var(--font-base); font-size: 0.85rem; color: var(--text-secondary);
    background: transparent; border: none;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--color-up) !important;
    border-bottom: 2px solid var(--color-up) !important;
}
</style>
""", unsafe_allow_html=True)
