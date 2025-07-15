import os
import argparse
import pandas as pd

from src.query import dataframe_to_tale
from src.database import create_db_engine
from src.preprocessing import validate_missing_values, validate_missing_timestamp, validate_duplicate_values, fill_time_gaps, fill_missing_values
from src.feature_engineering import amount_of_change_price, amount_of_change_rate
from utils.utils import load_spec_from_config


# globals
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


class Preprocessor:
    
    def __init__(self, cfg_database, cfg_preprocessor):
        self.cfg_database = cfg_database
        self.cfg_preprocessor = cfg_preprocessor
        
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
        		SELECT 
          			market,
					candle_date_time_kst,
					opening_price,
					trade_price,
					low_price,
					high_price,
					candle_acc_trade_price,
					candle_acc_trade_volume
             	FROM {self.cfg_database.layer['bronze']['scheme']}_{self.cfg_database.layer['bronze']['table']};
                """
        candle_data = pd.read_sql(query, con=self.engine)
        
        
        # 누락된 시간 정보 검증
        if not validate_missing_timestamp(candle_data, time_col='candle_date_time_kst'):
            print("⚠️ 데이터 내 1개 이상의 누락된 Timestamp가 존재.")
            print("🧹 데이터 클리닝")
            print("⚒️ Timestamp 보간 수행")
            candle_data = fill_time_gaps(
				candle_data,
				time_col=self.cfg_preprocessor.time_field,
				start_time=candle_data['candle_date_time_kst'].min(),
				end_time=candle_data['candle_date_time_kst'].max()
			)
            
            print("⚒️ 보간 된 Timestamp에 대한 NaN 값 처리")
            candle_data = fill_missing_values(
				candle_data,
    			columns=['market'],
				fill_value='KRW-BTC'
			)
        
        else:
            print("👌 데이터 무결. 누락 된 Timestamp 발견 안됨.")
            
            
        # 누락값 검증
        if not validate_missing_values(candle_data):
            print("⚠️ 데이터 내 1개 이상의 누락된 값 존재.")
            print("🧹 데이터 클리닝")
            candle_data = fill_missing_values(
				candle_data,
				columns=self.cfg_preprocessor.feature_fields
			)
            
        else:
            print("👌 데이터 무결. 누락 값 발견 안됨.")
            
            
        # 중복값 검증
        if not validate_duplicate_values(candle_data):
            print("⚠️ 데이터 내 1개 이상의 중복 된 attribute 존재.")
            candle_data.drop_duplicates(
                subset=self.cfg_preprocessor.time_field,
                inplace=True
            )
            
        else:
            print("👌 데이터 무결. 중복 attribute 발견 안됨.")
            
            
        # 파생 변수 생성
        print("🛠️ 파생 변수 생성")
        candle_data = amount_of_change_price(
            candle_data,
			time_col=self.cfg_preprocessor.time_field,
			feature_cols=self.cfg_preprocessor.feature_fields,
			unit='day',
			time_freq=1
		)
        
        candle_data = amount_of_change_rate(
			candle_data,
			time_col=self.cfg_preprocessor.time_field,
			feature_cols=self.cfg_preprocessor.feature_fields,
			unit='day',
			time_freq=1
		)
        
        
        # 데이터 적재
        print("📦 전처리 데이터 DB 적재")
        dataframe_to_tale(
			table_name=f"{self.cfg_database.layer['silver']['scheme']}_{self.cfg_database.layer['silver']['table']}",
			data=candle_data,
			conn=self.conn
		)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="gru", help="Config Python 파일 명. 확장자 제외.")
    args = parser.parse_args() 
    
    (
        cfg_database,
        cfg_preprocessor
    ) = load_spec_from_config(args.config)
    
    print(f"🐳 컨테이너 실행")
    preprocessor = Preprocessor(cfg_database, cfg_preprocessor)
    preprocessor.run()
    print(f"🐳 컨테이너 종료")