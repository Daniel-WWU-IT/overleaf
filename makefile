# Simple makefile to easily work with a local deployment via Docker compose

.DEFAULT_TARGET := run

run: build start

build:
	cd ./server-ce && make build-base build-community

start:
	docker compose -p overleaf up
	docker compose -p overleaf down

.PHONY: build start run
