class CfgMeta:
    name = "Crypto Transc MLOps Toy Project"
    asset_path = "./static/assets"
    schema_file = "crypto_transc_data.json"
    experiment_name = "CryptoForecast"
    artifact_path = "s3://mlflow"
    database_backend = "postgresql"


class CfgLoad:
    # scheme = 'dw_brz',
    # table = 'crypto_transc_candle_upbit_minutes'
    market = "KRW-BTC" 
    unit = "minutes"
    time_unit = 1
    tic = "2025-06-29T00:00:00"
    toc = "2025-06-30T23:59:59"
    max_per_attmp = 180


class CfgPreprocess:
    unit = "minute"

class CfgTransform:
    scaler = "MinMaxScaler"

class CfgTrain:
    pass


class CfgHyperparameter:
    num_epochs = [1]
    learning_rate = [0.05, 0.07]
    batch_size = [100]
    input_seq_len = [120]
    predict_seq_len = [60]


class CfgEvaluate:
    pass

class CfgDeploy:
    metric = "RMSE"
    model_name = "GRU"