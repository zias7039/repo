def inject(st):
    st.markdown("""
<style>
:root{
  --bg-pill:#111827; --bg-pill-hover:#1f2937; --bg-pill-active:#1e293b;
  --bd-muted:rgba(148,163,184,.25); --bd-active:#60a5fa;
  --fg:#e5e7eb; --fg-active:#f8fafc;
  --pill-py:8px; --pill-px:16px; --pill-gap:12px; --pill-radius:999px; --pill-font:.9rem;
}

/* 라벨 숨김 */
.stRadio > label { display:none !important; }

/* 원형 라디오와 잔여 여백 제거 */
.stRadio [role="radiogroup"] input[type="radio"],
.stRadio [role="radiogroup"] > label > div:first-child,
.stRadio [role="radiogroup"] > label svg,
.stRadio [role="radiogroup"] > label::before,
.stRadio [role="radiogroup"] > label::after { display:none !important; content:none !important; }
.stRadio [role="radiogroup"] > label > * { margin:0 !important; padding:0 !important; }
.stRadio [role="radiogroup"] > label span { line-height:1 !important; }

/* pill 버튼 */
.stRadio [role="radiogroup"]{ display:flex; align-items:center; gap:var(--pill-gap); }
.stRadio [role="radiogroup"] > label{
  display:inline-flex !important; align-items:center !important; justify-content:center !important;
  padding:var(--pill-py) var(--pill-px); border-radius:var(--pill-radius);
  border:1px solid var(--bd-muted); background:var(--bg-pill); color:var(--fg);
  font-size:var(--pill-font); font-weight:600; white-space:nowrap;
  box-shadow:none !important; outline:none !important; background-image:none !important; background-clip:padding-box !important;
  transition:transform .15s ease, background .15s ease, border-color .15s ease;
  flex:0 0 auto; min-width:0;
}
.stRadio [role="radiogroup"] > label:hover{ background:var(--bg-pill-hover); transform:translateY(-1px); }
.stRadio [role="radiogroup"] > label[data-checked="true"]{
  background:var(--bg-pill-active); color:var(--fg-active);
  border-color:var(--bd-active); box-shadow:inset 0 0 0 1px var(--bd-active);
}

/* ✅ 오른쪽 칼럼을 '진짜' 우측 벽에 붙이기 */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) { /* 두 번째 column */
  display:flex; justify-content:flex-end; padding-right:0 !important; margin-right:0 !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) [role="radiogroup"] {
  justify-content:flex-end;
}

/* (선택) 컨테이너 여백이 너무 넓으면 조정 */
.block-container { padding-right:1rem; }

/* 작은 화면 조정 */
@media (max-width: 768px){
  :root{ --pill-gap:10px; --pill-px:14px; }
}
</style>
""", unsafe_allow_html=True)
