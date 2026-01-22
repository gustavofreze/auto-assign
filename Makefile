PWD := $(CURDIR)
ARCH := $(shell uname -m)
PLATFORM :=

ifeq ($(ARCH),arm64)
    PLATFORM := --platform=linux/amd64
endif

IMAGE = gustavofreze/python:3.14-alpine
PYTHON = .venv/bin/python
DOCKER_RUN = docker run ${PLATFORM} --rm -it -v ${PWD}:/app --env-file .env.development -w /app ${IMAGE} sh -c

.DEFAULT_GOAL := help

.PHONY: configure
configure: ## Configure development environment
	@${DOCKER_RUN} "poetry config virtualenvs.in-project true \
		&& poetry env use python3.14 \
		&& poetry install --no-cache \
		&& poetry sync"

.PHONY: run
run: ## Run the application
	@${DOCKER_RUN} "${PYTHON} -m src.main"

.PHONY: test
test: ## Run tests with coverage
	@${DOCKER_RUN} "${PYTHON} -m coverage run --rcfile=.coveragerc -m unittest discover test '*Test.py' \
		&& ${PYTHON} -m coverage report && ${PYTHON} -m coverage html"

.PHONY: review
review: ## Run static code analysis
	@${DOCKER_RUN} "${PYTHON} -m pylint src test --rcfile=.pylintrc"

.PHONY: show-reports
show-reports: ## Open static analysis reports (e.g., coverage, lints) in the browser
	@sensible-browser htmlcov/index.html

.PHONY: clean
clean: ## Remove virtualenv and generated artifacts
	@sudo chown -R ${USER}:${USER} ${PWD}
	@rm -rf .venv .coverage htmlcov poetry.lock

.PHONY: help
help: ## Display this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Setup and run"
	@grep -E '^(configure|run):.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Testing"
	@grep -E '^(test):.*?## .*$$' $(MAKEFILE_LIST) \
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
