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

/* ---------------- Toolbar Area (수정됨) ---------------- */
.toolbar-container {
    display: flex;
    align-items: center;
    /* 패딩과 마진을 줄여서 차트와 가깝게 붙임 */
    padding-bottom: 4px; 
    margin-bottom: 4px;
    border-bottom: 1px solid var(--border-color);
}

/* [이하 기존 코드 동일] */
div[role="radiogroup"] {
    background-color: #1e2329; padding: 4px; border-radius: 8px; display: inline-flex; gap: 0px !important; border: 1px solid var(--border-color);
}
div[data-testid="stRadio"] label {
    margin: 0 !important; padding: 4px 12px !important; border-radius: 6px !important; transition: all 0.2s ease; border: none !important; background: transparent !important;
}
div[data-testid="stRadio"] label > div:first-child { display: none; }
div[data-testid="stRadio"] label p {
    color: var(--text-secondary); font-size: 0.85rem; font-weight: 600; margin: 0;
}
div[data-testid="stRadio"] label:hover { background-color: var(--bg-hover) !important; }
div[data-testid="stRadio"] label:hover p { color: var(--text-primary); }
div[data-testid="stRadio"] label[data-checked="true"] {
    background-color: #2b313a !important; box-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
div[data-testid="stRadio"] label[data-checked="true"] p { color: var(--color-accent) !important; }

div[data-testid="stPlotlyChart"] { overflow: hidden !important; }
div[data-testid="stPlotlyChart"] > div { overflow: hidden !important; }

.trade-table-container {
    background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px 8px 0 0; margin-top: 12px;
}
.trade-header {
    display: grid; grid-template-columns: 1.2fr 0.7fr 1.5fr 1.3fr 1fr 1fr 1fr 1fr 1fr; gap: 1rem; padding: 12px 16px; font-size: 0.75rem; font-weight: 500; color: var(--text-secondary);
}
.table-row-divider { border-top: 1px solid var(--border-color); margin: 4px 0; }

.stat-card {
    background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 16px;
}
.badge { padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
.badge-long { background: rgba(46, 189, 133, 0.15); color: #2ebd85; }
.badge-short { background: rgba(246, 70, 93, 0.15); color: #f6465d; }

div[data-testid="stVerticalBlock"] button {
    border: none !important; background: transparent !important; color: var(--text-primary) !important;
    text-align: left !important; padding: 0 !important; font-weight: 600 !important; font-size: 0.9rem !important;
}
div[data-testid="stVerticalBlock"] button:hover { color: var(--color-accent) !important; }
</style>
""", unsafe_allow_html=True)
