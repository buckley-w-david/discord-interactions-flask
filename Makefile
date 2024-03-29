.PHONY: test build publish docs format typecheck

test:
	poetry run pytest

build: test
	poetry build

publish: build
	poetry publish --username ${PYPI_USERNAME} --password ${PYPI_PASSWORD}

format:
	poetry run black discord_interactions_flask/ docs/ tests/

typecheck:
	poetry run pyright

docs:
	./build-docs.sh
