FROM python:3.10

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    /root/.local/bin/poetry config virtualenvs.create false

ENV PATH="${PATH}:/root/.local/bin"

COPY pyproject.toml poetry.lock /repo
WORKDIR /repo

RUN poetry install --no-root

COPY . /repo

RUN poetry install

WORKDIR /repo/docs
VOLUME /repo/docs/build/html

ENTRYPOINT ["make", "html"]
