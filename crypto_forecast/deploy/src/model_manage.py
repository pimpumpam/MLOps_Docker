import traceback
from datetime import datetime

import mlflow
from mlflow.tracking import MlflowClient


ALIAS = ["Archived", "Staging", "Production"]

def is_model_registered(model_name):
    """
    모델이 등록 되어 있는지 여부를 확인.

    Args:
        model_name(str): 조회 할 모델의 이름.

    Returns:
        (bool): 인자로 주어진 \'model_name\'과 동일한 모델이 존재하면 True, 아니면 False 반환.
        
    """
    
    model_info = tracking_registered_model(model_name)

    if model_info:
    
        if model_info['latest_versions']:
            return True
    
        else:
            return False
    
    return False
        

def register_model_by_run_id(run_id=None, **kwargs):
    """
    Run id를 활용해서 배포를 위한 모델을 등록.

    Args:
        run_id(str): 등록할 모델의 run id 정보
        kwargs:
            model_name(str): 등록할 모델명

    Return:
        (dict): 등록 된 모델의 속성 정보

    """
    
    assert run_id, f"Argument \"run_id\" is required"
    
    model_uri = f'runs:/{run_id}/model'
    
    if 'model_name' in kwargs:
        model_name = kwargs['model_name']
    else:
        model_name = mlflow.get_run(run_id).info.run_name    
    
    registered_model = mlflow.register_model(
        model_uri=model_uri,
        name=model_name
    )
    
    return dict(registered_model)


def set_model_stage(model_name, model_version, stage):
    
    assert stage in ALIAS, f"Argument \'stage\' must be one of {ALIAS}"
    
    try:
        client = MlflowClient()
                
        client.transition_model_version_stage(
            name=model_name,
            version=model_version,
            stage=stage,
            archive_existing_versions=True
        )
        print(f"🛠️ 모델의 상태를 성공적으로 변경했습니다.\n\t모델명 : \'{model_name}\' | 버전 : \'{model_version}\' | 상태 : \'{stage}\'")
    
    except Exception:
        err_msg = traceback.format_exc()
        print(err_msg)
        

def tracking_registered_model(model_name):
    try:
        client = MlflowClient()
        
        return dict(client.get_registered_model(name=model_name))
        
    except Exception:
        err_msg = traceback.format_exc()
        print(err_msg)
        

def tracking_latest_model(model_name):


    def timestamp_to_datetime(timestamp):
        """
        Args:
            timestamp (int, float): 초 단위의 timestamp. 밀리세컨드 단위는 /1000을 해서 초 단위로 맞춰줘야 함.

        Returns:
            (str): 연-월-일 시:분:초 형식의 시간 정보.
        """
    
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    
    model_info = tracking_registered_model(model_name)
    latest_version_info = dict(model_info['latest_versions'][-1])
    
    model_info_dict = {
        'name': model_info['name'],
        'version': latest_version_info['version'],
        'creation_time': timestamp_to_datetime(model_info['creation_timestamp']/1000),
        'latest_update_time': timestamp_to_datetime(latest_version_info['last_updated_timestamp']/1000),
        'run_id': latest_version_info['run_id'],
        'stage': latest_version_info['current_stage'],
        'source': latest_version_info['source']
    }
    
    return model_info_dict