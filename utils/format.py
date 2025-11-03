# utils/format.py
from urllib.parse import urlencode

def fnum(v):
    try: return float(v)
    except: return 0.0

def safe_pct(num, den):
    return (num/den*100.0) if den else 0.0

def normalize_symbol(sym: str) -> str:
    return (sym or "").split("_")[0].upper()

def render_html(st, block: str):
    from textwrap import dedent
    st.markdown(dedent(block).lstrip(), unsafe_allow_html=True)
