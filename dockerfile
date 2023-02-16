FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV POETRY_HOME=/opt/poetry

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH "${POETRY_HOME}/bin:${PATH}"

COPY poetry.lock pyproject.toml ./

ENV POETRY_VIRTUALENVS_PATH "${POETRY_HOME}/.venv"

ENV POETRY_VIRTUALENVS_CREATE false

ENV VIRTUAL_ENV ${POETRY_VIRTUALENVS_PATH}

ARG EDGEDB_DSN

ENV EDGEDB_DSN=$EDGEDB_DSN

RUN curl https://sh.edgedb.com --proto '=https' -sSf1 | sh -s -- -y

RUN poetry install --only main --no-root --ansi -n --no-cache

ENV PATH "/root/.local/bin:${PATH}"

COPY edgedb.toml main.py ./
COPY bin/docker-entrypoint.sh /bin/docker-entrypoint.sh
COPY dbschema ./dbschema
COPY  wishlist ./wishlist
COPY tests ./tests

CMD ["/bin/bash", "-c", "/bin/docker-entrypoint.sh"]

