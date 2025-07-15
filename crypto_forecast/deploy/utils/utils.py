from typing import Sequence, cast

def load_spec_from_config(cfg_name):
    
    meta_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgMeta
    
    # database_spec = __import__(
    #     f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    # ).CfgDatabase
    
    deploy_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgDeploy
    
    return meta_spec, deploy_spec
