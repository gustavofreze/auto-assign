FROM gustavofreze/python:3.14

LABEL author="Gustavo Freze" \
      maintainer="Gustavo Freze" \
      org.label-schema.name="gustavofreze/auto-assign" \
      org.label-schema.schema-version="1.0"

ENV PYTHONPATH="${PYTHONPATH}:/app"

WORKDIR /app

COPY pyproject.toml ./

RUN poetry config virtualenvs.in-project true \
  && poetry env use python3.14 \
  && poetry install --no-cache \
  && poetry sync

COPY src ./src

CMD ["/app/.venv/bin/python", "-m", "src.main"]
