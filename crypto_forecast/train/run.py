import os
import json
import argparse
import collections
import pandas as pd

import mlflow
from mlflow.models.signature import infer_signature

from src.database import create_db_engine
from src.preparation import split_sliding_window
from models.model import Model
from src.train import train
from utils.utils import load_spec_from_config, setup_experiment, hyperparameter_combination


# globals
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

RUN_IDs = collections.defaultdict(list)

class Trainer:
    
    def __init__(self, cfg_meta, cfg_database, cfg_model, cfg_hyperparameter, cfg_train):
        
        mlflow.set_tracking_uri(uri="http://mlflow-server:5000")
        
        self.cfg_meta = cfg_meta
        self.cfg_database = cfg_database
        self.cfg_model = cfg_model
        self.cfg_hyperparameter = cfg_hyperparameter
        self.cfg_train = cfg_train
        
        self.engine = create_db_engine(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        self.conn = self.engine.connect()
        self.cursor = self.engine.raw_connection().cursor()
        
    def run(self):
        print("🏃🏻Python 파일 실행")
                
        # 데이터 불러오기
        print("🧐 DB 내 데이터 조회")
        query = f"""
                SELECT *
                FROM {self.cfg_database.layer['gold']['scheme']}_{self.cfg_database.layer['gold']['table']}
                ;
                """
        train_dataset = pd.read_sql(query, con=self.engine)
        
        # MLFlow 실험 설정
        print("🧪 MLFlow 실험 설정")
        setup_experiment(
            self.cfg_meta.experiment_name,
            artifact_location=self.cfg_meta.artifacts_dir
        )
        
        # 하이퍼파라미터 설정
        print("🤹🏻‍♂️ 하이퍼파라미터 조합")
        hyp_list = hyperparameter_combination(self.cfg_hyperparameter)

        # 모델 학습
        print(f"🧑🏻‍🏫 {self.cfg_model.name} 모델 학습")
        with mlflow.start_run(run_name=self.cfg_model.name) as run: # parent_run
            
            if len(hyp_list)>1:
                print("🕵🏻‍♂️ 하이퍼파라미터 최적화 수행")
                
                for idx, hyp in enumerate(hyp_list):
                    with mlflow.start_run(run_name=f"{self.cfg_model.name}_{str(idx+1)}", nested=True) as nested_run:
                        print(f"🤖 {idx+1}/{len(hyp_list)} 모델 학습 중 ...")
                        model = Model(self.cfg_model)
                        
                        X, y = split_sliding_window(
                            data=train_dataset,
                            feature_col=self.cfg_train.feature_field,
                            input_seq_len=hyp['input_seq_len'],
                            label_seq_len=hyp['predict_seq_len'],
                            time_col=self.cfg_train.time_field
                        )
                    
                        train(
                            dataset=(X, y),
                            model=model,
                            batch_size=hyp['batch_size'],
                            num_epochs=hyp['num_epoch'],
                            learning_rate=hyp['learning_rate'],
                            device='cpu'
                        )
                        
                        print("📝 메타정보 및 아티팩트 기록")
                        mlflow.log_params(hyp)
                        mlflow.pytorch.log_model(
                            pytorch_model=model,
                            artifact_path='model',
                            code_paths=['models'],
                            signature=infer_signature(X[0], y[0])
                        )
                        
                        RUN_IDs['run_id'].append(nested_run.info.run_id)
                        
            else:
                hyp = hyp_list.pop()
                model = Model(self.cfg_model)
                
                X, y = split_sliding_window(
                    data=train_dataset,
                    feature_col=self.cfg_train.feature_field,
                    input_seq_len=hyp['input_seq_len'],
                    label_seq_len=hyp['predict_seq_len'],
                    time_col=self.cfg_train.time_field
                )
                
                # train(
                #     dataset=(X, y),
                #     model=model,
                #     batch_size=hyp['batch_size'],
                #     num_epochs=hyp['num_epoch'],
                #     learning_rate=hyp['learning_rate'],
                #     device='cpu'
                # )
                
                print("📝 메타정보 및 아티팩트 기록")
                mlflow.log_params(hyp)
                mlflow.pytorch.log_model(
                    pytorch_model=model,
                    artifact_path='model',
                    code_paths=['models'],
                    signature=infer_signature(X[0], y[0])
                )
                
                RUN_IDs['run_id'].append(run.info.run_id)
        
        with open(os.path.join(self.cfg_meta.static_dir, 'run_ids.json'), 'w') as f:
            json.dump(RUN_IDs, f)
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser() 
    parser.add_argument('--config', type=str, default='gru', help="Config 파이썬 파일 명. 확장자는 제외.")
    args = parser.parse_args()

    (
        cfg_meta,
        cfg_database,
        cfg_model,
        cfg_hyp,
        cfg_train
    ) = load_spec_from_config(args.config)
    
    print(f"🐳 컨테이너 실행")
    trainer = Trainer(cfg_meta, cfg_database, cfg_model, cfg_hyp, cfg_train)
    trainer.run()
    print(f"🐳 컨테이너 종료")