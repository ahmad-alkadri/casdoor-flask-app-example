#!/bin/sh

# build the docker image
docker-compose build

# run the app inside a docker container in detached (-d) mode
docker-compose up -d
