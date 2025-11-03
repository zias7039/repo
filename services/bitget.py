# services/bitget.py
import time, hmac, hashlib, base64, requests, pandas as pd
from utils.format import fnum

BASE_URL = "https://api.bitget.com"

def _timestamp_ms() -> str:
    return str(int(time.time() * 1000))

def _sign(ts, method, path, query_params, body, secret):
    body = body or ""
    method_up = method.upper()
    if query_params:
        from urllib.parse import urlencode
        q = urlencode(query_params)
        target = f"{ts}{method_up}{path}?{q}{body}"
    else:
        target = f"{ts}{method_up}{path}{body}"
    mac = hmac.new(secret.encode(), target.encode(), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()

def _private_get(api_key, api_secret, passphrase, path, params=None):
    ts = _timestamp_ms()
    sig = _sign(ts, "GET", path, params, "", api_secret)
    from urllib.parse import urlencode
    url = f"{BASE_URL}{path}" + (f"?{urlencode(params)}" if params else "")
    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sig,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": ts,
        "locale": "en-US",
        "Content-Type": "application/json",
    }
    return requests.get(url, headers=headers).json()

def fetch_positions(api_key, api_secret, passphrase, product_type, margin_coin):
    res = _private_get(api_key, api_secret, passphrase,
                       "/api/v2/mix/position/all-position",
                       {"productType": product_type, "marginCoin": margin_coin})
    return (res.get("data") or [], res)

def fetch_account(api_key, api_secret, passphrase, product_type, margin_coin):
    res = _private_get(api_key, api_secret, passphrase,
                       "/api/v2/mix/account/accounts",
                       {"productType": product_type, "marginCoin": margin_coin})
    arr = res.get("data") or []
    acct = next((a for a in arr if a.get("marginCoin")==margin_coin), None)
    return acct, res

def fetch_account_bills(api_key, api_secret, passphrase, product_type, limit=100):
    res = _private_get(api_key, api_secret, passphrase,
                       "/api/v2/mix/account/bill",
                       {"productType": product_type, "limit": str(limit)})
    data_obj = res.get("data", {})
    return data_obj.get("bills", [])

def fetch_kline_spot(symbol="BTCUSDT", granularity="1h", limit=100):
    params = {"symbol": symbol, "granularity": granularity, "limit": str(limit)}
    res = requests.get(f"{BASE_URL}/api/v2/spot/market/candles", params=params).json()
    if res.get("code") != "00000": return pd.DataFrame()
    data = res.get("data", [])
    if not data: return pd.DataFrame()
    df = pd.DataFrame(data, columns=["timestamp","open","high","low","close","vol_base","vol_usdt","vol_quote"])
    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(float), unit="ms")
    df = df.astype({"open":float,"high":float,"low":float,"close":float})
    return df.sort_values("timestamp")
