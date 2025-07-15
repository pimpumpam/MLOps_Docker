#!/bin/bash

docker compose exec -it -u root airflow-worker /usr/sbin/sshd
