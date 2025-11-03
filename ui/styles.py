def inject(st):
    st.markdown("""
<style>
/* 라벨(‘심볼’, ‘차트 간격’) 숨김 */
.stRadio > label,
div[role="radiogroup"]::before {
    display: none !important;
}

/* 내부 옵션 버튼도 숨김 */
div[role="radiogroup"] > label {
    display: none !important;
}

/* 남는 위쪽 여백 제거 (공백 방지) */
div[data-testid="stHorizontalBlock"], 
div[data-testid="stRadio"] {
    margin-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)
