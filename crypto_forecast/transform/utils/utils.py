from typing import Sequence, cast


def load_spec_from_config(cfg_name):
     
    database_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgDatabase
    
    transformer_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgTransform
    
    return database_spec, transformer_spec