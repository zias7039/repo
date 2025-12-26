# ui/styles.py
def inject(st):
    st.markdown("""
<style>
/* 폰트 설정 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg-app: #0f0f0f;
    --bg-card: #141414;
    --bg-hover: #1f1f1f;
    --border-color: #262626;

    --text-primary: #f5f5f5;
    --text-secondary: #a3a3a3;
    --text-tertiary: #525252;

    --color-up: #3dd995;
    --color-down: #ff4d4d;

    --font-base: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;

    --radius-md: 8px;
}

html, body, .stApp {
    background-color: var(--bg-app) !important;
    font-family: var(--font-base);
    color: var(--text-primary);
    letter-spacing: -0.01em;
}

/* 레이아웃 폭 고정 + 중앙정렬 */
.main .block-container {
    max-width: 1278px !important;
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    margin: auto;
}

/* 기본 헤더 숨김 */
header[data-testid="stHeader"] { display: none; }

/* ✅ (중요) gap 0은 겹침/클리핑 유발 → 최소 간격 부여 */
div[data-testid="stVerticalBlock"] { gap: 0.25rem; }

/* 카드 */
.dashboard-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
}

/* 텍스트 유틸 */
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.label { font-size: 0.75rem; color: var(--text-secondary); font-weight: 500; }
.value-xl { font-family: var(--font-mono); font-size: 1.5rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.03em; }
.text-mono { font-family: var(--font-mono); }
.text-up { color: var(--color-up) !important; }
.text-down { color: var(--color-down) !important; }

/* 뱃지 */
.badge {
    padding: 2px 8px;
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 600;
}
.badge-neutral { background: #262626; color: #a3a3a3; }
.badge-up { background: rgba(61, 217, 149, 0.1); color: var(--color-up); }
.badge-down { background: rgba(255, 77, 77, 0.1); color: var(--color-down); }

/* 프로그레스 */
.progress-bg {
    width: 100%;
    height: 6px;
    background: #1a1a1a;
    border-radius: 3px;
    overflow: hidden;
    margin-top: 8px;
}
.progress-fill { height: 100%; }

/* 테이블 */
.table-header {
    display: flex;
    padding: 12px 20px;
    border-bottom: 1px solid var(--border-color);
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-weight: 500;
}
.table-row {
    display: flex;
    padding: 14px 20px;
    align-items: center;
    border-bottom: 1px solid var(--border-color);
    transition: background 0.1s;
}
.table-row:last-child { border-bottom: none; }
.table-row:hover { background-color: var(--bg-hover); }

/* 탭 */
div[data-testid="stTabs"] { gap: 0px; }
div[data-testid="stTabs"] button {
    font-size: 0.85rem;
    color: var(--text-secondary);
    background: transparent;
    border: none;
    padding: 10px 20px;
    font-weight: 500;
    transition: color 0.2s;
}
div[data-testid="stTabs"] button:hover { color: var(--text-primary); }
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--text-primary) !important;
    border-bottom: 2px solid var(--color-up) !important;
}

/* ✅ Plotly 차트 잘림 방지 (강화판: iframe/내부 div 모두 커버) */
div[data-testid="stPlotlyChart"],
div[data-testid="stPlotlyChart"] > div,
div[data-testid="stPlotlyChart"] .js-plotly-plot,
div[data-testid="stPlotlyChart"] .plot-container,
div[data-testid="stPlotlyChart"] .svg-container,
div[data-testid="stPlotlyChart"] iframe {
    min-height: 340px !important;
    height: auto !important;
    overflow: visible !important;
}

/* ✅ Tabs 안에서 panel overflow로 잘리는 케이스 방지 */
div[data-testid="stTabs"] [role="tabpanel"] {
    overflow: visible !important;
}
</style>
""", unsafe_allow_html=True)
