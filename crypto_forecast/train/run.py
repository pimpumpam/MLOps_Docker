import os
import json
import argparse
import collections
from pathlib import Path

import mlflow
from mlflow.models.signature import infer_signature

from src.train import train
from src.preparation import split_sliding_window
from models.model import Model

from structure.schema import SchemaManager
from load.src.db_manager import DatabaseManager
from utils.utils import read_sql_file, load_spec_from_base_config, load_spec_from_model_config, setup_experiment, hyperparameter_combination


# globals
TASK = "train"
ROOT = Path(__file__).resolve().parent
RUN_IDs = collections.defaultdict(list)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")



class Trainer:
    
    def __init__(self, cfg_meta, cfg_model, cfg_hyperparameter, cfg_train):
        
        mlflow.set_tracking_uri(uri="http://mlflow-server:5000")
        
        self.cfg_meta = cfg_meta
        self.cfg_model = cfg_model
        self.cfg_hyperparameter = cfg_hyperparameter
        self.cfg_train = cfg_train
        self.schema_manager = SchemaManager(f"./configs.schema/{cfg_meta.schema_file}")
        
        
    def run(self):
        
        TIME_COL = "candle_date_time_kst"
        FEATURE_COLS = self.schema_manager.get_columns_by_filter(
            is_feature=True,
            usage="feature",
            task=TASK
        )
        
        print(FEATURE_COLS)
                
        # 데이터 불러오기
        print("🧐 DB 내 데이터 조회")
        # DB 엔진
        db_manager = DatabaseManager(
            backend=self.cfg_meta.database_backend,
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            passwd=DB_PASSWORD,
            database=DB_NAME
        )
        
        # 데이터 불러오기
        train_dataset = db_manager.inquire_data_from_table(
            query=read_sql_file(f"{self.cfg_meta.sql_path}/inquire-data-for-train.sql")
        )
        
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
                            feature_col=FEATURE_COLS,
                            input_seq_len=hyp['input_seq_len'],
                            label_seq_len=hyp['predict_seq_len'],
                            time_col=TIME_COL
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
                    feature_col=FEATURE_COLS,
                    input_seq_len=hyp['input_seq_len'],
                    label_seq_len=hyp['predict_seq_len'],
                    time_col=TIME_COL
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
        
        with open(os.path.join(self.cfg_meta.asset_path, 'run_ids.json'), 'w') as f:
            json.dump(RUN_IDs, f)
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="base_config", help="Config Python 파일 명. 확장자 제외.")
    args = parser.parse_args() 
    
    (
        meta_spec, 
        load_spec, 
        preprocess_spec, 
        transform_spec, 
        train_spec, 
        hyperparameter_spec, 
        evaluate_spec, 
        deploy_spec
    ) = load_spec_from_base_config(args.config)
    
    print(f"🐳 컨테이너 실행")
    trainer = Trainer(meta_spec, cfg_model, hyperparameter_spec, train_spec)
    trainer.run()
    print(f"🐳 컨테이너 종료")