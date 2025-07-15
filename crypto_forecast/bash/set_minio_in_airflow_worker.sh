#!/bin/bash

docker compose exec -it -u airflow airflow-worker /bin/bash -c 'mc config host add mlflowminio http://minio:9000 lazyplum kwsxfk8332'