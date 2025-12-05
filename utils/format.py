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
    # ✅ 공백과 줄바꿈을 강력하게 제거하여 HTML로 인식되게 함
    clean_html = dedent(block).strip()
    st.markdown(clean_html, unsafe_allow_html=True)
