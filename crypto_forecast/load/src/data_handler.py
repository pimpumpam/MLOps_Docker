import datetime
import requests
from sqlalchemy import text


def inquire_candle_api(market, tgt_date, unit, time_unit=1, max_per_attmp=180, **kwargs):

    # 시간 아규먼트 타입 검증
    if not isinstance(tgt_date, str):
        tgt_date = datetime.datetime.strftime(tgt_date, "%Y-%m-%dT%H:%M:%S")

    # API Request 파라미터
    URL = f"https://api.upbit.com/v1/candles/{unit}/{time_unit}"
    PARAMS = {
        "market" : market,
        "to" : tgt_date,
        "count" : max_per_attmp
    }
    
    # Request 파라미터 추가
    if 'params' in kwargs:
        for k, v in kwargs['params'].items():
            if v:
                PARAMS[k] = v

    # API 요청
    try:
        response = requests.get(URL, params=PARAMS)
        response.raise_for_status()
        
        print(f"✅ UpBit 데이터 요청 성공 | ~ {tgt_date}")
        
        return response.json()

    except requests.exceptions.RequestException as e:  
        print(f"🚨 UpBit 데이터 요청 실패 | 에러: {e}")
        
        return None