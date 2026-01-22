FROM gustavofreze/python:3.14-alpine

LABEL org.opencontainers.image.url="https://github.com/gustavofreze/auto-assign"
LABEL org.opencontainers.image.title="gustavofreze/auto-assign"
LABEL org.opencontainers.image.source="https://github.com/gustavofreze/auto-assign"
LABEL org.opencontainers.image.authors="Gustavo Freze"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.description="GitHub action that automatically assigns issues and pull requests to specified assignees."
LABEL org.opencontainers.image.documentation="https://github.com/gustavofreze/auto-assign/blob/main/README.md"

ENV PYTHONPATH="/app"

WORKDIR /app

COPY pyproject.toml ./

RUN poetry config virtualenvs.in-project true \
  && poetry env use python3.14 \
  && poetry install --no-cache \
  && poetry sync

COPY src ./src

CMD ["/app/.venv/bin/python", "-m", "src.main"]
