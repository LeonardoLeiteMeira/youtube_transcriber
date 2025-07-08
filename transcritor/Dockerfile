FROM python:3.12-slim

RUN apt-get update && apt-get install -y ffmpeg git build-essential && rm -rf /var/lib/apt/lists/*

ENV POETRY_VIRTUALENVS_CREATE=false

COPY pyproject.toml poetry.lock /app/
WORKDIR /app
RUN pip install --no-cache-dir poetry && poetry install --no-root --only main

COPY . /app

ENTRYPOINT ["python", "main.py"]
