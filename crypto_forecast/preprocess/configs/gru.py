class CfgDatabase:
    layer = {
        'bronze': {
            'scheme': 'dw_brz',
            'table': 'crypto_transc_candle_upbit_minutes'
        },
        'silver': {
            'scheme': 'dw_slv',
            'table': 'crypto_transc_candle_upbit_minutes'
        }
    }
    
    
class CfgPreprocessor:
    time_field = 'candle_date_time_kst'
    feature_fields = [
        'opening_price', 'trade_price', 'low_price', 'high_price',
        'candle_acc_trade_price', 'candle_acc_trade_volume'
    ]