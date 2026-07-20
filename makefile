# Simple makefile to easily work with a local deployment via Docker compose

.DEFAULT_TARGET := run

GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

run: build start

build:
	cd ./server-ce && make build-base build-community

start:
	OVERLEAF_BRANCH_NAME=$(GIT_BRANCH) docker compose -f ./local/docker-compose.yml up --no-attach mongo --no-attach redis --no-attach nextcloud --no-attach proxy
	OVERLEAF_BRANCH_NAME=$(GIT_BRANCH) docker compose -f ./local/docker-compose.yml down

.PHONY: build start run
