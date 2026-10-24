.PHONY: test build publish docs format typecheck

test:
	uv run pytest

build: test
	uv build

publish: build
	uv publish --username ${PYPI_USERNAME} --password ${PYPI_PASSWORD}

format:
	uv run black discord_interactions_flask/ docs/ tests/

typecheck:
	uv run pyright

docs:
	./build-docs.sh
