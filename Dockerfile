FROM python:3.11-alpine

LABEL author="Gustavo Freze" \
      maintainer="Gustavo Freze" \
      org.label-schema.name="gustavofreze/auto-assign" \
      org.label-schema.schema-version="1.0"

ARG VENV_PATH=/app/.venv

ENV PIP_PATH=${VENV_PATH}/bin/pip
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --upgrade pip poetry \
        && poetry config virtualenvs.in-project true \
        && poetry install --sync --no-root

COPY .venv ./
COPY src ./src

CMD [".venv/bin/python", "-m", "src.main"]
