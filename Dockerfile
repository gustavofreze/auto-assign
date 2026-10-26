# syntax=docker/dockerfile:1
FROM gustavofreze/python:3.14-builder AS builder

COPY pyproject.toml poetry.lock /app/

RUN poetry install --only main --no-cache

COPY src /app/src

FROM gustavofreze/python:3.14-runtime

LABEL org.opencontainers.image.url="https://github.com/gustavofreze/auto-assign" \
      org.opencontainers.image.title="gustavofreze/auto-assign" \
      org.opencontainers.image.source="https://github.com/gustavofreze/auto-assign" \
      org.opencontainers.image.authors="Gustavo Freze" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.description="GitHub action that automatically assigns issues and pull requests to specified assignees." \
      org.opencontainers.image.documentation="https://github.com/gustavofreze/auto-assign/blob/main/README.md"

ENV PYTHONPATH="/app"

COPY --from=builder --chown=app:app /app /app

USER 0

CMD ["python3", "-P", "-m", "src.main"]
