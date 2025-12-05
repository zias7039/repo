# utils/format.py
import streamlit as st
from textwrap import dedent

def fnum(v):
    try: return float(v)
    except: return 0.0

def safe_pct(num, den):
    return (num/den*100.0) if den else 0.0

def normalize_symbol(sym: str) -> str:
    return (sym or "").split("_")[0].upper()

def render_html(st, block: str):
    # 1. 문자열 앞뒤의 줄바꿈 제거
    block = block.strip()
    # 2. 공통 들여쓰기(indentation) 제거
    clean_html = dedent(block)
    # 3. HTML 렌더링
    st.markdown(clean_html, unsafe_allow_html=True)
