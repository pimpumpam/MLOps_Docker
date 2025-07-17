import os
import argparse
import pandas as pd
from datetime import datetime

from src.transformation import MultiColumnScaler, split_train_test

from structure.schema import SchemaManager
from load.src.db_manager import DatabaseManager
from utils.utils import read_sql_file, load_spec_from_base_config


# globals
ROOT = Path(__file__).resolve().parent
TASK = "transform"

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


class Transformer:
    
    def __init__(self, cfg_meta, cfg_transform):
        
        self.cfg_meta = cfg_meta
        self.cfg_transform = cfg_transform
        self.schema_manager = SchemaManager(f"./configs/schema/{cfg_meta.schema_file}")
                
    def run(self):
        
        TIME_COL = "candle_date_time_kst"
        FEATURE_COLS = self.schema_manager.get_columns_by_filter(
            is_feature=True,
            usage="feature",
            task=TASK
        )
        
        print(FEATURE_COLS)
        
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
        candle_data = db_manager.inquire_data_from_table(
            query=read_sql_file(f"{self.cfg_meta.sql_path}/inquire-data-for-transform.sql")
        )
        
        
        # scaler 적용
        print("⚖️ 컬럼 별 scaler 적용")
        scaler = MultiColumnScaler(self.cfg_transform.scaler)
        scaler.fit_transform(
            data=candle_data,
            columns=FEATURE_COLS,
            inplace=True,
            save_pkl=True,
            save_path=self.cfg_meta.artifact_path,
            save_name=f"{self.cfg_transform.scaler.lower()}_{datetime.now().strftime("%Y%m%d%H%M%S")}"
        )
        
        
        # 데이터 분리
        print("🪓 학습/검증 데이터 셋으로 분리")
        train_dataset, test_dataset = split_train_test(
            data=candle_data,
            train_ratio=0.7,
            test_ratio=None,
            time_col=TIME_COL
        )
        
        
        # 데이터 적재
        print("📦 학습 데이터 셋 DB 적재")
        db_manager.insert_data_to_table(
            table=self.schema_manager.schema["schema"]["table"]+"_train",
            data=train_dataset,
            mode="replace"
        )
        

        
        print("📦 검증 데이터 셋 DB 적재")
        db_manager.insert_data_to_table(
            table=self.schema_manager.schema["schema"]["table"]+"_test",
            data=test_dataset,
            mode="replace"
        )
        
        
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
    transformer = Transformer(meta_spec, transform_spec)
    transformer.run()
    print(f"🐳 컨테이너 종료")