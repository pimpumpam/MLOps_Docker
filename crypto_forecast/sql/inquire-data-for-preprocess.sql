SELECT 
    market,
    candle_date_time_kst,
    opening_price,
    trade_price,
    low_price,
    high_price,
    candle_acc_trade_price,
    candle_acc_trade_volume
FROM upbit_candles_1min
;