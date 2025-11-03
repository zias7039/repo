# ui/styles.py
def inject(st):
    st.markdown("""
<style>
/* ------------------ Global Layout Fix ------------------ */

/* Streamlit 기본 컨테이너 폭 제한 해제 → 화면 전체 폭 사용 */
.block-container{
  max-width: 100% !important;
  padding-left: 16px !important;
  padding-right: 16px !important;
}

/* columns 간격 최소화 */
div[data-testid="stHorizontalBlock"] { gap: 0 !important; }

/* 두 번째 column(우측 칼럼) → 우측 정렬 & 패딩 제거 */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-right: 0 !important;
  margin-right: 0 !important;
}

/* ------------------ Pill Style ------------------ */
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
  --pill-font:.5rem;
}

/* 라벨 텍스트 숨김 */
.stRadio > label { display:none !important; }

/* 원형 라디오 및 잔여 영역 제거 */
.stRadio [role="radiogroup"] input[type="radio"],
.stRadio [role="radiogroup"] > label > div:first-child,
.stRadio [role="radiogroup"] > label svg,
.stRadio [role="radiogroup"] > label::before,
.stRadio [role="radiogroup"] > label::after {
  display:none !important;
  content:none !important;
}
.stRadio [role="radiogroup"] > label > * { margin:0 !important; padding:0 !important; }
.stRadio [role="radiogroup"] > label span { line-height:1 !important; }

/* 버튼(텍스트 칩) */
.stRadio [role="radiogroup"]{
  display:flex;
  align-items:center;
  gap:var(--pill-gap);
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
  font-size:var(--pill-font) !important;
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

/* 작은 화면 대응 */
@media (max-width: 768px){
  :root{ --pill-gap:10px; --pill-px:14px; }
}

</style>
""", unsafe_allow_html=True)
