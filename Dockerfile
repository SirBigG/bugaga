FROM python:3.9.7-slim

ENV PYTHONUNBUFFERED 1
ENV PROJECT_DIR /web

RUN mkdir $PROJECT_DIR

COPY requirements.txt /web/
RUN apt -y update && \
    apt install -y --no-install-recommends \
    libpq-dev \
    gcc \
    libjpeg-dev \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    && \
    pip install --no-cache-dir -r $PROJECT_DIR/requirements.txt

WORKDIR $PROJECT_DIR
COPY . $PROJECT_DIR
