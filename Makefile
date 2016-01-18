test ci_test:
	@coverage run --branch `which nosetests` -v --with-yanc -s tests/
	@$(MAKE) coverage
	@$(MAKE) static

coverage:
	@coverage report -m --fail-under=75

publish:
	python setup.py sdist upload

setup:
	@pip install -U -e .\[tests\]

static:
	@flake8 --config=./flake8 .
