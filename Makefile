test ci_test: unit coverage black flake8 isort-check pylint

unit:
	@uv run pytest --cov=libthumbor --cov-report= tests/

coverage:
	@uv run coverage report -m --fail-under=100
	@uv run coverage lcov

setup:
	@uv sync
	@echo "\n\nYou are strongly recommended to run 'make pre-commit-install'\n"

black:
	@uv run black --check --verbose --config=pyproject.toml .

flake flake8:
	@uv run flake8 --config=.flake8 libthumbor tests

isort isort-check:
	@uv run isort --check-only --settings-file=pyproject.toml libthumbor tests

pylint:
	@uv run pylint libthumbor tests

pre-commit-install:
	@uv run pre-commit install

pre-commit:
	@uv run pre-commit run --all-files

lint: black flake8 isort-check pylint
