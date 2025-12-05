# utils/format.py
import streamlit as st

def fnum(v):
    try: return float(v)
    except: return 0.0

def safe_pct(num, den):
    return (num/den*100.0) if den else 0.0

def normalize_symbol(sym: str) -> str:
    return (sym or "").split("_")[0].upper()

def render_html(st, block: str):
    # [핵심 수정] HTML 문자열의 모든 줄에서 앞뒤 공백을 강제로 제거
    # 들여쓰기가 있으면 마크다운 코드 블록으로 인식되는 문제 완벽 해결
    lines = [line.strip() for line in block.split('\n') if line.strip()]
    clean_html = "\n".join(lines)
    st.markdown(clean_html, unsafe_allow_html=True)
