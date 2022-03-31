test ci_test: unit coverage flake8 pylint

unit:
	@poetry run pytest --cov=libthumbor tests/

coverage:
	@coverage report -m --fail-under=75

setup:
	@poetry install

flake flake8:
	@poetry run flake8

pylint lint:
	@poetry run pylint --exit-zero libthumbor tests
