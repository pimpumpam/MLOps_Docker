#!/bin/bash

docker build --tag airflow_with_docker:latest .
docker image tag airflow_with_docker:latest localhost:6000/airflow_with_docker:latest
docker push localhost:6000/airflow_with_docker:latest