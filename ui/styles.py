def inject(st):
    st.markdown("""
<style>
/* ========== 기본 라벨 숨기기 ========== */
.stRadio > label { display:none !important; }

/* ========== 라디오 원형 및 잔여 여백 완전 제거 ========== */
.stRadio [role="radiogroup"] input[type="radio"] { display:none !important; }
.stRadio [role="radiogroup"] > label > div:first-child {
  display:none !important;
  width:0 !important; height:0 !important;
  margin:0 !important; padding:0 !important; border:0 !important;
}
.stRadio [role="radiogroup"] > label svg { display:none !important; }
.stRadio [role="radiogroup"] > label::before,
.stRadio [role="radiogroup"] > label::after { content:none !important; display:none !important; }
.stRadio [role="radiogroup"] > label span {
  margin:0 !important; padding:0 !important; line-height:1 !important;
}

/* ========== 중앙 정렬 컨테이너 ========== */
.symbol-wrap, .gran-wrap { display:flex; justify-content:center; width:100%; }
.symbol-wrap .stRadio > div, .gran-wrap .stRadio > div { display:flex; justify-content:center !important; }

.symbol-wrap [role="radiogroup"], .gran-wrap [role="radiogroup"] {
  display:flex; align-items:center; justify-content:center; gap:12px;
  width:fit-content; margin:0 auto;
}

/* 버튼 크기 고정 */
.symbol-wrap [role="radiogroup"] > label,
.gran-wrap [role="radiogroup"] > label {
  flex:0 0 auto; min-width:0;
}

/* ========== 버튼(칩) 스타일 ========== */
div[role="radiogroup"] > label {
  display:inline-flex !important;
  align-items:center !important;
  justify-content:center;
  padding:8px 16px;
  border:1px solid rgba(148,163,184,.25);
  border-radius:999px;
  background:#111827;
  color:#e5e7eb;
  font-size:.3rem;
  white-space:nowrap;
  cursor:pointer;
  transition:all .15s ease;
  box-shadow:none !important;
  outline:none !important;
  background-image:none !important;
  background-clip:padding-box;
  overflow:hidden;
}

div[role="radiogroup"] > label:hover {
  background:#1f2937;
  transform:translateY(-1px);
}

div[role="radiogroup"] > label[data-checked="true"] {
  background:#1e293b;
  border-color:#60a5fa;
  box-shadow:inset 0 0 0 1px #60a5fa;
  color:#f8fafc;
}

/* 1) label을 강제로 flex 중앙 정렬, grid 흔적 제거 */
.stRadio [role="radiogroup"] > label {
  display:inline-flex !important;
  align-items:center !important;
  justify-content:center !important;
  position:relative;
  gap:0 !important;
  /* 좌우 패딩을 완전 대칭으로 */
  padding:8px 16px !important;
  text-align:center !important;

  /* 시각 잡음 제거 */
  box-shadow:none !important;
  outline:none !important;
  background-image:none !important;
  background-clip:padding-box !important;
  overflow:hidden !important;
}

/* 2) label 내부의 모든 자식 여백/패딩 제거 (원형 자리, span 등) */
.stRadio [role="radiogroup"] > label > * {
  margin:0 !important;
  padding:0 !important;
}

/* 3) 텍스트 노드(span) 강제 중앙화 */
.stRadio [role="radiogroup"] > label span {
  display:block !important;
  margin:0 !important;
  padding:0 !important;
  line-height:1 !important;
  text-align:center !important;
}

/* 4) 숨긴 라디오/아이콘 칸이 공간을 차지하지 못하게 */
.stRadio [role="radiogroup"] input[type="radio"] { display:none !important; }
.stRadio [role="radiogroup"] > label > div:first-child {
  display:none !important;
  width:0 !important; height:0 !important;
  margin:0 !important; padding:0 !important; border:0 !important;
}
.stRadio [role="radiogroup"] > label svg { display:none !important; }
.stRadio [role="radiogroup"] > label::before,
.stRadio [role="radiogroup"] > label::after { content:none !important; display:none !important; }

/* 5) (선택) 시각적 중심 맞춤 미세 튜닝
   Inter 대문자에서 약간 왼쪽으로 보이면 1px 정도 오른쪽에 더 주면 균형이 좋아짐 */
.symbol-wrap [role="radiogroup"] > label,
.gran-wrap   [role="radiogroup"] > label {
  padding-left:17px !important;
  padding-right:17px !important;  /* 좌우 완전 동일(원래 16px이면 17px/17px 같이 맞춰도 OK) */
}

/* 6) 그룹 자체 중앙 정렬 재확인 */
.symbol-wrap, .gran-wrap { display:flex; justify-content:center; width:100%; }
.symbol-wrap .stRadio > div, .gran-wrap .stRadio > div {
  display:flex; justify-content:center !important;
}
.symbol-wrap [role="radiogroup"], .gran-wrap [role="radiogroup"] {
  display:flex; align-items:center; justify-content:center;
  gap:12px; width:fit-content; margin:0 auto;
}
.symbol-wrap [role="radiogroup"] > label, .gran-wrap [role="radiogroup"] > label {
  flex:0 0 auto; min-width:0;
}
</style>
""", unsafe_allow_html=True)
