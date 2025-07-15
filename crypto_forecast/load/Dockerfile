# Data Load
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_USER=lazyplum
ENV DB_PASSWORD=kwsxfk8332
ENV DB_NAME=crypto_forecast

CMD ["python", "run.py"]

# 이미지 빌드
# $ docker build -t crypto_load_image .

# 컨테이너 실행
# $ docker run -d --name crypto_load --network crypto_forecast_crypto_network crypto_load_image