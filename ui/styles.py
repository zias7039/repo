def inject(st):
    st.markdown("""
<style>
/* 🔸 '심볼', '차트 간격' 같은 라디오 그룹 상단 라벨 제거 */
.stRadio > label {
    display: none !important;
}

/* 🔸 버튼 스타일은 유지 — 이전과 동일 */
div[role="radiogroup"] {
    display: flex;
    flex-wrap: nowrap;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    width: 100%;
    overflow: hidden;
    box-sizing: border-box;
}

div[role="radiogroup"] > label {
    flex: 1 1 0;
    min-width: 0;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center;
    padding: 10px 18px;
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

div[role="radiogroup"] > label:hover {
    background: #1f2937;
    transform: translateY(-1px);
}

div[role="radiogroup"] > label[data-checked="true"] {
    background: #1e293b;
    border-color: #60a5fa;
    box-shadow: 0 0 0 1px #60a5fa inset;
    color: #f8fafc;
}
</style>
""", unsafe_allow_html=True)
