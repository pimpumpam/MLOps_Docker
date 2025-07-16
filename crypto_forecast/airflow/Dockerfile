FROM apache/airflow:2.7.3

USER root

# Docker 설치
RUN curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh

# Root 그룹 권한 부여
RUN usermod -aG root airflow

# ACL, SSH 설정
RUN apt-get install -y acl
RUN setfacl -Rm d:g:root:rwx,g:root:rwx /var/run/
RUN apt install -y openssh-server
RUN mkdir /run/sshd && chmod 700 /run/sshd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/g' \
            /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/g' \
            /etc/ssh/sshd_config \
    && sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/g' \
            /etc/ssh/sshd_config \
    && sed -i 's/#AuthorizedKeysFile/AuthorizedKeysFile/g' \
            /etc/ssh/sshd_config

# Python 패키지 설치
# RUN pip install --no-cache-dir -r requirements.txt

USER airflow