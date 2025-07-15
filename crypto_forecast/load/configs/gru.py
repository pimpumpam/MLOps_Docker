class CfgDatabase:
    layer = {
        'bronze': {
            'scheme': 'dw_brz',
            'table': 'crypto_transc_candle_upbit_minutes'
        }
    }

class CfgLoader:
    platform = "upbit"
    market = "KRW-BTC"
    unit = "minutes"
    time_unit = 1
    tic = "2024-11-01T00:00:00"
    toc = "2024-11-10T23:59:00"
    max_per_attmp = 180 # 한번에 가져 올 데이터 개수 (최대 200)