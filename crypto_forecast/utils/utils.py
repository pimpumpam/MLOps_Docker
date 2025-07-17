from typing import Sequence, cast


def load_spec_from_base_config(cfg_name):

    meta_spec = __import__(
        f"configs.base.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgMeta

    load_spec = __import__(
        f"configs.base.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgLoad

    preprocess_spec = __import__(
        f"configs.base.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgPreprocess

    transform_spec = __import__(
        f"configs.base.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgTransform

    train_spec = __import__(
        f"configs.base.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgTrain

    hyperparameter_spec = __import__(
        f"configs.base.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgHyperparameter

    evaluate_spec = __import__(
        f"configs.base.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgEvaluate

    deploy_spec = __import__(
        f"configs.base.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgDeploy

    return meta_spec, load_spec, preprocess_spec, transform_spec, train_spec, hyperparameter_spec, evaluate_spec, deploy_spec


def read_sql_file(filepath):
    """
    SQL 폴더 내 쿼리 읽어오기

    Args:
        filepath (str): 읽어 올 쿼리 파일.

    Returns:
        query(str): 파일 내 쿼리문 전체.
        
    """
    
    with open(filepath, 'r', encoding="utf-8") as f:
        query = f.read()
        
    return query