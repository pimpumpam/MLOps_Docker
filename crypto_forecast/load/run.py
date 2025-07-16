import os
import time
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

from src.db_manager import DatabaseManager
from src.data_handler import inquire_candle_api, insert_data_to_database, get_recent_timestamp_from_table

from structure.schema import SchemaManager
from utils.utils import load_spec_from_base_config


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
        self.schema = SchemaManager(f"./configs/schema/{cfg_meta.schema_file}").schema
   
                
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
        is_table = db_manager.check_table_exists(table=self.schema["schema"]["table"])

        if is_table:
            latest_time = get_recent_timestamp_from_table(
                table=self.schema["schema"]["table"],
                engine=db_manager.engine
            )

            mode = 'append' # 데이터를 테이블로 적재시 활용
            tic = datetime.strptime(latest_time, "%Y-%m-%dT%H:%M:%S") + timedelta(minutes=1)
            toc = tic + timedelta(days=1)

        else:
            mode = 'fail' # 데이터를 테이블로 적재시 활용
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
        insert_data_to_database(
            table = self.schema["schema"]["table"],
            data = data,
            engine = db_manager.engine,
            mode = mode
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
    
    loader = Loader(meta_spec, load_spec)
    loader.run()