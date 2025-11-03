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

/* 원형옵션 완전 제거 */
.stRadio [role="radiogroup"] input[type="radio"],
.stRadio [role="radiogroup"] > label > div:first-child,
.stRadio [role="radiogroup"] > label svg,
.stRadio [role="radiogroup"] > label::before,
.stRadio [role="radiogroup"] > label::after { display:none !important; content:none !important; }
.stRadio [role="radiogroup"] > label > * { margin:0 !important; padding:0 !important; }
.stRadio [role="radiogroup"] > label span { line-height:1 !important; }

/* pill 공통 */
.stRadio [role="radiogroup"] { display:flex; gap:var(--pill-gap); }
.stRadio [role="radiogroup"] > label{
  display:inline-flex !important; align-items:center !important; justify-content:center !important;
  padding:var(--pill-py) var(--pill-px); border-radius:var(--pill-radius);
  border:1px solid var(--bd-muted); background:var(--bg-pill); color:var(--fg);
  font-size:var(--pill-font); font-weight:600; white-space:nowrap; flex:0 0 auto; min-width:0;
  box-shadow:none !important; outline:none !important; background-image:none !important; background-clip:padding-box !important;
  transition:transform .15s ease, background .15s ease, border-color .15s ease;
}
.stRadio [role="radiogroup"] > label:hover{ background:var(--bg-pill-hover); transform:translateY(-1px); }
.stRadio [role="radiogroup"] > label[data-checked="true"]{ background:var(--bg-pill-active); color:var(--fg-active); border-color:var(--bd-active); box-shadow:inset 0 0 0 1px var(--bd-active); }

/* 왼쪽 그룹: 중앙 배치(필요 시) */
.symbol-wrap{ display:flex; justify-content:flex-start; width:100%; }
.symbol-wrap .stRadio > div { display:flex; justify-content:flex-start !important; }
.symbol-wrap [role="radiogroup"]{ justify-content:flex-start; }

/* 오른쪽 그룹: 우측 벽 밀착 */
.gran-wrap{ display:flex; justify-content:flex-end; width:100%; }
.gran-wrap .stRadio > div{ display:flex; justify-content:flex-end !important; width:100%; }
.gran-wrap [role="radiogroup"]{ justify-content:flex-end; width:fit-content; margin-left:auto; }

/* 🔧 Streamlit 칼럼 좌/우 패딩 제거(우측 칼럼 끝까지 붙이기) */
div[data-testid="stHorizontalBlock"] > div:first-child { padding-left:0 !important; }
div[data-testid="stHorizontalBlock"] > div:last-child  { padding-right:0 !important; margin-right:0 !important; }

/* 상단 block은 좌/우로 벌리기 */
div[data-testid="stHorizontalBlock"] { justify-content:space-between !important; }

/* 반응형 */
@media (max-width: 768px){ :root{ --pill-gap:10px; --pill-px:14px; } }
</style>
""", unsafe_allow_html=True)
