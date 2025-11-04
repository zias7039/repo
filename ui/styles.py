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

.block-container {
  max-width: var(--layout-max) !important;
  margin: 0 auto !important;
  padding: 0 auto !important;
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

@media (max-width: 768px) {
  :root {
    --pill-gap: 10px;
    --pill-px: 14px;
    --pill-height: 34px;
  }
}
</style>
""", unsafe_allow_html=True)
