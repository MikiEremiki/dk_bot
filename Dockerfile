FROM python:3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN --mount=type=bind,source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt

WORKDIR /app
COPY . .