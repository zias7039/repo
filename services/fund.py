# services/fund.py
import json
import os

DATA_FILE = "data/fund_state.json"

def load_fund_state():
    """발행 좌수(Units) 정보를 불러옵니다. 파일이 없으면 초기값 1000 설정"""
    if not os.path.exists(DATA_FILE):
        # 초기 설정: 1000 Units (필요에 따라 수정 가능)
        return {"total_units": 1000.0}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"total_units": 1000.0}

def save_fund_state(total_units):
    """발행 좌수 변경 시 저장"""
    # data 폴더가 없으면 생성
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump({"total_units": float(total_units)}, f)

def get_nav_metrics(current_equity, history_df):
    """NAV 및 변동률 계산"""
    state = load_fund_state()
    total_units = state.get("total_units", 1000.0)
    
    # 0으로 나누기 방지
    if total_units <= 0: total_units = 1.0
        
    current_nav = current_equity / total_units
    
    # 변동률 계산 (전일 자산 데이터 활용)
    # history_df에 기록된 가장 최근(어제/오늘 아침) 자산과 비교
    nav_change_pct = 0.0
    if not history_df.empty:
        # 가장 최근 기록된 스냅샷(보통 오늘 아침 9시 or 어제)
        last_equity = history_df["equity"].iloc[-1]
        if last_equity > 0:
            nav_change_pct = ((current_equity - last_equity) / last_equity) * 100.0
            
    return {
        "nav": current_nav,
        "total_units": total_units,
        "change_pct": nav_change_pct
    }
