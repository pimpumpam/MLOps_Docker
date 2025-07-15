from typing import Sequence, cast


TIME_UNIT_DICT = {
    'minute' : 'T',
    'hour' : 'H',
    'day' : 'D',
    'week': 'W',
    'month': 'M'
}

def load_spec_from_config(cfg_name):
    
    database_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgDatabase
    
    preprocessor_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgPreprocessor
    
    return database_spec, preprocessor_spec