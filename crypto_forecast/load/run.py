import os
import time
import argparse
import pandas as pd
from datetime import datetime, timedelta

from src.loader import inquire_candle_data
from src.database import create_db_engine, fetch_one
from src.query import is_exists, get_recent_timestamp, dataframe_to_tale
from utils.utils import load_spec_from_config


# globals
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


class Loader:
    def __init__(self, cfg_database, cfg_loader):
        
        self.cfg_loader = cfg_loader
        self.cfg_database = cfg_database
        
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
        
        exists = fetch_one(
            cursor=self.cursor,
            query=is_exists(
                database_name=DB_NAME, 
                table_name=f"{self.cfg_database.layer['bronze']['scheme']}_{self.cfg_database.layer['bronze']['table']}"
            )
        )
        
        if bool(exists[0]):
            latest_time = fetch_one(
                cursor=self.cursor,
                query=get_recent_timestamp(table_name=f"{self.cfg_database.layer['bronze']['scheme']}_{self.cfg_database.layer['bronze']['table']}")
            )[0]
            
            tic = datetime.strptime(latest_time, "%Y-%m-%dT%H:%M:%S") + timedelta(minutes=1)
            toc = tic + timedelta(days=1)
            
            print("📢 DB 내 테이블 존재")
            print(f"⏱️ 데이터 요청 시간 범위: {tic} ~ {toc}")
            
        else:
            tic = datetime.strptime(self.cfg_loader.tic, "%Y-%m-%dT%H:%M:%S")
            toc = datetime.strptime(self.cfg_loader.toc, "%Y-%m-%dT%H:%M:%S")
            
            print("📢 DB 내 테이블 없음")
            print(f"⏱️ 데이터 요청 시간 범위: {tic} ~ {toc}")
            
        
        data = []
        while True:
            if tic > toc:
                break
                
            datum = inquire_candle_data(
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
            
        dataframe_to_tale(
            table_name=f"{self.cfg_database.layer['bronze']['scheme']}_{self.cfg_database.layer['bronze']['table']}",
            data=data,
            conn=self.conn
        )
        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="gru", help="Config Python 파일 명. 확장자 제외.")
    args = parser.parse_args() 
    
    (
        cfg_database,
        cfg_loader
    ) = load_spec_from_config(args.config)
    

    print(f"🐳 컨테이너 실행")
    loader = Loader(cfg_database, cfg_loader)
    loader.run()
    print(f"🐳 컨테이너 종료")