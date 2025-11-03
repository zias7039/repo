def inject(st):
    st.markdown("""
<style>
/* 상단 라벨(심볼/차트 간격) 숨김 */
.stRadio > label { display:none !important; }

/* 1) 기본 input 라디오 숨김 */
div[role="radiogroup"] input[type="radio"] { display:none !important; }

/* 2) Streamlit 라디오 원형 컨테이너 숨김 (label 안 첫 div가 보통 원형) */
div[role="radiogroup"] > label > div:first-child { display:none !important; }

/* 3) 혹시 svg 아이콘으로 그리는 테마 대응 */
div[role="radiogroup"] > label svg { display:none !important; }

/* 4) pseudo-element로 그리는 테마 대응 */
div[role="radiogroup"] > label::before,
div[role="radiogroup"] > label::after { content:none !important; display:none !important; }

/* 버튼(텍스트 칩) 스타일 유지 */
div[role="radiogroup"] {
  display:flex; flex-wrap:nowrap; justify-content:space-between; align-items:center; gap:12px; overflow:hidden;
}
div[role="radiogroup"] > label {
  flex:1 1 0; min-width:0;
  display:inline-flex !important; align-items:center !important; justify-content:center;
  padding:8px 16px; border:1px solid rgba(148,163,184,.25); border-radius:999px;
  background:#111827; color:#e5e7eb; font-size:.9rem; font-weight:600; white-space:nowrap; cursor:pointer;
  transition:all .15s ease;
}
div[role="radiogroup"] > label:hover { background:#1f2937; transform:translateY(-1px); }
div[role="radiogroup"] > label[data-checked="true"] {
  background:#1e293b; border-color:#60a5fa; box-shadow:0 0 0 1px #60a5fa inset; color:#f8fafc;

/* ✅ 라디오 그룹(특히 차트 간격) 중앙 정렬 */
div[role="radiogroup"] {
  /* 공통 기본값은 이렇게 두되 */
  display:flex; flex-wrap:nowrap; align-items:center;
  gap:12px;
  /* 중앙 정렬을 원하면 아래 두 줄이 핵심 */
  justify-content:center;     /* ← 가운데 정렬 */
  width:auto;                 /* ← 100%로 늘리지 않음 */
  margin:0 auto;              /* ← 부모 안에서 중앙 배치 */
}

/* ✅ 버튼(칩)들이 가로로 늘어나지 않도록 고정 */
div[role="radiogroup"] > label {
  flex:0 0 auto;              /* ← 더 이상 1 1 0 로 늘리지 않음 */
  min-width:0;
}

/* 만약 심볼/간격 두 그룹을 따로 제어하고 싶으면 (오른쪽 그룹만 중앙) */
div[role="radiogroup"]:last-of-type {
  justify-content:center;
  width:auto;
  margin:0 auto;
}
div[role="radiogroup"]:last-of-type > label {
  flex:0 0 auto;
}

/* (선택) columns 오른쪽 칸 자체를 중앙 정렬로 만들고 싶다면 추가 */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
  display:flex; justify-content:center;
}

}
</style>
""", unsafe_allow_html=True)
