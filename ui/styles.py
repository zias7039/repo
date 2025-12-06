# ui/styles.py
def inject(st):
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
  --bg-app: #0b0e11;
  --bg-card: #161a1e;
  --bg-hover: #2b313a;
  --border-color: #2b313a;
  --text-primary: #eaecef;
  --text-secondary: #848e9c;
  --text-tertiary: #5e6673;
  --color-up: #2ebd85;
  --color-down: #f6465d;
  --color-accent: #fcd535;
  --radius-md: 6px;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
    background-color: var(--bg-app);
}
.stApp { background-color: var(--bg-app); }

/* [수정됨] 상단 여백 확보 (Toolbar 겹침 방지) */
.block-container {
    max-width: 100% !important;
    padding-top: 3.5rem !important; /* 1rem -> 3.5rem으로 변경 */
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Streamlit 기본 헤더(햄버거 메뉴 등) 배경 투명화 (선택사항) */
header[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* 커스텀 헤더 */
.dashboard-header {
    display: flex; justify-content: space-between; align-items: center;
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 12px 20px;
    margin-bottom: 12px;
}
.header-title { font-size: 1.2rem; font-weight: 800; letter-spacing: 1px; }
.header-badge { font-size: 0.7rem; background: #2b313a; color: #848e9c; padding: 2px 6px; border-radius: 4px; margin-left: 8px; vertical-align: middle; }

/* 사이드바/정보 카드 */
.side-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 16px;
    margin-bottom: 12px;
}
.stat-label { font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px; }
.stat-value { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); font-family: 'JetBrains Mono', monospace; }
.stat-sub { font-size: 0.8rem; margin-top: 4px; font-family: 'JetBrains Mono', monospace; }

/* 탭 스타일 재정의 */
div[data-testid="stTabs"] button {
    font-size: 0.9rem; font-weight: 600; color: var(--text-secondary);
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--text-primary) !important;
    border-bottom-color: var(--color-accent) !important;
}

/* 테이블 스타일 */
.trade-table-container {
    background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md); margin-top: 0px;
}
.trade-header {
    display: grid; grid-template-columns: 1.2fr 0.7fr 1.5fr 1.3fr 1.0fr 1.0fr 1.0fr 1.0fr 1.0fr; 
    gap: 8px; padding: 12px 16px; font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); border-bottom: 1px solid var(--border-color);
}
.table-row-divider { border-top: 1px solid var(--border-color); margin: 6px 0; }
.badge { padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
.badge-long { background: rgba(46, 189, 133, 0.15); color: #2ebd85; }
.badge-short { background: rgba(246, 70, 93, 0.15); color: #f6465d; }

/* 차트/툴바 영역 조정 */
.toolbar-container { padding-bottom: 8px; border-bottom: none; }
</style>
""", unsafe_allow_html=True)
