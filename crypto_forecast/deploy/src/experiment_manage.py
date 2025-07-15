import mlflow

def is_nested(run_id):
    """
    특정 run이 child run을 갖는지 확인.

    parameter
    ----------
    run_id(str): parent run의 id 값.

    return
    ----------
    (bool): Child run을 갖는다면 True, 그렇지 않으면 False 리턴.

    """

    run_info  = mlflow.get_run(run_id)
    experiment_id = run_info.info.experiment_id

    child_runs = mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string=f"tags.mlflow.parentRunId='{run_id}'"
    )

    return True if len(child_runs)>0 else False


def tracking_experiment(experiment_id=None, experiment_name=None):
    """
    Experiment 탐색 및 속성 정보 조회

    parameter
    ----------
    experiment_id(str): 조회 대상이 되는 experiment id 정보.
    experiment_name(str): 조회 대상이 되는 experiment name 정보.

    return
    ----------
    (dict): Experiment에 대한 속성 정보.
    
    """
    
    assert experiment_id or experiment_name, f"At least one argument \"experiment_id\" or \"experiment_name\" is required"

    if experiment_id:
        if not isinstance(experiment_id, str):
            experiment_id = str(experiment_id)
            
        return dict(mlflow.get_experiment(experiment_id))
        
    elif experiment_name:
            
        return dict(mlflow.get_experiment_by_name(experiment_name))
    

def tracking_run(experiment_id, run_id=None, run_name=None):
    """
    Run 탐색 및 속성 정보 조회

    parameter
    ----------
    experiment_id(str): 조회 대상이 되는 run이 속한 experiment의 id 정보.
    run_id(str): 조회 대상이 되는 run id 정보.
    run_name(str): 조회 대상이 되는 run name 정보.

    return
    ----------
    (dict): Run에 대한 속성 정보.
    
    """
    assert run_id or run_name, f"At least one argument \"run_id\" or \"run_name\" is required"
    
    if run_id:
        if not isinstance(run_id, str):
            run_id = str(run_id)
        
        return mlflow.search_runs(
            experiment_ids=[experiment_id],
            filter_string=f"run_id='{run_id}'"
        ).to_dict('records')
        
    elif run_name:
        return mlflow.search_runs(
            experiment_ids=[experiment_id],
            filter_string=f"tags.mlflow.runName='{run_name}'"
        ).to_dict('records')
    

def tracking_latest_run(experiment_id=None, run_id=None):
    """
    가장 최근에 실행 한 run 탐색 및 속성 정보 조회.

    parameter
    ----------
    experiment_id(str): 조회 대상이 되는 run이 속한 experiment의 id 정보.
    run_id(str): 조회 대상이 되는 run id 정보.

    return
    ----------
    (dict): 가장 최근에 실행한 run에 대한 속성 정보.

    """      
    
    assert experiment_id or run_id, f"At least one argument \"experiment_id\" or \"run_id\" is required"
    
    if not experiment_id:
        run_info = mlflow.get_run(run_id)
        experiment_id = run_info.info.experiment_id
    
    all_runs = mlflow.search_runs(
        experiment_ids = [experiment_id],
        order_by=['attributes.created DESC']
    )
        
    try:
        return all_runs[all_runs['tags.mlflow.parentRunId'].isna()].iloc[0].to_dict()
    except:
        return all_runs.iloc[0].to_dict()
    
    
def tracking_best_run(experiment_id=None, run_id=None, metric='RMSE', filter_string=None):
    """
    특정 평가지표 기준 성능이 가장 좋은 run 탐색 및 속성 정보 조회.

    parameter
    ----------
    experiment_id(str): 조회 대상이 되는 run이 속한 experiment id 정보.
    run_id(str): 조회 대상이 되는 run id 정보.   
    metric(str): 성능 평가의 기준이 될 평가지표. MLFlow 대시보드에서 조회 가능한 지표여야 함.

    return
    ----------
    (dict): 가장 성능이 좋은 run에 대한 속성 정보

    """
    
    assert experiment_id or run_id, f"At least one argument \"experiment_id\" or \"run_id\" is required"
    
    if not experiment_id:
        run_info = mlflow.get_run(run_id)
        experiment_id = run_info.info.experiment_id
        
    best_run = mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string=filter_string,
        order_by=[f"metrics.{metric} ASC"],
        max_results=1
    )

    return best_run.to_dict('records')


def tracking_best_child_run(parent_run_id, experiment_id=None, criteria='RMSE', filter_string=None):
    """
    Child run 중에서 특정 평가지표 기준 성능이 가장 좋은 run 탐색 및 속성 정보 조회.
    
    Args:
        experiment_id(str): 조회 대상이 되는 run이 속한 experiment id 정보.
        parent_run_id(str): 조회 대상이 되는 run id 정보.
        metric(str): 성능 평가의 기준이 될 평가지표. MLFlow 대시보드에서 조회 가능한 지표여야 함.

    Returns:
        (dict): 가장 성능이 좋은 run에 대한 속성 정보
    
    """
    
    assert parent_run_id, f"Argument \"parent_run_id\" is required"
    
    if not experiment_id:
        run_info = mlflow.get_run(parent_run_id)
        experiment_id = run_info.info.experiment_id
    
    
    base_filter_string = f"tags.mlflow.parentRunId='{parent_run_id}'"
    if filter_string is not None:
        filter_string = f"{base_filter_string} AND {filter_string}"
    else:
        filter_string = base_filter_string
        

    nested_runs = mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string=filter_string,
        order_by=[f'metrics.{criteria} ASC'],
        max_results=1
    )
    
    return nested_runs.to_dict('records')