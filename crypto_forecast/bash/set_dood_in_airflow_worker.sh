#!/bin/bash

docker compose exec -it -u root airflow-worker /bin/bash -c "ls -al /var/run/docker.sock && \
                                                             usermod -aG root airflow && \
                                                             id airflow && \
                                                             chmod 773 /var/run/docker.sock && \
                                                             ls -al /var/run/docker.sock"