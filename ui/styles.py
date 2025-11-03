def inject(st):
    st.markdown("""
<style>
:root{
  --bg-pill:#111827;
  --bg-pill-hover:#1f2937;
  --bg-pill-active:#1e293b;
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

/* 라벨 숨김 */
.stRadio > label { display:none !important; }

/* 라디오 원형 제거 */
.stRadio [role="radiogroup"] input[type="radio"],
.stRadio [role="radiogroup"] > label > div:first-child,
.stRadio [role="radiogroup"] > label svg,
.stRadio [role="radiogroup"] > label::before,
.stRadio [role="radiogroup"] > label::after {
  display:none !important; content:none !important;
}

/* ---- 공통 pill 스타일 ---- */
.stRadio [role="radiogroup"]{
  display:flex; align-items:center; gap:var(--pill-gap);
}
.stRadio [role="radiogroup"] > label{
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
  background-clip:padding-box !important;
  overflow:hidden !important;
  transition:transform .15s ease, background .15s ease, border-color .15s ease;
  flex:0 0 auto; min-width:0;
}
.stRadio [role="radiogroup"] > label:hover{
  background:var(--bg-pill-hover);
  transform:translateY(-1px);
}
.stRadio [role="radiogroup"] > label[data-checked="true"]{
  background:var(--bg-pill-active);
  color:var(--fg-active);
  border-color:var(--bd-active);
  box-shadow:inset 0 0 0 1px var(--bd-active);
}

/* ---- 정렬 컨테이너 ---- */
.symbol-wrap{
  display:flex;
  justify-content:flex-start;
  width:100%;
}
.symbol-wrap .stRadio > div{
  display:flex;
  justify-content:flex-start !important;
}

.gran-wrap{
  display:flex;
  justify-content:flex-end;
  width:100%;
}
.gran-wrap .stRadio > div{
  display:flex;
  justify-content:flex-end !important;
}
.gran-wrap [role="radiogroup"]{
  width:fit-content;
  margin-left:auto; /* 오른쪽 끝으로 붙이기 */
}

/* 오른쪽 컬럼 기본 padding 제거 */
div[data-testid="column"]:has(.gran-wrap){
  padding-right:0 !important;
}

@media (max-width:768px){
  :root{ --pill-gap:10px; --pill-px:12px; }
}
</style>
""", unsafe_allow_html=True)
