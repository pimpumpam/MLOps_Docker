import sys
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
            
            
def create_db_engine(host, port, user, password, database, backend='postgresql'):

    # Sleep for initialize DB
    time.sleep(3)
    
    # Backend URL
    if backend == 'mysql':
        db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    elif backend == 'postgresql':
        db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        
    print(f"🔗 데이터베이스 URL: {db_url}")

    
    # Create engine
    try:
        engine = create_engine(db_url, echo=False)
        print(f"⚙️ {backend.upper()} 엔진 생성 성공")
        
        return engine

    except SQLAlchemyError as e:
        print(f"🚨 {backend.upper()} 엔진 생성 실패")
        print(e)
        sys.exit()

        
def fetch_one(cursor, query):
    
    cursor.execute(query)
    
    return cursor.fetchone()


# def connect_to_database(host, port, user, password, database):
    # import mysql.connector
    
#     # sleep for initialize DB
#     time.sleep(3)
    
#     try:
#         conn = mysql.connector.connect(
#             host = host,
#             port=port,
#             user=user,
#             password=password,
#             database=database
#         )
#         print("✅ MySQL 커넥션 성공")
#         return conn
        
#     except mysql.connector.Error as e:
#         print(f"🚨 MySQL 커넥션 실패 | 에러: {e}")
#         sys.exit()