#!/bin/bash

docker compose exec -it -u airflow airflow-worker /bin/bash -c 'mkdir -p /home/airflow/.ssh && echo -e "" > /home/airflow/.ssh/authorized_keys'
docker compose cp ./ssh_key/id_rsa.pub airflow-worker:/home/airflow/.ssh/gitlab-runner.pub
docker compose exec -it -u airflow airflow-worker /bin/bash -c 'cat /home/airflow/.ssh/gitlab-runner.pub >> /home/airflow/.ssh/authorized_keys && cat /home/airflow/.ssh/authorized_keys && chmod 700 ~ && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys'
