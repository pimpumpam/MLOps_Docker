import os
import time
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

from src.db_manager import DatabaseManager
from src.data_handler import inquire_candle_api

from structure.schema import SchemaManager
from utils.utils import read_sql_file, load_spec_from_base_config


# globals
ROOT = Path(__file__).resolve().parent
TASK = 'load'

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


class Loader:
    def __init__(self, cfg_meta, cfg_loader):
        
        self.cfg_meta = cfg_meta
        self.cfg_loader = cfg_loader
        self.schema_manager = SchemaManager(f"./configs/schema/{cfg_meta.schema_file}")
   
                
    def run(self):
        
        db_manager = DatabaseManager(
            backend=self.cfg_meta.database_backend,
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            passwd=DB_PASSWORD,
            database=DB_NAME
        )

        # 테이블 존재 여부 확인
        is_table = db_manager.check_table_exists(table=self.schema_manager.schema["schema"]["table"])

        if is_table:
            latest_time = db_manager.execute_query(
                query = read_sql_file(f"{self.cfg_meta.sql_path}/inquire-recent-timestamp.sql")
            ).scalar()

            tic = datetime.strptime(latest_time, "%Y-%m-%dT%H:%M:%S") + timedelta(minutes=1)
            toc = tic + timedelta(days=1)

        else:
            tic = datetime.strptime(self.cfg_loader.tic, "%Y-%m-%dT%H:%M:%S")
            toc = datetime.strptime(self.cfg_loader.toc, "%Y-%m-%dT%H:%M:%S")


        # API 요청
        data = []
        while True:
            if tic > toc:
                break
                
            datum = inquire_candle_api(
                market=self.cfg_loader.market,
                tgt_date=toc,
                unit=self.cfg_loader.unit,
                time_unit=self.cfg_loader.time_unit,
                max_per_attmp=self.cfg_loader.max_per_attmp
            )  
            data.extend(datum)
            
            toc = datetime.strptime(
                datum[-1]['candle_date_time_utc'],
                "%Y-%m-%dT%H:%M:%S"
            )
            toc -= timedelta(seconds=1)

            time.sleep(0.1)
        
        data = pd.DataFrame(data).drop_duplicates()
        

        # 테이블 적재
        db_manager.insert_data_to_table(
            table = self.schema_manager.schema["schema"]["table"],
            data = data,
            mode = "append" if is_table else "fail"
        )

        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="gru", help="Config Python 파일 명. 확장자 제외.")
    args = parser.parse_args() 
    
    (
        meta_spec, 
        load_spec, 
        preprocess_spec, 
        transform_spec,
        model_spec, 
        hyperparameter_spec, 
        train_spec, 
        evaluate_spec, 
        deploy_spec
    ) = load_spec_from_base_config(args.config)
    
    loader = Loader(meta_spec, load_spec)
    loader.run()