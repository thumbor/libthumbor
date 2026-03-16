test ci_test: unit coverage flake8 isort-check pylint

unit:
	@poetry run pytest --cov=libthumbor tests/

coverage:
	@poetry run coverage report -m --fail-under=75
	@poetry run coverage lcov

setup:
	@poetry install

flake flake8:
	@poetry run flake8 --config=.flake8 libthumbor tests

isort isort-check:
	@poetry run isort --check-only --settings-file=pyproject.toml libthumbor tests

pylint:
	@poetry run pylint --exit-zero libthumbor tests

lint: flake8 isort-check pylint
