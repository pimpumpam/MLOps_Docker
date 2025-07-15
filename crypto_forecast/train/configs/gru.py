class CfgMeta:
    static_dir = '/app/static'
    artifacts_dir = 's3://mlflow'
    experiment_name = 'CryptoForecast'

    
class CfgDatabase:
    layer = {
        'gold': {
            'scheme': 'dw_gld',
            'table': 'crypto_transc_candle_upbit_minutes_train'
        }
    }


class CfgModel:
    name = 'GRU'
    input_feature_dims = 18
    output_feature_dims = 4
    gru_layer = {
        'input_dim':18,
        'hidden_dim': 50,
        'num_layers': 2,
        'bias': True,
        'batch_first': True,
        'architecture': [
            ['nn.GRU', [18, 50, 2, True, True]]
        ]
    }
    linear_layer = {
        'input_dim': 6000, # GRU Hidden x Number of Sequence, hidden
        'output_dim': 240, # hidden, Prediction Sequence x Number of Output Feature
        'architecture': [
            ['nn.Linear', [6000, 1000]],
            ['nn.ReLU', [False]],
            ['nn.Linear', [1000, 240]]
        ]
    }
    
    
class CfgHyperparameter:
    num_epoch = [1]
    learning_rate = [0.05, 0.07]
    batch_size = [100]
    input_seq_len = [120]
    predict_seq_len = [60]
    
    
class CfgTrain:
    time_field = 'candle_date_time_kst'
    feature_field = [
        'opening_price', 'trade_price', 'low_price', 'high_price',
        'candle_acc_trade_price', 'candle_acc_trade_volume',
        'diff_opening_price', 'diff_trade_price', 'diff_low_price', 'diff_high_price',
        'diff_candle_acc_trade_price', 'diff_candle_acc_trade_volume',
        'ratio_opening_price', 'ratio_trade_price', 'ratio_low_price', 'ratio_high_price',
        'ratio_candle_acc_trade_price', 'ratio_candle_acc_trade_volume'
    ]
    label_field = ['opening_price', 'trade_price', 'low_price', 'high_price']