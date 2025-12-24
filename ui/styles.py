# ui/styles.py
def inject(st):
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --bg-app: #0b0b0b;
    --bg-card: #131313;
    --border-color: #222;
    --color-up: #3dd995;
    --color-down: #ff4d4d;
}

html, body, .stApp {
    background-color: var(--bg-app) !important;
    font-family: 'Inter', sans-serif;
    color: #ffffff;
}

/* 레이아웃 여백 조정 */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 98% !important;
}
header[data-testid="stHeader"] { display: none; }
div[data-testid="stVerticalBlock"] { gap: 0rem; }

/* 공통 카드 스타일 */
.dashboard-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    padding: 24px;
}

/* Plotly 차트 간격 제거 (카드 통합용) */
div[data-testid="stPlotlyChart"] {
    background-color: var(--bg-card);
    border-left: 1px solid var(--border-color);
    border-right: 1px solid var(--border-color);
    border-bottom: 1px solid var(--border-color);
    border-bottom-left-radius: 6px;
    border-bottom-right-radius: 6px;
    margin-top: -1px; /* 헤더와 겹치게 하여 선 제거 */
}

/* 텍스트 유틸 */
.label { font-size: 0.8rem; color: #888; margin-bottom: 4px; display: block; }
.value-xl { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #fff; letter-spacing: -1px; }

/* 프로그레스 바 */
.progress-bg {
    width: 100%; height: 6px; background: #1a1a1a; border-radius: 3px; overflow: hidden; margin-top: 8px;
}
.progress-fill { height: 100%; }

/* 테이블 */
.table-header {
    display: flex; padding: 12px 16px; border-bottom: 1px solid var(--border-color);
    font-size: 0.75rem; color: #888; font-weight: 600;
}
.table-row {
    display: flex; padding: 14px 16px; align-items: center; 
    border-bottom: 1px solid #161616; transition: background 0.1s;
}
.table-row:hover { background-color: #1c1c1c; }

/* 탭 */
div[data-testid="stTabs"] button {
    font-size: 0.85rem; color: #888; background: transparent; border: none; padding: 4px 12px;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--color-up) !important;
    background: rgba(61, 217, 149, 0.1) !important;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)
