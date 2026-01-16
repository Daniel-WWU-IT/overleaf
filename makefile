# Simple makefile to easily work with a local deployment via Docker compose

.DEFAULT_TARGET := run

run: build start

build:
	cd ./server-ce && make build-base build-community

start:
	docker compose -p overleaf -f docker-compose.local.yml up
	docker compose -p overleaf -f docker-compose.local.yml down

.PHONY: build start run
