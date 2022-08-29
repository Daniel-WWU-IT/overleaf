#!/bin/bash
docker build -f Dockerfile-base -t omnivox/overleaf-base:latest .
docker login --username omnivox --password "*FP!4p6z)D4VT4."
docker push omnivox/overleaf-base:latest
docker logout
docker system prune --all --volumes --force
