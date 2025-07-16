import sys
import time
import pandas as pd

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, inspect, create_engine
            
            
class DatabaseManager:
    
    def __init__(self, backend, host=None, port=None, user=None, passwd=None, database=None):

        self.backend = backend
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.database = database

        self.engine = self.__create_engine__(
            backend=backend, 
            host=host, 
            port=port, 
            user=user, 
            passwd=passwd, 
            database=database
        )


    def __create_engine__(self, backend, host, port, user, passwd, database):

        time.sleep(3)

        if backend == "postgresql":
            db_url = f"postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{database}"

        elif backend == "mysql":
            db_url = f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{database}"

        
        try:
            engine = create_engine(db_url, echo=False)

            return engine
        
        except SQLAlchemyError as e:
            print(e)
            sys.exit()


    def execute_query(self, query):
        """
        쿼리 실행 후 결과 반환

        Args:
            query (str): 실행 할 쿼리 문

        Returns:
            (sqlalchemy.engine.CursorResult): 쿼리 조회 결과
        """
        
        with self.engine.connect() as conn:
            return conn.execute(text(query))


    def check_table_exists(self, table, schema='public'):
        """
        테이블 존재 여부 확인

        Args:
            table (str): 존재 여부 대상이 되는 테이블 명
            schema (str, optional): 해당 테이블의 스키마 명. Defaults는 'public'.

        Returns:
            (bool): 해당 테이블이 존재하면 True, 존재하지 않으면 False 반환
        """
        inspector = inspect(self.engine)
        
        return table in inspector.get_table_names(schema=schema)
    
    
    def inquire_data_from_table(self, table=None, query=None):
        """
        쿼리를 통해 테이블 조회

        Args:
            table (str, optional): 조회 테이블 명. 테이블 명만 사용할 경우 적재 된 전체 데이터를 다 가져 옴. Defaults는 None.
            query (str, optional): 조회 쿼리문. Defaults는 None.

        Returns:
            (pandas.DataFrame): 조회 결과를 데이터프레임 형태로 반환
        """
        
        q = query or f"SELECT * FROM {table};"
        
        return pd.read_sql_query(q, con=self.engine)
    
    
    def insert_data_to_table(self, table, data, mode="append"):
        """
        DataFrame을 데이터베이스 내 테이블로 적재

        Args:
            table(str): 적재 테이블 명
            data(pandas.DataFrame): 적재 대상 데이터프레임
            engine(): 데이터베이스 엔진
            mode(str): 적재 방식
        
        Returns:
            None
        
        """
        
        data.to_sql(name=table, con=self.engine, if_exists=mode, index=False)
