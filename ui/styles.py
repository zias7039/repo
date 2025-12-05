# ui/styles.py
def inject(st):
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg-app: #0b0e11;
  --bg-card: #151a21;
  --border-color: #2b313a;
  --text-primary: #eaecef;
  --text-secondary: #848e9c;
  --text-tertiary: #5e6673;
  --color-up: #2ebd85;
  --color-down: #f6465d;
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

/* ---------------- Table Layout ---------------- */
.trade-table-container {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px 8px 0 0;
    margin-top: 12px;
}

/* 헤더: st.columns 비율과 비슷하게 CSS Grid로 맞춤 */
.trade-header {
    display: grid;
    grid-template-columns: 1.2fr 0.7fr 1.5fr 1.3fr 1fr 1fr 1fr 1fr 1fr;
    gap: 1rem;
    padding: 12px 16px;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-secondary);
}

.table-row-divider {
    border-top: 1px solid var(--border-color);
    margin: 4px 0;
}

/* ---------------- Badges ---------------- */
.badge {
    padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;
    display: inline-block;
}
.badge-long { background: rgba(46, 189, 133, 0.15); color: var(--color-up); }
.badge-short { background: rgba(246, 70, 93, 0.15); color: var(--color-down); }

/* ---------------- Invisible Button Style ---------------- */
/* 버튼을 텍스트처럼 보이게 만드는 마법 */
div[data-testid="stVerticalBlock"] button {
    border: none !important;
    background: transparent !important;
    color: var(--text-primary) !important;
    text-align: left !important;
    padding: 0 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    line-height: 1.2 !important;
    transition: color 0.2s;
}
div[data-testid="stVerticalBlock"] button:hover {
    color: var(--color-accent) !important;
}
div[data-testid="stVerticalBlock"] button p {
    font-size: 0.9rem;
}

/* ---------------- Others ---------------- */
.stat-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 16px;
}
.stTextInput input {
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
}
div[data-testid="stPlotlyChart"] { overflow: hidden !important; }
div[data-testid="stPlotlyChart"] > div { overflow: hidden !important; }
</style>
""", unsafe_allow_html=True)
