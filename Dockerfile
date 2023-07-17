FROM python:3.11-alpine

LABEL author="Gustavo Freze" \
      maintainer="Gustavo Freze" \
      org.label-schema.name="gustavofreze/auto-assign" \
      org.label-schema.schema-version="1.0"

ENV PIP_PATH="/venv/bin/pip"
ENV PYTHONPATH="${PYTHONPATH}:/app"

COPY src ./app/src
COPY requirements.txt .

RUN python -m venv /venv \
    && ${PIP_PATH} install --no-cache-dir --upgrade pip \
    && ${PIP_PATH} install --no-cache-dir -r requirements.txt

CMD ["/venv/bin/python", "-m", "src.main"]
