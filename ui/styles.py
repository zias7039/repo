# ui/styles.py
def inject(st):
    st.markdown("""
<style>
:root{
  --bg-pill:#111827; --bg-pill-hover:#1f2937; --bg-pill-active:#1e293b;
  --bd-muted:rgba(148,163,184,.25); --bd-active:#60a5fa;
  --fg:#e5e7eb; --fg-active:#f8fafc;
  --pill-py:8px; --pill-px:16px; --pill-gap:12px; --pill-radius:999px; --pill-font:.9rem;
}

/* ▶ 한 줄 레이아웃: 좌/우 끝에 붙이기 */
.toolbar-row{ display:flex; align-items:center; gap:16px; width:100%; }
.toolbar-left{ flex:1 1 auto; display:flex; justify-content:flex-start; }
.toolbar-right{ flex:1 1 auto; display:flex; justify-content:flex-end; }

/* 기본 라벨 숨김 */
.stRadio > label { display:none !important; }

/* 원형 라디오 및 잔여공간 제거 */
.stRadio [role="radiogroup"] input[type="radio"],
.stRadio [role="radiogroup"] > label > div:first-child,
.stRadio [role="radiogroup"] > label svg,
.stRadio [role="radiogroup"] > label::before,
.stRadio [role="radiogroup"] > label::after { display:none !important; content:none !important; }
.stRadio [role="radiogroup"] > label > * { margin:0 !important; padding:0 !important; }
.stRadio [role="radiogroup"] > label span { line-height:1 !important; }

/* 라디오 그룹(칩) */
.stRadio [role="radiogroup"]{ display:flex; align-items:center; gap:var(--pill-gap); }
.stRadio [role="radiogroup"] > label{
  display:inline-flex !important; align-items:center !important; justify-content:center !important;
  padding:var(--pill-py) var(--pill-px);
  border-radius:var(--pill-radius);
  border:1px solid var(--bd-muted);
  background:var(--bg-pill); color:var(--fg);
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

/* Streamlit 컨테이너 기본 패딩 때문에 오른쪽이 안 붙는 경우 방지 */
.block-container{ padding-left:1rem; padding-right:1rem; }    /* 원하면 조정 */
</style>
""", unsafe_allow_html=True)
