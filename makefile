# Simple makefile to easily work with a local deployment via Docker compose

.DEFAULT_TARGET := run

run: build start

build:
	cd ./server-ce && make build-base build-community

start:
	docker compose -f ./local/docker-compose.yml up --no-attach mongo --no-attach redis --no-attach nextcloud --no-attach proxy
	docker compose -f ./local/docker-compose.yml down

.PHONY: build start run
