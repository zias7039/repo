# services/upbit.py
import requests
import streamlit as st

@st.cache_data(ttl=60)
def fetch_usdt_krw() -> float | None:
    try:
        res = requests.get(
            "https://api.upbit.com/v1/ticker",
            params={"markets": "USDT-BTC,KRW-BTC"},
            timeout=5
        )
        data = res.json()
        btc_usdt = next((d["trade_price"] for d in data if d["market"]=="USDT-BTC"), None)
        btc_krw  = next((d["trade_price"] for d in data if d["market"]=="KRW-BTC"), None)
        if btc_usdt and btc_krw:
            return float(btc_krw) / float(btc_usdt)
    except Exception:
        pass
    return None
