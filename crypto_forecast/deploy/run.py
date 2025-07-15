import os
import mlflow
import argparse

from src.model_manage import register_model_by_run_id, set_model_stage, tracking_registered_model, tracking_latest_model, is_model_registered
from src.experiment_manage import is_nested, tracking_experiment, tracking_run, tracking_latest_run, tracking_best_run, tracking_best_child_run
from utils.utils import load_spec_from_config


mlflow.set_tracking_uri(uri="http://mlflow-server:5000")

class Deploy:

    def __init__(self, cfg_meta, cfg_deploy):

        self.cfg_meta = cfg_meta
        self.cfg_deploy = cfg_deploy

    def run(self):
    
        # 실험 정보 조회
        experiment_info = tracking_experiment(experiment_name=self.cfg_meta.experiment_name)

        # 실험 내 best run 조회
        best_run = tracking_best_run(
            experiment_id = experiment_info['experiment_id'],
            metric = self.cfg_deploy.metric,
            filter_string = None
        ).pop()
        

        if is_nested(best_run['run_id']):
            best_run = tracking_best_child_run(
                parent_run_id=best_run['run_id']
            ).pop()

        print(f"📢 최고 성능 모델의 Run ID : {best_run['run_id']}")


        # 레지스트리 모델 등록

        # 레지스트리 내 모델 존재
        if is_model_registered(self.cfg_deploy.model_name):

            print(f"📢 \'{self.cfg_deploy.model_name}\' 모델이 레지스트리에 존재합니다.")

            # 레지스트리에 존재하는 모델 정보 조회
            current_model = tracking_latest_model(self.cfg_deploy.model_name)

            current_model_info = tracking_run(
                experiment_id = experiment_info['experiment_id'],
                run_id = current_model['run_id']
            ).pop()

            # 새로운 모델 정보 조회
            new_model_info = tracking_run(
                experiment_id=experiment_info['experiment_id'],
                run_id = best_run['run_id']
            ).pop()

            # 새로운 모델의 성능이 더 좋은 경우 모델 교체
            if new_model_info[f'metrics.{self.cfg_deploy.metric}'] < current_model_info[f'metrics.{self.cfg_deploy.metric}']:
                print(f"📢 레지스트리에 등록 되어 있는 모델보다 좋은 성능을 갖는 모델이 존재합니다.\n🔄 기존 모델을 새로운 모델로 교체합니다.")

                # 레지스트리 내 새 모델 등록
                registered_model = register_model_by_run_id(
                    run_id = best_run['run_id'],
                    model_name = self.cfg_deploy.model_name
                )

                # 새 모델 Stage 설정
                set_model_stage(
                    model_name = registered_model['name'],
                    model_version = registered_model['version'],
                    stage = 'Production'
                )

            else:
                print(f"📢 레지스트리에 등록 되어 있는 모델의 성능이 양호합니다.\n🆗 기존 모델을 유지합니다.")
                

        # 레지스트리 내 모델 없음
        else:
            print(f"📢 레지스트리 내 \'{self.cfg_deploy.model_name}\' 모델이 존재하지 않습니다.\n🆕 \'{self.cfg_deploy.model_name}\' 이름으로 모델을 등록합니다.")

            registered_model = register_model_by_run_id(
                run_id = best_run['run_id'],
                model_name = self.cfg_deploy.model_name
            )

            set_model_stage(
                model_name = registered_model['name'],
                model_version = registered_model['version'],
                stage = 'Production'
            )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="gru", help="Config Python 파일 명. 확장자 제외.")
    args = parser.parse_args()

    (
        cfg_meta,
        cfg_deploy
    ) = load_spec_from_config(args.config)
    

    print(f"🐳 컨테이너 실행")
    runner = Deploy(cfg_meta, cfg_deploy)
    runner.run()
    print(f"🐳 컨테이너 종료")