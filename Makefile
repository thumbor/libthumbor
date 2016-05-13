COVERAGE = $(or $(shell which coverage), $(shell which python-coverage), coverage)

test ci_test:
	@$(COVERAGE) run --branch `which nosetests` -v --with-yanc -s tests/
	@$(MAKE) coverage
	@$(MAKE) static

coverage:
	
	@$(COVERAGE) report -m --fail-under=75

publish:
	python setup.py sdist upload

setup:
	@pip install -U -e .\[tests\]

static:
	@flake8 --config=./flake8 .
