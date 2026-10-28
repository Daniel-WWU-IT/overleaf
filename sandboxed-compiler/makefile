# Makefile for the sandboxed compiler containers

export BRANCH_NAME ?= $(shell git rev-parse --abbrev-ref HEAD)
export BRANCH_NAME_TAG_SAFE ?= $(subst /,--,$(BRANCH_NAME))

all: build-compiler build-compiler-host

build-compiler:
	docker build \
	  --progress=plain \
	  --file ./compiler/Dockerfile \
	  --pull \
	  --tag sharelatex/sharelatex-compiler:$(BRANCH_NAME_TAG_SAFE) \
	  ./compiler

build-compiler-host:
	docker build \
	  --progress=plain \
	  --file ./compiler-host/Dockerfile \
	  --pull \
	  --tag sharelatex/sharelatex-compiler-host:$(BRANCH_NAME_TAG_SAFE) \
	  ./compiler-host

.PHONY: build-compiler build-compiler-host
