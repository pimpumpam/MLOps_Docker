import sys
import pendulum
from pathlib import Path
from datetime import timedelta

from docker.types import Mount

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator


DAG_NAME = "CryptoForecast_Train_WorkFlow"
DEFAULT_ARGS = {
    'owner': 'lazyplum',
    'depends_on_past': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    DAG_NAME,
    default_args=DEFAULT_ARGS,
    description="Train Crypto Forecast Model",
    start_date=pendulum.datetime(2025, 1, 8, tz="Asia/Seoul"),
    schedule=None,
    catchup=False,
    tags=['Toy Project using Crypto Transc Data']
) as dag:
    
    load = DockerOperator(
        task_id='load_data',
        image='crypto_load_image:latest',
        container_name='crypto_forecast_load_task',
        api_version='auto',
        auto_remove='success', # never, success, force
        command='python run.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='crypto_forecast_crypto_network',
        working_dir='/app',
        mount_tmp_dir=False,
        environment={
            'DB_HOST': 'postgres',
            'DB_PORT': '5432',
            'DB_USER': 'lazyplum',
            'DB_PASSWORD': 'kwsxfk8332',
            'DB_NAME': 'crypto_forecast'
        }
    )

    preprocess = DockerOperator(
        task_id='preprocess_data',
        image='crypto_preprocess_image:latest',
        container_name='crypto_forecast_preprocess_task',
        api_version='auto',
        auto_remove='success',
        command='python run.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='crypto_forecast_crypto_network',
        working_dir='/app',
        mount_tmp_dir=False,
        environment={
            'DB_HOST': 'postgres',
            'DB_PORT': '5432',
            'DB_USER': 'lazyplum',
            'DB_PASSWORD': 'kwsxfk8332',
            'DB_NAME': 'crypto_forecast'
        }
    )

    transform = DockerOperator(
        task_id='transform_data',
        image='crypto_transform_image:latest',
        container_name='crypto_forecast_transform_task',
        api_version='auto',
        auto_remove='success',
        command='python run.py',
        docker_url= 'unix://var/run/docker.sock',
        network_mode='crypto_forecast_crypto_network',
        working_dir='/app',
        mount_tmp_dir=False,
        mounts=[
            Mount(source='static_volume', target='/app/static', type='volume')
        ],
        environment={
            'DB_HOST': 'postgres',
            'DB_PORT': '5432',
            'DB_USER': 'lazyplum',
            'DB_PASSWORD': 'kwsxfk8332',
            'DB_NAME': 'crypto_forecast'
        }
    )

    train = DockerOperator(
        task_id='train_model',
        image='crypto_train_image:latest',
        container_name='crypto_forecast_train_task',
        api_version='auto',
        auto_remove='success',
        command='python run.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='crypto_forecast_crypto_network',
        working_dir='/app',
        mount_tmp_dir=False,
        mounts=[
            Mount(source='static_volume', target='/app/static', type='volume')
        ],
        environment={
            'DB_HOST': 'postgres',
            'DB_PORT': '5432',
            'DB_USER': 'lazyplum',
            'DB_PASSWORD': 'kwsxfk8332',
            'DB_NAME': 'crypto_forecast',
            'AWS_ACCESS_KEY_ID': 'lazyplum',
            'AWS_SECRET_ACCESS_KEY': 'kwsxfk8332',
            'MLFLOW_S3_ENDPOINT_URL': 'http://minio:9000'
        }
    )

    evaluate = DockerOperator(
        task_id='evaluate_model',
        image= 'crypto_evaluate_image:latest',
        container_name='crypto_forecast_evaluate_task',
        api_version='auto',
        auto_remove='success',
        command='python run.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='crypto_forecast_crypto_network',
        working_dir='/app',
        mount_tmp_dir=False,
        mounts=[
            Mount(source='static_volume', target='/app/static', type='volume')
        ],
        environment={
            'DB_HOST': 'postgres',
            'DB_PORT': '5432',
            'DB_USER': 'lazyplum',
            'DB_PASSWORD': 'kwsxfk8332',
            'DB_NAME': 'crypto_forecast',
            'AWS_ACCESS_KEY_ID': 'lazyplum',
            'AWS_SECRET_ACCESS_KEY': 'kwsxfk8332',
            'MLFLOW_S3_ENDPOINT_URL': 'http://minio:9000'
        }
    )

    deploy = DockerOperator(
        task_id='deploy_model',
        image='crypto_deploy_image:latest',
        container_name='crypto_forecast_deploy_task',
        api_version='auto',
        auto_remove='success',
        command='python run.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='crypto_forecast_crypto_network',
        working_dir='/app',
        mount_tmp_dir=False,
        mounts=[
            Mount(source='static_volume', target='/app/static', type='volume')
        ],
        environment={
            'DB_HOST': 'postgres',
            'DB_PORT': '5432',
            'DB_USER': 'lazyplum',
            'DB_PASSWORD': 'kwsxfk8332',
            'DB_NAME': 'crypto_forecast',
            'AWS_ACCESS_KEY_ID': 'lazyplum',
            'AWS_SECRET_ACCESS_KEY': 'kwsxfk8332',
            'MLFLOW_S3_ENDPOINT_URL': 'http://minio:9000'
        }
    )

    load >> preprocess >> transform >> train >> evaluate >> deploy