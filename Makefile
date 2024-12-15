ifeq ($(OS),Windows_NT)
    PWD := $(shell cd)
else
    PWD := $(shell pwd -L)
endif

ARCH := $(shell uname -m)
PLATFORM :=

ifeq ($(ARCH),arm64)
    PLATFORM := --platform=linux/amd64
endif

IMAGE = python:3.11-alpine
PYTHON = .venv/bin/python
DOCKER_RUN = docker run ${PLATFORM} --rm -it -v ${PWD}:/app --env-file .env.development -w /app ${IMAGE} sh -c

.PHONY: configure run test clean

configure:
	@${DOCKER_RUN} "pip install --upgrade pip poetry \
						&& poetry config virtualenvs.in-project true \
						&& poetry install --with dev --sync --no-root"

run:
	@${DOCKER_RUN} "${PYTHON} -m src.main"

test:
	@${DOCKER_RUN} "${PYTHON} -m coverage run --rcfile=.coveragerc -m unittest discover test '*Test.py' \
						&& ${PYTHON} -m coverage report && ${PYTHON} -m coverage html"

review:
	@${DOCKER_RUN} "${PYTHON} -m pylint src test --rcfile=.pylintrc"

show-coverage:
	@sensible-browser htmlcov/index.html

clean:
	@sudo chown -R ${USER}:${USER} ${PWD}
	@rm -rf .venv .coverage poetry.lock
