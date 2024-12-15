FROM python:3.11-alpine

LABEL author="Gustavo Freze" \
      maintainer="Gustavo Freze" \
      org.label-schema.name="gustavofreze/auto-assign" \
      org.label-schema.schema-version="1.0"

ENV PYTHONPATH="${PYTHONPATH}:/app"

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --upgrade pip poetry \
        && poetry config virtualenvs.in-project true \
        && poetry install --sync --no-root

COPY src ./src

CMD ["/app/.venv/bin/python", "-m", "src.main"]
