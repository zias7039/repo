def inject(st):
    st.markdown("""
<style>
/* 1️⃣ 상단 라벨 (심볼 / 차트 간격) 숨기기 */
.stRadio > label {
    display: none !important;
}

/* 2️⃣ 내부 원형 옵션 단추(radio circle) 숨기기 */
div[role="radiogroup"] input[type="radio"] {
    display: none !important;
}

/* 3️⃣ 버튼 스타일 유지 (텍스트만 남게 칩 형태로 꾸밈) */
div[role="radiogroup"] {
    display: flex;
    flex-wrap: nowrap;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    overflow: hidden;
}

div[role="radiogroup"] > label {
    flex: 1 1 0;
    min-width: 0;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center;
    padding: 8px 16px;
    border: 1px solid rgba(148,163,184,.25);
    border-radius: 999px;
    background: #111827;
    color: #e5e7eb;
    font-size: .9rem;
    font-weight: 600;
    white-space: nowrap;
    transition: all .15s ease;
    cursor: pointer;
}

/* hover 시 강조 */
div[role="radiogroup"] > label:hover {
    background: #1f2937;
    transform: translateY(-1px);
}

/* 선택된 버튼 스타일 */
div[role="radiogroup"] > label[data-checked="true"] {
    background: #1e293b;
    border-color: #60a5fa;
    box-shadow: 0 0 0 1px #60a5fa inset;
    color: #f8fafc;
}
</style>
""", unsafe_allow_html=True)
