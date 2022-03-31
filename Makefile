test ci_test: unit coverage flake8 pylint

unit:
	@poetry run pytest --cov=libthumbor tests/

coverage:
	@poetry run coverage report -m --fail-under=75
	@poetry run coverage lcov

setup:
	@poetry install

flake flake8:
	@poetry run flake8

pylint lint:
	@poetry run pylint --exit-zero libthumbor tests
