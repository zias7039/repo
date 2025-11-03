def inject(st):
    st.markdown("""
<style>
/* ------------------ Design tokens ------------------ */
:root{
  --bg-pill:#111827;          /* pill 배경 */
  --bg-pill-hover:#1f2937;    /* hover */
  --bg-pill-active:#1e293b;   /* active */
  --bd-muted:rgba(148,163,184,.25);
  --bd-active:#60a5fa;
  --fg:#e5e7eb;
  --fg-active:#f8fafc;
  --pill-py:8px;
  --pill-px:16px;
  --pill-gap:12px;
  --pill-radius:999px;
  --pill-font:.9rem;
}

/* ------------------ 기본 설정 ------------------ */

/* 라벨 텍스트(“심볼/차트 간격”) 숨김 */
.stRadio > label { display:none !important; }

/* 라디오 원형, 아이콘 등 제거 */
.stRadio [role="radiogroup"] input[type="radio"],
.stRadio [role="radiogroup"] > label > div:first-child,
.stRadio [role="radiogroup"] > label svg,
.stRadio [role="radiogroup"] > label::before,
.stRadio [role="radiogroup"] > label::after {
  display:none !important; content:none !important;
}

/* 내부 여백 초기화 */
.stRadio [role="radiogroup"] > label > * {
  margin:0 !important; padding:0 !important;
}
.stRadio [role="radiogroup"] > label span {
  line-height:1 !important;
}

/* ------------------ 그룹 래퍼 ------------------ */
.symbol-wrap, .gran-wrap {
  display:flex;
  justify-content:center;
  width:100%;
}
.symbol-wrap .stRadio > div,
.gran-wrap .stRadio > div {
  display:flex;
  justify-content:center !important;
}
.symbol-wrap [role="radiogroup"],
.gran-wrap [role="radiogroup"] {
  display:flex;
  align-items:center;
  justify-content:center;
  gap:var(--pill-gap);
  width:fit-content;
  margin:0 auto;
}

/* ------------------ pill 공통 ------------------ */
.stRadio [role="radiogroup"] > label {
  display:inline-flex !important;
  align-items:center !important;
  justify-content:center !important;
  padding:var(--pill-py) var(--pill-px);
  border-radius:var(--pill-radius);
  border:1px solid var(--bd-muted);
  background:var(--bg-pill);
  color:var(--fg);
  font-size:var(--pill-font);
  font-weight:600;
  white-space:nowrap;
  box-shadow:none !important;
  outline:none !important;
  background-image:none !important;
  background-clip:padding-box !important;
  overflow:hidden !important;
  transition:transform .15s ease, background .15s ease, border-color .15s ease;
  flex:0 0 auto;
  min-width:0;
}

.stRadio [role="radiogroup"] > label:hover {
  background:var(--bg-pill-hover);
  transform:translateY(-1px);
}

.stRadio [role="radiogroup"] > label[data-checked="true"] {
  background:var(--bg-pill-active);
  color:var(--fg-active);
  border-color:var(--bd-active);
  box-shadow:inset 0 0 0 1px var(--bd-active);
}

/* ------------------ 오른쪽 정렬(차트 간격) ------------------ */
.gran-wrap {
  display:flex;
  justify-content:flex-end;
  width:100%;
  margin-right:0;
  padding-right:0;
}

/* 내부 라디오 그룹 내용만큼 차지 */
.gran-wrap [role="radiogroup"] {
  width:fit-content;
  margin-left:auto;
  margin-right:0;
}

/* Streamlit column 기본 패딩 제거 */
div[data-testid="column"]:has(.gran-wrap) {
  padding-right:0 !important;
  margin-right:0 !important;
}

/* 상위 컨테이너 좌우 끝 벌리기 */
div[data-testid="stHorizontalBlock"] {
  justify-content:space-between !important;
}

/* ------------------ 반응형 ------------------ */
@media (max-width:768px){
  :root{
    --pill-gap:10px;
    --pill-px:14px;
  }
}
</style>
""", unsafe_allow_html=True)
