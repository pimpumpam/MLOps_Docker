import mlflow
from itertools import product
from typing import Sequence, cast


PROGRESS_BAR_FORMAT = '{l_bar}{bar:10}{r_bar}'


def load_spec_from_config(cfg_name):
    
    meta_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgMeta
    
    database_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgDatabase
    
    model_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgModel
    
    hyperparameter_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgHyperparameter
    
    train_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgTrain
    
    return meta_spec, database_spec, model_spec, hyperparameter_spec, train_spec


def setup_experiment(experiment_name, artifact_location):
    
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
    attributes = {attr: getattr(cfg_hyp, attr) for attr in dir(cfg_hyp) if not attr.startswith("__") and not callable(getattr(cfg_hyp, attr))}
    hyps, vals = attributes.keys(), attributes.values()
    combinations = [dict(zip(hyps, comb)) for comb in product(*vals)]
    
    return combinations