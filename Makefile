PWD := $(CURDIR)
ARCH := $(shell uname -m)
PLATFORM :=

ifeq ($(ARCH),arm64)
    PLATFORM := --platform=linux/amd64
endif

IMAGE = gustavofreze/python:3.14-cli
PYTHON = .venv/bin/python
HADOLINT_IMAGE = hadolint/hadolint:v2.15.1
IDE_VENV = .venv-ide
HOST_PYTHON ?= python3.14
DOCKER_RUN = docker run ${PLATFORM} --rm --user $(shell id -u):$(shell id -g) -e HOME=/tmp -v ${PWD}:/app \
	--env-file .env.development -w /app ${IMAGE} sh -c

SMOKE_DIR = .smoke
SMOKE_IMAGE = auto-assign:smoke
REGISTRY_IMAGE = ghcr.io/gustavofreze/auto-assign
EVENT ?= scan
NUMBER ?=
OPTIONS ?= ISSUE
ASSIGNEES ?= ${ACTOR}
ALLOW_SELF_ASSIGN ?= true
ALLOW_NO_ASSIGNEES ?= false
ASSIGN_AUTHOR ?= false
SKIP_BOTS ?= false
SKIP_DRAFTS ?= false

ifeq ($(EVENT),scan)
    SMOKE_PAYLOAD = {}
else
    SMOKE_PAYLOAD = {"$(EVENT)":{"number":$(NUMBER)}}
endif

.DEFAULT_GOAL := help

.PHONY: configure
configure: ## Configure development environment
	@${DOCKER_RUN} "poetry env use python3.14 && poetry sync --no-cache"

.PHONY: ide
ide: ## Create a host virtualenv for the IDE, pinned to poetry.lock (HOST_PYTHON)
	@${HOST_PYTHON} -m venv --clear --prompt auto-assign-ide ${IDE_VENV}
	@${DOCKER_RUN} "poetry show --no-ansi" | awk '{print $$1"=="$$2}' > ${IDE_VENV}/requirements.txt
	@${IDE_VENV}/bin/python -m pip install --quiet --disable-pip-version-check --no-deps \
		-r ${IDE_VENV}/requirements.txt
	@echo "Interpreter: $(CURDIR)/${IDE_VENV}/bin/python"

.PHONY: run
run: ## Run the application
	@${DOCKER_RUN} "${PYTHON} -m src.main"

.PHONY: test
test: ## Run tests with coverage
	@${DOCKER_RUN} "${PYTHON} -m coverage run -m pytest \
		&& ${PYTHON} -m coverage report && ${PYTHON} -m coverage html"

.PHONY: smoke
smoke: ## Run the action image against a real repository (REPOSITORY, ACTOR, EVENT, NUMBER)
	$(if $(REPOSITORY),,$(error REPOSITORY is required, e.g. REPOSITORY=owner/sandbox))
	$(if $(ACTOR),,$(error ACTOR is required, the login that triggers the simulated workflow))
	$(if $(filter scan issue pull_request,$(EVENT)),,$(error EVENT must be scan, issue, or pull_request))
	$(if $(or $(filter scan,$(EVENT)),$(NUMBER)),,$(error NUMBER is required when EVENT is $(EVENT)))
	@test -f .env.local || (echo "Create .env.local with INPUT_GITHUB_TOKEN=<token>." && exit 1)
	@docker build ${PLATFORM} -q -t ${SMOKE_IMAGE} . > /dev/null
	@mkdir -p ${SMOKE_DIR}/workspace && printf '%s' '${SMOKE_PAYLOAD}' > ${SMOKE_DIR}/event.json
	@: > ${SMOKE_DIR}/output && : > ${SMOKE_DIR}/summary
	@docker run ${PLATFORM} --rm --env-file .env.local \
		-e GITHUB_ACTOR=${ACTOR} \
		-e GITHUB_REPOSITORY=${REPOSITORY} \
		-e GITHUB_EVENT_PATH=/github/event.json \
		-e GITHUB_OUTPUT=/github/output \
		-e GITHUB_STEP_SUMMARY=/github/summary \
		-e INPUT_ASSIGNEES=${ASSIGNEES} \
		-e INPUT_ALLOW_SELF_ASSIGN=${ALLOW_SELF_ASSIGN} \
		-e INPUT_ALLOW_NO_ASSIGNEES=${ALLOW_NO_ASSIGNEES} \
		-e INPUT_ASSIGNMENT_OPTIONS=${OPTIONS} \
		-e INPUT_ASSIGN_AUTHOR=${ASSIGN_AUTHOR} \
		-e INPUT_SKIP_BOTS=${SKIP_BOTS} \
		-e INPUT_SKIP_DRAFTS=${SKIP_DRAFTS} \
		-v ${PWD}/${SMOKE_DIR}/event.json:/github/event.json:ro \
		-v ${PWD}/${SMOKE_DIR}/output:/github/output \
		-v ${PWD}/${SMOKE_DIR}/summary:/github/summary \
		-v ${PWD}/${SMOKE_DIR}/workspace:/github/workspace \
		--workdir /github/workspace \
		${SMOKE_IMAGE}
	@cat ${SMOKE_DIR}/output ${SMOKE_DIR}/summary

.PHONY: publish
publish: ## Build and push the action image to the registry (VERSION, GITHUB_ACTOR, GITHUB_TOKEN)
	$(if $(VERSION),,$(error VERSION is required, e.g. VERSION=3.0.0))
	@printf '%s' "$${GITHUB_TOKEN}" | docker login ghcr.io --username "$${GITHUB_ACTOR}" --password-stdin
	@docker build ${PLATFORM} --tag ${REGISTRY_IMAGE}:${VERSION} .
	@docker push ${REGISTRY_IMAGE}:${VERSION}

.PHONY: review
review: ## Run static code analysis
	@${DOCKER_RUN} "${PYTHON} -m pylint src tests --rcfile=.pylintrc && ${PYTHON} -m mypy"
	@docker run ${PLATFORM} --rm -i -v ${PWD}/.hadolint.yaml:/hadolint.yaml:ro ${HADOLINT_IMAGE} \
		hadolint --config /hadolint.yaml - < Dockerfile

.PHONY: show-reports
show-reports: ## Open static analysis reports (e.g., coverage, lints) in the browser
	@sensible-browser htmlcov/index.html

.PHONY: clean
clean: ## Remove virtualenv and generated artifacts
	@${DOCKER_RUN} "rm -rf .venv .venv-ide .coverage htmlcov .mypy_cache .pytest_cache .smoke"

.PHONY: help
help: ## Display this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Setup and run"
	@grep -E '^(configure|ide|run):.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Testing"
	@grep -E '^(test|smoke):.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Release"
	@grep -E '^(publish):.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Code review"
	@grep -E '^(review):.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Reports"
	@grep -E '^(show-reports):.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Cleanup"
	@grep -E '^(clean):.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Help"
	@grep -E '^(help):.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
