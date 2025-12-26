/* ===== PnL Chart Card ===== */
.chart-card{
  padding: 16px 18px 14px 18px;
}

/* 헤더 영역 */
.chart-head{
  padding: 2px 6px 12px 6px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 10px;
}

.chart-head-grid{
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: start;
  column-gap: 12px;
}

.chart-left{
  display:flex;
  gap:8px;
  align-items:center;
}

.chart-title{
  font-size:0.95rem;
  font-weight:600;
  color: var(--text-primary);
}

.chart-badge{
  background:#262626;
  color:#737373;
  padding:2px 8px;
  border-radius:12px;
  font-size:0.7rem;
  font-weight:600;
}

.chart-right{ text-align:right; }

.chart-label{
  font-size:0.75rem;
  color:#737373;
  margin-bottom:2px;
  font-weight:500;
}

.chart-pnl{
  font-family: var(--font-mono);
  font-weight:700;
  font-size:1.1rem;
  letter-spacing:-0.5px;
  display:flex;
  justify-content:flex-end;
  gap:8px;
  flex-wrap:wrap;
}

.chart-krw{
  font-size:0.9rem;
  color:#737373;
  font-weight:500;
}

/* Plotly 영역: 카드 내부에서 모양 안정화 */
.chart-card div[data-testid="stPlotlyChart"],
.chart-card .stPlotlyChart{
  min-height: 300px !important;
  overflow: visible !important;
}

.chart-card div[data-testid="stPlotlyChart"] > div,
.chart-card .stPlotlyChart > div{
  border-radius: 8px;
  overflow: hidden; /* ✅ 카드 안에서만 깔끔하게 클리핑 */
}

/* Tabs 안 panel이 잘라먹는 경우 방지 */
div[data-testid="stTabs"] [role="tabpanel"]{
  overflow: visible !important;
}
