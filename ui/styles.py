# ui/styles.py
def inject(st):
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --bg-app: #0b0b0b;
    --bg-card: #111111;
    --bg-hover: #161616;
    --border-color: #222;
    
    --text-primary: #ffffff;
    --text-secondary: #888;
    --text-tertiary: #555;
    
    --color-up: #3dd995;
    --color-down: #ff4d4d;
    
    --font-base: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
}

html, body, .stApp {
    background-color: var(--bg-app) !important;
    font-family: var(--font-base);
    color: var(--text-primary);
}

/* 레이아웃 강제 조정 */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 95% !important; /* 좌우 꽉 차게 */
}
header[data-testid="stHeader"] { display: none; }
div[data-testid="stVerticalBlock"] { gap: 0rem; }

/* 공통 카드 스타일 */
.dashboard-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 24px;
    height: 100%; /* 높이 맞춤 */
}

/* 텍스트 유틸 */
.label { font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px; display: block; }
.value-xl { font-family: var(--font-mono); font-size: 1.8rem; font-weight: 700; color: #fff; letter-spacing: -1px; }
.value-lg { font-family: var(--font-mono); font-size: 1.2rem; font-weight: 600; color: #fff; }
.text-up { color: var(--color-up) !important; }
.text-down { color: var(--color-down) !important; }

/* 프로그레스 바 커스텀 */
.progress-bg {
    width: 100%; height: 6px; background: #1a1a1a; border-radius: 3px; overflow: hidden; margin-top: 8px; position: relative;
}
.progress-fill { height: 100%; transition: width 0.3s; }

/* 테이블 (하단) */
.table-header {
    display: flex; padding: 12px 16px; border-bottom: 1px solid var(--border-color);
    font-size: 0.75rem; color: var(--text-secondary); font-weight: 600;
}
.table-row {
    display: flex; padding: 14px 16px; align-items: center; 
    border-bottom: 1px solid #161616; transition: background 0.1s;
}
.table-row:hover { background-color: var(--bg-hover); }

/* 탭 커스텀 */
div[data-testid="stTabs"] button {
    font-size: 0.85rem; color: var(--text-secondary); background: transparent; border: none; padding: 4px 12px;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--color-up) !important;
    background: rgba(61, 217, 149, 0.1) !important;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)
