.PHONY: test build publish docs

test:
	pytest

build: test
	poetry build

publish: build
	poetry publish --username ${PYPI_USERNAME} --password ${PYPI_PASSWORD}

docs:
	./build-docs.sh
