IMAGE = python:3.11-alpine
DOCKER_RUN = docker run --rm -it -v ${PWD}:/app --env-file .env.development -w /app --network=host ${IMAGE} sh -c
REQUIREMENTS = pip install --upgrade pip -r requirements.txt

.PHONY: run test check-style show-coverage

run:
	@${DOCKER_RUN} '${REQUIREMENTS} && python -m src.main'

test:
	@${DOCKER_RUN} '${REQUIREMENTS} && coverage run --rcfile=.coveragerc -m unittest discover test "*Test.py" \
									&& coverage report && coverage html'

check-style:
	@${DOCKER_RUN} '${REQUIREMENTS} && python -m pylint src test --rcfile=.pylintrc'

show-coverage:
	@sensible-browser htmlcov/index.html
