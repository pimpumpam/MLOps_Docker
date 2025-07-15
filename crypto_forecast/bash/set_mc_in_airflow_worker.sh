#!/bin/bash

docker compose exec -it -u root airflow-worker /bin/bash -c '
    curl -O https://dl.min.io/client/mc/release/linux-amd64/mc && \
    chmod +x mc && \
    mv mc /usr/local/bin/mc'