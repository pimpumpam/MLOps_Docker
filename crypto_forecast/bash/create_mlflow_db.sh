#!/bin/bash

docker compose exec -it postgres /bin/bash -c 'psql postgresql://lazyplum:kwsxfk8332@postgres/crypto_forecast -c "CREATE DATABASE mlflow_db;"'