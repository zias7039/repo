def inject(st):
    st.markdown("""
<style>
:root{
  /* ---------- 공통 변수 ---------- */
  --layout-max: 1080px;

  /* 간격/사이즈 */
  --toolbar-top: 50px;         /* 상단 여백 (기존 50px → 20px) */
  --row-gap: 4px;              /* 툴바 내부 세로 간격 */
  --title-offset: -6px;        /* 검색창 아래 타이틀 위쪽 당김값 */
  --input-h: 32px;             /* 검색 입력 높이 */
  --input-radius: 8px;         /* 검색 입력 라운드 */
  --input-pl: 26px;            /* 아이콘 자리 패딩 */

  /* 팔레트 */
  --bg-input: #121317;
  --bd-muted: rgba(148,163,184,.25);
  --fg: #e5e7eb;
  --fg-dim: rgba(229,231,235,.45);
}

/* ---------- 컨테이너/레이아웃 ---------- */
.block-container{
  max-width: var(--layout-max) !important;
  margin: 0 auto !important;
  padding: 0 16px !important;
  box-sizing: border-box;
}

.layout-boundary{ max-width: var(--layout-max); margin: 0 auto; }

.toolbar-row{
  padding-top: var(--toolbar-top);
  margin-bottom: 0 !important;
}

.layout-boundary [data-testid="stVerticalBlock"]{ row-gap: var(--row-gap) !important; }

/* ---------- 차트(Plotly) 영역 ---------- */
div[data-testid="stPlotlyChart"]{
  max-width: var(--layout-max);
  margin: 0 auto;
}
div[data-testid="stPlotlyChart"] > div:first-child > div{
  width: 100% !important;
  margin: 0 auto !important;
}

/* ---------- 검색 입력 ---------- */
.symbol-search .stTextInput > div > div{
  position: relative;
  margin-bottom: 0 !important;   /* 입력 아래 여백 제거 */
  padding-bottom: 0 !important;
}
.symbol-search .stTextInput > div > div input{
  height: var(--input-h) !important;
  width: 100% !important;
  padding-left: var(--input-pl) !important;
  border-radius: var(--input-radius) !important;
  background: var(--bg-input) !important;
  border: 1px solid var(--bd-muted) !important;
  color: var(--fg) !important;
  font-size: .8rem !important;
}

.symbol-search .stTextInput > div > div::before{
  content: "🔍";
  position: absolute;
  left: 8px; top: 50%;
  transform: translateY(-50%);
  opacity: .55; pointer-events: none; font-size: 12px;
}
/* placeholder 톤 다운 */
.symbol-search input::placeholder{ color: var(--fg-dim) !important; }

/* 검색창 아래 여백 통제 */
.symbol-search{ margin-bottom: 0 !important; }

/* ---------- 차트 제목 ---------- */
.chart-title{
  margin: var(--title-offset) 0 0 0 !important; 
  line-height: 0 !important;
  padding: 0 !important;
}
</style>
""", unsafe_allow_html=True)
