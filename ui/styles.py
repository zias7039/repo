# ui/styles.py
def inject(st):
    st.markdown("""
<style>
:root {
  --layout-max: 1080px;
  --pill-height: 36px;
  --pill-px: 16px;
  --pill-gap: 12px;
  --pill-radius: 999px;
  --pill-font: .8rem;
  --bg-pill: #111827;
  --bg-pill-active: #1e293b;
  --bd-muted: rgba(148,163,184,.25);
  --bd-active: #60a5fa;
  --fg: #e5e7eb;
  --fg-active: #f8fafc;
}

.toolbar-row {
  padding-top: 50px;
  padding-bottom: 0 !important;  /* 기존보다 훨씬 줄임 */
  margin-bottom: -4px !important;
}

.block-container {
  max-width: var(--layout-max) !important;
  margin: 0 auto !important;
  padding: 0 16px !important;
  box-sizing: border-box;
}

div[data-testid="stHorizontalBlock"] { gap: 0 !important; }

.toolbar-row [data-testid="stHorizontalBlock"] {
  align-items: center !important;
  flex-wrap: nowrap;
  gap: 0 !important;
}

.toolbar-row [data-testid="stHorizontalBlock"] > div {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  flex: 1 1 0 !important;
  min-width: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
}

.toolbar-row [data-testid="stHorizontalBlock"] > div > div {
  width: 100% !important;
}

@media (max-width: 960px) {
  .toolbar-row [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap;
    row-gap: 8px;
  }
}

.layout-boundary,
div[data-testid="stPlotlyChart"] {
  width: 100%;
  max-width: var(--layout-max);
  margin: 0 auto;
}

div[data-testid="stPlotlyChart"] > div:first-child,
div[data-testid="stPlotlyChart"] > div:first-child > div {
  width: 100% !important;
  margin: 0 auto !important;
}

.stRadio > label { display: none !important; }

.stRadio [role="radiogroup"] {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--pill-gap);
  flex-wrap: nowrap;
  overflow-x: visible;
  overscroll-behavior-x: none;
}

.toolbar-row .stRadio { width: 100% !important; }

.stRadio [role="radiogroup"] input[type="radio"] { display: none !important; }
.stRadio [role="radiogroup"] > label > div:first-child { display: none !important; }

.stRadio [role="radiogroup"] > label {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 0 var(--pill-px) !important;
  border-radius: var(--pill-radius);
  border: 1px solid var(--bd-muted);
  background: var(--bg-pill);
  color: var(--fg);
  font-weight: 600;
  white-space: nowrap;
  min-height: var(--pill-height);
  height: var(--pill-height);
  text-align: center !important;
  overflow: hidden !important;
  transition: background .15s ease, border-color .15s ease;
}

.stRadio [role="radiogroup"] > label div[data-testid="stMarkdown"] {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  margin: 0 !important;
  font-size: var(--pill-font) !important;
  text-align: center !important;
}

.stRadio [role="radiogroup"] > label div[data-testid="stMarkdown"] p {
  margin: 0 !important;
}

.stRadio [role="radiogroup"] > label[data-checked="true"] {
  background: var(--bg-pill-active);
  color: var(--fg-active);
  border-color: var(--bd-active);
  box-shadow: inset 0 0 0 1px var(--bd-active);
}

@media (max-width: 768px) {
  :root {
    --pill-gap: 10px;
    --pill-px: 14px;
    --pill-height: 34px;
  }
}
</style>
""", unsafe_allow_html=True)
