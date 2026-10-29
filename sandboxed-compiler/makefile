# Makefile for the sandboxed compiler containers

.DEFAULT_TARGET := all

BRANCH_NAME := $(shell git rev-parse --abbrev-ref HEAD)
BRANCH_NAME_TAG_SAFE := $(subst /,--,$(BRANCH_NAME))

all: build-compiler build-compiler-host
local: build-compiler-local build-compiler-host

build-compiler:
	docker build \
	  --progress=plain \
	  --file ./compiler/Dockerfile \
	  --pull \
	  --tag sharelatex/sharelatex-compiler:$(BRANCH_NAME_TAG_SAFE) \
	  ./compiler

build-compiler-local:
	docker build \
	  --progress=plain \
	  --file ./compiler/Dockerfile \
	  --build-arg TEXLIVE_DISTRO=texlive-base \
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

.PHONY: all local build-compiler build-compiler-local build-compiler-host
