class CfgDatabase:
    layer = {
        'silver': {
            'scheme': 'dw_slv',
            'table': 'crypto_transc_candle_upbit_minutes'
        },
        'gold': {
            'scheme': 'dw_gld',
            'table': 'crypto_transc_candle_upbit_minutes'
        }
    }
    
    
class CfgTransform:
    split_point='2024-12-31T23:59:59'
    time_field = 'candle_date_time_kst'
    feature_field = [
        'opening_price', 'trade_price', 'low_price', 'high_price',
        'candle_acc_trade_price', 'candle_acc_trade_volume',
        'diff_opening_price', 'diff_trade_price', 'diff_low_price', 'diff_high_price',
        'diff_candle_acc_trade_price', 'diff_candle_acc_trade_volume',
        'ratio_opening_price', 'ratio_trade_price', 'ratio_low_price', 'ratio_high_price',
        'ratio_candle_acc_trade_price', 'ratio_candle_acc_trade_volume'
    ]
    scaler = {
        'name': 'MinMaxScaler',
        'save_dir': '/app/static',
        'save_name': 'crypto_scaler'
    }