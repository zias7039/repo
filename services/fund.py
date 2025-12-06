# services/fund.py
import json
import os

DATA_FILE = "data/fund_state.json"

def load_fund_state():
    """
    투자자별 Units 정보를 불러옵니다. 
    파일이 없거나 구버전일 경우, 기본적으로 Investor A/B에게 500좌씩 분배합니다.
    """
    default_state = {
        "investors": {
            "Investor A": 511.0,
            "Investor B": 467.0
        }
    }

    if not os.path.exists(DATA_FILE):
        return default_state
    
    try:
        with open(DATA_FILE, "r", encoding='utf-8') as f:
            data = json.load(f)
            # 호환성 체크: investors 키가 없으면 기본값 리턴
            if "investors" not in data:
                return default_state
            return data
    except:
        return default_state

def save_fund_state(investors_dict):
    """투자자별 현황 저장"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding='utf-8') as f:
        json.dump({"investors": investors_dict}, f, indent=2, ensure_ascii=False)

def get_nav_metrics(current_equity, history_df):
    """NAV, 변동률, 그리고 투자자별 평가액 계산"""
    state = load_fund_state()
    investors = state.get("investors", {})
    
    # 총 발행 좌수 = 모든 투자자 좌수의 합
    total_units = sum(investors.values())
    if total_units <= 0: total_units = 1.0
        
    current_nav = current_equity / total_units
    
    # NAV 변동률 (전일 대비)
    nav_change_pct = 0.0
    if not history_df.empty:
        last_equity = history_df["equity"].iloc[-1]
        # (주의) 과거의 Total Units를 정확히 알 수 없으므로, 
        # 간략히 자산(Equity) 변동률을 NAV 변동률로 근사하거나, 
        # 기록된 NAV가 있다면 그것을 써야 합니다. 여기선 자산 변동률 사용.
        if last_equity > 0:
            nav_change_pct = ((current_equity - last_equity) / last_equity) * 100.0
            
    return {
        "nav": current_nav,
        "total_units": total_units,
        "change_pct": nav_change_pct,
        "investors": investors  # 투자자별 좌수 정보 포함
    }
