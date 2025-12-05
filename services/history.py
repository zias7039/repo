# services/history.py
import os
import pandas as pd
from datetime import datetime, timedelta, timezone

# 데이터 저장 경로
DATA_DIR = "data"
FILE_PATH = os.path.join(DATA_DIR, "equity_history.csv")

def get_kst_now():
    return datetime.now(timezone(timedelta(hours=9)))

def load_history():
    """기록된 자산 데이터를 불러옵니다."""
    if not os.path.exists(FILE_PATH):
        return pd.DataFrame(columns=["date", "equity"])
    try:
        df = pd.read_csv(FILE_PATH)
        return df
    except Exception:
        return pd.DataFrame(columns=["date", "equity"])

def try_record_snapshot(current_equity):
    """
    오늘 날짜(KST 기준)의 기록이 없고, 현재 시간이 오전 9시 이후라면 저장합니다.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    df = load_history()
    now_kst = get_kst_now()
    today_str = now_kst.strftime("%Y-%m-%d")

    # 1. 이미 오늘 기록이 있는지 확인
    if today_str in df["date"].values:
        return df, False  # 이미 기록됨

    # 2. 시간이 09:00 넘었는지 확인
    if now_kst.hour >= 9:
        new_row = pd.DataFrame([{"date": today_str, "equity": current_equity}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(FILE_PATH, index=False)
        return df, True # 새로 기록됨
        
    return df, False
