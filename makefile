# Simple makefile to easily work with a local deployment via Docker compose

.DEFAULT_TARGET := run

BRANCH_NAME := $(shell git rev-parse --abbrev-ref HEAD)
BRANCH_NAME_TAG_SAFE := $(subst /,--,$(BRANCH_NAME))

run: build start

build:
	@echo "Building Overleaf Sandboxed Compiler..."
	cd ./sandboxed-compiler && make local

	@echo "Building Overleaf..."
	cd ./server-ce && make build-base build-community

	@echo "Building Overleaf Integration App..."
	cd ../overleaf-nextcloud && rm -rf build && make build

start:
	@echo "Copying Overleaf Sandboxed Compiler image..."
	docker save -o /tmp/sharelatex-compiler.tar sharelatex/sharelatex-compiler:$(BRANCH_NAME_TAG_SAFE)

	@echo "Launching Overleaf..."
	OVERLEAF_BRANCH_NAME=$(BRANCH_NAME) docker compose -f ./local/docker-compose.yml up --no-attach mongo --no-attach redis --no-attach nextcloud --no-attach proxy

	@echo "Shutting down Overleaf..."
	OVERLEAF_BRANCH_NAME=$(BRANCH_NAME) docker compose -f ./local/docker-compose.yml down

	@echo "Cleaning up..."
	rm -f /tmp/sharelatex-compiler.tar

.PHONY: build start run
