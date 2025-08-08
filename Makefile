PORT ?= 8000

install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

check:
	uv run ruff check

fix-lint:
	uv run ruff check --fix page_analyzer

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh