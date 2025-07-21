import importlib
from itertools import product
from typing import Sequence, cast

PROGRESS_BAR_FORMAT = '{l_bar}{bar:10}{r_bar}'

def load_spec_from_base_config(cfg_name):

    try:
        base_module = importlib.import_module("configs.base.base_config")
        model_module = importlib.import_module(f"configs.model.{cfg_name}")

        model_cfg = getattr(model_module, "CfgModel")
        setattr(base_module, "CfgModel", model_cfg)

    except ModuleNotFoundError as e:
        raise(e)

    meta_spec = __import__(
        f"configs.base.base_config", fromlist=cast(Sequence[str], [None])
    ).CfgMeta

    load_spec = __import__(
        f"configs.base.base_config", fromlist=cast(Sequence[str], [None])
    ).CfgLoad

    preprocess_spec = __import__(
        f"configs.base.base_config", fromlist=cast(Sequence[str], [None])
    ).CfgPreprocess

    transform_spec = __import__(
        f"configs.base.base_config", fromlist=cast(Sequence[str], [None])
    ).CfgTransform

    model_spec = __import__(
        f"configs.base.base_config", fromlist=cast(Sequence[str], [None])
    ).CfgModel

    hyperparameter_spec = __import__(
        f"configs.base.base_config", fromlist=cast(Sequence[str], [None])
    ).CfgHyperparameter
    
    train_spec = __import__(
        f"configs.base.base_config", fromlist=cast(Sequence[str], [None])
    ).CfgTrain

    evaluate_spec = __import__(
        f"configs.base.base_config", fromlist=cast(Sequence[str], [None])
    ).CfgEvaluate

    deploy_spec = __import__(
        f"configs.base.base_config", fromlist=cast(Sequence[str], [None])
    ).CfgDeploy

    return meta_spec, load_spec, preprocess_spec, transform_spec, model_spec, hyperparameter_spec, train_spec, evaluate_spec, deploy_spec



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


def setup_experiment(experiment_name, artifact_location):
    """
    MLFlow 기반 Experiment 설정. 존재하지 않는 경우 새로운 Experiment 생성. 존재하는 경우 해당 Experiment 내 기록.

    Args:
        experiment_name (str): Experiment 명
        artifact_location (str): Artiface 저장 경로
    """

    import mlflow
    
    try:
        mlflow.create_experiment(
            experiment_name, 
            artifact_location=artifact_location
        )
        print(
            f"🧪 Experiment {experiment_name} is not Exist. \
            Create Experiment."
        )
    except:
        print(
            f"🧪 Experienmt {experiment_name} is Already Exist. \
            Execute Run on the \"{experiment_name}\"."
        )
            
    # set experiment
    mlflow.set_experiment(experiment_name)
    

def hyperparameter_combination(cfg_hyp):
    """
    하이퍼파라미터의 모든 조합 산출

    Args:
        cfg_hyp (class): Config 파일에 정의 된 하이퍼파라미터 정보

    Returns:
        combinations (list): {하이퍼파라미터 명: 하이퍼파라미터 값, ... } 형태의 딕셔너리들로 구성 된 리스트
    """
    attributes = {attr: getattr(cfg_hyp, attr) for attr in dir(cfg_hyp) if not attr.startswith("__") and not callable(getattr(cfg_hyp, attr))}
    hyps, vals = attributes.keys(), attributes.values()
    combinations = [dict(zip(hyps, comb)) for comb in product(*vals)]
    
    return combinations