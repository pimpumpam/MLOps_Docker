FROM mysql:latest

# 환경 변수
ENV MYSQL_ROOT_PASSWORD=8332
ENV MYSQL_DATABASE=crypto_currency
ENV MYSQL_USER=pimpumpam
ENV MYSQL_PASSWORD=kwsxfk8332

# MySQL 포트 설정
EXPOSE 3306

# MySQL 서버 실행
CMD ["mysqld"]

# 이미지빌드
# $ docker build -t crypto_database_image .

# 컨테이너 실행
# $ docker run -d --name crypto_database --network crypto_network -p 3306:3306 crypto_database_image