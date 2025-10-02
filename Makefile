DOCKER_USERNAME ?= test
APPLICATION_NAME ?= patientsapi
GIT_HASH ?= $(shell git log --format="%h" -n 1)

_BUILD_ARGS_TAG ?= $(GIT_HASH)
_BUILD_ARGS_RELEASE_TAG ?= latest
_BUILD_ARGS_DOCKERFILE ?= Dockerfile

_builder:
	docker build --tag $(DOCKER_USERNAME)/$(APPLICATION_NAME):$(_BUILD_ARGS_TAG) -f $(_BUILD_ARGS_DOCKERFILE) .

_pusher:
	docker push $(DOCKER_USERNAME)/$(APPLICATION_NAME):$(_BUILD_ARGS_TAG)

_releaser:
	docker pull $(DOCKER_USERNAME)/$(APPLICATION_NAME):$(_BUILD_ARGS_TAG)
	docker tag $(DOCKER_USERNAME)/$(APPLICATION_NAME):$(_BUILD_ARGS_TAG) $(DOCKER_USERNAME)/$(APPLICATION_NAME):latest
	docker push $(DOCKER_USERNAME)/$(APPLICATION_NAME):$(_BUILD_ARGS_RELEASE_TAG)

build:
	$(MAKE) _builder

push:
	$(MAKE) _pusher

release:
	$(MAKE) _releaser

complete:
	$(MAKE) build
	$(MAKE) push
	$(MAKE) release
