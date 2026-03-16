test ci_test: unit coverage flake8 isort-check pylint

unit:
	@poetry run pytest --cov=libthumbor tests/

coverage:
	@poetry run coverage report -m --fail-under=75
	@poetry run coverage lcov

setup:
	@poetry install
	@echo "\n\nYou are strongly recommended to run 'make pre-commit-install'\n"

flake flake8:
	@poetry run flake8 --config=.flake8 libthumbor tests

isort isort-check:
	@poetry run isort --check-only --settings-file=pyproject.toml libthumbor tests

pylint:
	@poetry run pylint --exit-zero libthumbor tests

pre-commit-install:
	@poetry run pre-commit install

pre-commit:
	@poetry run pre-commit run --all-files

lint: flake8 isort-check pylint
