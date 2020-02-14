COVERAGE = $(or $(shell which coverage), $(shell which python-coverage), coverage)

test ci_test: unit coverage flake8 pylint

unit:
	@poetry run pytest -n `nproc` --cov=libthumbor tests/

coverage:
	@$(COVERAGE) report -m --fail-under=75

setup:
	@poetry install

flake flake8:
	@poetry run flake8

pylint lint:
	@poetry run pylint libthumbor tests
