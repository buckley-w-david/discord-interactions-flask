.PHONY: test build publish docs format

test:
	pytest

build: test
	poetry build

publish: build
	poetry publish --username ${PYPI_USERNAME} --password ${PYPI_PASSWORD}

format:
	poetry run black discord_interactions_flask/ docs/ tests/

docs:
	./build-docs.sh
