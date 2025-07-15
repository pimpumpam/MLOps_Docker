import os
import sys
import json
import pickle
import argparse
import numpy as np
import pandas as pd

import mlflow
import mlflow.artifacts

from src.database import create_db_engine
from src.preparation import split_sliding_window
from src.transformation import MultiColumnScaler
from src.evaluate import evaluate
from utils.utils import load_spec_from_config
from utils.metrics import root_mean_square_error, mean_absolute_error, mean_absolute_percentage_error

# globals
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


class Evaluator:
    
    def __init__(self, cfg_meta, cfg_database, cfg_transform, cfg_model, cfg_evaluate):
        
        mlflow.set_tracking_uri(uri="http://mlflow-server:5000")
        
        self.cfg_meta = cfg_meta
        self.cfg_database = cfg_database
        self.cfg_transform = cfg_transform
        self.cfg_model = cfg_model
        self.cfg_evaluate = cfg_evaluate
        
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
        
        # Run ID 정보 불러오기
        print("🪪 Run ID 정보 조회")
        with open(os.path.join(self.cfg_meta.static_dir, 'run_ids.json'), 'r') as f:
            RUN_IDs = json.load(f)
        RUN_IDs = RUN_IDs['run_id']
        
        # Scaler 불러오기
        print("📐 Scaler 정보 조회")
        with open(os.path.join(self.cfg_meta.static_dir, f"{self.cfg_transform.scaler['name']}_{self.cfg_transform.scaler['save_name']}.pkl"), 'rb') as r:
            scaler_dict = pickle.load(r)
        
        scaler = MultiColumnScaler(self.cfg_transform.scaler['name'])
        scaler.scaler_dict = scaler_dict
        
        # 데이터 불러오기
        print("🧐 DB 내 데이터 조회")
        query = f"""
                SELECT *
                FROM {self.cfg_database.layer['gold']['scheme']}_{self.cfg_database.layer['gold']['table']}
                ;
                """
        test_dataset = pd.read_sql(query, con=self.engine)

        for run_id in RUN_IDs:    
            with mlflow.start_run(run_id=run_id) as run:
                print(f"🤔 {run.info.run_name} 모델(Run ID: {run_id}) 평가 시작")
                
                MODEL_URI = f"runs:/{run_id}/model"
                MODEL_DIR = mlflow.artifacts.download_artifacts(MODEL_URI)
                CODE_DIR = os.path.join(MODEL_DIR, "code")
                sys.path.append(CODE_DIR)
                from models.model import Model
                
                hyp = mlflow.get_run(run_id=run_id).data.params
                model = mlflow.pytorch.load_model(MODEL_URI)
                
                X, y = split_sliding_window(
                    data=test_dataset,
                    feature_col=self.cfg_evaluate.feature_field,
                    input_seq_len=int(hyp['input_seq_len']),
                    label_seq_len=int(hyp['predict_seq_len']),
                    time_col=self.cfg_evaluate.time_field
                )
                
                pred, truth = evaluate(
                    dataset=(X, y),
                    model=model,
                    batch_size=int(hyp['batch_size']),
                    device='cpu'
                )
                
                print("🔄 Scale 역변환 수행")
                pred = np.array(pred).reshape(-1, len(self.cfg_evaluate.label_field))
                truth = np.array(truth).reshape(-1, len(self.cfg_evaluate.label_field))
                
                pred = pd.DataFrame(pred, columns=self.cfg_evaluate.label_field)
                truth = pd.DataFrame(truth, columns=self.cfg_evaluate.label_field)
                
                scaler.inverse_transform(
                    data=pred,
                    columns=self.cfg_evaluate.label_field,
                    inplace=True
                )
                
                scaler.inverse_transform(
                    data=truth,
                    columns=self.cfg_evaluate.label_field,
                    inplace=True
                )
                
                print("📝 평가지표 기록")
                mlflow.log_metrics({
                    'RMSE': root_mean_square_error(pred, truth),
                    'MAE': mean_absolute_error(pred, truth),
                    'MAPE': mean_absolute_percentage_error(pred, truth) 
                })


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser() 
    parser.add_argument('--config', type=str, default='gru', help="Config 파이썬 파일 명. 확장자는 제외.")
    args = parser.parse_args()
    
    (
        meta_spec,
        database_spec,
        transform_spec,
        model_spec,
        evaluate_spec
    ) = load_spec_from_config(args.config)
    
    print(f"🐳 컨테이너 실행")
    evaluator = Evaluator(meta_spec, database_spec, transform_spec, model_spec, evaluate_spec)
    evaluator.run()
    print(f"🐳 컨테이너 종료")