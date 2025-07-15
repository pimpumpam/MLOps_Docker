import os
import argparse
import pandas as pd

from src.query import dataframe_to_tale
from src.database import create_db_engine
from src.transformation import MultiColumnScaler
from src.preparation import split_train_test
from utils.utils import load_spec_from_config

# globals
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


class Transformer:
    
    def __init__(self, cfg_database, cfg_transformer):
        self.cfg_database = cfg_database
        self.cfg_transformer = cfg_transformer
        
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
                    candle_acc_trade_volume,
                    diff_opening_price,
                    diff_trade_price,
                    diff_low_price,
                    diff_high_price,
                    diff_candle_acc_trade_price,
                    diff_candle_acc_trade_volume,
                    ratio_opening_price,
                    ratio_trade_price,
                    ratio_low_price,
                    ratio_high_price,
                    ratio_candle_acc_trade_price,
                    ratio_candle_acc_trade_volume
                FROM {self.cfg_database.layer['silver']['scheme']}_{self.cfg_database.layer['silver']['table']}
        """
        candle_data = pd.read_sql(query, con=self.engine)
        
        
        # scaler 적용
        print("⚖️ 컬럼 별 scaler 적용")
        scaler = MultiColumnScaler(self.cfg_transformer.scaler['name'])
        scaler.fit_transform(
            data=candle_data,
            columns=self.cfg_transformer.feature_field,
            inplace=True,
            save_pkl=True,
            save_path=self.cfg_transformer.scaler['save_dir'],
            save_name=self.cfg_transformer.scaler['save_name']
        )
        
        
        # 데이터 분리
        print("🪓 학습/검증 데이터 셋으로 분리")
        train_dataset, test_dataset = split_train_test(
            data=candle_data,
            train_ratio=0.7,
            test_ratio=None,
            time_col=self.cfg_transformer.time_field,
            # split_point=self.cfg_transformer.split_point
        )
        
        
        # 데이터 적재
        print("📦 학습 데이터 셋 DB 적재")
        dataframe_to_tale(
            table_name=f"{self.cfg_database.layer['gold']['scheme']}_{self.cfg_database.layer['gold']['table']}",
            data=train_dataset,
            conn=self.conn,
            table_name_suffix='train',
            table_exists_handling='replace'
        )
        
        print("📦 검증 데이터 셋 DB 적재")
        dataframe_to_tale(
            table_name=f"{self.cfg_database.layer['gold']['scheme']}_{self.cfg_database.layer['gold']['table']}",
            data=test_dataset,
            conn=self.conn,
            table_name_suffix='test',
            table_exists_handling='replace'
        )
        
        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="gru", help="Config Python 파일 명. 확장자 제외.")
    args = parser.parse_args() 
    
    (
        cfg_database,
        cfg_transformer
    ) = load_spec_from_config(args.config)
    
    transformer = Transformer(cfg_database, cfg_transformer)
    transformer.run()