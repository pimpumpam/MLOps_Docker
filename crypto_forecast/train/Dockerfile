# Model Training
FROM pytorch/pytorch

RUN apt-get update && apt-get install -y git

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_USER=lazyplum
ENV DB_PASSWORD=kwsxfk8332
ENV DB_NAME=crypto_transc
ENV AWS_ACCESS_KEY_ID=lazyplum
ENV AWS_SECRET_ACCESS_KEY=kwsxfk8332
ENV MLFLOW_S3_ENDPOINT_URL=http://minio:9000

CMD ["python", "run.py"]

# 이미지 빌드
# $ docker build -t crypto_train_image .

# 컨테이너 실행
# $ docker run -dit --name crypto_train --network crypto_forecast_crypto_network -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/sql:/app/sql" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/configs:/app/configs" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/utils:/app/utils" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/structure:/app/structure" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/load/src:/app/load/src" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/static/assets:/app/static/assets" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/train/src:/app/src" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/train/models:/app/models" -v "/Users/pimpumpam/Desktop/myScript/MLOps_Docker/crypto_forecast/train/run.py:/app/run.py" crypto_train_image tail -f /dev/null