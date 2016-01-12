test ci_test:
	@coverage run --branch `which nosetests` -v --with-yanc -s tests/
	@$(MAKE) coverage

coverage:
	@coverage report -m --fail-under=76

publish:
	python setup.py sdist upload

setup:
	@pip install -U -e .\[tests\]
