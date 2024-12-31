FROM python:3.12-slim as python-base

# python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.4.1 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt" \
    VENV_PATH="/opt/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as poetry-base
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    # deps for installing poetry
    curl

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python

# `builder-base` stage is used to build deps + create our virtual environment
FROM poetry-base as builder-base
RUN apt-get update && \
    apt-get install --no-install-recommends -y  \
    # deps for building python deps
    build-essential \
    libpq-dev \
    pkg-config

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./README.md ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --only main


FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
RUN npm install

# Rebuild the source code only when needed
FROM base AS builder
RUN apk --no-cache add openjdk11 --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community
WORKDIR /app
COPY . .


RUN cd frontend && npm run generate-api-deploy && npm run build

# `development` image is used during development / testing
FROM python-base as development

# copy in our built poetry + venv
COPY --from=poetry-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $VENV_PATH $VENV_PATH

RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq-dev sudo nodejs npm && \
    useradd -m -d /home/app -s /bin/bash app && \
    echo '%app ALL=(ALL) NOPASSWD:ALL' >>/etc/sudoers

USER app

# will become mountpoint of our code
WORKDIR /workspace

COPY . .

EXPOSE 8000
