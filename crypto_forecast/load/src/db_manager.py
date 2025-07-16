import sys
import time
import pandas as pd

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, inspect
            
            

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



    def check_table_exists(self, table, schema='public'):
        inspector = inspect(self.engine)
        
        return table in inspector.get_table_names(schema=schema)


        
def fetch_one(cursor, query):
    
    cursor.execute(query)
    
    return cursor.fetchone()