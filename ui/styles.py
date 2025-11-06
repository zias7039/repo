def inject(st):
    st.markdown("""
<style>
:root {
  --layout-max: 1080px;
  --pill-height: 36px;
  --pill-px: 16px;
  --pill-gap: 6px;
  --pill-radius: 999px;
  --pill-font: .8rem;
  --bg-pill: #111827;
  --bg-pill-active: #1e293b;
  --bd-muted: rgba(148,163,184,.25);
  --bd-active: #60a5fa;
  --fg: #e5e7eb;
  --fg-active: #f8fafc;
}

.chart-title {
  margin-top: 0px !important;   /* 위 간격 */
  margin-bottom: 0 !important;
  line-height: 1.2;
}

/* 상단 툴바 정렬 */
.toolbar-row {
  padding-top: 50px;
  padding-bottom: 0 !important;
  margin-bottom: 0 !important;
}

.toolbar-row .stRadio,
.toolbar-row [data-testid="stHorizontalBlock"],
.toolbar-row [role="radiogroup"] {
  margin-bottom: 0 !important;
}

.block-container {
  max-width: var(--layout-max) !important;
  margin: 0 auto !important;
  padding: 0 16px !important;
  box-sizing: border-box;
}

.toolbar-row [data-testid="stHorizontalBlock"] {
  display: flex;
  align-items: center !important;
  flex-wrap: nowrap;
  gap: 0 !important;
}

.toolbar-row [data-testid="stHorizontalBlock"] > div {
  flex: 1 1 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  min-width: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
}

@media (max-width: 960px) {
  .toolbar-row [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap;
    row-gap: 8px;
  }
}

/* 차트 크기 조정 */
.layout-boundary,
div[data-testid="stPlotlyChart"] {
  width: 100%;
  max-width: var(--layout-max);
  margin: 0 auto;
}

div[data-testid="stPlotlyChart"] > div:first-child > div {
  width: 100% !important;
  margin: 0 auto !important;
}

/* 라디오 버튼 스타일 */
.stRadio > label { display: none !important; }

.stRadio [role="radiogroup"] {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: nowrap;
  gap: var(--pill-gap) !important;
}

.stRadio [role="radiogroup"] input[type="radio"],
.stRadio [role="radiogroup"] > label > div:first-child {
  display: none !important;
}

.stRadio [role="radiogroup"] > label {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  padding: 0 var(--pill-px) !important;
  border-radius: var(--pill-radius);
  border: 1px solid var(--bd-muted);
  background: var(--bg-pill);
  color: var(--fg);
  font-weight: 600;
  white-space: nowrap;
  height: var(--pill-height);
  transition: background .15s ease, border-color .15s ease;
}

.stRadio [role="radiogroup"] > label div[data-testid="stMarkdown"] {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 !important;
  font-size: var(--pill-font) !important;
}

.stRadio [role="radiogroup"] > label[data-checked="true"] {
  background: var(--bg-pill-active);
  color: var(--fg-active);
  border-color: var(--bd-active);
  box-shadow: inset 0 0 0 1px var(--bd-active);
}
</style>
""", unsafe_allow_html=True)
