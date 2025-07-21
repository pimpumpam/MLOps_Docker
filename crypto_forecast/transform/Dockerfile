# Data Tranformation
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_USER=lazyplum
ENV DB_PASSWORD=kwsxfk8332
ENV DB_NAME=crypto_transc

CMD ["python", "run.py"]

# 이미지 빌드
# $ docker build -t crypto_transform_image .

# 컨테이너 실행
# $ docker run -d --name crypto_transform --network crypto_forecast_crypto_network -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/sql:/app/sql" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/configs:/app/configs" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/utils:/app/utils" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/structure:/app/structure" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/load/src:/app/load/src" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/transform/src:/app/src" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/transform/run.py:/app/run.py" crypto_transform_image tail -f /dev/null
