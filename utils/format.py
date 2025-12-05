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
    # [핵심 수정] 모든 줄의 앞뒤 공백을 제거하여 코드로 인식되는 것을 방지
    lines = [line.strip() for line in block.split('\n') if line.strip()]
    clean_html = "\n".join(lines)
    st.markdown(clean_html, unsafe_allow_html=True)
