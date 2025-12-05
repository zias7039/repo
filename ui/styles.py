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

/* 상단 카드 */
.stat-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 16px;
}

/* 입력창 */
.stTextInput input {
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
}

/* 차트 스크롤 숨김 */
div[data-testid="stPlotlyChart"] { overflow: hidden !important; }
div[data-testid="stPlotlyChart"] > div { overflow: hidden !important; }

/* 데이터프레임 헤더 테두리 조정 (선택 사항) */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-color);
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)
