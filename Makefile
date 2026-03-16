.PHONY: uv-sync venv lint format tests

lint:
	black --check .
	ruff check
	mypy src tests --config-file=./pyproject.toml

format:
	black .
	ruff check --fix
	black .

uv-sync:
	uv sync --all-extras

tests:
	pytest tests
