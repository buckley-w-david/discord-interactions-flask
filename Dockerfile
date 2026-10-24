FROM python:3.10

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /repo

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-install-project

COPY . /repo

RUN uv sync --locked

ENV PATH="/repo/.venv/bin:$PATH"

WORKDIR /repo/docs
VOLUME /repo/docs/build/html

ENTRYPOINT ["make", "html"]
